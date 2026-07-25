from __future__ import annotations

import pytest

from backend.tools.alert_tool import AlertTool
from backend.tools.health_tool import HealthTool
from backend.tools.legal_tool import LegalTool
from backend.tools.report_tool import ReportTool
from backend.tools.timeline_tool import TimelineTool


class MockAsyncSession:
    pass  # Used to bypass DB for completely simulated tools


@pytest.mark.asyncio
async def test_alert_tool_execution():
    tool = AlertTool()
    db = MockAsyncSession()
    
    # We skip validate() because it checks DB ownership, which is tested in test_tool_permissions.py
    result = await tool.execute(db, user_id="u", property_id="p")  # type: ignore
    
    assert hasattr(result, "alerts")
    assert len(result.alerts) > 0
    assert result.alerts[0]["type"] == "tax_due"


@pytest.mark.asyncio
async def test_health_tool_execution():
    tool = HealthTool()
    db = MockAsyncSession()
    
    result = await tool.execute(db, user_id="u", property_id="p")  # type: ignore
    
    assert hasattr(result, "health_score")
    assert result.health_score == 85
    assert "Unpaid Taxes" in result.risk_indicators


@pytest.mark.asyncio
async def test_legal_tool_execution():
    tool = LegalTool()
    db = MockAsyncSession()
    
    # Legal tool doesn't even require property validation
    await tool.validate(db, user_id="u", query="How to mutate?")  # type: ignore
    result = await tool.execute(db, user_id="u", query="How to mutate?")  # type: ignore
    
    assert hasattr(result, "procedures")
    assert len(result.procedures) > 0
    assert result.procedures[0]["name"] == "Mutation"


@pytest.mark.asyncio
async def test_timeline_tool_execution():
    tool = TimelineTool()
    db = MockAsyncSession()
    
    result = await tool.execute(db, user_id="u", property_id="p")  # type: ignore
    
    assert hasattr(result, "events")
    assert len(result.events) == 2


@pytest.mark.asyncio
async def test_report_tool_execution():
    tool = ReportTool()
    db = MockAsyncSession()
    
    result = await tool.execute(db, user_id="u", property_id="p")  # type: ignore
    
    assert hasattr(result, "property_summary")
    assert hasattr(result, "evidence_bundle")
    assert hasattr(result, "timeline_summary")
