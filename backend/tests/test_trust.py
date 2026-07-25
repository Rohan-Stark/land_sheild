from __future__ import annotations

import pytest

from backend.agents.agent_result import AgentResult, SourceReference
from backend.llm.schemas.response import FinalResponse
from backend.trust.citations import CitationGenerator
from backend.trust.hallucination import HallucinationDetector
from backend.trust.trust_score import TrustScoreCalculator


def test_hallucination_detector():
    detector = HallucinationDetector()
    
    response = FinalResponse(content="The owner is John Doe based on Survey No. 999.")
    evidence = ["Survey No. 123 shows the plot is clear.", "Tax is paid."]
    
    hallucinations = detector.detect(response, evidence)
    assert len(hallucinations) == 1
    assert "999" in hallucinations[0]


def test_citation_generator():
    agent_result = AgentResult(
        agent="Test",
        sources=[
            SourceReference(document_id="doc123", chunk_id="chunk1", confidence=0.9)
        ]
    )
    
    citations = CitationGenerator.generate(agent_result)
    assert len(citations) == 1
    assert "doc123" in citations[0].document_name
    assert citations[0].chunk_id == "chunk1"


def test_trust_score_calculator():
    from backend.schemas.trust import ConfidenceMetrics
    
    calc = TrustScoreCalculator()
    conf = ConfidenceMetrics(overall_confidence=0.9)
    
    # 90% confidence + 3 citations = 100
    score = calc.calculate(conf, citation_count=3, hallucinations=[])
    assert score.score == 100
    assert score.category == "Excellent"
    
    # Hallucination drops score by 80
    score2 = calc.calculate(conf, citation_count=3, hallucinations=["Invented ID"])
    assert score2.score == 20
    assert score2.category == "Low"
