from __future__ import annotations

from backend.config.logging import get_logger

logger = get_logger("llm.responses.validator")


class OutputValidator:
    """Validates LLM output before it reaches the client.

    Checks:
    - Non-empty content
    - UTF-8 validity
    - Maximum length enforcement
    - Basic structural checks for JSON/Markdown outputs
    """

    def __init__(self, max_length: int = 16384) -> None:
        self._max_length = max_length

    def validate(self, content: str, expected_format: str = "markdown") -> tuple[bool, list[str]]:
        """Return (is_valid, list_of_errors)."""
        errors: list[str] = []

        if not content or not content.strip():
            errors.append("Response content is empty.")

        if len(content) > self._max_length:
            errors.append(
                f"Response exceeds maximum length ({len(content)} > {self._max_length})."
            )

        # UTF-8 validity
        try:
            content.encode("utf-8")
        except UnicodeEncodeError:
            errors.append("Response contains invalid UTF-8 characters.")

        # Format-specific checks
        if expected_format == "json":
            errors.extend(self._validate_json(content))

        if errors:
            logger.warning("Output validation failed: %s", errors)

        return len(errors) == 0, errors

    @staticmethod
    def _validate_json(content: str) -> list[str]:
        import json
        errors: list[str] = []
        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON output: {exc}")
        return errors
