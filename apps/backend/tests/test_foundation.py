"""Tests for the foundation layer: registry, task model, lifecycle, store."""

from __future__ import annotations

import pytest

from runtime.lifecycle import InvalidTransitionError, assert_transition, can_transition
from runtime.registry import build_default_registry
from runtime.store import TaskStore
from schemas.agent import Agent
from schemas.enums import AgentName, Capability, TaskStatus
from schemas.event import Event, EventType
from schemas.task import Task


def test_default_registry_has_three_agents():
    reg = build_default_registry()
    names = {a.name for a in reg.list_agents()}
    assert names == {AgentName.JARVIS, AgentName.EDITH, AgentName.FRIDAY}


def test_registry_capabilities_match_baseline():
    reg = build_default_registry()
    assert reg.get(AgentName.JARVIS).has_capability(Capability.CODING)
    assert reg.get(AgentName.FRIDAY).has_capability(Capability.FILE_MANAGEMENT)
    assert reg.get(AgentName.EDITH).has_capability(Capability.COMPUTER_CONTROL)
    # Coding is NOT EDITH's job per baseline §13.
    assert not reg.get(AgentName.EDITH).has_capability(Capability.CODING)


def test_find_by_capability():
    reg = build_default_registry()
    assert reg.find_by_capability(Capability.FILE_MANAGEMENT).name == AgentName.FRIDAY
    assert reg.find_by_capability(Capability.CODING).name == AgentName.JARVIS


def test_lifecycle_valid_path():
    assert can_transition(TaskStatus.CREATED, TaskStatus.QUEUED)
    assert can_transition(TaskStatus.QUEUED, TaskStatus.RUNNING)
    assert can_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED)
    assert can_transition(TaskStatus.RUNNING, TaskStatus.FAILED)


def test_lifecycle_rejects_invalid():
    assert not can_transition(TaskStatus.CREATED, TaskStatus.COMPLETED)
    assert not can_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING)
    with pytest.raises(InvalidTransitionError):
        assert_transition(TaskStatus.CREATED, TaskStatus.RUNNING)


def test_store_roundtrip():
    store = TaskStore()
    task = Task(requester="user", input="hello")
    store.add(task)
    assert store.get(task.id) is task
    assert store.list_tasks() == [task]
    ev = Event(task_id=task.id, type=EventType.TASK_CREATED)
    store.add_event(ev)
    assert store.get_events(task.id) == [ev]


def test_task_defaults():
    task = Task(requester="user", input="do a thing")
    assert task.status == TaskStatus.CREATED
    assert task.parent_task_id is None
    assert task.id
