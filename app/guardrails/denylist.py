"""
Denylist guardrail: blocks queries containing harmful phrases.
Deterministic, auditable, zero-ML baseline safety control.
"""
from typing import Optional

# Phrases that trigger the guardrail (case-insensitive)
DENYLIST = [
    "instructions for illegal",
    "how to build a weapon",
    "self-harm",
    "violent wrongdoing",
    "bypass security",
    "create malware",
    "hack into",
    "steal credentials",
    "child exploitation",
    "terrorist attack"
]


def query_is_denied(query: str) -> Optional[str]:
    """
    Check if query contains any denied phrases.
    
    Args:
        query: User's query text
    
    Returns:
        Matched phrase if denied, None otherwise
    """
    query_lower = query.lower()
    
    for phrase in DENYLIST:
        if phrase in query_lower:
            return phrase
    
    return None
