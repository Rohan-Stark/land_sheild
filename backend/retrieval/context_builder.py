from __future__ import annotations

from typing import Any

from backend.config.logging import get_logger
from backend.schemas.retrieval import RetrievalContext, ScoredChunk
from backend.utils.tokenizer import count_tokens

logger = get_logger("retrieval.context_builder")


def build_context(chunks: list[ScoredChunk]) -> RetrievalContext:
    """Merge OCR, Chunks, and Metadata while removing duplicates.

    Prepares the context object for the compression phase.
    No prompt generation occurs here per Phase 1 scope.
    """
    unique_chunks: dict[str, ScoredChunk] = {}
    sources: set[str] = set()
    metadata_summary: dict[str, Any] = {}

    for chunk in chunks:
        # Deduplicate based on exact text content
        # In a real system, you might fuzzy match or use embedding distances for deduplication
        # but exact string match is safest for extracted chunks.
        text_hash = hash(chunk.text)
        if text_hash not in unique_chunks:
            unique_chunks[text_hash] = chunk
            
            # Track sources
            doc_id = chunk.document_id
            if doc_id:
                sources.add(doc_id)
                
            # Aggregate metadata safely
            for k, v in chunk.metadata.items():
                if v and k not in ("chunk_index", "document_id", "user_id"):
                    if k not in metadata_summary:
                        metadata_summary[k] = set()
                    metadata_summary[k].add(str(v))

    final_chunks = list(unique_chunks.values())
    
    # Clean up metadata summary
    clean_summary = {k: list(v) for k, v in metadata_summary.items()}
    
    # Calculate initial token count
    total_tokens = sum(count_tokens(c.text) for c in final_chunks)
    
    logger.info(
        "Context built: %d unique chunks, %d total tokens",
        len(final_chunks), total_tokens
    )

    return RetrievalContext(
        chunks=final_chunks,
        total_tokens=total_tokens,
        metadata_summary=clean_summary,
        sources=list(sources),
    )
