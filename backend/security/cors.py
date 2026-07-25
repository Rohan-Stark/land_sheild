from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI) -> None:
    """Configures restrictive CORS for production.
    
    Reads allowed origins from environment. Never uses wildcards in production.
    """
    
    # In development, you might set this to ["http://localhost:3000"]
    # In production, strictly ["https://app.landshield.ai"]
    raw_origins = os.environ.get("ALLOWED_CORS_ORIGINS", "")
    allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    
    if not allowed_origins:
        # Failsafe default if environment isn't configured yet
        allowed_origins = ["http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization", 
            "Content-Type", 
            "X-API-Key",
            "X-CSRF-Token",
            "X-Request-ID"
        ],
        expose_headers=["X-Request-ID"]
    )
