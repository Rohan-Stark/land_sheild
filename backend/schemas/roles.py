from __future__ import annotations

from enum import Enum


class SystemRole(str, Enum):
    """The standard RBAC roles defined in the system."""
    ADMIN = "admin"
    PROPERTY_OWNER = "property_owner"
    INSPECTOR = "inspector"
    LEGAL_ADVISOR = "legal_advisor"
    READ_ONLY = "read_only"
    SERVICE_ACCOUNT = "service_account"
