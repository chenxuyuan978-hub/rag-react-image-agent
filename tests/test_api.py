from pathlib import Path

import pytest
from fastapi import HTTPException

from app.api.main import health, read_report_api, run_agent_api, run_experiment_api
from app.api.schemas import AgentRunRequest, ExperimentRunRequest
from scripts.prepare_demo_data import prepare_demo_data


def test_health_returns_ok() -> None:
    """Check the API health endpoint."""
    response = health()

    assert response.status == "ok"


def test_experiment_run_api_runs_demo_config() -> None:
    """Check that the experiment API can run the demo config."""
    prepare_demo_data()

    response = run_experiment_api(
        ExperimentRunRequest(config_path="examples/demo_config.yaml")
    )

    assert response.experiment_name == "demo_blur_experiment"
    assert response.run_id
    assert Path(response.run_dir).is_dir()
    assert Path(response.summary_path).is_file()
    assert response.metrics_path is not None
    assert Path(response.metrics_path).is_file()


def test_agent_run_api_returns_trace() -> None:
    """Check that the ReAct agent API returns a trace."""
    prepare_demo_data()

    response = run_agent_api(
        AgentRunRequest(
            task="根据论文设置运行图像处理实验并生成报告",
            config_path="examples/demo_config.yaml",
            paper_dir="examples",
        )
    )

    assert "RagRetrieveTool" in response.trace
    assert "RunExperimentTool" in response.trace
    assert "报告已生成" in response.final_answer
    assert response.run_id
    assert Path(response.run_dir).is_dir()
    assert (Path(response.run_dir) / "trace.txt").is_file()


def test_report_api_blocks_path_traversal() -> None:
    """Check that report reading blocks traversal outside data/outputs."""
    with pytest.raises(HTTPException) as error:
        read_report_api("../../README.md")

    assert error.value.status_code in {400, 404}
