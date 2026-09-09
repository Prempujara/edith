"""Shared singletons for the API layer.

For the in-memory vertical slice, the registry, store, Coding Service, JARVIS
service, and Runtime are process-wide singletons wired together once. When
persistence arrives, these become request/session-scoped dependencies instead.
"""

from __future__ import annotations

from functools import lru_cache

from core.config import Settings, load_settings
from runtime.registry import AgentRegistry, build_default_registry
from runtime.runtime import AgentRuntime
from runtime.store import TaskStore
from services.coding_service import CodingService
from services.jarvis_service import JarvisService
from services.llm.base import LLMClient
from services.llm.fake import FakeLLMClient


def _build_llm_client(settings: Settings) -> LLMClient:
    """Select the LLM client according to configuration.

    Uses the offline fake in mock mode (or when no API key is configured);
    otherwise the real provider adapter. The vendor SDK is imported lazily
    inside the adapter, so it is only needed when a real provider is used.
    """
    if settings.use_mock:
        return FakeLLMClient()

    from services.llm.anthropic_client import AnthropicClient

    return AnthropicClient(
        api_key=settings.llm_api_key or "",
        model=settings.llm_model,
        timeout=settings.llm_timeout,
    )


@lru_cache(maxsize=1)
def _singletons() -> tuple[AgentRegistry, TaskStore, AgentRuntime]:
    settings = load_settings()
    registry = build_default_registry()
    store = TaskStore()
    coding = CodingService(_build_llm_client(settings))
    jarvis = JarvisService(registry, coding)
    runtime = AgentRuntime(registry, store, jarvis)
    return registry, store, runtime


def get_registry() -> AgentRegistry:
    return _singletons()[0]


def get_store() -> TaskStore:
    return _singletons()[1]


def get_runtime() -> AgentRuntime:
    return _singletons()[2]
