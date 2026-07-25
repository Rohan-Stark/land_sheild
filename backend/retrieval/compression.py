from __future__ import annotations

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.schemas.retrieval import RetrievalContext
from backend.utils.tokenizer import count_tokens

logger = get_logger("retrieval.compression")


def compress_context(context: RetrievalContext) -> RetrievalContext:
    """Ensure the built context does not exceed the maximum token limit.

    Drops the lowest-ranked chunks until the context fits within
    MAX_CONTEXT_TOKENS (4000). Keeps citations/sources intact.
    """
    settings = get_settings()
    max_tokens = settings.MAX_CONTEXT_TOKENS

    if context.total_tokens <= max_tokens:
        return context

    # Chunks are already assumed to be sorted by final_score descending from reranker
    compressed_chunks = []
    current_tokens = 0

    for chunk in context.chunks:
        chunk_tokens = count_tokens(chunk.text)
        if current_tokens + chunk_tokens > max_tokens:
            break
        compressed_chunks.append(chunk)
        current_tokens += chunk_tokens

    dropped = len(context.chunks) - len(compressed_chunks)
    logger.info(
        "Compressed context from %d to %d tokens (dropped %d chunks)",
        context.total_tokens, current_tokens, dropped
    )

    context.chunks = compressed_chunks
    context.total_tokens = current_tokens
    
    # We do NOT remove from context.sources or context.metadata_summary
    # because even dropped chunks might contain relevant metadata/citations 
    # that we want to pass to the LLM later as background facts.
    
    return context
