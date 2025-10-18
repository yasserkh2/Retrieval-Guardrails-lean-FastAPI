"""
Corpus repository - manages document storage and access.
Provides abstraction over the data source (currently in-memory list).
"""
from typing import List, Optional
from app.models.document import Document


class CorpusRepository:
    """
    Repository for managing the document corpus.
    Provides a clean interface for document access.
    """
    
    def __init__(self):
        self._documents: List[Document] = []
    
    def load_documents(self, documents: List[Document]):
        """Load documents into the repository."""
        self._documents = documents
    
    def get_all(self) -> List[Document]:
        """Get all documents."""
        return self._documents.copy()
    
    def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        for doc in self._documents:
            if doc.id == doc_id:
                return doc
        return None
    
    def get_texts(self) -> List[str]:
        """Get all document texts."""
        return [doc.text for doc in self._documents]
    
    def get_ids(self) -> List[str]:
        """Get all document IDs."""
        return [doc.id for doc in self._documents]
    
    def count(self) -> int:
        """Get total number of documents."""
        return len(self._documents)


# Create corpus data
def create_default_corpus() -> List[Document]:
    """
    Create the default corpus of 12 snippets.
    Separated from repository for easy testing/mocking.
    """
    return [
        Document(
            id="s1",
            text="Cosine similarity measures the angle between two vectors, normalizing for magnitude. It's ideal for text comparison where document length shouldn't dominate."
        ),
        Document(
            id="s2",
            text="Dot product similarity considers both direction and magnitude of vectors. Longer documents with more terms can score higher even if conceptually similar."
        ),
        Document(
            id="s3",
            text="TF-IDF (Term Frequency-Inverse Document Frequency) weights terms by their importance in a document relative to the entire corpus. Common words get lower weights."
        ),
        Document(
            id="s4",
            text="Guardrails in AI systems include content filters, rate limits, and policy enforcement. They protect against harmful outputs and resource abuse."
        ),
        Document(
            id="s5",
            text="FastAPI provides automatic request validation using Pydantic models. Invalid inputs return HTTP 422 with detailed error messages."
        ),
        Document(
            id="s6",
            text="Latency percentiles (p95, p99) matter more than averages in production systems. Tail latency affects user experience and SLA compliance."
        ),
        Document(
            id="s7",
            text="The twelve-factor app methodology recommends storing configuration in environment variables, not code. This enables clean separation between environments."
        ),
        Document(
            id="s8",
            text="Low-confidence detection helps identify when a retrieval system may be returning poor results. It's a simple drift indicator for monitoring."
        ),
        Document(
            id="s9",
            text="Middleware in FastAPI runs before and after request processing. It's perfect for cross-cutting concerns like logging, metrics, and timing."
        ),
        Document(
            id="s10",
            text="Top-k retrieval returns the k most similar documents. Higher k increases recall but may reduce precision by including noisier results."
        ),
        Document(
            id="s11",
            text="Denylist guardrails block specific phrases or patterns. They're deterministic, auditable, and require no ML models—ideal for baseline safety."
        ),
        Document(
            id="s12",
            text="Vector normalization (L2) scales vectors to unit length. This makes dot product equivalent to cosine similarity and removes magnitude bias."
        )
    ]
