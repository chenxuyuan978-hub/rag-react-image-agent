from pathlib import Path

import pytest
from fastapi import HTTPException

from app.api.main import (
    get_run_detail_api,
    get_run_summary_api,
    health,
    list_runs_api,
    read_report_api,
    run_agent_api,
    run_comparison_api,
    run_experiment_api,
)
from app.api.schemas import AgentRunRequest, ComparisonRunRequest, ExperimentRunRequest
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


def test_runs_api_returns_list() -> None:
    """Check that the run history API returns a list."""
    runs = list_runs_api()

    assert isinstance(runs, list)


def test_run_summary_api_returns_single_run() -> None:
    """Check that the run summary API returns one archived run."""
    prepare_demo_data()
    experiment_response = run_experiment_api(
        ExperimentRunRequest(config_path="examples/demo_config.yaml")
    )

    run_response = get_run_summary_api(experiment_response.run_id)

    assert run_response.run_id == experiment_response.run_id
    assert Path(run_response.run_dir).is_dir()
    assert run_response.has_summary is True


def test_run_detail_api_returns_single_run_detail() -> None:
    """Check that the run detail API returns archived run files."""
    prepare_demo_data()
    experiment_response = run_experiment_api(
        ExperimentRunRequest(config_path="examples/demo_config.yaml")
    )

    detail_response = get_run_detail_api(experiment_response.run_id)

    assert detail_response.run_id == experiment_response.run_id
    assert detail_response.summary is not None
    assert detail_response.metrics is not None
    assert detail_response.output_images


def test_comparison_run_api_runs_demo_config() -> None:
    """Check that the comparison API can run the demo comparison config."""
    prepare_demo_data()

    response = run_comparison_api(
        ComparisonRunRequest(config_path="examples/comparison_config.yaml")
    )

    assert response.comparison_name == "demo_denoising_comparison"
    assert response.run_id
    assert Path(response.run_dir).is_dir()
    assert Path(response.metrics_path).is_file()
    assert Path(response.summary_path).is_file()
