from __future__ import annotations

from typing import Any

from backend.schemas.retrieval import RetrievalRequest


def build_chroma_filter(request: RetrievalRequest) -> dict[str, Any] | None:
    """Build a ChromaDB metadata filter from the retrieval request.

    Every retrieval begins with metadata filtering. We never search the full
    vector database without filtering first by at least user_id.
    """
    conditions: list[dict[str, Any]] = [{"user_id": str(request.user_id)}]

    if request.property_id:
        conditions.append({"property_id": str(request.property_id)})
    if request.document_type:
        conditions.append({"document_type": request.document_type})
    if request.survey_number:
        conditions.append({"survey_number": request.survey_number})
    if request.registration_number:
        conditions.append({"registration_number": request.registration_number})
    if request.khata_number:
        conditions.append({"khata_number": request.khata_number})
    if request.inspection_id:
        conditions.append({"inspection_id": request.inspection_id})
    if request.alert_id:
        conditions.append({"alert_id": request.alert_id})

    if len(conditions) == 1:
        return conditions[0]
    else:
        return {"$and": conditions}
