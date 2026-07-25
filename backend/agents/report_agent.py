from __future__ import annotations

from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult, SourceReference
from backend.agents.base_agent import BaseAgent
from backend.agents.exceptions import AgentValidationError
from backend.schemas.graph import IntentCategory
from backend.utils.confidence import ConfidenceCalculator


class ReportAgent(BaseAgent):
    """Concrete agent for generating structured reports, timelines, and summaries."""

    @property
    def name(self) -> str:
        return "ReportAgent"

    @property
    def description(self) -> str:
        return "Aggregates property history, documents, and inspections into structured reports."

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [
            IntentCategory.REPORT_REQUEST,
            IntentCategory.INSPECTION_QUESTION,
        ]

    @property
    def supported_entities(self) -> list[str]:
        return ["propertyId"]

    @property
    def required_tools(self) -> list[type]:
        return []

    @property
    def requires_retrieval(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return 40

    def validate(self, context: AgentContext) -> None:
        if not context.entities.propertyId:
            raise AgentValidationError("ReportAgent requires a propertyId to aggregate reports.")
        if not context.retrievalResults:
            raise AgentValidationError("ReportAgent requires retrieved historical context.")

    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        return {"action": "generate_report"}

    async def process(self, context: AgentContext) -> AgentResult:
        findings: list[dict[str, Any]] = []
        sources: list[SourceReference] = []

        total_score = 0.0
        
        for chunk in context.retrievalResults:
            meta = chunk.get("metadata", {})
            score = chunk.get("final_score", 0.0)
            chunk_id = chunk.get("chunk_id", "unknown")
            doc_id = meta.get("document_id", "unknown")
            
            total_score += score
            sources.append(
                SourceReference(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    source_type="report_evidence",
                    retrieval_score=score,
                    confidence=score
                )
            )

        avg_score = total_score / max(len(context.retrievalResults), 1)
        
        findings.append({
            "type": "structured_report",
            "report_sections": ["Property Summary", "Evidence Timeline", "Recommendations"]
        })

        summary = "Successfully aggregated retrieved data into a structured report format."

        confidence = ConfidenceCalculator.calculate(
            retrieval_quality=avg_score,
            metadata_match=1.0,
            semantic_similarity=avg_score,
            source_count=len(sources)
        )

        return AgentResult(
            agent=self.name,
            status="success",
            summary=summary,
            findings=findings,
            sources=sources,
            confidence=confidence,
            next_actions=["Export report to PDF", "Share report with stakeholders"]
        )

    async def post_process(self, result: AgentResult) -> AgentResult:
        # Standardize outputs
        return result
