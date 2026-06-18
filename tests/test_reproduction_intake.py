import json
from pathlib import Path

from app.reproduction.intake import run_reproduction_intake
from app.reproduction.schemas import ReproductionIntakeInput


def test_run_reproduction_intake_creates_workspace_and_summary(
    tmp_path: Path,
) -> None:
    """Check paper and source materials are copied into an isolated workspace."""
    paper_path = tmp_path / "paper.txt"
    paper_text = "Title\nGaussian blur experiment\nPSNR and SSIM"
    paper_path.write_text(paper_text, encoding="utf-8")

    source_dir = tmp_path / "source_repo"
    source_dir.mkdir()
    (source_dir / "main.py").write_text("print('demo')", encoding="utf-8")

    summary = run_reproduction_intake(
        ReproductionIntakeInput(
            paper_path=str(paper_path),
            source_path=str(source_dir),
            base_dir=str(tmp_path / "reproduction_runs"),
        )
    )

    workspace_dir = Path(summary.workspace_dir)
    summary_path = workspace_dir / "intake_summary.json"

    assert summary.status == "completed"
    assert summary.run_id.startswith("repro_")
    assert workspace_dir.is_dir()
    assert (workspace_dir / "paper").is_dir()
    assert (workspace_dir / "source").is_dir()
    assert (workspace_dir / "artifacts").is_dir()
    assert (workspace_dir / "logs").is_dir()
    assert summary_path.is_file()
    assert summary.paper_saved_path is not None
    assert Path(summary.paper_saved_path).is_file()
    assert summary.paper_text_path is not None
    assert Path(summary.paper_text_path).read_text(encoding="utf-8") == paper_text
    assert summary.paper_text_chars == len(paper_text)
    assert summary.paper_text_lines == 3
    assert summary.source_saved_path is not None
    assert (Path(summary.source_saved_path) / "main.py").is_file()
    assert summary.source_file_count == 1
    assert summary.source_top_level_items == ["main.py"]

    saved_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expected_fields = {
        "run_id",
        "workspace_dir",
        "paper_input_path",
        "source_input_path",
        "paper_saved_path",
        "source_saved_path",
        "paper_text_path",
        "paper_text_chars",
        "paper_text_lines",
        "source_file_count",
        "source_top_level_items",
        "status",
        "warnings",
        "errors",
    }
    assert expected_fields.issubset(saved_summary)
    assert saved_summary["status"] == "completed"
