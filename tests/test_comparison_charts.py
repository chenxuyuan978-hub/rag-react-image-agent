import csv
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.reports.comparison_charts import generate_metric_charts


@pytest.fixture
def chart_base_dir() -> Iterator[Path]:
    """Create an isolated chart test directory inside the workspace."""
    with TemporaryDirectory(prefix="_charts_", dir="tests") as temp_dir:
        yield Path(temp_dir)


def test_generate_metric_charts_creates_png_files(chart_base_dir: Path) -> None:
    """Check that comparison metrics can be rendered as PNG charts."""
    metrics_path = chart_base_dir / "comparison_metrics.csv"
    output_dir = chart_base_dir / "charts"

    with metrics_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["method", "metric", "value"])
        writer.writeheader()
        writer.writerows(
            [
                {"method": "gaussian_blur", "metric": "mse", "value": "12.0"},
                {"method": "median_blur", "metric": "mse", "value": "10.0"},
                {"method": "gaussian_blur", "metric": "psnr", "value": "28.0"},
                {"method": "median_blur", "metric": "psnr", "value": "30.0"},
                {"method": "gaussian_blur", "metric": "ssim", "value": "0.8"},
                {"method": "median_blur", "metric": "ssim", "value": "0.9"},
            ]
        )

    chart_paths = generate_metric_charts(str(metrics_path), str(output_dir))

    assert chart_paths
    assert len(chart_paths) == 3
    assert all(Path(chart_path).is_file() for chart_path in chart_paths)
