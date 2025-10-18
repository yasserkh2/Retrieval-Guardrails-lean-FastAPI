"""
Metrics aggregation model.
Encapsulates all monitoring metrics in one place.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class MetricsSnapshot:
    """Snapshot of current metrics state."""
    total_requests: int
    denylist_hits: int
    low_confidence_count: int
    latency_samples: List[float]
    
    @property
    def low_confidence_rate(self) -> float:
        """Calculate low confidence rate."""
        if self.total_requests == 0:
            return 0.0
        return self.low_confidence_count / self.total_requests
