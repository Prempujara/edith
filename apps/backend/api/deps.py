"""Shared singletons for the API layer.

For the in-memory vertical slice, the registry, store, JARVIS service, and
Runtime are process-wide singletons wired together once. When persistence
arrives, these become request/session-scoped dependencies instead.
"""

from __future__ import annotations

from functools import lru_cache

from runtime.registry import AgentRegistry, build_default_registry
from runtime.runtime import AgentRuntime
from runtime.store import TaskStore
from services.jarvis_service import JarvisService


@lru_cache(maxsize=1)
def _singletons() -> tuple[AgentRegistry, TaskStore, AgentRuntime]:
    registry = build_default_registry()
    store = TaskStore()
    jarvis = JarvisService(registry)
    runtime = AgentRuntime(registry, store, jarvis)
    return registry, store, runtime


def get_registry() -> AgentRegistry:
    return _singletons()[0]


def get_store() -> TaskStore:
    return _singletons()[1]


def get_runtime() -> AgentRuntime:
    return _singletons()[2]
