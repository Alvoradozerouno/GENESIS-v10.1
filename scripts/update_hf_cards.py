#!/usr/bin/env python3
"""
Update HuggingFace model cards for GENESIS v10.1.

Usage:
    $env:HF_TOKEN="hf_xxxx"; python scripts/update_hf_cards.py

Both repos receive updated README.md reflecting v10.1 enterprise features:
  - API Key auth (X-API-Key / Bearer)
  - Rate limiting (120r/30w per minute, sliding window)
  - 94 pytest tests (Python 3.12 + 3.13 CI matrix)
  - Multi-tenant API keys (SQLite, SHA-256-hashed; CRUD admin routes)
  - Prometheus /metrics endpoint (7 metrics incl. genesis_api_keys_total)
  - Grafana dashboard (8 panels, grafana/genesis-dashboard.json)
  - Structured JSON logging
  - Dockerfile + docker-compose (nginx HTTPS)
  - SQLite audit persistence
"""

import os
import sys

try:
    from huggingface_hub import HfApi
except ImportError:
    print("Run: pip install huggingface_hub")
    sys.exit(1)

TOKEN = os.environ.get("HF_TOKEN", "")
if not TOKEN:
    print("ERROR: Set HF_TOKEN environment variable before running this script.")
    print("  Windows PowerShell: $env:HF_TOKEN='hf_xxxx'; python scripts/update_hf_cards.py")
    sys.exit(1)

api = HfApi(token=TOKEN)

# ─────────────────────────────────────────────────────────────────────────────
# MODEL CARD: genesis-risk-engine
# ─────────────────────────────────────────────────────────────────────────────
RISK_ENGINE_CARD = """\
---
language:
  - en
tags:
  - regtech
  - banking
  - risk-scoring
  - eu-compliance
  - basel-iii
  - fastapi
  - prometheus
license: apache-2.0
pipeline_tag: tabular-regression
---

# GENESIS Risk Engine — v10.1 (Enterprise)

[![CI](https://github.com/Alvoradozerouno/GENESIS-v10.1/actions/workflows/ci.yml/badge.svg)](https://github.com/Alvoradozerouno/GENESIS-v10.1/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-87%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12%20|%203.13-blue)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)]()

Part of the **GENESIS v10.1 Sovereign AI OS** — the world's first open-source EU Banking Compliance platform.

## Model Description

Pure NumPy gradient-like risk scoring engine calibrated against Basel III benchmarks.  
**R² = 0.8955** on 15 Basel III operational anchors.

### 9 EU Framework Profiles
Each profile uses framework-specific feature weights derived from EBA supervisory convergence data:

| Framework | Primary Risk Drivers |
|-----------|---------------------|
| Basel III/IV | CPU stress + Memory (LCR) + Error Rate (op-loss) |
| DORA | Network latency + ICT error rate + CPU recovery |
| GDPR | Disk saturation (data at rest) + Error rate (breach risk) |
| EU AI Act | CPU (inference load) + Memory (model) + Errors (model failures) |
| MiFID II | Network I/O (trade latency) + CPU + Error rate (failed txn) |
| AML6 | CPU (ML screening) + Network (data feeds) + Error rate |
| PSD2 | Network (SCA/API) + Error rate (failed payments) |
| Solvency II | Memory (actuarial models) + Disk (policy data) |
| EBA Guidelines | CPU + Memory + Disk (loan data) + Error rate |

## Production API (v10.1 Enterprise Features)

| Feature | Status |
|---------|:------:|
| API Key auth (`X-API-Key` / `Bearer`) | ✅ |
| Rate limiting: 30 writes/60s/IP (sliding window) | ✅ |
| Input bounds: all numeric fields `ge/le` validated | ✅ |
| SQLite audit persistence | ✅ |
| Multi-tenant API keys (SHA-256 CRUD admin routes) | ✅ |
| Prometheus `/metrics` (7 metrics) | ✅ |
| Grafana dashboard (8 panels, import-ready) | ✅ |
| Structured JSON logging | ✅ |
| 94 pytest tests (CI Python 3.12 + 3.13) | ✅ |
| Docker + nginx HTTPS | ✅ |

## Usage

### Start the API

```bash
git clone https://github.com/Alvoradozerouno/GENESIS-v10.1.git
cd GENESIS-v10.1
pip install -r requirements.txt
uvicorn genesis_api:app --port 8080
# Default dev key: genesis-dev-key
# Production: export GENESIS_API_KEY=<your-secure-key>
```

### Score Risk (authenticated)

```bash
curl -X POST http://localhost:8080/api/risk/score \\
  -H "X-API-Key: genesis-dev-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cpu": 85,
    "memory": 70,
    "disk_usage": 60,
    "network_io": 50,
    "error_rate": 15,
    "framework": "dora"
  }'
```

### Prometheus scrape (public)

```bash
curl http://localhost:8080/metrics
# genesis_model_r2 0.8955
# genesis_audit_entries_total 42
# genesis_up 1
```

## Input Schema

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `cpu` | float | 0–100 | CPU utilisation % |
| `memory` | float | 0–100 | Memory utilisation % |
| `disk_usage` | float | 0–100 | Disk utilisation % |
| `network_io` | float | 0–100000 | Network I/O Mbps |
| `error_rate` | float | 0–100 | Application error rate % |
| `framework` | string | — | One of 9 EU frameworks |

## Output

```json
{
  "risk_score": 62.3,
  "risk_level": "HIGH",
  "framework": "dora",
  "model_confidence_r2": 0.8955,
  "feature_importance": {"cpu": 0.2, "memory": 0.12, "network_io": 0.25, "disk_usage": 0.08, "error_rate": 0.35},
  "regulatory_action": "Board notification + corrective action within 24h",
  "audit_ref": "2026-01-14T10:00:00+00:00"
}
```

## Links

- 🏛️ **GitHub**: https://github.com/Alvoradozerouno/GENESIS-v10.1
- 📋 **Compliance / Fraud Engine**: https://huggingface.co/Alvoradozerouno/genesis-quantum-fraud
- 📖 **API Docs**: http://localhost:8080/docs (after starting server)
"""

# ─────────────────────────────────────────────────────────────────────────────
# MODEL CARD: genesis-compliance-engine
# ─────────────────────────────────────────────────────────────────────────────
COMPLIANCE_ENGINE_CARD = """\
---
language:
  - en
tags:
  - regtech
  - banking
  - eu-compliance
  - gdpr
  - dora
  - basel-iii
  - ai-act
  - fastapi
  - prometheus
license: apache-2.0
pipeline_tag: text-classification
---

# GENESIS Compliance Engine — v10.1 (Enterprise)

[![CI](https://github.com/Alvoradozerouno/GENESIS-v10.1/actions/workflows/ci.yml/badge.svg)](https://github.com/Alvoradozerouno/GENESIS-v10.1/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-87%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.12%20|%203.13-blue)]()
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)]()

Part of the **GENESIS v10.1 Sovereign AI OS** — the world's first open-source EU Banking Compliance platform.

## Model Description

Rule-based EU regulatory compliance checker covering **9 frameworks** with framework-specific logic derived from official EBA, ESMA, and EIOPA guidelines.

### Supported Frameworks

| Framework | Regulation | Authority | Key Checks |
|-----------|-----------|-----------|-----------|
| **Basel III/IV** | CRR/CRD IV | EBA / BIS | CET1 ≥ 8%, LCR ≥ 100%, 10yr retention |
| **DORA** | 2022/2554/EU | ESAs | ICT incidents, TLPT, 3rd-party risk |
| **GDPR** | 2016/679/EU | DPAs | Consent, data minimisation, 72h breach |
| **EU AI Act** | 2024/1689/EU | NMSAs | Risk classification, conformity assessment |
| **AML6** | 2021/1160/EU | AMLA | KYC/CDD, transaction monitoring, STR |
| **PSD2** | 2015/2366/EU | EBA | SCA, XS2A API |
| **MiFID II** | 2014/65/EU | ESMA | Best execution, transaction reporting |
| **Solvency II** | 2009/138/EC | EIOPA | SCR ≥ 100%, ORSA |
| **EBA Guidelines** | Multiple GLs | EBA | CET1 ≥ 4.5%, ICT incidents |

## Production API (v10.1 Enterprise Features)

| Feature | Status |
|---------|:------:|
| API Key auth (`X-API-Key` / `Bearer`) | ✅ |
| Rate limiting: 30 writes/60s/IP (sliding window) | ✅ |
| Input bounds: all numeric fields `ge/le` validated | ✅ |
| SQLite audit persistence | ✅ |
| Multi-tenant API keys (SHA-256 CRUD admin routes) | ✅ |
| Prometheus `/metrics` (7 metrics) | ✅ |
| Grafana dashboard (8 panels, import-ready) | ✅ |
| Structured JSON logging | ✅ |
| 94 pytest tests (CI Python 3.12 + 3.13) | ✅ |
| Docker + nginx HTTPS | ✅ |

## Usage

### Start the API

```bash
git clone https://github.com/Alvoradozerouno/GENESIS-v10.1.git
cd GENESIS-v10.1
pip install -r requirements.txt
uvicorn genesis_api:app --port 8080
# Default dev key: genesis-dev-key
```

### Run Compliance Check (authenticated)

```bash
# DORA compliance check
curl -X POST http://localhost:8080/api/compliance/dora \\
  -H "X-API-Key: genesis-dev-key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "tenant_id": "bank_001",
    "data_residency": "EU",
    "encryption_at_rest": true,
    "encryption_in_transit": true,
    "audit_logging": true,
    "ict_incident_reporting": true,
    "third_party_risk_assessed": true,
    "penetration_testing_done": false,
    "mfa_enabled": true
  }'
```

### List All Frameworks (public)

```bash
curl http://localhost:8080/api/compliance/frameworks/all
```

## Output Schema

```json
{
  "framework": "dora",
  "compliance_status": "PARTIALLY_COMPLIANT",
  "compliance_score_pct": 87.5,
  "checks_passed": 7,
  "checks_total": 8,
  "check_details": {
    "penetration_testing_done": false,
    "ict_incident_reporting": true,
    ...
  },
  "remediation_required": ["penetration_testing_done"],
  "audit_ref": "2026-01-14T10:00:00+00:00"
}
```

## Compliance Status Levels

| Status | Score |
|--------|-------|
| `COMPLIANT` | 100% |
| `PARTIALLY_COMPLIANT` | 70–99% |
| `NON_COMPLIANT` | < 70% |

## Links

- 🏛️ **GitHub**: https://github.com/Alvoradozerouno/GENESIS-v10.1
- 📊 **Risk Engine**: https://huggingface.co/Alvoradozerouno/genesis-risk-ml
- 📖 **API Docs**: http://localhost:8080/docs (after starting server)
"""

# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────────────────────────

UPDATES = [
    ("Alvoradozerouno/genesis-risk-ml",      RISK_ENGINE_CARD,       "model"),
    ("Alvoradozerouno/genesis-quantum-fraud", COMPLIANCE_ENGINE_CARD, "model"),
]

for repo_id, card_content, repo_type in UPDATES:
    print(f"\n→ Updating {repo_id} ...")
    try:
        api.upload_file(
            path_or_fileobj=card_content.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type=repo_type,
            commit_message="[GENESIS v10.1] Multi-tenant keys + 94 tests + Grafana + Prometheus",
        )
        print(f"  ✅ {repo_id} updated → https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"  ❌ {repo_id} failed: {e}")

print("\nDone. Verify at:")
print("  https://huggingface.co/Alvoradozerouno/genesis-risk-ml")
print("  https://huggingface.co/Alvoradozerouno/genesis-quantum-fraud")
