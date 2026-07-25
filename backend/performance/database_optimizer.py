from __future__ import annotations

from typing import Any, Sequence

from backend.config.logging import get_logger

logger = get_logger("performance.database_optimizer")


class DatabaseOptimizer:
    """Provides query optimization utilities to prevent N+1 problems and enforce batching.

    These are configuration helpers that inform SQLAlchemy ORM usage patterns.
    They do not execute raw SQL themselves.
    """

    @staticmethod
    def batch_ids(ids: Sequence[str], batch_size: int = 100) -> list[list[str]]:
        """Split a large ID list into chunks suitable for IN-clause queries.
        
        Prevents sending excessively long SQL IN clauses that exceed
        database parser limits or degrade query plan performance.
        """
        batches = []
        for i in range(0, len(ids), batch_size):
            batches.append(list(ids[i : i + batch_size]))
        logger.debug("Batched %d IDs into %d groups of %d", len(ids), len(batches), batch_size)
        return batches

    @staticmethod
    def paginate(offset: int, limit: int, max_limit: int = 200) -> tuple[int, int]:
        """Enforce safe pagination boundaries.

        Ensures:
        - offset >= 0
        - limit between 1 and max_limit
        """
        safe_offset = max(0, offset)
        safe_limit = min(max(1, limit), max_limit)
        return safe_offset, safe_limit

    @staticmethod
    def suggest_indexes() -> list[dict[str, str]]:
        """Return recommended indexes for core tables based on query patterns.

        This is a static analysis utility that can be consumed by migration scripts.
        """
        return [
            {"table": "documents", "column": "property_id", "type": "btree"},
            {"table": "documents", "column": "uploaded_at", "type": "btree"},
            {"table": "properties", "column": "owner_id", "type": "btree"},
            {"table": "inspections", "column": "property_id", "type": "btree"},
            {"table": "inspections", "column": "inspection_date", "type": "btree"},
            {"table": "alerts", "column": "property_id", "type": "btree"},
            {"table": "alerts", "column": "severity", "type": "btree"},
            {"table": "audit_logs", "column": "user_id", "type": "btree"},
            {"table": "audit_logs", "column": "created_at", "type": "btree"},
        ]
