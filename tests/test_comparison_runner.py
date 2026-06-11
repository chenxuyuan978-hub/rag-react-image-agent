import csv
import json
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest

from app.experiments.comparison_runner import (
    ComparisonConfig,
    ComparisonMethodConfig,
    load_comparison_config,
    run_comparison,
)
from app.experiments.experiment_runner import save_image


@pytest.fixture
def comparison_base_dir() -> Iterator[Path]:
    """Create an isolated comparison test directory inside the workspace."""
    with TemporaryDirectory(prefix="_comparison_", dir="tests") as temp_dir:
        yield Path(temp_dir)


def _make_test_image(value: int = 100) -> np.ndarray:
    """Create a small RGB image for comparison tests."""
    image = np.full((32, 32, 3), value, dtype=np.uint8)
    image[8:24, 8:24] = [160, 80, 120]
    return image


def _make_comparison_config(
    comparison_base_dir: Path,
    methods: list[ComparisonMethodConfig] | None = None,
) -> ComparisonConfig:
    """Create a comparison config with generated test images."""
    input_path = comparison_base_dir / "input.png"
    reference_path = comparison_base_dir / "reference.png"
    output_dir = comparison_base_dir / "outputs"
    save_image(str(input_path), _make_test_image(90))
    save_image(str(reference_path), _make_test_image(100))

    return ComparisonConfig(
        comparison_name="comparison_demo",
        input_image=str(input_path),
        reference_image=str(reference_path),
        methods=methods
        or [
            ComparisonMethodConfig(name="gaussian_blur", params={"kernel_size": 3}),
            ComparisonMethodConfig(name="median_blur", params={"kernel_size": 3}),
        ],
        metrics=["mse", "psnr", "ssim"],
        output_dir=str(output_dir),
    )


def test_load_comparison_config_reads_example() -> None:
    """Check that the example comparison YAML can be loaded."""
    config = load_comparison_config("examples/comparison_config.yaml")

    assert config.comparison_name == "demo_denoising_comparison"
    assert len(config.methods) == 3
    assert config.methods[0].name == "gaussian_blur"
    assert config.methods[0].params["kernel_size"] == 5


def test_run_comparison_generates_outputs_and_metrics(
    comparison_base_dir: Path,
) -> None:
    """Check that a comparison run generates images, metrics, and summary."""
    config = _make_comparison_config(comparison_base_dir)

    result = run_comparison(config)

    assert result["comparison_name"] == "comparison_demo"
    assert len(result["output_images"]) == 2
    assert Path(result["metrics_path"]).is_file()
    assert Path(result["summary_path"]).is_file()
    assert result["chart_paths"]
    assert all(Path(chart_path).is_file() for chart_path in result["chart_paths"])

    with Path(result["metrics_path"]).open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 6
    assert {row["method"] for row in rows} == {"gaussian_blur", "median_blur"}

    summary = json.loads(Path(result["summary_path"]).read_text(encoding="utf-8"))
    assert summary["comparison_name"] == "comparison_demo"
    assert summary["chart_paths"]


def test_run_comparison_with_run_dir_overrides_output_dir(
    comparison_base_dir: Path,
) -> None:
    """Check that run_dir can archive comparison outputs into a chosen directory."""
    config = _make_comparison_config(comparison_base_dir)
    run_dir = comparison_base_dir / "archived_run"

    result = run_comparison(config, run_dir=str(run_dir))

    assert result["output_dir"] == str(run_dir)
    assert Path(result["metrics_path"]).parent == run_dir
    assert Path(result["summary_path"]).parent == run_dir


def test_run_comparison_unknown_method_raises_value_error(
    comparison_base_dir: Path,
) -> None:
    """Check that unknown methods raise ValueError."""
    config = _make_comparison_config(
        comparison_base_dir,
        methods=[ComparisonMethodConfig(name="unknown_method", params={})],
    )

    with pytest.raises(ValueError):
        run_comparison(config)
