from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.security.headers import SecureHeadersMiddleware
from backend.security.sanitization import InputSanitizer
from backend.security.validation import RequestValidator


def test_secure_headers():
    app = FastAPI()
    app.add_middleware(SecureHeadersMiddleware)
    
    @app.get("/")
    def read_root():
        return {"msg": "ok"}
        
    client = TestClient(app)
    response = client.get("/")
    
    # Assert OWASP headers are injected
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers


def test_input_sanitization():
    # Remove HTML
    dirty = "<script>alert(1)</script>Hello"
    clean = InputSanitizer.sanitize_text(dirty)
    assert clean == "Hello"
    
    # Prevent log injection
    dirty_log = "User log \n\r [Fake Admin Log]"
    clean_log = InputSanitizer.sanitize_text(dirty_log)
    assert "\n" not in clean_log
    
    # Clean filenames
    assert InputSanitizer.sanitize_filename("bad file@name.txt") == "bad_file_name.txt"


def test_request_validation():
    # Valid ID
    RequestValidator.validate_id("valid-uuid-123")
    
    # Invalid ID
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        RequestValidator.validate_id("SELECT * FROM users")
