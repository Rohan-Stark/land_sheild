from __future__ import annotations

import uuid
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/bmp",
}


def validate_extension(filename: str) -> bool:
    """Check whether the file extension is supported."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def generate_safe_filename(original: str) -> str:
    """Generate a collision-free filename preserving the original extension."""
    ext = Path(original).suffix.lower()
    return f"{uuid.uuid4().hex}{ext}"


def ensure_dir(path: Path) -> Path:
    """Create directory tree if it does not exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_size_mb(path: Path) -> float:
    """Return file size in megabytes."""
    return path.stat().st_size / (1024 * 1024)
