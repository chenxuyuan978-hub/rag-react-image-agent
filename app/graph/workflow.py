from typing import Any

from langgraph.graph import END, StateGraph

from app.graph.error_handling import should_retry
from app.graph.nodes import (
    analyze_metrics_node,
    diagnose_error_node,
    extract_experiment_spec_node,
    generate_report_node,
    retrieve_paper_context_node,
    retry_failed_step_node,
    run_experiment_node,
)
from app.graph.state import GraphAgentState
from app.observability.langsmith_config import configure_langsmith_environment


def _route_after_run_experiment(state: GraphAgentState) -> str:
    """Route after run_experiment based on workflow error state."""
    return "diagnose_error" if state.get("error") else "analyze_metrics"


def _route_after_analyze_metrics(state: GraphAgentState) -> str:
    """Route after analyze_metrics based on workflow error state."""
    return "diagnose_error" if state.get("error") else "generate_report"


def _route_after_generate_report(state: GraphAgentState) -> str:
    """Route after generate_report based on workflow error state."""
    return "diagnose_error" if state.get("error") else END


def _route_after_diagnosis(state: GraphAgentState) -> str:
    """Route after diagnosis to retry run_experiment once when appropriate."""
    diagnosis = state.get("diagnosis") or {}
    can_retry = should_retry(
        diagnosis=diagnosis,
        retry_count=state.get("retry_count", 0),
        max_retries=state.get("max_retries", 1),
    )
    if can_retry and state.get("failed_node") == "run_experiment":
        return "retry_failed_step"
    return END


def build_langgraph_workflow() -> Any:
    """Build and compile the LangGraph image experiment workflow."""
    workflow = StateGraph(GraphAgentState)
    workflow.add_node("retrieve_paper_context", retrieve_paper_context_node)
    workflow.add_node("extract_experiment_spec", extract_experiment_spec_node)
    workflow.add_node("run_experiment", run_experiment_node)
    workflow.add_node("analyze_metrics", analyze_metrics_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("diagnose_error", diagnose_error_node)
    workflow.add_node("retry_failed_step", retry_failed_step_node)

    workflow.set_entry_point("retrieve_paper_context")
    workflow.add_edge("retrieve_paper_context", "extract_experiment_spec")
    workflow.add_edge("extract_experiment_spec", "run_experiment")
    workflow.add_conditional_edges(
        "run_experiment",
        _route_after_run_experiment,
        {"analyze_metrics": "analyze_metrics", "diagnose_error": "diagnose_error"},
    )
    workflow.add_conditional_edges(
        "analyze_metrics",
        _route_after_analyze_metrics,
        {"generate_report": "generate_report", "diagnose_error": "diagnose_error"},
    )
    workflow.add_conditional_edges(
        "generate_report",
        _route_after_generate_report,
        {"diagnose_error": "diagnose_error", END: END},
    )
    workflow.add_conditional_edges(
        "diagnose_error",
        _route_after_diagnosis,
        {"retry_failed_step": "retry_failed_step", END: END},
    )
    workflow.add_edge("retry_failed_step", "run_experiment")

    return workflow.compile()


def run_langgraph_agent(
    task: str,
    config_path: str,
    paper_dir: str = "data/papers",
) -> GraphAgentState:
    """Run the LangGraph workflow and return the final state."""
    langsmith_tracing_enabled = configure_langsmith_environment()
    initial_state: GraphAgentState = {
        "task": task,
        "config_path": config_path,
        "paper_dir": paper_dir,
        "paper_context": [],
        "extracted_spec": None,
        "experiment_result": None,
        "metrics_analysis": None,
        "report_path": None,
        "final_answer": None,
        "error": None,
        "error_type": None,
        "diagnosis": None,
        "retry_count": 0,
        "max_retries": 1,
        "failed_node": None,
        "steps": [
            {
                "node": "configure_langsmith",
                "status": "ok",
                "detail": (
                    "LangSmith tracing enabled."
                    if langsmith_tracing_enabled
                    else "LangSmith tracing disabled."
                ),
                "data": {"langsmith_tracing_enabled": langsmith_tracing_enabled},
            }
        ],
    }
    return build_langgraph_workflow().invoke(initial_state)
