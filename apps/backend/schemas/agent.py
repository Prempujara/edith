"""Agent domain model (baseline §3, §13).

Minimal by design: only identity, capabilities, and a short human-facing
description. Persona/voice/tool-grants from the baseline are deliberately
omitted until a slice needs them.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .enums import AgentName, Capability


class Agent(BaseModel):
    """A registered agent and the capabilities it can be delegated work for."""

    name: AgentName
    role: str = Field(..., description="One-line role summary from the baseline.")
    capabilities: list[Capability] = Field(default_factory=list)

    def has_capability(self, capability: Capability) -> bool:
        return capability in self.capabilities
