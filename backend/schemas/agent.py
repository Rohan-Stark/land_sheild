from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Base schema for agent input."""

    query: str
    user_id: str
    property_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Base schema for structured agent output."""

    response: str
    sources: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    agent_name: str = ""
