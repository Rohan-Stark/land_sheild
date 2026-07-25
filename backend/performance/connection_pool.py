from __future__ import annotations

import os
from dataclasses import dataclass, field

from backend.config.logging import get_logger

logger = get_logger("performance.connection_pool")


@dataclass
class PoolConfig:
    """Connection pool settings for a single backend service."""
    service_name: str
    min_connections: int = 2
    max_connections: int = 20
    max_idle_seconds: int = 300
    connection_timeout_seconds: int = 10
    health_check_interval_seconds: int = 30


@dataclass
class PoolStats:
    """Runtime stats for a connection pool."""
    active: int = 0
    idle: int = 0
    total_created: int = 0
    total_recycled: int = 0
    failed_acquisitions: int = 0


class ConnectionPoolManager:
    """Centralized registry and lifecycle controller for database and service pools.

    In production, each pool would wrap an actual driver-specific pool:
    - asyncpg.Pool for PostgreSQL
    - redis.asyncio.ConnectionPool for Redis
    - httpx.AsyncClient with limits for HTTP
    - chromadb.AsyncHttpClient for ChromaDB

    This manager provides the configuration, monitoring, and lifecycle hooks.
    """

    def __init__(self) -> None:
        self._configs: dict[str, PoolConfig] = {}
        self._stats: dict[str, PoolStats] = {}

    def register(self, config: PoolConfig) -> None:
        self._configs[config.service_name] = config
        self._stats[config.service_name] = PoolStats()
        logger.info(
            "Registered pool for %s: min=%d, max=%d",
            config.service_name,
            config.min_connections,
            config.max_connections,
        )

    def get_config(self, service_name: str) -> PoolConfig | None:
        return self._configs.get(service_name)

    def get_stats(self, service_name: str) -> PoolStats | None:
        return self._stats.get(service_name)

    def record_acquire(self, service_name: str) -> None:
        stats = self._stats.get(service_name)
        if stats:
            stats.active += 1
            stats.total_created += 1

    def record_release(self, service_name: str) -> None:
        stats = self._stats.get(service_name)
        if stats:
            stats.active = max(0, stats.active - 1)
            stats.idle += 1

    def record_failure(self, service_name: str) -> None:
        stats = self._stats.get(service_name)
        if stats:
            stats.failed_acquisitions += 1


# Singleton with default pools
pool_manager = ConnectionPoolManager()

pool_manager.register(PoolConfig(
    service_name="postgres",
    min_connections=int(os.environ.get("PG_POOL_MIN", "5")),
    max_connections=int(os.environ.get("PG_POOL_MAX", "20")),
))
pool_manager.register(PoolConfig(
    service_name="redis",
    min_connections=2,
    max_connections=10,
))
pool_manager.register(PoolConfig(
    service_name="chromadb",
    min_connections=1,
    max_connections=5,
))
pool_manager.register(PoolConfig(
    service_name="http_ollama",
    min_connections=2,
    max_connections=8,
    connection_timeout_seconds=30,
))
