from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.utils.errors import ConfigError


@dataclass
class OperationConfig:
    """Configuration for one image processing operation."""

    name: str
    params: dict[str, Any]


@dataclass
class ExperimentConfig:
    """Configuration for one reproducible image processing experiment."""

    experiment_name: str
    input_image: str
    reference_image: str | None
    operations: list[OperationConfig]
    metrics: list[str]
    output_dir: str


def _require_text_field(config: dict[str, Any], field_name: str) -> str:
    value = config.get(field_name)
    if not isinstance(value, str) or not value:
        raise ConfigError(
            f"Missing required field: {field_name}", "CONFIG_MISSING_FIELD"
        )
    return value


def _parse_operations(raw_operations: Any) -> list[OperationConfig]:
    if not isinstance(raw_operations, list) or not raw_operations:
        raise ConfigError(
            "Missing required field: operations", "CONFIG_MISSING_OPERATIONS"
        )

    operations: list[OperationConfig] = []
    for raw_operation in raw_operations:
        if not isinstance(raw_operation, dict):
            raise ConfigError(
                "Each operation must be a mapping", "CONFIG_INVALID_OPERATION"
            )

        name = raw_operation.get("name")
        if not isinstance(name, str) or not name:
            raise ConfigError(
                "Each operation must have a name", "CONFIG_OPERATION_MISSING_NAME"
            )

        params = raw_operation.get("params", {})
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise ConfigError(
                "Operation params must be a mapping", "CONFIG_INVALID_PARAMS"
            )

        operations.append(OperationConfig(name=name, params=params))

    return operations


def load_experiment_config(config_path: str) -> ExperimentConfig:
    """Load and validate an experiment configuration from a YAML file."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    if not isinstance(raw_config, dict):
        raise ConfigError("Experiment config must be a mapping", "CONFIG_INVALID_ROOT")

    experiment_name = _require_text_field(raw_config, "experiment_name")
    input_image = _require_text_field(raw_config, "input_image")
    output_dir = _require_text_field(raw_config, "output_dir")
    operations = _parse_operations(raw_config.get("operations"))

    reference_image = raw_config.get("reference_image")
    if reference_image is not None and not isinstance(reference_image, str):
        raise ConfigError(
            "reference_image must be a string or empty", "CONFIG_INVALID_REFERENCE"
        )

    metrics = raw_config.get("metrics", [])
    if metrics is None:
        metrics = []
    if not isinstance(metrics, list) or not all(
        isinstance(item, str) for item in metrics
    ):
        raise ConfigError("metrics must be a list of strings", "CONFIG_INVALID_METRICS")

    return ExperimentConfig(
        experiment_name=experiment_name,
        input_image=input_image,
        reference_image=reference_image,
        operations=operations,
        metrics=metrics,
        output_dir=output_dir,
    )
