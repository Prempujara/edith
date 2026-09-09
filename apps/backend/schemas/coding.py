"""Typed result of a coding request handled by JARVIS (Capability.CODING).

This is the structured payload produced by the Coding Service and stored,
serialized, in ``Task.result``. The field set is the contract the existing API
and frontend already rely on (``kind``/``language``/``code``/``summary``), plus
additive provenance fields (``mock``/``model``) that older clients can ignore.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CodingResult(BaseModel):
    """A generated code artefact and its metadata."""

    kind: Literal["coding"] = "coding"
    language: str = Field(..., description="Programming language of the generated code.")
    code: str = Field(..., description="The complete generated source code.")
    summary: str = Field(..., description="Concise description of what the code does.")
    mock: bool = Field(
        ...,
        description="True when produced by the offline fake client rather than a real provider.",
    )
    model: str = Field(
        ...,
        description="Identifier of the model/provider that produced this result.",
    )
