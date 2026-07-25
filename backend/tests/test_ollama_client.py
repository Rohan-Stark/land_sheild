from __future__ import annotations

import httpx
import pytest

from backend.llm.client import OllamaClient
from backend.llm.schemas.prompt import PromptMessage, PromptRequest, PromptRole
from backend.llm.schemas.runtime import RuntimeConfig


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("Error", request=None, response=self)  # type: ignore


@pytest.fixture
def mock_httpx_post(monkeypatch):
    async def mock_post(*args, **kwargs):
        return MockResponse({
            "model": "llama3.1",
            "message": {"role": "assistant", "content": "Mocked response"},
            "prompt_eval_count": 10,
            "eval_count": 5
        })

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)


@pytest.mark.asyncio
async def test_ollama_generate(mock_httpx_post):
    config = RuntimeConfig()
    client = OllamaClient(config)
    
    request = PromptRequest(
        model="llama3.1",
        messages=[PromptMessage(role=PromptRole.USER, content="Hello")]
    )
    
    content, metrics = await client.generate(request)
    
    assert content == "Mocked response"
    assert metrics.model_used == "llama3.1"
    assert metrics.prompt_tokens == 10
    assert metrics.completion_tokens == 5
    
    await client.close()
