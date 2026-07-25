from __future__ import annotations

import time
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("utils.metrics")


class MetricsTracker:
    """Reusable metrics tracker for agent execution."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        self.start_time = time.perf_counter()
        self.metrics: dict[str, float] = {
            "execution_time_ms": 0.0,
            "retrieval_time_ms": 0.0,
            "tool_time_ms": 0.0,
            "validation_time_ms": 0.0,
            "retry_count": 0.0,
            "failure_count": 0.0,
        }

    def record_time(self, metric_key: str, elapsed_ms: float) -> None:
        """Add elapsed time to a specific metric."""
        if metric_key in self.metrics:
            self.metrics[metric_key] += elapsed_ms
        else:
            self.metrics[metric_key] = elapsed_ms

    def record_event(self, metric_key: str, count: int = 1) -> None:
        """Increment an event counter."""
        if metric_key in self.metrics:
            self.metrics[metric_key] += count
        else:
            self.metrics[metric_key] = float(count)

    def finish(self) -> dict[str, float]:
        """Finalise execution time and return collected metrics."""
        self.metrics["execution_time_ms"] = (time.perf_counter() - self.start_time) * 1000
        logger.debug("Metrics finalized for %s: %s", self.agent_name, self.metrics)
        return self.metrics.copy()
