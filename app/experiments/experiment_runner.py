import csv
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from app.experiments.config_schema import ExperimentConfig
from app.image_ops.image_loader import load_image
from app.image_ops.metrics import mse, psnr, ssim
from app.image_ops.processors import (
    edge_detect,
    gaussian_blur,
    histogram_equalization,
    median_blur,
    sharpen,
)
from app.utils.errors import ExperimentError
from app.utils.logger import get_logger

logger = get_logger(__name__)


Processor = Callable[..., np.ndarray]
Metric = Callable[[np.ndarray, np.ndarray], float]


PROCESSORS: dict[str, Processor] = {
    "gaussian_blur": gaussian_blur,
    "median_blur": median_blur,
    "sharpen": sharpen,
    "edge_detect": edge_detect,
    "histogram_equalization": histogram_equalization,
}

METRICS: dict[str, Metric] = {
    "mse": mse,
    "psnr": psnr,
    "ssim": ssim,
}


@dataclass
class ExperimentResult:
    """Result metadata produced by a completed experiment run."""

    experiment_name: str
    output_dir: str
    output_images: list[str]
    metrics_path: str | None
    summary_path: str


def save_image(path: str, image: np.ndarray) -> None:
    """Save an image with Windows Chinese path compatibility."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_to_save = image
    if image.ndim == 3 and image.shape[2] == 3:
        image_to_save = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    extension = output_path.suffix or ".png"
    success, encoded_image = cv2.imencode(extension, image_to_save)
    if not success:
        raise ExperimentError(
            f"Failed to encode image for path: {path}", "IMAGE_ENCODE_FAILED"
        )

    output_path.write_bytes(encoded_image.tobytes())


def _run_operation(image: np.ndarray, operation_name: str, params: dict) -> np.ndarray:
    """Run one configured image processing operation."""
    processor = PROCESSORS.get(operation_name)
    if processor is None:
        raise ExperimentError(
            f"Unknown operation: {operation_name}", "UNKNOWN_OPERATION"
        )

    return processor(image, **params)


def _calculate_metrics(
    image: np.ndarray,
    reference_image: np.ndarray,
    metric_names: list[str],
) -> list[dict[str, float]]:
    """Calculate configured metrics against the reference image."""
    rows: list[dict[str, float]] = []
    for metric_name in metric_names:
        metric = METRICS.get(metric_name)
        if metric is None:
            raise ExperimentError(f"Unknown metric: {metric_name}", "UNKNOWN_METRIC")

        rows.append({"metric": metric_name, "value": metric(image, reference_image)})

    return rows


def _write_metrics_csv(path: Path, rows: list[dict[str, float]]) -> None:
    """Write metric rows to a CSV file."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["metric", "value"])
        writer.writeheader()
        writer.writerows(rows)


def _write_summary(path: Path, result: ExperimentResult) -> None:
    """Write experiment result metadata to a JSON summary file."""
    path.write_text(
        json.dumps(asdict(result), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_experiment(
    config: ExperimentConfig,
    run_dir: str | None = None,
) -> ExperimentResult:
    """Run an image processing experiment from a validated config."""
    output_dir = Path(run_dir) if run_dir else Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Running experiment %s into %s", config.experiment_name, output_dir)

    current_image = load_image(config.input_image)
    output_images: list[str] = []

    for index, operation in enumerate(config.operations, start=1):
        current_image = _run_operation(current_image, operation.name, operation.params)
        image_path = output_dir / f"step_{index:02d}_{operation.name}.png"
        save_image(str(image_path), current_image)
        output_images.append(str(image_path))

    metrics_path: str | None = None
    if config.reference_image and config.metrics:
        reference_image = load_image(config.reference_image)
        metric_rows = _calculate_metrics(current_image, reference_image, config.metrics)
        metrics_file = output_dir / "metrics.csv"
        _write_metrics_csv(metrics_file, metric_rows)
        metrics_path = str(metrics_file)

    summary_path = output_dir / "summary.json"
    result = ExperimentResult(
        experiment_name=config.experiment_name,
        output_dir=str(output_dir),
        output_images=output_images,
        metrics_path=metrics_path,
        summary_path=str(summary_path),
    )
    _write_summary(summary_path, result)

    return result
