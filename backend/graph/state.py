from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from backend.schemas.graph import ExecutionPlan, ExtractedEntities, IntentCategory


class GraphState(TypedDict):
    """The shared state for the LangGraph orchestration layer."""

    requestId: str
    userId: str
    propertyId: str | None
    conversationId: str | None
    query: str

    # Pipeline state
    intent: IntentCategory
    entities: ExtractedEntities
    plan: ExecutionPlan

    # Execution tracking (append lists)
    selected_agents: Annotated[list[str], operator.add]
    tool_calls: Annotated[list[dict[str, Any]], operator.add]
    agent_outputs: Annotated[list[dict[str, Any]], operator.add]
    retrieved_context: Annotated[list[dict[str, Any]], operator.add]
    execution_history: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]

    # Global metadata
    metadata: dict[str, Any]
