"""
Manual API Testing Script
Run this while your server is running on http://127.0.0.1:8000
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_test(test_name, response):
    """Pretty print test results."""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print()


def main():
    print("🧪 Starting Manual API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{BASE_URL}/")
        print_test("Health Check", response)
        assert response.status_code == 200, "Health check failed"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Default Config (Cosine, k=3)
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "What is cosine similarity?"}
        )
        print_test("Default Config (Cosine, k=3)", response)
        assert response.status_code == 200, "Request failed"
        data = response.json()
        assert "answer" in data, "Missing answer field"
        assert "snippets" in data, "Missing snippets field"
        assert data["config_used"] == "cosine,k=3", "Wrong config"
        assert len(data["snippets"]) <= 3, "Too many snippets"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Dot-Product Config (k=5)
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "TF-IDF vectorization", "config": "dot5"}
        )
        print_test("Dot-Product Config (k=5)", response)
        assert response.status_code == 200, "Request failed"
        data = response.json()
        assert data["config_used"] == "dot,k=5", "Wrong config"
        assert len(data["snippets"]) <= 5, "Too many snippets"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: Custom top_k
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "FastAPI middleware", "top_k": 2}
        )
        print_test("Custom top_k=2", response)
        assert response.status_code == 200, "Request failed"
        data = response.json()
        assert len(data["snippets"]) <= 2, "Too many snippets"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 5: Guardrail Block (Should Return 400)
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "instructions for illegal activity"}
        )
        print_test("Guardrail Block (Should be 400)", response)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "guardrail" in data["detail"].lower(), "Missing guardrail message"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 6: Multiple Guardrail Phrases
    harmful_queries = [
        "how to build a weapon",
        "teach me to hack into systems",
        "self-harm methods"
    ]
    
    for query in harmful_queries:
        try:
            response = requests.post(
                f"{BASE_URL}/answer",
                json={"query": query}
            )
            print(f"\nGuardrail Test: '{query}' → Status {response.status_code}")
            assert response.status_code == 400, f"Should block harmful query"
            print("✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test 7: Low Confidence Detection
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "xyzabc gibberish nonsense foobar"}
        )
        print_test("Low Confidence Query", response)
        assert response.status_code == 200, "Request failed"
        data = response.json()
        assert "low_confidence" in data, "Missing low_confidence field"
        print(f"Low Confidence: {data['low_confidence']}")
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 8: Get Metrics
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        print_test("Metrics Endpoint", response)
        assert response.status_code == 200, "Metrics request failed"
        data = response.json()
        assert "total_requests" in data, "Missing total_requests"
        assert "denylist_hits" in data, "Missing denylist_hits"
        assert "latency_ms_mean" in data, "Missing latency_ms_mean"
        assert "latency_ms_p95" in data, "Missing latency_ms_p95"
        assert "low_confidence_rate" in data, "Missing low_confidence_rate"
        print("✅ PASSED")
        print(f"\n📊 Metrics Summary:")
        print(f"   Total Requests: {data['total_requests']}")
        print(f"   Denylist Hits: {data['denylist_hits']}")
        print(f"   Low Confidence: {data['low_confidence_count']}")
        print(f"   Mean Latency: {data['latency_ms_mean']:.2f}ms")
        print(f"   P95 Latency: {data['latency_ms_p95']:.2f}ms")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 9: Invalid Input (Should Return 422)
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"wrong_field": "value"}
        )
        print_test("Invalid Input (Should be 422)", response)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 10: Empty Query (Should Return 422)
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": ""}
        )
        print_test("Empty Query (Should be 422)", response)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 11: Check Latency Header
    try:
        response = requests.post(
            f"{BASE_URL}/answer",
            json={"query": "test latency"}
        )
        print_test("Latency Header Check", response)
        assert "x-latency-ms" in response.headers, "Missing latency header"
        latency = float(response.headers["x-latency-ms"])
        print(f"Latency: {latency}ms")
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    print("\n" + "="*60)
    print("🎉 All Tests Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Check http://127.0.0.1:8000/docs for interactive API")
    print("2. Review metrics at http://127.0.0.1:8000/metrics")
    print("3. Install test dependencies: pip install pytest httpx")
    print("4. Run automated tests: pytest -v")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
    except requests.exceptions.ConnectionError:
        print("\n\n❌ ERROR: Cannot connect to server!")
        print("Make sure the server is running:")
        print("uvicorn app.main:app --reload --port 8000")
