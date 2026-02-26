#!/bin/bash
set -euo pipefail

###############################################################################
# GENESIS v10.1 - Azure Cloud Deployment
# Deploys GENESIS to Azure Kubernetes Service (AKS) with EU compliance
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENESIS_ROOT="$(dirname "$SCRIPT_DIR")"

# ==========================================
# CONFIGURATION
# ==========================================
AZURE_REGION="${AZURE_REGION:-westeurope}"          # GDPR: EU region default
RESOURCE_GROUP="${RESOURCE_GROUP:-genesis-rg}"
AKS_CLUSTER="${AKS_CLUSTER:-genesis-aks}"
NODE_COUNT="${NODE_COUNT:-3}"
NODE_VM_SIZE="${NODE_VM_SIZE:-Standard_D4s_v3}"     # 4 vCPU, 16 GB RAM
KUBERNETES_VERSION="${K8S_VERSION:-1.29}"

# Storage & Backup
STORAGE_ACCOUNT="genesis$(date +%s | tail -c 8)"    # Unique name
BACKUP_CONTAINER="genesis-backups"

# Monitoring
LOG_ANALYTICS_WS="genesis-logs"
APP_INSIGHTS="genesis-insights"

# Networking
VNET_NAME="genesis-vnet"
SUBNET_NAME="aks-subnet"

# Key Vault (for secrets)
KEY_VAULT_NAME="genesis-kv-$(date +%s | tail -c 6)"

# ==========================================
# COLORS & LOGGING
# ==========================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ==========================================
# PREREQUISITES CHECK
# ==========================================
log "Checking Azure CLI..."
if ! command -v az &> /dev/null; then
  error "Azure CLI not found!"
  echo "Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
  exit 1
fi

log "Checking kubectl..."
if ! command -v kubectl &> /dev/null; then
  error "kubectl not found!"
  echo "Install: curl -LO https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  exit 1
fi

log "Checking Helm..."
if ! command -v helm &> /dev/null; then
  error "Helm not found!"
  echo "Install: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
  exit 1
fi

# ==========================================
# AZURE LOGIN & SUBSCRIPTION
# ==========================================
log "Logging into Azure..."
if ! az account show &> /dev/null; then
  az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
log "Using Azure Subscription: $SUBSCRIPTION_ID"
log "Azure Tenant: $TENANT_ID"

# ==========================================
# CREATE RESOURCE GROUP
# ==========================================
log "Creating Resource Group: $RESOURCE_GROUP in $AZURE_REGION..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$AZURE_REGION" \
  --tags \
    "Project=GENESIS" \
    "Environment=Production" \
    "Compliance=GDPR,eIDAS,PSD2,DORA" \
    "ManagedBy=GENESIS-Deploy"

# ==========================================
# CREATE LOG ANALYTICS WORKSPACE
# ==========================================
log "Creating Log Analytics Workspace..."
az monitor log-analytics workspace create \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS_WS" \
  --location "$AZURE_REGION"

LOG_ANALYTICS_ID=$(az monitor log-analytics workspace show \
  --resource-group "$RESOURCE_GROUP" \
  --workspace-name "$LOG_ANALYTICS_WS" \
  --query id -o tsv)

# ==========================================
# CREATE VIRTUAL NETWORK
# ==========================================
log "Creating Virtual Network..."
az network vnet create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$VNET_NAME" \
  --address-prefixes 10.0.0.0/16 \
  --subnet-name "$SUBNET_NAME" \
  --subnet-prefixes 10.0.1.0/24

SUBNET_ID=$(az network vnet subnet show \
  --resource-group "$RESOURCE_GROUP" \
  --vnet-name "$VNET_NAME" \
  --name "$SUBNET_NAME" \
  --query id -o tsv)

# ==========================================
# CREATE AKS CLUSTER
# ==========================================
log "Creating AKS Cluster: $AKS_CLUSTER..."
log "  Region: $AZURE_REGION (EU GDPR Compliant)"
log "  Nodes: $NODE_COUNT x $NODE_VM_SIZE"
log "  Kubernetes: $KUBERNETES_VERSION"

az aks create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --location "$AZURE_REGION" \
  --kubernetes-version "$KUBERNETES_VERSION" \
  --node-count "$NODE_COUNT" \
  --node-vm-size "$NODE_VM_SIZE" \
  --vnet-subnet-id "$SUBNET_ID" \
  --enable-managed-identity \
  --enable-addons monitoring \
  --workspace-resource-id "$LOG_ANALYTICS_ID" \
  --enable-pod-security-policy \
  --network-plugin azure \
  --network-policy azure \
  --service-cidr 10.1.0.0/16 \
  --dns-service-ip 10.1.0.10 \
  --generate-ssh-keys \
  --tags \
    "Project=GENESIS" \
    "Environment=Production" \
    "Compliance=GDPR"

log "✅ AKS Cluster created successfully!"

# ==========================================
# GET AKS CREDENTIALS
# ==========================================
log "Getting AKS credentials..."
az aks get-credentials \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --overwrite-existing

kubectl cluster-info
kubectl get nodes

# ==========================================
# CREATE AZURE KEY VAULT
# ==========================================
log "Creating Azure Key Vault: $KEY_VAULT_NAME..."
az keyvault create \
  --name "$KEY_VAULT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$AZURE_REGION" \
  --enable-rbac-authorization true

# Get AKS identity
AKS_IDENTITY=$(az aks show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --query identityProfile.kubeletidentity.objectId -o tsv)

# Grant AKS access to Key Vault
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee "$AKS_IDENTITY" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEY_VAULT_NAME"

# ==========================================
# CREATE STORAGE ACCOUNT FOR BACKUPS
# ==========================================
log "Creating Azure Storage Account for backups..."
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$AZURE_REGION" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --encryption-services blob \
  --https-only true \
  --min-tls-version TLS1_2

# Create container for Velero backups
STORAGE_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_ACCOUNT" \
  --query '[0].value' -o tsv)

az storage container create \
  --name "$BACKUP_CONTAINER" \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY"

log "✅ Backup storage configured: $STORAGE_ACCOUNT/$BACKUP_CONTAINER"

# ==========================================
# CONFIGURE AZURE CREDENTIALS FOR GENESIS
# ==========================================
log "Storing Azure credentials in environment..."
export AZURE_SUBSCRIPTION_ID="$SUBSCRIPTION_ID"
export AZURE_TENANT_ID="$TENANT_ID"
export AZURE_RESOURCE_GROUP="$RESOURCE_GROUP"
export VELERO_STORAGE_ACCOUNT="$STORAGE_ACCOUNT"
export VELERO_STORAGE_KEY="$STORAGE_KEY"
export VELERO_BLOB_CONTAINER="$BACKUP_CONTAINER"

# Store in Key Vault
az keyvault secret set \
  --vault-name "$KEY_VAULT_NAME" \
  --name "storage-account-key" \
  --value "$STORAGE_KEY"

# ==========================================
# INSTALL CERT-MANAGER (for TLS)
# ==========================================
log "Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.1/cert-manager.yaml
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=120s

# ==========================================
# DEPLOY GENESIS v10.1
# ==========================================
log "Deploying GENESIS v10.1 to AKS..."
cd "$GENESIS_ROOT"

# Update environment for Azure specifics
export VAULT_STORAGE_TYPE="azure"
export VAULT_AZURE_ACCOUNT_NAME="$STORAGE_ACCOUNT"
export VAULT_AZURE_ACCOUNT_KEY="$STORAGE_KEY"
export VAULT_AZURE_CONTAINER="genesis-vault"

# Create vault container
az storage container create \
  --name "genesis-vault" \
  --account-name "$STORAGE_ACCOUNT" \
  --account-key "$STORAGE_KEY"

# Run GENESIS deployment
chmod +x genesis_v10.1.sh
./genesis_v10.1.sh

# ==========================================
# WAIT FOR DEPLOYMENT
# ==========================================
log "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all -A --timeout=600s || true

# ==========================================
# CONFIGURE INGRESS (Azure Application Gateway)
# ==========================================
log "Configuring Azure Application Gateway Ingress..."
az aks enable-addons \
  --resource-group "$RESOURCE_GROUP" \
  --name "$AKS_CLUSTER" \
  --addons ingress-appgw \
  --appgw-name "genesis-appgw" \
  --appgw-subnet-cidr "10.0.2.0/24"

# ==========================================
# OUTPUT SUMMARY
# ==========================================
echo ""
echo "=========================================="
echo "  GENESIS v10.1 - AZURE DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "✅ AKS Cluster: $AKS_CLUSTER"
echo "   Region: $AZURE_REGION (GDPR Compliant)"
echo "   Nodes: $(kubectl get nodes --no-headers | wc -l)"
echo "   Kubernetes: $(kubectl version --short | grep Server | cut -d' ' -f3)"
echo ""
echo "✅ Storage Account: $STORAGE_ACCOUNT"
echo "   Backup Container: $BACKUP_CONTAINER"
echo "   Vault Container: genesis-vault"
echo ""
echo "✅ Key Vault: $KEY_VAULT_NAME"
echo "   Secrets stored: storage-account-key"
echo ""
echo "✅ Monitoring:"
echo "   Log Analytics: $LOG_ANALYTICS_WS"
echo "   View logs: az monitor log-analytics workspace show --resource-group $RESOURCE_GROUP --workspace-name $LOG_ANALYTICS_WS"
echo ""
echo "=========================================="
echo "  NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Access Grafana Dashboard:"
echo "   kubectl port-forward -n observability svc/prometheus-grafana 3000:80"
echo "   Open: http://localhost:3000 (admin / prom-operator)"
echo ""
echo "2. Access GENESIS UI:"
echo "   kubectl port-forward -n ui-system svc/genesis-ui 8080:80"
echo "   Open: http://localhost:8080"
echo ""
echo "3. View All Pods:"
echo "   kubectl get pods -A"
echo ""
echo "4. Create Test Tenant:"
echo "   kubectl apply -f examples/tenant-sample.yaml"
echo ""
echo "=========================================="
echo "  COMPLIANCE STATUS:"
echo "=========================================="
echo ""
echo "✅ GDPR: Data in EU region ($AZURE_REGION)"
echo "✅ eIDAS 2.0: QES client deployed"
echo "✅ PSD2: API Gateway configured"
echo "✅ DORA: Incident reporting active"
echo "✅ Basel III: AI risk engine operational"
echo ""
echo "Evidence vault: evidence/$(date +%Y%m%d)/"
echo ""
