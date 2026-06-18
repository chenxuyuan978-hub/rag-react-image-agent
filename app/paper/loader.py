from pathlib import Path


def _load_pdf_text_with_pypdf(path: Path) -> str:
    """Load PDF text with pypdf when the optional dependency is installed."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _load_pdf_text_with_pypdf2(path: Path) -> str:
    """Load PDF text with PyPDF2 when the optional dependency is installed."""
    from PyPDF2 import PdfReader

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _load_pdf_text(path: Path) -> str:
    """Load PDF text with optional PDF parsers and clear fallback errors."""
    try:
        return _load_pdf_text_with_pypdf(path)
    except ImportError:
        pass
    except Exception as error:
        raise RuntimeError(f"Failed to parse PDF with pypdf: {error}") from error

    try:
        return _load_pdf_text_with_pypdf2(path)
    except ImportError as error:
        raise RuntimeError(
            "PDF parsing requires optional dependency pypdf or PyPDF2. "
            "Install pypdf to parse PDF files."
        ) from error
    except Exception as error:
        raise RuntimeError(f"Failed to parse PDF with PyPDF2: {error}") from error


def load_paper_text(path: str | Path) -> str:
    """Load text from a paper file, supporting txt, md, and optional PDF parsing."""
    paper_path = Path(path)
    if not paper_path.is_file():
        raise FileNotFoundError(f"Paper file not found: {paper_path}")

    suffix = paper_path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return paper_path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _load_pdf_text(paper_path)

    raise ValueError(
        f"Unsupported paper file extension: {suffix}. "
        "Supported extensions are .txt, .md, and .pdf."
    )
