# CortexAI

## Product Description

CortexAI is a modular AI platform designed to streamline the development, deployment, and scaling of intelligent applications. With a focus on flexibility and collaboration, CortexAI supports a variety of AI workflows, including data preprocessing, model training, evaluation, and deployment. By organizing core components into dedicated directories, CortexAI allows teams to work efficiently and securely on different aspects of the platform.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Monorepo layout (key folders)
- `Backend/api`: FastAPI backend
- `AIEngine/*`: Microservices
- `Analytics/dashboard`: Vite/React dashboard
- `UnityClient`: Unity project

### Backend API (dev)
```bash
cd Backend/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health check:
```bash
curl -s http://localhost:8000/health
```

### Unity client
- Open `UnityClient` in Unity.
- Default backend base: `http://localhost:8000`.
- Override via PlayerPrefs key `cortexai.api_base`.

## New: User Onboarding

Unity creates a local profile and syncs to backend.

Backend additions:
- Model `OnboardingProfile`: `client_user_id`, `display_name`, `age`, `created_at`.
- Endpoints:
  - `POST /onboarding/`
  - `GET /onboarding/{client_user_id}`

Unity flow:
- `AuthManager.CreateAndSignIn(name, age)` saves local profile and posts to `/onboarding/` (fire-and-forget).

Quick test:
```bash
curl -s -X POST http://localhost:8000/onboarding/ \
  -H 'Content-Type: application/json' \
  -d '{"client_user_id":"abc123","display_name":"Test","age":20}'
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
