from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import Document
from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import DocumentResult
from backend.tools.base_tool import BaseTool
from backend.tools.validation import PermissionValidator


class DocumentToolInput(BaseModel):
    user_id: str
    document_id: str | None = None
    property_id: str | None = None
    query: str | None = None


class DocumentTool(BaseTool):
    """Tool for retrieving and interacting with property documents securely."""

    @property
    def name(self) -> str:
        return "DocumentTool"

    @property
    def description(self) -> str:
        return "Fetch and search user-owned document metadata and contents."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.DOCUMENT_QUESTION]

    @property
    def input_schema(self) -> type[BaseModel]:
        return DocumentToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return DocumentResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        doc_id = kwargs.get("document_id")
        prop_id = kwargs.get("property_id")
        
        if doc_id:
            await PermissionValidator.verify_document_ownership(db, user_id, doc_id)
        elif prop_id:
            await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        user_id = kwargs.get("user_id")
        doc_id = kwargs.get("document_id")
        prop_id = kwargs.get("property_id")

        stmt = select(Document).where(Document.user_id == uuid.UUID(user_id))
        if doc_id:
            stmt = stmt.where(Document.id == uuid.UUID(doc_id))
        if prop_id:
            stmt = stmt.where(Document.property_id == uuid.UUID(prop_id))
            
        result = await db.execute(stmt)
        docs = result.scalars().all()
        
        doc_list = []
        for d in docs:
            doc_list.append({
                "id": str(d.id),
                "title": d.title,
                "document_type": d.document_type,
                "metadata": d.extracted_metadata
            })
            
        # In Phase 2B.3 we don't directly hit ChromaDB here to avoid circular imports.
        # RetrievalService is used in the Agent level, but this tool handles Postgres DB lookups.

        return DocumentResult(
            documents=doc_list,
            chunks=[],
            metadata_summary={"total_found": len(doc_list)}
        )
