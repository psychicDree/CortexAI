# Emotion Analysis Service

FastAPI service exposing `POST /analyze`. It returns the dominant emotion (`joy`, `sadness`, `anger`, `fear`, `neutral`), per-emotion scores, and a crisis-language flag.

- **Model:** [`SamLowe/roberta-base-go_emotions`](https://huggingface.co/SamLowe/roberta-base-go_emotions) (MIT), pinned to a fixed revision. It runs locally, so text never leaves the service. Its 28 GoEmotions labels are grouped into the five emotions (`classifier.py`).
- **Fallback:** if PyTorch or the model is unavailable, a keyword classifier with simple negation handling is used. `GET /health` reports which one is active.
- **Crisis flag:** a keyword screen (`safety.py`). It is a safety net, not a clinical assessment.

Run with the model (first start downloads about 500 MB):

```bash
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-ml.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

| Variable | Default |
| --- | --- |
| `EMOTION_BACKEND` | `transformer` (`lexicon` forces the fallback) |
| `EMOTION_MODEL` | `SamLowe/roberta-base-go_emotions` |
| `EMOTION_MODEL_REVISION` | pinned commit in `classifier.py` |

Example:

```bash
curl -X POST http://localhost:8001/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text": "I feel great and grateful today"}'
```

Tests:

```bash
pip install -r requirements-dev.txt
pytest
RUN_MODEL_TESTS=1 pytest -k real_model   # needs requirements-ml.txt
```

To serve a model fine-tuned with `AIEngine/training`, set `EMOTION_MODEL` to its directory. See [the training README](../training/README.md) for results; the default model scored best on the GoEmotions test split.
