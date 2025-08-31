# Emotion Analysis Service

FastAPI microservice that exposes `/analyze` to return a dummy emotion and confidence.

Run:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Example:

```bash
curl -X POST http://localhost:8001/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text": "I feel great and grateful today"}'
```

