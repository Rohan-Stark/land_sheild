from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.config.logging import get_logger
from backend.schemas.auth import TokenPayload
from backend.security.jwt import JWTService

logger = get_logger("security.authentication")

# The OAuth2 scheme extracts the Bearer token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=False  # Allow us to handle missing tokens gracefully
)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> TokenPayload:
    """FastAPI Dependency extracting the authenticated user payload.
    
    If the token is missing or invalid, immediately throws a 401.
    """
    if not token:
        logger.warning("Unauthenticated request attempted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = JWTService.verify_token(token)
    return payload


def get_current_user_optional(token: str | None = Depends(oauth2_scheme)) -> TokenPayload | None:
    """FastAPI Dependency for endpoints where auth is optional."""
    if not token:
        return None
    try:
        return JWTService.verify_token(token)
    except HTTPException:
        return None
