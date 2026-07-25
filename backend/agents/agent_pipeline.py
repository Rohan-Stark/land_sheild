from __future__ import annotations

import time

from backend.agents.agent_context import AgentContext
from backend.agents.agent_result import AgentResult
from backend.agents.base_agent import BaseAgent
from backend.agents.validation import validate_context, validate_retrieval, validate_tools


class AgentExecutionPipeline:
    """The standardized pipeline wrapper for running any concrete agent."""

    def __init__(self, agent: BaseAgent) -> None:
        self.agent = agent

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the universal agent lifecycle.
        
        Lifecycle:
        1. Base validation
        2. Agent-specific validation
        3. Build execution plan
        4. Run business logic (process)
        5. Post-process
        """
        start = time.perf_counter()
        
        try:
            # 1. Base Validation
            validate_context(context, self.agent.supported_entities)
            validate_retrieval(context, self.agent.requires_retrieval)
            validate_tools(context, self.agent.required_tools)
            
            # 2. Agent-Specific Validation
            self.agent.validate(context)
            
            # 3. Plan (optional usage by the agent during processing)
            _ = self.agent.build_execution_plan(context)
            
            # 4. Business Logic
            result = await self.agent.process(context)
            
            # 5. Post Processing
            final_result = await self.agent.post_process(result)
            
            # Automatic metrics
            elapsed = (time.perf_counter() - start) * 1000
            final_result.metrics["total_execution_ms"] = elapsed
            
            return final_result
            
        except Exception as exc:
            # Automatic error formatting
            elapsed = (time.perf_counter() - start) * 1000
            return AgentResult(
                agent=self.agent.name,
                status="failed",
                summary=f"Pipeline execution failed: {str(exc)}",
                warnings=[str(exc)],
                metrics={"total_execution_ms": elapsed}
            )
