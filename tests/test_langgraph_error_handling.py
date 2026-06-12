from app.graph.error_handling import (
    build_error_diagnosis,
    classify_error,
    should_retry,
)
from app.graph.nodes import diagnose_error_node
from app.graph.workflow import run_langgraph_agent
from scripts.prepare_demo_data import prepare_demo_data


def _make_error_state() -> dict:
    """Create a minimal graph state containing an error."""
    return {
        "task": "demo",
        "config_path": "missing.yaml",
        "paper_dir": "data/papers",
        "paper_context": [],
        "extracted_spec": None,
        "experiment_result": None,
        "metrics_analysis": None,
        "report_path": None,
        "final_answer": None,
        "error": "Config file not found: missing.yaml",
        "error_type": None,
        "diagnosis": None,
        "retry_count": 0,
        "max_retries": 1,
        "failed_node": "run_experiment",
        "steps": [],
    }


def test_classify_error_file_not_found() -> None:
    """Check file-not-found error classification."""
    assert classify_error("Input image file not found") == "file_not_found"


def test_classify_error_config_error() -> None:
    """Check config error classification."""
    assert classify_error("Invalid YAML config_path") == "config_error"


def test_classify_error_metrics_error() -> None:
    """Check metrics error classification."""
    assert classify_error("metrics.csv could not be read") == "metrics_error"


def test_build_error_diagnosis_returns_stable_dict() -> None:
    """Check diagnosis contains stable fields for downstream display."""
    diagnosis = build_error_diagnosis(
        "metrics.csv could not be read",
        failed_node="analyze_metrics",
        retry_count=0,
    )

    assert diagnosis["error_type"] == "metrics_error"
    assert "suggested_action" in diagnosis
    assert "retryable" in diagnosis


def test_should_retry_when_retryable_and_under_limit() -> None:
    """Check retry is allowed when retryable and under max_retries."""
    diagnosis = {"retryable": True}

    assert should_retry(diagnosis, retry_count=0, max_retries=1) is True


def test_should_retry_false_when_limit_reached() -> None:
    """Check retry is blocked after reaching max_retries."""
    diagnosis = {"retryable": True}

    assert should_retry(diagnosis, retry_count=1, max_retries=1) is False


def test_diagnose_error_node_writes_diagnosis() -> None:
    """Check diagnose_error_node writes diagnosis and error_type."""
    result = diagnose_error_node(_make_error_state())

    assert result["diagnosis"]["error_type"] == "config_error"
    assert result["error_type"] == "config_error"
    assert result["steps"][0]["node"] == "diagnose_error"


def test_langgraph_workflow_returns_error_state_for_bad_config() -> None:
    """Check workflow returns structured error state instead of crashing."""
    state = run_langgraph_agent(
        task="Run Gaussian blur denoising and generate a report.",
        config_path="tests/not_existing_config.yaml",
        paper_dir="tests/not_existing_paper_dir",
    )

    assert state["error"]
    assert state["diagnosis"] is not None
    assert state["failed_node"] == "run_experiment"
    assert any(step["node"] == "diagnose_error" for step in state["steps"])


def test_langgraph_normal_workflow_still_completes() -> None:
    """Check normal workflow still succeeds after adding error handling."""
    prepare_demo_data()

    state = run_langgraph_agent(
        task="Run Gaussian blur denoising and generate a report.",
        config_path="examples/demo_config.yaml",
        paper_dir="examples",
    )

    assert state["error"] is None
    assert state["diagnosis"] is None
    assert state["final_answer"]
    assert any(step["node"] == "generate_report" for step in state["steps"])
