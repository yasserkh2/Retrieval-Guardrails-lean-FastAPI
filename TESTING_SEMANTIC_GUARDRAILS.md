## Quick Test Commands

### 1. Restart the Server
Press `CTRL+C` in the uvicorn terminal, then run:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Run Semantic Guardrail Tests
In another terminal:
```bash
python test_semantic_guardrails.py
```

### 3. Expected Improvements
The new approach:
- ✅ Creates a separate TF-IDF vectorizer trained on denylist phrases
- ✅ Uses bigrams (1-2 word phrases) for better semantic capture
- ✅ Should now catch paraphrases like "guide to unlawful actions"
- ✅ Threshold set to 0.30 (balanced)

### 4. Manual Testing Examples

**Test Blocked Queries:**
```bash
# Should be BLOCKED
curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" -d "{\"query\":\"instructions for illegal activity\"}"

curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" -d "{\"query\":\"guide to unlawful actions\"}"

curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" -d "{\"query\":\"tutorial on creating weapons\"}"
```

**Test Safe Queries:**
```bash
# Should be ALLOWED
curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" -d "{\"query\":\"What is cosine similarity?\"}"

curl -X POST http://127.0.0.1:8000/answer -H "Content-Type: application/json" -d "{\"query\":\"How to build a web application?\"}"
```

### 5. Enable Debug Mode (Optional)
To see similarity scores, edit `app/guardrails/denylist.py`:
```python
DEBUG_SIMILARITY_SCORES = True  # Change from False to True
```

Then restart server and watch the logs for similarity scores.

### 6. Tune Threshold (If Needed)
Edit `app/guardrails/denylist.py`:
```python
TFIDF_THRESHOLD = 0.30  # Adjust: 0.25 (strict) to 0.40 (lenient)
```

- Lower = More strict (may have false positives)
- Higher = More lenient (may miss some paraphrases)
