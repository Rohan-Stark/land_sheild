from __future__ import annotations

from typing import Any

from backend.agents.agent_result import AgentResult
from backend.config.logging import get_logger
from backend.llm.schemas.prompt import PromptContext

logger = get_logger("llm.prompting.builder")


class PromptBuilder:
    """Transforms AgentResult outputs and user questions into a PromptContext.

    Responsibilities:
    - Merge agent findings and retrieved chunks
    - Remove duplicate chunk content
    - Order chunks by relevance score descending
    - Normalize text formatting
    """

    def build(
        self,
        user_question: str,
        agent_result: AgentResult | None = None,
        retrieved_chunks: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PromptContext:
        chunks = self._deduplicate_chunks(retrieved_chunks or [])
        chunks = self._sort_by_relevance(chunks)

        agent_sources: list[dict[str, Any]] = []
        if agent_result:
            agent_sources = [s.model_dump() for s in agent_result.sources]

        return PromptContext(
            user_question=user_question,
            agent_summary=agent_result.summary if agent_result else "",
            agent_findings=agent_result.findings if agent_result else [],
            agent_sources=agent_sources,
            agent_warnings=agent_result.warnings if agent_result else [],
            agent_next_actions=agent_result.next_actions if agent_result else [],
            retrieved_chunks=chunks,
            metadata=metadata or {},
        )

    # ── Internals ─────────────────────────────────────────────────

    @staticmethod
    def _deduplicate_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove chunks with identical text content."""
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for c in chunks:
            text = c.get("text", "")
            if text and text not in seen:
                seen.add(text)
                unique.append(c)
        return unique

    @staticmethod
    def _sort_by_relevance(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Order by final_score descending."""
        return sorted(chunks, key=lambda c: c.get("final_score", 0.0), reverse=True)
