from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.schemas.graph import ExtractedEntities, IntentCategory


class AgentContext(BaseModel):
    """The standardized context passed to every concrete agent."""

    requestId: str
    userId: str
    propertyId: str | None = None
    conversationId: str | None = None
    
    intent: IntentCategory
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    
    retrievalResults: list[dict[str, Any]] = Field(default_factory=list)
    toolResults: list[dict[str, Any]] = Field(default_factory=list)
    
    metadata: dict[str, Any] = Field(default_factory=dict)
    executionHistory: list[str] = Field(default_factory=list)
    
    # Raw underlying graph state if absolutely needed, but agents should rely on typed fields
    graphState: dict[str, Any] = Field(default_factory=dict)
    
    sharedContext: dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
