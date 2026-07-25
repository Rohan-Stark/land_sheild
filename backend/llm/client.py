from __future__ import annotations

import json
import time
from typing import Any, AsyncIterator

import httpx

from backend.config.logging import get_logger
from backend.llm.schemas.prompt import PromptMessage, PromptRequest
from backend.llm.schemas.response import LLMResponseMetrics, StreamChunk
from backend.llm.schemas.runtime import RuntimeConfig

logger = get_logger("llm.client")


class OllamaClient:
    """Production-ready async client for the Ollama API.

    Supports both full generation and token-by-token streaming.
    Does NOT handle retries or fallback — those are delegated to RetryPolicy and FallbackChain.
    """

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config
        self._base_url = config.ollama_base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(config.request_timeout_seconds, connect=10.0),
        )

    # ── Health ────────────────────────────────────────────────────

    async def health_check(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            resp = await self._client.get("/api/tags")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> list[str]:
        """Return names of all models currently loaded in Ollama."""
        try:
            resp = await self._client.get("/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except httpx.HTTPError as exc:
            logger.error("Failed to list models: %s", exc)
            return []

    async def model_available(self, model_name: str) -> bool:
        """Check if a specific model is loaded."""
        models = await self.list_models()
        return any(model_name in m for m in models)

    # ── Full Generation ───────────────────────────────────────────

    async def generate(self, request: PromptRequest) -> tuple[str, LLMResponseMetrics]:
        """Send a non-streaming chat completion and return the full text + metrics."""
        payload = self._build_payload(request, stream=False)
        start = time.perf_counter()

        resp = await self._client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed_ms = (time.perf_counter() - start) * 1000
        content = data.get("message", {}).get("content", "")

        metrics = LLMResponseMetrics(
            model_used=request.model,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            latency_ms=elapsed_ms,
        )

        logger.info(
            "Generated response model=%s latency=%.0fms tokens=%d",
            request.model,
            elapsed_ms,
            metrics.completion_tokens,
        )
        return content, metrics

    # ── Streaming Generation ──────────────────────────────────────

    async def generate_stream(self, request: PromptRequest) -> AsyncIterator[StreamChunk]:
        """Yield incremental StreamChunk objects from a streaming chat completion."""
        payload = self._build_payload(request, stream=True)

        async with self._client.stream(
            "POST",
            "/api/chat",
            json=payload,
            timeout=httpx.Timeout(self._config.streaming_timeout_seconds, connect=10.0),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                content = data.get("message", {}).get("content", "")
                done = data.get("done", False)
                yield StreamChunk(content=content, done=done, model=request.model)

                if done:
                    return

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _build_payload(request: PromptRequest, stream: bool) -> dict[str, Any]:
        messages = [{"role": m.role.value, "content": m.content} for m in request.messages]
        return {
            "model": request.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "num_predict": request.max_tokens,
            },
        }

    async def close(self) -> None:
        await self._client.aclose()
