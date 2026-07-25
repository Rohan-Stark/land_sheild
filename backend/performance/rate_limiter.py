from __future__ import annotations

import time
from typing import Any

from fastapi import HTTPException, Request, status

from backend.config.logging import get_logger
from backend.schemas.performance import RateLimitConfig

logger = get_logger("performance.rate_limiter")


class SlidingWindowCounter:
    """In-memory sliding-window rate limiter for a single key.

    In production, the counters would be stored in Redis using MULTI/EXEC
    for atomic increments. This implementation mirrors that interface exactly.
    """

    def __init__(self, config: RateLimitConfig) -> None:
        self._config = config
        # key -> list of request timestamps within the current window
        self._windows: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Return True if the request should proceed, False if rate limited."""
        now = time.monotonic()
        window_start = now - self._config.window_seconds

        # Initialize or prune expired entries
        timestamps = self._windows.get(key, [])
        timestamps = [t for t in timestamps if t > window_start]

        if len(timestamps) >= self._config.requests_per_window:
            self._windows[key] = timestamps
            return False

        timestamps.append(now)
        self._windows[key] = timestamps
        return True

    def remaining(self, key: str) -> int:
        """Return how many requests are still allowed in this window."""
        now = time.monotonic()
        window_start = now - self._config.window_seconds
        timestamps = [t for t in self._windows.get(key, []) if t > window_start]
        return max(0, self._config.requests_per_window - len(timestamps))

    def retry_after(self, key: str) -> float:
        """Return seconds until the next request will be allowed."""
        timestamps = self._windows.get(key, [])
        if not timestamps:
            return 0.0
        oldest_in_window = min(timestamps)
        return max(0.0, self._config.window_seconds - (time.monotonic() - oldest_in_window))


class RateLimiterRegistry:
    """Holds configured rate limiters per scope."""

    def __init__(self) -> None:
        self._limiters: dict[str, SlidingWindowCounter] = {}

    def register(self, name: str, config: RateLimitConfig) -> SlidingWindowCounter:
        limiter = SlidingWindowCounter(config)
        self._limiters[name] = limiter
        return limiter

    def get(self, name: str) -> SlidingWindowCounter | None:
        return self._limiters.get(name)

    def check_or_reject(self, name: str, key: str) -> None:
        """Convenience: check rate limit and raise HTTP 429 if exceeded."""
        limiter = self._limiters.get(name)
        if not limiter:
            return

        if not limiter.is_allowed(key):
            retry_after = limiter.retry_after(key)
            logger.warning("Rate limit exceeded for %s on limiter %s", key, name)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(int(retry_after))},
            )


# Singleton with default limiters
rate_limiter_registry = RateLimiterRegistry()

rate_limiter_registry.register(
    "api_default", RateLimitConfig(requests_per_window=120, window_seconds=60)
)
rate_limiter_registry.register(
    "ai_query", RateLimitConfig(requests_per_window=20, window_seconds=60)
)
rate_limiter_registry.register(
    "auth", RateLimitConfig(requests_per_window=10, window_seconds=60)
)
