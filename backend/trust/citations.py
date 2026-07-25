from __future__ import annotations

from typing import Any

from backend.agents.agent_result import AgentResult, SourceReference
from backend.config.logging import get_logger
from backend.schemas.citation import Citation

logger = get_logger("trust.citations")


class CitationGenerator:
    """Generates rigorous citations mapping LLM responses back to Agent sources."""

    @staticmethod
    def generate(agent_result: AgentResult | None) -> list[Citation]:
        """Convert Agent SourceReferences into final frontend-facing Citations."""
        if not agent_result or not agent_result.sources:
            return []

        citations: list[Citation] = []
        for src in agent_result.sources:
            citations.append(
                Citation(
                    document_name=CitationGenerator._resolve_doc_name(src),
                    document_type=CitationGenerator._resolve_doc_type(src),
                    page_number=src.page_number,
                    chunk_id=src.chunk_id,
                    source_type=src.source_type,
                    retrieval_score=src.retrieval_score,
                    reranker_score=src.reranker_score,
                    confidence=src.confidence,
                )
            )

        logger.debug("Generated %d citations from agent result.", len(citations))
        return citations

    @staticmethod
    def _resolve_doc_name(source: SourceReference) -> str:
        # In a real DB integration, this would cross-reference document_id to title
        return f"Document {source.document_id[-6:]}"

    @staticmethod
    def _resolve_doc_type(source: SourceReference) -> str:
        return "Unknown"
