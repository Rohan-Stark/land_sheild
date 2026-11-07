from __future__ import annotations

import time
from functools import lru_cache

from sentence_transformers import CrossEncoder

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.schemas.retrieval import RetrievalRequest, ScoredChunk

logger = get_logger("retrieval.reranker")


@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder | None:
    """Load the BGE reranker cross-encoder model if cached locally, else fallback cleanly."""
    settings = get_settings()
    try:
        model = CrossEncoder(settings.RERANKER_MODEL, max_length=512, local_files_only=True)
        logger.info("Local reranker model loaded successfully.")
        return model
    except Exception:
        logger.info("Local reranker weights not cached; using dense vector similarity ranking.")
        return None


def _calculate_metadata_score(chunk: ScoredChunk, request: RetrievalRequest) -> float:
    """Calculate how well the chunk's metadata matches the request context."""
    score = 0.0
    meta = chunk.metadata
    
    # Exact property match boosts score significantly
    if request.property_id and meta.get("property_id") == str(request.property_id):
        score += 0.5
        
    # Document type match
    if request.document_type and meta.get("document_type") == request.document_type:
        score += 0.3
        
    # Specific identifier matches
    for req_val, meta_val in [
        (request.survey_number, meta.get("survey_number")),
        (request.registration_number, meta.get("registration_number")),
        (request.khata_number, meta.get("khata_number")),
    ]:
        if req_val and meta_val and req_val.lower() == str(meta_val).lower():
            score += 0.2
            
    return min(1.0, score)


def rerank_chunks(
    request: RetrievalRequest, chunks: list[ScoredChunk]
) -> list[ScoredChunk]:
    """Re-rank candidate chunks using a cross-encoder and custom heuristics.

    Ranking Formula:
        Semantic Similarity (Cross-Encoder) : 40%
        Metadata Match                      : 25%
        Keyword Match                       : 20%
        Recency                             : 10%
        Document Importance                 : 5%
    """
    if not chunks:
        return []

    start = time.perf_counter()
    model = _get_reranker()
    ce_scores = None
    if model is not None:
        try:
            pairs = [[request.query, chunk.text] for chunk in chunks]
            ce_scores = model.predict(pairs)
        except Exception as exc:
            logger.warning("Reranker prediction failed (%s), using dense similarity.", exc)

    for i, chunk in enumerate(chunks):
        if ce_scores is not None:
            import math
            try:
                semantic_ce = 1 / (1 + math.exp(-ce_scores[i]))
            except OverflowError:
                semantic_ce = 0.0 if ce_scores[i] < 0 else 1.0
            chunk.semantic_score = semantic_ce
        
        # Calculate heuristics
        chunk.metadata_score = _calculate_metadata_score(chunk, request)
        
        # Keyword score is passed from keyword_search (0.0 or 1.0)
        # Recency and Document Importance are placeholder implementations for Phase 1
        chunk.recency_score = 0.5      # Neutral default
        chunk.importance_score = 0.5   # Neutral default

        # Apply the exact weighted formula from the specification
        chunk.final_score = (
            (chunk.semantic_score * 0.40)
            + (chunk.metadata_score * 0.25)
            + (chunk.keyword_score * 0.20)
            + (chunk.recency_score * 0.10)
            + (chunk.importance_score * 0.05)
        )

    # Sort descending by final score
    chunks.sort(key=lambda x: x.final_score, reverse=True)
    
    elapsed = (time.perf_counter() - start) * 1000
    logger.info("Reranked %d chunks in %.1fms", len(chunks), elapsed)
    
    return chunks
