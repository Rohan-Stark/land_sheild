from __future__ import annotations

from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult, SourceReference
from backend.agents.base_agent import BaseAgent
from backend.agents.exceptions import AgentValidationError
from backend.schemas.graph import IntentCategory
from backend.utils.confidence import ConfidenceCalculator


class DocumentAgent(BaseAgent):
    """Concrete agent for handling document understanding and metadata extraction.
    
    The Document Agent MUST NEVER:
    - Determine ownership
    - Interpret legal validity
    - Declare fraud
    """

    @property
    def name(self) -> str:
        return "DocumentAgent"

    @property
    def description(self) -> str:
        return "Understands uploaded property documents and extracts metadata."

    @property
    def supported_intents(self) -> list[IntentCategory]:
        # Represents DocumentQuestion, DocumentComparison, DocumentSummary, MetadataExtraction from spec
        # Mapping to existing intents or adding general logic for now.
        return [
            IntentCategory.DOCUMENT_QUESTION,
            IntentCategory.PROPERTY_QUESTION, 
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
        return 10

    def validate(self, context: AgentContext) -> None:
        if not context.retrievalResults:
            raise AgentValidationError("DocumentAgent requires retrieved documents.")

    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        return {"action": "summarize_documents"}

    async def process(self, context: AgentContext) -> AgentResult:
        findings: list[dict[str, Any]] = []
        sources: list[SourceReference] = []
        metadata_found = {}
        missing_info = []

        total_score = 0.0
        
        # Analyze chunks (simulated for Phase 2B.2)
        for chunk in context.retrievalResults:
            meta = chunk.get("metadata", {})
            score = chunk.get("final_score", 0.0)
            chunk_id = chunk.get("chunk_id", "unknown")
            doc_id = meta.get("document_id", "unknown")
            
            total_score += score
            
            # Map source
            sources.append(
                SourceReference(
                    document_id=doc_id,
                    chunk_id=chunk_id,
                    source_type="document",
                    retrieval_score=score,
                    confidence=score
                )
            )
            
            # Extract basic metadata simulation
            if "survey_number" in meta and meta["survey_number"]:
                metadata_found["survey_number"] = meta["survey_number"]
            if "khata_number" in meta and meta["khata_number"]:
                metadata_found["khata_number"] = meta["khata_number"]

        avg_score = total_score / max(len(context.retrievalResults), 1)
        
        if not metadata_found.get("survey_number"):
            missing_info.append("Survey Number")
            
        findings.append({
            "type": "metadata",
            "extracted": metadata_found,
            "missing": missing_info
        })
        
        # Simulated LLM finding
        summary = "Extracted structural information from retrieved document chunks."

        confidence = ConfidenceCalculator.calculate(
            retrieval_quality=avg_score,
            metadata_match=1.0 if metadata_found else 0.0,
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
            next_actions=["Review extracted metadata for accuracy."]
        )

    async def post_process(self, result: AgentResult) -> AgentResult:
        # Enforce strict constraints on the summary output
        forbidden_phrases = ["owns the property", "is legally valid", "fraudulent"]
        for phrase in forbidden_phrases:
            if phrase in result.summary.lower():
                result.warnings.append(f"Filtered potentially interpretative phrase: '{phrase}'")
        return result
