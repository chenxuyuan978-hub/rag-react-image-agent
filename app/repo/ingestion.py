import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceIngestionResult:
    """Summary of ingested source material."""

    source_saved_path: str
    source_file_count: int
    source_top_level_items: list[str]


def _count_files(path: Path) -> int:
    """Count regular files under a directory recursively."""
    return sum(1 for item in path.rglob("*") if item.is_file())


def _top_level_items(path: Path) -> list[str]:
    """Return sorted top-level item names under a directory."""
    return sorted(item.name for item in path.iterdir())


def _ensure_within_directory(target_dir: Path, target_path: Path) -> None:
    """Raise when a target path would escape the intended directory."""
    base = target_dir.resolve()
    resolved_target = target_path.resolve()
    try:
        resolved_target.relative_to(base)
    except ValueError as error:
        raise ValueError(f"Unsafe zip entry path detected: {target_path}") from error


def _extract_zip_safely(zip_path: Path, target_dir: Path) -> None:
    """Extract a zip file while blocking zip slip path traversal."""
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            member_path = target_dir / member.filename
            _ensure_within_directory(target_dir, member_path)

            if member.is_dir():
                member_path.mkdir(parents=True, exist_ok=True)
                continue

            member_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source_file, member_path.open("wb") as output:
                shutil.copyfileobj(source_file, output)


def ingest_source(
    source_path: str | Path, target_dir: str | Path
) -> SourceIngestionResult:
    """Ingest a source zip file or local source directory into a target directory."""
    source = Path(source_path)
    target = Path(target_dir)
    if not source.exists():
        raise FileNotFoundError(f"Source material not found: {source}")

    target.mkdir(parents=True, exist_ok=True)

    if source.is_file() and source.suffix.lower() == ".zip":
        _extract_zip_safely(source, target)
    elif source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        raise ValueError(
            f"Unsupported source material: {source}. "
            "Provide a .zip file or a local source directory."
        )

    return SourceIngestionResult(
        source_saved_path=str(target),
        source_file_count=_count_files(target),
        source_top_level_items=_top_level_items(target),
    )
