from __future__ import annotations

import secrets
import time
from typing import Any

from fastapi import HTTPException, status

from backend.config.logging import get_logger
from backend.security.secrets import get_secrets

logger = get_logger("security.refresh")

# In a real system, this would be backed by Redis or Postgres to track revocation.
# For phase 2D.2, we simulate the persistent store with an in-memory dictionary.
# Mapping: refresh_token -> {"user_id": str, "role": str, "exp": int}
_REFRESH_DB: dict[str, dict[str, Any]] = {}


class RefreshTokenService:
    """Service for issuing and validating opaque refresh tokens.
    
    Refresh tokens are opaque strings (not JWTs) to allow immediate server-side
    revocation without waiting for expiration.
    """

    @staticmethod
    def create_refresh_token(user_id: str, role: str) -> str:
        """Issue a new refresh token and store it securely."""
        config = get_secrets()
        token = secrets.token_urlsafe(64)
        expires = int(time.time()) + (config.jwt_refresh_expire_days * 86400)
        
        _REFRESH_DB[token] = {
            "user_id": user_id,
            "role": role,
            "exp": expires
        }
        
        return token

    @staticmethod
    def validate_and_rotate(old_token: str) -> tuple[str, str, str]:
        """Validate an existing token, revoke it, and return (new_refresh, user_id, role)."""
        record = _REFRESH_DB.get(old_token)
        
        if not record:
            logger.warning("Attempted use of invalid or revoked refresh token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token."
            )
            
        if record["exp"] < time.time():
            # Clean up expired token
            del _REFRESH_DB[old_token]
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired."
            )
            
        # Token is valid. Immediately revoke it (Rotate)
        user_id = record["user_id"]
        role = record["role"]
        del _REFRESH_DB[old_token]
        
        # Issue new token
        new_token = RefreshTokenService.create_refresh_token(user_id, role)
        return new_token, user_id, role

    @staticmethod
    def revoke_token(token: str) -> None:
        """Explicitly invalidate a refresh token (e.g., during logout)."""
        _REFRESH_DB.pop(token, None)
