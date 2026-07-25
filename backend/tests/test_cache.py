from __future__ import annotations

import asyncio
import math

import pytest

from backend.performance.cache import CacheManager
from backend.performance.semantic_cache import SemanticCache


@pytest.mark.asyncio
async def test_cache_hit_and_miss():
    cache = CacheManager()

    await cache.set("key1", "value1", ttl_seconds=60, namespace="test")
    result = await cache.get("key1", namespace="test")
    assert result == "value1"

    miss = await cache.get("nonexistent", namespace="test")
    assert miss is None

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


@pytest.mark.asyncio
async def test_cache_delete():
    cache = CacheManager()

    await cache.set("del_key", "val", namespace="ns")
    deleted = await cache.delete("del_key", namespace="ns")
    assert deleted is True

    result = await cache.get("del_key", namespace="ns")
    assert result is None


@pytest.mark.asyncio
async def test_cache_namespace_invalidation():
    cache = CacheManager()

    await cache.set("a", 1, namespace="prop_123")
    await cache.set("b", 2, namespace="prop_123")
    await cache.set("c", 3, namespace="other")

    removed = await cache.invalidate_namespace("prop_123")
    assert removed == 2

    assert await cache.get("c", namespace="other") == 3


@pytest.mark.asyncio
async def test_semantic_cache_hit():
    sc = SemanticCache(similarity_threshold=0.90)

    embedding = [1.0, 0.0, 0.0]
    await sc.store("What is Survey No 5?", embedding, "It is a land survey.", user_id="u1")

    # Identical query should hit
    result = await sc.lookup(embedding, user_id="u1")
    assert result is not None
    assert result.response == "It is a land survey."

    stats = sc.get_stats()
    assert stats["hits"] == 1


@pytest.mark.asyncio
async def test_semantic_cache_user_isolation():
    sc = SemanticCache(similarity_threshold=0.90)

    embedding = [1.0, 0.0, 0.0]
    await sc.store("query", embedding, "response", user_id="user_A")

    # Different user should NOT hit
    result = await sc.lookup(embedding, user_id="user_B")
    assert result is None


@pytest.mark.asyncio
async def test_semantic_cache_below_threshold():
    sc = SemanticCache(similarity_threshold=0.99)

    await sc.store("query", [1.0, 0.0, 0.0], "response", user_id="u1")

    # Different embedding below threshold
    result = await sc.lookup([0.7, 0.7, 0.0], user_id="u1")
    assert result is None


def test_cosine_similarity():
    assert SemanticCache._cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)
    assert SemanticCache._cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)
    assert SemanticCache._cosine_similarity([], []) == 0.0
