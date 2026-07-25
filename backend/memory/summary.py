from __future__ import annotations

from backend.config.logging import get_logger
from backend.memory.manager import memory_manager
from backend.schemas.memory import ConversationMemory

logger = get_logger("memory.summary")


class ConversationSummarizer:
    """Service for compressing long chat histories into a persistent summary string.
    
    In a real environment, this would call the LLM directly via `AIRuntime`.
    For this phase boundary, we define the deterministic state-transition logic.
    """

    def __init__(self, message_threshold: int = 15) -> None:
        self._message_threshold = message_threshold

    async def summarize_if_needed(
        self, conversation_id: str, user_id: str
    ) -> ConversationMemory:
        """Check if history exceeds the threshold and synthesize if necessary."""
        memory = await memory_manager.get_conversation(conversation_id, user_id)

        if len(memory.messages) <= self._message_threshold:
            return memory

        logger.info(
            "Conversation %s exceeds %d messages. Triggering summarization.",
            conversation_id,
            self._message_threshold,
        )

        # Mock LLM Summarization behavior for this layer
        new_summary = self._mock_summarize(memory)
        
        # Keep the summary, but archive (delete) the oldest messages, keeping last 5
        memory.summary = new_summary
        memory.messages = memory.messages[-5:]
        
        await memory_manager.save_conversation(memory)
        return memory

    @staticmethod
    def _mock_summarize(memory: ConversationMemory) -> str:
        """Deterministic mockup of the LLM summarizer logic."""
        base = memory.summary + "\n" if memory.summary else ""
        user_intents = [m.content for m in memory.messages if m.role == "user"]
        return (
            f"{base}Archived context: The user asked about "
            f"{len(user_intents)} topics recently, heavily focusing on property "
            f"{memory.current_property_id or 'unknown'}."
        )
