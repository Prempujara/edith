"""In-memory Task Store and Event log (baseline §14, §16; ADR-005).

Concrete in-memory implementation of :class:`runtime.repository.TaskRepository`.
It is the only storage implementation in M2.1 — no database is introduced.

Three properties were added for production-readiness while keeping the surface
small:

- **Thread-safety.** All reads and mutations are guarded by a lock. Execution
  is still synchronous today, but M2.2 introduces concurrent execution; the
  store's containers are safe for that ahead of time. (The lock protects the
  store's structures; individual :class:`~schemas.task.Task` objects handed out
  by :meth:`get` are still mutated in place by the Runtime, single-writer, as
  before.)
- **Monotonic event sequencing.** Each event gets a per-task, 1-based ``seq``
  so a task's stream has a deterministic total order and events are never
  silently overwritten.
- **Bounded retention.** An optional ``max_tasks`` cap evicts the oldest
  *fully-terminal* task families (a root task together with its children) when
  exceeded. Active (non-terminal) tasks are never evicted, and a family is only
  evicted once every member is terminal, so parent/child records and their
  events stay consistent. ``max_tasks=None`` (the default) keeps the original
  unbounded behaviour.

No persistence yet: everything lives in process memory and is lost on restart.
"""

from __future__ import annotations

import threading

from runtime.lifecycle import is_terminal
from schemas.event import Event
from schemas.task import Task


class TaskStore:
    """Stores tasks and their events in process memory (thread-safe)."""

    def __init__(self, max_tasks: int | None = None) -> None:
        # Insertion order is preserved by dict, which defines eviction order.
        self._tasks: dict[str, Task] = {}
        self._events: dict[str, list[Event]] = {}
        self._max_tasks = max_tasks if (max_tasks and max_tasks > 0) else None
        self._lock = threading.Lock()

    # --- tasks ---------------------------------------------------------
    def add(self, task: Task) -> Task:
        with self._lock:
            self._tasks[task.id] = task
            self._events.setdefault(task.id, [])
            self._enforce_retention()
        return task

    def get(self, task_id: str) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    # --- events --------------------------------------------------------
    def add_event(self, event: Event) -> Event:
        with self._lock:
            stream = self._events.setdefault(event.task_id, [])
            event.seq = len(stream) + 1  # per-task, 1-based, monotonic
            stream.append(event)
            self._enforce_retention()
        return event

    def get_events(self, task_id: str) -> list[Event]:
        with self._lock:
            events = list(self._events.get(task_id, []))
        return sorted(events, key=lambda e: e.seq)

    # --- retention -----------------------------------------------------
    def _enforce_retention(self) -> None:
        """Evict oldest fully-terminal families until within ``max_tasks``.

        Caller must hold ``self._lock``. Never evicts active tasks, and only
        evicts a family (root + children) once every member is terminal, so no
        active task is dropped and no parent/child reference is left dangling.
        """
        limit = self._max_tasks
        if limit is None or len(self._tasks) <= limit:
            return

        # Index children by parent id in a single pass (insertion order).
        children: dict[str, list[str]] = {}
        for tid, task in self._tasks.items():
            if task.parent_task_id is not None:
                children.setdefault(task.parent_task_id, []).append(tid)

        for root_id in list(self._tasks.keys()):  # oldest first
            if len(self._tasks) <= limit:
                break
            root = self._tasks.get(root_id)
            if root is None or root.parent_task_id is not None:
                continue  # already evicted, or not a root
            if not is_terminal(root.status):
                continue  # active root -> retain the whole family
            child_ids = children.get(root_id, [])
            if not self._family_fully_terminal(child_ids):
                continue  # a child is still active -> retain the whole family
            for cid in child_ids:
                self._tasks.pop(cid, None)
                self._events.pop(cid, None)
            self._tasks.pop(root_id, None)
            self._events.pop(root_id, None)

    def _family_fully_terminal(self, child_ids: list[str]) -> bool:
        for cid in child_ids:
            child = self._tasks.get(cid)
            if child is not None and not is_terminal(child.status):
                return False
        return True
