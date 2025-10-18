"""
Mathematical and scoring utilities.
"""
import numpy as np
from typing import List


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile of a list of values.
    
    Args:
        values: List of numeric values
        percentile: Percentile to calculate (0-100)
    
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    return float(np.percentile(values, percentile))


def calculate_mean(values: List[float]) -> float:
    """
    Calculate mean of a list of values.
    
    Args:
        values: List of numeric values
    
    Returns:
        Mean value
    """
    if not values:
        return 0.0
    return float(np.mean(values))


def normalize_scores(scores: np.ndarray, method: str = "minmax") -> np.ndarray:
    """
    Normalize scores to [0, 1] range.
    
    Args:
        scores: Array of scores
        method: Normalization method ("minmax" or "standard")
    
    Returns:
        Normalized scores
    """
    if len(scores) == 0:
        return scores
    
    if method == "minmax":
        min_score = scores.min()
        max_score = scores.max()
        if max_score == min_score:
            return np.ones_like(scores)
        return (scores - min_score) / (max_score - min_score)
    elif method == "standard":
        mean = scores.mean()
        std = scores.std()
        if std == 0:
            return np.zeros_like(scores)
        return (scores - mean) / std
    else:
        raise ValueError(f"Unknown normalization method: {method}")
