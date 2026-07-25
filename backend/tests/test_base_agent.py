from __future__ import annotations

import pytest
from typing import Any

from backend.agents.agent_context import AgentContext
from backend.agents.agent_pipeline import AgentExecutionPipeline
from backend.agents.agent_result import AgentResult
from backend.agents.base_agent import BaseAgent
from backend.schemas.graph import IntentCategory


class DummyAgent(BaseAgent):
    """Mock agent for testing the pipeline."""
    
    @property
    def name(self) -> str:
        return "DummyAgent"

    @property
    def description(self) -> str:
        return "A dummy agent"

    @property
    def supported_intents(self) -> list[IntentCategory]:
        return [IntentCategory.DOCUMENT_QUESTION]

    @property
    def supported_entities(self) -> list[str]:
        return ["propertyId"]

    @property
    def required_tools(self) -> list[type]:
        return []

    @property
    def requires_retrieval(self) -> bool:
        return False

    @property
    def priority(self) -> int:
        return 1

    def validate(self, context: AgentContext) -> None:
        pass

    def build_execution_plan(self, context: AgentContext) -> dict[str, Any]:
        return {}

    async def process(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            agent=self.name,
            status="success",
            summary="Processed successfully"
        )

    async def post_process(self, result: AgentResult) -> AgentResult:
        result.summary += " (post-processed)"
        return result


@pytest.mark.asyncio
async def test_agent_execution_pipeline_success():
    agent = DummyAgent()
    pipeline = AgentExecutionPipeline(agent)
    
    context = AgentContext(
        requestId="123",
        userId="user_1",
        intent=IntentCategory.DOCUMENT_QUESTION
    )
    # Provide required entity
    context.entities.propertyId = "prop_1"
    
    result = await pipeline.execute(context)
    
    assert result.status == "success"
    assert result.summary == "Processed successfully (post-processed)"
    assert "total_execution_ms" in result.metrics
