"""
Text preprocessing utilities.
"""
import re


def normalize_text(text: str) -> str:
    """
    Normalize text for processing.
    - Convert to lowercase
    - Strip extra whitespace
    """
    text = text.lower().strip()
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length, adding ellipsis if needed.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
