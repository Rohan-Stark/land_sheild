from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ───────────────────────────────────────────────────────────────────


class DocumentType(str, Enum):
    DEED = "deed"
    SURVEY = "survey"
    LEGAL = "legal"
    TAX = "tax"
    INSURANCE = "insurance"
    INSPECTION = "inspection"
    OTHER = "other"


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ── Request Schemas ─────────────────────────────────────────────────────────


class DocumentUploadRequest(BaseModel):
    user_id: uuid.UUID
    property_id: uuid.UUID | None = None
    document_type: DocumentType = DocumentType.OTHER
    title: str | None = None


# ── Response Schemas ────────────────────────────────────────────────────────


class DocumentMetadataResponse(BaseModel):
    survey_number: str | None = None
    registration_number: str | None = None
    khata_number: str | None = None
    property_address: str | None = None
    dates: list[str] = Field(default_factory=list)
    owner_names: list[str] = Field(default_factory=list)
    district: str | None = None
    state: str | None = None


class ChunkResponse(BaseModel):
    chunk_id: str
    chunk_index: int
    chunk_text: str
    embedding_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    property_id: uuid.UUID | None
    title: str
    document_type: DocumentType
    file_hash: str
    file_size: int
    page_count: int | None
    ocr_applied: bool
    extracted_metadata: DocumentMetadataResponse | None
    status: DocumentStatus
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
