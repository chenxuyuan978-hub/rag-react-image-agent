from pathlib import Path

from app.graph.workflow import build_langgraph_workflow, run_langgraph_agent
from scripts.prepare_demo_data import prepare_demo_data


def test_build_langgraph_workflow_compiles() -> None:
    """Check that the LangGraph workflow can be built and compiled."""
    graph = build_langgraph_workflow()

    assert graph is not None


def test_run_langgraph_agent_completes_with_example_config() -> None:
    """Check that the LangGraph agent can run the full MVP workflow."""
    prepare_demo_data()

    state = run_langgraph_agent(
        task="Run Gaussian blur denoising and generate a report.",
        config_path="examples/demo_config.yaml",
        paper_dir="examples",
    )

    step_names = [step["node"] for step in state["steps"]]

    assert "retrieve_paper_context" in step_names
    assert "extract_experiment_spec" in step_names
    assert "run_experiment" in step_names
    assert "analyze_metrics" in step_names
    assert "generate_report" in step_names
    assert state["final_answer"]
    assert state["report_path"] is not None
    assert Path(state["report_path"]).is_file()
    assert state["error"] is None


def test_run_langgraph_agent_handles_empty_paper_dir() -> None:
    """Check that an empty paper directory does not crash the workflow."""
    prepare_demo_data()

    state = run_langgraph_agent(
        task="Run Gaussian blur denoising and generate a report.",
        config_path="examples/demo_config.yaml",
        paper_dir="tests/not_existing_paper_dir",
    )

    assert state["paper_context"] == []
    assert state["final_answer"]
    assert state["steps"]
