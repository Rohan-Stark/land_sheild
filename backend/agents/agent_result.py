from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Citation mapping for facts returned by an agent."""
    
    document_id: str
    chunk_id: str
    source_type: str = "document"  # e.g., 'document', 'alert', 'knowledge_base'
    page_number: int | None = None
    retrieval_score: float = 0.0
    reranker_score: float = 0.0
    confidence: float = 0.0


class AgentResult(BaseModel):
    """The universally required structured output for all concrete agents."""

    agent: str
    status: str = "success"  # 'success', 'partial', 'failed'
    confidence: float = 0.0  # 0.0 to 1.0

    summary: str = ""
    findings: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)
    
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    
    metrics: dict[str, float] = Field(default_factory=dict)
