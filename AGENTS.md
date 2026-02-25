# AGENTS.md

## Cursor Cloud specific instructions

### Codebase overview

GENESIS v10.1 is a Sovereign AI Operating System for banking/RegTech. It is **not** a traditional web app — it is an infrastructure automation platform that deploys onto Kubernetes. The locally-runnable components are:

| Component | Language | Location | Run command |
|-----------|----------|----------|-------------|
| Tenant Operator | Go 1.22 | `operator/` | `go build -o genesis-operator ./cmd/main.go` (needs K8s cluster to run) |
| Risk ML Engine | Python 3 | `ai/risk_ml.py` | `python3 ai/risk_ml.py [cpu] [mem] [net] [disk] [err]` |
| eIDAS QES Client | Python 3 | `cert/qes_client.py` | `python3 cert/qes_client.py [document] [provider]` |
| Control Center UI | HTML/JS | `ui/index.html` | `python3 -m http.server 8080` from `ui/` dir |
| Alerting | Bash | `alerts.sh` | Requires `SLACK_WEBHOOK` or `PAGERDUTY_KEY` env vars |
| XBRL Validator | Bash | `regulatory/validate_xbrl.sh` | Requires `arelle-release` pip package |
| Main Deployer | Bash | `genesis_v10.1.sh` | Requires a live Kubernetes cluster |

### Key caveats

- The Go operator (`operator/`) has no `go.sum` committed. Run `go mod tidy` before building.
- Python scripts have no `requirements.txt`. Dependencies (`numpy`, `scikit-learn`, `pandas`) are auto-installed inline in `risk_ml.py` on first run, but for dev setup use: `pip3 install numpy scikit-learn pandas`.
- `genesis_v10.1.sh` requires a live Kubernetes cluster with `kubectl`, `helm`, and several other CLI tools. It cannot run without K8s.
- The Go operator binary builds but cannot *run* locally — it calls `ctrl.GetConfigOrDie()` which requires a kubeconfig / in-cluster K8s API.
- There are no automated tests in the repository.

### Lint commands

- **Go**: `cd operator && go vet ./...`
- **Bash**: `shellcheck genesis_v10.1.sh alerts.sh regulatory/validate_xbrl.sh`
- **Python**: `python3 -m py_compile ai/risk_ml.py && python3 -m py_compile cert/qes_client.py`

### Build commands

- **Go operator**: `cd operator && go build -o genesis-operator ./cmd/main.go`

### Running the UI dashboard

```bash
cd ui && python3 -m http.server 8080
```

Then open `http://localhost:8080/` in a browser.
