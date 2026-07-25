from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.database.postgres import get_db
from backend.retrieval.retriever import hybrid_retrieve
from backend.schemas.retrieval import RetrievalRequest, RetrievalResponse

logger = get_logger("api.retrieval")
router = APIRouter(prefix="/api/retrieval", tags=["Retrieval"])


@router.post("", response_model=RetrievalResponse)
async def perform_retrieval(
    request: RetrievalRequest, db: AsyncSession = Depends(get_db)
) -> RetrievalResponse:
    """Execute hybrid retrieval for a given query and metadata filter."""
    try:
        response = await hybrid_retrieve(request, db)
        return response
    except Exception as exc:
        logger.error("Retrieval failed: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error during retrieval")
