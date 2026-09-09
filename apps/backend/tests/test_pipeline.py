"""Tests for JARVIS decisioning and the Runtime pipeline."""

from __future__ import annotations

import pytest

from runtime.registry import build_default_registry
from runtime.runtime import AgentRuntime
from runtime.store import TaskStore
from schemas.enums import AgentName, Capability, EventType, TaskStatus
from services.coding_service import CodingService
from services.jarvis_service import JarvisService
from services.llm.fake import FakeLLMClient


def _jarvis() -> JarvisService:
    """JARVIS wired with an offline, fake-backed Coding Service."""
    return JarvisService(build_default_registry(), CodingService(FakeLLMClient()))


@pytest.fixture
def runtime():
    registry = build_default_registry()
    store = TaskStore()
    jarvis = JarvisService(registry, CodingService(FakeLLMClient()))
    return AgentRuntime(registry, store, jarvis), store


def test_jarvis_classifies_coding_as_own():
    decision = _jarvis().decide("Create a Python factorial program")
    assert decision.capability == Capability.CODING
    assert decision.handled_directly is True
    assert decision.target_agent == AgentName.JARVIS


def test_jarvis_delegates_file_management_to_friday():
    decision = _jarvis().decide("Organize the files in my downloads folder")
    assert decision.capability == Capability.FILE_MANAGEMENT
    assert decision.handled_directly is False
    assert decision.target_agent == AgentName.FRIDAY


def test_jarvis_delegates_computer_control_to_edith():
    decision = _jarvis().decide("Open the browser and navigate to the app")
    assert decision.capability == Capability.COMPUTER_CONTROL
    assert decision.handled_directly is False
    assert decision.target_agent == AgentName.EDITH


def test_direct_coding_pipeline(runtime):
    rt, store = runtime
    task = rt.submit_command("Create a Python factorial program")
    assert task.status == TaskStatus.COMPLETED
    assert task.assigned_agent == AgentName.JARVIS
    # Structured coding result, now produced via the Coding Service rather than
    # a hardcoded method. Validate the shape, not exact generated content.
    assert task.result["kind"] == "coding"
    assert task.result["language"] == "python"
    assert isinstance(task.result["code"], str) and task.result["code"].strip()
    assert task.result["mock"] is True
    # No child task created for the direct path.
    assert task.parent_task_id is None


def test_delegated_friday_pipeline(runtime):
    rt, store = runtime
    task = rt.submit_command("Please organize my project files into folders")
    assert task.status == TaskStatus.COMPLETED
    assert task.result["kind"] == "delegation"
    assert task.result["delegated_to"] == "FRIDAY"

    child_id = task.result["child_task_id"]
    child = store.get(child_id)
    assert child is not None
    assert child.parent_task_id == task.id
    assert child.assigned_agent == AgentName.FRIDAY
    assert child.status == TaskStatus.COMPLETED
    assert child.result["kind"] == "file_management"


def test_delegation_emits_agent_delegated_event(runtime):
    rt, store = runtime
    task = rt.submit_command("organize my files")
    types = [e.type for e in store.get_events(task.id)]
    assert EventType.AGENT_DELEGATED in types
    assert EventType.AGENT_SELECTED in types
    assert EventType.TASK_COMPLETED in types


def test_direct_path_has_no_delegation_event(runtime):
    rt, store = runtime
    task = rt.submit_command("write a python script")
    types = [e.type for e in store.get_events(task.id)]
    assert EventType.AGENT_DELEGATED not in types
    assert EventType.AGENT_SELECTED in types
