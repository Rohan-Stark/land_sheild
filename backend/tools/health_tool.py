from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.schemas.tool_result import HealthResult
from backend.tools.base_tool import BaseTool
from backend.tools.validation import PermissionValidator


class HealthToolInput(BaseModel):
    user_id: str
    property_id: str


class HealthTool(BaseTool):
    """Tool for retrieving pre-calculated health scores."""

    @property
    def name(self) -> str:
        return "HealthTool"

    @property
    def description(self) -> str:
        return "Retrieve the current health score of a property."

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.PROPERTY_QUESTION]

    @property
    def input_schema(self) -> type[BaseModel]:
        return HealthToolInput

    @property
    def output_schema(self) -> type[BaseModel]:
        return HealthResult

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        user_id = kwargs.get("user_id")
        prop_id = kwargs.get("property_id")
        await PermissionValidator.verify_property_ownership(db, user_id, prop_id)

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        prop_id = kwargs.get("property_id")
        
        # In a real system, this fetches the pre-calculated score from a Health engine table.
        # We will mock the response structure as requested.
        return HealthResult(
            property_id=str(prop_id),
            health_score=85,
            risk_indicators=["Unpaid Taxes"],
            health_factors={"legal_clearance": True, "mutation_done": False},
            recommendations=["Pay pending taxes to improve score."]
        )
