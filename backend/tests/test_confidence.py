from __future__ import annotations

from backend.utils.confidence import ConfidenceCalculator


def test_confidence_perfect_score():
    score = ConfidenceCalculator.calculate(
        retrieval_quality=1.0,
        metadata_match=1.0,
        keyword_match=1.0,
        semantic_similarity=1.0,
        tool_success=True,
        source_count=3,
    )
    # 0.3 + 0.2 + 0.2 + 0.1 + 0.2 = 1.0
    assert score == 1.0


def test_confidence_partial_score():
    score = ConfidenceCalculator.calculate(
        retrieval_quality=0.5,    # 0.5 * 0.3 = 0.15
        metadata_match=0.0,       # 0.0 * 0.2 = 0.0
        keyword_match=0.0,        #
        semantic_similarity=0.5,  # 0.5 * 0.2 = 0.1
        tool_success=False,       # 0.0
        source_count=1,           # (1/3) * 0.1 = 0.0333
    )
    # Total: ~ 0.2833
    assert abs(score - 0.2833) < 0.01


def test_confidence_caps_at_one():
    score = ConfidenceCalculator.calculate(
        retrieval_quality=2.0,    # Maxes at 1.0
        metadata_match=5.0,
        keyword_match=5.0,
        semantic_similarity=5.0,
        tool_success=True,
        source_count=10,          # Maxes at 3
    )
    assert score == 1.0
