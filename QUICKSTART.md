# GENESIS v10.1 - Quick Start Guide

**Time to First Deployment: 1-2 Hours**

---

## 🚀 Fastest Path to Running System

### Option 1: WSL2 (Recommended for Windows)

```powershell
# 1. Install WSL2
wsl --install
wsl --install -d Ubuntu-22.04

# 2. Enter WSL
wsl

# 3. Install tools in Ubuntu
sudo apt update
sudo apt install -y curl git jq python3 python3-pip golang-go

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install k3d (lightweight Kubernetes)
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# 4. Create Kubernetes cluster
k3d cluster create genesis --servers 1 --agents 2

# 5. Navigate to GENESIS
cd /mnt/c/Users/annah/Dropbox/Mein\ PC\ \(LAPTOP-RQH448P4\)/Downloads/GENESIS-v10.1

# 6. Install Python dependencies
pip3 install -r requirements.txt

# 7. Deploy GENESIS
chmod +x genesis_v10.1.sh
./genesis_v10.1.sh

# 8. Watch deployment
kubectl get pods -A --watch
```

**Total Time: ~45-60 minutes**

---

### Option 2: Docker Desktop (Simpler but Heavier)

```powershell
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Enable Kubernetes
# Docker Desktop → Settings → Kubernetes → Enable Kubernetes

# 3. Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 4. Install tools via Chocolatey
choco install kubernetes-cli kubernetes-helm jq golang git -y

# 5. Open Git Bash and navigate to GENESIS
cd "C:/Users/annah/Dropbox/Mein PC (LAPTOP-RQH448P4)/Downloads/GENESIS-v10.1"

# 6. Install Python dependencies
pip install -r requirements.txt

# 7. Deploy GENESIS
bash genesis_v10.1.sh
```

**Total Time: ~60-90 minutes**

---

## 🧪 Minimal Test Deployment (No Kubernetes)

Test individual components without full Kubernetes setup:

### 1. AI Risk ML Engine

```powershell
cd "C:\Users\annah\Dropbox\Mein PC (LAPTOP-RQH448P4)\Downloads\GENESIS-v10.1"

# Install dependencies
pip install numpy scikit-learn pandas

# Run risk assessment
python ai/risk_ml.py

# Check output
cat ai/risk_score.txt
```

**Expected Output:**
```
Risk Score: 45.3 (MEDIUM)
Confidence: ±8.2
Features: [cpu=0.65, memory=0.72, network=0.45, disk=0.58, errors=12]
```

### 2. eIDAS QES Client (Mock Mode)

```powershell
# Run QES client (will use mock signatures without real QTSP)
python cert/qes_client.py --mock --document test.pdf

# Check signature output
ls cert/*.sig
```

### 3. XBRL Validator

```bash
# For WSL/Git Bash only
bash regulatory/validate_xbrl.sh sample.xbrl
```

---

## 📊 Verify Deployment

After running `genesis_v10.1.sh`:

```bash
# 1. Check all namespaces created
kubectl get namespaces | grep genesis
kubectl get namespaces | grep system

# Expected: 11 namespaces
# genesis-system, security-system, auth-system, tenant-system,
# ai-system, governance-system, federation-system, audit-system,
# observability, ui-system, backup-system

# 2. Check all pods running
kubectl get pods -A

# Wait until all pods show STATUS: Running

# 3. Access Grafana Dashboard
kubectl port-forward -n observability svc/prometheus-grafana 3000:80

# Open browser: http://localhost:3000
# Default credentials: admin / prom-operator

# 4. Access GENESIS UI
kubectl port-forward -n ui-system svc/genesis-ui 8080:80

# Open browser: http://localhost:8080

# 5. Check Evidence Vault
ls -lh evidence/

# Should contain timestamped directory with:
# - manifest.json
# - audit-package.tar.gz
# - hash.txt
# - sig.txt (if cosign installed)
```

---

## 🎯 Create Your First Tenant

```bash
# 1. Apply Tenant CRD
cat <<EOF | kubectl apply -f -
apiVersion: genesis.ai/v1
kind: Tenant
metadata:
  name: acme-bank
spec:
  displayName: "ACME Bank AG"
  quota: "medium"
  isolation: "namespace"
  oidcGroup: "acme-admins"
  esgEnabled: true
  complianceFrameworks:
    - "GDPR"
    - "PSD2"
    - "Basel III"
EOF

# 2. Watch tenant creation
kubectl get tenants -w

# 3. Check tenant namespace
kubectl get ns | grep tenant-acme-bank

# 4. Verify tenant resources
kubectl get all -n tenant-acme-bank
```

---

## 🔍 Troubleshooting

### Pods stuck in Pending

```bash
# Check events
kubectl get events -A --sort-by='.lastTimestamp'

# Check node resources
kubectl top nodes

# Common issue: Insufficient resources
# Solution: Increase Docker Desktop resources or use k3d
```

### Deployment script fails

```bash
# Check prerequisites
which kubectl helm jq go python3

# Check Kubernetes connectivity
kubectl cluster-info

# Re-run with verbose output
bash -x genesis_v10.1.sh 2>&1 | tee deployment.log
```

### Permission denied errors

```bash
# Make script executable
chmod +x genesis_v10.1.sh

# Check kubeconfig permissions
ls -l ~/.kube/config
```

---

## 📚 Next Steps After Deployment

1. **Read Full Documentation**
   - [README.md](README.md) - Complete system overview
   - [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) - Detailed status
   - [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows-specific guides

2. **Configure Production Settings**
   - QTSP credentials for eIDAS signatures
   - Vault storage backend (AWS S3/Azure Blob)
   - PagerDuty/Slack alerting

3. **Run AI Risk Assessment**
   ```bash
   kubectl exec -n ai-system deploy/risk-ml -- python /app/risk_ml.py
   ```

4. **Test Backup & Restore**
   ```bash
   # Create manual backup
   kubectl exec -n backup-system deploy/velero -- \
     velero backup create genesis-test --wait

   # List backups
   kubectl exec -n backup-system deploy/velero -- \
     velero backup get
   ```

5. **Explore Observability**
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090
   - Alertmanager: http://localhost:9093

---

## 🌐 Production Deployment

For production use:

1. **Cloud Kubernetes** (instead of local)
   - Azure AKS: `az aks create ...`
   - AWS EKS: `eksctl create cluster ...`
   - GCP GKE: `gcloud container clusters create ...`

2. **Update Environment Variables**
   ```bash
   export VAULT_ADDR="https://vault.prod.example.com:8200"
   export KEYCLOAK_URL="https://sso.prod.example.com"
   export SLACK_WEBHOOK="https://hooks.slack.com/..."
   export PAGERDUTY_KEY="..."
   ```

3. **Enable FIPS Mode**
   ```bash
   export FIPS_MODE=true
   export HSM_ENABLED=true
   ```

4. **Configure QTSP Credentials**
   ```bash
   export QTSP_SWISSCOM_URL="https://ais.swisscom.com/..."
   export QTSP_SWISSCOM_KEY="..."
   ```

5. **Deploy to Production**
   ```bash
   ./genesis_v10.1.sh
   ```

---

## ⚡ One-Liner for Advanced Users

Already have Kubernetes and tools installed?

```bash
git clone https://github.com/YOUR_ORG/GENESIS-v10.1.git && \
cd GENESIS-v10.1 && \
pip install -r requirements.txt && \
chmod +x genesis_v10.1.sh && \
./genesis_v10.1.sh
```

**Time: ~15-20 minutes**

---

## 📞 Getting Help

- **Documentation:** [README.md](README.md)
- **Status Check:** [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)
- **Windows Setup:** [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Authors:**
- ORION - Autonomous Sovereign Intelligence
- Gerhard Hirschmann - Architecture & Vision
- Elisabeth Steurer - Regulatory Compliance

**License:** Apache 2.0

---

**Happy Deploying! 🚀**
