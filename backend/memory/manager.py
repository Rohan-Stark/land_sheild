from __future__ import annotations

from backend.config.logging import get_logger
from backend.schemas.memory import ConversationMemory, PropertyMemory

logger = get_logger("memory.manager")


class MemoryManager:
    """Facade for managing conversation and property state.

    Handles loading, updating, persisting, and expiring memory states.
    For this implementation phase, we simulate an in-memory cache backing store,
    but the interface perfectly mirrors a Redis/Postgres Key-Value store.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, ConversationMemory] = {}
        self._properties: dict[str, PropertyMemory] = {}

    # ── Conversation Memory ──────────────────────────────────────

    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationMemory:
        """Retrieve conversation memory or initialize a new one."""
        if conversation_id not in self._conversations:
            logger.info("Initializing new ConversationMemory: %s", conversation_id)
            self._conversations[conversation_id] = ConversationMemory(
                conversation_id=conversation_id, user_id=user_id
            )
        return self._conversations[conversation_id]

    async def save_conversation(self, memory: ConversationMemory) -> None:
        """Persist conversation state."""
        self._conversations[memory.conversation_id] = memory
        logger.debug("Saved ConversationMemory: %s", memory.conversation_id)

    # ── Property Memory ──────────────────────────────────────────

    async def get_property_memory(self, property_id: str, user_id: str) -> PropertyMemory:
        """Retrieve property memory or initialize a new one."""
        if property_id not in self._properties:
            logger.info("Initializing new PropertyMemory: %s", property_id)
            self._properties[property_id] = PropertyMemory(
                property_id=property_id, owner_id=user_id
            )
        return self._properties[property_id]

    async def save_property_memory(self, memory: PropertyMemory) -> None:
        """Persist property state."""
        self._properties[memory.property_id] = memory
        logger.debug("Saved PropertyMemory: %s", memory.property_id)


# Singleton instance for the application runtime
memory_manager = MemoryManager()
