#!/usr/bin/env bash
set -euo pipefail

REPORT="${1:-report.xbrl}"
LOG_FILE="validation_$(date +%Y%m%d_%H%M%S).log"

if ! command -v arelleCmdLine >/dev/null 2>&1; then
  echo "Arelle not found. Install: pip install arelle-release"
  exit 1
fi

echo "Validating XBRL report: $REPORT"

arelleCmdLine \
  --validate \
  --file "$REPORT" \
  --logFile "$LOG_FILE" \
  --plugins transforms/SEC \
  2>&1

ERRORS=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
WARNINGS=$(grep -c "WARNING" "$LOG_FILE" 2>/dev/null || echo "0")

echo ""
echo "Validation complete:"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo "  Log:      $LOG_FILE"

if [[ "$ERRORS" -gt 0 ]]; then
  echo "STATUS: FAILED"
  exit 1
else
  echo "STATUS: PASSED"
fi
