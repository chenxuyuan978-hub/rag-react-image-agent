import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RunSummary:
    """Summary metadata for one archived run directory."""

    run_id: str
    run_dir: str
    experiment_name: str | None
    created_at: str | None
    has_metrics: bool
    has_summary: bool
    has_report: bool
    metrics_path: str | None
    summary_path: str | None
    report_path: str | None


def _read_summary_json(summary_path: Path) -> dict[str, Any]:
    """Read summary.json as a dictionary, returning empty data on invalid JSON."""
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}
    return data


def _build_run_summary(run_dir: Path) -> RunSummary:
    """Build a run summary from one run directory."""
    metrics_path = run_dir / "metrics.csv"
    summary_path = run_dir / "summary.json"
    report_path = run_dir / "report.md"

    summary_data: dict[str, Any] = {}
    if summary_path.is_file():
        summary_data = _read_summary_json(summary_path)

    experiment_name = summary_data.get("experiment_name")
    created_at = summary_data.get("created_at")

    return RunSummary(
        run_id=run_dir.name,
        run_dir=str(run_dir),
        experiment_name=experiment_name if isinstance(experiment_name, str) else None,
        created_at=created_at if isinstance(created_at, str) else None,
        has_metrics=metrics_path.is_file(),
        has_summary=summary_path.is_file(),
        has_report=report_path.is_file(),
        metrics_path=str(metrics_path) if metrics_path.is_file() else None,
        summary_path=str(summary_path) if summary_path.is_file() else None,
        report_path=str(report_path) if report_path.is_file() else None,
    )


def list_runs(base_dir: str = "data/runs") -> list[RunSummary]:
    """List archived run directories, newest directory names first."""
    runs_path = Path(base_dir)
    if not runs_path.is_dir():
        return []

    run_dirs = [path for path in runs_path.iterdir() if path.is_dir()]
    run_dirs.sort(key=lambda path: path.name, reverse=True)
    return [_build_run_summary(run_dir) for run_dir in run_dirs]


def get_run_summary(run_id: str, base_dir: str = "data/runs") -> RunSummary:
    """Return one run summary while preventing path traversal."""
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

    return _build_run_summary(run_path)
