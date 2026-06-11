from dataclasses import dataclass

from app.rag.loader import Document


@dataclass
class Chunk:
    """A searchable text chunk derived from a document."""

    text: str
    source: str
    chunk_id: int


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """Split documents into overlapping fixed-size chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks: list[Chunk] = []
    next_chunk_id = 0
    step = chunk_size - overlap

    for document in documents:
        text = document.text
        if len(text) <= chunk_size:
            chunks.append(
                Chunk(text=text, source=document.source, chunk_id=next_chunk_id)
            )
            next_chunk_id += 1
            continue

        start = 0
        while start < len(text):
            chunk_text = text[start : start + chunk_size]
            chunks.append(
                Chunk(text=chunk_text, source=document.source, chunk_id=next_chunk_id)
            )
            next_chunk_id += 1
            if start + chunk_size >= len(text):
                break
            start += step

    return chunks
