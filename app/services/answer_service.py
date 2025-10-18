"""
Answer synthesis service - creates responses from retrieved documents.
Handles naive answer generation (can be extended with LLM later).
"""
from typing import List
from app.models.document import ScoredDocument
from app.utils.text import truncate_text


class AnswerSynthesisService:
    """
    Service for synthesizing answers from retrieved documents.
    Currently uses naive concatenation; can be upgraded to LLM generation.
    """
    
    def synthesize(
        self, 
        query: str, 
        documents: List[ScoredDocument],
        max_snippets: int = 2
    ) -> str:
        """
        Synthesize an answer from retrieved documents.
        
        Args:
            query: Original query (for context)
            documents: Retrieved documents with scores
            max_snippets: Maximum number of snippets to include
        
        Returns:
            Synthesized answer string
        """
        if not documents:
            return "No relevant information found for your query."
        
        # Use top N documents
        top_docs = documents[:max_snippets]
        
        if len(top_docs) == 1:
            return f"Based on available information: {top_docs[0].document.text}"
        
        # Combine multiple documents
        first_text = top_docs[0].document.text
        second_text = top_docs[1].document.text
        
        return f"Based on available information: {first_text} Additionally, {second_text}"
    
    def synthesize_with_confidence_warning(
        self,
        query: str,
        documents: List[ScoredDocument],
        is_low_confidence: bool
    ) -> str:
        """
        Synthesize answer with optional low-confidence warning.
        
        Args:
            query: Original query
            documents: Retrieved documents
            is_low_confidence: Whether confidence is low
        
        Returns:
            Synthesized answer with optional warning
        """
        answer = self.synthesize(query, documents)
        
        if is_low_confidence and documents:
            answer = f"Note: Low confidence in results. {answer}"
        
        return answer


# Singleton instance
_answer_service: AnswerSynthesisService = None


def get_answer_service() -> AnswerSynthesisService:
    """Get the global answer synthesis service instance."""
    global _answer_service
    if _answer_service is None:
        _answer_service = AnswerSynthesisService()
    return _answer_service
