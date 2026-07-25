from __future__ import annotations

from backend.config.logging import get_logger
from backend.llm.schemas.response import FinalResponse
from backend.safety.policies import DEFAULT_POLICIES, SafetyPolicy

logger = get_logger("safety.validator")


class SafetyValidator:
    """Evaluates an LLM response against all active safety policies."""

    def __init__(self, policies: list[SafetyPolicy] | None = None) -> None:
        self._policies = policies or DEFAULT_POLICIES

    def validate(self, response: FinalResponse) -> list[str]:
        """Return a list of policy violation strings. Empty list means safe."""
        violations: list[str] = []
        for policy in self._policies:
            error = policy(response)
            if error:
                violations.append(error)

        if violations:
            logger.warning("Safety violations detected: %s", violations)

        return violations
