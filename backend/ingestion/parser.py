from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from backend.config.logging import get_logger
from backend.ingestion.ocr import extract_text_ocr, is_scanned_page

logger = get_logger("ingestion.parser")


class ParseResult:
    """Result of parsing a document."""

    def __init__(
        self,
        text: str,
        page_count: int,
        ocr_applied: bool,
        page_texts: list[str],
        parse_time_ms: float,
    ) -> None:
        self.text = text
        self.page_count = page_count
        self.ocr_applied = ocr_applied
        self.page_texts = page_texts
        self.parse_time_ms = parse_time_ms


def parse_pdf(file_path: Path) -> ParseResult:
    """Extract text from a PDF, falling back to OCR for scanned pages."""
    start = time.perf_counter()
    ocr_applied = False
    page_texts: list[str] = []

    try:
        doc = fitz.open(str(file_path))
    except Exception as exc:
        raise ValueError(f"Cannot open PDF: {exc}") from exc

    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()

            if not text or is_scanned_page(text):
                # Scanned page — use OCR
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                text = extract_text_ocr(img_bytes)
                ocr_applied = True
                logger.debug("OCR applied to page %d", page_num + 1)

            page_texts.append(text)
    finally:
        doc.close()

    full_text = "\n\n".join(page_texts)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info(
        "Parsed PDF: pages=%d, ocr=%s, time=%.1fms, chars=%d",
        len(page_texts), ocr_applied, elapsed, len(full_text),
    )

    return ParseResult(
        text=full_text,
        page_count=len(page_texts),
        ocr_applied=ocr_applied,
        page_texts=page_texts,
        parse_time_ms=elapsed,
    )


def parse_image(file_path: Path) -> ParseResult:
    """Extract text from a standalone image via OCR."""
    start = time.perf_counter()

    with open(file_path, "rb") as f:
        img_bytes = f.read()

    text = extract_text_ocr(img_bytes)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info("Parsed image via OCR: time=%.1fms, chars=%d", elapsed, len(text))

    return ParseResult(
        text=text,
        page_count=1,
        ocr_applied=True,
        page_texts=[text],
        parse_time_ms=elapsed,
    )


def parse_document(file_path: Path) -> ParseResult:
    """Route to the correct parser based on file extension."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
        return parse_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
