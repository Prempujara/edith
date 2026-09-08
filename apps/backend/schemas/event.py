"""Event model (baseline §16).

An event records meaningful system activity. Each event carries enough
information to reconstruct dashboard activity, task history, and agent
communication visualisation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from .enums import AgentName, EventType


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Event(BaseModel):
    """A single recorded event tied to a task."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    task_id: str
    type: EventType
    agent: AgentName | None = Field(
        default=None, description="Agent that produced the event, if any."
    )
    timestamp: datetime = Field(default_factory=_now)
    payload: dict = Field(default_factory=dict)
