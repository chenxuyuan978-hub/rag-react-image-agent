import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from app.experiments.config_schema import ExperimentConfig, OperationConfig
from app.experiments.experiment_runner import run_experiment, save_image


def make_runner_temp_dir() -> Path:
    """Create a clean workspace-local directory for runner tests."""
    temp_dir = Path("tests") / "_runner_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    return temp_dir


def make_test_image(value: int = 100) -> np.ndarray:
    """Create a small RGB image for experiment runner tests."""
    image = np.full((16, 16, 3), value, dtype=np.uint8)
    image[4:8, 4:8] = [120, 80, 60]
    return image


def test_run_experiment_generates_outputs_and_metrics() -> None:
    temp_dir = make_runner_temp_dir()
    input_path = temp_dir / "input.png"
    reference_path = temp_dir / "reference.png"
    output_dir = temp_dir / "outputs"

    try:
        save_image(str(input_path), make_test_image())
        save_image(str(reference_path), make_test_image())
        config = ExperimentConfig(
            experiment_name="runner_demo",
            input_image=str(input_path),
            reference_image=str(reference_path),
            operations=[
                OperationConfig(name="gaussian_blur", params={"kernel_size": 3})
            ],
            metrics=["mse", "psnr", "ssim"],
            output_dir=str(output_dir),
        )

        result = run_experiment(config)

        assert result.experiment_name == "runner_demo"
        assert Path(result.output_dir).is_dir()
        assert len(result.output_images) >= 1
        assert Path(result.output_images[0]).is_file()
        assert result.metrics_path is not None
        assert Path(result.metrics_path).is_file()
        assert Path(result.summary_path).is_file()

        summary = json.loads(Path(result.summary_path).read_text(encoding="utf-8"))
        assert summary["experiment_name"] == "runner_demo"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_unknown_operation_raises_value_error() -> None:
    temp_dir = make_runner_temp_dir()
    input_path = temp_dir / "input.png"
    output_dir = temp_dir / "outputs"

    try:
        save_image(str(input_path), make_test_image())
        config = ExperimentConfig(
            experiment_name="bad_operation_demo",
            input_image=str(input_path),
            reference_image=None,
            operations=[OperationConfig(name="unknown_operation", params={})],
            metrics=[],
            output_dir=str(output_dir),
        )

        with pytest.raises(ValueError):
            run_experiment(config)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
