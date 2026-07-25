from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Citation(BaseModel):
    """A direct reference backing a claim made by the LLM."""
    document_name: str | None = None
    document_type: str | None = None
    page_number: int | None = None
    chunk_id: str | None = None
    source_type: str = "document"
    retrieval_score: float = 0.0
    reranker_score: float = 0.0
    confidence: float = 0.0


class EvidenceMatch(BaseModel):
    """Result of cross-referencing an LLM claim against retrieved context."""
    claim: str
    is_supported: bool
    matched_chunk_id: str | None = None
    matched_text: str | None = None
    contradiction_reason: str | None = None
