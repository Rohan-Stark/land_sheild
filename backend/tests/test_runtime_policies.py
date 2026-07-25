from __future__ import annotations

import httpx
import pytest

from backend.llm.fallback import FallbackChain
from backend.llm.manager import ModelManager
from backend.llm.retry import RetryPolicy
from backend.llm.schemas.runtime import RuntimeConfig


@pytest.mark.asyncio
async def test_retry_policy():
    config = RuntimeConfig(retry_count=2, retry_base_delay_seconds=0.01)
    retry = RetryPolicy(config)
    
    attempts = 0
    
    async def mock_fail_then_succeed():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise httpx.TimeoutException("Timeout")
        return "Success"
        
    result = await retry.execute(mock_fail_then_succeed)
    assert result == "Success"
    assert attempts == 2


@pytest.mark.asyncio
async def test_retry_policy_exhausted():
    config = RuntimeConfig(retry_count=1, retry_base_delay_seconds=0.01)
    retry = RetryPolicy(config)
    
    async def always_fail():
        raise httpx.TimeoutException("Timeout")
        
    with pytest.raises(httpx.TimeoutException):
        await retry.execute(always_fail)


@pytest.mark.asyncio
async def test_fallback_chain():
    config = RuntimeConfig(default_model="llama", fallback_models=["qwen", "gemma"])
    manager = ModelManager(config, client=None)  # type: ignore
    
    # We will just verify it cycles the correct models
    assert manager.all_models == ["llama", "qwen", "gemma"]
