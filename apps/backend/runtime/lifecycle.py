"""Task lifecycle state machine (baseline §15).

Enforces the lifecycle and prevents invalid transitions:

    CREATED -> QUEUED -> RUNNING -> COMPLETED
    CREATED | QUEUED | RUNNING -> FAILED
    CREATED | QUEUED | RUNNING -> CANCELLED
                       RUNNING -> TIMED_OUT

Failure is reachable from every non-terminal state: a task can fail before it
ever starts (e.g. the decision stage raises while the task is still CREATED),
so ``FAILED`` must be a legal target from CREATED and QUEUED as well as RUNNING.

``CANCELLED`` and ``TIMED_OUT`` are legal targets but no code performs those
transitions yet (cancellation is M2.4; timeout is M2.3). Terminal states have
no outgoing edges, so a terminal task can never be transitioned again.
"""

from __future__ import annotations

from schemas.enums import TaskStatus

# Terminal states have no outgoing edges.
TERMINAL_STATES: frozenset[TaskStatus] = frozenset(
    {
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.TIMED_OUT,
    }
)

# Allowed forward transitions.
_ALLOWED: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.CREATED: {TaskStatus.QUEUED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED,
        TaskStatus.TIMED_OUT,
    },
    TaskStatus.COMPLETED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
    TaskStatus.TIMED_OUT: set(),
}


def is_terminal(status: TaskStatus) -> bool:
    return status in TERMINAL_STATES


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
