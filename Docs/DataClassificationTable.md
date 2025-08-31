## Data Classification Table

Legend for classification
- Public: non-sensitive, may be shared externally
- Internal: non-public, low sensitivity
- Confidential: sensitive, limited to need-to-know
- Restricted: highly sensitive (PII/PHI/Secrets)

| Data element | Examples | Source | Purpose | Lawful basis / Reg. | Classification | Storage location | Retention | Access | Controls |
|---|---|---|---|---|---|---|---|---|---|
| Identity & Auth | Email (if used), federated subject, auth logs | User, IdP | Authentication, account management | GDPR: Contract/Consent; HIPAA: non-PHI | Restricted (PII) | Azure AD B2C; minimal in Azure SQL | Until account deletion + legal holds | Support (limited), Security, System | TLS, hashed IDs, MFA, RBAC, data minimization |
| Pseudonymous Identifiers | user_id, session_id, device_id | Client | Link events without direct PII | GDPR: Legitimate interests (de-identified) | Confidential | Cosmos DB | 24 months (raw), aggregates longer | Analytics, System | Pseudonymization, key rotation, TTL |
| Consent & Preferences | consent_given, timestamps, purposes | User | Compliance record, feature flags | GDPR: Consent; HIPAA: Admin record | Restricted (PII/Regulated) | Azure SQL | 7 years or policy | Compliance, Limited Admin | Encryption at rest, audit trail, immutable logs |
| Gameplay Telemetry | game_start, level_result, rt_ms | Client | Product analytics, adaptation | GDPR: Legitimate interests; minimal | Internal/Confidential | Cosmos DB | 12–24 months | Analytics (aggregate), System | Redaction on client, schema validation, IP allowlist |
| Voice Audio (User) | mic audio frames | Client | ASR/TTS for companion | GDPR: Consent; HIPAA: potential PHI | Restricted (PHI possible) | Transient; optional Blob (if enabled) | Default 0–30 days (configurable) | System; no general access | Provider logging disabled, regional routing, KMS keys |
| Transcripts (ASR) | recognized text, timestamps | Provider/Backend | Dialogue processing, accessibility | GDPR: Consent | Restricted (PHI possible) | Cosmos DB (scoped) or transient only | Default 0–90 days or disabled | System; minimal analysts (if approved) | Content redaction, policy filters, DLP |
| LLM Prompts/Responses | prompt, response, safety flags | Backend | Guidance, reflection, explanations | GDPR: Consent/Legit. interests | Confidential/Restricted | Cosmos DB (minimal), or disabled | 0–90 days (summary only) | System | Training opt-out, no logging, prompt scrubbing |
| Surveys & Self-Reports | PANAS/state, mood, symptoms | User | Outcome measures, personalization | GDPR: Explicit consent; HIPAA PHI | Restricted (PHI) | Azure SQL | 5 years (clinical validation window) | Clinical advisors (limited), Compliance | Access segregation, column-level encryption |
| Support & Communications | Helpdesk tickets, emails | User | Support, safety escalation | GDPR: Legitimate interests/Consent | Confidential/Restricted | Helpdesk SaaS (HIPAA-ready) | 2 years | Support, Compliance | DLP, role-based views, redaction tools |
| Keys & Secrets | API keys, client secrets, certs | System | Service auth | N/A | Restricted (Secrets) | Key Vault | Rotation ≤90 days | DevOps (limited) | HSM-backed, access policies, JIT elevation |
| Access Logs & Audit | auth logs, admin actions | System | Security monitoring, forensics | Legal obligation | Confidential | Log Analytics/SIEM | 180–365 days | Security | Tamper-evident, alerting, IP allowlists |
| Analytics Aggregates | cohorts, funnels, retention | System | Decision-making, reporting | Legitimate interests | Internal | BI workspace | Indefinite (de-identified) | Product, Exec | k-anonymity thresholds, suppression of small n |

Additional notes
- Data residency: provision regional stacks (e.g., EU) and pin storage to region; avoid cross-region transfers.
- DSR automation: implement discover/export/delete across `Azure SQL`, `Cosmos DB`, `Blob`; maintain mapping from identity to pseudonymous IDs.
- Provider controls: disable training and long-term logging on AI providers; use private/enterprise endpoints and signed DPA/BAA.
- Right-to-Erasure: cascade deletes for transcripts/audio and associated telemetry; ensure backups respect delete windows where feasible.
- Minimization: store only what is strictly required; prefer aggregates and summaries over raw content.

