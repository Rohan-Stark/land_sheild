from __future__ import annotations

import re

from backend.config.logging import get_logger
from backend.llm.schemas.response import FinalResponse

logger = get_logger("trust.hallucination")


class HallucinationDetector:
    """Deterministically detects hallucinations in LLM output.

    Strategy:
    Uses regex to extract explicit identifiers (Survey Numbers, Registration Numbers)
    from the LLM text. If these numbers exist in the text but NOT in the provided 
    raw evidence pool, the LLM hallucinated them.
    """

    @staticmethod
    def detect(response: FinalResponse, evidence_texts: list[str]) -> list[str]:
        """Return a list of detected hallucinated claims. Empty if clean."""
        hallucinations: list[str] = []
        
        # Combine all valid evidence text for fast substring matching
        valid_corpus = " ".join(evidence_texts).lower()

        text = response.content.lower()

        # Extract Survey Numbers (e.g., "Survey No. 123", "Survey 45A")
        survey_matches = re.findall(r"survey (?:no\.? )?([a-z0-9/]+)", text)
        for num in survey_matches:
            if num not in valid_corpus:
                hallucinations.append(f"Invented Survey Number: {num}")

        # Extract Registration Numbers (e.g., "Reg 9876", "Registration No. 543")
        reg_matches = re.findall(r"reg(?:istration)? (?:no\.? )?([0-9]{4,})", text)
        for num in reg_matches:
            if num not in valid_corpus:
                hallucinations.append(f"Invented Registration Number: {num}")

        if hallucinations:
            logger.warning("Hallucinations detected: %s", hallucinations)

        return hallucinations
