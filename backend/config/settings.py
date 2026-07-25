from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application-wide settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "LandShield AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── PostgreSQL ───────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/landshield",
        description="Async PostgreSQL connection string",
    )
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # ── ChromaDB ─────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = Field(
        default=str(Path(__file__).resolve().parent.parent / "data" / "chroma"),
        description="ChromaDB persistent storage directory",
    )

    # ── Embedding Model ──────────────────────────────────────────
    EMBEDDING_MODEL: str = "nomic-ai/nomic-embed-text-v1.5"
    EMBEDDING_DIMENSION: int = 768

    # ── Reranker Model ───────────────────────────────────────────
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # ── Ingestion ────────────────────────────────────────────────
    CHUNK_SIZE_TOKENS: int = 600
    CHUNK_OVERLAP_TOKENS: int = 120
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── Retrieval ────────────────────────────────────────────────
    SEMANTIC_TOP_K: int = 20
    FINAL_TOP_K: int = 5
    MAX_CONTEXT_TOKENS: int = 4000

    # ── Tesseract ────────────────────────────────────────────────
    TESSERACT_CMD: str | None = None  # Path to tesseract binary if not in PATH

    # ── File Storage ─────────────────────────────────────────────
    UPLOAD_DIR: str = Field(
        default=str(Path(__file__).resolve().parent.parent / "data" / "uploads"),
        description="Directory for uploaded documents",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton for application settings."""
    return Settings()
