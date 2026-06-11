import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from app.experiments.experiment_runner import METRICS, PROCESSORS, save_image
from app.image_ops.image_loader import load_image
from app.reports.comparison_charts import generate_metric_charts
from app.utils.errors import ConfigError, ExperimentError
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ComparisonMethodConfig:
    """Configuration for one method in a comparison experiment."""

    name: str
    params: dict[str, Any]


@dataclass
class ComparisonConfig:
    """Configuration for a multi-method image processing comparison."""

    comparison_name: str
    input_image: str
    reference_image: str
    methods: list[ComparisonMethodConfig]
    metrics: list[str]
    output_dir: str


def _require_text_field(config: dict[str, Any], field_name: str) -> str:
    """Read a required non-empty string field from a YAML mapping."""
    value = config.get(field_name)
    if not isinstance(value, str) or not value:
        raise ConfigError(
            f"Missing required field: {field_name}", "COMPARISON_MISSING_FIELD"
        )
    return value


def _parse_methods(raw_methods: Any) -> list[ComparisonMethodConfig]:
    """Parse method configurations from raw YAML data."""
    if not isinstance(raw_methods, list) or not raw_methods:
        raise ConfigError(
            "Missing required field: methods", "COMPARISON_MISSING_METHODS"
        )

    methods: list[ComparisonMethodConfig] = []
    for raw_method in raw_methods:
        if not isinstance(raw_method, dict):
            raise ConfigError(
                "Each method must be a mapping", "COMPARISON_INVALID_METHOD"
            )

        name = raw_method.get("name")
        if not isinstance(name, str) or not name:
            raise ConfigError(
                "Each method must have a name", "COMPARISON_METHOD_MISSING_NAME"
            )

        params = raw_method.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise ConfigError(
                "Method params must be a mapping", "COMPARISON_INVALID_PARAMS"
            )

        methods.append(ComparisonMethodConfig(name=name, params=params))

    return methods


def _parse_metrics(raw_metrics: Any) -> list[str]:
    """Parse metric names from raw YAML data."""
    if raw_metrics is None:
        return []
    if not isinstance(raw_metrics, list) or not all(
        isinstance(item, str) for item in raw_metrics
    ):
        raise ConfigError(
            "metrics must be a list of strings", "COMPARISON_INVALID_METRICS"
        )
    return raw_metrics


def load_comparison_config(config_path: str) -> ComparisonConfig:
    """Load and validate a comparison experiment YAML configuration."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    raw_config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw_config, dict):
        raise ConfigError("Comparison config must be a mapping", "CONFIG_INVALID_ROOT")

    return ComparisonConfig(
        comparison_name=_require_text_field(raw_config, "comparison_name"),
        input_image=_require_text_field(raw_config, "input_image"),
        reference_image=_require_text_field(raw_config, "reference_image"),
        methods=_parse_methods(raw_config.get("methods")),
        metrics=_parse_metrics(raw_config.get("metrics")),
        output_dir=_require_text_field(raw_config, "output_dir"),
    )


def _run_method(image: Any, method: ComparisonMethodConfig) -> Any:
    """Run one configured comparison method."""
    processor = PROCESSORS.get(method.name)
    if processor is None:
        raise ExperimentError(f"Unknown method: {method.name}", "UNKNOWN_METHOD")
    return processor(image, **method.params)


def _calculate_method_metrics(
    method_name: str,
    output_image: Any,
    reference_image: Any,
    metric_names: list[str],
    output_image_path: str,
) -> list[dict[str, Any]]:
    """Calculate metrics for one method output image."""
    rows: list[dict[str, Any]] = []
    for metric_name in metric_names:
        metric = METRICS.get(metric_name)
        if metric is None:
            raise ExperimentError(f"Unknown metric: {metric_name}", "UNKNOWN_METRIC")
        rows.append(
            {
                "method": method_name,
                "metric": metric_name,
                "value": metric(output_image, reference_image),
                "output_image": output_image_path,
            }
        )
    return rows


def _write_comparison_metrics(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write comparison metric rows to a CSV file."""
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["method", "metric", "value", "output_image"],
        )
        writer.writeheader()
        writer.writerows(rows)


def run_comparison(
    config: ComparisonConfig,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Run a multi-method comparison experiment and return output paths."""
    output_dir = Path(run_dir) if run_dir else Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Running comparison %s into %s", config.comparison_name, output_dir)

    input_image = load_image(config.input_image)
    reference_image = load_image(config.reference_image)
    output_images: dict[str, str] = {}
    metric_rows: list[dict[str, Any]] = []

    for method in config.methods:
        method_output = _run_method(input_image, method)
        image_path = output_dir / f"{method.name}.png"
        save_image(str(image_path), method_output)
        output_images[method.name] = str(image_path)
        metric_rows.extend(
            _calculate_method_metrics(
                method.name,
                method_output,
                reference_image,
                config.metrics,
                str(image_path),
            )
        )

    metrics_path = output_dir / "comparison_metrics.csv"
    summary_path = output_dir / "comparison_summary.json"
    _write_comparison_metrics(metrics_path, metric_rows)
    chart_paths = generate_metric_charts(str(metrics_path), str(output_dir))

    result: dict[str, Any] = {
        "comparison_name": config.comparison_name,
        "output_dir": str(output_dir),
        "output_images": output_images,
        "metrics_path": str(metrics_path),
        "summary_path": str(summary_path),
        "chart_paths": chart_paths,
        "methods": [asdict(method) for method in config.methods],
    }
    summary_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result
