from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from backend.config.logging import get_logger

# Dedicated logger for audit events. In production, this would route to a secure, 
# append-only log aggregator (like Splunk or Datadog Audit).
audit_logger = get_logger("security.audit")


class AuditLogger:
    """Immutable, structured logging for critical security events."""

    @staticmethod
    def log_event(
        action: str,
        user_id: str | None = None,
        resource_id: str | None = None,
        status: str = "success",
        details: dict[str, Any] | None = None,
        request_id: str | None = None
    ) -> None:
        """Record an audit trail event."""
        
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "status": status,
            "user_id": user_id or "anonymous",
            "resource_id": resource_id,
            "request_id": request_id,
            "details": details or {}
        }
        
        # Serialize to strict JSON format for log ingestion
        log_line = json.dumps(event, default=str)
        
        if status == "success":
            audit_logger.info("AUDIT: %s", log_line)
        else:
            audit_logger.warning("AUDIT_FAILURE: %s", log_line)
