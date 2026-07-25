from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.config.settings import get_settings
from backend.database.postgres import get_db
from backend.ingestion.indexer import ingest_document
from backend.utils.file_utils import ensure_dir, generate_safe_filename, validate_extension

logger = get_logger("api.upload")
router = APIRouter(prefix="/api/upload", tags=["Ingestion"])


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    property_id: str | None = Form(None),
    document_type: str = Form("other"),
    title: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Upload a document and trigger the full ingestion pipeline."""
    if not file.filename or not validate_extension(file.filename):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Supported: PDF, PNG, JPG, TIFF, BMP"
        )

    try:
        uuid.UUID(user_id)
        if property_id:
            uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id or property_id format")

    settings = get_settings()
    upload_dir = ensure_dir(Path(settings.UPLOAD_DIR) / user_id)
    safe_name = generate_safe_filename(file.filename)
    file_path = upload_dir / safe_name

    try:
        # Save file to disk
        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):
                f.write(chunk)

        # Ensure file isn't too large
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            file_path.unlink()
            raise HTTPException(
                status_code=413, detail=f"File too large. Maximum {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Trigger ingestion
        result = await ingest_document(
            file_path=file_path,
            user_id=user_id,
            db=db,
            property_id=property_id,
            document_type=document_type,
            title=title or file.filename,
        )

        return {
            "status": "success",
            "document_id": result.document_id,
            "metrics": {
                "chunk_count": result.chunk_count,
                "page_count": result.page_count,
                "ocr_applied": result.ocr_applied,
                "parse_time_ms": round(result.parse_time_ms, 1),
                "embed_time_ms": round(result.embed_time_ms, 1),
                "total_time_ms": round(result.total_time_ms, 1),
            },
            "extracted_metadata": result.metadata,
        }

    except ValueError as ve:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.error("Upload pipeline failed: %s", exc)
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail="Internal server error during ingestion")
