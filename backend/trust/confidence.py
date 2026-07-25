from __future__ import annotations

from backend.agents.agent_result import AgentResult
from backend.config.logging import get_logger
from backend.schemas.trust import ConfidenceMetrics

logger = get_logger("trust.confidence")


class ConfidenceEngine:
    """Calculates granular and overall confidence scores for a response."""

    @staticmethod
    def evaluate(agent_result: AgentResult | None) -> ConfidenceMetrics:
        """Derive confidence metrics based on agent output and retrieved sources."""
        if not agent_result:
            return ConfidenceMetrics(explanation="No agent context provided.")

        agent_conf = agent_result.confidence
        sources = agent_result.sources
        
        # 1. Retrieval Quality (Average reranker score)
        retrieval_qual = 0.0
        if sources:
            retrieval_qual = sum(s.reranker_score for s in sources) / len(sources)

        # 2. Source Count Score (diminishing returns maxing out at 3 sources)
        source_count_score = min(len(sources) / 3.0, 1.0)

        # 3. Overall calculation (weighted sum)
        # 50% Agent Confidence, 30% Retrieval Quality, 20% Source Density
        overall = (agent_conf * 0.5) + (retrieval_qual * 0.3) + (source_count_score * 0.2)

        # Explanation generation
        if overall > 0.8:
            exp = f"Confidence is High because the answer is supported by {len(sources)} highly relevant sources."
        elif overall > 0.5:
            exp = f"Confidence is Medium based on partial evidence from {len(sources)} sources."
        else:
            exp = "Confidence is Low due to weak or missing evidence."

        return ConfidenceMetrics(
            agent_confidence=agent_conf,
            retrieval_quality=retrieval_qual,
            source_count_score=source_count_score,
            overall_confidence=overall,
            explanation=exp
        )
