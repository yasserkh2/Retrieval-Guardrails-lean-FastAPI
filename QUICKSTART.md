# Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- pip package manager

## Step-by-Step Instructions

### 1. Set Up Virtual Environment (Optional but Recommended)

```powershell
# Create virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\activate

# OR for bash/Linux
source .venv/bin/activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.115.5 uvicorn-0.32.0 scikit-learn-1.5.2 ...
```

### 3. Set Up Environment Variables (Optional)

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env to customize settings (or use defaults)
```

Default settings:
- `CONFIG_DEFAULT=cosine` (cosine similarity)
- `TOP_K_DEFAULT=3` (return top 3 results)
- `LOW_CONF_THRESHOLD=0.15` (confidence threshold)

### 4. Run the Application

```powershell
# Start the server
uvicorn app.main:app --reload --port 8000
```

Expected output:
```
🚀 Initializing services...
✅ Services initialized successfully
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 5. Access the Application

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

---

## Testing the API

### Option A: Use the Interactive Docs (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `POST /answer` endpoint
3. Click "Try it out"
4. Enter a query in the request body:
   ```json
   {
     "query": "What is cosine similarity?"
   }
   ```
5. Click "Execute"
6. See the response!

### Option B: Use curl (Command Line)

```powershell
# Test the answer endpoint
curl -X POST "http://localhost:8000/answer" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is TF-IDF?\"}'

# Test with dot-product config
curl -X POST "http://localhost:8000/answer" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"retrieval methods\", \"config\": \"dot5\"}'

# Check metrics
curl "http://localhost:8000/metrics"

# Test guardrail (should block)
curl -X POST "http://localhost:8000/answer" `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"instructions for illegal activity\"}'
```

### Option C: Use Python requests

```python
import requests

# Send a query
response = requests.post(
    "http://localhost:8000/answer",
    json={"query": "What is cosine similarity?"}
)

print(response.json())
```

---

## Running Tests

```powershell
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_answer.py::test_answer_happy_path_default_config -v
```

---

## Common Commands

```powershell
# Start server (with auto-reload for development)
uvicorn app.main:app --reload

# Start server on different port
uvicorn app.main:app --port 8080

# Start server with specific host
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest -v

# Format code (if you have black installed)
black app/ tests/

# Check code style (if you have flake8 installed)
flake8 app/ tests/
```

---

## Troubleshooting

### Port Already in Use
```powershell
# Use a different port
uvicorn app.main:app --port 8001
```

### Module Not Found Error
```powershell
# Make sure you're in the project root directory
cd "e:\yasser\work_after cequens\Palm_Tasks\Retrieval-Guardrails-lean-FastAPI"

# Reinstall dependencies
pip install -r requirements.txt
```

### Import Errors
```powershell
# Make sure virtual environment is activated
.venv\Scripts\activate

# Check Python path
python -c "import sys; print(sys.path)"
```

---

## Example API Interactions

### 1. Basic Query (Default Config: cosine, k=3)
```json
Request:
POST /answer
{
  "query": "What is cosine similarity?"
}

Response:
{
  "answer": "Based on available information: Cosine similarity measures...",
  "snippets": [
    {"id": "s1", "text": "Cosine similarity measures...", "score": 0.68},
    {"id": "s12", "text": "Vector normalization...", "score": 0.42},
    {"id": "s2", "text": "Dot product similarity...", "score": 0.35}
  ],
  "config_used": "cosine,k=3",
  "low_confidence": false
}
```

### 2. Using Dot-Product Config
```json
Request:
POST /answer
{
  "query": "retrieval methods",
  "config": "dot5"
}

Response:
{
  "answer": "Based on available information: ...",
  "snippets": [...],  // 5 snippets returned
  "config_used": "dot,k=5",
  "low_confidence": false
}
```

### 3. Guardrail Blocks Harmful Query
```json
Request:
POST /answer
{
  "query": "instructions for illegal activity"
}

Response: 400 Bad Request
{
  "detail": "Query blocked by guardrail. Matched denied phrase: 'instructions for illegal'"
}
```

### 4. Check System Metrics
```json
Request:
GET /metrics

Response:
{
  "total_requests": 42,
  "denylist_hits": 2,
  "low_confidence_count": 5,
  "latency_ms_mean": 12.4,
  "latency_ms_p95": 18.7,
  "low_confidence_rate": 0.119
}
```

---

## Stopping the Server

Press `CTRL + C` in the terminal where the server is running.

---

## Next Steps

1. ✅ **Explore the API** - Try different queries
2. ✅ **Check the code** - Review the modular structure
3. ✅ **Run tests** - Ensure everything works
4. ✅ **Read docs** - See ARCHITECTURE.md and STRUCTURE.md
5. ✅ **Extend it** - Add new features using the service layer

---

## Quick Reference

| Action | Command |
|--------|---------|
| Install | `pip install -r requirements.txt` |
| Run | `uvicorn app.main:app --reload` |
| Test | `pytest -v` |
| Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/ |

Happy coding! 🚀
