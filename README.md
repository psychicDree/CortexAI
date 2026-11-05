# CortexAI

Early-stage prototype of a mental wellbeing app: a Unity client, a FastAPI backend, two AI microservices, a React dashboard, and Firebase scaffolding.

The AI services are placeholders (keyword matching and a fixed lookup table). See [Docs/SystemArchitecture.md](Docs/SystemArchitecture.md) for what is built and what is still planned.

## Repository layout

| Path | What it is | Port |
| --- | --- | --- |
| `Backend/api/` | FastAPI backend: auth, users, sessions, onboarding | 8000 |
| `AIEngine/emotion_analysis/` | FastAPI service: text → emotion | 8001 |
| `AIEngine/recommendation/` | FastAPI service: mood → exercise module | 8002 |
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
| `JWT_SECRET` | `dev_secret_change_me` | Signs access tokens. Set this outside local dev. |
| `JWT_ALGORITHM` | `HS256` | Token signing algorithm |
| `PORT` | `8000` | Only used by `python -m app.main` |

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
  -d '{"client_user_id":"abc12345","display_name":"Test","age":20}'
```

Endpoints are listed in [Docs/API_REFERENCE.md](Docs/API_REFERENCE.md). The auth flow is in [Docs/AuthenticationFlow.md](Docs/AuthenticationFlow.md).

## AI services

```bash
cd AIEngine/emotion_analysis
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

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

Both services also expose `GET /health`. Nothing in the repo calls them yet.

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

The client posts onboarding profiles to `http://localhost:8000`. Override that with the PlayerPrefs key `cortexai.api_base`.

## Docker

Each Python service has a Dockerfile:

```bash
docker build -t cortexai-backend Backend/api
docker run --rm -p 8000:8000 cortexai-backend
```

## CI/CD

- `ci.yml`: on every push and PR, imports and health-checks each Python service, and builds the dashboard.
- `ghcr.yml`: on push to `main`, builds and pushes the three service images to GHCR.
- `pages.yml`: on push to `main`, deploys the dashboard to GitHub Pages.

## License

MIT. See [LICENSE](LICENSE).
