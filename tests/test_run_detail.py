import json
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.core.run_detail import get_run_detail


@pytest.fixture
def detail_base_dir() -> Iterator[Path]:
    """Create an isolated run detail test directory inside the workspace."""
    with TemporaryDirectory(prefix="_run_detail_", dir="tests") as temp_dir:
        yield Path(temp_dir)


def _make_run_dir(base_dir: Path, run_id: str = "20260105_120000_detail") -> Path:
    """Create a run directory for run detail tests."""
    run_dir = base_dir / "runs" / run_id
    run_dir.mkdir(parents=True)
    return run_dir


def test_get_run_detail_reads_summary(detail_base_dir: Path) -> None:
    """Check that summary.json is loaded into the run detail."""
    run_dir = _make_run_dir(detail_base_dir)
    (run_dir / "summary.json").write_text(
        json.dumps({"experiment_name": "detail_demo"}),
        encoding="utf-8",
    )

    detail = get_run_detail(run_dir.name, base_dir=str(detail_base_dir / "runs"))

    assert detail.summary is not None
    assert detail.summary["experiment_name"] == "detail_demo"


def test_get_run_detail_reads_metrics(detail_base_dir: Path) -> None:
    """Check that metrics.csv is loaded into the run detail."""
    run_dir = _make_run_dir(detail_base_dir)
    (run_dir / "metrics.csv").write_text(
        "metric,value\npsnr,30.5\nssim,0.9\n",
        encoding="utf-8",
    )

    detail = get_run_detail(run_dir.name, base_dir=str(detail_base_dir / "runs"))

    assert detail.metrics == [
        {"metric": "psnr", "value": "30.5"},
        {"metric": "ssim", "value": "0.9"},
    ]


def test_get_run_detail_reads_report_and_trace(detail_base_dir: Path) -> None:
    """Check that report.md and trace.txt are loaded into the run detail."""
    run_dir = _make_run_dir(detail_base_dir)
    (run_dir / "report.md").write_text("# report\nDemo analysis", encoding="utf-8")
    (run_dir / "trace.txt").write_text("Thought: demo", encoding="utf-8")

    detail = get_run_detail(run_dir.name, base_dir=str(detail_base_dir / "runs"))

    assert detail.report_text == "# report\nDemo analysis"
    assert detail.trace_text == "Thought: demo"


def test_get_run_detail_detects_output_images(detail_base_dir: Path) -> None:
    """Check that output image paths are listed from the run directory."""
    run_dir = _make_run_dir(detail_base_dir)
    (run_dir / "step_02_sharpen.jpg").write_bytes(b"jpg")
    (run_dir / "step_01_gaussian_blur.png").write_bytes(b"png")
    (run_dir / "notes.txt").write_text("not an image", encoding="utf-8")

    detail = get_run_detail(run_dir.name, base_dir=str(detail_base_dir / "runs"))

    assert detail.output_images == [
        str((run_dir / "step_01_gaussian_blur.png").resolve()),
        str((run_dir / "step_02_sharpen.jpg").resolve()),
    ]


def test_get_run_detail_missing_run_raises_file_not_found(
    detail_base_dir: Path,
) -> None:
    """Check that missing run IDs raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        get_run_detail("missing_run", base_dir=str(detail_base_dir / "runs"))


def test_get_run_detail_blocks_path_traversal(detail_base_dir: Path) -> None:
    """Check that run_id path traversal is rejected."""
    base_dir = detail_base_dir / "runs"
    base_dir.mkdir()

    with pytest.raises(ValueError):
        get_run_detail("../outside", base_dir=str(base_dir))
