from __future__ import annotations

from typing import Any

from backend.config.logging import get_logger
from backend.memory.manager import memory_manager
from backend.schemas.memory import ConversationMemory, PropertyMemory

logger = get_logger("memory.retriever")


class MemoryRetriever:
    """Fetches and packages relevant memory context for LLM inclusion."""

    @staticmethod
    async def get_active_context(
        conversation_id: str,
        user_id: str,
        property_id: str | None = None
    ) -> dict[str, Any]:
        """Bundle the most relevant conversational and property state."""
        conv: ConversationMemory | None = None
        prop: PropertyMemory | None = None

        try:
            conv = await memory_manager.get_conversation(conversation_id, user_id)
        except Exception as exc:
            logger.warning("Failed to retrieve conversation memory: %s", exc)

        if property_id:
            try:
                prop = await memory_manager.get_property_memory(property_id, user_id)
            except Exception as exc:
                logger.warning("Failed to retrieve property memory: %s", exc)

        context: dict[str, Any] = {
            "conversation_summary": conv.summary if conv else None,
            "recent_topics": conv.recent_topics if conv else [],
            "selected_documents": conv.selected_documents if conv else [],
            "property_alerts": prop.active_alerts if prop else [],
            "generated_reports": prop.generated_reports if prop else [],
        }
        
        return context
