from __future__ import annotations

from backend.config.logging import get_logger
from backend.llm.schemas.prompt import PromptRequest

logger = get_logger("llm.prompting.validator")


class PromptValidator:
    """Validates a fully rendered PromptRequest before sending to Ollama."""

    def __init__(self, max_prompt_tokens: int = 4096) -> None:
        self._max_tokens = max_prompt_tokens

    def validate(self, request: PromptRequest) -> list[str]:
        """Return a list of validation errors. Empty list means valid."""
        errors: list[str] = []

        if not request.messages:
            errors.append("Prompt must contain at least one message.")

        if not request.model:
            errors.append("Model name must be specified.")

        if request.prompt_token_estimate > self._max_tokens:
            errors.append(
                f"Estimated prompt tokens ({request.prompt_token_estimate}) "
                f"exceed budget ({self._max_tokens})."
            )

        # Verify system message exists
        has_system = any(m.role.value == "system" for m in request.messages)
        if not has_system:
            errors.append("Prompt must contain a system message.")

        # Verify user message exists
        has_user = any(m.role.value == "user" for m in request.messages)
        if not has_user:
            errors.append("Prompt must contain a user message.")

        if errors:
            logger.warning("Prompt validation failed: %s", errors)

        return errors
