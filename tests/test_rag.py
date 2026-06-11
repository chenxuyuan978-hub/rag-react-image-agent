import shutil
from pathlib import Path

import pytest

from app.rag.chunker import chunk_documents
from app.rag.loader import Document, load_documents
from app.rag.retriever import TfidfRetriever


def make_rag_temp_dir() -> Path:
    """Create a clean workspace-local directory for RAG tests."""
    temp_dir = Path("tests") / "_rag_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    return temp_dir


def test_load_documents_reads_md_and_txt_files() -> None:
    temp_dir = make_rag_temp_dir()

    try:
        (temp_dir / "paper.md").write_text("Gaussian blur paper", encoding="utf-8")
        (temp_dir / "notes.txt").write_text("PSNR and SSIM notes", encoding="utf-8")
        (temp_dir / "ignore.pdf").write_text("ignore me", encoding="utf-8")

        documents = load_documents(str(temp_dir))

        assert len(documents) == 2
        assert {Path(document.source).suffix for document in documents} == {
            ".md",
            ".txt",
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_chunk_documents_splits_documents() -> None:
    document = Document(text="abcdefghi", source="paper.md")

    chunks = chunk_documents([document], chunk_size=4, overlap=1)

    assert len(chunks) == 3
    assert chunks[0].text == "abcd"
    assert chunks[1].text == "defg"
    assert chunks[2].source == "paper.md"


def test_short_document_returns_one_chunk() -> None:
    document = Document(text="short text", source="paper.md")

    chunks = chunk_documents([document], chunk_size=500, overlap=50)

    assert len(chunks) == 1
    assert chunks[0].text == "short text"


def test_invalid_overlap_raises_value_error() -> None:
    document = Document(text="text", source="paper.md")

    with pytest.raises(ValueError):
        chunk_documents([document], chunk_size=10, overlap=10)


def test_build_index_then_retrieve_returns_relevant_result() -> None:
    documents = [
        Document(
            text="The experiment setting uses Gaussian blur with kernel size 5. PSNR and SSIM are reported.",
            source="demo.md",
        ),
        Document(
            text="This unrelated section discusses file organization.",
            source="other.md",
        ),
    ]
    chunks = chunk_documents(documents, chunk_size=200, overlap=20)
    retriever = TfidfRetriever()
    retriever.build_index(chunks)

    results = retriever.retrieve("Gaussian blur PSNR", top_k=1)

    assert len(results) == 1
    assert "Gaussian blur" in results[0].text or "PSNR" in results[0].text
    assert results[0].score > 0


def test_retrieve_before_build_index_raises_runtime_error() -> None:
    retriever = TfidfRetriever()

    with pytest.raises(RuntimeError):
        retriever.retrieve("Gaussian blur PSNR")
