from __future__ import annotations

from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    """Configuration for the AI Runtime Layer. Loaded from environment or defaults."""

    # ── Model Selection ──────────────────────────────────────────
    default_model: str = "llama3.1"
    fallback_models: list[str] = Field(default_factory=lambda: ["qwen2", "gemma2", "mistral"])

    # ── Generation Parameters ────────────────────────────────────
    temperature: float = 0.7
    top_p: float = 0.9
    context_window: int = 8192
    max_tokens: int = 2048

    # ── Retry ────────────────────────────────────────────────────
    retry_count: int = 3
    retry_base_delay_seconds: float = 1.0
    retry_max_delay_seconds: float = 30.0

    # ── Timeout ──────────────────────────────────────────────────
    request_timeout_seconds: float = 120.0
    streaming_timeout_seconds: float = 300.0

    # ── Streaming ────────────────────────────────────────────────
    streaming_enabled: bool = True
    heartbeat_interval_seconds: float = 15.0

    # ── Ollama Connection ────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"

    # ── Token Budget ─────────────────────────────────────────────
    max_prompt_tokens: int = 4096
