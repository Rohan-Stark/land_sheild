from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import AlertResult
from backend.tools.base_tool import BaseTool
from backend.tools.validation import PermissionValidator


class AlertToolInput(BaseModel):
    user_id: str
    property_id: str


class AlertTool(BaseTool):
    """Tool for retrieving property alerts."""

    @property
    def name(self) -> str:
        return "AlertTool"

    @property
    def description(self) -> str:
        return "Retrieve active alerts and history for a property."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.ALERT_QUESTION]

    @property
    def input_schema(self) -> type[BaseModel]:
        return AlertToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return AlertResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        prop_id = kwargs.get("property_id")
        await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        # Simulated alert retrieval (as alerts aren't a Postgres model yet, they exist in Chroma)
        # We will mock a response to fulfill the typed schema securely.
        alerts = [
            {"id": "a1", "type": "tax_due", "severity": 3, "message": "Property tax is due."}
        ]
        
        return AlertResult(
            alerts=alerts,
            severity_summary={"high": 0, "medium": 1, "low": 0}
        )
