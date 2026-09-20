"""Backend configuration (core cross-cutting concern).

Minimal, dependency-light settings loaded from environment variables (with an
optional ``.env`` file via python-dotenv, which is already a project
dependency). No secrets are hardcoded; credentials come from the environment.

Exposed knobs (all optional; sensible defaults):

    EDITH_LLM_API_KEY   API key for the LLM provider. If absent, the backend
                        falls back to the offline fake client (mock mode).
    ANTHROPIC_API_KEY   Accepted as a fallback for EDITH_LLM_API_KEY.
    EDITH_LLM_MODEL     Model identifier (default: ``claude-sonnet-5``).
    EDITH_LLM_TIMEOUT   Provider request timeout in seconds (default: 30).
    EDITH_LLM_MOCK      Force the offline fake client even if a key is set
                        (``1``/``true``/``yes``/``on``).
    EDITH_TASK_RETENTION_LIMIT
                        Max number of tasks retained in the in-memory store
                        before the oldest fully-terminal task families are
                        evicted (default: 1000). ``0`` or a negative value
                        disables the bound (unbounded, the original behaviour).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from dotenv import load_dotenv

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
DEFAULT_TIMEOUT = 30.0
DEFAULT_TASK_RETENTION_LIMIT = 1000

_TRUTHY = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Immutable snapshot of backend configuration."""

    llm_api_key: str | None
    llm_model: str
    llm_timeout: float
    llm_force_mock: bool
    task_retention_limit: int | None

    @property
    def use_mock(self) -> bool:
        """Whether to use the offline fake LLM client.

        True when mock mode is explicitly forced, or when no API key is
        configured (so the demo still runs offline without credentials).
        """
        return self.llm_force_mock or not self.llm_api_key


def _parse_retention(raw: str | None) -> int | None:
    """Parse the retention limit; unset/invalid -> default, <=0 -> unbounded."""
    if raw is None or raw.strip() == "":
        return DEFAULT_TASK_RETENTION_LIMIT
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_TASK_RETENTION_LIMIT
    return value if value > 0 else None


def _settings_from_env(env: Mapping[str, str]) -> Settings:
    api_key = env.get("GEMINI_API_KEY") or env.get("EDITH_LLM_API_KEY") or env.get("ANTHROPIC_API_KEY") or None
    model = env.get("EDITH_LLM_MODEL") or DEFAULT_MODEL

    raw_timeout = env.get("EDITH_LLM_TIMEOUT")
    try:
        timeout = float(raw_timeout) if raw_timeout else DEFAULT_TIMEOUT
    except ValueError:
        timeout = DEFAULT_TIMEOUT

    force_mock = (env.get("EDITH_LLM_MOCK") or "").strip().lower() in _TRUTHY
    retention = _parse_retention(env.get("EDITH_TASK_RETENTION_LIMIT"))
    return Settings(
        llm_api_key=api_key,
        llm_model=model,
        llm_timeout=timeout,
        llm_force_mock=force_mock,
        task_retention_limit=retention,
    )


def load_settings(*, use_dotenv: bool = True) -> Settings:
    """Build a :class:`Settings` from the process environment.

    ``use_dotenv`` loads a ``.env`` file if present (never overriding variables
    already set in the environment). Tests pass ``use_dotenv=False`` for full
    determinism regardless of any local ``.env``.
    """
    if use_dotenv:
        load_dotenv()
    return _settings_from_env(os.environ)
