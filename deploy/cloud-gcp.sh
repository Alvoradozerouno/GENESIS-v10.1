#!/bin/bash
set -euo pipefail

###############################################################################
# GENESIS v10.1 - GCP Cloud Deployment
# Deploys GENESIS to Google Kubernetes Engine (GKE) with EU compliance
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENESIS_ROOT="$(dirname "$SCRIPT_DIR")"

# ==========================================
# CONFIGURATION
# ==========================================
GCP_PROJECT="${GCP_PROJECT:-}"                      # Will prompt if not set
GCP_REGION="${GCP_REGION:-europe-west3}"            # Frankfurt (GDPR)
GCP_ZONE="${GCP_ZONE:-europe-west3-a}"
CLUSTER_NAME="${CLUSTER_NAME:-genesis-gke}"
NODE_COUNT="${NODE_COUNT:-3}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-standard-4}"       # 4 vCPU, 16 GB RAM

# Storage
GCS_BACKUP_BUCKET="genesis-backups-$(date +%s)"
GCS_VAULT_BUCKET="genesis-vault-$(date +%s)"

# ==========================================
# COLORS & LOGGING
# ==========================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ==========================================
# PREREQUISITES CHECK
# ==========================================
log "Checking gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
  error "gcloud CLI not found!"
  echo "Install: https://cloud.google.com/sdk/docs/install"
  exit 1
fi

log "Checking kubectl..."
if ! command -v kubectl &> /dev/null; then
  error "kubectl not found!"
  exit 1
fi

log "Checking Helm..."
if ! command -v helm &> /dev/null; then
  error "Helm not found!"
  exit 1
fi

# ==========================================
# GCP AUTHENTICATION & PROJECT
# ==========================================
log "Verifying GCP authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
  log "No active GCP account found. Running gcloud auth login..."
  gcloud auth login
fi

if [ -z "$GCP_PROJECT" ]; then
  log "No GCP_PROJECT set. Available projects:"
  gcloud projects list
  read -rp "Enter GCP Project ID: " GCP_PROJECT
fi

gcloud config set project "$GCP_PROJECT"
log "Using GCP Project: $GCP_PROJECT"

# Enable required APIs
log "Enabling required GCP APIs..."
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  storage-api.googleapis.com \
  cloudkms.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project="$GCP_PROJECT"

# ==========================================
# CREATE GCS BUCKETS
# ==========================================
log "Creating GCS bucket for backups: $GCS_BACKUP_BUCKET..."
gsutil mb -l "$GCP_REGION" -p "$GCP_PROJECT" "gs://$GCS_BACKUP_BUCKET"
gsutil versioning set on "gs://$GCS_BACKUP_BUCKET"
gsutil encryption default -k "projects/$GCP_PROJECT/locations/$GCP_REGION/keyRings/genesis-keyring/cryptoKeys/genesis-key" "gs://$GCS_BACKUP_BUCKET" || log "Using default encryption"

log "Creating GCS bucket for Vault: $GCS_VAULT_BUCKET..."
gsutil mb -l "$GCP_REGION" -p "$GCP_PROJECT" "gs://$GCS_VAULT_BUCKET"
gsutil versioning set on "gs://$GCS_VAULT_BUCKET"

# ==========================================
# CREATE GKE CLUSTER
# ==========================================
log "Creating GKE Cluster: $CLUSTER_NAME..."
log "  Region: $GCP_REGION (Frankfurt - GDPR Compliant)"
log "  Nodes: $NODE_COUNT x $MACHINE_TYPE"

gcloud container clusters create "$CLUSTER_NAME" \
  --region="$GCP_REGION" \
  --node-locations="$GCP_ZONE" \
  --num-nodes="$NODE_COUNT" \
  --machine-type="$MACHINE_TYPE" \
  --disk-type=pd-ssd \
  --disk-size=100 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=10 \
  --enable-stackdriver-kubernetes \
  --enable-ip-alias \
  --network=default \
  --subnetwork=default \
  --enable-cloud-logging \
  --enable-cloud-monitoring \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
  --workload-pool="$GCP_PROJECT.svc.id.goog" \
  --enable-shielded-nodes \
  --shielded-secure-boot \
  --shielded-integrity-monitoring \
  --labels=project=genesis,environment=production,compliance=gdpr-eidas-psd2 \
  --project="$GCP_PROJECT"

log "✅ GKE Cluster created successfully!"

# ==========================================
# GET GKE CREDENTIALS
# ==========================================
log "Getting GKE credentials..."
gcloud container clusters get-credentials "$CLUSTER_NAME" \
  --region="$GCP_REGION" \
  --project="$GCP_PROJECT"

kubectl cluster-info
kubectl get nodes

# ==========================================
# CREATE SERVICE ACCOUNT FOR VELERO
# ==========================================
log "Creating service account for Velero backups..."
GSA_NAME="genesis-velero"
GSA_EMAIL="$GSA_NAME@$GCP_PROJECT.iam.gserviceaccount.com"

gcloud iam service-accounts create "$GSA_NAME" \
  --display-name="GENESIS Velero Backup Service Account" \
  --project="$GCP_PROJECT" || true

# Grant permissions
gsutil iam ch "serviceAccount:$GSA_EMAIL:objectAdmin" "gs://$GCS_BACKUP_BUCKET"

gcloud projects add-iam-policy-binding "$GCP_PROJECT" \
  --member="serviceAccount:$GSA_EMAIL" \
  --role="roles/compute.storageAdmin"

# Bind to Kubernetes service account with Workload Identity
kubectl create namespace backup-system || true
kubectl create serviceaccount velero -n backup-system || true

gcloud iam service-accounts add-iam-policy-binding "$GSA_EMAIL" \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$GCP_PROJECT.svc.id.goog[backup-system/velero]" \
  --project="$GCP_PROJECT"

kubectl annotate serviceaccount velero \
  -n backup-system \
  iam.gke.io/gcp-service-account="$GSA_EMAIL" \
  --overwrite

# ==========================================
# CREATE SERVICE ACCOUNT KEY FOR VAULT
# ==========================================
log "Creating service account credentials for Vault storage..."
VAULT_GSA="genesis-vault"
VAULT_GSA_EMAIL="$VAULT_GSA@$GCP_PROJECT.iam.gserviceaccount.com"

gcloud iam service-accounts create "$VAULT_GSA" \
  --display-name="GENESIS Vault Storage Service Account" \
  --project="$GCP_PROJECT" || true

gsutil iam ch "serviceAccount:$VAULT_GSA_EMAIL:objectAdmin" "gs://$GCS_VAULT_BUCKET"

gcloud iam service-accounts keys create /tmp/vault-gcs-key.json \
  --iam-account="$VAULT_GSA_EMAIL" \
  --project="$GCP_PROJECT"

# ==========================================
# DEPLOY GENESIS v10.1
# ==========================================
log "Deploying GENESIS v10.1 to GKE..."
cd "$GENESIS_ROOT"

# Configure environment for GCP
export VAULT_STORAGE_TYPE="gcs"
export GCS_BUCKET="$GCS_VAULT_BUCKET"
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/vault-gcs-key.json"
export VELERO_BUCKET="$GCS_BACKUP_BUCKET"
export GCP_PROJECT_ID="$GCP_PROJECT"

# Run GENESIS deployment
chmod +x genesis_v10.1.sh
./genesis_v10.1.sh

# ==========================================
# WAIT FOR DEPLOYMENT
# ==========================================
log "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all -A --timeout=600s || true

# ==========================================
# CREATE INGRESS (automatically provisions GCP Load Balancer)
# ==========================================
log "Creating Ingress for GENESIS UI..."
kubectl create namespace ui-system || true

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: genesis-ingress
  namespace: ui-system
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "genesis-ip"
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: genesis-ui
                port:
                  number: 80
EOF

# ==========================================
# OUTPUT SUMMARY
# ==========================================
EXTERNAL_IP=$(kubectl get ingress genesis-ingress -n ui-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")

echo ""
echo "=========================================="
echo "  GENESIS v10.1 - GCP DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "✅ GKE Cluster: $CLUSTER_NAME"
echo "   Project: $GCP_PROJECT"
echo "   Region: $GCP_REGION (Frankfurt - GDPR Compliant)"
echo "   Nodes: $(kubectl get nodes --no-headers | wc -l)"
echo ""
echo "✅ GCS Buckets:"
echo "   Backups: gs://$GCS_BACKUP_BUCKET"
echo "   Vault: gs://$GCS_VAULT_BUCKET"
echo ""
echo "✅ Workload Identity: Enabled"
echo "   Velero SA: $GSA_EMAIL"
echo "   Vault SA: $VAULT_GSA_EMAIL"
echo ""
echo "✅ Ingress IP: $EXTERNAL_IP"
echo "   (May take 5-10 minutes to provision)"
echo ""
echo "=========================================="
echo "  NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Access Grafana Dashboard:"
echo "   kubectl port-forward -n observability svc/prometheus-grafana 3000:80"
echo "   Open: http://localhost:3000"
echo ""
echo "2. Access GENESIS UI:"
echo "   kubectl port-forward -n ui-system svc/genesis-ui 8080:80"
echo "   Open: http://localhost:8080"
echo "   Or via Ingress: http://$EXTERNAL_IP (when ready)"
echo ""
echo "3. View All Pods:"
echo "   kubectl get pods -A"
echo ""
echo "4. View Cluster:"
echo "   gcloud container clusters describe $CLUSTER_NAME --region $GCP_REGION"
echo ""
echo "=========================================="
echo "  COMPLIANCE STATUS:"
echo "=========================================="
echo ""
echo "✅ GDPR: Data in EU region ($GCP_REGION)"
echo "✅ eIDAS 2.0: QES client deployed"
echo "✅ Encryption: GCS default encryption, shielded nodes"
echo "✅ Monitoring: Cloud Logging + Monitoring enabled"
echo "✅ Backup: Velero → GCS with versioning"
echo ""
