from __future__ import annotations

import re

from fastapi import HTTPException, status

from backend.config.logging import get_logger

logger = get_logger("security.validation")


class RequestValidator:
    """Provides regex-based validation for critical request parameters."""

    # Restrict UUIDs, alphanumeric IDs, and specific safe characters.
    ID_REGEX = re.compile(r"^[a-zA-Z0-9\-_]{5,50}$")
    
    @staticmethod
    def validate_id(resource_id: str, field_name: str = "ID") -> None:
        """Validates that a path or query ID parameter contains only safe characters."""
        if not RequestValidator.ID_REGEX.match(resource_id):
            logger.warning("Rejected malformed %s: %s", field_name, resource_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format for {field_name}."
            )
