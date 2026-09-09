"""Deterministic offline LLM client — FOR TESTS AND LOCAL DEVELOPMENT ONLY.

This fake never performs network I/O. Its default output *varies with the
request* (it echoes the request text and a detected language) so tests can
prove the real request flows through the Coding Service — it deliberately does
NOT hard-code a factorial answer. It can also be constructed to raise a chosen
error or to return a canned (possibly malformed) response, so failure handling
can be exercised deterministically.
"""

from __future__ import annotations

import json


class FakeLLMClient:
    """A configurable, deterministic stand-in for a real LLM provider."""

    model = "fake-llm-1"
    is_mock = True

    def __init__(
        self,
        *,
        response: str | None = None,
        error: Exception | None = None,
    ) -> None:
        # If set, complete() raises this (simulates provider failure/timeout).
        self._error = error
        # If set, complete() returns this verbatim (simulates malformed output).
        self._response = response
        # Recorded inputs so tests can assert the request was passed through.
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.calls = 0

    def complete(self, *, system: str, user: str) -> str:
        self.calls += 1
        self.last_system = system
        self.last_user = user
        if self._error is not None:
            raise self._error
        if self._response is not None:
            return self._response
        return self._default_response(user)

    # --- deterministic default output ----------------------------------
    def _default_response(self, user: str) -> str:
        language = self._detect_language(user)
        request = " ".join(user.split())
        code = self._stub_code(language, request)
        summary = f"Offline fake output for request: {request}"
        return json.dumps({"language": language, "code": code, "summary": summary})

    @staticmethod
    def _detect_language(user: str) -> str:
        """Best-effort language sniff. Confined to this test double; the real
        Coding Service never keyword-matches to decide what to generate."""
        text = user.lower()
        if "javascript" in text or "node" in text:
            return "javascript"
        if "typescript" in text:
            return "typescript"
        if "java" in text:
            return "java"
        if "c++" in text or "cpp" in text:
            return "c++"
        if "c#" in text or "csharp" in text:
            return "c#"
        if "golang" in text or " go " in f" {text} ":
            return "go"
        if "rust" in text:
            return "rust"
        if "ruby" in text:
            return "ruby"
        return "python"

    @staticmethod
    def _stub_code(language: str, request: str) -> str:
        """A minimal, language-appropriate stub that echoes the request so the
        output is obviously request-derived (and never a fixed factorial)."""
        line_comment = {
            "python": "#",
            "ruby": "#",
            "java": "//",
            "javascript": "//",
            "typescript": "//",
            "c++": "//",
            "c#": "//",
            "go": "//",
            "rust": "//",
        }.get(language, "#")
        return (
            f"{line_comment} Task: {request}\n"
            f"{line_comment} NOTE: offline fake output — configure a real LLM "
            f"provider for working {language} code.\n"
        )
