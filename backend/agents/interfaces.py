from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from backend.schemas.tool import ToolInput, ToolOutput


class RetrievalService(ABC):
    """Interface ensuring agents never query ChromaDB/Postgres directly."""

    @abstractmethod
    async def retrieve(self, query: str, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Perform hybrid retrieval."""
        ...

    @abstractmethod
    async def retrieve_by_metadata(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        """Retrieve specifically by structured metadata without semantic search."""
        ...

    @abstractmethod
    async def retrieve_documents(self, property_id: str) -> list[dict[str, Any]]:
        """Retrieve all documents linked to a property."""
        ...

    @abstractmethod
    async def retrieve_property(self, property_id: str) -> dict[str, Any] | None:
        """Retrieve property details."""
        ...

    @abstractmethod
    async def retrieve_alerts(self, property_id: str) -> list[dict[str, Any]]:
        """Retrieve alerts for a property."""
        ...


class ToolExecutor(ABC):
    """Interface for invoking tools, insulating agents from execution details."""

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: ToolInput) -> ToolOutput:
        """Execute a tool by name, handling retries, logging, and error conversion."""
        ...
