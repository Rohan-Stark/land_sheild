from __future__ import annotations

import contextlib
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import health, retrieval, upload
from backend.config.logging import get_logger, setup_logging
from backend.config.settings import get_settings
from backend.database.postgres import init_db

setup_logging(debug=get_settings().DEBUG)
logger = get_logger("main")


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events."""
    logger.info("Starting LandShield AI Backend (Phase 1)...")
    await init_db()
    
    yield
    
    logger.info("Shutting down LandShield AI Backend...")


def create_app() -> FastAPI:
    """Factory to create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(retrieval.router)

    return app


app = create_app()
