from __future__ import annotations

import pytest

from backend.llm.schemas.response import FinalResponse
from backend.safety.validator import SafetyValidator


def test_safety_validator_legal_ownership():
    validator = SafetyValidator()
    
    response = FinalResponse(content="Based on the documents, John is the legal owner.")
    violations = validator.validate(response)
    
    assert len(violations) == 1
    assert "determine legal ownership" in violations[0]


def test_safety_validator_fraud():
    validator = SafetyValidator()
    
    response = FinalResponse(content="This document is a scam and this is fraud.")
    violations = validator.validate(response)
    
    assert len(violations) == 1
    assert "declare fraud" in violations[0]


def test_safety_validator_disclaimer():
    validator = SafetyValidator()
    
    # Missing disclaimer on legal agent
    response1 = FinalResponse(
        agent="LegalGuidanceAgent",
        content="Here are the mutation steps."
    )
    violations1 = validator.validate(response1)
    assert len(violations1) == 1
    assert "missing mandatory educational disclaimer" in violations1[0]
    
    # Has disclaimer
    response2 = FinalResponse(
        agent="LegalGuidanceAgent",
        content="Here are the steps. This is for educational purposes only."
    )
    violations2 = validator.validate(response2)
    assert len(violations2) == 0
