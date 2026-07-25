from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import Document, Property
from backend.tools.exceptions import ResourceNotFoundError, ToolPermissionError


class PermissionValidator:
    """Core validation for ensuring users own the resources they access."""

    @staticmethod
    async def verify_property_ownership(
        db: AsyncSession, user_id: str, property_id: str
    ) -> None:
        """Verify the user owns the specified property."""
        try:
            pid = uuid.UUID(property_id)
            uid = uuid.UUID(user_id)
        except ValueError:
            raise ToolPermissionError("Invalid UUID format for user_id or property_id.")

        stmt = select(Property.id).where(Property.id == pid, Property.user_id == uid)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            # Standardizing to PermissionError so we don't leak existence of properties they don't own.
            raise ToolPermissionError("Access denied or Property not found.")

    @staticmethod
    async def verify_document_ownership(
        db: AsyncSession, user_id: str, document_id: str
    ) -> None:
        """Verify the user owns the specified document."""
        try:
            did = uuid.UUID(document_id)
            uid = uuid.UUID(user_id)
        except ValueError:
            raise ToolPermissionError("Invalid UUID format for user_id or document_id.")

        stmt = select(Document.id).where(Document.id == did, Document.user_id == uid)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise ToolPermissionError("Access denied or Document not found.")
