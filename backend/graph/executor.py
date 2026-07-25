from __future__ import annotations

import time
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.graph.state import GraphState
from backend.retrieval.retriever import hybrid_retrieve
from backend.schemas.retrieval import RetrievalRequest

logger = get_logger("graph.executor")


async def execute_tools(state: GraphState, db: AsyncSession) -> dict[str, Any]:
    """Execute required tools based on the execution plan.

    For Phase 2A, the primary tool is the Hybrid Retrieval engine built in Phase 1.
    If the plan requires retrieval, this node directly invokes `hybrid_retrieve`.
    """
    plan = state.get("plan")
    if not plan or not plan.requires_retrieval:
        return {}

    start = time.perf_counter()
    logger.info("Executor invoking hybrid retrieval for intent: %s", plan.intent)

    entities = state.get("entities")
    req = RetrievalRequest(
        query=state["query"],
        user_id=uuid.UUID(state["userId"]),
        property_id=uuid.UUID(entities.propertyId) if entities and entities.propertyId else None,
        document_type=entities.documentType if entities else None,
        survey_number=entities.surveyNumber if entities else None,
        registration_number=entities.registrationNumber if entities else None,
        khata_number=entities.khataNumber if entities else None,
        inspection_id=entities.inspectionId if entities else None,
        alert_id=entities.alertId if entities else None,
    )

    try:
        response = await hybrid_retrieve(req, db)
        elapsed = (time.perf_counter() - start) * 1000
        
        # Serialize chunks to dictionaries for LangGraph state compatibility
        context_chunks = [
            {
                "chunk_id": c.chunk_id,
                "text": c.text,
                "metadata": c.metadata,
                "final_score": c.final_score
            }
            for c in response.context.chunks
        ]

        logger.info("Executor completed retrieval in %.1fms", elapsed)

        return {
            "retrieved_context": context_chunks,
            "tool_calls": [{"name": "HybridRetrieval", "status": "success", "time_ms": elapsed}],
        }

    except Exception as exc:
        logger.error("Executor retrieval failed: %s", exc)
        return {
            "errors": [f"Retrieval tool failed: {str(exc)}"],
            "tool_calls": [{"name": "HybridRetrieval", "status": "failed", "error": str(exc)}],
        }
