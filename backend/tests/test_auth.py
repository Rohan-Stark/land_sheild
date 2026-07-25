from __future__ import annotations

import os
from unittest import mock

import pytest
from fastapi import HTTPException

from backend.security.jwt import JWTService
from backend.security.passwords import PasswordService
from backend.security.refresh_tokens import RefreshTokenService


def test_password_hashing():
    plain = "SuperSecure123!"
    hashed = PasswordService.get_password_hash(plain)
    
    assert hashed != plain
    assert PasswordService.verify_password(plain, hashed) is True
    assert PasswordService.verify_password("wrong", hashed) is False


@mock.patch.dict(os.environ, {"JWT_SECRET_KEY": "test-secret"})
def test_jwt_creation_and_validation():
    token = JWTService.create_access_token(user_id="user_1", role="admin")
    
    # Verify valid token
    payload = JWTService.verify_token(token)
    assert payload.sub == "user_1"
    assert payload.role == "admin"
    
    # Verify invalid token throws 401
    with pytest.raises(HTTPException) as exc:
        JWTService.verify_token(token + "invalid")
    assert exc.value.status_code == 401


def test_refresh_token_flow():
    token = RefreshTokenService.create_refresh_token(user_id="user_2", role="inspector")
    assert len(token) > 20
    
    # Rotate token
    new_token, uid, role = RefreshTokenService.validate_and_rotate(token)
    assert uid == "user_2"
    assert role == "inspector"
    assert new_token != token
    
    # Old token should now be invalid
    with pytest.raises(HTTPException):
        RefreshTokenService.validate_and_rotate(token)
