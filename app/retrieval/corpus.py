"""
Corpus initialization and access.
Uses repository pattern for better testability and flexibility.
"""
from app.retrieval.repository import CorpusRepository, create_default_corpus

# Global corpus repository instance
_corpus_repository: CorpusRepository = None


def initialize_corpus() -> CorpusRepository:
    """
    Initialize the corpus repository with default documents.
    Call once at startup.
    """
    global _corpus_repository
    _corpus_repository = CorpusRepository()
    documents = create_default_corpus()
    _corpus_repository.load_documents(documents)
    return _corpus_repository


def get_corpus() -> CorpusRepository:
    """Get the initialized corpus repository."""
    if _corpus_repository is None:
        raise RuntimeError("Corpus not initialized. Call initialize_corpus() first.")
    return _corpus_repository
