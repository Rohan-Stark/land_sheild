from __future__ import annotations

import json
from typing import Any, AsyncIterator

from backend.config.logging import get_logger
from backend.llm.schemas.response import StreamChunk

logger = get_logger("llm.streaming")


async def sse_event_generator(
    chunks: AsyncIterator[StreamChunk],
    heartbeat_interval: float = 15.0,
) -> AsyncIterator[str]:
    """Convert an async stream of StreamChunks into SSE-formatted strings.

    Yields:
        SSE lines in the format ``data: {...}\\n\\n``.
        Sends a heartbeat comment (``:``) if no data is received within the interval.
        Emits a final ``data: [DONE]\\n\\n`` on completion.
    """
    import asyncio

    try:
        async for chunk in chunks:
            payload: dict[str, Any] = {
                "content": chunk.content,
                "done": chunk.done,
                "model": chunk.model,
            }
            yield f"data: {json.dumps(payload)}\n\n"

            if chunk.done:
                yield "data: [DONE]\n\n"
                return

        # If the stream ends without an explicit done flag
        yield "data: [DONE]\n\n"

    except asyncio.CancelledError:
        logger.info("SSE stream cancelled by client.")
        yield "data: [DONE]\n\n"

    except Exception as exc:
        logger.error("SSE stream error: %s", exc)
        error_payload = json.dumps({"error": str(exc), "done": True})
        yield f"data: {error_payload}\n\n"
