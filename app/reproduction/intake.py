import json
import shutil
from dataclasses import asdict
from pathlib import Path

from app.paper.loader import load_paper_text
from app.repo.ingestion import ingest_source
from app.reproduction.schemas import (
    ReproductionIntakeInput,
    ReproductionIntakeSummary,
)
from app.reproduction.workspace import create_reproduction_workspace


def _write_summary(path: Path, summary: ReproductionIntakeSummary) -> None:
    """Write intake summary JSON with stable UTF-8 formatting."""
    path.write_text(
        json.dumps(asdict(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _copy_paper(paper_path: Path, paper_dir: Path) -> Path:
    """Copy the input paper file into the workspace paper directory."""
    if not paper_path.is_file():
        raise FileNotFoundError(f"Paper file not found: {paper_path}")
    saved_path = paper_dir / paper_path.name
    shutil.copy2(paper_path, saved_path)
    return saved_path


def run_reproduction_intake(
    input_data: ReproductionIntakeInput,
) -> ReproductionIntakeSummary:
    """Create a reproduction workspace and ingest paper and source materials."""
    workspace = create_reproduction_workspace(input_data.base_dir)
    warnings: list[str] = []
    errors: list[str] = []

    paper_input_path = Path(input_data.paper_path)
    source_input_path = Path(input_data.source_path)
    paper_saved_path: str | None = None
    source_saved_path: str | None = None
    paper_text_path: str | None = None
    paper_text_chars = 0
    paper_text_lines = 0
    source_file_count = 0
    source_top_level_items: list[str] = []

    try:
        saved_paper = _copy_paper(paper_input_path, workspace.paper_dir)
        paper_saved_path = str(saved_paper)
        paper_text = load_paper_text(saved_paper)
        text_path = workspace.paper_dir / "paper_text.txt"
        text_path.write_text(paper_text, encoding="utf-8")
        paper_text_path = str(text_path)
        paper_text_chars = len(paper_text)
        paper_text_lines = len(paper_text.splitlines())
    except Exception as error:
        errors.append(f"paper intake failed: {error}")

    try:
        source_result = ingest_source(source_input_path, workspace.source_dir)
        source_saved_path = source_result.source_saved_path
        source_file_count = source_result.source_file_count
        source_top_level_items = source_result.source_top_level_items
    except Exception as error:
        errors.append(f"source intake failed: {error}")

    summary = ReproductionIntakeSummary(
        run_id=workspace.run_id,
        workspace_dir=str(workspace.workspace_dir),
        paper_input_path=str(paper_input_path),
        source_input_path=str(source_input_path),
        paper_saved_path=paper_saved_path,
        source_saved_path=source_saved_path,
        paper_text_path=paper_text_path,
        paper_text_chars=paper_text_chars,
        paper_text_lines=paper_text_lines,
        source_file_count=source_file_count,
        source_top_level_items=source_top_level_items,
        status="failed" if errors else "completed",
        warnings=warnings,
        errors=errors,
    )
    _write_summary(workspace.intake_summary_path, summary)
    return summary
