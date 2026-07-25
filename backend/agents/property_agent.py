from __future__ import annotations

from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult, SourceReference
from backend.agents.base_agent import BaseAgent
from backend.agents.exceptions import AgentValidationError
from backend.schemas.graph import IntentCategory
from backend.utils.confidence import ConfidenceCalculator


class PropertyAgent(BaseAgent):
    """Concrete agent for understanding overall property status, health, and timelines."""

    @property
    def name(self) -> str:
        return "PropertyAgent"

    @property
    def description(self) -> str:
        return "Analyzes property health, timelines, alerts, and risk factors."

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [
            IntentCategory.PROPERTY_QUESTION,
            IntentCategory.ALERT_QUESTION,
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
        return 20

    def validate(self, context: AgentContext) -> None:
        if not context.entities.propertyId:
            raise AgentValidationError("PropertyAgent strictly requires a propertyId to evaluate health.")
        if not context.retrievalResults:
            raise AgentValidationError("PropertyAgent requires retrieved property context.")

    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        return {"action": "evaluate_health_and_timeline"}

    async def process(self, context: AgentContext) -> AgentResult:
        findings: list[dict[str, Any]] = []
        sources: list[SourceReference] = []
        warnings: list[str] = []
        
        # Simulated risk logic based on context size
        risk_score = 0
        has_alerts = False

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
                    source_type="property_record",
                    retrieval_score=score,
                    confidence=score
                )
            )

            if "alert" in chunk.get("text", "").lower() or meta.get("is_alert"):
                has_alerts = True
                risk_score += 1
                warnings.append(f"Potential risk detected in document {doc_id}")

        avg_score = total_score / max(len(context.retrievalResults), 1)
        
        findings.append({
            "type": "health_evaluation",
            "risk_level": "high" if risk_score > 1 else ("medium" if risk_score == 1 else "low"),
            "active_alerts": has_alerts
        })

        health_score_numeric = 100 - (risk_score * 20)
        
        summary = f"Property health evaluation complete. Estimated health score: {health_score_numeric}/100."

        confidence = ConfidenceCalculator.calculate(
            retrieval_quality=avg_score,
            metadata_match=1.0,  # We know propertyId matched due to validation
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
            warnings=warnings,
            next_actions=["Review alerts if any are active.", "Check recent timeline events."]
        )

    async def post_process(self, result: AgentResult) -> AgentResult:
        # Standardize outputs
        return result
