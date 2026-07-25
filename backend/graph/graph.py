from __future__ import annotations

import re
from typing import Any

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.logging import get_logger
from backend.graph.executor import execute_tools
from backend.graph.planner import execute_planner
from backend.graph.router import execute_router
from backend.graph.state import GraphState
from backend.schemas.graph import ExtractedEntities, IntentCategory, OrchestrationResponse

logger = get_logger("graph.main")


# ── Internal Nodes ────────────────────────────────────────────────────────────

def parse_request(state: GraphState) -> dict[str, Any]:
    """Parse the raw query and extract basic deterministic entities (Step 3)."""
    query = state["query"].lower()
    entities = ExtractedEntities()

    # Naive Phase 2A deterministic entity extraction (to be replaced by LLM)
    survey_match = re.search(r'survey\s*(?:no\.?|number)?\s*(\d+[a-z/]*)', query)
    if survey_match:
        entities.surveyNumber = survey_match.group(1)

    khata_match = re.search(r'khata\s*(?:no\.?|number)?\s*(\d+[a-z/]*)', query)
    if khata_match:
        entities.khataNumber = khata_match.group(1)
        
    if "inspection" in query or "report" in query:
        entities.documentType = "inspection"
    elif "alert" in query:
        entities.documentType = "alert"

    return {"entities": entities, "execution_history": ["parse_request"]}


def classify_intent(state: GraphState) -> dict[str, Any]:
    """Classify the intent using deterministic rules (Step 2)."""
    query = state["query"].lower()
    intent = IntentCategory.UNKNOWN

    if "survey" in query or "khata" in query or "owner" in query:
        intent = IntentCategory.PROPERTY_QUESTION
    elif "alert" in query or "warning" in query or "dispute" in query:
        intent = IntentCategory.ALERT_QUESTION
    elif "inspection" in query or "visit" in query:
        intent = IntentCategory.INSPECTION_QUESTION
    elif "report" in query or "generate" in query:
        intent = IntentCategory.REPORT_REQUEST
    elif "legal" in query or "law" in query or "guidance" in query:
        intent = IntentCategory.LEGAL_GUIDANCE
    elif "document" in query or "deed" in query or "read" in query:
        intent = IntentCategory.DOCUMENT_QUESTION
    elif "what is" in query or "how to" in query:
        intent = IntentCategory.GENERAL_KNOWLEDGE

    return {"intent": intent, "execution_history": ["classify_intent"]}


# Note: planner node uses `execute_planner` from planner.py
# Note: router node uses `execute_router` from router.py


async def execute_tool_node(state: GraphState, db: AsyncSession) -> dict[str, Any]:
    """Wrapper node for executing tools via the executor."""
    result = await execute_tools(state, db)
    if result:
        result["execution_history"] = ["execute_tools"]
    return result


def aggregate_response(state: GraphState) -> dict[str, Any]:
    """Aggregate all state into a final OrchestrationResponse format (Step 10)."""
    # Since we can't return an OrchestrationResponse directly into the StateGraph dict,
    # we just update the metadata or prepare the final outputs. 
    # The actual response is built after the graph finishes.
    return {"execution_history": ["aggregate_response"]}


# ── Edge Routers ────────────────────────────────────────────────────────────

def route_after_planner(state: GraphState) -> str:
    """Conditional edge: if no agents are required, skip router and tools."""
    plan = state.get("plan")
    if not plan or not plan.required_agents:
        return "aggregate"
    return "router"


# ── Graph Construction ────────────────────────────────────────────────────────

def build_orchestration_graph() -> StateGraph:
    """Construct the LangGraph orchestration state machine."""
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("parser", parse_request)
    workflow.add_node("classifier", classify_intent)
    workflow.add_node("planner", execute_planner)
    workflow.add_node("router", execute_router)
    
    # We use a dummy wrapper for the tool node so we can inject the DB session at runtime
    # See `run_orchestration` for how this is handled.
    async def tool_wrapper(state: GraphState, **kwargs: Any) -> dict[str, Any]:
        db = kwargs.get("db")
        if not db:
            raise ValueError("DB session required for tool execution")
        return await execute_tool_node(state, db)
        
    # LangGraph allows async nodes
    workflow.add_node("tools", tool_wrapper)
    workflow.add_node("aggregate", aggregate_response)

    # Add Edges
    workflow.add_edge(START, "parser")
    workflow.add_edge("parser", "classifier")
    workflow.add_edge("classifier", "planner")
    
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {"router": "router", "aggregate": "aggregate"}
    )
    
    workflow.add_edge("router", "tools")
    workflow.add_edge("tools", "aggregate")
    workflow.add_edge("aggregate", END)

    return workflow.compile()


# Singleton compiled graph
orchestrator = build_orchestration_graph()


async def run_orchestration(
    request: dict[str, Any], db: AsyncSession
) -> OrchestrationResponse:
    """Entry point to invoke the LangGraph orchestration layer."""
    # Initialize state
    initial_state = {
        "requestId": request.get("requestId", ""),
        "userId": request.get("userId", ""),
        "propertyId": request.get("propertyId"),
        "conversationId": request.get("conversationId"),
        "query": request.get("query", ""),
        "intent": IntentCategory.UNKNOWN,
        "entities": ExtractedEntities(),
        "selected_agents": [],
        "tool_calls": [],
        "agent_outputs": [],
        "retrieved_context": [],
        "execution_history": [],
        "errors": [],
        "metadata": {},
    }

    try:
        # We pass DB session via kwargs to the nodes that need it
        final_state = await orchestrator.ainvoke(initial_state, {"db": db})
    except Exception as exc:
        logger.error("Orchestration failed catastrophically: %s", exc)
        # Fallback error state
        final_state = initial_state
        final_state["errors"].append(str(exc))

    # Build the final structured response (Step 10)
    return OrchestrationResponse(
        requestId=final_state["requestId"],
        intent=final_state["intent"],
        agent_outputs={"raw_state_outputs": final_state["agent_outputs"]},
        tool_results={"invocations": final_state["tool_calls"]},
        retrieval_results={"context": final_state["retrieved_context"]},
        confidence_placeholders={"semantic_match": 0.0, "intent_confidence": 1.0},
        errors=final_state["errors"],
        metadata={"history": final_state["execution_history"]},
    )
