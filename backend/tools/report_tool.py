from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import ReportResult
from backend.tools.base_tool import BaseTool
from backend.tools.validation import PermissionValidator


class ReportToolInput(BaseModel):
    user_id: str
    property_id: str


class ReportTool(BaseTool):
    """Tool for gathering cross-domain structured data to build reports."""

    @property
    def name(self) -> str:
        return "ReportTool"

    @property
    def description(self) -> str:
        return "Generate structured multi-domain reports for a property."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.REPORT_REQUEST]

    @property
    def input_schema(self) -> type[BaseModel]:
        return ReportToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return ReportResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        prop_id = kwargs.get("property_id")
        await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        # Simulated multi-domain aggregation.
        # It relies on fetching other tables or engines but does not build PDFs itself.
        return ReportResult(
            property_summary={"status": "Active", "flags": 1},
            evidence_bundle=[{"doc_id": "d1", "verified": True}],
            timeline_summary=[{"event": "Inspection complete"}]
        )
