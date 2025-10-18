"""
Retrieval service - high-level business logic for retrieval operations.
Orchestrates index, scoring, and result formatting.
"""
from typing import List
from app.models.document import ScoredDocument
from app.models.retrieval_config import RetrievalConfig
from app.retrieval.index import get_index
from app.schemas.answer import RetrievedSnippet


class RetrievalService:
    """
    Service for managing retrieval operations.
    Provides high-level API independent of specific index implementation.
    """
    
    def __init__(self):
        self._index = None
    
    def initialize(self):
        """Initialize the retrieval index."""
        from app.retrieval.index import initialize_index
        initialize_index()
        self._index = get_index()
    
    def retrieve_documents(
        self, 
        query: str, 
        config: RetrievalConfig
    ) -> List[ScoredDocument]:
        """
        Retrieve documents for a query using specified config.
        
        Args:
            query: Search query
            config: Retrieval configuration
        
        Returns:
            List of scored documents
        """
        if self._index is None:
            self._index = get_index()
        
        # Retrieve using the index
        snippets = self._index.retrieve(
            query=query,
            k=config.top_k,
            kind=config.similarity_metric
        )
        
        # Convert to domain models
        scored_docs = []
        for snippet in snippets:
            from app.models.document import Document
            doc = Document(id=snippet.id, text=snippet.text)
            scored_doc = ScoredDocument(document=doc, score=snippet.score)
            scored_docs.append(scored_doc)
        
        return scored_docs
    
    def check_confidence(self, scored_docs: List[ScoredDocument], threshold: float) -> bool:
        """
        Check if retrieval confidence is low.
        
        Args:
            scored_docs: List of retrieved documents with scores
            threshold: Confidence threshold
        
        Returns:
            True if confidence is low (max score < threshold)
        """
        if not scored_docs:
            return True
        
        max_score = max(doc.score for doc in scored_docs)
        return max_score < threshold
    
    def format_for_api(self, scored_docs: List[ScoredDocument]) -> List[RetrievedSnippet]:
        """
        Format scored documents for API response.
        
        Args:
            scored_docs: Domain model documents
        
        Returns:
            API schema snippets
        """
        return [
            RetrievedSnippet(
                id=doc.document.id,
                text=doc.document.text,
                score=doc.score
            )
            for doc in scored_docs
        ]


# Singleton instance
_retrieval_service: RetrievalService = None


def get_retrieval_service() -> RetrievalService:
    """Get the global retrieval service instance."""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
