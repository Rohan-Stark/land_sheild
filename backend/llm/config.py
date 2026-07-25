from __future__ import annotations

from functools import lru_cache

from backend.llm.schemas.runtime import RuntimeConfig


@lru_cache(maxsize=1)
def get_runtime_config() -> RuntimeConfig:
    """Cached singleton for the AI runtime configuration."""
    return RuntimeConfig()
