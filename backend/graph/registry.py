from __future__ import annotations

from typing import Type

from backend.agents.base_agent import BaseAgent
from backend.config.logging import get_logger

logger = get_logger("graph.registry")


class AgentRegistry:
    """Registry for managing active AI agents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register a new agent instance."""
        if agent.name in self._agents:
            logger.warning("Overwriting existing agent registration: %s", agent.name)
        self._agents[agent.name] = agent
        logger.info("Registered agent: %s", agent.name)

    def unregister(self, agent_name: str) -> None:
        """Unregister an agent."""
        if agent_name in self._agents:
            del self._agents[agent_name]
            logger.info("Unregistered agent: %s", agent_name)

    def lookup(self, agent_name: str) -> BaseAgent | None:
        """Retrieve an agent by name."""
        return self._agents.get(agent_name)

    def list_agents(self) -> list[str]:
        """List all registered agent names."""
        return list(self._agents.keys())


# Global singleton registry
agent_registry = AgentRegistry()
