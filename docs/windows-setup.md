# GENESIS v10.1 Windows Setup Guide

## Prerequisites Installation for Windows

This guide helps you install all required tools for GENESIS v10.1 on Windows.

### Required Tools Checklist

- [x] Git - Already installed (2.52.0)
- [x] Python - Already installed (3.14.0)
- [ ] kubectl - Kubernetes CLI
- [ ] Helm - Kubernetes package manager
- [ ] Go - Go programming language
- [ ] jq - JSON processor
- [ ] OpenSSL - Cryptography toolkit
- [ ] Cosign - Container signing
- [ ] Trivy - Vulnerability scanner
- [ ] Syft - SBOM generator

---

## Installation Steps

### 1. Install Python Dependencies

```powershell
# Navigate to GENESIS directory
cd "C:\Users\annah\Dropbox\Mein PC (LAPTOP-RQH448P4)\Downloads\GENESIS-v10.1"

# Install Python packages
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install Chocolatey (Package Manager)

If not already installed:

```powershell
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 3. Install kubectl

```powershell
# Via Chocolatey
choco install kubernetes-cli -y

# OR via direct download
curl.exe -LO "https://dl.k8s.io/release/v1.29.0/bin/windows/amd64/kubectl.exe"
# Move to C:\Program Files\kubectl\kubectl.exe and add to PATH
```

### 4. Install Helm

```powershell
# Via Chocolatey
choco install kubernetes-helm -y

# OR via Scoop
scoop install helm
```

### 5. Install Go

```powershell
# Via Chocolatey
choco install golang -y

# OR download from https://go.dev/dl/
# Install go1.22.windows-amd64.msi
```

### 6. Install jq

```powershell
# Via Chocolatey
choco install jq -y

# OR via Scoop
scoop install jq
```

### 7. Install OpenSSL

```powershell
# Via Chocolatey
choco install openssl -y

# OR download from https://slproweb.com/products/Win32OpenSSL.html
# Install Win64OpenSSL-3_2_0.exe
```

### 8. Install Cosign

```powershell
# Download latest release
$COSIGN_VERSION = "v2.2.3"
curl.exe -LO "https://github.com/sigstore/cosign/releases/download/$COSIGN_VERSION/cosign-windows-amd64.exe"

# Rename and move to PATH
Rename-Item cosign-windows-amd64.exe cosign.exe
Move-Item cosign.exe "C:\Program Files\cosign\cosign.exe" -Force
# Add C:\Program Files\cosign to PATH
```

### 9. Install Trivy

```powershell
# Via Chocolatey
choco install trivy -y

# OR download from https://github.com/aquasecurity/trivy/releases
```

### 10. Install Syft

```powershell
# Download latest release
$SYFT_VERSION = "v1.0.1"
curl.exe -LO "https://github.com/anchore/syft/releases/download/$SYFT_VERSION/syft_${SYFT_VERSION}_windows_amd64.zip"

# Extract and move to PATH
Expand-Archive syft_${SYFT_VERSION}_windows_amd64.zip -DestinationPath "C:\Program Files\syft"
# Add C:\Program Files\syft to PATH
```

---

## Verification

After installation, verify all tools:

```powershell
# Verify installations
kubectl version --client
helm version --short
go version
jq --version
openssl version
cosign version
trivy --version
syft version
python --version
git --version
```

---

## Kubernetes Cluster Setup

GENESIS requires a Kubernetes cluster. For local development:

### Option 1: Docker Desktop with Kubernetes

1. Install Docker Desktop for Windows
2. Enable Kubernetes in Settings > Kubernetes
3. Wait for cluster to start

### Option 2: Minikube

```powershell
# Install Minikube
choco install minikube -y

# Start cluster
minikube start --driver=docker --cpus=4 --memory=8192
```

### Option 3: Kind (Kubernetes in Docker)

```powershell
# Install Kind
choco install kind -y

# Create cluster
kind create cluster --name genesis --config kind-config.yaml
```

---

## WSL2 Alternative (Recommended for Production-like Testing)

For better compatibility with the bash-based deployment script:

```powershell
# Install WSL2
wsl --install

# Install Ubuntu
wsl --install -d Ubuntu-22.04

# Inside WSL, install tools via apt
sudo apt update
sudo apt install -y curl git jq python3 python3-pip golang-go

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Cosign, Trivy, Syft (same pattern as above, Linux versions)
```

---

## Next Steps

Once all tools are installed:

1. **Configure kubectl** to point to your cluster:
   ```powershell
   kubectl cluster-info
   kubectl get nodes
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run GENESIS deployment**:
   ```bash
   # If using WSL
   bash genesis_v10.1.sh
   
   # If using PowerShell (may require adaptations)
   # Convert bash script to PowerShell or run via Git Bash
   ```

---

## Troubleshooting

### PATH Not Updated

After installing tools, restart PowerShell or run:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Permission Errors

Run PowerShell as Administrator for installations.

### Kubernetes Cluster Not Available

Ensure Docker Desktop Kubernetes is running:

```powershell
kubectl cluster-info
```

### Genesis Script Requires Bash

The `genesis_v10.1.sh` script is bash-based. Use one of:

1. **WSL2** (recommended)
2. **Git Bash** (included with Git for Windows)
3. **Cygwin**
4. **Convert to PowerShell** (advanced)

---

## Authors

- ORION
- Gerhard Hirschmann
- Elisabeth Steurer

## License

Apache 2.0
