#!/usr/bin/env bash
set -euo pipefail

SEVERITY="${1:-critical}"
SUMMARY="${2:-Genesis System Alert}"
SOURCE="${3:-genesis-operator}"

if [[ -n "${SLACK_WEBHOOK:-}" ]]; then
  curl -s -X POST "$SLACK_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "{
      \"blocks\": [{
        \"type\": \"section\",
        \"text\": {
          \"type\": \"mrkdwn\",
          \"text\": \"*GENESIS ALERT* [$SEVERITY]\\n$SUMMARY\\nSource: $SOURCE\\nTime: $(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }
      }]
    }"
  echo "Slack alert sent"
fi

if [[ -n "${PAGERDUTY_KEY:-}" ]]; then
  curl -s -X POST https://events.pagerduty.com/v2/enqueue \
    -H "Content-Type: application/json" \
    -d "{
      \"routing_key\": \"$PAGERDUTY_KEY\",
      \"event_action\": \"trigger\",
      \"payload\": {
        \"summary\": \"$SUMMARY\",
        \"severity\": \"$SEVERITY\",
        \"source\": \"$SOURCE\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
        \"component\": \"genesis-v10.1\",
        \"group\": \"infrastructure\"
      }
    }"
  echo "PagerDuty alert sent"
fi
