from __future__ import annotations


class ConfidenceCalculator:
    """Reusable calculator for agent output confidence scores."""

    @staticmethod
    def calculate(
        retrieval_quality: float = 0.0,
        metadata_match: float = 0.0,
        keyword_match: float = 0.0,
        semantic_similarity: float = 0.0,
        tool_success: bool = True,
        source_count: int = 0,
    ) -> float:
        """Calculate a 0.0 to 1.0 confidence score based on input metrics.
        
        Weighting:
        - Retrieval Quality (scores from chunking/ranking) : 30%
        - Semantic Similarity (direct match)               : 20%
        - Metadata/Keyword Match (accuracy factors)        : 20%
        - Source Count (corroboration, capped at 3)        : 10%
        - Tool Success (failure drops confidence)          : 20%
        """
        
        base_score = 0.0
        
        # 30% from retrieval quality
        base_score += min(1.0, max(0.0, retrieval_quality)) * 0.30
        
        # 20% from semantic similarity
        base_score += min(1.0, max(0.0, semantic_similarity)) * 0.20
        
        # 20% from metadata/keyword (average of both if provided)
        match_avg = (metadata_match + keyword_match) / 2
        base_score += min(1.0, max(0.0, match_avg)) * 0.20
        
        # 10% from sources (max credit at 3 sources)
        source_credit = min(source_count / 3.0, 1.0)
        base_score += source_credit * 0.10
        
        # 20% from tool execution success
        if tool_success:
            base_score += 0.20
            
        return round(min(1.0, base_score), 4)
