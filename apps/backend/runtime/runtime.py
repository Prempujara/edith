"""Agent Runtime (baseline §12).

The Runtime is shared infrastructure, NOT a central AI decision-maker. It:

- receives a command, asks JARVIS for the delegation decision,
- creates and tracks the task through the lifecycle (§15),
- transports the work to the target agent (direct JARVIS execution, or a
  delegated child task to FRIDAY/EDITH),
- records events (§16),
- returns the completed task.

The Runtime does not decide *which* agent handles a semantic task — that
decision is made by JARVIS and merely executed here.

Failure handling (M2.1): every exception is mapped to a user-safe
:class:`~schemas.errors.TaskError` and the affected task(s) are driven to a
valid terminal ``FAILED`` state with a ``task.failed`` event. In particular, a
delegated child that raises terminalizes **both** the child and its parent — no
task is ever left stuck in ``RUNNING``. Detailed diagnostics go to the server
log; provider internals and stack traces are never surfaced to callers.
"""

from __future__ import annotations

import logging

from runtime.lifecycle import assert_transition, is_terminal
from runtime.registry import AgentRegistry
from runtime.repository import TaskRepository
from schemas.enums import AgentName, EventType, TaskStatus
from schemas.errors import TaskError
from schemas.event import Event
from schemas.task import Task, _now
from services import edith_service, friday_service
from services.coding_service import CodingError
from services.jarvis_service import Decision, JarvisService
from services.llm.base import LLMConfigError, LLMError, LLMTimeoutError

logger = logging.getLogger(__name__)

# Maps a delegate agent to its executor callable.
_DELEGATE_EXECUTORS = {
    AgentName.FRIDAY: friday_service.execute,
    AgentName.EDITH: edith_service.execute,
}


class AgentRuntime:
    def __init__(
        self,
        registry: AgentRegistry,
        store: TaskRepository,
        jarvis: JarvisService,
    ) -> None:
        self._registry = registry
        self._store = store
        self._jarvis = jarvis

    # --- event helper ---------------------------------------------------
    def _emit(
        self,
        task_id: str,
        type_: EventType,
        agent: AgentName | None = None,
        **payload,
    ) -> None:
        self._store.add_event(
            Event(task_id=task_id, type=type_, agent=agent, payload=payload)
        )

    def _set_status(self, task: Task, target: TaskStatus) -> None:
        assert_transition(task.status, target)
        task.status = target

    # --- main entry point ----------------------------------------------
    def submit_command(self, command: str) -> Task:
        """Run a user command through the full pipeline and return the task."""
        # 1. Create the root task (requested by the user).
        task = Task(requester="user", input=command)
        self._store.add(task)
        self._emit(task.id, EventType.TASK_CREATED, payload_command=command)

        # 2. JARVIS makes the semantic decision. A failure in the decision
        #    stage must terminalize the task and must NOT proceed to execute an
        #    undefined decision.
        try:
            decision = self._jarvis.decide(command)
        except Exception as exc:
            self._fail(
                task,
                self._error_from_exception(
                    exc,
                    task_id=task.id,
                    stage="decision",
                    default_code="DECISION_FAILED",
                    default_message="Could not determine how to handle the request.",
                ),
            )
            return task

        self._emit(
            task.id,
            EventType.AGENT_SELECTED,
            agent=AgentName.JARVIS,
            capability=decision.capability.value if decision.capability else None,
            target_agent=decision.target_agent.value,
            handled_directly=decision.handled_directly,
        )

        # 3. Execute the decision. The delegated path terminalizes its own
        #    child/parent on failure; this guard is the safety net for the
        #    direct path and any unexpected error.
        try:
            if decision.handled_directly:
                return self._run_direct(task, decision)
            return self._run_delegated(task, decision)
        except Exception as exc:
            self._fail(task, self._error_from_exception(exc, task_id=task.id))
            return task

    # --- direct JARVIS path --------------------------------------------
    def _run_direct(self, task: Task, decision: Decision) -> Task:
        task.assigned_agent = AgentName.JARVIS
        self._set_status(task, TaskStatus.QUEUED)
        task.queued_at = _now()
        self._emit(task.id, EventType.TASK_QUEUED, agent=AgentName.JARVIS)

        self._set_status(task, TaskStatus.RUNNING)
        task.started_at = _now()
        self._emit(task.id, EventType.TASK_STARTED, agent=AgentName.JARVIS)
        self._emit(task.id, EventType.AGENT_STARTED, agent=AgentName.JARVIS)

        result = self._jarvis.handle_directly(task.input, decision.capability)

        self._emit(task.id, EventType.AGENT_COMPLETED, agent=AgentName.JARVIS)
        self._complete(task, result)
        return task

    # --- delegated path (JARVIS -> Runtime -> target agent) ------------
    def _run_delegated(self, task: Task, decision: Decision) -> Task:
        target = decision.target_agent

        # Parent task is assigned to JARVIS (the coordinator) and queued.
        task.assigned_agent = AgentName.JARVIS
        self._set_status(task, TaskStatus.QUEUED)
        task.queued_at = _now()
        self._emit(task.id, EventType.TASK_QUEUED, agent=AgentName.JARVIS)
        self._set_status(task, TaskStatus.RUNNING)
        task.started_at = _now()
        self._emit(task.id, EventType.TASK_STARTED, agent=AgentName.JARVIS)

        # JARVIS delegates -> create a linked child task for the specialist.
        child = Task(
            parent_task_id=task.id,
            requester=AgentName.JARVIS.value,
            assigned_agent=target,
            input=task.input,
        )
        self._store.add(child)
        self._emit(
            child.id,
            EventType.TASK_CREATED,
            agent=AgentName.JARVIS,
            parent_task_id=task.id,
        )
        self._emit(
            task.id,
            EventType.AGENT_DELEGATED,
            agent=AgentName.JARVIS,
            target_agent=target.value,
            child_task_id=child.id,
        )

        # Runtime transports the child task to the specialist agent.
        executor = _DELEGATE_EXECUTORS[target]
        self._set_status(child, TaskStatus.QUEUED)
        child.queued_at = _now()
        self._emit(child.id, EventType.TASK_QUEUED, agent=target)
        self._set_status(child, TaskStatus.RUNNING)
        child.started_at = _now()
        self._emit(child.id, EventType.TASK_STARTED, agent=target)
        self._emit(child.id, EventType.AGENT_STARTED, agent=target)

        try:
            child_result = executor(child.input)
        except Exception as exc:
            # A failing delegate must terminalize BOTH the child and the parent.
            # Nothing may remain RUNNING because an executor raised.
            child_error = self._error_from_exception(
                exc, task_id=child.id, stage=f"{target.value} execution"
            )
            self._fail(child, child_error)
            self._fail(
                task,
                TaskError(
                    code="DELEGATION_FAILED",
                    message=(
                        f"Delegation to {target.value} failed: {child_error.message}"
                    ),
                    details={"child_task_id": child.id, "cause": child_error.code},
                ),
            )
            return task

        self._emit(child.id, EventType.AGENT_COMPLETED, agent=target)
        self._complete(child, child_result)

        # Parent completes, wrapping the delegate's result (§5: result returns
        # to the requesting agent).
        parent_result = {
            "agent": "JARVIS",
            "kind": "delegation",
            "delegated_to": target.value,
            "child_task_id": child.id,
            "result": child_result,
            "summary": (
                f"JARVIS delegated the task to {target.value} and returned "
                f"its result."
            ),
        }
        self._complete(task, parent_result)
        return task

    # --- terminal helpers ----------------------------------------------
    def _complete(self, task: Task, result: dict) -> None:
        self._set_status(task, TaskStatus.COMPLETED)
        task.result = result
        task.completed_at = _now()
        self._emit(task.id, EventType.TASK_COMPLETED, agent=task.assigned_agent)

    def _fail(self, task: Task, error: TaskError) -> None:
        """Drive ``task`` to a valid terminal FAILED state.

        Safe to call from any state: an already-terminal task is left untouched
        (its terminal state is never corrupted), and FAILED is a legal target
        from CREATED/QUEUED/RUNNING, so a task that failed before it started is
        still terminalized correctly.
        """
        if is_terminal(task.status):
            logger.warning(
                "Ignoring failure for already-terminal task %s (%s): %s",
                task.id,
                task.status.value,
                error.code,
            )
            return
        self._set_status(task, TaskStatus.FAILED)
        task.error = error
        if task.completed_at is None:
            task.completed_at = _now()
        self._emit(
            task.id,
            EventType.TASK_FAILED,
            agent=task.assigned_agent,
            error_code=error.code,
        )

    # --- error mapping --------------------------------------------------
    def _error_from_exception(
        self,
        exc: Exception,
        *,
        task_id: str,
        stage: str = "execution",
        default_code: str = "INTERNAL_ERROR",
        default_message: str = "An internal error occurred while processing the task.",
    ) -> TaskError:
        """Map an exception to a user-safe :class:`TaskError`.

        Known domain errors carry curated, safe messages and are surfaced as-is.
        Anything unexpected is logged with a full traceback server-side and
        reported to the caller only as a generic message — no stack traces,
        provider internals, or credentials ever leave the process.
        """
        if isinstance(exc, LLMTimeoutError):
            code = "LLM_TIMEOUT"
        elif isinstance(exc, LLMConfigError):
            code = "LLM_CONFIG_ERROR"
        elif isinstance(exc, LLMError):
            code = "LLM_ERROR"
        elif isinstance(exc, CodingError):
            code = "CODING_ERROR"
        else:
            logger.exception(
                "Unexpected error during %s for task %s", stage, task_id
            )
            return TaskError(code=default_code, message=default_message)

        logger.warning("Task %s failed during %s: %s: %s", task_id, stage, code, exc)
        return TaskError(code=code, message=str(exc))
