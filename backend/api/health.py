from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.database.chroma import chroma_health_check
from backend.database.postgres import get_db

logger = get_logger("api.health")
router = APIRouter(prefix="/api/health", tags=["System"])


class HealthResponse(BaseModel):
    status: str
    uptime_ms: float
    postgres: str
    chroma: dict[str, object]


_START_TIME = time.perf_counter()


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """System health check endpoint verifying DB connections."""
    uptime = (time.perf_counter() - _START_TIME) * 1000

    # Check Postgres
    try:
        await db.execute(text("SELECT 1"))
        pg_status = "healthy"
    except Exception as exc:
        logger.error("PostgreSQL health check failed: %s", exc)
        pg_status = f"unhealthy ({exc})"

    # Check Chroma
    chroma_status = chroma_health_check()

    overall_status = "healthy" if pg_status == "healthy" and chroma_status.get("status") == "healthy" else "degraded"

    return HealthResponse(
        status=overall_status,
        uptime_ms=uptime,
        postgres=pg_status,
        chroma=chroma_status,
    )
