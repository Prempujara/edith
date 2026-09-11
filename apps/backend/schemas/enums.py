"""Enumerations shared across the EDITH backend domain.

All values are drawn directly from the authoritative baseline in
``docs/EDITH_SYSTEM_ARCHITECTURE.md`` (agent capabilities §13, task
lifecycle §15, event catalogue §16, permission levels §7).
"""

from __future__ import annotations

from enum import Enum


class AgentName(str, Enum):
    """The three agents defined by the baseline (§3)."""

    JARVIS = "JARVIS"
    EDITH = "EDITH"
    FRIDAY = "FRIDAY"


class Capability(str, Enum):
    """Agent capabilities as enumerated in the Agent Registry (§13)."""

    # JARVIS
    CODING = "coding"
    DEBUGGING = "debugging"
    GIT = "git"
    GITHUB = "github"
    WEB = "web"
    # EDITH
    COMPUTER_CONTROL = "computer_control"
    BROWSER = "browser"
    SCREEN = "screen"
    # FRIDAY
    FILE_MANAGEMENT = "file_management"
    DOCUMENT_OPERATIONS = "document_operations"


class PermissionLevel(str, Enum):
    """Tool permission levels (§7). Present for typing; enforcement is future work."""

    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    DESTRUCTIVE = "DESTRUCTIVE"


class TaskStatus(str, Enum):
    """Task lifecycle states (§15).

    ``RUNNING`` is the active-execution state (kept for compatibility; the
    baseline prose calls this "in progress").

    ``CANCELLED`` and ``TIMED_OUT`` are defined terminal states that are not
    yet *driven* by any code: cancellation behaviour lands in M2.4 and timeout
    enforcement in M2.3. They are declared here so the lifecycle machine and
    persisted data are ready for those milestones.
    """

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class EventType(str, Enum):
    """Event catalogue (§16)."""

    TASK_CREATED = "task.created"
    TASK_QUEUED = "task.queued"
    TASK_STARTED = "task.started"
    AGENT_SELECTED = "agent.selected"
    AGENT_DELEGATED = "agent.delegated"
    AGENT_STARTED = "agent.started"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    AGENT_COMPLETED = "agent.completed"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
