import shutil
from pathlib import Path

import numpy as np

from app.experiments.experiment_runner import save_image
from app.react.agent import ReActAgent


def make_agent_temp_dir() -> Path:
    """Create a clean workspace-local directory for ReAct agent tests."""
    temp_dir = Path("tests") / "_react_agent_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    return temp_dir


def make_image() -> np.ndarray:
    """Create a small RGB image for ReAct agent tests."""
    image = np.full((16, 16, 3), 130, dtype=np.uint8)
    image[3:9, 3:9] = [170, 80, 90]
    return image


def write_config(
    config_path: Path, input_path: Path, reference_path: Path, output_dir: Path
) -> None:
    """Write a minimal experiment YAML config for agent tests."""
    config_path.write_text(
        "\n".join(
            [
                "experiment_name: react_agent_experiment",
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


def test_react_agent_can_run_full_workflow() -> None:
    temp_dir = make_agent_temp_dir()
    paper_dir = temp_dir / "papers"
    paper_dir.mkdir()
    input_path = temp_dir / "input.png"
    reference_path = temp_dir / "reference.png"
    config_path = temp_dir / "config.yaml"
    output_dir = temp_dir / "outputs"

    try:
        (paper_dir / "demo.md").write_text(
            "The experiment setting applies Gaussian blur with kernel size 5 and reports PSNR, SSIM, and MSE.",
            encoding="utf-8",
        )
        save_image(str(input_path), make_image())
        save_image(str(reference_path), make_image())
        write_config(config_path, input_path, reference_path, output_dir)

        trace = ReActAgent().run(
            task="run Gaussian blur reproduction and generate report",
            config_path=str(config_path),
            paper_dir=str(paper_dir),
        )
        trace_text = trace.to_text()

        assert len(trace.steps) >= 4
        assert "RagRetrieveTool" in trace_text
        assert "RunExperimentTool" in trace_text
        assert "报告已生成" in trace.final_answer
        assert (output_dir / "report.md").is_file()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_react_agent_stops_when_tool_fails() -> None:
    trace = ReActAgent().run(
        task="run impossible task",
        config_path="missing_config.yaml",
        paper_dir="missing_papers",
    )

    assert len(trace.steps) == 1
    assert trace.steps[0].action == "RagRetrieveTool"
    assert trace.steps[0].observation["success"] is False
    assert "任务失败" in trace.final_answer
