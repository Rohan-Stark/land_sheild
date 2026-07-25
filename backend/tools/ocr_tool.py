from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import Document
from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import OCRResult
from backend.tools.base_tool import BaseTool
from backend.tools.exceptions import ResourceNotFoundError
from backend.tools.validation import PermissionValidator


class OCRToolInput(BaseModel):
    user_id: str
    document_id: str


class OCRTool(BaseTool):
    """Tool for retrieving OCR text and metadata for a document."""

    @property
    def name(self) -> str:
        return "OCRTool"

    @property
    def description(self) -> str:
        return "Fetch previously processed OCR results and metadata."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.DOCUMENT_QUESTION]

    @property
    def input_schema(self) -> type[BaseModel]:
        return OCRToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return OCRResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        doc_id = kwargs.get("document_id")
        await PermissionValidator.verify_document_ownership(db, user_id, doc_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        doc_id = kwargs.get("document_id")
        stmt = select(Document).where(Document.id == uuid.UUID(doc_id))
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()

        if not doc:
            raise ResourceNotFoundError(f"Document {doc_id} not found.")

        # Real implementation would fetch the full text from S3/Postgres chunk aggregator
        # We reuse Phase 1 metadata extraction here conceptually, but fetch from DB.
        
        return OCRResult(
            document_id=str(doc.id),
            extracted_text="[Simulated OCR Text from DB Storage]",
            metadata=doc.extracted_metadata if doc.extracted_metadata else {}
        )
