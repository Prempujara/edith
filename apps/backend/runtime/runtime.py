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
"""

from __future__ import annotations

from runtime.lifecycle import assert_transition
from runtime.registry import AgentRegistry
from runtime.store import TaskStore
from schemas.enums import AgentName, EventType, TaskStatus
from schemas.event import Event
from schemas.task import Task, _now
from services import edith_service, friday_service
from services.jarvis_service import Decision, JarvisService

# Maps a delegate agent to its executor callable.
_DELEGATE_EXECUTORS = {
    AgentName.FRIDAY: friday_service.execute,
    AgentName.EDITH: edith_service.execute,
}


class AgentRuntime:
    def __init__(
        self,
        registry: AgentRegistry,
        store: TaskStore,
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

        # 2. JARVIS makes the semantic decision.
        decision = self._jarvis.decide(command)
        self._emit(
            task.id,
            EventType.AGENT_SELECTED,
            agent=AgentName.JARVIS,
            capability=decision.capability.value if decision.capability else None,
            target_agent=decision.target_agent.value,
            handled_directly=decision.handled_directly,
        )

        try:
            if decision.handled_directly:
                return self._run_direct(task, decision)
            return self._run_delegated(task, decision)
        except Exception as exc:  # pragma: no cover - defensive
            self._fail(task, str(exc))
            return task

    # --- direct JARVIS path --------------------------------------------
    def _run_direct(self, task: Task, decision: Decision) -> Task:
        task.assigned_agent = AgentName.JARVIS
        self._set_status(task, TaskStatus.QUEUED)
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
        self._emit(child.id, EventType.TASK_QUEUED, agent=target)
        self._set_status(child, TaskStatus.RUNNING)
        child.started_at = _now()
        self._emit(child.id, EventType.TASK_STARTED, agent=target)
        self._emit(child.id, EventType.AGENT_STARTED, agent=target)

        child_result = executor(child.input)

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

    def _fail(self, task: Task, error: str) -> None:
        if task.status == TaskStatus.RUNNING:
            self._set_status(task, TaskStatus.FAILED)
        task.error = error
        task.completed_at = _now()
        self._emit(task.id, EventType.TASK_FAILED, agent=task.assigned_agent)
