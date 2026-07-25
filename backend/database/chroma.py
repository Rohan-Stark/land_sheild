from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import chromadb
from chromadb.api import ClientAPI

from backend.config.logging import get_logger
from backend.config.settings import get_settings

logger = get_logger("database.chroma")

COLLECTION_NAMES = ("documents", "knowledge", "alerts", "reports")


@lru_cache(maxsize=1)
def get_chroma_client() -> ClientAPI:
    """Return a persistent ChromaDB client (singleton)."""
    settings = get_settings()
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(persist_dir))
    logger.info("ChromaDB client initialised at %s", persist_dir)
    return client


def get_collection(name: str) -> chromadb.Collection:
    """Get or create a named ChromaDB collection."""
    if name not in COLLECTION_NAMES:
        raise ValueError(f"Unknown collection '{name}'. Must be one of {COLLECTION_NAMES}")
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
    logger.debug("ChromaDB collection '%s' ready (count=%d)", name, collection.count())
    return collection


def chroma_health_check() -> dict[str, object]:
    """Return ChromaDB health status and collection counts."""
    try:
        client = get_chroma_client()
        counts = {}
        for name in COLLECTION_NAMES:
            col = client.get_or_create_collection(name=name)
            counts[name] = col.count()
        return {"status": "healthy", "collections": counts}
    except Exception as exc:
        logger.error("ChromaDB health check failed: %s", exc)
        return {"status": "unhealthy", "error": str(exc)}
