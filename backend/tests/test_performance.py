from __future__ import annotations

import asyncio

import pytest

from backend.performance.database_optimizer import DatabaseOptimizer
from backend.performance.queue import QueueManager, QueuedTask, TaskPriority, TaskStatus
from backend.performance.rate_limiter import RateLimitConfig, SlidingWindowCounter


def test_rate_limiter_allows_within_limit():
    config = RateLimitConfig(requests_per_window=3, window_seconds=60)
    limiter = SlidingWindowCounter(config)

    assert limiter.is_allowed("user_1") is True
    assert limiter.is_allowed("user_1") is True
    assert limiter.is_allowed("user_1") is True
    # 4th request should be blocked
    assert limiter.is_allowed("user_1") is False

    assert limiter.remaining("user_1") == 0


def test_rate_limiter_isolates_keys():
    config = RateLimitConfig(requests_per_window=2, window_seconds=60)
    limiter = SlidingWindowCounter(config)

    limiter.is_allowed("user_A")
    limiter.is_allowed("user_A")
    assert limiter.is_allowed("user_A") is False

    # user_B should still be allowed
    assert limiter.is_allowed("user_B") is True


@pytest.mark.asyncio
async def test_queue_priority_ordering():
    qm = QueueManager()

    low = QueuedTask(name="low_job", payload={}, priority=TaskPriority.LOW)
    high = QueuedTask(name="high_job", payload={}, priority=TaskPriority.HIGH)
    critical = QueuedTask(name="critical_job", payload={}, priority=TaskPriority.CRITICAL)

    await qm.enqueue(low)
    await qm.enqueue(high)
    await qm.enqueue(critical)

    # Dequeue should return highest priority first
    first = await qm.dequeue()
    assert first is not None
    assert first.name == "critical_job"

    second = await qm.dequeue()
    assert second is not None
    assert second.name == "high_job"


@pytest.mark.asyncio
async def test_queue_dead_letter():
    qm = QueueManager()

    task = QueuedTask(name="failing_job", payload={}, max_retries=1)
    await qm.enqueue(task)

    # Dequeue and fail
    t = await qm.dequeue()
    assert t is not None
    await qm.fail(t, "error1")
    assert qm.depth == 1  # re-enqueued

    # Dequeue and fail again (exceeds max_retries)
    t2 = await qm.dequeue()
    assert t2 is not None
    await qm.fail(t2, "error2")
    assert qm.dead_letter_count == 1
    assert qm.depth == 0


def test_database_optimizer_batching():
    ids = [f"id_{i}" for i in range(250)]
    batches = DatabaseOptimizer.batch_ids(ids, batch_size=100)
    assert len(batches) == 3
    assert len(batches[0]) == 100
    assert len(batches[2]) == 50


def test_database_optimizer_pagination():
    offset, limit = DatabaseOptimizer.paginate(-5, 500, max_limit=200)
    assert offset == 0
    assert limit == 200

    offset2, limit2 = DatabaseOptimizer.paginate(10, 25, max_limit=200)
    assert offset2 == 10
    assert limit2 == 25
