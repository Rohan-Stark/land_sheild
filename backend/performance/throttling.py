from __future__ import annotations

import asyncio
from typing import Any

from backend.config.logging import get_logger
from backend.schemas.performance import ThrottleConfig

logger = get_logger("performance.throttling")


class RequestThrottler:
    """Limits concurrent execution of heavy operations using async semaphores.

    This prevents resource exhaustion when many LLM or OCR requests arrive simultaneously.
    Requests exceeding the queue capacity are rejected immediately.
    """

    def __init__(self, config: ThrottleConfig) -> None:
        self._config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent)
        self._queue_depth = 0

    @property
    def active_count(self) -> int:
        """Approximate number of currently in-flight tasks."""
        return self._config.max_concurrent - self._semaphore._value  # type: ignore[attr-defined]

    @property
    def queue_depth(self) -> int:
        return self._queue_depth

    async def acquire(self) -> bool:
        """Attempt to acquire a concurrency slot.

        Returns True if acquired, False if the queue is full and the request
        should be rejected with HTTP 503.
        """
        waiters = getattr(self._semaphore, "_waiters", None)
        pending = len(waiters) if waiters else 0

        if pending >= self._config.queue_size:
            logger.warning(
                "Throttler queue full (%d/%d). Rejecting request.",
                pending,
                self._config.queue_size,
            )
            return False

        self._queue_depth += 1
        await self._semaphore.acquire()
        self._queue_depth -= 1
        return True

    def release(self) -> None:
        """Release a concurrency slot after the operation completes."""
        self._semaphore.release()


class ThrottlerRegistry:
    """Central registry for operation-specific throttlers."""

    def __init__(self) -> None:
        self._throttlers: dict[str, RequestThrottler] = {}

    def register(self, name: str, config: ThrottleConfig) -> RequestThrottler:
        throttler = RequestThrottler(config)
        self._throttlers[name] = throttler
        return throttler

    def get(self, name: str) -> RequestThrottler | None:
        return self._throttlers.get(name)


throttler_registry = ThrottlerRegistry()

throttler_registry.register("llm", ThrottleConfig(max_concurrent=5, queue_size=20))
throttler_registry.register("ocr", ThrottleConfig(max_concurrent=3, queue_size=10))
throttler_registry.register("upload", ThrottleConfig(max_concurrent=10, queue_size=30))
throttler_registry.register("streaming", ThrottleConfig(max_concurrent=8, queue_size=15))
