from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PromptRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class PromptMessage(BaseModel):
    """A single message in a multi-turn prompt."""
    role: PromptRole
    content: str


class PromptRequest(BaseModel):
    """The fully assembled prompt payload ready for the Ollama API."""
    model: str
    messages: list[PromptMessage]
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 2048
    stream: bool = False

    # Metadata for logging/metrics (not sent to Ollama)
    request_id: str = ""
    user_id: str = ""
    intent: str = ""
    prompt_token_estimate: int = 0


class PromptContext(BaseModel):
    """Structured context fed into the PromptBuilder before rendering."""
    user_question: str
    agent_summary: str = ""
    agent_findings: list[dict[str, Any]] = Field(default_factory=list)
    agent_sources: list[dict[str, Any]] = Field(default_factory=list)
    agent_warnings: list[str] = Field(default_factory=list)
    agent_next_actions: list[str] = Field(default_factory=list)
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
