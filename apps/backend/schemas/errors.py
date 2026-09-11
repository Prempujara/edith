"""Structured, user-safe error representation for tasks (M2.1).

A :class:`TaskError` is what ends up in ``Task.error`` and is serialized over
the API. It is deliberately minimal and **safe to show to a user**:

- ``code``    machine-readable category (e.g. ``"CODING_ERROR"``).
- ``message`` short, human-readable, curated message. Never a raw stack trace,
  provider internals, secrets, or credentials.
- ``details`` optional, small, safe metadata (e.g. a related child task id).

Detailed diagnostics (stack traces, provider messages) are kept out of this
object entirely; the Runtime logs them server-side instead. See
``runtime.runtime`` for how exceptions are mapped onto this shape.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TaskError(BaseModel):
    """A user-safe description of why a task failed."""

    code: str = Field(..., description="Machine-readable error category.")
    message: str = Field(..., description="User-safe, human-readable summary.")
    details: dict | None = Field(
        default=None,
        description="Optional small, safe metadata. Never secrets or stack traces.",
    )
