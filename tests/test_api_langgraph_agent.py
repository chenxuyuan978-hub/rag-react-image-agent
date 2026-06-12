from fastapi.testclient import TestClient

from app.api.main import app
from scripts.prepare_demo_data import prepare_demo_data

client = TestClient(app)


def test_langgraph_agent_api_runs_successfully() -> None:
    """Check that the LangGraph Agent API runs the normal workflow."""
    prepare_demo_data()

    response = client.post(
        "/api/agent/langgraph/run",
        json={
            "task": "Run Gaussian blur denoising and generate a report.",
            "config_path": "examples/demo_config.yaml",
            "paper_dir": "examples",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    step_names = [step["node"] for step in payload["steps"]]

    assert "final_answer" in payload
    assert "steps" in payload
    assert "error" in payload
    assert "diagnosis" in payload
    assert "retrieve_paper_context" in step_names
    assert "extract_experiment_spec" in step_names
    assert "run_experiment" in step_names
    assert payload["error"] is None
    assert payload["diagnosis"] is None
    assert payload["paper_context_count"] >= 0


def test_langgraph_agent_api_returns_error_state_for_missing_config() -> None:
    """Check missing config returns structured workflow error JSON."""
    response = client.post(
        "/api/agent/langgraph/run",
        json={
            "task": "Run an experiment with a missing config.",
            "config_path": "examples/not_exists.yaml",
            "paper_dir": "examples",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    step_names = [step["node"] for step in payload["steps"]]

    assert payload["error"] or payload["diagnosis"]
    assert payload["diagnosis"] is not None
    assert payload["error_type"] in {"config_error", "file_not_found"}
    assert "run_experiment" in step_names
    assert "diagnose_error" in step_names
