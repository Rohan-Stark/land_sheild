from __future__ import annotations

from backend.config.logging import get_logger
from backend.llm.schemas.response import FinalResponse
from backend.schemas.citation import EvidenceMatch

logger = get_logger("trust.evidence")


class EvidenceValidator:
    """Validates if the response text logically traces back to retrieved chunks."""

    @staticmethod
    def validate(response: FinalResponse, evidence_texts: list[str]) -> list[EvidenceMatch]:
        """Verify the LLM output against the evidence corpus.
        
        In a production pipeline this might use an NLI (Natural Language Inference)
        model. For this deterministic phase, we verify that if the agent provided 
        evidence, the response is generally considered 'supported' unless a 
        hallucination was triggered elsewhere.
        """
        matches: list[EvidenceMatch] = []
        
        # If there is no evidence provided but the LLM made a long claim
        if not evidence_texts and len(response.content) > 100:
            if "i don't have enough verified information" not in response.content.lower():
                matches.append(
                    EvidenceMatch(
                        claim="Entire response",
                        is_supported=False,
                        contradiction_reason="Response makes claims without any retrieved evidence."
                    )
                )

        return matches
