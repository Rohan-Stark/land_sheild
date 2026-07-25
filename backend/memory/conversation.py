from __future__ import annotations

import uuid
from typing import Any

from backend.config.logging import get_logger
from backend.memory.manager import memory_manager
from backend.schemas.memory import ConversationMemory, MemoryMessage

logger = get_logger("memory.conversation")


class ConversationService:
    """Service for manipulating conversational history."""

    @staticmethod
    async def add_message(
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> ConversationMemory:
        """Append a single message (user or assistant) to the history."""
        memory = await memory_manager.get_conversation(conversation_id, user_id)
        
        msg = MemoryMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        memory.messages.append(msg)
        await memory_manager.save_conversation(memory)
        
        logger.debug("Added %s message to conversation %s", role, conversation_id)
        return memory

    @staticmethod
    async def update_context(
        conversation_id: str,
        user_id: str,
        property_id: str | None = None,
        documents: list[str] | None = None,
        topic: str | None = None
    ) -> ConversationMemory:
        """Update active contextual pointers in the memory."""
        memory = await memory_manager.get_conversation(conversation_id, user_id)
        
        if property_id:
            memory.current_property_id = property_id
            
        if documents:
            # Union to keep existing selections without duplicating
            existing = set(memory.selected_documents)
            existing.update(documents)
            memory.selected_documents = list(existing)
            
        if topic and topic not in memory.recent_topics:
            memory.recent_topics.append(topic)
            # Keep only last 5 topics
            memory.recent_topics = memory.recent_topics[-5:]

        await memory_manager.save_conversation(memory)
        return memory
