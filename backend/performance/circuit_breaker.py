from __future__ import annotations

import time
from typing import Any, Callable

from backend.config.logging import get_logger
from backend.schemas.performance import CircuitBreakerConfig, CircuitState

logger = get_logger("performance.circuit_breaker")


class CircuitBreaker:
    """Protects external service calls using the Circuit Breaker pattern.

    States:
        CLOSED  – Normal operation. Failures are counted.
        OPEN    – All calls are immediately rejected. Waits for recovery timeout.
        HALF_OPEN – A limited number of probe calls are allowed to test recovery.
    """

    def __init__(self, config: CircuitBreakerConfig) -> None:
        self._config = config
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self._config.recovery_timeout_seconds:
                logger.info(
                    "Circuit %s transitioning OPEN -> HALF_OPEN after %.1fs",
                    self._config.service_name,
                    elapsed,
                )
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state

    @property
    def service_name(self) -> str:
        return self._config.service_name

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._config.half_open_max_calls:
                logger.info("Circuit %s recovered. HALF_OPEN -> CLOSED.", self._config.service_name)
                self._reset()
        else:
            self._failure_count = max(0, self._failure_count - 1)

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            logger.warning("Circuit %s probe failed. HALF_OPEN -> OPEN.", self._config.service_name)
            self._state = CircuitState.OPEN
            self._success_count = 0
        elif self._failure_count >= self._config.failure_threshold:
            logger.warning(
                "Circuit %s tripped after %d failures. CLOSED -> OPEN.",
                self._config.service_name,
                self._failure_count,
            )
            self._state = CircuitState.OPEN

    def allow_request(self) -> bool:
        """Return True if the circuit allows an outgoing call."""
        current = self.state  # triggers auto-recovery check
        if current == CircuitState.CLOSED:
            return True
        if current == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            return self._half_open_calls <= self._config.half_open_max_calls
        return False

    def _reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0


class CircuitBreakerRegistry:
    """Central registry holding circuit breakers for all protected services."""

    def __init__(self) -> None:
        self._breakers: dict[str, CircuitBreaker] = {}

    def register(self, config: CircuitBreakerConfig) -> CircuitBreaker:
        breaker = CircuitBreaker(config)
        self._breakers[config.service_name] = breaker
        logger.info("Registered circuit breaker for %s", config.service_name)
        return breaker

    def get(self, service_name: str) -> CircuitBreaker | None:
        return self._breakers.get(service_name)

    def get_open_circuits(self) -> list[str]:
        return [name for name, cb in self._breakers.items() if cb.state == CircuitState.OPEN]


# Singleton registry pre-loaded with default service protections
circuit_registry = CircuitBreakerRegistry()

_DEFAULT_SERVICES = ["ollama", "redis", "postgres", "chromadb"]
for _svc in _DEFAULT_SERVICES:
    circuit_registry.register(CircuitBreakerConfig(service_name=_svc))
