from __future__ import annotations

import pytest

from backend.agents.agent_context import AgentContext
from backend.agents.agent_pipeline import AgentExecutionPipeline
from backend.agents.property_agent import PropertyAgent
from backend.schemas.graph import IntentCategory


@pytest.mark.asyncio
async def test_property_agent_missing_property_id():
    agent = PropertyAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.PROPERTY_QUESTION,
        retrievalResults=[{"chunk_id": "c1"}]
    )
    
    result = await pipeline.execute(context)
    assert result.status == "failed"
    assert "propertyId" in result.summary


@pytest.mark.asyncio
async def test_property_agent_health_score():
    agent = PropertyAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.PROPERTY_QUESTION,
        retrievalResults=[
            {"chunk_id": "c_123", "text": "This property has an active alert due to dispute."},
            {"chunk_id": "c_124", "text": "Another alert for unpaid taxes."}
        ]
    )
    context.entities.propertyId = "prop_123"
    
    result = await pipeline.execute(context)
    assert result.status == "success"
    
    # 2 alerts = risk score of 2, 100 - 40 = 60
    assert "60/100" in result.summary
    assert len(result.warnings) == 2
