"""
Denylist guardrail with TF-IDF semantic checking.
Blocks queries that are semantically similar to harmful phrases.
"""
from typing import List, Optional
import numpy as np
from sklearn.preprocessing import normalize

# Harmful phrases to block
DENYLIST: List[str] = [
    "instructions for illegal activity",
    "how to build a weapon",
    "self-harm methods",
    "violent wrongdoing instructions",
    "bypass safety mechanisms",
    "create malware code",
    "fraud techniques tutorial",
    "illegal drug manufacturing",
    "hack into systems",
    "steal personal information"
]

# TF-IDF semantic matching configuration
TFIDF_THRESHOLD = 0.30  # Cosine similarity threshold (tune based on testing)
USE_SEMANTIC_CHECK = True  # Toggle semantic checking
DEBUG_SIMILARITY_SCORES = False  # Print all similarity scores for debugging

# Global variables for TF-IDF vectors (initialized at startup)
_deny_vectors_tfidf = None
_vectorizer = None


def initialize_denylist_vectors(vectorizer):
    """
    Initialize TF-IDF vectors for denylist phrases.
    Creates a NEW vectorizer trained on denylist phrases for better semantic matching.
    
    Args:
        vectorizer: The fitted TfidfVectorizer from retrieval index (for reference)
    """
    global _deny_vectors_tfidf, _vectorizer
    
    try:
        # Create a NEW vectorizer specifically for guardrails
        # This ensures denylist phrases have proper vocabulary coverage
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        _vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Capture both unigrams and bigrams
            max_features=500,     # Limit vocabulary size
            lowercase=True
        )
        
        # Fit vectorizer on denylist phrases
        _vectorizer.fit(DENYLIST)
        
        # Transform denylist phrases to TF-IDF vectors
        deny_matrix = _vectorizer.transform(DENYLIST)
        
        # L2-normalize for cosine similarity (dot product = cosine)
        _deny_vectors_tfidf = normalize(deny_matrix, axis=1)
        
        print(f"✅ Guardrails: Initialized {len(DENYLIST)} denylist vectors with {len(_vectorizer.vocabulary_)} features")
    except Exception as e:
        print(f"⚠️ Guardrails: Failed to initialize TF-IDF vectors: {e}")
        _deny_vectors_tfidf = None
        _vectorizer = None


def _compute_cosine_similarity(query_vec, deny_matrix) -> np.ndarray:
    """
    Compute cosine similarity between query and denylist vectors.
    
    Args:
        query_vec: Normalized query vector (1 x vocab_size)
        deny_matrix: Normalized denylist vectors (N x vocab_size)
    
    Returns:
        Array of similarity scores (N,)
    """
    # Matrix multiplication: (1 x D) @ (D x N) = (1 x N)
    similarities = query_vec @ deny_matrix.T
    return similarities.toarray().ravel()


def _check_semantic_similarity(query: str) -> Optional[str]:
    """
    Check if query is semantically similar to any denylist phrase.
    Uses TF-IDF vectors and cosine similarity.
    
    Args:
        query: User's input query
        
    Returns:
        Matched denylist phrase if blocked, None otherwise
    """
    if not USE_SEMANTIC_CHECK or _deny_vectors_tfidf is None or _vectorizer is None:
        return None
    
    try:
        # Transform query to TF-IDF vector
        query_vec = _vectorizer.transform([query])
        
        # Normalize for cosine similarity
        query_vec_norm = normalize(query_vec, axis=1)
        
        # Compute similarity with all denylist phrases
        similarities = _compute_cosine_similarity(query_vec_norm, _deny_vectors_tfidf)
        
        # Find best match
        best_match_idx = int(np.argmax(similarities))
        best_score = similarities[best_match_idx]
        
        # Debug: print all scores
        if DEBUG_SIMILARITY_SCORES:
            print(f"\n🔍 Similarity scores for query: '{query}'")
            for i, (phrase, score) in enumerate(zip(DENYLIST, similarities)):
                marker = "⚠️ " if score >= TFIDF_THRESHOLD else "   "
                print(f"{marker}  [{i}] {score:.3f} - {phrase}")
            print(f"🎯 Best match: [{best_match_idx}] {best_score:.3f} (threshold: {TFIDF_THRESHOLD})\n")
        
        # Block if above threshold
        if best_score >= TFIDF_THRESHOLD:
            matched_phrase = DENYLIST[best_match_idx]
            print(f"🛡️ Semantic guardrail triggered: '{query}' → '{matched_phrase}' (score: {best_score:.3f})")
            return matched_phrase
        
    except Exception as e:
        print(f"⚠️ Semantic guardrail check failed: {e}")
    
    return None


def _check_substring_match(query: str) -> Optional[str]:
    """
    Check if query contains any denylist phrase as substring.
    Fast deterministic check (fallback).
    
    Args:
        query: User's input query
        
    Returns:
        Matched denylist phrase if blocked, None otherwise
    """
    query_lower = query.lower()
    
    for phrase in DENYLIST:
        if phrase in query_lower:
            print(f"🛡️ Substring guardrail triggered: '{query}' → '{phrase}'")
            return phrase
    
    return None


def check_query(query: str) -> Optional[str]:
    """
    Check if query should be blocked by guardrails.
    
    Strategy:
    1. Fast substring check first (deterministic)
    2. If no match, try semantic TF-IDF check
    3. Return matched phrase if blocked, None if allowed
    
    Args:
        query: User's input query string
        
    Returns:
        Matched denylist phrase if query is blocked, None if allowed
    """
    if not query or not query.strip():
        return None
    
    # Strategy 1: Fast substring check (catches exact/near-exact matches)
    substring_match = _check_substring_match(query)
    if substring_match:
        return substring_match
    
    # Strategy 2: Semantic similarity check (catches paraphrases)
    semantic_match = _check_semantic_similarity(query)
    if semantic_match:
        return semantic_match
    
    # No match - allow query
    return None


# Backward compatibility alias
def query_is_denied(query: str) -> Optional[str]:
    """
    Legacy function name. Use check_query() instead.
    """
    return check_query(query)
