from __future__ import annotations

from passlib.context import CryptContext

from backend.config.logging import get_logger

logger = get_logger("security.passwords")

# Argon2 is the OWASP recommended password hashing algorithm
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


class PasswordService:
    """Service for securely hashing and verifying passwords."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Return True if the plain password matches the hashed version."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as exc:
            logger.error("Failed to verify password hash: %s", exc)
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plaintext password using Argon2id."""
        return pwd_context.hash(password)

    @staticmethod
    def check_needs_rehash(hashed_password: str) -> bool:
        """Return True if the hash needs upgrading to stronger parameters."""
        return pwd_context.needs_update(hashed_password)
