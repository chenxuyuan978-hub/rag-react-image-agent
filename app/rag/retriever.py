from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.chunker import Chunk
from app.utils.errors import RagError


@dataclass
class RetrievalResult:
    """One ranked retrieval result from the TF-IDF index."""

    text: str
    source: str
    score: float
    chunk_id: int


class TfidfRetriever:
    """A local TF-IDF retriever for document chunks."""

    def __init__(self) -> None:
        """Initialize an empty TF-IDF retriever."""
        self._chunks: list[Chunk] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None

    def build_index(self, chunks: list[Chunk]) -> None:
        """Build a TF-IDF index from chunks."""
        if not chunks:
            raise RagError("chunks must not be empty", "RAG_EMPTY_CHUNKS")
        self._chunks = chunks
        self._vectorizer = TfidfVectorizer()
        texts = [chunk.text for chunk in chunks]
        self._matrix = self._vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """Retrieve the top matching chunks for a query."""
        if self._vectorizer is None or self._matrix is None:
            raise RagError(
                "build_index must be called before retrieve", "RAG_INDEX_NOT_BUILT"
            )
        if not query.strip():
            raise RagError("query must not be empty", "RAG_EMPTY_QUERY")
        if top_k <= 0:
            raise RagError("top_k must be positive", "RAG_INVALID_TOP_K")

        query_vector = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self._matrix).ravel()
        ranked_indices = scores.argsort()[::-1][:top_k]

        return [
            RetrievalResult(
                text=self._chunks[index].text,
                source=self._chunks[index].source,
                score=float(scores[index]),
                chunk_id=self._chunks[index].chunk_id,
            )
            for index in ranked_indices
        ]
