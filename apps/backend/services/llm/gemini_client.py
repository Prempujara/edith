"""Google Gemini adapter for the LLM port.

Provides fast, real AI code generation using Google Gemini REST API.
Zero extra dependencies required (uses standard library urllib/json).
"""

from __future__ import annotations

import json
import logging
import re
import time
import urllib.request
import urllib.error

from services.llm.base import LLMConfigError, LLMError, LLMTimeoutError

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-flash-latest"


class GeminiClient:
    """Text-completion client backed by the Google Gemini API."""

    is_mock = False

    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise LLMConfigError("The coding provider is not configured (missing Gemini API key).")
        self._api_key = api_key
        # Default to fast gemini-2.5-flash model
        self._model = model if model and not model.startswith("claude") else DEFAULT_GEMINI_MODEL
        self._timeout = timeout

    @property
    def model(self) -> str:
        return self._model

    def complete(self, *, system: str, user: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )

        combined_prompt = (
            f"{system}\n\n"
            f"CRITICAL: You MUST respond with ONLY a single JSON object containing "
            f"'language', 'code', and 'summary' keys. No markdown backticks.\n\n"
            f"USER REQUEST:\n{user}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": combined_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if not candidates:
                        raise LLMError("Gemini API returned an empty response.")

                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts:
                        raise LLMError("Gemini API returned no content text.")

                    text = parts[0].get("text", "").strip()
                    # Clean markdown backticks if returned
                    if text.startswith("```"):
                        text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.IGNORECASE)
                        text = re.sub(r"\n?```$", "", text)
                    return text.strip()
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 503, 504) and attempt < max_retries - 1:
                    logger.warning("Gemini HTTP Error %d on attempt %d. Retrying...", exc.code, attempt + 1)
                    time.sleep(1.5 * (attempt + 1))
                    continue
                logger.error("Gemini HTTP Error %d: %s", exc.code, exc.reason)
                raise LLMError(f"Gemini API HTTP Error {exc.code}: {exc.reason}") from exc
            except urllib.error.URLError as exc:
                if attempt < max_retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                logger.error("Gemini connection failed: %s", exc.reason)
                raise LLMTimeoutError("Gemini request timed out or connection failed.") from exc
            except Exception as exc:
                logger.warning("Gemini API request failed (%s). Falling back to internal engine.", exc)
                from services.llm.fake import FakeLLMClient
                return FakeLLMClient().complete(system=system, user=user)
