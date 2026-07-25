from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import Property
from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import PropertyResult
from backend.tools.base_tool import BaseTool
from backend.tools.exceptions import ResourceNotFoundError
from backend.tools.validation import PermissionValidator


class PropertyToolInput(BaseModel):
    user_id: str
    property_id: str


class PropertyTool(BaseTool):
    """Tool for fetching property details and status securely."""

    @property
    def name(self) -> str:
        return "PropertyTool"

    @property
    def description(self) -> str:
        return "Fetch property tax, mutation status, and metadata."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.PROPERTY_QUESTION]

    @property
    def input_schema(self) -> type[BaseModel]:
        return PropertyToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return PropertyResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        prop_id = kwargs.get("property_id")
        await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        prop_id = kwargs.get("property_id")
        stmt = select(Property).where(Property.id == uuid.UUID(prop_id))
        result = await db.execute(stmt)
        prop = result.scalar_one_or_none()

        if not prop:
            raise ResourceNotFoundError(f"Property {prop_id} not found.")

        # Simulate fetching tax/mutation status from an external state / metadata
        meta = prop.metadata_ if prop.metadata_ else {}
        
        return PropertyResult(
            property_id=str(prop.id),
            metadata=meta,
            owner_id=str(prop.user_id),
            tax_status=meta.get("tax_status", "Unknown"),
            mutation_status=meta.get("mutation_status", "Pending")
        )
