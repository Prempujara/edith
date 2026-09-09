"""Anthropic adapter for the LLM port.

The Anthropic SDK is imported lazily and used **only** inside this module, so
the rest of the backend (and the whole test suite) runs without the vendor
package installed. All provider errors are converted into user-safe
:class:`~services.llm.base.LLMError` variants; raw SDK messages and credentials
are never propagated to callers.
"""

from __future__ import annotations

import logging

from services.llm.base import LLMConfigError, LLMError, LLMTimeoutError

logger = logging.getLogger(__name__)

# Generous default for a single code-generation response. Kept internal to the
# adapter; not part of the public configuration surface.
_DEFAULT_MAX_TOKENS = 4096


class AnthropicClient:
    """Text-completion client backed by the Anthropic Messages API."""

    is_mock = False

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout: float,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> None:
        if not api_key:
            raise LLMConfigError("The coding provider is not configured (missing API key).")
        self._model = model
        self._max_tokens = max_tokens
        # Lazy import: the SDK is only required when a real provider is used.
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise LLMConfigError(
                "The 'anthropic' package is not installed on the server."
            ) from exc
        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout)

    @property
    def model(self) -> str:
        return self._model

    def complete(self, *, system: str, user: str) -> str:
        anthropic = self._anthropic
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except anthropic.APITimeoutError as exc:
            logger.warning("Anthropic request timed out")
            raise LLMTimeoutError(
                "The coding provider timed out. Please try again."
            ) from exc
        except Exception as exc:  # SDK/network/auth errors — never leak details
            logger.exception("Anthropic request failed")
            raise LLMError(
                "The coding provider failed to complete the request."
            ) from exc
        return self._extract_text(response)

    @staticmethod
    def _extract_text(response) -> str:
        """Concatenate the text blocks of a Messages API response."""
        parts: list[str] = []
        for block in getattr(response, "content", None) or []:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()
