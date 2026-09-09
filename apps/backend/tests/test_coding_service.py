"""Tests for the Coding Service using the offline FakeLLMClient.

These are fully deterministic and never make network calls. They verify that
the user's actual request drives generation (no hardcoded example), that the
result is a well-formed CodingResult, and that malformed/failed provider
responses become controlled errors.
"""

from __future__ import annotations

import json

import pytest

from schemas.coding import CodingResult
from services.coding_service import CodingError, CodingService
from services.llm.base import LLMError, LLMTimeoutError
from services.llm.fake import FakeLLMClient


def test_python_request_passes_through_to_llm():
    fake = FakeLLMClient()
    result = CodingService(fake).generate("Write a Python program to reverse a string")

    assert isinstance(result, CodingResult)
    assert result.kind == "coding"
    assert result.language == "python"
    assert result.mock is True
    assert result.model == "fake-llm-1"
    # The exact user request reached the LLM (not a keyword-derived stand-in).
    assert fake.last_user == "Write a Python program to reverse a string"
    assert "reverse a string" in result.code.lower()
    # It is NOT the old hardcoded factorial behaviour.
    assert "def factorial" not in result.code.lower()


def test_java_request_generates_java():
    fake = FakeLLMClient()
    result = CodingService(fake).generate("Create a Java class implementing a stack")
    assert result.language == "java"
    assert "def factorial" not in result.code.lower()


def test_javascript_request_generates_javascript():
    fake = FakeLLMClient()
    result = CodingService(fake).generate(
        "Write a JavaScript function that validates an email"
    )
    assert result.language == "javascript"


def test_arbitrary_natural_language_request_passes_through():
    fake = FakeLLMClient()
    request = "Build a small CLI todo app that keeps tasks in memory"
    result = CodingService(fake).generate(request)
    assert fake.last_user == request
    assert request.split()[0].lower() in result.code.lower() or result.summary


def test_system_prompt_enforces_structured_output():
    fake = FakeLLMClient()
    CodingService(fake).generate("write anything")
    assert fake.last_system is not None
    assert "JSON" in fake.last_system


def test_json_with_fences_and_surrounding_prose_is_parsed():
    payload = (
        "Sure, here you go:\n```json\n"
        + json.dumps({"language": "python", "code": "print('hi')", "summary": "prints hi"})
        + "\n```\nHope that helps!"
    )
    result = CodingService(FakeLLMClient(response=payload)).generate("x")
    assert result.language == "python"
    assert result.code == "print('hi')"
    assert result.summary == "prints hi"


def test_malformed_non_json_response_raises_coding_error():
    fake = FakeLLMClient(response="I cannot help with that.")
    with pytest.raises(CodingError):
        CodingService(fake).generate("write code")


def test_missing_required_fields_raises_coding_error():
    fake = FakeLLMClient(response=json.dumps({"language": "python"}))
    with pytest.raises(CodingError):
        CodingService(fake).generate("write code")


def test_empty_fields_raise_coding_error():
    fake = FakeLLMClient(
        response=json.dumps({"language": "python", "code": "  ", "summary": "x"})
    )
    with pytest.raises(CodingError):
        CodingService(fake).generate("write code")


def test_provider_failure_propagates_as_llm_error():
    fake = FakeLLMClient(error=LLMError("The coding provider failed."))
    with pytest.raises(LLMError):
        CodingService(fake).generate("write code")


def test_provider_timeout_propagates():
    fake = FakeLLMClient(error=LLMTimeoutError("The coding provider timed out."))
    with pytest.raises(LLMTimeoutError):
        CodingService(fake).generate("write code")


def test_empty_request_raises_coding_error():
    with pytest.raises(CodingError):
        CodingService(FakeLLMClient()).generate("   ")


def test_mock_mode_flag_is_reflected_in_result():
    # A fake (offline) client marks the result as mock=True.
    result = CodingService(FakeLLMClient()).generate("write code")
    assert result.mock is True


def test_error_messages_do_not_leak_internals():
    # CodingError messages are user-safe: no stack traces / provider guts.
    fake = FakeLLMClient(response="not json")
    try:
        CodingService(fake).generate("write code")
    except CodingError as exc:
        assert "Traceback" not in str(exc)
        assert str(exc)  # non-empty, human-readable
