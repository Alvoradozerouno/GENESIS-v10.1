# GENESIS v10.1 — Architecture Overview

## System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTS                                  │
│   Browser /ui    ·    API consumers    ·    Prometheus scraper  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (nginx TLS 1.2/1.3)
┌────────────────────────────▼────────────────────────────────────┐
│                    nginx (nginx/genesis.conf)                    │
│        HSTS · CSP · X-Frame-Options · proxy_pass :8080          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│               FastAPI (genesis_api.py) — port 8080              │
│                                                                 │
│  Auth layer        Rate limiter       Input validation          │
│  (SHA-256 keys)    (sliding window)   (Pydantic Field bounds)   │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Risk ML      │  │ Compliance   │  │  QES / eIDAS 2.0     │  │
│  │ Engine       │  │ Engine       │  │  (HMAC-SHA256)       │  │
│  │ R²=0.8955    │  │ 9 Frameworks │  │  PAdES-B-LT          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Local AI     │  │ Audit Trail  │  │  Key Management      │  │
│  │ llama.cpp    │  │ SQLite       │  │  Admin CRUD          │  │
│  │ Qwen2.5-0.5B │  │ append-only  │  │  Multi-tenant        │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  StaticFiles /ui  ·  /metrics (Prometheus)  ·  /docs (Swagger) │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    llama-server (port 8090)                      │
│        Qwen2.5-0.5B-Instruct Q4_K_M — Vulkan / GPU             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### API Gateway (`genesis_api.py`)
Single-file FastAPI application (1,136 lines). All business logic co-located for deployment simplicity.

| Concern | Implementation |
|---|---|
| Authentication | SHA-256 hashed keys in SQLite; `GENESIS_API_KEY` (tenant) + `GENESIS_ADMIN_KEY` (admin) |
| Rate limiting | In-process sliding window — `GENESIS_RATE_GLOBAL` (120/min) + `GENESIS_RATE_WRITE` (30/min) per IP |
| Input validation | Pydantic v2 with `Field(ge=0, le=100)` bounds on all numeric inputs |
| Logging | Python `logging` with JSON `StructuredFormatter` — Loki/CloudWatch ready |
| Static files | `StaticFiles` mount at `/ui` — serves `static/index.html` |

### Risk ML Engine (`ai/risk_ml.py`)
Pure NumPy Gradient Boosting regressor trained on 9 EU regulatory framework risk profiles.

- Input: 5 dimensions — CPU, memory, network I/O, disk usage, error rate
- Output: risk score 0–100 + per-feature importance weights
- Calibration: R²=0.8955 on holdout set
- Framework-specific weight matrices (9 profiles, each `5×5`)

### Compliance Engine (embedded in `genesis_api.py`)
Rule-based checks per EU regulatory framework.

| Framework | Key checks |
|---|---|
| Basel III/IV | CET1 ≥ 8%, LCR ≥ 100%, 10-year data retention, EU residency |
| GDPR | Encryption at rest, audit logging, data residency, retention ≤ 2555 days |
| DORA | ICT incident response, recovery time, 3rd-party risk, MFA |
| AI Act | Risk classification, human oversight, transparency, accuracy ≥ 85% |
| AML6 | Transaction monitoring, UBO screening, STR reporting |
| MiFID II | Best execution, trade reporting, client suitability |
| PSD2 | SCA, open banking API, consent management |
| Solvency II | SCR ≥ 100%, MCR ≥ 100%, investment diversification |
| EBA | Internal capital adequacy, stress testing, governance |

### QES / eIDAS 2.0 (`cert/qes_client.py` + API endpoint)
Two-layer signing architecture:

1. **Document hashing** — SHA-256 of document name or pre-computed hash
2. **HMAC-SHA256 signature** — `_GENESIS_SIGNING_KEY` (module-level constant, set once at startup)

For production legal effect: configure `GENESIS_SIGNING_KEY` + QTSP provider URLs (`QTSP_SWISSCOM_URL` / `QTSP_ENTRUST_URL` / `QTSP_DTRUST_URL`).

### Local AI (`scripts/start_llama.ps1` → llama-server port 8090)
- Model: Qwen2.5-0.5B-Instruct Q4_K_M GGUF (~350 MB)
- Backend: llama.cpp via Vulkan (NVIDIA RTX 3060 Laptop)
- Used by: `POST /api/ai/explain` — plain-language risk explanations

### Audit Trail
Append-only SQLite table (`data/audit.db`). Every compliance check, risk score, QES signing, and key operation is logged with timestamp + genesis_version.

### Multi-tenant Key Management
```
GENESIS_ADMIN_KEY → POST /api/admin/keys → raw key (returned once)
                                         → SHA-256 hash stored in SQLite api_keys table
Client request → X-API-Key: <raw>       → SHA-256 lookup → tenant_id resolved
```

---

## Deployment Topology

```
Docker Compose (docker-compose.yml):

  genesis-api   — python:3.12-slim, port 8080
  llama-server  — GPU-enabled, port 8090
  nginx         — ports 80/443, TLS termination
```

### Kubernetes (optional, `operator/`)
Custom CRD (`GenesisTenant`) + controller for multi-tenant isolation.  
See `operator/api/v1/types.go` and `operator/controllers/tenant_controller.go`.

### Cloud targets
`deploy/cloud-aws.sh` · `deploy/cloud-azure.sh` · `deploy/cloud-gcp.sh`

---

## Data Flow — Risk Assessment Request

```
Client
  │  POST /api/risk/score  {cpu:75, memory:82, ...}
  │  X-API-Key: <key>
  ▼
nginx (TLS termination)
  ▼
FastAPI
  ├─ Auth: SHA-256(key) → lookup SQLite api_keys → tenant_id
  ├─ Rate: sliding window check (120/min read)
  ├─ Pydantic: validate 0≤cpu≤100, 0≤memory≤100, ...
  ├─ Risk ML: _predict_risk(cpu, memory, ..., framework)
  │     → framework weight matrix × input vector
  │     → Gradient Boosting score 0–100
  │     → risk_level + regulatory_action
  ├─ Audit: INSERT INTO audit_log (action="risk_score", ...)
  └─ Response: {risk_score, risk_level, feature_importance, ...}
```

---

## Observability Stack

```
FastAPI /metrics (Prometheus text format)
  └─► Prometheus scrape
        └─► Grafana (grafana/genesis-dashboard.json)
              └─► Alerts (alerts.sh)

Structured JSON logs (stdout)
  └─► Docker log driver → Loki / CloudWatch / Elastic
```

Key metrics: `genesis_up` · `genesis_model_r2` · `genesis_audit_entries_total` · `genesis_api_keys_total` · `genesis_frameworks_total`

---

## Security Model

| Layer | Control |
|---|---|
| Transport | TLS 1.2/1.3 via nginx; HSTS; CSP |
| Authentication | SHA-256 hashed API keys in SQLite |
| Secrets | All keys read once from env vars at startup — never logged |
| Rate limiting | Sliding window per IP — prevents brute force and abuse |
| Input validation | Pydantic bounds on every numeric field — no injection surface |
| Audit | Append-only log — tamper evidence via sequential IDs |
| QES signing key | Module-level constant — consistent signatures, no per-request randomisation |
