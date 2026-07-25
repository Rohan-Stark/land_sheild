from __future__ import annotations

import time

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.utils.tokenizer import tokens_to_chars

logger = get_logger("ingestion.chunker")


def _build_splitter() -> RecursiveCharacterTextSplitter:
    """Create a text splitter configured from application settings."""
    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=tokens_to_chars(settings.CHUNK_SIZE_TOKENS),
        chunk_overlap=tokens_to_chars(settings.CHUNK_OVERLAP_TOKENS),
        separators=[
            "\n\n\n",   # triple newline (section break)
            "\n\n",      # paragraph break
            "\n",         # line break
            ". ",         # sentence boundary
            ", ",         # clause boundary
            " ",          # word boundary
        ],
        keep_separator=True,
        strip_whitespace=True,
        length_function=len,
    )


def chunk_text(text: str) -> list[str]:
    """Split document text into semantically meaningful chunks.

    Uses RecursiveCharacterTextSplitter with configured chunk size (600 tokens)
    and overlap (120 tokens). Preserves headings and table structures.

    Returns:
        List of text chunks.
    """
    if not text.strip():
        return []

    start = time.perf_counter()
    splitter = _build_splitter()
    chunks = splitter.split_text(text)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info("Chunking: %d chunks in %.1fms", len(chunks), elapsed)
    return chunks
