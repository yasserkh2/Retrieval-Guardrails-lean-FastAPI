"""
TF-IDF-based retrieval engine with cosine and dot-product scoring.
Builds index once at startup, exposes score() and retrieve() APIs.
"""
import numpy as np
from typing import List, Literal
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from app.retrieval.corpus import get_corpus
from app.schemas.answer import RetrievedSnippet


class RetrievalIndex:
    """
    TF-IDF index supporting cosine and dot-product similarity.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=500
        )
        # Get documents from corpus repository
        corpus = get_corpus()
        self.doc_ids = corpus.get_ids()
        self.doc_texts = corpus.get_texts()
        
        # Build TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.doc_texts)
        
        # Pre-compute normalized matrix for cosine similarity
        self.normalized_matrix = normalize(self.tfidf_matrix, norm='l2', axis=1)
    
    def score(self, query: str, kind: Literal["cosine", "dot"] = "cosine") -> np.ndarray:
        """
        Compute similarity scores for query against all documents.
        
        Args:
            query: Query text
            kind: "cosine" (normalized, angle-based) or "dot" (raw, magnitude-sensitive)
        
        Returns:
            Array of scores, one per document
        """
        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        
        if kind == "cosine":
            # Normalize query and use normalized doc matrix
            query_normalized = normalize(query_vec, norm='l2', axis=1)
            scores = (self.normalized_matrix @ query_normalized.T).toarray().flatten()
        else:  # dot
            # Use raw TF-IDF (magnitude matters)
            scores = (self.tfidf_matrix @ query_vec.T).toarray().flatten()
        
        return scores
    
    def retrieve(
        self, 
        query: str, 
        k: int = 3, 
        kind: Literal["cosine", "dot"] = "cosine"
    ) -> List[RetrievedSnippet]:
        """
        Retrieve top-k most similar documents.
        
        Args:
            query: Query text
            k: Number of results to return
            kind: Similarity metric
        
        Returns:
            List of RetrievedSnippet objects, sorted by score (descending)
        """
        scores = self.score(query, kind=kind)
        
        # Get top-k indices
        top_k_indices = np.argsort(scores)[::-1][:k]
        
        # Build result snippets
        snippets = [
            RetrievedSnippet(
                id=self.doc_ids[idx],
                text=self.doc_texts[idx],
                score=float(scores[idx])
            )
            for idx in top_k_indices
        ]
        
        return snippets


# Global instance (initialized at startup)
retrieval_index: RetrievalIndex = None


def initialize_index():
    """Build the TF-IDF index. Call once at app startup."""
    from app.retrieval.corpus import initialize_corpus
    
    # Initialize corpus first
    initialize_corpus()
    
    # Then build index
    global retrieval_index
    retrieval_index = RetrievalIndex()


def get_index() -> RetrievalIndex:
    """Get the initialized retrieval index."""
    if retrieval_index is None:
        raise RuntimeError("Retrieval index not initialized. Call initialize_index() first.")
    return retrieval_index
