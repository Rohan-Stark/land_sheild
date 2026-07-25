from __future__ import annotations

import secrets
from fastapi import Request, HTTPException, status
from backend.config.logging import get_logger

logger = get_logger("security.csrf")


class CSRFService:
    """Provides utilities for CSRF protection for cookie-based endpoints.
    
    Note: For standard Bearer token API requests, CSRF is not required because
    browsers do not automatically attach Authorization headers to cross-site requests.
    This service is provided for future endpoints (like OAuth callbacks or session cookies).
    """

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_token(request: Request) -> None:
        """Validates the CSRF token from the header matches the expected token."""
        # Only validate mutating methods
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return

        expected_token = request.cookies.get("csrf_token")
        provided_token = request.headers.get("X-CSRF-Token")

        if not expected_token or not provided_token:
            logger.warning("CSRF validation failed: Missing tokens.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing."
            )

        # Constant time comparison to prevent timing attacks
        if not secrets.compare_digest(expected_token, provided_token):
            logger.warning("CSRF validation failed: Token mismatch.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token invalid."
            )
