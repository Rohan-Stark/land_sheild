from __future__ import annotations

from enum import Enum


class Permission(str, Enum):
    """Granular permissions enforced at the endpoint/service boundary."""
    
    # Document Access
    DOCUMENT_READ = "document.read"
    DOCUMENT_WRITE = "document.write"
    DOCUMENT_DELETE = "document.delete"
    
    # Property Access
    PROPERTY_READ = "property.read"
    PROPERTY_WRITE = "property.write"
    
    # Inspections
    INSPECTION_READ = "inspection.read"
    INSPECTION_WRITE = "inspection.write"
    
    # Reporting
    REPORT_GENERATE = "report.generate"
    REPORT_READ = "report.read"
    
    # Admin & Overrides
    ADMIN_MANAGE = "admin.manage"
    AUDIT_READ = "audit.read"
