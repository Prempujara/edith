"""In-memory Task Store and Event log (baseline §14, §16; ADR-005).

Deliberately in-memory for the first vertical slice. The public surface is
kept small so a persistent implementation can replace it later without
touching callers.
"""

from __future__ import annotations

from schemas.event import Event
from schemas.task import Task


class TaskStore:
    """Stores tasks and their events in process memory."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._events: dict[str, list[Event]] = {}

    # --- tasks ---------------------------------------------------------
    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        self._events.setdefault(task.id, [])
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    # --- events --------------------------------------------------------
    def add_event(self, event: Event) -> Event:
        self._events.setdefault(event.task_id, []).append(event)
        return event

    def get_events(self, task_id: str) -> list[Event]:
        return list(self._events.get(task_id, []))
