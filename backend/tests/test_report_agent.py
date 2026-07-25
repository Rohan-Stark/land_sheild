from __future__ import annotations

import pytest

from backend.agents.agent_context import AgentContext
from backend.agents.agent_pipeline import AgentExecutionPipeline
from backend.agents.report_agent import ReportAgent
from backend.schemas.graph import IntentCategory


@pytest.mark.asyncio
async def test_report_agent_success():
    agent = ReportAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="req_1",
        userId="usr_1",
        intent=IntentCategory.REPORT_REQUEST,
        retrievalResults=[
            {"chunk_id": "c1", "metadata": {"document_id": "doc1", "is_alert": False}}
        ]
    )
    context.entities.propertyId = "prop_123"
    
    result = await pipeline.execute(context)
    assert result.status == "success"
    
    # Must have the structured report layout in findings
    assert len(result.findings) == 1
    assert result.findings[0]["type"] == "structured_report"
    assert "Property Summary" in result.findings[0]["report_sections"]
