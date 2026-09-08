"""JARVIS service (baseline §3.1, §5.2).

JARVIS is the primary user-facing agent and the delegation decision-maker.
For this slice the decision is deterministic and rule-based (no LLM): JARVIS
classifies a command into a required capability, then:

- if the capability is one of JARVIS's own (coding/debugging/git/github/web),
  JARVIS handles it directly and produces a deterministic result;
- otherwise JARVIS chooses the target agent via the Agent Registry and
  returns a delegation decision for the Runtime to transport (§12).

JARVIS decides *whether* to delegate and *which* agent. The Runtime never
makes this semantic choice.
"""

from __future__ import annotations

from dataclasses import dataclass

from runtime.registry import AgentRegistry
from schemas.enums import AgentName, Capability

# Deterministic keyword rules mapping to a required capability. Ordered by
# specificity; first match wins. This stands in for future LLM reasoning.
_KEYWORD_CAPABILITY: list[tuple[Capability, tuple[str, ...]]] = [
    (Capability.FILE_MANAGEMENT,
     ("file", "files", "folder", "directory", "organize", "organise",
      "rename", "move", "document")),
    (Capability.COMPUTER_CONTROL,
     ("screen", "mouse", "keyboard", "click", "open app", "application",
      "browser", "navigate", "computer")),
    (Capability.CODING,
     ("code", "program", "function", "script", "factorial", "python",
      "javascript", "bug", "debug", "compile", "git", "github")),
]


@dataclass
class Decision:
    """The outcome of JARVIS's routing decision."""

    capability: Capability | None       # None => plain conversation
    handled_directly: bool              # True => JARVIS does the work itself
    target_agent: AgentName             # who ultimately performs the work


class JarvisService:
    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    # --- decision -------------------------------------------------------
    def classify(self, command: str) -> Capability | None:
        text = command.lower()
        for capability, keywords in _KEYWORD_CAPABILITY:
            if any(k in text for k in keywords):
                return capability
        return None

    def decide(self, command: str) -> Decision:
        """Decide whether JARVIS handles the command or delegates it."""
        capability = self.classify(command)

        # Plain conversation, or a capability JARVIS itself owns -> direct.
        jarvis = self._registry.get(AgentName.JARVIS)
        if capability is None or jarvis.has_capability(capability):
            return Decision(
                capability=capability,
                handled_directly=True,
                target_agent=AgentName.JARVIS,
            )

        # Otherwise find the specialist agent for this capability.
        target = self._registry.find_by_capability(capability)
        if target is None:
            # No agent advertises this capability; JARVIS keeps it.
            return Decision(
                capability=capability,
                handled_directly=True,
                target_agent=AgentName.JARVIS,
            )
        return Decision(
            capability=capability,
            handled_directly=False,
            target_agent=target.name,
        )

    # --- direct execution ----------------------------------------------
    def handle_directly(self, command: str, capability: Capability | None) -> dict:
        """Produce JARVIS's own deterministic result.

        Coding requests get a mock code artefact; anything else gets a
        conversational reply.
        """
        if capability == Capability.CODING:
            return self._mock_coding_result(command)
        return {
            "agent": "JARVIS",
            "kind": "conversation",
            "mock": True,
            "command": command,
            "reply": "JARVIS acknowledges your request.",
        }

    def _mock_coding_result(self, command: str) -> dict:
        code = (
            "def factorial(n):\n"
            "    if n < 0:\n"
            "        raise ValueError('n must be non-negative')\n"
            "    result = 1\n"
            "    for i in range(2, n + 1):\n"
            "        result *= i\n"
            "    return result\n"
        )
        return {
            "agent": "JARVIS",
            "kind": "coding",
            "mock": True,
            "command": command,
            "language": "python",
            "code": code,
            "summary": (
                "JARVIS generated a deterministic sample program. This is a "
                "mock coding result; no code was executed."
            ),
        }
