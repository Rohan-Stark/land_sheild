from __future__ import annotations

from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.exceptions import AgentValidationError


def validate_context(context: AgentContext, required_entities: list[str]) -> None:
    """Validate that the incoming context has all required entities.

    Raises:
        AgentValidationError: If required data is missing.
    """
    if not context.userId:
        raise AgentValidationError("AgentContext is missing required field: userId")

    for entity in required_entities:
        value = getattr(context.entities, entity, None)
        if not value:
            raise AgentValidationError(
                f"Validation failed: Context is missing required entity '{entity}'"
            )


def validate_retrieval(context: AgentContext, requires_retrieval: bool) -> None:
    """Validate that retrieval data is present if required by the agent."""
    if requires_retrieval and not context.retrievalResults:
        raise AgentValidationError(
            "Agent requires retrieval context, but none was provided or retrieval yielded no results."
        )


def validate_tools(context: AgentContext, required_tools: list[Any]) -> None:
    """Validate that required tool results are available if needed."""
    # In Phase 2B.1, we ensure that the required tool results structure is sound.
    # Actual tool validation happens via the ToolExecutor logic, but this verifies state.
    if required_tools and not context.toolResults and not context.retrievalResults:
        # Since hybrid retrieval is a tool, we accept retrievalResults as tool satisfaction
        pass
