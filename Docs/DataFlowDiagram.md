## Data Flow Diagram (DFD)

Scope: End-user mobile/desktop client (Unity), secure backend (Azure), external AI providers (LLM, TTS/ASR), analytics, and admin access. Trust boundaries are shown as subgraphs. Data labels indicate classification hints.

```mermaid
flowchart LR
  %% Trust Boundary: Client Device
  subgraph TB1[Client Device (Trust Boundary)]
    U[Unity Client App]
    Mic[(Microphone Input)]
    Spk((Speaker Output))
    Cache[(Encrypted Local Cache / Offline Queue)]
  end

  %% Trust Boundary: Identity
  subgraph TB2[Identity & Access]
    B2C[Azure AD B2C (OIDC)]
  end

  %% Trust Boundary: Secure Backend (VNet + Private Endpoints)
  subgraph TB3[Secure Backend (VNet)]
    APIM[API Management (WAF/Rate Limit)]
    API[App Service API]
    KV[Key Vault]
    COS[(Cosmos DB - Telemetry, Pseudonymous IDs)]
    SQL[(Azure SQL - Consent/PII/Minimal PHI)]
    BLOB[(Blob Storage - Audio Artifacts)]
    BUS[(Queue/Service Bus - Ingest/Retry)]
    LOG[Log Analytics / SIEM]
  end

  %% Trust Boundary: External AI Providers
  subgraph TB4[External AI Providers]
    AOAI[Azure OpenAI - LLM]
    SPEECH[Speech (ASR/TTS) - Azure Speech / ElevenLabs]
  end

  %% Trust Boundary: Analytics / Admin
  subgraph TB5[Analytics & Admin]
    BI[Analytics/Dashboard]
    ADMIN[Admin/Clinical Portal]
  end

  %% Client Flows
  Mic -->|audio PCM/Opus| U
  U -->|1. Login (PII minimal)| B2C
  B2C -->|2. OIDC/JWT tokens| U

  U -->|3. Telemetry events (pseudonymous)| APIM
  APIM --> API
  API -->|write| COS
  API -->|write| BUS

  U -->|4. Consent/self-reports (PII/PHI)| APIM
  APIM --> API
  API -->|write| SQL

  U -->|5. Voice stream (redacted)| APIM
  APIM --> API
  API -->|proxied audio/text| SPEECH
  SPEECH -->|tts/partial asr| API
  API -->|audio chunks| U

  U -->|6. Companion prompt (no PII)| APIM
  APIM --> API
  API -->|context-limited prompt| AOAI
  AOAI -->|completion| API
  API -->|response + safety flags| U

  %% Storage & Ops
  API -->|7. Audio artifacts (if retained)| BLOB
  API -->|8. Config/feature flags| COS
  API -->|9. Secrets/keys (read)| KV
  API -->|10. Audit/metrics| LOG

  %% Admin & Analytics
  ADMIN -->|OIDC| APIM
  APIM --> API
  API -->|read (least privilege)| SQL
  API -->|read (aggregates)| COS
  COS -->|ETL/Export (de-identified)| BI
  LOG -->|security alerts| ADMIN

  %% Local cache
  U <--> Cache

  %% Notes (styles optional)
  classDef pii fill:#ffe0e0,stroke:#c00,stroke-width:1px
  classDef phi fill:#ffe8cc,stroke:#c60,stroke-width:1px
  classDef pseudo fill:#e0f0ff,stroke:#06c,stroke-width:1px
  class SQL,BLOB pii
  class COS pseudo
```

Key flows
- 1–2 Auth: Minimal PII to identity provider; tokens scoped and rotated.
- 3 Telemetry: Pseudonymous event envelope, client-side redaction, buffered offline.
- 4 Consent/Surveys: Treated as regulated data; stored in `Azure SQL` with tight RBAC.
- 5 Voice: Streaming via backend proxy; provider logging/training disabled; transient by default.
- 6 LLM: Prompt is context-minimized; safety filters; no provider training.
- 7–10 Storage/Ops: Audio optional/short-lived; secrets in `Key Vault`; audit to SIEM.

Trust boundaries
- Client Device: local encryption-at-rest; data minimization; offline queue.
- Secure Backend (VNet): private endpoints, WAF, mTLS (service-to-service), least privilege.
- External AI Providers: contractual safeguards (BAA/DPA), data logging/training opt-out, regional endpoints.
- Analytics/Admin: de-identified aggregates only; role-based access; just-in-time elevation.

Assumptions
- All traffic uses TLS 1.2+; tokens are short-lived with refresh; 
- Right-to-Erasure supports cascaded deletes across `SQL`, `COS`, `BLOB`.
- Regional data residency honored per user region (e.g., EU tenants).

