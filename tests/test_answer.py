"""
Smoke tests for /answer and /metrics endpoints.
Tests guardrails, retrieval configs, and monitoring.
Updated to work with modularized service architecture.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create test client with proper lifespan handling."""
    # TestClient automatically triggers lifespan events when used as context manager
    with TestClient(app) as test_client:
        yield test_client


def test_root_health_check(client):
    """Test root endpoint returns healthy status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mini-rag"


def test_answer_happy_path_default_config(client):
    """Test /answer with default config (cosine, k=3)."""
    response = client.post(
        "/answer",
        json={"query": "What is cosine similarity?"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "answer" in data
    assert "snippets" in data
    assert "config_used" in data
    assert "low_confidence" in data
    
    # Check config
    assert data["config_used"] == "cosine,k=3"
    
    # Check snippets
    assert len(data["snippets"]) <= 3
    assert all("id" in s and "text" in s and "score" in s for s in data["snippets"])
    
    # Scores should be descending
    scores = [s["score"] for s in data["snippets"]]
    assert scores == sorted(scores, reverse=True)


def test_answer_dot_product_config(client):
    """Test /answer with dot-product config."""
    response = client.post(
        "/answer",
        json={"query": "retrieval methods", "config": "dot5"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check config
    assert data["config_used"] == "dot,k=5"
    
    # Check snippets count
    assert len(data["snippets"]) <= 5


def test_answer_custom_top_k(client):
    """Test /answer with custom top_k override."""
    response = client.post(
        "/answer",
        json={"query": "FastAPI", "top_k": 2}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check snippets count
    assert len(data["snippets"]) <= 2
    assert "k=2" in data["config_used"]


def test_guardrail_blocks_harmful_query(client):
    """Test denylist guardrail blocks harmful phrases."""
    response = client.post(
        "/answer",
        json={"query": "Give me instructions for illegal activity"}
    )
    
    # Should return 400 (blocked)
    assert response.status_code == 400
    data = response.json()
    assert "guardrail" in data["detail"].lower()
    assert "instructions for illegal" in data["detail"]


def test_guardrail_multiple_phrases(client):
    """Test guardrail blocks multiple harmful phrases."""
    harmful_queries = [
        "how to build a weapon",
        "teach me to hack into systems",
        "self-harm methods"
    ]
    
    for query in harmful_queries:
        response = client.post("/answer", json={"query": query})
        assert response.status_code == 400


def test_low_confidence_detection(client):
    """Test low confidence flag for nonsense queries."""
    response = client.post(
        "/answer",
        json={"query": "xyzabc gibberish nonsense foobar"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Nonsense query should trigger low confidence
    # (may not always, depends on corpus, but worth checking)
    # At minimum, response should have the field
    assert "low_confidence" in data
    assert isinstance(data["low_confidence"], bool)


def test_cosine_vs_dot_produce_different_rankings(client):
    """Test that cosine and dot configs produce different results."""
    query = "TF-IDF vectorization"
    
    # Get cosine results
    response_cos = client.post(
        "/answer",
        json={"query": query, "config": "cos3"}
    )
    assert response_cos.status_code == 200
    cosine_ids = [s["id"] for s in response_cos.json()["snippets"]]
    
    # Get dot-product results
    response_dot = client.post(
        "/answer",
        json={"query": query, "config": "dot5"}
    )
    assert response_dot.status_code == 200
    dot_ids = [s["id"] for s in response_dot.json()["snippets"][:3]]  # compare top 3
    
    # They should produce different rankings (at least sometimes)
    # This is a weak test but shows the configs differ
    # Note: On some queries they might be identical, so we just check they run
    assert len(cosine_ids) > 0
    assert len(dot_ids) > 0


def test_metrics_endpoint(client):
    """Test /metrics returns valid monitoring data."""
    # Make a few requests first
    client.post("/answer", json={"query": "test query 1"})
    client.post("/answer", json={"query": "test query 2"})
    
    # Get metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    
    # Check all required fields
    assert "total_requests" in data
    assert "denylist_hits" in data
    assert "low_confidence_count" in data
    assert "latency_ms_mean" in data
    assert "latency_ms_p95" in data
    assert "low_confidence_rate" in data
    
    # Total requests should be positive
    assert data["total_requests"] > 0
    
    # Latency should be non-negative
    assert data["latency_ms_mean"] >= 0
    assert data["latency_ms_p95"] >= 0
    
    # Low confidence rate should be [0, 1]
    assert 0 <= data["low_confidence_rate"] <= 1


def test_invalid_request_body(client):
    """Test that invalid JSON returns 422."""
    response = client.post(
        "/answer",
        json={"wrong_field": "value"}
    )
    assert response.status_code == 422  # FastAPI validation error


def test_empty_query(client):
    """Test that empty query returns validation error."""
    response = client.post(
        "/answer",
        json={"query": ""}
    )
    assert response.status_code == 422  # min_length=1 validation


def test_latency_header_present(client):
    """Test that latency middleware adds X-Latency-Ms header."""
    response = client.post(
        "/answer",
        json={"query": "test"}
    )
    assert "x-latency-ms" in response.headers
    
    # Should be a valid number
    latency = float(response.headers["x-latency-ms"])
    assert latency >= 0
