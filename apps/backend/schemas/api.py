"""Request/response schemas for the /api/v1 surface."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import AgentName, Capability, EventType, TaskStatus


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1, description="The user's command text.")


class AgentResponse(BaseModel):
    name: AgentName
    role: str
    capabilities: list[Capability]


class TaskResponse(BaseModel):
    id: str
    parent_task_id: str | None
    requester: str
    assigned_agent: AgentName | None
    input: str
    status: TaskStatus
    priority: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    result: dict | None
    error: str | None


class EventResponse(BaseModel):
    id: str
    task_id: str
    type: EventType
    agent: AgentName | None
    timestamp: datetime
    payload: dict


class CommandResponse(BaseModel):
    """Returned by POST /api/v1/commands: the resulting (root) task."""

    task: TaskResponse
