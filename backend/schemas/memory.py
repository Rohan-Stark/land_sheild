from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryMessage(BaseModel):
    """A single Q&A turn or system event in memory."""
    id: str
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationMemory(BaseModel):
    """Short-term conversational state tied to a session/conversation ID."""
    conversation_id: str
    user_id: str
    messages: list[MemoryMessage] = Field(default_factory=list)
    recent_topics: list[str] = Field(default_factory=list)
    selected_documents: list[str] = Field(default_factory=list)
    current_property_id: str | None = None
    user_preferences: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None  # Archived state if messages get too long


class PropertyMemory(BaseModel):
    """Persistent state tied to a specific property across conversations."""
    property_id: str
    owner_id: str
    recent_searches: list[str] = Field(default_factory=list)
    active_alerts: list[dict[str, Any]] = Field(default_factory=list)
    generated_reports: list[str] = Field(default_factory=list)
    retrieved_metadata: dict[str, Any] = Field(default_factory=dict)
    inspection_history: list[dict[str, Any]] = Field(default_factory=list)
    timeline_summary: str | None = None
