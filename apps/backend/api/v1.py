"""Versioned API routes under /api/v1 (baseline §14, §16).

Endpoints:
    POST /api/v1/commands           submit a user command
    GET  /api/v1/agents             list registered agents
    GET  /api/v1/tasks/{task_id}    fetch a task
    GET  /api/v1/tasks/{task_id}/events   fetch a task's events
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_registry, get_runtime, get_store
from runtime.registry import AgentRegistry
from runtime.runtime import AgentRuntime
from runtime.store import TaskStore
from schemas.api import (
    AgentResponse,
    CommandRequest,
    CommandResponse,
    EventResponse,
    TaskResponse,
)

router = APIRouter(prefix="/api/v1", tags=["v1"])


@router.post("/commands", response_model=CommandResponse)
def submit_command(
    body: CommandRequest,
    runtime: AgentRuntime = Depends(get_runtime),
) -> CommandResponse:
    """Run a command through JARVIS -> Runtime -> (JARVIS | delegate)."""
    task = runtime.submit_command(body.command)
    return CommandResponse(task=TaskResponse(**task.model_dump()))


@router.get("/agents", response_model=list[AgentResponse])
def list_agents(
    registry: AgentRegistry = Depends(get_registry),
) -> list[AgentResponse]:
    return [AgentResponse(**a.model_dump()) for a in registry.list_agents()]


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    store: TaskStore = Depends(get_store),
) -> TaskResponse:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task.model_dump())


@router.get("/tasks/{task_id}/events", response_model=list[EventResponse])
def get_task_events(
    task_id: str,
    store: TaskStore = Depends(get_store),
) -> list[EventResponse]:
    if store.get(task_id) is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return [EventResponse(**e.model_dump()) for e in store.get_events(task_id)]
