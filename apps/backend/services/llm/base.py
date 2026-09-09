"""LLM client abstraction: a small, provider-independent text-completion port.

Callers (e.g. the Coding Service) depend only on :class:`LLMClient` and the
exception hierarchy here — never on a vendor SDK. Error messages are written to
be user-safe: they must not embed API keys, credentials, or raw provider
internals, because the Runtime surfaces ``str(exc)`` as the task error.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class LLMError(RuntimeError):
    """Base class for LLM transport/configuration failures (user-safe message)."""


class LLMConfigError(LLMError):
    """The provider is not usable: missing API key, missing SDK, bad config."""


class LLMTimeoutError(LLMError):
    """The provider did not respond within the configured timeout."""


@runtime_checkable
class LLMClient(Protocol):
    """A minimal synchronous text-completion client.

    Implementations return the model's raw text output; parsing/structuring is
    the caller's responsibility. Transport failures must be raised as
    :class:`LLMError` (or a subclass) with a user-safe message.
    """

    @property
    def model(self) -> str:
        """Identifier of the underlying model (for provenance/reporting)."""
        ...

    @property
    def is_mock(self) -> bool:
        """True for offline/fake clients used in tests and local development."""
        ...

    def complete(self, *, system: str, user: str) -> str:
        """Return the model's completion for a system prompt and user message."""
        ...
