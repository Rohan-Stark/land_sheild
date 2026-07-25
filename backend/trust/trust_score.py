from __future__ import annotations

from backend.config.logging import get_logger
from backend.schemas.trust import ConfidenceMetrics, TrustScore

logger = get_logger("trust.trust_score")


class TrustScoreCalculator:
    """Calculates the final 0-100 Trust Score based on confidence and citations."""

    @staticmethod
    def calculate(
        confidence: ConfidenceMetrics,
        citation_count: int,
        hallucinations: list[str]
    ) -> TrustScore:
        """Derive the final TrustScore."""
        # Baseline from confidence (0-100 scale)
        raw_score = int(confidence.overall_confidence * 100)
        factors = []

        # Adjust for citations
        if citation_count >= 3:
            raw_score += 10
            factors.append("Backed by multiple evidence sources.")
        elif citation_count == 0:
            raw_score -= 30
            factors.append("No direct citations provided.")

        # Hard penalty for hallucinations
        if hallucinations:
            raw_score -= 80
            factors.append("Potential hallucinated facts detected.")

        # Clamp between 0 and 100
        score = max(0, min(100, raw_score))

        # Categorize
        if score >= 85:
            cat = "Excellent"
        elif score >= 70:
            cat = "Good"
        elif score >= 50:
            cat = "Fair"
        else:
            cat = "Low"

        return TrustScore(
            score=score,
            category=cat,
            factors=factors
        )
