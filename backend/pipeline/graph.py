"""
LangGraph pipeline builder.
Ported from src/pipeline/graph.py with updated imports.
"""
from langgraph.graph import StateGraph, END
from backend.core.state import AgentState
from backend.core.config import AppConfig
from backend.pipeline.nodes.validation_node import validate_schema_node
from backend.pipeline.nodes.enrichment_node import enrich_metadata_node
from backend.connectors.sql_connector import SQLConnector


def extraction_node(state: AgentState):
    """Entry point: Connects to DB and gets raw schema."""
    conn_str = state["connection_string"]
    connector = SQLConnector(conn_str)
    raw_schema = connector.get_live_schema()
    return {"schema_raw": raw_schema}


def should_continue(state: AgentState):
    """Edge Logic: Decide whether to retry, finish, or error out."""
    status = state.get("validation_status", "PENDING")
    retry_count = state.get("retry_count", 0)

    # Validation passed
    if status == "PASSED":
        return "end"
    
    # Retry statuses
    if status in ["RETRY", "FAILED"]:
        if retry_count < AppConfig.MAX_RETRIES:
            return "retry"
        else:
            return "max_retries"
    
    # Terminal failure states
    if status in ["FAILED_FINAL", "FAILED_BUDGET"]:
        return "max_retries"
    
    # Default (shouldn't reach here)
    return "max_retries"


def build_pipeline():
    workflow = StateGraph(AgentState)

    workflow.add_node("extract", extraction_node)
    workflow.add_node("enrich", enrich_metadata_node)
    workflow.add_node("validate", validate_schema_node)

    workflow.set_entry_point("extract")

    workflow.add_edge("extract", "enrich")
    workflow.add_edge("enrich", "validate")

    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "end": END,
            "retry": "enrich",
            "max_retries": END,
        },
    )

    return workflow.compile()
