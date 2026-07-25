from __future__ import annotations

from typing import AsyncIterator

from backend.config.logging import get_logger
from backend.llm.client import OllamaClient
from backend.llm.manager import ModelManager
from backend.llm.schemas.prompt import PromptRequest
from backend.llm.schemas.response import LLMResponseMetrics, StreamChunk

logger = get_logger("llm.fallback")


class FallbackChain:
    """Automatically walks the model priority list when the current model fails.

    The chain tries the preferred model first, then each fallback in order.
    If all models fail, the last exception is raised.
    """

    def __init__(self, manager: ModelManager, client: OllamaClient) -> None:
        self._manager = manager
        self._client = client

    async def generate_with_fallback(
        self, request: PromptRequest
    ) -> tuple[str, LLMResponseMetrics]:
        """Attempt generation across the entire model chain."""
        last_exc: Exception | None = None

        for model in self._manager.all_models:
            try:
                request_copy = request.model_copy(update={"model": model})
                content, metrics = await self._client.generate(request_copy)
                metrics.model_used = model
                if model != self._manager.preferred_model:
                    metrics.fallback_used = True
                    logger.info("Fallback succeeded with model: %s", model)
                return content, metrics
            except Exception as exc:
                last_exc = exc
                logger.warning("Model %s failed, trying next fallback: %s", model, exc)

        assert last_exc is not None
        raise last_exc

    async def stream_with_fallback(
        self, request: PromptRequest
    ) -> AsyncIterator[StreamChunk]:
        """Attempt streaming generation across the entire model chain."""
        last_exc: Exception | None = None

        for model in self._manager.all_models:
            try:
                request_copy = request.model_copy(update={"model": model})
                async for chunk in self._client.generate_stream(request_copy):
                    yield chunk
                return  # Streaming completed successfully
            except Exception as exc:
                last_exc = exc
                logger.warning("Stream model %s failed, trying next: %s", model, exc)

        assert last_exc is not None
        raise last_exc
