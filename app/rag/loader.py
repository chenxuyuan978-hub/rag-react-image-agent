from dataclasses import dataclass
from pathlib import Path

SUPPORTED_DOCUMENT_EXTENSIONS = {".txt", ".md"}


@dataclass
class Document:
    """A text document loaded from a local paper file."""

    text: str
    source: str


def load_documents(directory: str = "data/papers") -> list[Document]:
    """Load .txt and .md documents from a directory."""
    document_dir = Path(directory)
    if not document_dir.is_dir():
        return []

    documents: list[Document] = []
    for file_path in sorted(document_dir.iterdir()):
        if file_path.suffix.lower() not in SUPPORTED_DOCUMENT_EXTENSIONS:
            continue
        text = file_path.read_text(encoding="utf-8")
        documents.append(Document(text=text, source=str(file_path)))

    return documents
