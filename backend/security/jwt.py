from __future__ import annotations

import time
from typing import Any

import jwt
from fastapi import HTTPException, status

from backend.config.logging import get_logger
from backend.schemas.auth import TokenPayload
from backend.security.secrets import get_secrets

logger = get_logger("security.jwt")


class JWTService:
    """Service for encoding and decoding standard JSON Web Tokens."""

    @staticmethod
    def create_access_token(user_id: str, role: str) -> str:
        """Issue a short-lived access token."""
        secrets = get_secrets()
        expires = int(time.time()) + (secrets.jwt_access_expire_minutes * 60)
        
        payload = {
            "sub": user_id,
            "role": role,
            "exp": expires,
            "type": "access"
        }
        
        return jwt.encode(payload, secrets.jwt_secret_key, algorithm=secrets.jwt_algorithm)

    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        """Decode and validate a token, returning the strongly typed payload."""
        secrets = get_secrets()
        try:
            payload = jwt.decode(
                token, 
                secrets.jwt_secret_key, 
                algorithms=[secrets.jwt_algorithm]
            )
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type.",
                )
                
            return TokenPayload(**payload)
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (jwt.PyJWTError, ValueError) as exc:
            logger.warning("Token verification failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
