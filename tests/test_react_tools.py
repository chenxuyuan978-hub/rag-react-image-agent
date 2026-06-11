import csv
import json
import shutil
from pathlib import Path

import numpy as np

from app.experiments.experiment_runner import save_image
from app.react.tools import (
    AnalyzeMetricsTool,
    GenerateReportTool,
    RagRetrieveTool,
    RunExperimentTool,
)


def make_react_temp_dir() -> Path:
    """Create a clean workspace-local directory for ReAct tool tests."""
    temp_dir = Path("tests") / "_react_tools_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    return temp_dir


def make_image() -> np.ndarray:
    """Create a small RGB image for experiment tool tests."""
    image = np.full((16, 16, 3), 120, dtype=np.uint8)
    image[4:10, 4:10] = [160, 90, 70]
    return image


def write_metrics(path: Path) -> None:
    """Write a metrics CSV file for tool tests."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerow({"metric": "mse", "value": "2.5"})
        writer.writerow({"metric": "psnr", "value": "34.2"})
        writer.writerow({"metric": "ssim", "value": "0.95"})


def write_summary(path: Path, metrics_path: Path) -> None:
    """Write a summary JSON file for report tool tests."""
    summary = {
        "experiment_name": "react_tool_report",
        "output_dir": str(path.parent),
        "output_images": [str(path.parent / "step_01_gaussian_blur.png")],
        "metrics_path": str(metrics_path),
        "summary_path": str(path),
    }
    path.write_text(json.dumps(summary), encoding="utf-8")


def test_rag_retrieve_tool_returns_results() -> None:
    temp_dir = make_react_temp_dir()
    paper_dir = temp_dir / "papers"
    paper_dir.mkdir()

    try:
        (paper_dir / "demo.md").write_text(
            "The experiment setting uses Gaussian blur with kernel size 5. PSNR and SSIM are measured.",
            encoding="utf-8",
        )

        result = RagRetrieveTool().run(
            {"query": "Gaussian blur PSNR", "paper_dir": str(paper_dir), "top_k": 1}
        )

        assert result["success"] is True
        assert len(result["results"]) == 1
        assert "Gaussian blur" in result["results"][0]["text"]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_run_experiment_tool_runs_config() -> None:
    temp_dir = make_react_temp_dir()
    input_path = temp_dir / "input.png"
    reference_path = temp_dir / "reference.png"
    config_path = temp_dir / "config.yaml"
    output_dir = temp_dir / "outputs"

    try:
        save_image(str(input_path), make_image())
        save_image(str(reference_path), make_image())
        config_path.write_text(
            "\n".join(
                [
                    "experiment_name: react_tool_experiment",
                    f"input_image: {input_path.as_posix()}",
                    f"reference_image: {reference_path.as_posix()}",
                    "operations:",
                    "  - name: gaussian_blur",
                    "    params:",
                    "      kernel_size: 3",
                    "metrics:",
                    "  - mse",
                    "  - psnr",
                    "  - ssim",
                    f"output_dir: {output_dir.as_posix()}",
                ]
            ),
            encoding="utf-8",
        )

        result = RunExperimentTool().run({"config_path": str(config_path)})

        assert result["success"] is True
        assert result["experiment_name"] == "react_tool_experiment"
        assert Path(result["summary_path"]).is_file()
        assert Path(result["metrics_path"]).is_file()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_analyze_metrics_tool_reads_metrics_csv() -> None:
    temp_dir = make_react_temp_dir()
    metrics_path = temp_dir / "metrics.csv"

    try:
        write_metrics(metrics_path)

        result = AnalyzeMetricsTool().run({"metrics_path": str(metrics_path)})

        assert result["success"] is True
        assert "PSNR" in result["analysis"]
        assert "SSIM" in result["analysis"]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_report_tool_generates_report() -> None:
    temp_dir = make_react_temp_dir()
    metrics_path = temp_dir / "metrics.csv"
    summary_path = temp_dir / "summary.json"
    report_path = temp_dir / "report.md"

    try:
        write_metrics(metrics_path)
        write_summary(summary_path, metrics_path)

        result = GenerateReportTool().run(
            {
                "summary_path": str(summary_path),
                "metrics_path": str(metrics_path),
                "paper_context": ["Gaussian blur reports PSNR and SSIM."],
                "output_path": str(report_path),
            }
        )

        assert result["success"] is True
        assert Path(result["report_path"]).is_file()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_tool_error_input_returns_success_false() -> None:
    result = RagRetrieveTool().run({"query": "", "paper_dir": "missing_dir"})

    assert result["success"] is False
    assert "error" in result
