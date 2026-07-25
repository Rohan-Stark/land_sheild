from __future__ import annotations

import logging
from typing import Any

from backend.config.logging import get_logger


class AgentLogger:
    """Context-aware logger specifically for agent executions."""

    def __init__(self, agent_name: str, request_id: str) -> None:
        self.agent_name = agent_name
        self.request_id = request_id
        self._logger = get_logger(f"agent.{agent_name}")

    def _format(self, msg: str, **kwargs: Any) -> str:
        base = f"[{self.request_id}] {msg}"
        if kwargs:
            base += " | " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        return base

    def info(self, msg: str, **kwargs: Any) -> None:
        self._logger.info(self._format(msg, **kwargs))

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._logger.debug(self._format(msg, **kwargs))

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._logger.warning(self._format(msg, **kwargs))

    def error(self, msg: str, **kwargs: Any) -> None:
        self._logger.error(self._format(msg, **kwargs))
