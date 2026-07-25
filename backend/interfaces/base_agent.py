from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from backend.interfaces.base_tool import BaseTool


class AgentInput(BaseModel):
    """Base schema for agent input."""

    query: str
    user_id: str
    property_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Base schema for agent output."""

    response: str
    sources: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    agent_name: str = ""


class BaseAgent(ABC):
    """Abstract base class for all LandShield AI agents.

    Agents are domain-specific reasoning units that use tools and retrieval
    to answer user queries. Implementation deferred to Phase 2.
    """

    name: str
    description: str
    tools: list[BaseTool]

    @abstractmethod
    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process a user query and return a response."""
        ...

    def __repr__(self) -> str:
        return f"<Agent: {self.name}>"
