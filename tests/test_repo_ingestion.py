from pathlib import Path
from zipfile import ZipFile

import pytest

from app.repo.ingestion import ingest_source


def test_ingest_source_extracts_zip_safely(tmp_path: Path) -> None:
    """Check zip source materials are safely extracted into the target directory."""
    zip_path = tmp_path / "source.zip"
    with ZipFile(zip_path, "w") as archive:
        archive.writestr("src/main.py", "print('hello')")
        archive.writestr("README.md", "# demo")

    target_dir = tmp_path / "target"
    result = ingest_source(zip_path, target_dir)

    assert (target_dir / "src" / "main.py").is_file()
    assert (target_dir / "README.md").is_file()
    assert result.source_file_count == 2
    assert result.source_top_level_items == ["README.md", "src"]


def test_ingest_source_copies_directory(tmp_path: Path) -> None:
    """Check local source directories can be copied into the target directory."""
    source_dir = tmp_path / "source"
    (source_dir / "pkg").mkdir(parents=True)
    (source_dir / "pkg" / "__init__.py").write_text("", encoding="utf-8")

    target_dir = tmp_path / "target"
    result = ingest_source(source_dir, target_dir)

    assert (target_dir / "pkg" / "__init__.py").is_file()
    assert result.source_file_count == 1
    assert result.source_top_level_items == ["pkg"]


def test_ingest_source_rejects_zip_slip(tmp_path: Path) -> None:
    """Check zip entries cannot escape the target directory."""
    zip_path = tmp_path / "unsafe.zip"
    with ZipFile(zip_path, "w") as archive:
        archive.writestr("../evil.py", "print('bad')")

    with pytest.raises(ValueError, match="Unsafe zip entry path"):
        ingest_source(zip_path, tmp_path / "target")
