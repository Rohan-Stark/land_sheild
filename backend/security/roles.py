from __future__ import annotations

from backend.schemas.permissions import Permission
from backend.schemas.roles import SystemRole

# RBAC Definition: Maps a single Role to many Permissions.
# Uses additive inheritance where possible.

_ROLE_PERMISSIONS: dict[SystemRole, set[Permission]] = {
    SystemRole.READ_ONLY: {
        Permission.DOCUMENT_READ,
        Permission.PROPERTY_READ,
        Permission.INSPECTION_READ,
        Permission.REPORT_READ,
    },
    SystemRole.INSPECTOR: {
        Permission.DOCUMENT_READ,
        Permission.PROPERTY_READ,
        Permission.INSPECTION_READ,
        Permission.INSPECTION_WRITE,
        Permission.REPORT_READ,
    },
    SystemRole.LEGAL_ADVISOR: {
        Permission.DOCUMENT_READ,
        Permission.PROPERTY_READ,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
    },
    SystemRole.PROPERTY_OWNER: {
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_WRITE,
        Permission.DOCUMENT_DELETE,
        Permission.PROPERTY_READ,
        Permission.PROPERTY_WRITE,
        Permission.INSPECTION_READ,
        Permission.REPORT_READ,
        Permission.REPORT_GENERATE,
    },
    SystemRole.ADMIN: {
        # Admins get everything implicitly below, but we declare it explicitly.
        p for p in Permission
    },
    SystemRole.SERVICE_ACCOUNT: {
        # System-level overrides
        Permission.PROPERTY_READ,
        Permission.DOCUMENT_READ,
    }
}


class RoleResolver:
    """Resolves abstract roles down to concrete granular permissions."""

    @staticmethod
    def get_permissions(role_name: str) -> set[Permission]:
        try:
            role_enum = SystemRole(role_name.lower())
            return _ROLE_PERMISSIONS.get(role_enum, set())
        except ValueError:
            return set()
