"""Task/event persistence boundary (M2.1; ADR-005).

The Runtime depends on the :class:`TaskRepository` *interface* rather than on a
concrete store, so the in-memory implementation can be swapped for a persistent
one later (SQLite/Postgres, per ADR-005) without touching the Runtime or the
API. This milestone keeps the in-memory :class:`runtime.store.TaskStore` as the
only implementation — no database is introduced.

The interface mirrors the operations callers already perform against the store:
task upsert/lookup/listing and per-task event append/listing. It is a
structural :class:`typing.Protocol`; the concrete store satisfies it simply by
providing these methods (no inheritance required).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from schemas.event import Event
from schemas.task import Task


@runtime_checkable
class TaskRepository(Protocol):
    """Storage boundary for tasks and their event streams."""

    # --- tasks ---------------------------------------------------------
    def add(self, task: Task) -> Task:
        """Insert (or replace) ``task`` and return it."""
        ...

    def get(self, task_id: str) -> Task | None:
        """Return the live task for ``task_id``, or ``None`` if unknown."""
        ...

    def list_tasks(self) -> list[Task]:
        """Return a snapshot list of all currently retained tasks."""
        ...

    # --- events --------------------------------------------------------
    def add_event(self, event: Event) -> Event:
        """Append ``event`` to its task's stream, assigning its ``seq``."""
        ...

    def get_events(self, task_id: str) -> list[Event]:
        """Return a task's events in deterministic (ascending ``seq``) order."""
        ...
