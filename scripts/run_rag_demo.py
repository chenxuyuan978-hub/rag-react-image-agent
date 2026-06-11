import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.chunker import chunk_documents
from app.rag.loader import Document, load_documents
from app.rag.retriever import TfidfRetriever


def load_demo_documents() -> list[Document]:
    """Load demo paper documents for the local RAG demo."""
    papers = load_documents("data/papers")
    if papers:
        return papers

    demo_paper = Path("examples/demo_paper.md")
    return [
        Document(text=demo_paper.read_text(encoding="utf-8"), source=str(demo_paper))
    ]


def main() -> int:
    """Run a local TF-IDF RAG retrieval demo."""
    documents = load_demo_documents()
    chunks = chunk_documents(documents)
    retriever = TfidfRetriever()
    retriever.build_index(chunks)

    results = retriever.retrieve("Gaussian blur PSNR SSIM kernel size", top_k=3)
    for index, result in enumerate(results, start=1):
        preview = result.text.replace("\n", " ")[:160]
        print(
            f"{index}. score={result.score:.4f} source={result.source} chunk={result.chunk_id}"
        )
        print(f"   {preview}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
