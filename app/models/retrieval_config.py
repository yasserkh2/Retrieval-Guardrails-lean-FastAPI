"""
Configuration for retrieval operations.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass
class RetrievalConfig:
    """Configuration for a retrieval operation."""
    similarity_metric: Literal["cosine", "dot"]
    top_k: int
    
    def __post_init__(self):
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        if self.top_k > 10:
            raise ValueError("top_k cannot exceed 10")
    
    @property
    def description(self) -> str:
        """Human-readable config description."""
        return f"{self.similarity_metric},k={self.top_k}"
    
    @classmethod
    def from_preset(cls, preset: Literal["cos3", "dot5"]) -> "RetrievalConfig":
        """Create config from preset name."""
        if preset == "cos3":
            return cls(similarity_metric="cosine", top_k=3)
        elif preset == "dot5":
            return cls(similarity_metric="dot", top_k=5)
        else:
            raise ValueError(f"Unknown preset: {preset}")
    
    @classmethod
    def default(cls) -> "RetrievalConfig":
        """Return default configuration."""
        from app.core import config
        return cls(
            similarity_metric=config.CONFIG_DEFAULT,  # type: ignore
            top_k=config.TOP_K_DEFAULT
        )
