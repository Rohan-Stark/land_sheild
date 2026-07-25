from __future__ import annotations

from backend.config.logging import get_logger
from backend.llm.client import OllamaClient
from backend.llm.schemas.runtime import RuntimeConfig

logger = get_logger("llm.manager")


class ModelManager:
    """Manages model selection, capability detection, and health monitoring.

    The ModelManager is the single point of truth for which model the runtime
    should use. It exposes the preferred model, an ordered fallback list, and
    health status per model.
    """

    def __init__(self, config: RuntimeConfig, client: OllamaClient) -> None:
        self._config = config
        self._client = client
        self._health_cache: dict[str, bool] = {}

    @property
    def preferred_model(self) -> str:
        return self._config.default_model

    @property
    def fallback_models(self) -> list[str]:
        return list(self._config.fallback_models)

    @property
    def all_models(self) -> list[str]:
        """Preferred model first, then fallbacks."""
        return [self.preferred_model] + self.fallback_models

    async def refresh_health(self) -> dict[str, bool]:
        """Probe Ollama for all configured models and cache availability."""
        available = await self._client.list_models()
        for model in self.all_models:
            self._health_cache[model] = any(model in m for m in available)
        logger.info("Model health refreshed: %s", self._health_cache)
        return dict(self._health_cache)

    def is_healthy(self, model_name: str) -> bool | None:
        """Return cached health. None means health has never been checked."""
        return self._health_cache.get(model_name)

    async def select_model(self) -> str:
        """Return the first healthy model in priority order.

        Falls back through the list. If none are healthy, returns the
        preferred model anyway (letting the client fail with a clear error).
        """
        if not self._health_cache:
            await self.refresh_health()

        for model in self.all_models:
            if self._health_cache.get(model, False):
                logger.info("Selected model: %s", model)
                return model

        logger.warning("No healthy models found, defaulting to %s", self.preferred_model)
        return self.preferred_model

    async def detect_capabilities(self, model_name: str) -> dict[str, bool]:
        """Return a simple capability map for a model.

        This is an approximation based on naming conventions. Real capability
        detection would inspect Ollama model metadata.
        """
        name_lower = model_name.lower()
        return {
            "chat": True,
            "streaming": True,
            "json_mode": "llama" in name_lower or "qwen" in name_lower,
            "large_context": "32k" in name_lower or "128k" in name_lower,
        }
