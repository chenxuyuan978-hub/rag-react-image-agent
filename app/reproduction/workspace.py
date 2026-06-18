from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ReproductionWorkspace:
    """Paths for one isolated reproduction intake workspace."""

    run_id: str
    workspace_dir: Path
    paper_dir: Path
    source_dir: Path
    artifacts_dir: Path
    logs_dir: Path
    intake_summary_path: Path


def _build_run_id() -> str:
    """Build a timestamp-based reproduction run id."""
    return f"repro_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def create_reproduction_workspace(
    base_dir: str | Path = "data/reproduction_runs",
    run_id: str | None = None,
) -> ReproductionWorkspace:
    """Create an isolated reproduction workspace with standard subdirectories."""
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    resolved_run_id = run_id or _build_run_id()
    workspace_dir = base_path / resolved_run_id
    suffix = 1
    while workspace_dir.exists():
        resolved_run_id = f"{run_id or _build_run_id()}_{suffix:02d}"
        workspace_dir = base_path / resolved_run_id
        suffix += 1

    paper_dir = workspace_dir / "paper"
    source_dir = workspace_dir / "source"
    artifacts_dir = workspace_dir / "artifacts"
    logs_dir = workspace_dir / "logs"
    for directory in [paper_dir, source_dir, artifacts_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    return ReproductionWorkspace(
        run_id=resolved_run_id,
        workspace_dir=workspace_dir,
        paper_dir=paper_dir,
        source_dir=source_dir,
        artifacts_dir=artifacts_dir,
        logs_dir=logs_dir,
        intake_summary_path=workspace_dir / "intake_summary.json",
    )
