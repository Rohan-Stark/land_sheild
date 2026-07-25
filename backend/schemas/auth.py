from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Returned to the client upon successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """The decoded payload inside the JWT."""
    sub: str  # user_id
    role: str
    exp: int


class LoginRequest(BaseModel):
    """Standard OAuth2 compatible login payload."""
    username: EmailStr
    password: str
