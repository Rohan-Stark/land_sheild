from __future__ import annotations

from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult, SourceReference
from backend.agents.base_agent import BaseAgent
from backend.schemas.graph import IntentCategory
from backend.utils.confidence import ConfidenceCalculator


class LegalGuidanceAgent(BaseAgent):
    """Concrete agent for explaining property procedures and legal concepts.
    
    The Legal Guidance Agent MUST NEVER:
    - Determine ownership
    - Predict court decisions
    - Provide legal verdicts
    - Guarantee legal outcomes
    """

    @property
    def name(self) -> str:
        return "LegalGuidanceAgent"

    @property
    def description(self) -> str:
        return "Explains property procedures and provides general educational legal guidance."

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [
            IntentCategory.LEGAL_GUIDANCE,
        ]

    @property
    def supported_entities(self) -> list[str]:
        return []

    @property
    def required_tools(self) -> list[type]:
        return []

    @property
    def requires_retrieval(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return 30

    def validate(self, context: AgentContext) -> None:
        # No strict entity requirements, relies primarily on semantic retrieval from Knowledge Base
        pass

    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        return {"action": "explain_procedure"}

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
                    source_type="knowledge_base",
                    retrieval_score=score,
                    confidence=score
                )
            )

        avg_score = total_score / max(len(context.retrievalResults), 1)
        
        findings.append({
            "type": "procedure_explanation",
            "procedure_steps": ["Step 1: Placeholder", "Step 2: Placeholder"],
            "required_documents": ["Identity Proof", "Sale Deed"]
        })

        summary = "Provided educational explanation on requested property procedures."

        confidence = ConfidenceCalculator.calculate(
            retrieval_quality=avg_score,
            metadata_match=0.0,
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
            next_actions=["Consult a qualified property lawyer for specific advice."]
        )

    async def post_process(self, result: AgentResult) -> AgentResult:
        # Mandatory educational disclaimer
        disclaimer = "This information is educational only and should not be considered legal advice. Please consult a qualified property lawyer."
        
        if disclaimer not in result.summary:
            result.summary = f"{result.summary}\n\nIMPORTANT: {disclaimer}"
            
        result.warnings.append(disclaimer)
        
        return result
