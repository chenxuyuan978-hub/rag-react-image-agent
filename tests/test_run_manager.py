from pathlib import Path

import pytest

from app.core.run_manager import copy_file_to_run, create_run_dir


def test_create_run_dir_creates_directory() -> None:
    """Check that create_run_dir creates an archived run directory."""
    run_info = create_run_dir("Demo Experiment", base_dir="tests/_run_manager_temp")

    assert run_info.run_id
    assert Path(run_info.run_dir).is_dir()
    assert run_info.experiment_name == "Demo_Experiment"


def test_create_run_dir_sanitizes_experiment_name() -> None:
    """Check that unsafe characters are removed from experiment names."""
    run_info = create_run_dir("中文 Demo !@# 01", base_dir="tests/_run_manager_temp")

    assert run_info.experiment_name == "Demo_01"
    assert "中文" not in run_info.run_id


def test_copy_file_to_run_copies_file() -> None:
    """Check that a file can be copied into a run directory."""
    base_dir = Path("tests/_run_manager_temp")
    source_path = base_dir / "source.txt"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("demo", encoding="utf-8")
    run_info = create_run_dir("copy demo", base_dir=str(base_dir))

    copied_path = copy_file_to_run(str(source_path), run_info.run_dir, "config.txt")

    assert Path(copied_path).is_file()
    assert Path(copied_path).read_text(encoding="utf-8") == "demo"


def test_copy_file_to_run_missing_source_raises_file_not_found() -> None:
    """Check that missing source files raise FileNotFoundError."""
    run_info = create_run_dir("missing source", base_dir="tests/_run_manager_temp")

    with pytest.raises(FileNotFoundError):
        copy_file_to_run("tests/_run_manager_temp/not_exists.txt", run_info.run_dir)
