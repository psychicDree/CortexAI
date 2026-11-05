# Recommendation Service

FastAPI service exposing `POST /recommend`. It picks an exercise module and level from the catalog in `catalog.py`.

Rules (`engine.py`):
- `crisis_flag: true` always returns `crisis_support`.
- A confidence below 0.4 is treated as `neutral`.
- Modules matching the mood rotate by how often they appear in `history`, and the last one isn't repeated.
- The level is `intro`, then `intermediate` after 3 prior recommendations of that module, then `advanced` after 8.

Run:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

Example:

```bash
curl -X POST http://localhost:8002/recommend \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "abc123", "mood": "sadness", "confidence": 0.9, "history": ["mood_journaling"]}'
```

Tests:

```bash
pip install -r requirements-dev.txt
pytest
```
