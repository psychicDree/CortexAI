# CortexAI Monorepo

Modular AI platform with a FastAPI backend, AI microservices, a React analytics dashboard, Firebase Cloud Functions, and a Unity client. This README provides a high-level overview and quickstart instructions for each component.

## Repository Structure

```
Backend/api/                 FastAPI backend API
AIEngine/emotion_analysis/   FastAPI microservice: emotion analysis (port 8001)
AIEngine/recommendation/     FastAPI microservice: recommendations (port 8002)
Analytics/dashboard/         React + Vite analytics dashboard (port 5173)
functions/                   Firebase Cloud Functions (Node 20)
UnityClient/                 Unity client project
Docs/                        Architecture and API docs
Compliance/                  Security and privacy docs
firebase.json, *.rules       Firebase config and rules
LICENSE                      MIT License
```

## Prerequisites

- Python 3.11
- Node.js 20 (for dashboard and functions)
- npm (or your preferred Node package manager)
- Docker (optional; each service has a Dockerfile)
- Firebase CLI (for local emulators and functions deploy)
- Unity Editor (for `UnityClient/`)

## Quick Start

Run services in separate terminals as needed.

### 1) Backend API (FastAPI)

Location: `Backend/api`

Install and run:

```bash
cd Backend/api
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check: `GET http://localhost:8000/health`

Docker:

```bash
cd Backend/api
docker build -t cortexai-backend .
docker run --rm -p 8000:8000 cortexai-backend
```

### 2) AIEngine Services (FastAPI)

Emotion Analysis (port 8001):

```bash
cd AIEngine/emotion_analysis
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Example
curl -X POST http://localhost:8001/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"I feel great and grateful today"}'
```

Recommendation (port 8002):

```bash
cd AIEngine/recommendation
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Example
curl -X POST http://localhost:8002/recommend \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"abc123","mood":"sadness"}'
```

Docker builds are available in each service directory.

### 3) Analytics Dashboard (React + Vite)

Location: `Analytics/dashboard`

```bash
cd Analytics/dashboard
npm install
npm run dev
# App: http://localhost:5173
```

### 4) Firebase Cloud Functions

Location: `functions`

```bash
cd functions
npm install
npm run build
# Start local emulators (functions + firestore + storage)
npm run serve
```

Deploy (requires Firebase project configured and auth):

```bash
npm run build && npm run deploy
```

### 5) Unity Client

Location: `UnityClient`

Open the project in Unity Hub/Editor and press Play. Platform-specific build settings and Unity version depend on your environment.

## Configuration

- Backend and services in this repo run with sensible defaults and do not require root-level `.env` by default. If a service requires secrets, provide them via environment variables or a local `.env` in that service directory.
- Firebase uses `firebase.json`, `firestore.rules`, and `storage.rules`. Update rules as needed for your project.

## Useful Endpoints

- Backend API: `GET /health` → `{ "status": "ok" }`
- Emotion Analysis: `POST /analyze` (see service README)
- Recommendation: `POST /recommend` (see service README)

## Documentation and Compliance

- Docs: `Docs/` (e.g., `API_REFERENCE.md`, data flow diagrams)
- Compliance: `Compliance/PRIVACY_POLICY.md`, `Compliance/SECURITY_CHECKLIST.md`

## Contributing

Please open an issue or pull request with clear context. Ensure linting/tests pass where applicable.

## License

MIT — see [`LICENSE`](LICENSE).
