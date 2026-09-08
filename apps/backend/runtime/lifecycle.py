"""Task lifecycle state machine (baseline §15).

Enforces the minimum lifecycle and prevents invalid transitions:

    CREATED -> QUEUED -> RUNNING -> COMPLETED
                            RUNNING -> FAILED

CANCELLED is reachable from the non-terminal states (the baseline permits
cancellation "if required"); it is not used by the current slice.
"""

from __future__ import annotations

from schemas.enums import TaskStatus

# Allowed forward transitions. Terminal states have no outgoing edges.
_ALLOWED: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
}


class InvalidTransitionError(ValueError):
    """Raised when a task is moved between incompatible states."""

    def __init__(self, current: TaskStatus, target: TaskStatus) -> None:
        super().__init__(f"Invalid task transition: {current.value} -> {target.value}")
        self.current = current
        self.target = target


def can_transition(current: TaskStatus, target: TaskStatus) -> bool:
    return target in _ALLOWED.get(current, set())


def assert_transition(current: TaskStatus, target: TaskStatus) -> None:
    if not can_transition(current, target):
        raise InvalidTransitionError(current, target)
