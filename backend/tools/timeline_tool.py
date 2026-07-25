from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import TimelineResult
from backend.tools.base_tool import BaseTool
from backend.tools.validation import PermissionValidator


class TimelineToolInput(BaseModel):
    user_id: str
    property_id: str


class TimelineTool(BaseTool):
    """Tool for retrieving unified timelines for a property."""

    @property
    def name(self) -> str:
        return "TimelineTool"

    @property
    def description(self) -> str:
        return "Retrieve historical events, alert triggers, and inspection logs."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.PROPERTY_QUESTION, IntentCategory.REPORT_REQUEST]

    @property
    def input_schema(self) -> type[BaseModel]:
        return TimelineToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return TimelineResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        prop_id = kwargs.get("property_id")
        await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        prop_id = kwargs.get("property_id")
        
        # Simulated timeline retrieval
        events = [
            {"date": "2024-01-01", "type": "registration", "description": "Property registered."},
            {"date": "2024-06-15", "type": "alert", "description": "Unpaid tax alert triggered."}
        ]
        
        return TimelineResult(
            property_id=str(prop_id),
            events=events
        )
