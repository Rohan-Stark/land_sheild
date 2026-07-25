from __future__ import annotations

from typing import Any

from backend.agents.agent_result import AgentResult
from backend.config.logging import get_logger
from backend.llm.schemas.response import FinalResponse
from backend.schemas.trust import VerificationResult
from backend.safety.validator import SafetyValidator
from backend.trust.citations import CitationGenerator
from backend.trust.confidence import ConfidenceEngine
from backend.trust.evidence import EvidenceValidator
from backend.trust.hallucination import HallucinationDetector
from backend.trust.trust_score import TrustScoreCalculator

logger = get_logger("trust.verification")


class ResponseVerifier:
    """The final gatekeeper. Executes the entire Trust, Safety, and Evidence pipeline.

    If the response violates safety policies or contains hallucinations, it is
    deterministically rejected and replaced with a structured error.
    """

    def __init__(self) -> None:
        self._safety = SafetyValidator()
        self._hallucination = HallucinationDetector()
        self._evidence = EvidenceValidator()
        self._confidence = ConfidenceEngine()
        self._citations = CitationGenerator()
        self._score = TrustScoreCalculator()

    def verify(
        self,
        response: FinalResponse,
        agent_result: AgentResult | None,
        retrieved_chunks: list[dict[str, Any]] | None
    ) -> VerificationResult:
        logger.info("Starting response verification for request %s", response.request_id)

        # 1. Safety Policies
        safety_violations = self._safety.validate(response)
        
        # 2. Extract raw evidence text for hallucination/evidence checks
        evidence_texts = [c.get("text", "") for c in (retrieved_chunks or [])]
        
        # 3. Hallucination Detection
        hallucinations = self._hallucination.detect(response, evidence_texts)
        
        # 4. Evidence Validation
        evidence_matches = self._evidence.validate(response, evidence_texts)
        is_supported = not any(not m.is_supported for m in evidence_matches)

        # 5. Citations & Confidence
        citations = self._citations.generate(agent_result)
        confidence = self._confidence.evaluate(agent_result)
        
        # 6. Final Trust Score
        trust_score = self._score.calculate(
            confidence=confidence,
            citation_count=len(citations),
            hallucinations=hallucinations
        )

        # 7. Decision
        is_safe = len(safety_violations) == 0
        rejection_reason = None

        if not is_safe:
            rejection_reason = "Response blocked due to safety policy violations."
            logger.error(rejection_reason)
        elif hallucinations:
            rejection_reason = "Response blocked due to detected hallucinations."
            logger.error(rejection_reason)

        return VerificationResult(
            is_safe=is_safe,
            is_supported=is_supported,
            trust_score=trust_score,
            confidence=confidence,
            citations=citations,
            evidence_matches=evidence_matches,
            hallucinations_detected=hallucinations,
            safety_violations=safety_violations,
            rejection_reason=rejection_reason
        )
