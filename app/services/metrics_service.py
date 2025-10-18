"""
Metrics service - business logic for metrics computation.
Separates calculation from storage/middleware concerns.
"""
from typing import List
from app.models.metrics import MetricsSnapshot
from app.utils.scoring import calculate_mean, calculate_percentile


class MetricsService:
    """
    Service for computing metrics from raw data.
    Separates business logic from storage.
    """
    
    def compute_latency_stats(self, latency_samples: List[float]) -> dict:
        """
        Compute latency statistics.
        
        Args:
            latency_samples: List of latency measurements in ms
        
        Returns:
            Dict with mean and p95 latency
        """
        return {
            "mean": calculate_mean(latency_samples),
            "p95": calculate_percentile(latency_samples, 95)
        }
    
    def compute_confidence_metrics(
        self, 
        low_confidence_count: int, 
        total_requests: int
    ) -> dict:
        """
        Compute confidence-related metrics.
        
        Returns:
            Dict with count and rate
        """
        rate = 0.0 if total_requests == 0 else low_confidence_count / total_requests
        return {
            "count": low_confidence_count,
            "rate": rate
        }
    
    def create_metrics_report(self, snapshot: MetricsSnapshot) -> dict:
        """
        Create a comprehensive metrics report from a snapshot.
        
        Args:
            snapshot: Current metrics snapshot
        
        Returns:
            Formatted metrics report
        """
        latency_stats = self.compute_latency_stats(snapshot.latency_samples)
        confidence_stats = self.compute_confidence_metrics(
            snapshot.low_confidence_count,
            snapshot.total_requests
        )
        
        return {
            "total_requests": snapshot.total_requests,
            "denylist_hits": snapshot.denylist_hits,
            "low_confidence_count": confidence_stats["count"],
            "latency_ms_mean": latency_stats["mean"],
            "latency_ms_p95": latency_stats["p95"],
            "low_confidence_rate": confidence_stats["rate"]
        }


# Singleton instance
_metrics_service: MetricsService = None


def get_metrics_service() -> MetricsService:
    """Get the global metrics service instance."""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service
