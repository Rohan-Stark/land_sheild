from __future__ import annotations

import time
from typing import Any

from backend.config.logging import get_logger
from backend.performance.cache import cache_manager
from backend.performance.circuit_breaker import circuit_registry
from backend.performance.connection_pool import pool_manager
from backend.performance.profiler import profiler
from backend.performance.queue import queue_registry
from backend.performance.semantic_cache import semantic_cache
from backend.performance.background_tasks import background_manager
from backend.schemas.performance import CircuitState, PerformanceSnapshot

logger = get_logger("performance.metrics")


class MetricsCollector:
    """Aggregates performance telemetry from all subsystems into a unified snapshot.

    Designed to be consumed by a /metrics or /health endpoint for operational dashboards.
    """

    def __init__(self) -> None:
        self._retry_count = 0
        self._circuit_trips = 0

    def record_retry(self) -> None:
        self._retry_count += 1

    def record_circuit_trip(self) -> None:
        self._circuit_trips += 1

    def snapshot(self) -> PerformanceSnapshot:
        """Build a point-in-time performance snapshot."""
        cache_stats = cache_manager.get_stats()
        sem_stats = semantic_cache.get_stats()

        open_circuits = circuit_registry.get_open_circuits()
        total_queue_depth = sum(q.depth for q in queue_registry.values())

        avg_latency = profiler.get_average("api_request")
        p95 = profiler.get_percentile("api_request", 95)
        p99 = profiler.get_percentile("api_request", 99)

        return PerformanceSnapshot(
            avg_latency_ms=round(avg_latency, 2),
            p95_latency_ms=round(p95, 2),
            p99_latency_ms=round(p99, 2),
            total_requests=cache_stats.get("total_requests", 0),
            active_circuits_open=len(open_circuits),
            retry_count=self._retry_count,
            queue_depth=total_queue_depth,
            background_tasks_running=background_manager.running_count,
        )

    def detailed_report(self) -> dict[str, Any]:
        """Full diagnostic report for debugging and dashboards."""
        return {
            "cache": cache_manager.get_stats(),
            "semantic_cache": semantic_cache.get_stats(),
            "open_circuits": circuit_registry.get_open_circuits(),
            "queues": {name: {"depth": q.depth, "dlq": q.dead_letter_count} for name, q in queue_registry.items()},
            "pools": {
                name: {
                    "active": pool_manager.get_stats(name).active if pool_manager.get_stats(name) else 0,
                    "failed": pool_manager.get_stats(name).failed_acquisitions if pool_manager.get_stats(name) else 0,
                }
                for name in ["postgres", "redis", "chromadb", "http_ollama"]
            },
            "background_tasks": background_manager.running_count,
            "retries_total": self._retry_count,
            "circuit_trips_total": self._circuit_trips,
        }


# Singleton
metrics = MetricsCollector()
