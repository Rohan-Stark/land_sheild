from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.schemas.citation import Citation, EvidenceMatch


class ConfidenceMetrics(BaseModel):
    """Granular breakdown of how confidence was calculated."""
    agent_confidence: float = 0.0
    retrieval_quality: float = 0.0
    source_count_score: float = 0.0
    metadata_match_score: float = 0.0
    memory_consistency_score: float = 0.0
    overall_confidence: float = 0.0
    explanation: str = ""


class TrustScore(BaseModel):
    """The final trust score exposed to the frontend."""
    score: int = 0  # 0 to 100
    category: str = "Low"  # Excellent, Good, Fair, Low
    factors: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    """The complete safety, trust, and evidence verification packet."""
    is_safe: bool
    is_supported: bool
    trust_score: TrustScore
    confidence: ConfidenceMetrics
    citations: list[Citation] = Field(default_factory=list)
    evidence_matches: list[EvidenceMatch] = Field(default_factory=list)
    hallucinations_detected: list[str] = Field(default_factory=list)
    safety_violations: list[str] = Field(default_factory=list)
    rejection_reason: str | None = None
