from __future__ import annotations

import asyncio
import time
import uuid
from enum import Enum
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("performance.queue")


class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 3
    NORMAL = 5
    LOW = 7
    BACKGROUND = 9


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class QueuedTask:
    """A single unit of work submitted to the queue."""

    def __init__(
        self,
        name: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.payload = payload
        self.priority = priority
        self.max_retries = max_retries
        self.attempt = 0
        self.status = TaskStatus.PENDING
        self.created_at = time.monotonic()
        self.result: Any = None
        self.error: str | None = None


class QueueManager:
    """Priority-based asynchronous task queue with Dead-Letter Queue (DLQ).

    Tasks are sorted by priority (lowest number = highest priority).
    Failed tasks exceeding max_retries are moved to the DLQ for manual inspection.
    """

    def __init__(self) -> None:
        self._queue: list[QueuedTask] = []
        self._dead_letter: list[QueuedTask] = []
        self._completed: list[QueuedTask] = []
        self._lock = asyncio.Lock()

    async def enqueue(self, task: QueuedTask) -> str:
        """Add a task to the priority queue. Returns the task ID."""
        async with self._lock:
            self._queue.append(task)
            self._queue.sort(key=lambda t: t.priority.value)
        logger.info("Enqueued task %s (priority=%s, id=%s)", task.name, task.priority.name, task.id)
        return task.id

    async def dequeue(self) -> QueuedTask | None:
        """Pop the highest-priority task from the queue."""
        async with self._lock:
            if not self._queue:
                return None
            task = self._queue.pop(0)
            task.status = TaskStatus.RUNNING
            task.attempt += 1
            return task

    async def complete(self, task: QueuedTask, result: Any = None) -> None:
        """Mark a task as successfully completed."""
        task.status = TaskStatus.COMPLETED
        task.result = result
        self._completed.append(task)

    async def fail(self, task: QueuedTask, error: str) -> None:
        """Handle a failed task. Re-enqueue or move to DLQ."""
        task.error = error

        if task.attempt < task.max_retries:
            task.status = TaskStatus.PENDING
            await self.enqueue(task)
            logger.warning("Re-enqueued task %s (attempt %d/%d)", task.id, task.attempt, task.max_retries)
        else:
            task.status = TaskStatus.DEAD_LETTER
            self._dead_letter.append(task)
            logger.error("Task %s moved to DLQ after %d failures: %s", task.id, task.attempt, error)

    @property
    def depth(self) -> int:
        return len(self._queue)

    @property
    def dead_letter_count(self) -> int:
        return len(self._dead_letter)

    def get_dead_letter_tasks(self) -> list[QueuedTask]:
        return list(self._dead_letter)


# Named queues for different workload types
queue_registry: dict[str, QueueManager] = {
    "ocr": QueueManager(),
    "embedding": QueueManager(),
    "ingestion": QueueManager(),
    "report": QueueManager(),
    "indexing": QueueManager(),
}
