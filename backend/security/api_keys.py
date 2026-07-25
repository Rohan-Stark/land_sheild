from __future__ import annotations

import secrets
from typing import Any

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from backend.config.logging import get_logger

logger = get_logger("security.apikeys")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Simulated secure vault for API keys.
# Maps API_KEY -> {"owner": str, "scopes": list[str]}
_API_KEY_VAULT: dict[str, dict[str, Any]] = {}


class APIKeyService:
    """Service for managing and validating long-lived API keys."""

    @staticmethod
    def create_api_key(owner: str, scopes: list[str]) -> str:
        """Generate a secure random API key."""
        # Standard prefix to easily identify key types in logs/scanners
        prefix = "ls_" 
        key = prefix + secrets.token_urlsafe(32)
        _API_KEY_VAULT[key] = {"owner": owner, "scopes": scopes}
        logger.info("Created new API key for %s with scopes %s", owner, scopes)
        return key

    @staticmethod
    def validate_api_key(api_key: str = Security(api_key_header)) -> dict[str, Any]:
        """FastAPI Dependency to validate an incoming API key."""
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing API Key header.",
            )
            
        record = _API_KEY_VAULT.get(api_key)
        if not record:
            logger.warning("Invalid API Key used.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key."
            )
            
        return record
