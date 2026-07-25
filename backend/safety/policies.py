from __future__ import annotations

from typing import Callable

from backend.llm.schemas.response import FinalResponse

# A Policy is a function that takes a response and returns an error string if violated, or None if safe
SafetyPolicy = Callable[[FinalResponse], str | None]


def policy_no_legal_determination(response: FinalResponse) -> str | None:
    text = response.content.lower()
    forbidden = [
        "is the legal owner",
        "legally owns",
        "court will decide",
        "you will win",
        "guaranteed to be",
    ]
    for phrase in forbidden:
        if phrase in text:
            return f"Policy Violation: Response attempts to determine legal ownership or outcomes ('{phrase}')."
    return None


def policy_no_fraud_declaration(response: FinalResponse) -> str | None:
    text = response.content.lower()
    forbidden = [
        "this is fraud",
        "fraudulent document",
        "is a scam",
    ]
    for phrase in forbidden:
        if phrase in text:
            return f"Policy Violation: Response attempts to declare fraud ('{phrase}')."
    return None


def policy_requires_disclaimer(response: FinalResponse) -> str | None:
    # Only enforce on Legal Agent responses
    if response.agent != "LegalGuidanceAgent":
        return None
        
    text = response.content.lower()
    if "educational purposes only" not in text and "not legal advice" not in text:
        return "Policy Violation: Legal response missing mandatory educational disclaimer."
    return None


DEFAULT_POLICIES: list[SafetyPolicy] = [
    policy_no_legal_determination,
    policy_no_fraud_declaration,
    policy_requires_disclaimer
]
