from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config.logging import get_logger

logger = get_logger("security.middleware")


class SecurityMiddleware(BaseHTTPMiddleware):
    """Global ASGI middleware enforcing security boundaries and request tracing."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        
        # 1. Generate Request ID for distributed tracing
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.perf_counter()
        
        # 2. Forward to the application
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            # Catch unhandled errors before they bubble out
            logger.exception("Unhandled error processing request %s", request_id)
            raise exc

        # 3. Add trace headers
        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Note: Security headers are injected via a separate middleware/utility (headers.py)
        # to adhere to the single-responsibility principle.
        
        # 4. Access log (simplified audit)
        if request.url.path != "/health":  # Don't spam logs with health checks
            logger.info(
                "Request %s: %s %s completed in %.2fms with status %d",
                request_id,
                request.method,
                request.url.path,
                process_time * 1000,
                response.status_code
            )

        return response
