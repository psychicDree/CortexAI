# CortexAI

Early-stage prototype of a mental wellbeing app: a Unity client, a FastAPI backend, two AI microservices, a React dashboard, and Firebase scaffolding.

Emotion analysis runs a local open-source model, so user text stays on your server. Recommendations come from a small rule-based exercise catalog. See [Docs/SystemArchitecture.md](Docs/SystemArchitecture.md) for what is built and what is still planned.

## Repository layout

| Path | What it is | Port |
| --- | --- | --- |
| `Backend/api/` | FastAPI backend: auth, users, sessions, onboarding, check-ins | 8000 |
| `AIEngine/emotion_analysis/` | FastAPI service: text → emotion and crisis flag | 8001 |
| `AIEngine/recommendation/` | FastAPI service: mood → exercise module | 8002 |
| `AIEngine/companion/` | FastAPI service: check-in replies and question answering via local Ollama | 8003 |
| `AIEngine/training/` | Scripts to export a public dataset, fine-tune, and evaluate the emotion model | — |
| `Analytics/dashboard/` | React + Vite dashboard that calls the backend | 5173 |
| `functions/` | Firebase Cloud Functions (TypeScript, Node 20) | — |
| `UnityClient/` | Unity C# scripts (no Unity project settings or scenes yet) | — |
| `Docs/` | Architecture, auth, schema, API, and data flow docs | — |
| `Compliance/` | Privacy policy and security checklist drafts | — |

## Prerequisites

- Python 3.11 (the version CI uses)
- Node.js 20 and npm
- Firebase CLI, only for `functions/`
- Unity Editor and the Firebase Unity SDK, only for `UnityClient/`
- Docker, optional

## Backend API

```bash
cd Backend/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Tables are created on startup. Interactive API docs are at `http://localhost:8000/docs`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./cortexai_dev.db` | SQLAlchemy URL. For Postgres, also install `psycopg2-binary`. |
| `APP_ENV` | `development` | Any other value (the Docker image uses `production`) requires a strong `JWT_SECRET` |
| `JWT_SECRET` | `dev_secret_change_me` | Signs access tokens. Outside development the backend refuses to start unless this is set to 32+ random characters. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token lifetime |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated browser origins allowed to call the API |
| `ADMIN_EMAILS` | empty | Comma-separated emails allowed to call `GET /users/` |
| `JWT_ALGORITHM` | `HS256` | Token signing algorithm |
| `PORT` | `8000` | Only used by `python -m app.main` |
| `EMOTION_SERVICE_URL` | `http://localhost:8001` | Emotion service used by `/checkins/` |
| `RECOMMENDATION_SERVICE_URL` | `http://localhost:8002` | Recommendation service used by `/checkins/` |
| `AIENGINE_TIMEOUT_SECONDS` | `10` | Timeout for emotion and recommendation calls |
| `COMPANION_SERVICE_URL` | `http://localhost:8003` | Companion service used by `/checkins/` and `/ask/` |
| `COMPANION_TIMEOUT_SECONDS` | `60` | Timeout for companion calls (local generation is slower) |

Run the tests:

```bash
cd Backend/api
pytest
```

Quick check:

```bash
curl -s http://localhost:8000/health
```

```bash
curl -s -X POST http://localhost:8000/onboarding/ \
  -H 'Content-Type: application/json' \
  -H "X-Device-Secret: $(openssl rand -hex 32)" \
  -d '{"client_user_id":"abc12345","display_name":"Test","age":20}'
```

Endpoints are listed in [Docs/API_REFERENCE.md](Docs/API_REFERENCE.md). The auth flow is in [Docs/AuthenticationFlow.md](Docs/AuthenticationFlow.md).

## AI services

The backend's `POST /checkins/` sends the user's text to emotion analysis, passes the mood to recommendation, and then asks the companion for a short reply. `POST /ask/` answers questions from the reviewed question bank. Emotion and recommendation are required; if the companion is down, check-ins still work, just without a reply.

Emotion analysis uses [`SamLowe/roberta-base-go_emotions`](https://huggingface.co/SamLowe/roberta-base-go_emotions) (MIT). The first start downloads about 500 MB:

```bash
cd AIEngine/emotion_analysis
pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-ml.txt
uvicorn main:app --port 8001
```

Without the model dependencies, install `requirements.txt` instead. The service then falls back to a keyword classifier; `GET /health` reports which one is running. Set `EMOTION_BACKEND=lexicon` to force the fallback.

```bash
cd AIEngine/recommendation
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

```bash
curl -s -X POST http://localhost:8001/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"I feel anxious and worried"}'
```

```bash
curl -s -X POST http://localhost:8002/recommend \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"abc12345","mood":"fear"}'
```

Run each service's tests with `pip install -r requirements-dev.txt` and then `pytest`. To also test the real model, set `RUN_MODEL_TESTS=1` in the emotion service.

The crisis flag is a keyword screen, not a clinical assessment.

The companion needs [Ollama](https://ollama.com) running locally:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
cd AIEngine/companion
pip install -r requirements.txt
uvicorn main:app --port 8003
```

All question-bank entries ship as drafts, and only reviewed entries are used to answer questions. See [AIEngine/companion/README.md](AIEngine/companion/README.md).

### Training

[AIEngine/training](AIEngine/training/README.md) exports GoEmotions as a 5-emotion dataset, fine-tunes the emotion classifier, and evaluates any model exactly as the service runs it. Exported data and weights are git-ignored.

## Dashboard

```bash
cd Analytics/dashboard
npm install
npm run dev
```

Opens at `http://localhost:5173`. Set `VITE_API_BASE` to point it at a backend other than `http://localhost:8000`.

## Firebase functions

```bash
cd functions
npm install
npm run build
npm run serve
```

`serve` starts the Functions, Firestore, and Storage emulators. Set your project ID in `.firebaserc` before deploying with `npm run deploy`.

## Unity client

`UnityClient/` holds scripts only. To try it, create a Unity project, copy `UnityClient/Assets` into it, import the Firebase Unity SDK (the `Network/*Sample.cs` scripts need it), and build the scene described in [UnityClient/README.md](UnityClient/README.md).

The client posts onboarding profiles to `http://localhost:8000` with its device secret. Override the URL with the PlayerPrefs key `cortexai.api_base`.

## Docker

Each Python service has a Dockerfile. The emotion image bakes in CPU-only PyTorch and the model, so it runs without network access:

```bash
docker build -t cortexai-backend Backend/api
docker run --rm -p 8000:8000 -e JWT_SECRET="$(openssl rand -hex 32)" cortexai-backend
```

## CI/CD

- `ci.yml`: on every push and PR, tests, imports, and health-checks each Python service, and builds the dashboard. The emotion job uses the keyword classifier, not the model.
- `ghcr.yml`: on push to `main`, builds and pushes the four service images to GHCR.
- `pages.yml`: on push to `main`, deploys the dashboard to GitHub Pages.

## License

MIT. See [LICENSE](LICENSE).
