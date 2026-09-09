"""API-level and end-to-end tests via FastAPI's TestClient.

Runs in offline mock mode (forced by tests/conftest.py), so no network calls
are made and coding results are produced by the deterministic fake client.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_existing_root_unchanged(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"].startswith("Welcome to EDITH")


def test_existing_health_unchanged(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["service"] == "edith-backend"


def test_openapi_available(client):
    assert client.get("/openapi.json").status_code == 200


def test_list_agents(client):
    r = client.get("/api/v1/agents")
    assert r.status_code == 200
    names = {a["name"] for a in r.json()}
    assert names == {"JARVIS", "EDITH", "FRIDAY"}


def test_e2e_coding_direct(client):
    # Backward compatibility: the original command still works end to end, but
    # is now generated through the Coding Service (not a hardcoded method).
    r = client.post(
        "/api/v1/commands",
        json={"command": "Create a Python factorial program"},
    )
    assert r.status_code == 200
    task = r.json()["task"]
    assert task["status"] == "COMPLETED"
    assert task["assigned_agent"] == "JARVIS"
    result = task["result"]
    assert result["kind"] == "coding"
    assert result["language"] == "python"
    assert isinstance(result["code"], str) and result["code"].strip()
    assert result["mock"] is True


def test_e2e_coding_reverse_string_is_request_specific(client):
    r = client.post(
        "/api/v1/commands",
        json={"command": "Write a Python program to reverse a string"},
    )
    assert r.status_code == 200
    result = r.json()["task"]["result"]
    assert result["kind"] == "coding"
    assert result["language"] == "python"
    # The actual request drives generation; it is not a fixed factorial.
    assert "reverse a string" in result["code"].lower()
    assert "def factorial" not in result["code"].lower()


def test_e2e_coding_java_request(client):
    r = client.post(
        "/api/v1/commands",
        json={"command": "Create a Java class implementing a stack"},
    )
    assert r.status_code == 200
    result = r.json()["task"]["result"]
    assert result["kind"] == "coding"
    assert result["language"] == "java"
    assert "def factorial" not in result["code"].lower()


def test_e2e_delegation_to_friday(client):
    r = client.post(
        "/api/v1/commands",
        json={"command": "Organize the files in my project folder"},
    )
    assert r.status_code == 200
    task = r.json()["task"]
    assert task["status"] == "COMPLETED"
    assert task["result"]["kind"] == "delegation"
    assert task["result"]["delegated_to"] == "FRIDAY"

    # Fetch the task back.
    task_id = task["id"]
    got = client.get(f"/api/v1/tasks/{task_id}")
    assert got.status_code == 200
    assert got.json()["id"] == task_id

    # Events include the delegation.
    events = client.get(f"/api/v1/tasks/{task_id}/events").json()
    types = [e["type"] for e in events]
    assert "agent.selected" in types
    assert "agent.delegated" in types
    assert "task.completed" in types

    # Child task is retrievable and links back to the parent.
    child_id = task["result"]["child_task_id"]
    child = client.get(f"/api/v1/tasks/{child_id}").json()
    assert child["parent_task_id"] == task_id
    assert child["assigned_agent"] == "FRIDAY"
    assert child["status"] == "COMPLETED"


def test_unknown_task_404(client):
    assert client.get("/api/v1/tasks/does-not-exist").status_code == 404
    assert client.get("/api/v1/tasks/does-not-exist/events").status_code == 404


def test_empty_command_rejected(client):
    assert client.post("/api/v1/commands", json={"command": ""}).status_code == 422
