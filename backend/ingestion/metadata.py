from __future__ import annotations

import re
from typing import Any

from backend.config.logging import get_logger

logger = get_logger("ingestion.metadata")

# ── Regex patterns for Indian land document fields ──────────────────────────

_PATTERNS: dict[str, re.Pattern[str]] = {
    "survey_number": re.compile(
        r"(?:survey\s*(?:no\.?|number)[:\s]*|sy\.?\s*no\.?[:\s]*)([A-Za-z0-9/\-]+)",
        re.IGNORECASE,
    ),
    "registration_number": re.compile(
        r"(?:registration\s*(?:no\.?|number)[:\s]*|reg\.?\s*no\.?[:\s]*)([A-Za-z0-9/\-]+)",
        re.IGNORECASE,
    ),
    "khata_number": re.compile(
        r"(?:khata\s*(?:no\.?|number)[:\s]*|kh\.?\s*no\.?[:\s]*)([A-Za-z0-9/\-]+)",
        re.IGNORECASE,
    ),
    "district": re.compile(
        r"(?:district|dist\.?)[:\s]+([A-Za-z\s]{2,40})",
        re.IGNORECASE,
    ),
    "state": re.compile(
        r"(?:state)[:\s]+([A-Za-z\s]{2,30})",
        re.IGNORECASE,
    ),
}

_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b"
    r"|"
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
    re.IGNORECASE,
)

_OWNER_PATTERN = re.compile(
    r"(?:owner|name\s*of\s*owner|proprietor|sold\s*by|purchased\s*by|buyer|seller)"
    r"[:\s]+([A-Z][a-zA-Z\s\.]{2,60})",
    re.IGNORECASE,
)

_ADDRESS_PATTERN = re.compile(
    r"(?:property\s*address|address|situated\s*at|located\s*at)"
    r"[:\s]+(.+?)(?:\n|$)",
    re.IGNORECASE,
)


def extract_metadata(text: str) -> dict[str, Any]:
    """Extract structured metadata fields from document text using regex patterns.

    Returns a dictionary with keys:
        survey_number, registration_number, khata_number, district, state,
        dates, owner_names, property_address
    """
    result: dict[str, Any] = {}

    # Single-value fields
    for field_name, pattern in _PATTERNS.items():
        match = pattern.search(text)
        if match:
            result[field_name] = match.group(1).strip()

    # Dates — collect all occurrences
    date_matches = _DATE_PATTERN.findall(text)
    dates: list[str] = []
    for groups in date_matches:
        for g in groups:
            if g:
                dates.append(g.strip())
    if dates:
        result["dates"] = list(dict.fromkeys(dates))[:10]  # deduplicate, cap at 10

    # Owner names
    owner_matches = _OWNER_PATTERN.findall(text)
    if owner_matches:
        owners = [name.strip().rstrip(".") for name in owner_matches]
        result["owner_names"] = list(dict.fromkeys(owners))[:5]

    # Property address
    addr_match = _ADDRESS_PATTERN.search(text)
    if addr_match:
        result["property_address"] = addr_match.group(1).strip()

    field_count = len([v for v in result.values() if v])
    logger.info("Metadata extraction: %d fields found", field_count)

    return result
