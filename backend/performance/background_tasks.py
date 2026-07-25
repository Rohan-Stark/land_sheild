from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Callable, Coroutine
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("performance.background_tasks")


class BackgroundTaskRecord:
    """Tracks a single background task execution."""

    def __init__(self, task_id: str, name: str) -> None:
        self.task_id = task_id
        self.name = name
        self.started_at = time.monotonic()
        self.completed_at: float | None = None
        self.error: str | None = None
        self.is_done = False


class BackgroundTaskManager:
    """Executes non-blocking background work without blocking HTTP request threads.

    Manages lifecycle of fire-and-forget async tasks for OCR, embeddings,
    cache refresh, memory summarization, and report generation.
    """

    def __init__(self, max_concurrent: int = 20) -> None:
        self._max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active: dict[str, BackgroundTaskRecord] = {}
        self._history: list[BackgroundTaskRecord] = []

    def submit(
        self,
        name: str,
        coro: Coroutine[Any, Any, Any],
    ) -> str:
        """Submit a coroutine for background execution. Returns the task ID."""
        task_id = str(uuid.uuid4())
        record = BackgroundTaskRecord(task_id=task_id, name=name)
        self._active[task_id] = record

        asyncio.ensure_future(self._run(task_id, record, coro))
        logger.info("Submitted background task %s (id=%s)", name, task_id)
        return task_id

    async def _run(
        self,
        task_id: str,
        record: BackgroundTaskRecord,
        coro: Coroutine[Any, Any, Any],
    ) -> None:
        await self._semaphore.acquire()
        try:
            await coro
            record.completed_at = time.monotonic()
            logger.info(
                "Background task %s completed in %.2fs",
                record.name,
                record.completed_at - record.started_at,
            )
        except Exception as exc:
            record.error = str(exc)
            logger.exception("Background task %s failed: %s", record.name, exc)
        finally:
            record.is_done = True
            self._semaphore.release()
            self._active.pop(task_id, None)
            self._history.append(record)

    @property
    def running_count(self) -> int:
        return len(self._active)

    def get_active_tasks(self) -> list[BackgroundTaskRecord]:
        return list(self._active.values())

    def get_recent_history(self, limit: int = 50) -> list[BackgroundTaskRecord]:
        return self._history[-limit:]


# Singleton
background_manager = BackgroundTaskManager()
