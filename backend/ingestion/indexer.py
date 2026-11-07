from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.database.chroma import get_collection
from backend.database.postgres import Document, DocumentChunk
from backend.ingestion.chunker import chunk_text
from backend.ingestion.embeddings import generate_embeddings
from backend.ingestion.metadata import extract_metadata
from backend.ingestion.parser import parse_document
from backend.utils.hashing import sha256_file

logger = get_logger("ingestion.indexer")


class IngestionResult:
    """Result of ingesting a single document."""

    def __init__(
        self,
        document_id: str,
        chunk_count: int,
        page_count: int,
        ocr_applied: bool,
        metadata: dict[str, Any],
        parse_time_ms: float,
        embed_time_ms: float,
        total_time_ms: float,
    ) -> None:
        self.document_id = document_id
        self.chunk_count = chunk_count
        self.page_count = page_count
        self.ocr_applied = ocr_applied
        self.metadata = metadata
        self.parse_time_ms = parse_time_ms
        self.embed_time_ms = embed_time_ms
        self.total_time_ms = total_time_ms


async def ingest_document(
    file_path: Path,
    user_id: str,
    db: AsyncSession,
    property_id: str | None = None,
    document_type: str = "other",
    title: str | None = None,
) -> IngestionResult:
    """Full ingestion pipeline: parse → extract metadata → chunk → embed → store.

    Args:
        file_path: Path to the uploaded file.
        user_id: UUID of the uploading user.
        db: Async database session.
        property_id: Optional UUID of the associated property.
        document_type: Type classification for the document.
        title: Optional title (defaults to filename).

    Returns:
        IngestionResult with processing metrics.

    Raises:
        ValueError: If the file is invalid, duplicate, or unsupported.
    """
    total_start = time.perf_counter()

    # ── 1. File hash for deduplication ──────────────────────────
    file_hash = sha256_file(file_path)
    existing = await db.execute(
        Document.__table__.select().where(Document.file_hash == file_hash)
    )
    if existing.first():
        raise ValueError(f"Duplicate document detected (hash: {file_hash[:12]}...)")

    # ── 2. Parse document ───────────────────────────────────────
    parse_result = parse_document(file_path)

    if not parse_result.text.strip():
        raise ValueError("Document produced no extractable text")

    # ── 3. Extract metadata ─────────────────────────────────────
    extracted_meta = extract_metadata(parse_result.text)

    # ── 4. Create DB document record ────────────────────────────
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        user_id=uuid.UUID(user_id),
        property_id=uuid.UUID(property_id) if property_id else None,
        title=title or file_path.stem,
        document_type=document_type,
        file_path=str(file_path),
        file_hash=file_hash,
        file_size=file_path.stat().st_size,
        page_count=parse_result.page_count,
        ocr_applied=parse_result.ocr_applied,
        metadata_extracted=extracted_meta,
        status="processing",
    )
    db.add(doc)
    await db.flush()

    # ── 5. Chunk text ───────────────────────────────────────────
    chunks = chunk_text(parse_result.text)

    if not chunks:
        doc.status = "failed"
        doc.error_message = "Chunking produced no results"
        await db.flush()
        raise ValueError("Chunking produced no results")

    # ── 6. Generate embeddings ──────────────────────────────────
    embed_start = time.perf_counter()
    embeddings = generate_embeddings(chunks)
    embed_time = (time.perf_counter() - embed_start) * 1000

    # ── 7. Store in ChromaDB ────────────────────────────────────
    collection = get_collection("documents")
    embedding_ids: list[str] = []

    for i, (chunk_text_str, embedding) in enumerate(zip(chunks, embeddings)):
        emb_id = f"{doc_id}_chunk_{i}"
        embedding_ids.append(emb_id)

        chunk_metadata: dict[str, Any] = {
            "user_id": user_id,
            "document_id": str(doc_id),
            "document_type": document_type,
            "chunk_index": i,
        }
        if property_id:
            chunk_metadata["property_id"] = property_id
        # Merge extracted metadata (flatten for ChromaDB)
        for key in ("survey_number", "registration_number", "khata_number", "district", "state"):
            if key in extracted_meta:
                chunk_metadata[key] = extracted_meta[key]

        collection.add(
            ids=[emb_id],
            embeddings=[embedding],
            documents=[chunk_text_str],
            metadatas=[chunk_metadata],
        )

    # ── 8. Store chunks in PostgreSQL ───────────────────────────
    for i, chunk_text_str in enumerate(chunks):
        db_chunk = DocumentChunk(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            property_id=uuid.UUID(property_id) if property_id else None,
            document_id=doc_id,
            document_type=document_type,
            chunk_index=i,
            chunk_text=chunk_text_str,
            embedding_id=embedding_ids[i],
            chunk_metadata=extracted_meta,
        )
        db.add(db_chunk)

    # ── 9. Finalise document status ─────────────────────────────
    doc.status = "completed"
    await db.flush()

    total_time = (time.perf_counter() - total_start) * 1000

    logger.info(
        "Ingestion complete: doc=%s, chunks=%d, pages=%d, ocr=%s, "
        "parse=%.1fms, embed=%.1fms, total=%.1fms",
        doc_id, len(chunks), parse_result.page_count,
        parse_result.ocr_applied, parse_result.parse_time_ms,
        embed_time, total_time,
    )

    return IngestionResult(
        document_id=str(doc_id),
        chunk_count=len(chunks),
        page_count=parse_result.page_count,
        ocr_applied=parse_result.ocr_applied,
        metadata=extracted_meta,
        parse_time_ms=parse_result.parse_time_ms,
        embed_time_ms=embed_time,
        total_time_ms=total_time,
    )
