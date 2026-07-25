from __future__ import annotations

import pytest
from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_pipeline import AgentExecutionPipeline
from backend.agents.document_agent import DocumentAgent
from backend.agents.exceptions import AgentValidationError
from backend.schemas.graph import IntentCategory


@pytest.mark.asyncio
async def test_document_agent_missing_retrieval():
    agent = DocumentAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.DOCUMENT_QUESTION,
        retrievalResults=[]
    )
    
    result = await pipeline.execute(context)
    assert result.status == "failed"
    assert "retrieved documents" in result.summary


@pytest.mark.asyncio
async def test_document_agent_success():
    agent = DocumentAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.DOCUMENT_QUESTION,
        retrievalResults=[
            {
                "chunk_id": "c_123",
                "final_score": 0.85,
                "metadata": {"document_id": "d_123", "survey_number": "123/4"}
            }
        ]
    )
    
    result = await pipeline.execute(context)
    assert result.status == "success"
    assert len(result.sources) == 1
    assert result.sources[0].retrieval_score == 0.85
    assert result.findings[0]["extracted"]["survey_number"] == "123/4"


@pytest.mark.asyncio
async def test_document_agent_forbidden_phrase_filter():
    agent = DocumentAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.DOCUMENT_QUESTION,
        retrievalResults=[
            {
                "chunk_id": "c_123",
                "final_score": 0.9,
                "metadata": {"document_id": "d_123"}
            }
        ]
    )
    
    # We must patch the process output to simulate an LLM saying something forbidden
    # Since we aren't using an LLM, we can just call post_process manually to test it
    result = await agent.process(context)
    result.summary = "The user owns the property."
    
    final_result = await agent.post_process(result)
    assert any("owns the property" in w for w in final_result.warnings)
