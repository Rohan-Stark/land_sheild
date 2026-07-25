from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from backend.config.logging import get_logger

logger = get_logger("performance.retry")

T = TypeVar("T")

# Exceptions that should never be retried
PERMANENT_FAILURES = (
    ValueError,
    TypeError,
    PermissionError,
    KeyError,
)


class RetryManager:
    """Retries transient failures with exponential backoff and jitter.

    Permanent failures (ValueError, TypeError, PermissionError) are never retried.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay_seconds: float = 0.5,
        max_delay_seconds: float = 30.0,
        jitter: bool = True,
    ) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay_seconds
        self._max_delay = max_delay_seconds
        self._jitter = jitter

    async def execute(
        self,
        func: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute an async callable with automatic retry on transient failure."""
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except PERMANENT_FAILURES:
                raise  # Never retry these
            except Exception as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    logger.error(
                        "All %d retries exhausted for %s: %s",
                        self._max_retries,
                        func.__qualname__,
                        exc,
                    )
                    raise

                delay = self._calculate_delay(attempt)
                logger.warning(
                    "Retry %d/%d for %s after %.2fs (error: %s)",
                    attempt + 1,
                    self._max_retries,
                    func.__qualname__,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)

        raise last_exc  # type: ignore[misc]  # unreachable safety net

    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff: base * 2^attempt, capped at max_delay, with optional jitter."""
        delay = min(self._base_delay * (2 ** attempt), self._max_delay)
        if self._jitter:
            delay *= random.uniform(0.5, 1.5)
        return delay


# Pre-configured singleton instances
default_retry = RetryManager()
aggressive_retry = RetryManager(max_retries=5, base_delay_seconds=1.0)
