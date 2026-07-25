from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from backend.config.logging import get_logger

logger = get_logger("performance.profiler")


class ProfileResult:
    """Immutable record of a profiled operation."""

    __slots__ = ("operation", "duration_ms", "timestamp", "metadata")

    def __init__(self, operation: str, duration_ms: float, metadata: dict[str, Any] | None = None) -> None:
        self.operation = operation
        self.duration_ms = duration_ms
        self.timestamp = time.time()
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"<Profile {self.operation}: {self.duration_ms:.2f}ms>"


class PerformanceProfiler:
    """Measures and records execution times for critical code paths.

    Usage:
        async with profiler.measure("llm_generate"):
            response = await ollama.generate(...)
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._history: list[ProfileResult] = []
        self._max_history = max_history

    @asynccontextmanager
    async def measure(self, operation: str, metadata: dict[str, Any] | None = None) -> AsyncGenerator[None, None]:
        """Async context manager that times the enclosed block."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            result = ProfileResult(operation, elapsed_ms, metadata)
            self._record(result)

            if elapsed_ms > 5000:
                logger.warning("Slow operation: %s took %.2fms", operation, elapsed_ms)
            else:
                logger.debug("Profiled %s: %.2fms", operation, elapsed_ms)

    def _record(self, result: ProfileResult) -> None:
        self._history.append(result)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def get_history(self, operation: str | None = None, limit: int = 100) -> list[ProfileResult]:
        """Retrieve profiling history, optionally filtered by operation name."""
        if operation:
            filtered = [r for r in self._history if r.operation == operation]
        else:
            filtered = list(self._history)
        return filtered[-limit:]

    def get_percentile(self, operation: str, percentile: float) -> float:
        """Compute a specific latency percentile for an operation."""
        entries = [r.duration_ms for r in self._history if r.operation == operation]
        if not entries:
            return 0.0
        entries.sort()
        idx = int(len(entries) * percentile / 100)
        idx = min(idx, len(entries) - 1)
        return entries[idx]

    def get_average(self, operation: str) -> float:
        """Compute the average latency for an operation."""
        entries = [r.duration_ms for r in self._history if r.operation == operation]
        if not entries:
            return 0.0
        return sum(entries) / len(entries)


# Singleton
profiler = PerformanceProfiler()
