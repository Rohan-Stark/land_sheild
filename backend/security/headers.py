from __future__ import annotations

from typing import Any, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Automatically injects OWASP recommended security headers into every response."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        
        response: Response = await call_next(request)
        
        # 1. HSTS (Strict-Transport-Security)
        # Enforces HTTPS for 1 year (31536000 seconds), including subdomains.
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 2. X-Content-Type-Options
        # Prevents MIME-sniffing.
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 3. X-Frame-Options
        # Prevents clickjacking by denying iframe rendering outside origin.
        response.headers["X-Frame-Options"] = "DENY"
        
        # 4. Content-Security-Policy (CSP)
        # Prevents XSS by restricting resource loading. Default deny-all executable inline.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # 5. Referrer-Policy
        # Restricts how much referral information is sent with requests.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 6. Permissions-Policy
        # Disables access to sensitive browser features.
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
