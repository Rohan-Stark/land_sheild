from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ── Request Schemas ─────────────────────────────────────────────────────────


class RetrievalRequest(BaseModel):
    """Query the hybrid retrieval engine."""

    query: str = Field(..., min_length=1, max_length=2000)
    user_id: uuid.UUID
    property_id: uuid.UUID | None = None
    document_type: str | None = None
    inspection_id: str | None = None
    alert_id: str | None = None
    survey_number: str | None = None
    registration_number: str | None = None
    khata_number: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)


# ── Internal Data Models ────────────────────────────────────────────────────


class ScoredChunk(BaseModel):
    """A single chunk with retrieval scores."""

    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Individual scores (0.0 – 1.0)
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    metadata_score: float = 0.0
    recency_score: float = 0.0
    importance_score: float = 0.0

    # Weighted final score
    final_score: float = 0.0


class RetrievalContext(BaseModel):
    """Compressed context object returned by the retrieval engine."""

    chunks: list[ScoredChunk]
    total_tokens: int
    metadata_summary: dict[str, Any] = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)


# ── Response Schemas ────────────────────────────────────────────────────────


class RetrievalResponse(BaseModel):
    """API response wrapper for retrieval results."""

    query: str
    context: RetrievalContext
    retrieval_time_ms: float
    chunk_count: int
