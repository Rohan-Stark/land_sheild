from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult
from backend.schemas.graph import IntentCategory


class BaseAgent(ABC):
    """Abstract base class establishing the core framework for all LandShield agents.

    All future concrete agents must inherit from this class and implement
    the required abstract methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the agent."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the agent does."""
        ...

    @property
    @abstractmethod
    def supported_intents(self) -> list[IntentCategory]:
        """Intents this agent is permitted to handle."""
        ...

    @property
    @abstractmethod
    def supported_entities(self) -> list[str]:
        """Entity fields required by this agent to function properly."""
        ...

    @property
    @abstractmethod
    def required_tools(self) -> list[type]:
        """List of Tool classes this agent depends on."""
        ...

    @property
    @abstractmethod
    def requires_retrieval(self) -> bool:
        """Whether this agent fundamentally relies on vector retrieval context."""
        ...

    @property
    @abstractmethod
    def priority(self) -> int:
        """Execution priority (higher executes earlier in parallel batches)."""
        ...

    async def execute(self, context: AgentContext) -> AgentResult:
        """The main entry point. Delegates to the standard execution pipeline."""
        # Note: To avoid circular imports, the execution pipeline wraps this.
        # This method is typically called by the executor or graph.
        return await self.process(context)

    @abstractmethod
    def validate(self, context: AgentContext) -> None:
        """Agent-specific pre-flight validation (in addition to framework validation)."""
        ...

    @abstractmethod
    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        """Determine what internal steps the agent needs to take based on the context."""
        ...

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResult:
        """The core business logic implemented by concrete agents."""
        ...

    @abstractmethod
    async def post_process(self, result: AgentResult) -> AgentResult:
        """Clean up, format, or mutate the result before final emission."""
        ...

    def __repr__(self) -> str:
        return f"<Agent: {self.name}>"
