"""
Guardrail service - encapsulates all guardrail logic.
Makes it easy to add more guardrails beyond denylist.
"""
from typing import Optional, Protocol
from app.guardrails.denylist import query_is_denied as denylist_check


class GuardrailResult:
    """Result of a guardrail check."""
    
    def __init__(self, blocked: bool, reason: Optional[str] = None):
        self.blocked = blocked
        self.reason = reason
    
    def is_safe(self) -> bool:
        """Check if query passed all guardrails."""
        return not self.blocked


class Guardrail(Protocol):
    """Protocol for guardrail implementations."""
    
    def check(self, query: str) -> GuardrailResult:
        """Check if query violates guardrail."""
        ...


class DenylistGuardrail:
    """Denylist-based guardrail implementation."""
    
    def check(self, query: str) -> GuardrailResult:
        """Check query against denylist."""
        matched_phrase = denylist_check(query)
        if matched_phrase:
            return GuardrailResult(
                blocked=True,
                reason=f"Matched denied phrase: '{matched_phrase}'"
            )
        return GuardrailResult(blocked=False)


class GuardrailService:
    """
    Orchestrates multiple guardrails.
    Runs all checks and returns first failure or success.
    """
    
    def __init__(self):
        self.guardrails: list[Guardrail] = [
            DenylistGuardrail()
        ]
    
    def check_query(self, query: str) -> GuardrailResult:
        """
        Run all guardrails on a query.
        Returns first failure or success if all pass.
        """
        for guardrail in self.guardrails:
            result = guardrail.check(query)
            if result.blocked:
                return result
        
        return GuardrailResult(blocked=False)
    
    def add_guardrail(self, guardrail: Guardrail):
        """Add a new guardrail to the service."""
        self.guardrails.append(guardrail)


# Global service instance
_guardrail_service: Optional[GuardrailService] = None


def get_guardrail_service() -> GuardrailService:
    """Get or create the global guardrail service."""
    global _guardrail_service
    if _guardrail_service is None:
        _guardrail_service = GuardrailService()
    return _guardrail_service
