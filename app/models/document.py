"""
Domain model for a document/snippet in the corpus.
Separates internal representation from API response schemas.
"""
from dataclasses import dataclass


@dataclass
class Document:
    """A document in the corpus."""
    id: str
    text: str
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("Document id cannot be empty")
        if not self.text:
            raise ValueError("Document text cannot be empty")


@dataclass
class ScoredDocument:
    """A document with a similarity score."""
    document: Document
    score: float
    
    def __post_init__(self):
        if self.score < 0:
            raise ValueError("Score cannot be negative")
