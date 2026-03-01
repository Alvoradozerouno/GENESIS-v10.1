# Changelog

All notable changes to GENESIS v10.1 are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [10.1.4] — 2026-03-01

### Security
- `_GENESIS_SIGNING_KEY` promoted to module-level constant — was re-randomised per-request when env var unset, causing non-reproducible signatures

### CI/CD
- GitHub Actions: added 6 previously missing pip packages (`scikit-learn`, `pandas`, `pydantic`, `cryptography`, `aiofiles`, `python-multipart`, `prometheus-client`)
- Lint scope extended to `cert/`, `ai/`, `scripts/`

### Documentation
- Full repo restructure: 28 root-level markdown files moved to `docs/`, `docs/setup/`, `docs/marketing/`, `archive/`
- Added `docs/api-reference.md` — complete reference for all 15 endpoints
- Added `docs/architecture.md` — system architecture overview
- Added `CHANGELOG.md`
- `pyproject.toml` created with pytest + ruff + mypy config
- `.env.example` rewritten with all 14 environment variables (clean UTF-8)
- `.gitignore` updated: added `mypy_cache/` and `.mypy_cache/`

### Fixed
- `ui/index.html` replaced with meta-refresh redirect to `/ui` (was stale Tailwind/Alpine CDN dashboard)
- README badge updated: `87 passing` → `94 passing`

---

## [10.1.3] — 2026-02-28

### Added
- `static/index.html` — full browser dashboard: R² semicircle gauge, system metrics bars, 9 EU frameworks grid, live risk scorer (5 sliders), audit log table, 5s auto-refresh
- FastAPI `StaticFiles` mount at `/ui`; root `/` redirects to `/ui`
- `cert/qes_client.py` — real X.509 parsing via `cryptography` lib (expiry, subject, issuer, QcStatement OID)
- `scripts/setup_discord.py` — Discord webhook announcement with rich embed, `--dry-run`, `--guide` flags

### Changed
- QES endpoint: "Simulate QES" → real HMAC-SHA256 signing with `_GENESIS_SIGNING_KEY`
- Removed all "dev/demo" startup annotations

---

## [10.1.2] — 2026-02-20

### Added
- Multi-tenant API key management: SQLite-backed SHA-256 hashed keys
- Admin CRUD routes (`POST/GET/DELETE /api/admin/keys`) protected by separate `GENESIS_ADMIN_KEY`
- Grafana dashboard JSON (`grafana/genesis-dashboard.json`)
- `scripts/start_api.ps1`, `scripts/post_reddit.py`
- GitHub repository topics set (10 topics)

---

## [10.1.1] — 2026-02-15

### Added
- Rate limiting: sliding window 120 reads / 30 writes per minute per IP — `429 + Retry-After`
- Input validation: Pydantic `Field(ge/le)` bounds on all numeric inputs
- CI/CD GitHub Actions matrix (Python 3.12 + 3.13)
- nginx HTTPS configuration (`nginx/genesis.conf`)
- Prometheus `/metrics` endpoint
- Structured JSON logging (Loki / CloudWatch ready)

### Security
- API Key authentication (`X-API-Key` header / `Authorization: Bearer`)

---

## [10.1.0] — 2026-02-01

### Initial Release
- FastAPI compliance API with 9 EU regulatory frameworks (Basel III/IV, MiFID II, GDPR, AI Act, AML6, DORA, PSD2, Solvency II, EBA)
- Risk ML Engine: Gradient Boosting — R²=0.8955, 5-dimensional input
- QES / eIDAS 2.0 signing endpoint
- Append-only SQLite audit trail
- llama.cpp integration: Qwen2.5-0.5B-Instruct GGUF
- Docker + docker-compose stack
- Kubernetes operator (`operator/`)
- EU Federation layer (`federation/treaty.json`)
