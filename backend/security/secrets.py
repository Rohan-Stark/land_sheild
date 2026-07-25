from __future__ import annotations

import os
from functools import lru_cache

from backend.config.logging import get_logger

logger = get_logger("security.secrets")


class SecretsConfig:
    """Centralized management for highly sensitive configuration.
    
    In a real production environment this would fetch from AWS Secrets Manager
    or HashiCorp Vault. Here it fetches from environment variables.
    """
    
    @property
    def jwt_secret_key(self) -> str:
        secret = os.environ.get("JWT_SECRET_KEY")
        if not secret:
            logger.warning("JWT_SECRET_KEY not set. Using insecure fallback.")
            return "insecure-dev-jwt-secret-do-not-use-in-production"
        return secret

    @property
    def jwt_algorithm(self) -> str:
        return "HS256"

    @property
    def jwt_access_expire_minutes(self) -> int:
        return int(os.environ.get("JWT_ACCESS_EXPIRE_MINUTES", "30"))
        
    @property
    def jwt_refresh_expire_days(self) -> int:
        return int(os.environ.get("JWT_REFRESH_EXPIRE_DAYS", "7"))


@lru_cache(maxsize=1)
def get_secrets() -> SecretsConfig:
    """Cached singleton for secrets."""
    return SecretsConfig()
