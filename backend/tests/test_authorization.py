from __future__ import annotations

import pytest
from fastapi import HTTPException

from backend.schemas.auth import TokenPayload
from backend.schemas.permissions import Permission
from backend.security.api_keys import APIKeyService
from backend.security.authorization import RequirePermission


def test_require_permission_success():
    dependency = RequirePermission(Permission.DOCUMENT_READ)
    payload = TokenPayload(sub="user_1", role="property_owner", exp=9999999999)
    
    # Should return payload without raising exception
    result = dependency(user=payload)
    assert result == payload


def test_require_permission_denied():
    dependency = RequirePermission(Permission.ADMIN_MANAGE)
    payload = TokenPayload(sub="user_1", role="property_owner", exp=9999999999)
    
    with pytest.raises(HTTPException) as exc:
        dependency(user=payload)
    assert exc.value.status_code == 403


def test_api_keys():
    key = APIKeyService.create_api_key(owner="test_service", scopes=["all"])
    assert key.startswith("ls_")
    
    # Valid key
    record = APIKeyService.validate_api_key(api_key=key)
    assert record["owner"] == "test_service"
    
    # Invalid key
    with pytest.raises(HTTPException):
        APIKeyService.validate_api_key(api_key="ls_invalid")
