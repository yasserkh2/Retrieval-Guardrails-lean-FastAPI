"""
Pydantic models for the /answer endpoint.
Provides typed request/response with automatic validation and OpenAPI docs.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnswerRequest(BaseModel):
    """Request payload for POST /answer."""
    
    query: str = Field(..., description="User's query text", min_length=1)
    config: Optional[Literal["cos3", "dot5"]] = Field(
        None, 
        description="Retrieval config: 'cos3' (cosine,k=3) or 'dot5' (dot-product,k=5)"
    )
    top_k: Optional[int] = Field(
        None, 
        description="Override number of snippets to retrieve (1-10)",
        ge=1,
        le=10
    )


class RetrievedSnippet(BaseModel):
    """A single retrieved snippet with score."""
    
    id: str = Field(..., description="Snippet identifier")
    text: str = Field(..., description="Snippet content")
    score: float = Field(..., description="Similarity score (0-1)")


class AnswerResponse(BaseModel):
    """Response from POST /answer."""
    
    answer: str = Field(..., description="Synthesized answer from top snippets")
    snippets: List[RetrievedSnippet] = Field(..., description="Ranked retrieved snippets")
    config_used: str = Field(..., description="Config applied (e.g., 'cosine,k=3')")
    low_confidence: bool = Field(..., description="True if max score < threshold")


class MetricsResponse(BaseModel):
    """Response from GET /metrics."""
    
    total_requests: int = Field(..., description="Total /answer requests processed")
    denylist_hits: int = Field(..., description="Requests blocked by guardrail")
    low_confidence_count: int = Field(..., description="Requests with low confidence")
    latency_ms_mean: float = Field(..., description="Mean request latency (ms)")
    latency_ms_p95: float = Field(..., description="95th percentile latency (ms)")
    low_confidence_rate: float = Field(..., description="Fraction of low-confidence requests")
