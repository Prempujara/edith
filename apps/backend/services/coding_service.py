"""Coding Service: JARVIS's code-generation engine (baseline §3.1).

JARVIS owns the CODING capability. This service turns a natural-language
programming request into a structured :class:`~schemas.coding.CodingResult` by
prompting an LLM (through the provider-independent
:class:`~services.llm.base.LLMClient` port) and robustly parsing its response.

It deliberately does **not** keyword-match to decide *what* code to write — the
user's actual request is sent to the model. Malformed model output is rejected
as a controlled :class:`CodingError` rather than being passed off as a valid
result.
"""

from __future__ import annotations

import json
import logging

from schemas.coding import CodingResult
from services.llm.base import LLMClient

logger = logging.getLogger(__name__)


class CodingError(RuntimeError):
    """The model response could not be turned into a valid CodingResult.

    Carries a user-safe message (no provider internals); the Runtime surfaces
    it via the standard task-failure path.
    """


_SYSTEM_PROMPT = """\
You are JARVIS's code-generation engine for the EDITH platform.

Read the user's programming request and produce source code that correctly and
directly fulfills THAT request — the right language and the right task. Never
substitute an unrelated example (for instance, do not return a factorial
program unless the user actually asked for one).

Guidelines:
- Infer the programming language from the request. If none is stated, choose the
  most appropriate mainstream language.
- Return a complete, self-contained solution for the request, not a fragment.
- Stay focused: no unrelated boilerplate.

Respond with EXACTLY ONE JSON object and nothing else. No markdown, no code
fences, no text before or after. The object must have exactly these keys:
  "language": string  - e.g. "python", "java", "javascript"
  "code":     string  - the complete source code as a single JSON string
  "summary":  string  - one or two sentences describing what the code does

The "code" value must be valid JSON (escape newlines and quotes). Do not wrap
the response in ``` fences."""


class CodingService:
    """Generates code for JARVIS via an injected LLM client."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def generate(self, request: str) -> CodingResult:
        """Generate code for ``request``.

        Raises:
            CodingError: the request is empty or the model response is malformed.
            LLMError: the provider is misconfigured, timed out, or failed.
        """
        if not request or not request.strip():
            raise CodingError("No coding request was provided.")

        raw = self._llm.complete(system=_SYSTEM_PROMPT, user=request.strip())
        fields = self._parse(raw)

        return CodingResult(
            language=fields["language"],
            code=fields["code"],
            summary=fields["summary"],
            mock=self._llm.is_mock,
            model=self._llm.model,
        )

    # --- response parsing ----------------------------------------------
    @staticmethod
    def _parse(raw: str) -> dict[str, str]:
        """Extract and validate the JSON object from a model response.

        Robust to leading prose and trailing commentary/code fences: it decodes
        the first complete JSON object found. Any deviation from the required
        shape raises :class:`CodingError`.
        """
        text = (raw or "").strip()
        if not text:
            raise CodingError("The coding model returned an empty response.")

        start = text.find("{")
        if start == -1:
            raise CodingError("The coding model did not return a JSON object.")

        try:
            data, _ = json.JSONDecoder().raw_decode(text[start:])
        except json.JSONDecodeError as exc:
            raise CodingError("The coding model returned malformed JSON.") from exc

        if not isinstance(data, dict):
            raise CodingError("The coding model response was not a JSON object.")

        language = data.get("language")
        code = data.get("code")
        summary = data.get("summary")
        if not _nonempty_str(language) or not _nonempty_str(code) or not _nonempty_str(summary):
            raise CodingError(
                "The coding model response was missing required fields "
                "(language, code, summary)."
            )

        return {
            "language": language.strip(),
            "code": code,
            "summary": summary.strip(),
        }


def _nonempty_str(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""
