import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}


@dataclass
class RunDetail:
    """Detailed content for one archived run directory."""

    run_id: str
    run_dir: str
    summary: dict[str, Any] | None
    metrics: list[dict[str, str]] | None
    report_text: str | None
    trace_text: str | None
    output_images: list[str]


def _resolve_run_dir(run_id: str, base_dir: str) -> Path:
    """Resolve a run directory while preventing path traversal."""
    if not run_id or Path(run_id).is_absolute():
        raise ValueError("Invalid run_id")

    base_path = Path(base_dir).resolve()
    run_path = (base_path / run_id).resolve()

    try:
        run_path.relative_to(base_path)
    except ValueError as error:
        raise ValueError("run_id is outside the runs directory") from error

    if not run_path.is_dir():
        raise FileNotFoundError(f"Run not found: {run_id}")

    return run_path


def _read_summary(path: Path) -> dict[str, Any] | None:
    """Read summary.json if it exists."""
    if not path.is_file():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return None
    return data


def _read_metrics(path: Path) -> list[dict[str, str]] | None:
    """Read metrics.csv if it exists."""
    if not path.is_file():
        return None

    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _read_trace(run_dir: Path) -> str | None:
    """Read trace.txt or trace.json if either exists."""
    for trace_name in ("trace.txt", "trace.json"):
        trace_path = run_dir / trace_name
        if trace_path.is_file():
            return trace_path.read_text(encoding="utf-8")
    return None


def _list_output_images(run_dir: Path) -> list[str]:
    """List image files directly under a run directory."""
    image_paths = [
        path
        for path in run_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    image_paths.sort(key=lambda path: path.name)
    return [str(path) for path in image_paths]


def get_run_detail(run_id: str, base_dir: str = "data/runs") -> RunDetail:
    """Return detailed files and metadata for one archived run."""
    run_dir = _resolve_run_dir(run_id, base_dir)
    report_path = run_dir / "report.md"

    return RunDetail(
        run_id=run_dir.name,
        run_dir=str(run_dir),
        summary=_read_summary(run_dir / "summary.json"),
        metrics=_read_metrics(run_dir / "metrics.csv"),
        report_text=(
            report_path.read_text(encoding="utf-8") if report_path.is_file() else None
        ),
        trace_text=_read_trace(run_dir),
        output_images=_list_output_images(run_dir),
    )
