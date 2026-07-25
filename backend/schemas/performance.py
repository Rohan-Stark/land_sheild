from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CircuitState(str, Enum):
    """Circuit breaker state machine states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerConfig(BaseModel):
    """Configuration for a single circuit breaker instance."""
    service_name: str
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 30
    half_open_max_calls: int = 3
    monitored_exceptions: list[str] = Field(default_factory=lambda: ["TimeoutError", "ConnectionError"])


class RateLimitConfig(BaseModel):
    """Configuration for a rate limiter."""
    requests_per_window: int = 60
    window_seconds: int = 60
    scope: str = "user"  # user, ip, api_key, endpoint


class ThrottleConfig(BaseModel):
    """Configuration for a request throttler."""
    max_concurrent: int = 10
    queue_size: int = 50
    priority: int = 5  # 1 = highest, 10 = lowest


class ProfileEntry(BaseModel):
    """A single profiled operation."""
    operation: str
    duration_ms: float
    timestamp: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerformanceSnapshot(BaseModel):
    """Aggregate performance metrics for export."""
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    total_requests: int = 0
    active_circuits_open: int = 0
    retry_count: int = 0
    queue_depth: int = 0
    background_tasks_running: int = 0
