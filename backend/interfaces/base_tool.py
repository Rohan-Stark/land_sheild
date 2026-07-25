from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """Base schema for tool input."""

    query: str
    context: dict[str, Any] = Field(default_factory=dict)


class ToolOutput(BaseModel):
    """Base schema for tool output."""

    result: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: str | None = None


class BaseTool(ABC):
    """Abstract base class for all LandShield AI tools.

    Tools are specific capabilities that agents use to interact with
    databases, APIs, or processing pipelines.
    """

    name: str
    description: str

    @abstractmethod
    async def execute(self, tool_input: ToolInput) -> ToolOutput:
        """Execute the tool with the given input."""
        ...

    def __repr__(self) -> str:
        return f"<Tool: {self.name}>"
