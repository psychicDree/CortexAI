### CortexAI™ API Reference (Draft)

Note: All responses are JSON. Unless noted, endpoints may require `Authorization: Bearer <JWT>`.

## Emotion Analysis Service
- **POST** `/analyze`
  - Purpose: Analyze text for dominant emotion
  - Request: `{ "text": "I feel great" }`
  - Response: `{ "emotion": "joy", "confidence": 0.8 }`
  - Example:
    - `curl -X POST $EMO/analyze -H 'Content-Type: application/json' -d '{"text":"I feel great"}'`
- **GET** `/health` → `{ "status": "ok" }`

## Recommendation Service
- **POST** `/recommend`
  - Purpose: Recommend therapy module/level based on mood
  - Request: `{ "user_id": "abc123", "mood": "sadness" }`
  - Response: `{ "module": "mood_journaling", "level": "intro" }`
  - Example:
    - `curl -X POST $REC/recommend -H 'Content-Type: application/json' -d '{"user_id":"abc123","mood":"sadness"}'`
- **GET** `/health` → `{ "status": "ok" }`

## Backend API
- Base URL: `$API`

### Auth
- **POST** `/auth/register`
  - Purpose: Create a user
  - Request: `{ "email": "user@example.com", "password": "secret" }`
  - Response: `{ "id": 1, "email": "user@example.com" }`

- **POST** `/auth/login`
  - Purpose: Obtain JWT
  - Request (form): `username=<email>&password=<password>`
  - Response: `{ "access_token": "...", "token_type": "bearer" }`
  - Example:
    - `curl -X POST $API/auth/login -d 'username=user@example.com&password=secret&grant_type=password' -H 'Content-Type: application/x-www-form-urlencoded'`

### Users
- **GET** `/users/me`
  - Purpose: Get current user profile
  - Response: `{ "id": 1, "email": "user@example.com" }`

- **GET** `/users/`
  - Purpose: List users (admin placeholder)
  - Response: `[ { "id": 1, "email": "..." }, ... ]`

### Sessions
- **POST** `/sessions/`
  - Purpose: Create a session record
  - Request: `{ "mood": "sadness", "duration_seconds": 600 }`
  - Response: `{ "id": 1, "user_id": 1, "mood": "sadness", "started_at": "...", "duration_seconds": 600 }`

- **GET** `/sessions/`
  - Purpose: List current user's sessions
  - Response: `[ { ... }, ... ]`

### Onboarding
- **POST** `/onboarding/`
  - Purpose: Create or update a lightweight onboarding profile by client-generated ID
  - Request: `{ "client_user_id": "local-guid", "display_name": "Alice", "age": 22 }`
  - Response: `{ "id": 1, "client_user_id": "local-guid", "display_name": "Alice", "age": 22, "created_at": "..." }`

- **GET** `/onboarding/{client_user_id}`
  - Purpose: Fetch onboarding profile by client ID
  - Response: `{ "id": 1, "client_user_id": "local-guid", "display_name": "Alice", "age": 22, "created_at": "..." }`

Notes:
- Use HTTPS. Set `Authorization` header with JWT for protected endpoints.
- Error schema (example): `{ "detail": "message" }`

