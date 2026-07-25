from __future__ import annotations

import time

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.retrieval.compression import compress_context
from backend.retrieval.context_builder import build_context
from backend.retrieval.keyword_search import execute_keyword_search
from backend.retrieval.metadata_filter import build_chroma_filter
from backend.retrieval.reranker import rerank_chunks
from backend.retrieval.semantic_search import execute_semantic_search
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse, ScoredChunk

logger = get_logger("retrieval.retriever")


async def hybrid_retrieve(
    request: RetrievalRequest, db: AsyncSession
) -> RetrievalResponse:
    """Execute the full Hybrid Retrieval Pipeline (Steps 8-14).

    Workflow:
        1. Metadata Filter
        2. Keyword Search (PostgreSQL FTS)
        3. Semantic Search (ChromaDB)
        4. Merge
        5. Re-rank (BGE Cross-Encoder + Heuristics)
        6. Context Builder
        7. Context Compression
    """
    total_start = time.perf_counter()
    settings = get_settings()

    # 1. Metadata Filter for ChromaDB
    chroma_filter = build_chroma_filter(request)

    # 2 & 3. Parallel-ish Search Execution
    # (Since ChromaDB API is currently synchronous in this setup, we run them sequentially.
    # In a fully async Chroma setup, we'd use asyncio.gather)
    keyword_results = await execute_keyword_search(request, db)
    semantic_results = execute_semantic_search(request, chroma_filter)

    # 4. Merge results
    merged_map: dict[str, ScoredChunk] = {}

    for chunk in semantic_results:
        merged_map[chunk.chunk_id] = chunk

    for chunk in keyword_results:
        if chunk.chunk_id in merged_map:
            # If found in both, combine scores (reranker will normalize this later)
            merged_map[chunk.chunk_id].keyword_score = chunk.keyword_score
        else:
            merged_map[chunk.chunk_id] = chunk

    merged_chunks = list(merged_map.values())
    logger.info("Merged pool size before reranking: %d chunks", len(merged_chunks))

    # 5. Re-rank
    ranked_chunks = rerank_chunks(request, merged_chunks)

    # Apply Top K slice after reranking
    top_k_chunks = ranked_chunks[: settings.FINAL_TOP_K]

    # 6. Context Builder
    context = build_context(top_k_chunks)

    # 7. Context Compression
    compressed_context = compress_context(context)

    total_time = (time.perf_counter() - total_start) * 1000
    logger.info(
        "Hybrid retrieval completed in %.1fms. Returning %d chunks.",
        total_time, len(compressed_context.chunks)
    )

    return RetrievalResponse(
        query=request.query,
        context=compressed_context,
        retrieval_time_ms=total_time,
        chunk_count=len(compressed_context.chunks),
    )
