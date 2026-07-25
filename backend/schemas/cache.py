from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """A single cached value with metadata."""
    key: str
    value: Any
    namespace: str = "default"
    ttl_seconds: int = 300
    created_at: float = 0.0
    hit_count: int = 0


class SemanticCacheEntry(BaseModel):
    """A cached AI response keyed by embedding similarity."""
    query: str
    embedding: list[float] = Field(default_factory=list)
    response: str
    user_id: str
    property_id: str | None = None
    agent: str = ""
    similarity_score: float = 0.0
    ttl_seconds: int = 1800
    created_at: float = 0.0
    hit_count: int = 0


class CacheStats(BaseModel):
    """Aggregate cache performance statistics."""
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    hit_ratio: float = 0.0
    semantic_hits: int = 0
    semantic_misses: int = 0
    semantic_hit_ratio: float = 0.0
