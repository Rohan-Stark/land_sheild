from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StreamChunk(BaseModel):
    """A single incremental token chunk from a streaming response."""
    content: str = ""
    done: bool = False
    model: str = ""


class LLMResponseMetrics(BaseModel):
    """Metrics captured from a single LLM call."""
    model_used: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    retry_count: int = 0
    fallback_used: bool = False
    streaming_duration_ms: float = 0.0


class FinalResponse(BaseModel):
    """The fully synthesized response returned to the caller."""
    request_id: str = ""
    status: str = "success"
    content: str = ""
    format: str = "markdown"  # 'markdown', 'plain', 'json'
    agent: str = ""
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metrics: LLMResponseMetrics = Field(default_factory=LLMResponseMetrics)
    metadata: dict[str, Any] = Field(default_factory=dict)
