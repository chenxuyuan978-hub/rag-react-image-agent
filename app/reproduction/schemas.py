from dataclasses import dataclass


@dataclass
class ReproductionIntakeInput:
    """Input paths for a real paper and source-code intake task."""

    paper_path: str
    source_path: str
    base_dir: str = "data/reproduction_runs"


@dataclass
class ReproductionIntakeSummary:
    """Summary written after a reproduction intake task."""

    run_id: str
    workspace_dir: str
    paper_input_path: str
    source_input_path: str
    paper_saved_path: str | None
    source_saved_path: str | None
    paper_text_path: str | None
    paper_text_chars: int
    paper_text_lines: int
    source_file_count: int
    source_top_level_items: list[str]
    status: str
    warnings: list[str]
    errors: list[str]
