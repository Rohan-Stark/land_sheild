from __future__ import annotations

import time
from typing import Any, AsyncIterator

from backend.agents.agent_result import AgentResult
from backend.config.logging import get_logger
from backend.llm.client import OllamaClient
from backend.llm.fallback import FallbackChain
from backend.llm.manager import ModelManager
from backend.llm.prompting.builder import PromptBuilder
from backend.llm.prompting.renderer import PromptRenderer
from backend.llm.prompting.validator import PromptValidator
from backend.llm.responses.synthesizer import ResponseSynthesizer
from backend.llm.responses.validator import OutputValidator
from backend.llm.retry import RetryPolicy
from backend.llm.schemas.prompt import PromptContext
from backend.llm.schemas.response import FinalResponse, LLMResponseMetrics, StreamChunk
from backend.llm.schemas.runtime import RuntimeConfig
from backend.llm.streaming.sse import sse_event_generator

logger = get_logger("llm.runtime")


class AIRuntime:
    """Top-level facade for the AI Runtime Layer.

    Orchestrates prompt building, compression, rendering, Ollama communication,
    retry, fallback, output validation, and response synthesis.

    Usage:
        runtime = AIRuntime(config)
        response = await runtime.generate(question, agent_result, intent=...)
    """

    def __init__(self, config: RuntimeConfig | None = None) -> None:
        self._config = config or RuntimeConfig()
        self._client = OllamaClient(self._config)
        self._manager = ModelManager(self._config, self._client)
        self._retry = RetryPolicy(self._config)
        self._fallback = FallbackChain(self._manager, self._client)
        self._builder = PromptBuilder()
        self._renderer = PromptRenderer(self._config)
        self._prompt_validator = PromptValidator(self._config.max_prompt_tokens)
        self._output_validator = OutputValidator()
        self._synthesizer = ResponseSynthesizer()

    # ── Full Generation ───────────────────────────────────────────

    async def generate(
        self,
        user_question: str,
        agent_result: AgentResult | None = None,
        retrieved_chunks: list[dict[str, Any]] | None = None,
        intent: str = "general_chat",
        request_id: str = "",
        user_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> FinalResponse:
        """End-to-end: build prompt → call Ollama with retry/fallback → synthesize response."""
        start = time.perf_counter()

        # 1. Build context
        context = self._builder.build(
            user_question=user_question,
            agent_result=agent_result,
            retrieved_chunks=retrieved_chunks,
            metadata=metadata,
        )

        # 2. Select model
        model = await self._manager.select_model()

        # 3. Render prompt
        prompt_request = self._renderer.render(
            context=context,
            intent=intent,
            model=model,
            request_id=request_id,
            user_id=user_id,
            stream=False,
        )

        # 4. Validate prompt
        errors = self._prompt_validator.validate(prompt_request)
        if errors:
            logger.error("Prompt validation failed: %s", errors)
            return FinalResponse(
                request_id=request_id,
                status="error",
                content="Failed to construct a valid prompt.",
                warnings=errors,
            )

        # 5. Generate with retry + fallback
        content, metrics = await self._retry.execute(
            self._fallback.generate_with_fallback, prompt_request
        )

        # 6. Validate output
        is_valid, output_errors = self._output_validator.validate(content)
        if not is_valid:
            logger.warning("Output validation issues: %s", output_errors)

        # 7. Synthesize
        metrics.latency_ms = (time.perf_counter() - start) * 1000
        response = self._synthesizer.synthesize(
            llm_content=content,
            agent_result=agent_result,
            metrics=metrics,
            request_id=request_id,
        )

        logger.info(
            "Runtime generate complete: model=%s latency=%.0fms confidence=%.2f",
            metrics.model_used,
            metrics.latency_ms,
            response.confidence,
        )
        return response

    # ── Streaming Generation ──────────────────────────────────────

    async def generate_stream(
        self,
        user_question: str,
        agent_result: AgentResult | None = None,
        retrieved_chunks: list[dict[str, Any]] | None = None,
        intent: str = "general_chat",
        request_id: str = "",
        user_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """End-to-end streaming: build prompt → stream SSE chunks."""
        context = self._builder.build(
            user_question=user_question,
            agent_result=agent_result,
            retrieved_chunks=retrieved_chunks,
            metadata=metadata,
        )

        model = await self._manager.select_model()

        prompt_request = self._renderer.render(
            context=context,
            intent=intent,
            model=model,
            request_id=request_id,
            user_id=user_id,
            stream=True,
        )

        errors = self._prompt_validator.validate(prompt_request)
        if errors:
            logger.error("Prompt validation failed for stream: %s", errors)
            yield 'data: {"error": "Invalid prompt", "done": true}\n\n'
            return

        chunk_stream = self._fallback.stream_with_fallback(prompt_request)
        async for sse_line in sse_event_generator(
            chunk_stream,
            heartbeat_interval=self._config.heartbeat_interval_seconds,
        ):
            yield sse_line

    # ── Health ────────────────────────────────────────────────────

    async def health(self) -> dict[str, Any]:
        """Return runtime health status."""
        ollama_ok = await self._client.health_check()
        model_health = await self._manager.refresh_health()
        return {
            "ollama_reachable": ollama_ok,
            "models": model_health,
            "preferred_model": self._manager.preferred_model,
        }

    async def close(self) -> None:
        await self._client.close()
