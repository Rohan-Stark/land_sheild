from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

from backend.config.logging import get_logger
from backend.llm.schemas.runtime import RuntimeConfig

logger = get_logger("llm.retry")

T = TypeVar("T")


class RetryPolicy:
    """Exponential backoff retry policy for transient LLM failures.

    Retryable errors: network failures, model busy (503), streaming interruptions.
    Non-retryable: 4xx client errors, validation errors.
    """

    def __init__(self, config: RuntimeConfig) -> None:
        self._max_retries = config.retry_count
        self._base_delay = config.retry_base_delay_seconds
        self._max_delay = config.retry_max_delay_seconds

    async def execute(
        self,
        fn: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute `fn` with exponential backoff retries."""
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                last_exc = exc

                if not self._is_retryable(exc):
                    logger.error("Non-retryable error on attempt %d: %s", attempt + 1, exc)
                    raise

                if attempt == self._max_retries:
                    logger.error("All %d retries exhausted: %s", self._max_retries, exc)
                    raise

                delay = min(self._base_delay * (2 ** attempt), self._max_delay)
                logger.warning(
                    "Retryable error on attempt %d/%d, retrying in %.1fs: %s",
                    attempt + 1,
                    self._max_retries,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)

        # Should never reach here, but satisfy the type checker
        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        """Determine if an exception warrants a retry."""
        import httpx

        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in (429, 500, 502, 503, 504)
        if isinstance(exc, (ConnectionError, OSError)):
            return True
        return False
