from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.tools.exceptions import ToolBaseException, ToolNotRegisteredError, ExternalServiceError
from backend.tools.registry import tool_registry

logger = get_logger("tools.executor")


class ToolExecutorWrapper:
    """Safe wrapper for executing tools from the registry."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def execute_tool(
        self, tool_name: str, kwargs: dict[str, Any], timeout: float = 30.0, retries: int = 2
    ) -> BaseModel:
        """Execute a tool with built-in validation, timeout, and retries."""
        tool = tool_registry.get(tool_name)
        if not tool:
            raise ToolNotRegisteredError(f"Tool '{tool_name}' not found in registry.")

        for attempt in range(retries + 1):
            start = time.perf_counter()
            try:
                # 1. Validation (Input schema & Permissions)
                await tool.validate(self.db, **kwargs)

                # 2. Execution with timeout
                result = await asyncio.wait_for(
                    tool.execute(self.db, **kwargs),
                    timeout=timeout
                )

                elapsed = (time.perf_counter() - start) * 1000
                logger.info("Tool %s executed successfully in %.1fms", tool_name, elapsed)
                
                return result

            except asyncio.TimeoutError:
                logger.warning("Tool %s timed out on attempt %d", tool_name, attempt + 1)
                if attempt == retries:
                    raise ExternalServiceError(f"Tool '{tool_name}' timed out after {timeout}s.")
                await asyncio.sleep(1)
                
            except ToolBaseException:
                # Direct tool exceptions (like Permissions) should fail immediately, no retry.
                raise
                
            except Exception as exc:
                logger.error("Tool %s failed: %s", tool_name, exc)
                if attempt == retries:
                    raise ExternalServiceError(f"Tool execution failed: {str(exc)}")
                await asyncio.sleep(1)

        raise ExternalServiceError("Tool execution failed unexpectedly.")
