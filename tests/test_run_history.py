import json
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.core.run_history import get_run_summary, list_runs


@pytest.fixture
def history_base_dir() -> Iterator[Path]:
    """Create an isolated run history test directory inside the workspace."""
    with TemporaryDirectory(prefix="_run_history_", dir="tests") as temp_dir:
        yield Path(temp_dir)


def test_list_runs_returns_empty_for_missing_directory(
    history_base_dir: Path,
) -> None:
    """Check that missing run history directories return an empty list."""
    runs = list_runs(str(history_base_dir / "missing_runs"))

    assert runs == []


def test_list_runs_reads_multiple_run_directories(history_base_dir: Path) -> None:
    """Check that multiple run directories are listed newest first."""
    base_dir = history_base_dir / "runs"
    older_run = base_dir / "20260101_120000_old_experiment"
    newer_run = base_dir / "20260102_120000_new_experiment"
    older_run.mkdir(parents=True)
    newer_run.mkdir(parents=True)

    (older_run / "summary.json").write_text(
        json.dumps({"experiment_name": "old_experiment"}),
        encoding="utf-8",
    )
    (newer_run / "summary.json").write_text(
        json.dumps({"experiment_name": "new_experiment"}),
        encoding="utf-8",
    )

    runs = list_runs(str(base_dir))

    assert [run.run_id for run in runs] == [
        "20260102_120000_new_experiment",
        "20260101_120000_old_experiment",
    ]
    assert runs[0].experiment_name == "new_experiment"


def test_list_runs_detects_output_files(history_base_dir: Path) -> None:
    """Check that metrics, summary, and report files are detected."""
    base_dir = history_base_dir / "runs"
    run_dir = base_dir / "20260103_120000_demo"
    run_dir.mkdir(parents=True)
    (run_dir / "metrics.csv").write_text("metric,value\npsnr,30\n", encoding="utf-8")
    (run_dir / "summary.json").write_text(
        json.dumps({"experiment_name": "demo", "created_at": "2026-01-03T12:00:00"}),
        encoding="utf-8",
    )
    (run_dir / "report.md").write_text("# report", encoding="utf-8")

    run = list_runs(str(base_dir))[0]

    assert run.has_metrics is True
    assert run.has_summary is True
    assert run.has_report is True
    assert run.metrics_path == str(run_dir / "metrics.csv")
    assert run.summary_path == str(run_dir / "summary.json")
    assert run.report_path == str(run_dir / "report.md")
    assert run.created_at == "2026-01-03T12:00:00"


def test_get_run_summary_returns_selected_run(history_base_dir: Path) -> None:
    """Check that one selected run summary can be returned by run_id."""
    base_dir = history_base_dir / "runs"
    run_id = "20260104_120000_selected"
    run_dir = base_dir / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "summary.json").write_text(
        json.dumps({"experiment_name": "selected"}),
        encoding="utf-8",
    )

    run = get_run_summary(run_id, base_dir=str(base_dir))

    assert run.run_id == run_id
    assert run.experiment_name == "selected"


def test_get_run_summary_missing_run_raises_file_not_found(
    history_base_dir: Path,
) -> None:
    """Check that missing run IDs raise FileNotFoundError."""
    base_dir = history_base_dir / "runs"

    with pytest.raises(FileNotFoundError):
        get_run_summary("missing_run", base_dir=str(base_dir))


def test_get_run_summary_blocks_path_traversal(history_base_dir: Path) -> None:
    """Check that run_id path traversal is rejected."""
    base_dir = history_base_dir / "runs"
    base_dir.mkdir()

    with pytest.raises(ValueError):
        get_run_summary("../outside", base_dir=str(base_dir))
