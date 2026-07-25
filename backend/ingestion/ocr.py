from __future__ import annotations

import io
import time

import pytesseract
from PIL import Image

from backend.config.logging import get_logger
from backend.config.settings import get_settings

logger = get_logger("ingestion.ocr")

# Minimum text length to consider a page as having extractable text
_MIN_TEXT_LENGTH = 50


def _configure_tesseract() -> None:
    """Point pytesseract to the binary if configured."""
    settings = get_settings()
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def is_scanned_page(text: str) -> bool:
    """Determine if a page is likely scanned (insufficient native text)."""
    stripped = text.strip()
    if len(stripped) < _MIN_TEXT_LENGTH:
        return True
    # High ratio of non-alphanumeric might indicate garbled extraction
    alpha_count = sum(1 for c in stripped if c.isalnum())
    return alpha_count / max(len(stripped), 1) < 0.3


def extract_text_ocr(image_bytes: bytes) -> str:
    """Run Tesseract OCR on raw image bytes and return extracted text."""
    _configure_tesseract()
    start = time.perf_counter()

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Use English + Hindi for Indian land documents
        text = pytesseract.image_to_string(image, lang="eng", config="--psm 6")
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("OCR completed: time=%.1fms, chars=%d", elapsed, len(text))
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        logger.error(
            "Tesseract binary not found. Install tesseract-ocr or set TESSERACT_CMD."
        )
        raise RuntimeError(
            "Tesseract OCR is not installed. Please install tesseract-ocr on this system."
        )
    except Exception as exc:
        logger.error("OCR failed: %s", exc)
        raise ValueError(f"OCR processing failed: {exc}") from exc
