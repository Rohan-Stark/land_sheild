from __future__ import annotations

from typing import Any

from backend.config.logging import get_logger
from backend.memory.manager import memory_manager
from backend.schemas.memory import PropertyMemory

logger = get_logger("memory.property")


class PropertyService:
    """Service for mutating persistent, long-term property state."""

    @staticmethod
    async def update_alerts(
        property_id: str,
        user_id: str,
        alerts: list[dict[str, Any]]
    ) -> PropertyMemory:
        """Overwrite the currently cached alerts for a property."""
        memory = await memory_manager.get_property_memory(property_id, user_id)
        memory.active_alerts = alerts
        await memory_manager.save_property_memory(memory)
        logger.debug("Updated %d alerts for property %s", len(alerts), property_id)
        return memory

    @staticmethod
    async def log_generated_report(
        property_id: str,
        user_id: str,
        report_id: str
    ) -> PropertyMemory:
        """Track reports generated for this property."""
        memory = await memory_manager.get_property_memory(property_id, user_id)
        if report_id not in memory.generated_reports:
            memory.generated_reports.append(report_id)
            await memory_manager.save_property_memory(memory)
        return memory

    @staticmethod
    def _merge_metadata(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        """Deep merge dicts, prioritizing incoming on conflict."""
        merged = existing.copy()
        for k, v in incoming.items():
            if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
                merged[k] = PropertyService._merge_metadata(merged[k], v)
            else:
                merged[k] = v
        return merged

    @staticmethod
    async def update_metadata(
        property_id: str,
        user_id: str,
        metadata: dict[str, Any]
    ) -> PropertyMemory:
        """Merge new metadata findings into long-term storage."""
        memory = await memory_manager.get_property_memory(property_id, user_id)
        memory.retrieved_metadata = PropertyService._merge_metadata(
            memory.retrieved_metadata, metadata
        )
        await memory_manager.save_property_memory(memory)
        return memory
