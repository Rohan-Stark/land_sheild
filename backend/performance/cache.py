from __future__ import annotations

import json
import time
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("performance.cache")


class CacheManager:
    """Redis-compatible key-value cache with namespace isolation and TTL.

    The interface mirrors redis.asyncio exactly so that swapping in a live Redis
    connection requires zero changes to call sites.
    """

    def __init__(self) -> None:
        # key -> {"value": Any, "expires_at": float, "namespace": str, "hits": int}
        self._store: dict[str, dict[str, Any]] = {}
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}

    async def get(self, key: str, namespace: str = "default") -> Any | None:
        """Retrieve a cached value. Returns None on miss or expiration."""
        full_key = f"{namespace}:{key}"
        record = self._store.get(full_key)

        if record is None:
            self._stats["misses"] += 1
            return None

        if record["expires_at"] and time.monotonic() > record["expires_at"]:
            del self._store[full_key]
            self._stats["evictions"] += 1
            self._stats["misses"] += 1
            return None

        self._stats["hits"] += 1
        record["hits"] += 1
        return record["value"]

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
        namespace: str = "default",
    ) -> None:
        """Store a value with a configurable TTL."""
        full_key = f"{namespace}:{key}"
        self._store[full_key] = {
            "value": value,
            "expires_at": time.monotonic() + ttl_seconds if ttl_seconds > 0 else None,
            "namespace": namespace,
            "hits": 0,
        }
        self._stats["sets"] += 1

    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Explicitly remove a cache entry. Returns True if existed."""
        full_key = f"{namespace}:{key}"
        if full_key in self._store:
            del self._store[full_key]
            return True
        return False

    async def invalidate_namespace(self, namespace: str) -> int:
        """Wipe all entries in a namespace. Returns count of removed items."""
        prefix = f"{namespace}:"
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]
        logger.info("Invalidated %d entries in namespace '%s'", len(keys_to_remove), namespace)
        return len(keys_to_remove)

    async def invalidate_by_property(self, property_id: str) -> int:
        """Invalidate all cache entries related to a specific property."""
        keys_to_remove = [k for k in self._store if property_id in k]
        for k in keys_to_remove:
            del self._store[k]
        return len(keys_to_remove)

    def get_stats(self) -> dict[str, int]:
        total = self._stats["hits"] + self._stats["misses"]
        return {
            **self._stats,
            "total_requests": total,
            "hit_ratio": round(self._stats["hits"] / total, 3) if total > 0 else 0.0,
        }


# Singleton
cache_manager = CacheManager()
