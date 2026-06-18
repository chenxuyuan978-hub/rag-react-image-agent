from pathlib import Path

import pytest

from app.paper.loader import load_paper_text


def test_load_paper_text_reads_txt(tmp_path: Path) -> None:
    """Check txt paper files can be read as text."""
    paper_path = tmp_path / "paper.txt"
    paper_path.write_text("line one\nline two", encoding="utf-8")

    assert load_paper_text(paper_path) == "line one\nline two"


def test_load_paper_text_reads_md(tmp_path: Path) -> None:
    """Check markdown paper files can be read as text."""
    paper_path = tmp_path / "paper.md"
    paper_path.write_text("# Demo Paper\nGaussian blur", encoding="utf-8")

    assert "Gaussian blur" in load_paper_text(paper_path)


def test_load_paper_text_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Check unsupported paper extensions raise a clear ValueError."""
    paper_path = tmp_path / "paper.docx"
    paper_path.write_text("not supported", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported paper file extension"):
        load_paper_text(paper_path)
