"""
API endpoints: POST /answer and GET /metrics.
Core retrieval-augmented answering logic with guardrails.
Refactored to use service layer for better separation of concerns.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.answer import AnswerRequest, AnswerResponse, MetricsResponse
from app.core import config
from app.core.dependencies import (
    RetrievalServiceDep,
    GuardrailServiceDep,
    AnswerServiceDep,
    MetricsServiceDep,
    MetricsCollectorDep
)
from app.models.retrieval_config import RetrievalConfig
from app.models.metrics import MetricsSnapshot


router = APIRouter()


@router.post("/answer", response_model=AnswerResponse)
async def answer_query(
    request: AnswerRequest,
    retrieval_service: RetrievalServiceDep,
    guardrail_service: GuardrailServiceDep,
    answer_service: AnswerServiceDep,
    metrics_collector: MetricsCollectorDep
):
    """
    Answer a query using retrieval-augmented approach.
    
    Flow:
    1. Guardrail check (denylist)
    2. Choose config (cosine,k=3 or dot,k=5)
    3. Retrieve top-k snippets
    4. Detect low confidence
    5. Synthesize naive answer
    """
    metrics_collector.increment_total_requests()
    
    # Step 1: Guardrail check
    guardrail_result = guardrail_service.check_query(request.query)
    if guardrail_result.blocked:
        metrics_collector.increment_denylist_hits()
        raise HTTPException(
            status_code=400,
            detail=f"Query blocked by guardrail. {guardrail_result.reason}"
        )
    
    # Step 2: Choose retrieval config
    if request.config == "dot5":
        retrieval_config = RetrievalConfig.from_preset("dot5")
    elif request.config == "cos3":
        retrieval_config = RetrievalConfig.from_preset("cos3")
    else:
        # Use defaults from environment
        retrieval_config = RetrievalConfig.default()
    
    # Override k if specified
    if request.top_k is not None:
        retrieval_config.top_k = request.top_k
    
    # Step 3: Retrieve documents
    scored_docs = retrieval_service.retrieve_documents(request.query, retrieval_config)
    
    # Step 4: Check for low confidence
    low_confidence = retrieval_service.check_confidence(
        scored_docs, 
        config.LOW_CONF_THRESHOLD
    )
    
    if low_confidence:
        metrics_collector.increment_low_confidence()
    
    # Step 5: Synthesize answer
    answer = answer_service.synthesize(request.query, scored_docs)
    
    # Step 6: Format response
    snippets = retrieval_service.format_for_api(scored_docs)
    
    return AnswerResponse(
        answer=answer,
        snippets=snippets,
        config_used=retrieval_config.description,
        low_confidence=low_confidence
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    metrics_service: MetricsServiceDep,
    metrics_collector: MetricsCollectorDep
):
    """
    Return system monitoring metrics.
    
    Metrics:
    - Request counts (total, denylist hits, low confidence)
    - Latency stats (mean, p95)
    - Low confidence rate
    """
    # Create snapshot from current metrics
    snapshot = MetricsSnapshot(
        total_requests=metrics_collector.total_requests,
        denylist_hits=metrics_collector.denylist_hits,
        low_confidence_count=metrics_collector.low_confidence_count,
        latency_samples=metrics_collector.latency_samples.copy()
    )
    
    # Generate report using metrics service
    report = metrics_service.create_metrics_report(snapshot)
    
    return MetricsResponse(**report)
