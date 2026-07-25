from __future__ import annotations

from backend.config.logging import get_logger
from backend.agents.agent_result import AgentResult
from backend.llm.schemas.response import FinalResponse, LLMResponseMetrics

logger = get_logger("llm.responses.synthesizer")


class ResponseSynthesizer:
    """Merges the raw LLM text output with agent metadata into a FinalResponse.

    Responsibilities:
    - Combine LLM-generated text with agent warnings, next_actions, and confidence.
    - Normalize formatting (strip trailing whitespace, collapse blank lines).
    - Handle empty or malformed LLM output gracefully.
    """

    def synthesize(
        self,
        llm_content: str,
        agent_result: AgentResult | None,
        metrics: LLMResponseMetrics,
        request_id: str = "",
        output_format: str = "markdown",
    ) -> FinalResponse:
        content = self._normalize(llm_content)

        if not content:
            content = self._build_fallback_content(agent_result)

        warnings: list[str] = []
        next_actions: list[str] = []
        confidence = 0.0
        agent_name = ""

        if agent_result:
            warnings = list(agent_result.warnings)
            next_actions = list(agent_result.next_actions)
            confidence = agent_result.confidence
            agent_name = agent_result.agent

        return FinalResponse(
            request_id=request_id,
            status="success",
            content=content,
            format=output_format,
            agent=agent_name,
            confidence=confidence,
            warnings=warnings,
            next_actions=next_actions,
            metrics=metrics,
        )

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """Strip excess whitespace and collapse blank lines."""
        lines = text.strip().split("\n")
        cleaned: list[str] = []
        prev_blank = False
        for line in lines:
            stripped = line.rstrip()
            if not stripped:
                if not prev_blank:
                    cleaned.append("")
                prev_blank = True
            else:
                cleaned.append(stripped)
                prev_blank = False
        return "\n".join(cleaned).strip()

    @staticmethod
    def _build_fallback_content(agent_result: AgentResult | None) -> str:
        """If the LLM returned nothing, fall back to the agent's own summary."""
        if agent_result and agent_result.summary:
            logger.warning("LLM returned empty response, using agent summary as fallback.")
            return agent_result.summary
        return "I was unable to generate a response. Please try again."
