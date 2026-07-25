from __future__ import annotations

import pytest

from backend.agents.agent_context import AgentContext
from backend.agents.exceptions import AgentValidationError
from backend.agents.validation import validate_context, validate_retrieval, validate_tools
from backend.schemas.graph import IntentCategory


def test_validate_context_missing_user():
    context = AgentContext(
        requestId="123",
        userId="",
        intent=IntentCategory.UNKNOWN
    )
    with pytest.raises(AgentValidationError, match="userId"):
        validate_context(context, [])


def test_validate_context_missing_entity():
    context = AgentContext(
        requestId="123",
        userId="user_1",
        intent=IntentCategory.UNKNOWN
    )
    with pytest.raises(AgentValidationError, match="propertyId"):
        validate_context(context, ["propertyId"])


def test_validate_retrieval_missing():
    context = AgentContext(
        requestId="123",
        userId="user_1",
        intent=IntentCategory.UNKNOWN
    )
    with pytest.raises(AgentValidationError, match="retrieval context"):
        validate_retrieval(context, requires_retrieval=True)


def test_validate_retrieval_success():
    context = AgentContext(
        requestId="123",
        userId="user_1",
        intent=IntentCategory.UNKNOWN,
        retrievalResults=[{"chunk_id": "c1"}]
    )
    # Should not raise
    validate_retrieval(context, requires_retrieval=True)
