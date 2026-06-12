from typing import Any

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    analyze_metrics_node,
    extract_experiment_spec_node,
    generate_report_node,
    retrieve_paper_context_node,
    run_experiment_node,
)
from app.graph.state import GraphAgentState


def build_langgraph_workflow() -> Any:
    """Build and compile the LangGraph image experiment workflow."""
    workflow = StateGraph(GraphAgentState)
    workflow.add_node("retrieve_paper_context", retrieve_paper_context_node)
    workflow.add_node("extract_experiment_spec", extract_experiment_spec_node)
    workflow.add_node("run_experiment", run_experiment_node)
    workflow.add_node("analyze_metrics", analyze_metrics_node)
    workflow.add_node("generate_report", generate_report_node)

    workflow.set_entry_point("retrieve_paper_context")
    workflow.add_edge("retrieve_paper_context", "extract_experiment_spec")
    workflow.add_edge("extract_experiment_spec", "run_experiment")
    workflow.add_edge("run_experiment", "analyze_metrics")
    workflow.add_edge("analyze_metrics", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()


def run_langgraph_agent(
    task: str,
    config_path: str,
    paper_dir: str = "data/papers",
) -> GraphAgentState:
    """Run the LangGraph workflow and return the final state."""
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
        "steps": [],
    }
    return build_langgraph_workflow().invoke(initial_state)
