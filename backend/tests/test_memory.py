from __future__ import annotations

import pytest

from backend.memory.conversation import ConversationService
from backend.memory.manager import memory_manager


@pytest.mark.asyncio
async def test_add_message():
    conv_id = "conv_123"
    user_id = "user_123"
    
    memory = await ConversationService.add_message(conv_id, user_id, "user", "Hello")
    assert len(memory.messages) == 1
    assert memory.messages[0].content == "Hello"
    assert memory.messages[0].role == "user"
    
    # Retrieve directly
    cached = await memory_manager.get_conversation(conv_id, user_id)
    assert len(cached.messages) == 1


@pytest.mark.asyncio
async def test_update_context():
    conv_id = "conv_123"
    user_id = "user_123"
    
    memory = await ConversationService.update_context(
        conv_id, user_id, property_id="prop_456", topic="tax"
    )
    assert memory.current_property_id == "prop_456"
    assert "tax" in memory.recent_topics
