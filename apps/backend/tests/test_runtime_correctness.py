"""Runtime correctness tests for M2.1.

Covers the behaviours M2.1 set out to fix/add:
- delegated child failure propagates to BOTH child and parent (no task left RUNNING),
- decision-stage failure terminalizes the task without executing,
- _fail() is valid from any state and never corrupts a terminal task,
- structured, user-safe errors (no internal detail leakage),
- deterministic per-task event sequencing,
- queued_at lifecycle timestamp,
- lifecycle transition rules (failure from any non-terminal state; TIMED_OUT).
"""

from __future__ import annotations

import pytest

import runtime.runtime as runtime_module
from runtime.lifecycle import can_transition, is_terminal
from runtime.registry import build_default_registry
from runtime.runtime import AgentRuntime
from runtime.store import TaskStore
from schemas.enums import AgentName, EventType, TaskStatus
from schemas.errors import TaskError
from services.coding_service import CodingService
from services.jarvis_service import JarvisService
from services.llm.base import LLMError
from services.llm.fake import FakeLLMClient

_FILE_CMD = "Please organize my project files into folders"   # delegates to FRIDAY
_CODE_CMD = "write a python script"                            # direct (JARVIS coding)


@pytest.fixture
def runtime():
    registry = build_default_registry()
    store = TaskStore()
    jarvis = JarvisService(registry, CodingService(FakeLLMClient()))
    return AgentRuntime(registry, store, jarvis), store


def _children_of(store, parent_id):
    return [t for t in store.list_tasks() if t.parent_task_id == parent_id]


# --- delegated child failure propagation (the core regression) ---------
def test_delegated_child_failure_terminalizes_child_and_parent(runtime, monkeypatch):
    rt, store = runtime

    def boom(_command):
        raise RuntimeError("friday exploded internally")

    monkeypatch.setitem(runtime_module._DELEGATE_EXECUTORS, AgentName.FRIDAY, boom)

    task = rt.submit_command(_FILE_CMD)

    # Parent failed with a structured delegation error.
    assert task.status == TaskStatus.FAILED
    assert task.error is not None and task.error.code == "DELEGATION_FAILED"
    assert task.completed_at is not None

    # The child exists and is terminal (FAILED) — not stuck RUNNING.
    children = _children_of(store, task.id)
    assert len(children) == 1
    child = children[0]
    assert child.status == TaskStatus.FAILED
    assert child.error is not None
    assert child.completed_at is not None

    # No task anywhere remains non-terminal.
    assert all(is_terminal(t.status) for t in store.list_tasks())

    # Both streams recorded a task.failed event.
    assert EventType.TASK_FAILED in [e.type for e in store.get_events(task.id)]
    assert EventType.TASK_FAILED in [e.type for e in store.get_events(child.id)]

    # An unexpected RuntimeError must not leak internals to either task.
    assert "exploded internally" not in child.error.message
    assert "exploded internally" not in task.error.message
    assert task.error.details == {"child_task_id": child.id, "cause": child.error.code}


# --- decision-stage failure --------------------------------------------
def test_decision_failure_terminalizes_without_executing(runtime, monkeypatch):
    rt, store = runtime

    def boom(_command):
        raise RuntimeError("decider blew up with secret detail")

    monkeypatch.setattr(rt._jarvis, "decide", boom)

    task = rt.submit_command("do something")

    assert task.status == TaskStatus.FAILED
    assert task.error is not None and task.error.code == "DECISION_FAILED"
    assert task.completed_at is not None
    assert task.result is None

    types = [e.type for e in store.get_events(task.id)]
    assert EventType.TASK_CREATED in types
    assert EventType.TASK_FAILED in types
    # It must NOT have proceeded to select/queue/start (no execution attempted).
    assert EventType.AGENT_SELECTED not in types
    assert EventType.TASK_QUEUED not in types
    assert EventType.TASK_STARTED not in types
    # No internal detail leaked.
    assert "secret detail" not in task.error.message


# --- _fail() edge cases -------------------------------------------------
def test_fail_does_not_corrupt_a_terminal_task(runtime):
    rt, store = runtime
    task = rt.submit_command(_CODE_CMD)
    assert task.status == TaskStatus.COMPLETED

    events_before = len(store.get_events(task.id))
    rt._fail(task, TaskError(code="SHOULD_IGNORE", message="ignored"))

    # Terminal state, result, and error are untouched; no spurious event.
    assert task.status == TaskStatus.COMPLETED
    assert task.error is None
    assert task.result is not None
    assert len(store.get_events(task.id)) == events_before


def test_direct_coding_failure_is_structured_and_safe():
    registry = build_default_registry()
    store = TaskStore()
    fake = FakeLLMClient(
        error=LLMError("The coding provider failed to complete the request.")
    )
    rt = AgentRuntime(registry, store, JarvisService(registry, CodingService(fake)))

    task = rt.submit_command("write a python function")

    assert task.status == TaskStatus.FAILED
    assert task.error is not None
    assert task.error.code == "LLM_ERROR"
    assert task.error.message == "The coding provider failed to complete the request."
    assert "Traceback" not in task.error.message
    assert task.completed_at is not None
    assert EventType.TASK_FAILED in [e.type for e in store.get_events(task.id)]


def test_unexpected_direct_error_is_generic_and_safe(runtime, monkeypatch):
    rt, store = runtime

    def boom(_command, _capability):
        raise ValueError("SECRET internal detail xyz")

    monkeypatch.setattr(rt._jarvis, "handle_directly", boom)

    task = rt.submit_command(_CODE_CMD)

    assert task.status == TaskStatus.FAILED
    assert task.error is not None and task.error.code == "INTERNAL_ERROR"
    assert task.error.message  # non-empty, generic
    assert "SECRET internal detail" not in task.error.message


# --- event sequencing ---------------------------------------------------
def test_direct_event_sequence_is_deterministic_and_monotonic(runtime):
    rt, store = runtime
    task = rt.submit_command(_CODE_CMD)
    events = store.get_events(task.id)

    assert [e.seq for e in events] == list(range(1, len(events) + 1))
    assert [e.type for e in events] == [
        EventType.TASK_CREATED,
        EventType.AGENT_SELECTED,
        EventType.TASK_QUEUED,
        EventType.TASK_STARTED,
        EventType.AGENT_STARTED,
        EventType.AGENT_COMPLETED,
        EventType.TASK_COMPLETED,
    ]


def test_parent_and_child_event_streams_are_distinct_and_monotonic(runtime):
    rt, store = runtime
    task = rt.submit_command(_FILE_CMD)
    child_id = task.result["child_task_id"]

    parent_events = store.get_events(task.id)
    child_events = store.get_events(child_id)

    # Each stream is independently 1..N monotonic.
    assert [e.seq for e in parent_events] == list(range(1, len(parent_events) + 1))
    assert [e.seq for e in child_events] == list(range(1, len(child_events) + 1))
    # Events never bleed across tasks.
    assert all(e.task_id == task.id for e in parent_events)
    assert all(e.task_id == child_id for e in child_events)
    # Delegation is on the parent's stream, not the child's.
    assert EventType.AGENT_DELEGATED in [e.type for e in parent_events]
    assert EventType.AGENT_DELEGATED not in [e.type for e in child_events]


# --- queued_at timestamp -----------------------------------------------
def test_queued_at_is_set_on_direct_task(runtime):
    rt, _ = runtime
    task = rt.submit_command(_CODE_CMD)
    assert task.queued_at is not None
    assert task.created_at <= task.queued_at <= task.started_at <= task.completed_at


def test_queued_at_is_set_on_parent_and_child(runtime):
    rt, store = runtime
    task = rt.submit_command(_FILE_CMD)
    child = store.get(task.result["child_task_id"])
    for t in (task, child):
        assert t.queued_at is not None
        assert t.created_at <= t.queued_at <= t.started_at <= t.completed_at


# --- lifecycle rules ----------------------------------------------------
def test_failure_is_reachable_from_every_nonterminal_state():
    assert can_transition(TaskStatus.CREATED, TaskStatus.FAILED)
    assert can_transition(TaskStatus.QUEUED, TaskStatus.FAILED)
    assert can_transition(TaskStatus.RUNNING, TaskStatus.FAILED)


def test_timed_out_is_a_supported_terminal_state():
    assert can_transition(TaskStatus.RUNNING, TaskStatus.TIMED_OUT)
    assert is_terminal(TaskStatus.TIMED_OUT)


def test_terminal_states_have_no_outgoing_transitions():
    for terminal in (
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.TIMED_OUT,
    ):
        assert not can_transition(terminal, TaskStatus.RUNNING)
        assert not can_transition(terminal, TaskStatus.FAILED)
