# GENESIS Backup System

## Overview

Automated backup and disaster recovery for GENESIS v10.1 using Velero.

## Features

- **Automated Backups**: Every 6 hours via CronJob
- **Restore Testing**: Weekly automated restore validation
- **Retention**: 30 days (720h TTL)
- **Scope**: All GENESIS namespaces (genesis-system, tenant-system, governance-system, federation-system)

## Backup Schedule

```yaml
Schedule: "0 */6 * * *"  # Every 6 hours
TTL: 720h                # 30 days
```

## Restore Test Schedule

```yaml
Schedule: "0 2 * * 0"    # Every Sunday at 2 AM
```

## Manual Backup

```bash
# Create manual backup
velero backup create genesis-manual-$(date +%Y%m%d) \
  --include-namespaces=genesis-system,tenant-system,governance-system,federation-system \
  --ttl 720h

# List backups
velero backup get

# Restore from backup
velero restore create --from-backup <backup-name>
```

## Configuration

Velero is deployed via `genesis_v10.1.sh` with AWS S3-compatible storage:

```bash
helm upgrade --install velero vmware-tanzu/velero \
  -n backup-system \
  --set configuration.provider=aws \
  --set configuration.backupStorageLocation.bucket=genesis-backups \
  --set snapshotsEnabled=false
```

**Note**: Requires cloud provider configuration (AWS, GCP, Azure, or MinIO).

## Monitoring

Check backup status:

```bash
kubectl get cronjob -n backup-system
kubectl get backup -n backup-system
kubectl logs -n backup-system -l app.kubernetes.io/name=velero
```

## Authors

- ORION
- Gerhard Hirschmann
- Elisabeth Steurer

## License

Apache 2.0
