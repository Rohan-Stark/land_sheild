from __future__ import annotations

import time

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.database.postgres import DocumentChunk
from backend.schemas.retrieval import RetrievalRequest, ScoredChunk

logger = get_logger("retrieval.keyword_search")


async def execute_keyword_search(
    request: RetrievalRequest, db: AsyncSession
) -> list[ScoredChunk]:
    """Perform PostgreSQL Full-Text Search on DocumentChunks.

    Handles specific keyword matching for identifiers like Survey Numbers,
    Registration IDs, and Khata Numbers that semantic search might miss.
    """
    start = time.perf_counter()
    results: list[ScoredChunk] = []

    # Clean query for tsquery (convert spaces to logical ANDs for basic search)
    # Note: A real production system would parse the query more robustly.
    clean_query = " & ".join(
        word for word in request.query.replace("'", "").split() if word.isalnum()
    )
    if not clean_query:
        return results

    # Base query combining filter constraints and full-text search
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.user_id == request.user_id)
        .where(
            text(f"to_tsvector('english', chunk_text) @@ to_tsquery('english', :query)")
        )
    )

    if request.property_id:
        stmt = stmt.where(DocumentChunk.property_id == request.property_id)

    # We fetch a slightly larger pool to ensure we have enough after re-ranking
    stmt = stmt.limit(20)

    try:
        cursor = await db.execute(stmt, {"query": clean_query})
        db_chunks = cursor.scalars().all()

        for chunk in db_chunks:
            # We assign a baseline keyword score of 1.0; the reranker will weigh this
            results.append(
                ScoredChunk(
                    chunk_id=chunk.embedding_id,
                    document_id=str(chunk.document_id),
                    chunk_index=chunk.chunk_index,
                    text=chunk.chunk_text,
                    metadata=chunk.metadata or {},
                    keyword_score=1.0,
                )
            )

        elapsed = (time.perf_counter() - start) * 1000
        logger.info("Keyword search returned %d results in %.1fms", len(results), elapsed)
    except Exception as exc:
        logger.error("Keyword search failed: %s", exc)

    return results
