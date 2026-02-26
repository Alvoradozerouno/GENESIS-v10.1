# GENESIS Evidence Vault

## Overview

Complete audit evidence collection, package signing, and provenance chain for compliance verification.

## Features

- **Automated Evidence Collection**: Kubernetes resources, events, network policies, CRDs
- **SBOM Generation**: Software Bill of Materials via Syft
- **Vulnerability Scanning**: Security analysis via Trivy
- **Package Signing**: Cosign signature with SHA-256 hashing
- **Master Manifest**: Complete system state with compliance attestation

## Evidence Structure

Each evidence collection creates a timestamped directory:

```
evidence/YYYYMMDD-HHMMSS/
├── resources.json       # All Kubernetes resources across namespaces
├── events.json          # Cluster events
├── netpol.yaml          # Network policies
├── crd.yaml             # Custom Resource Definitions
├── sbom.json            # Software Bill of Materials (Syft)
├── trivy.json           # Vulnerability scan results
├── audit-package.tar.gz # Compressed evidence package
├── hash.txt             # SHA-256 hash of package
├── sig.txt              # Cosign signature
└── manifest.json        # Master manifest with compliance attestation
```

## Master Manifest

The `manifest.json` contains:

- System version and timestamp
- Authors attribution
- Security configuration (FIPS, HSM, Zero-Trust)
- Compliance frameworks (eIDAS 2.0, GDPR, PSD2, Basel III, XBRL, AI Act)
- Risk score from ML engine
- OIDC and Federation status
- Backup configuration
- Evidence package hash (SHA-256)
- Supervisor-readiness attestation

## Manual Evidence Collection

Evidence is automatically collected during deployment. For manual collection:

```bash
# Set evidence directory
EVIDENCE_DIR="evidence/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$EVIDENCE_DIR"

# Collect resources
kubectl get all -A -o json > "$EVIDENCE_DIR/resources.json"
kubectl get events -A -o json > "$EVIDENCE_DIR/events.json"
kubectl get netpol -A -o yaml > "$EVIDENCE_DIR/netpol.yaml"
kubectl get crd -o yaml > "$EVIDENCE_DIR/crd.yaml"

# Generate SBOM (requires Syft)
syft packages dir:. -o json > "$EVIDENCE_DIR/sbom.json"

# Scan vulnerabilities (requires Trivy)
trivy fs . --format json -o "$EVIDENCE_DIR/trivy.json"

# Package and hash
cd "$EVIDENCE_DIR"
tar czf audit-package.tar.gz . --exclude=audit-package.tar.gz
sha256sum audit-package.tar.gz > hash.txt

# Sign (requires Cosign)
cosign sign-blob \
  --output-signature sig.txt \
  --yes \
  audit-package.tar.gz
```

## Verification

Verify evidence package integrity:

```bash
# Verify hash
sha256sum -c hash.txt

# Verify signature (requires public key)
cosign verify-blob \
  --signature sig.txt \
  --key <public-key-file> \
  audit-package.tar.gz
```

## Regulatory Compliance

The Evidence Vault supports:

- **eIDAS 2.0**: Qualified Electronic Signatures via Cosign
- **GDPR Article 32**: Security measures documentation
- **Basel III**: Risk management evidence
- **DORA**: Operational resilience testing records
- **AI Act**: AI system governance documentation
- **ISO 27001**: Audit trail requirements

## Retention Policy

- **Default**: Evidence packages retained indefinitely
- **Cloud Storage**: Sync to S3/MinIO for long-term archival
- **Compliance**: Follow regulatory retention requirements (typically 5-10 years)

## Authors

- ORION
- Gerhard Hirschmann
- Elisabeth Steurer

## License

Apache 2.0
