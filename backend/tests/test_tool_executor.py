from __future__ import annotations

import asyncio
import pytest
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory
from backend.tools.base_tool import BaseTool
from backend.tools.exceptions import ExternalServiceError, ToolNotRegisteredError, ToolValidationError
from backend.tools.executor import ToolExecutorWrapper
from backend.tools.registry import tool_registry


class MockInputSchema(BaseModel):
    user_id: str


class MockOutputSchema(BaseModel):
    success: bool


class MockTool(BaseTool):
    @property
    def name(self) -> str: return "MockTool"
    @property
    def description(self) -> str: return "Mock"
    @property
    def version(self) -> str: return "1.0"
    @property
    def supported_intents(self) -> list[IntentCategory]: return []
    @property
    def input_schema(self) -> type[BaseModel]: return MockInputSchema
    @property
    def output_schema(self) -> type[BaseModel]: return MockOutputSchema

    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        if not kwargs.get("user_id"):
            raise ToolValidationError("Missing user_id")

    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        if kwargs.get("trigger_timeout"):
            await asyncio.sleep(2)
        return MockOutputSchema(success=True)


@pytest.fixture(autouse=True)
def setup_registry():
    tool_registry.register(MockTool())
    yield
    tool_registry.unregister("MockTool")


@pytest.mark.asyncio
async def test_tool_executor_success():
    # We mock AsyncSession as None for simple logic testing
    executor = ToolExecutorWrapper(db=None)  # type: ignore
    result = await executor.execute_tool("MockTool", {"user_id": "usr_1"})
    
    assert isinstance(result, MockOutputSchema)
    assert result.success is True


@pytest.mark.asyncio
async def test_tool_executor_not_registered():
    executor = ToolExecutorWrapper(db=None)  # type: ignore
    with pytest.raises(ToolNotRegisteredError):
        await executor.execute_tool("UnknownTool", {})


@pytest.mark.asyncio
async def test_tool_executor_timeout_retry():
    executor = ToolExecutorWrapper(db=None)  # type: ignore
    
    # We set a tiny timeout to artificially force a TimeoutError
    with pytest.raises(ExternalServiceError, match="timed out"):
        await executor.execute_tool("MockTool", {"user_id": "usr_1", "trigger_timeout": True}, timeout=0.1, retries=0)
