"""Test working demo functionality for all 3 agents (JARVIS, EDITH, FRIDAY)."""

import pytest

from runtime.registry import build_default_registry
from runtime.store import TaskStore
from runtime.runtime import AgentRuntime
from schemas.enums import AgentName, TaskStatus
from services.coding_service import CodingService
from services.jarvis_service import JarvisService
from services.llm.fake import FakeLLMClient


@pytest.fixture
def runtime_fixture():
    registry = build_default_registry()
    store = TaskStore()
    llm = FakeLLMClient()
    coding_service = CodingService(llm=llm)
    jarvis_service = JarvisService(registry=registry, coding_service=coding_service)
    return AgentRuntime(registry=registry, store=store, jarvis=jarvis_service), store


def test_jarvis_agent_demo(runtime_fixture):
    runtime, store = runtime_fixture
    task = runtime.submit_command("Write a python function for factorial")

    assert task.status == TaskStatus.COMPLETED
    assert task.assigned_agent == AgentName.JARVIS
    assert task.result["kind"] == "coding"
    assert task.result["language"] == "python"


def test_edith_agent_demo(runtime_fixture):
    runtime, store = runtime_fixture
    task = runtime.submit_command("Open application browser and navigate to site")

    assert task.status == TaskStatus.COMPLETED
    assert task.assigned_agent == AgentName.JARVIS
    assert task.result["kind"] == "delegation"
    assert task.result["delegated_to"] == "EDITH"
    assert task.result["result"]["agent"] == "EDITH"
    assert task.result["result"]["kind"] == "computer_control"


def test_friday_agent_demo(runtime_fixture):
    runtime, store = runtime_fixture
    task = runtime.submit_command("Organize the project files into folders")

    assert task.status == TaskStatus.COMPLETED
    assert task.assigned_agent == AgentName.JARVIS
    assert task.result["kind"] == "delegation"
    assert task.result["delegated_to"] == "FRIDAY"
    assert task.result["result"]["agent"] == "FRIDAY"
    assert task.result["result"]["kind"] == "file_management"
