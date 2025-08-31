### Onboarding Prerequisites

This document lists the minimum setup required to run CortexAI components locally.

### Accounts and Access
- **GitHub**: Access to the repository (and CI logs if needed).
- **Container registry (optional)**: Access to GitHub Container Registry if pulling prebuilt images.

### Supported OS
- **Linux/macOS**: Native supported.
- **Windows**: Use WSL2 for best compatibility.

### Core Tooling
- **Git**: Latest stable.
- **Python**: 3.11.x with `pip`.
- **Node.js**: 20.x with `npm` (npm 10+ recommended).
- **Docker** (optional): Docker Engine 24+ if you prefer containers.
- **Docker Compose** (optional): v2+ if orchestrating multiple services.

Recommended helpers (optional):
- **pyenv** or **virtualenv** for Python environments
- **nvm** for Node version management
- **VS Code** or preferred IDE; REST client (curl/Postman/Insomnia)

### Component Requirements

#### Backend API (`Backend/api`)
- **Runtime**: Python 3.11
- **Dependencies**: `pip install -r requirements.txt`
- **Database**:
  - Default: SQLite (no extra setup)
  - Optional: PostgreSQL 14+ when providing `DATABASE_URL`
- **Environment variables**:
  - `DATABASE_URL` (optional): e.g. `postgresql+psycopg2://user:pass@localhost:5432/cortex`
  - `JWT_SECRET` (recommended for non-dev)
  - `JWT_ALGORITHM` (default `HS256`)
  - `ACCESS_TOKEN_EXPIRE_MINUTES` (default `60`)
- **Ports**: 8000 (FastAPI)

#### AIEngine Services (`AIEngine/*`)
- Emotion Analysis (`AIEngine/emotion_analysis`)
  - **Runtime**: Python 3.11
  - **Dependencies**: `pip install -r requirements.txt`
  - **Port**: 8001
- Recommendation (`AIEngine/recommendation`)
  - **Runtime**: Python 3.11
  - **Dependencies**: `pip install -r requirements.txt`
  - **Port**: 8002

#### Analytics Dashboard (`Analytics/dashboard`)
- **Runtime**: Node.js 20.x, npm 10+
- **Dependencies**: `npm ci`
- **Dev server**: Vite on port 5173
- **Env**: `VITE_API_BASE` (defaults to `http://localhost:8000`)

#### Unity Client (`UnityClient`)
- **Unity Hub** installed
- **Unity Editor**: Recent LTS recommended (e.g., 2022.3 LTS or newer)

### Networking and Ports
- Backend API: `8000`
- Emotion Analysis: `8001`
- Recommendation: `8002`
- Dashboard (Vite dev): `5173`

Ensure these ports are available locally and allowed through any firewall.

### Optional: Docker
- Backend API: `Backend/api/Dockerfile` (Python 3.11-slim base)
- AIEngine services: Dockerfiles available in each service directory

### Quick Verification
Run these to verify prerequisites (examples):

```bash
python3 --version   # Expect 3.11.x
pip --version       # Recent pip
node -v             # Expect v20.x
npm -v              # Expect 10+
docker --version    # If using Docker
```

If using PostgreSQL, confirm connectivity and credentials for `DATABASE_URL`.

### Notes
- CORS is permissive in dev across services.
- CI targets Python 3.11 and Node 20; aligning locally avoids version drift.

