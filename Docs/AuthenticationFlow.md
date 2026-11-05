# Authentication Flow

Three identity mechanisms exist in the repo. They are not linked to each other.

| Mechanism | Used by | Credential | Code |
| --- | --- | --- | --- |
| Backend JWT | Dashboard | Email and password | `Backend/api/app/auth.py`, `routers/auth.py` |
| Onboarding profile | Unity client | Device-generated ID, no secret | `routers/onboarding.py`, `UnityClient/.../AuthManager.cs` |
| Firebase Auth | Sample scripts, `onUserCreate` | Firebase UID | `functions/src/index.ts`, `UnityClient/.../Network/AuthSample.cs` |

## Backend JWT

```mermaid
sequenceDiagram
  participant C as Client
  participant API as Backend API
  participant DB as Database

  C->>API: POST /auth/register {email, password}
  API->>DB: insert user (bcrypt hash)
  API-->>C: 200 {id, email}

  C->>API: POST /auth/login (form: username=email, password)
  API->>DB: find user by email, verify hash
  API-->>C: 200 {access_token, token_type: "bearer"}

  C->>API: GET /sessions/ (Authorization: Bearer token)
  API->>API: decode JWT, read sub
  API->>DB: load user by id
  API-->>C: 200 [sessions for that user]
```

- Passwords: at least 6 characters, hashed with bcrypt through passlib.
- Login takes OAuth2 password form fields (`application/x-www-form-urlencoded`). The email goes in `username`.
- Token: HS256 by default, signed with `JWT_SECRET`. Claims are `sub` (the user ID as a string) and `exp` (60 minutes).
- No refresh tokens, logout, or revocation. A token is valid until it expires.
- No roles. Every signed-in user has the same access.

### Endpoint access

| Endpoint | Auth |
| --- | --- |
| `GET /health` | None |
| `POST /auth/register`, `POST /auth/login` | None |
| `GET /users/me`, `GET /users/` | Bearer token |
| `POST /sessions/`, `GET /sessions/` | Bearer token; scoped to the token's user |
| `POST /checkins/`, `GET /checkins/` | Bearer token; scoped to the token's user |
| `POST /ask/` | Bearer token |
| `POST /onboarding/`, `GET /onboarding/{client_user_id}` | None |
| AI services (`/analyze`, `/recommend`, `/reply`, `/ask`, `/health`) | None |

### Errors

| Status | When |
| --- | --- |
| 400 `Email already registered` | Register with an existing email |
| 401 `Incorrect email or password` | Login fails |
| 401 `Could not validate credentials` | Missing, expired, or invalid token, or the user no longer exists. Includes `WWW-Authenticate: Bearer`. |
| 404 `Onboarding profile not found` | Unknown `client_user_id` |
| 422 | Request body fails validation |

## Unity onboarding

```mermaid
sequenceDiagram
  participant P as Player
  participant U as Unity client
  participant PP as PlayerPrefs
  participant API as Backend API

  U->>PP: load cortexai.user_profile
  alt profile exists
    U-->>P: show home
  else no profile
    U-->>P: show onboarding form
    P->>U: name, age
    U->>PP: save profile (new random ID)
    U--)API: POST /onboarding/ (no wait)
    U-->>P: show home
  end
```

"Sign in as existing user" only checks for a profile already saved on the same device. There is no password and no server lookup, so a profile cannot move between devices.

## Firebase Auth

`onUserCreate` runs when a Firebase Auth user is created and writes `users/{uid}` with `uid`, `email`, and `createdAt`. Firestore and Storage rules allow each user to access only paths under their own UID.

The Unity `AuthSample` script shows anonymous sign-in and sign-out, but no scene uses it, and the backend does not accept Firebase ID tokens.

## Not built yet

The planned design in [DataFlowDiagram.md](DataFlowDiagram.md) uses Azure AD B2C (OIDC) for identity. None of that exists in code. Also missing: roles, refresh tokens, and a single user ID shared by the backend, Unity, and Firebase.
