from __future__ import annotations

import pytest

from backend.agents.agent_context import AgentContext
from backend.agents.agent_pipeline import AgentExecutionPipeline
from backend.agents.legal_agent import LegalGuidanceAgent
from backend.schemas.graph import IntentCategory


@pytest.mark.asyncio
async def test_legal_agent_mandatory_disclaimer():
    agent = LegalGuidanceAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.LEGAL_GUIDANCE,
        retrievalResults=[{"chunk_id": "c1", "metadata": {"document_id": "doc1"}}]
    )
    
    result = await pipeline.execute(context)
    assert result.status == "success"
    
    # Must contain the disclaimer in summary and warnings
    disclaimer = "educational only and should not be considered legal advice"
    assert disclaimer in result.summary
    assert any(disclaimer in w for w in result.warnings)
