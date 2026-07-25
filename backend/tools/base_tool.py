from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.graph import IntentCategory


class BaseTool(ABC):
    """Abstract base class for all LandShield AI Tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for registry lookup."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of the tool's capabilities."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Tool version for tracing."""
        ...

    @property
    @abstractmethod
    def supported_intents(self) -> list[IntentCategory]:
        """Intents this tool is suited for."""
        ...

    @property
    @abstractmethod
    def input_schema(self) -> type[BaseModel]:
        """The Pydantic schema required for input."""
        ...

    @property
    @abstractmethod
    def output_schema(self) -> type[BaseModel]:
        """The strictly typed Pydantic schema for output."""
        ...

    @abstractmethod
    async def validate(self, db: AsyncSession, **kwargs: Any) -> None:
        """Enforce permissions and parameter correctness before execution."""
        ...

    @abstractmethod
    async def execute(self, db: AsyncSession, **kwargs: Any) -> BaseModel:
        """Core business logic that queries services and returns output_schema."""
        ...
