from __future__ import annotations

import pytest
import uuid

from backend.tools.exceptions import ToolPermissionError
from backend.tools.validation import PermissionValidator


# We'll build a mock db session that simulates an empty response for a permission check
class MockScalarResult:
    def scalar_one_or_none(self):
        return None  # Simulates resource not found / not owned


class MockResult:
    def __init__(self):
        pass
    def scalar_one_or_none(self):
        return None


class MockAsyncSession:
    async def execute(self, stmt):
        return MockResult()


@pytest.mark.asyncio
async def test_permission_validator_property_denied():
    db = MockAsyncSession()
    # Random UUIDs
    uid = str(uuid.uuid4())
    pid = str(uuid.uuid4())
    
    with pytest.raises(ToolPermissionError, match="Access denied or Property not found"):
        await PermissionValidator.verify_property_ownership(db, uid, pid)  # type: ignore


@pytest.mark.asyncio
async def test_permission_validator_document_denied():
    db = MockAsyncSession()
    uid = str(uuid.uuid4())
    did = str(uuid.uuid4())
    
    with pytest.raises(ToolPermissionError, match="Access denied or Document not found"):
        await PermissionValidator.verify_document_ownership(db, uid, did)  # type: ignore


@pytest.mark.asyncio
async def test_permission_validator_invalid_uuid():
    db = MockAsyncSession()
    
    with pytest.raises(ToolPermissionError, match="Invalid UUID format"):
        await PermissionValidator.verify_property_ownership(db, "not-a-uuid", "also-not")  # type: ignore
