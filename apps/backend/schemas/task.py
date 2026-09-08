"""Task model (baseline §14).

A task represents an operation requested by the user or delegated by
another agent. Delegated tasks link back to their parent via
``parent_task_id`` (§14).
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import AgentName, TaskStatus


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Task(BaseModel):
    """A unit of work tracked through the lifecycle (§15)."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    parent_task_id: str | None = None
    requester: str = Field(
        ..., description="Originating actor: 'user' or an agent name."
    )
    assigned_agent: AgentName | None = None
    input: str = Field(..., description="The command / request text.")
    status: TaskStatus = TaskStatus.CREATED
    priority: int = 0
    created_at: datetime = Field(default_factory=_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict | None = None
    error: str | None = None
