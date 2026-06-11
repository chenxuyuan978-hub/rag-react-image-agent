import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RunInfo:
    """Metadata for one archived experiment or agent run."""

    run_id: str
    run_dir: str
    created_at: str
    experiment_name: str


def sanitize_experiment_name(experiment_name: str) -> str:
    """Convert an experiment name into a safe ASCII path segment."""
    normalized = experiment_name.strip().replace(" ", "_")
    safe_name = re.sub(r"[^A-Za-z0-9_-]", "", normalized)
    safe_name = re.sub(r"_+", "_", safe_name).strip("_-")
    return safe_name or "experiment"


def create_run_dir(experiment_name: str, base_dir: str = "data/runs") -> RunInfo:
    """Create a unique run directory and return its metadata."""
    created_at = datetime.now().isoformat(timespec="seconds")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_experiment_name(experiment_name)
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    run_id = f"{timestamp}_{safe_name}"
    run_path = base_path / run_id
    suffix = 1
    while run_path.exists():
        run_id = f"{timestamp}_{safe_name}_{suffix:02d}"
        run_path = base_path / run_id
        suffix += 1

    run_path.mkdir(parents=True)
    return RunInfo(
        run_id=run_id,
        run_dir=str(run_path),
        created_at=created_at,
        experiment_name=safe_name,
    )


def copy_file_to_run(
    file_path: str,
    run_dir: str,
    target_name: str | None = None,
) -> str:
    """Copy a source file into a run directory and return the copied path."""
    source_path = Path(file_path)
    if not source_path.is_file():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    target_dir = Path(run_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / (target_name or source_path.name)
    shutil.copy2(source_path, target_path)
    return str(target_path)
