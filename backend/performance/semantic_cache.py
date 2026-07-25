from __future__ import annotations

import math
import time
from typing import Any

from backend.config.logging import get_logger
from backend.schemas.cache import SemanticCacheEntry

logger = get_logger("performance.semantic_cache")


class SemanticCache:
    """Caches AI responses by semantic embedding similarity.

    When a new query arrives, its embedding is compared against cached entries.
    If a semantically similar query from the same user context exists, the cached
    response is returned immediately, completely bypassing the LLM.

    Security: entries are scoped by user_id so one user's cache never leaks to another.
    """

    def __init__(self, similarity_threshold: float = 0.92, max_entries: int = 500) -> None:
        self._threshold = similarity_threshold
        self._max_entries = max_entries
        self._entries: list[SemanticCacheEntry] = []
        self._stats = {"hits": 0, "misses": 0}

    async def lookup(
        self,
        embedding: list[float],
        user_id: str,
        property_id: str | None = None,
    ) -> SemanticCacheEntry | None:
        """Search for a semantically similar cached response."""
        best_match: SemanticCacheEntry | None = None
        best_score = 0.0

        now = time.monotonic()

        for entry in self._entries:
            # Security: never cross user boundaries
            if entry.user_id != user_id:
                continue

            # Property scope check
            if property_id and entry.property_id and entry.property_id != property_id:
                continue

            # TTL check
            if entry.created_at > 0 and (now - entry.created_at) > entry.ttl_seconds:
                continue

            score = self._cosine_similarity(embedding, entry.embedding)
            if score > best_score:
                best_score = score
                best_match = entry

        if best_match and best_score >= self._threshold:
            best_match.hit_count += 1
            best_match.similarity_score = best_score
            self._stats["hits"] += 1
            logger.info("Semantic cache HIT (score=%.4f) for user %s", best_score, user_id)
            return best_match

        self._stats["misses"] += 1
        return None

    async def store(
        self,
        query: str,
        embedding: list[float],
        response: str,
        user_id: str,
        agent: str = "",
        property_id: str | None = None,
        ttl_seconds: int = 1800,
    ) -> None:
        """Cache a new AI response."""
        # Evict oldest if at capacity
        if len(self._entries) >= self._max_entries:
            self._entries.sort(key=lambda e: e.created_at)
            self._entries.pop(0)

        entry = SemanticCacheEntry(
            query=query,
            embedding=embedding,
            response=response,
            user_id=user_id,
            property_id=property_id,
            agent=agent,
            ttl_seconds=ttl_seconds,
            created_at=time.monotonic(),
        )
        self._entries.append(entry)
        logger.debug("Stored semantic cache entry for user %s (agent=%s)", user_id, agent)

    async def invalidate_user(self, user_id: str) -> int:
        """Remove all cached entries for a specific user."""
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.user_id != user_id]
        removed = before - len(self._entries)
        return removed

    async def invalidate_property(self, property_id: str) -> int:
        """Remove all cached entries for a specific property."""
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.property_id != property_id]
        removed = before - len(self._entries)
        return removed

    def get_stats(self) -> dict[str, Any]:
        total = self._stats["hits"] + self._stats["misses"]
        return {
            **self._stats,
            "total": total,
            "hit_ratio": round(self._stats["hits"] / total, 3) if total > 0 else 0.0,
            "entries": len(self._entries),
        }

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two embedding vectors."""
        if len(a) != len(b) or not a:
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot / (norm_a * norm_b)


# Singleton
semantic_cache = SemanticCache()
