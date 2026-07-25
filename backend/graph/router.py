from __future__ import annotations

from typing import Any

from backend.config.logging import get_logger
from backend.graph.registry import agent_registry
from backend.graph.state import GraphState

logger = get_logger("graph.router")


def execute_router(state: GraphState) -> dict[str, Any]:
    """Route requests to registered agents based on the execution plan.

    If an agent is required by the plan but missing in the registry,
    an error is logged and added to the state.
    """
    plan = state.get("plan")
    if not plan:
        logger.error("Router executed without an execution plan")
        return {"errors": ["No execution plan found"]}

    selected_agents: list[str] = []
    errors: list[str] = []

    for agent_name in plan.required_agents:
        agent = agent_registry.lookup(agent_name)
        if agent:
            selected_agents.append(agent.name)
        else:
            logger.warning("Required agent '%s' not found in registry", agent_name)
            errors.append(f"Agent '{agent_name}' not registered")

    logger.info("Router selected agents: %s", selected_agents)

    return {
        "selected_agents": selected_agents,
        "errors": errors,
    }
