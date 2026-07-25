from __future__ import annotations

import time
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from backend.config.logging import get_logger
from backend.config.settings import get_settings

logger = get_logger("ingestion.embeddings")


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load the embedding model (singleton, cached)."""
    settings = get_settings()
    logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
    start = time.perf_counter()
    model = SentenceTransformer(
        settings.EMBEDDING_MODEL,
        trust_remote_code=True,
    )
    elapsed = (time.perf_counter() - start) * 1000
    logger.info("Embedding model loaded in %.1fms", elapsed)
    return model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts using nomic-embed-text.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    if not texts:
        return []

    model = _get_model()
    start = time.perf_counter()

    # nomic-embed-text requires 'search_document: ' prefix for indexing
    prefixed = [f"search_document: {t}" for t in texts]
    embeddings = model.encode(prefixed, show_progress_bar=False, normalize_embeddings=True)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info(
        "Generated %d embeddings in %.1fms (%.1fms/embedding)",
        len(texts), elapsed, elapsed / max(len(texts), 1),
    )

    return [emb.tolist() for emb in embeddings]


def generate_query_embedding(query: str) -> list[float]:
    """Generate a single embedding for a search query.

    Uses the 'search_query: ' prefix required by nomic-embed-text.
    """
    model = _get_model()
    prefixed = f"search_query: {query}"
    embedding = model.encode(prefixed, show_progress_bar=False, normalize_embeddings=True)
    return embedding.tolist()
