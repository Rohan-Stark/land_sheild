from __future__ import annotations

import pytest

from backend.llm.prompting.builder import PromptBuilder
from backend.llm.prompting.compressor import PromptCompressor
from backend.llm.prompting.renderer import PromptRenderer
from backend.llm.prompting.validator import PromptValidator
from backend.llm.schemas.runtime import RuntimeConfig


def test_prompt_builder():
    builder = PromptBuilder()
    context = builder.build(
        user_question="What is this?",
        retrieved_chunks=[
            {"text": "A", "final_score": 0.5},
            {"text": "B", "final_score": 0.9}
        ]
    )
    
    # Check sorting by relevance
    assert context.retrieved_chunks[0]["text"] == "B"


def test_prompt_compressor_deduplication():
    compressor = PromptCompressor(max_tokens=4000)
    
    findings = [{"type": "status", "val": "active"}, {"type": "status", "val": "active"}]
    chunks = [{"text": "Hello world"}]
    
    f, c, s = compressor.compress(findings, chunks, [])
    assert len(f) == 1  # Deduplicated


def test_prompt_validator():
    validator = PromptValidator(max_prompt_tokens=4000)
    renderer = PromptRenderer(RuntimeConfig())
    builder = PromptBuilder()
    
    context = builder.build(user_question="test")
    request = renderer.render(context, intent="general_chat")
    
    errors = validator.validate(request)
    assert len(errors) == 0  # Should be valid
