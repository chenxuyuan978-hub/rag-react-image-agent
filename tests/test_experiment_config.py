from pathlib import Path

import pytest
import yaml

from app.experiments.config_schema import load_experiment_config


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data), encoding="utf-8")


def test_demo_yaml_can_be_loaded() -> None:
    config_path = Path("examples/demo_config.yaml")

    config = load_experiment_config(str(config_path))

    assert config.experiment_name == "demo_blur_experiment"
    assert len(config.operations) == 2
    assert config.operations[0].name == "gaussian_blur"
    assert config.operations[0].params["kernel_size"] == 5
    assert config.operations[1].name == "sharpen"
    assert config.operations[1].params == {}
    assert config.metrics == ["mse", "psnr", "ssim"]


def test_missing_required_fields_raise_value_error() -> None:
    base_config = {
        "experiment_name": "demo",
        "input_image": "data/images/input.png",
        "operations": [{"name": "gaussian_blur", "params": {"kernel_size": 5}}],
        "output_dir": "data/outputs/demo",
    }

    for field_name in ["experiment_name", "input_image", "output_dir", "operations"]:
        config = base_config.copy()
        config.pop(field_name)
        config_path = Path("tests") / f"missing_{field_name}.yaml"

        try:
            write_yaml(config_path, config)

            with pytest.raises(ValueError):
                load_experiment_config(str(config_path))
        finally:
            config_path.unlink(missing_ok=True)


def test_empty_operations_raise_value_error() -> None:
    config_path = Path("tests") / "empty_operations.yaml"
    config = {
        "experiment_name": "demo",
        "input_image": "data/images/input.png",
        "operations": [],
        "output_dir": "data/outputs/demo",
    }

    try:
        write_yaml(config_path, config)

        with pytest.raises(ValueError):
            load_experiment_config(str(config_path))
    finally:
        config_path.unlink(missing_ok=True)


def test_operation_without_name_raises_value_error() -> None:
    config_path = Path("tests") / "operation_without_name.yaml"
    config = {
        "experiment_name": "demo",
        "input_image": "data/images/input.png",
        "operations": [{"params": {"kernel_size": 5}}],
        "output_dir": "data/outputs/demo",
    }

    try:
        write_yaml(config_path, config)

        with pytest.raises(ValueError):
            load_experiment_config(str(config_path))
    finally:
        config_path.unlink(missing_ok=True)


def test_missing_config_file_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        load_experiment_config("tests/not_exists.yaml")
