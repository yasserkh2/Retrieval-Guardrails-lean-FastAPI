"""
Metrics collection and middleware for monitoring.
Tracks latency (mean, p95) and request counters.
"""
import time
import numpy as np
from typing import List
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsCollector:
    """
    In-memory metrics storage.
    Tracks request counts, latency samples, and guardrail hits.
    """
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.latency_samples: List[float] = []
        
        # Counters
        self.total_requests = 0
        self.denylist_hits = 0
        self.low_confidence_count = 0
    
    def record_latency(self, latency_ms: float):
        """Record a latency sample (in milliseconds)."""
        self.latency_samples.append(latency_ms)
        
        # Keep only recent samples to avoid unbounded growth
        if len(self.latency_samples) > self.max_samples:
            self.latency_samples = self.latency_samples[-self.max_samples:]
    
    def increment_total_requests(self):
        """Increment total request counter."""
        self.total_requests += 1
    
    def increment_denylist_hits(self):
        """Increment denylist counter."""
        self.denylist_hits += 1
    
    def increment_low_confidence(self):
        """Increment low confidence counter."""
        self.low_confidence_count += 1
    
    def get_latency_mean(self) -> float:
        """Calculate mean latency."""
        if not self.latency_samples:
            return 0.0
        return float(np.mean(self.latency_samples))
    
    def get_latency_p95(self) -> float:
        """Calculate 95th percentile latency (tail latency)."""
        if not self.latency_samples:
            return 0.0
        return float(np.percentile(self.latency_samples, 95))
    
    def get_low_confidence_rate(self) -> float:
        """Calculate fraction of requests with low confidence."""
        if self.total_requests == 0:
            return 0.0
        return self.low_confidence_count / self.total_requests


# Global metrics instance
metrics = MetricsCollector()


class LatencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that measures request latency and stores samples.
    Runs for all requests to the app.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.perf_counter()
        
        # Process request
        response = await call_next(request)
        
        # Calculate latency
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        # Record latency
        metrics.record_latency(latency_ms)
        
        # Add latency header for debugging
        response.headers["X-Latency-Ms"] = f"{latency_ms:.2f}"
        
        return response


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics
