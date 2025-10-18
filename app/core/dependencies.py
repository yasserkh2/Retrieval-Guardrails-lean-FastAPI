"""
FastAPI dependency injection utilities.
Provides clean access to services and configurations.
"""
from typing import Annotated
from fastapi import Depends

from app.services.retrieval_service import get_retrieval_service, RetrievalService
from app.services.guardrail_service import get_guardrail_service, GuardrailService
from app.services.answer_service import get_answer_service, AnswerSynthesisService
from app.services.metrics_service import get_metrics_service, MetricsService
from app.core.metrics import get_metrics, MetricsCollector


# Type aliases for cleaner endpoint signatures
RetrievalServiceDep = Annotated[RetrievalService, Depends(get_retrieval_service)]
GuardrailServiceDep = Annotated[GuardrailService, Depends(get_guardrail_service)]
AnswerServiceDep = Annotated[AnswerSynthesisService, Depends(get_answer_service)]
MetricsServiceDep = Annotated[MetricsService, Depends(get_metrics_service)]
MetricsCollectorDep = Annotated[MetricsCollector, Depends(get_metrics)]
