"""Agent Registry (baseline §13).

Maintains the available agents and their capabilities. Agents use this to
determine which agent is appropriate for delegation. The registry only
*stores and reports* capabilities; it makes no semantic decision about who
should handle a task — that decision belongs to the agents (§12).
"""

from __future__ import annotations

from schemas.agent import Agent
from schemas.enums import AgentName, Capability


class AgentRegistry:
    """In-memory registry of agents keyed by name."""

    def __init__(self) -> None:
        self._agents: dict[AgentName, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: AgentName) -> Agent | None:
        return self._agents.get(name)

    def list_agents(self) -> list[Agent]:
        return list(self._agents.values())

    def find_by_capability(self, capability: Capability) -> Agent | None:
        """Return the first agent advertising ``capability`` (or None).

        This is a lookup helper for delegating agents; it is not a decision
        maker. The calling agent decides *whether* to delegate and *what*
        capability to look up.
        """
        for agent in self._agents.values():
            if agent.has_capability(capability):
                return agent
        return None


def build_default_registry() -> AgentRegistry:
    """Registry seeded with the three baseline agents (§3, §13).

    Capabilities are copied verbatim from the Agent Registry table in §13.
    Roles are the one-line primary-role summaries from §3.
    """
    registry = AgentRegistry()
    registry.register(
        Agent(
            name=AgentName.JARVIS,
            role="Primary conversational and technical agent.",
            capabilities=[
                Capability.CODING,
                Capability.DEBUGGING,
                Capability.GIT,
                Capability.GITHUB,
                Capability.WEB,
            ],
        )
    )
    registry.register(
        Agent(
            name=AgentName.EDITH,
            role="Intelligence and computer-control agent.",
            capabilities=[
                Capability.COMPUTER_CONTROL,
                Capability.BROWSER,
                Capability.SCREEN,
            ],
        )
    )
    registry.register(
        Agent(
            name=AgentName.FRIDAY,
            role="File-management and operations agent.",
            capabilities=[
                Capability.FILE_MANAGEMENT,
                Capability.DOCUMENT_OPERATIONS,
            ],
        )
    )
    return registry
