# GENESIS v10.1 — API Reference

Base URL: `http://localhost:8080`  
Interactive docs: `http://localhost:8080/docs` (Swagger UI) · `http://localhost:8080/redoc`  
Authentication: `X-API-Key: <key>` header or `Authorization: Bearer <key>`

---

## Authentication

All protected endpoints require a valid API key.

| Key type | Header | Source |
|---|---|---|
| Tenant key | `X-API-Key` or `Authorization: Bearer` | Issued via `/api/admin/keys` |
| Admin key | `X-API-Key` | `GENESIS_ADMIN_KEY` env var |

Errors: `401 Unauthorized` (missing/invalid key) · `429 Too Many Requests` (rate limit exceeded)

Rate limits: **120 read** / **30 write** requests per minute per IP.

---

## Operations

### `GET /api/health`
Health check — no auth required.

**Response 200**
```json
{
  "status": "healthy",
  "services": { "risk_ml_engine": "operational", "...": "..." },
  "model_r2": 0.8955,
  "frameworks_loaded": 9,
  "audit_entries": 1024,
  "local_ai_ready": true,
  "uptime_check": "2026-03-01T12:00:00+00:00"
}
```

---

### `GET /api/system/metrics`
Live system metrics via psutil — no auth required.

**Response 200**
```json
{
  "cpu_usage_pct": 12.3,
  "memory_usage_pct": 44.1,
  "disk_usage_pct": 38.0,
  "network_io_mbps": 0.04,
  "error_rate_pct": 0.0,
  "memory_total_gb": 16.0,
  "timestamp": "2026-03-01T12:00:00+00:00"
}
```

---

## Risk ML Engine

### `POST /api/risk/score` 🔒
Predict infrastructure risk score using the Gradient Boosting engine (R²=0.8955).

**Request body**
```json
{
  "cpu": 75.0,
  "memory": 82.0,
  "network_io": 45.0,
  "disk_usage": 60.0,
  "error_rate": 2.5,
  "framework": "basel_iii",
  "tenant_id": "tenant-001"
}
```

| Field | Type | Range | Required |
|---|---|---|---|
| `cpu` | float | 0–100 | ✅ |
| `memory` | float | 0–100 | ✅ |
| `network_io` | float | 0–100 | ✅ |
| `disk_usage` | float | 0–100 | ✅ |
| `error_rate` | float | 0–100 | ✅ |
| `framework` | string | see `/api/compliance/frameworks/all` | optional |
| `tenant_id` | string | — | optional |

**Response 200**
```json
{
  "risk_score": 68.42,
  "risk_level": "HIGH",
  "feature_importance": { "cpu": 0.31, "memory": 0.27, "..." : 0.0 },
  "model_confidence_r2": 0.8955,
  "regulatory_action": "Board notification + corrective action within 24h",
  "timestamp": "2026-03-01T12:00:00+00:00",
  "audit_ref": "2026-03-01T12:00:00+00:00"
}
```

Risk levels: `MINIMAL` (0–19) · `LOW` (20–39) · `MEDIUM` (40–59) · `HIGH` (60–79) · `CRITICAL` (80–100)

---

## Compliance Engine

### `GET /api/compliance/frameworks/all`
List all 9 supported EU regulatory frameworks — no auth required.

**Response 200**
```json
{
  "total_frameworks": 9,
  "frameworks": {
    "basel_iii": { "name": "Basel III/IV Capital Adequacy", "authority": "EBA/BIS" },
    "gdpr":      { "name": "GDPR Data Protection", "authority": "EDPB" },
    "..."
  },
  "coverage": "Basel III/IV, MiFID II, GDPR, AI Act, AML6, DORA, PSD2, Solvency II, EBA"
}
```

Available framework keys: `basel_iii` · `mifid_ii` · `gdpr` · `ai_act` · `aml6` · `dora` · `psd2` · `solvency_ii` · `eba`

---

### `POST /api/compliance/{framework}` 🔒
Run compliance check against a specific EU regulatory framework.

**Path parameter:** `framework` — one of the keys from `/api/compliance/frameworks/all`

**Request body (example — Basel III)**
```json
{
  "data_residency": "EU",
  "encryption_at_rest": true,
  "audit_logging": true,
  "mfa_enabled": true,
  "cet1_ratio_pct": 12.5,
  "lcr_ratio_pct": 110.0,
  "data_retention_days": 3650
}
```

**Response 200**
```json
{
  "framework": "basel_iii",
  "compliant": true,
  "score": 100,
  "checks": {
    "data_residency_eu": true,
    "cet1_above_minimum": true,
    "lcr_above_100pct": true,
    "data_retention_10yr": true,
    "...": true
  },
  "timestamp": "2026-03-01T12:00:00+00:00"
}
```

**Errors:** `404` — unknown framework

---

## QES / eIDAS 2.0

### `POST /api/cert/sign` 🔒
Qualified Electronic Signature (QES) — SHA-256 document hash + HMAC-SHA256 signing.  
eIDAS 2.0 compliant, PAdES-B-LT format, EUDI Wallet ready.

**Request body**
```json
{
  "document_name": "contract-2026-001.pdf",
  "document_hash": "optional-precomputed-sha256",
  "signer": "max.mustermann@example.com",
  "provider": "swisscom"
}
```

| `provider` | Service |
|---|---|
| `swisscom` | Swisscom All-in Signing Service (CH/EU) |
| `entrust` | Entrust Remote Signing (EU) |
| `dtrust` | D-Trust / Bundesdruckerei (DE/EU) |

**Response 200**
```json
{
  "signing_status": "SIGNED",
  "document_sha256": "e3b0c44298fc1c14...",
  "signature_hmac_sha256": "a1b2c3d4...",
  "signature_level": "QES",
  "signature_format": "PAdES-B-LT",
  "eidas_compliance": "eIDAS 2.0 Article 26",
  "eudi_wallet_ready": true,
  "legal_weight": "Equivalent to handwritten signature (EU eIDAS Regulation)",
  "timestamp": "2026-03-01T12:00:00+00:00"
}
```

---

## Local AI (llama.cpp)

### `GET /api/ai/status`
Check llama-server availability — no auth required.

**Response 200**
```json
{
  "llama_server": "online",
  "endpoint": "http://localhost:8090",
  "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "start_cmd": "scripts/start_llama.ps1"
}
```

---

### `POST /api/ai/explain` 🔒
Ask local Qwen2.5-0.5B to explain a risk assessment result in plain language.  
Requires llama-server running (`scripts/start_llama.ps1`).

**Request body**
```json
{
  "framework": "dora",
  "risk_score": 72.5,
  "risk_level": "HIGH",
  "regulatory_action": "Board notification + corrective action within 24h",
  "feature_importance": { "cpu": 0.4, "memory": 0.3, "error_rate": 0.2 },
  "max_tokens": 200
}
```

**Response 200**
```json
{
  "framework": "dora",
  "risk_score": 72.5,
  "explanation": "The infrastructure shows elevated risk primarily...",
  "model": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
  "timestamp": "2026-03-01T12:00:00+00:00"
}
```

**Errors:** `503` — llama-server offline · `502` — LLM inference failed

---

## Audit Trail

### `GET /api/audit` 🔒
Retrieve immutable audit log entries from SQLite.

**Query parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 50 | Max entries to return |

**Response 200**
```json
{
  "total_entries": 1024,
  "showing": 50,
  "entries": [
    {
      "timestamp": "2026-03-01T12:00:00+00:00",
      "action": "risk_score",
      "payload": { "score": 68.42, "level": "HIGH" },
      "genesis_version": "10.1.4"
    }
  ]
}
```

---

## Key Management (Admin)

All endpoints require `X-API-Key: <GENESIS_ADMIN_KEY>`.

### `POST /api/admin/keys` 🔒🔑
Create a new tenant API key. The raw key is returned **once** — store it securely.

**Request body**
```json
{ "tenant_id": "tenant-acme", "name": "ACME Bank Production" }
```

**Response 200**
```json
{
  "id": 3,
  "key": "raw-key-returned-once",
  "tenant_id": "tenant-acme",
  "name": "ACME Bank Production",
  "warning": "Store this key securely — it cannot be retrieved again."
}
```

---

### `GET /api/admin/keys` 🔒🔑
List all API keys. Key hashes are never exposed.

---

### `DELETE /api/admin/keys/{key_id}` 🔒🔑
Soft-revoke a key by id.

**Response 200**
```json
{ "revoked": true, "key_id": 3 }
```

---

## Observability

### `GET /metrics`
Prometheus text-format exposition — no auth required.

```
genesis_up 1
genesis_model_r2 0.8955
genesis_frameworks_total 9
genesis_audit_entries_total 1024
genesis_api_keys_total 5
genesis_rate_window_entries 12
genesis_rate_limit_global 120
genesis_rate_limit_write 30
```

---

## Market Intelligence

### `GET /api/valuation`
GENESIS v10.1 market valuation summary — no auth required.

---

## Browser Dashboard

### `GET /` → redirects to `/ui`
### `GET /ui` — Full browser dashboard

Served from `static/index.html`. Features: live health, R² gauge, system metrics, 9 EU frameworks grid, risk scorer (5 sliders), audit log table. Auto-refreshes every 5 seconds.
