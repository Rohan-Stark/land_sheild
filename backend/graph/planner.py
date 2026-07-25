from __future__ import annotations

from backend.config.logging import get_logger
from backend.graph.state import GraphState
from backend.schemas.graph import ExecutionPlan, IntentCategory

logger = get_logger("graph.planner")


def execute_planner(state: GraphState) -> dict[str, ExecutionPlan]:
    """Determine the execution plan based on intent and entities.

    In Phase 2A, this uses deterministic rule-based logic.
    It decides if retrieval is required, if tools are needed, and which agents 
    should logically handle the request type.
    """
    intent = state.get("intent", IntentCategory.UNKNOWN)
    plan = ExecutionPlan(intent=intent)

    logger.info("Executing planner for intent: %s", intent)

    if intent == IntentCategory.DOCUMENT_QUESTION:
        plan.requires_retrieval = True
        plan.requires_tools = True
        plan.required_agents = ["DocumentAgent"]

    elif intent == IntentCategory.PROPERTY_QUESTION:
        plan.requires_retrieval = True
        plan.requires_tools = True
        plan.required_agents = ["PropertyAgent"]

    elif intent == IntentCategory.LEGAL_GUIDANCE:
        plan.requires_retrieval = True
        plan.requires_tools = True
        plan.required_agents = ["LegalAgent"]

    elif intent == IntentCategory.ALERT_QUESTION:
        plan.requires_retrieval = True
        plan.required_agents = ["AlertAgent"]

    elif intent == IntentCategory.INSPECTION_QUESTION:
        plan.requires_retrieval = True
        plan.required_agents = ["ReportAgent"]

    elif intent == IntentCategory.REPORT_REQUEST:
        plan.requires_retrieval = True
        plan.requires_tools = True
        plan.required_agents = ["ReportAgent"]

    elif intent == IntentCategory.GENERAL_KNOWLEDGE:
        plan.requires_retrieval = False
        plan.required_agents = ["GeneralAgent"]

    else:
        plan.requires_retrieval = False
        plan.required_agents = ["RouterAgent"]

    # Check for multi-agent collaboration triggers
    # If multiple entity types exist, we might need parallel agents.
    entities = state.get("entities")
    if entities:
        if entities.documentType and entities.alertId:
            plan.parallel_execution = True
            if "AlertAgent" not in plan.required_agents:
                plan.required_agents.append("AlertAgent")
            if "DocumentAgent" not in plan.required_agents:
                plan.required_agents.append("DocumentAgent")

    logger.info(
        "Planner generated plan: %s agents, retrieval=%s",
        plan.required_agents, plan.requires_retrieval
    )

    return {"plan": plan}
