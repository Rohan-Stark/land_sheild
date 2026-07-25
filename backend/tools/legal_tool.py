from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import LegalResult
from backend.tools.base_tool import BaseTool


class LegalToolInput(BaseModel):
    user_id: str
    query: str


class LegalTool(BaseTool):
    """Tool for fetching public legal procedures and FAQs from knowledge bases."""

    @property
    def name(self) -> str:
        return "LegalTool"

    @property
    def description(self) -> str:
        return "Fetch public property laws and procedural rules."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.LEGAL_GUIDANCE]

    @property
    def input_schema(self) -> type[BaseModel]:
        return LegalToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return LegalResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        # Legal knowledge is public domain in the system, no property validation needed
        pass

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        # Simulated knowledge extraction from the legal/knowledge base table.
        return LegalResult(
            procedures=[{"name": "Mutation", "steps": ["Apply", "Pay Fee"]}],
            rules=[{"rule": "Registration must happen within 4 months."}]
        )
