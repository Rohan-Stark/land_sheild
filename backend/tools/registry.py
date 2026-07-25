from __future__ import annotations

from typing import Type

from backend.config.logging import get_logger
from backend.tools.base_tool import BaseTool

logger = get_logger("tools.registry")


class ToolRegistry:
    """Dynamic registry for all tools in the system."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            logger.warning("Overwriting existing tool registration: %s", tool.name)
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s v%s", tool.name, tool.version)

    def unregister(self, tool_name: str) -> None:
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info("Unregistered tool: %s", tool_name)

    def get(self, tool_name: str) -> BaseTool | None:
        return self._tools.get(tool_name)

    def exists(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def list(self) -> list[str]:
        return list(self._tools.keys())


# Singleton instance
tool_registry = ToolRegistry()
