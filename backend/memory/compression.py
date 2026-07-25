from __future__ import annotations

import json
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("memory.compression")


class MemoryCompressor:
    """Removes duplicate facts from retrieved memory chunks before prompting."""

    @staticmethod
    def deduplicate_facts(facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove exactly matching fact dicts (ignoring order/timestamps where possible)."""
        seen_hashes: set[int] = set()
        unique: list[dict[str, Any]] = []

        for fact in facts:
            # We sort keys to ensure stable JSON stringification
            dumped = json.dumps(fact, sort_keys=True, default=str)
            fact_hash = hash(dumped)

            if fact_hash not in seen_hashes:
                seen_hashes.add(fact_hash)
                unique.append(fact)

        logger.debug("Compressed %d facts to %d unique facts", len(facts), len(unique))
        return unique
