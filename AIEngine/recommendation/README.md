# Recommendation Service

FastAPI microservice that exposes `/recommend` to return a dummy therapy journey recommendation.

Run:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Example:

```bash
curl -X POST http://localhost:8002/recommend \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "abc123", "mood": "sadness"}'
```

