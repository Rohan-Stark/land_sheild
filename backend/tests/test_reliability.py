from __future__ import annotations

import asyncio
import time

import pytest

from backend.performance.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from backend.performance.retry import RetryManager
from backend.schemas.performance import CircuitState


def test_circuit_breaker_closed_to_open():
    config = CircuitBreakerConfig(service_name="test_svc", failure_threshold=3, recovery_timeout_seconds=1)
    cb = CircuitBreaker(config)

    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    # Trip the breaker
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()

    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False


def test_circuit_breaker_recovery():
    config = CircuitBreakerConfig(
        service_name="test_recovery",
        failure_threshold=2,
        recovery_timeout_seconds=0,  # immediate recovery for test
        half_open_max_calls=2,
    )
    cb = CircuitBreaker(config)

    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Since timeout is 0, checking state should transition to HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.allow_request() is True

    # Successful probes recover the circuit
    cb.record_success()
    cb.record_success()
    assert cb.state == CircuitState.CLOSED


def test_circuit_breaker_half_open_failure():
    config = CircuitBreakerConfig(
        service_name="test_half_fail",
        failure_threshold=1,
        recovery_timeout_seconds=0,
        half_open_max_calls=2,
    )
    cb = CircuitBreaker(config)

    cb.record_failure()
    _ = cb.state  # first evaluation
    assert cb.state == CircuitState.HALF_OPEN  # auto-recovery due to timeout=0

    cb.record_failure()
    assert cb.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_retry_manager_success():
    call_count = 0

    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("transient")
        return "ok"

    rm = RetryManager(max_retries=3, base_delay_seconds=0.01)
    result = await rm.execute(flaky)
    assert result == "ok"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_manager_permanent_failure():
    async def bad():
        raise ValueError("permanent")

    rm = RetryManager(max_retries=3, base_delay_seconds=0.01)
    with pytest.raises(ValueError, match="permanent"):
        await rm.execute(bad)


@pytest.mark.asyncio
async def test_retry_manager_exhaustion():
    async def always_fail():
        raise ConnectionError("down")

    rm = RetryManager(max_retries=2, base_delay_seconds=0.01)
    with pytest.raises(ConnectionError):
        await rm.execute(always_fail)
