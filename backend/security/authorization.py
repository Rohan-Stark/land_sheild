from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status

from backend.config.logging import get_logger
from backend.schemas.auth import TokenPayload
from backend.schemas.permissions import Permission
from backend.security.authentication import get_current_user
from backend.security.roles import RoleResolver

logger = get_logger("security.authorization")


class RequirePermission:
    """FastAPI Dependency enforcing fine-grained RBAC permissions.
    
    Usage:
        @app.get("/documents")
        async def get_docs(user = Depends(RequirePermission(Permission.DOCUMENT_READ))):
            ...
    """

    def __init__(self, required_permission: Permission) -> None:
        self.required_permission = required_permission

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        permissions = RoleResolver.get_permissions(user.role)
        
        if self.required_permission not in permissions:
            logger.warning(
                "Permission denied. User %s (role %s) attempted action requiring %s",
                user.sub,
                user.role,
                self.required_permission.value
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions."
            )
            
        return user
