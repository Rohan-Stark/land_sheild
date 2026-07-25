from __future__ import annotations

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
