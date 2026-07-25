from __future__ import annotations

import time
from typing import Any

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.database.chroma import get_collection
from backend.ingestion.embeddings import generate_query_embedding
from backend.schemas.retrieval import RetrievalRequest, ScoredChunk

logger = get_logger("retrieval.semantic_search")


def execute_semantic_search(
    request: RetrievalRequest, filter_dict: dict[str, Any] | None
) -> list[ScoredChunk]:
    """Perform Semantic Search using ChromaDB and nomic embeddings."""
    start = time.perf_counter()
    settings = get_settings()

    query_emb = generate_query_embedding(request.query)

    collection = get_collection("documents")
    results = collection.query(
        query_embeddings=[query_emb],
        where=filter_dict,
        n_results=settings.SEMANTIC_TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    scored_chunks: list[ScoredChunk] = []

    if not results or not results["ids"] or not results["ids"][0]:
        return scored_chunks

    ids = results["ids"][0]
    documents = results["documents"][0] if results.get("documents") else []
    metadatas = results["metadatas"][0] if results.get("metadatas") else []
    distances = results["distances"][0] if results.get("distances") else []

    for i in range(len(ids)):
        # Convert ChromaDB cosine distance (0=identical) to a similarity score (0-1)
        # Assuming normalized embeddings where distance = 1 - cosine_similarity
        similarity = 1.0 - distances[i] if i < len(distances) else 0.0
        meta = metadatas[i] if i < len(metadatas) and metadatas[i] else {}
        text = documents[i] if i < len(documents) else ""

        scored_chunks.append(
            ScoredChunk(
                chunk_id=ids[i],
                document_id=str(meta.get("document_id", "")),
                chunk_index=int(meta.get("chunk_index", 0)),
                text=text,
                metadata=meta,
                semantic_score=max(0.0, similarity),
            )
        )

    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "Semantic search returned %d results in %.1fms", len(scored_chunks), elapsed
    )

    return scored_chunks
