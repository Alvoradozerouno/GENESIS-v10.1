#!/usr/bin/env python3
"""
GENESIS v10.1 – Discord Announcement Script

Posts a rich embed announcement to a Discord channel via Webhook.

Setup:
  1. Go to your Discord server → Channel Settings → Integrations → Webhooks
  2. Create a webhook and copy the URL
  3. Set env var: $env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
  4. Run: python scripts/setup_discord.py

Optional customisation:
  DISCORD_CHANNEL_NAME  – display name in the embed footer (default: #genesis-ai)
  GENESIS_API_URL       – public URL of your API (default: http://localhost:8080)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

WEBHOOK_URL  = os.environ.get("DISCORD_WEBHOOK_URL", "")
API_URL      = os.environ.get("GENESIS_API_URL", "http://localhost:8080")
CHANNEL_NAME = os.environ.get("DISCORD_CHANNEL_NAME", "#genesis-ai")

# ── Announcement payload ─────────────────────────────────────────────────────

def build_payload() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "username": "GENESIS v10.1",
        "avatar_url": "https://huggingface.co/front/assets/huggingface_logo.svg",
        "embeds": [
            {
                "title": "🏛️ GENESIS v10.1 — Sovereign AI OS for EU Banking Compliance",
                "description": (
                    "World's first **open-source Sovereign AI OS** for EU regulatory compliance.\n\n"
                    "**9 EU Regulatory Frameworks:**\n"
                    "Basel III/IV · MiFID II · GDPR · EU AI Act · AML6 · DORA · PSD2 · Solvency II · EBA\n\n"
                    "**Production Features:**\n"
                    "• Risk ML Engine · R²=0.8955 · Framework-aware scoring\n"
                    "• QES / eIDAS 2.0 · HMAC-SHA256 signing · EUDI Wallet ready\n"
                    "• Multi-tenant API keys · SQLite audit trail\n"
                    "• Prometheus metrics · Grafana dashboard\n"
                    "• Local LLM (Qwen2.5-0.5B) · 94 passing tests\n"
                    "• Browser Dashboard · Rate limiting · Docker-ready"
                ),
                "color": 0x58A6FF,  # GitHub blue
                "fields": [
                    {
                        "name": "📦 GitHub",
                        "value": "[Alvoradozerouno/GENESIS-v10.1](https://github.com/Alvoradozerouno/GENESIS-v10.1)",
                        "inline": True,
                    },
                    {
                        "name": "🤗 HuggingFace",
                        "value": "[Alvoradozerouno](https://huggingface.co/Alvoradozerouno)",
                        "inline": True,
                    },
                    {
                        "name": "🚀 API",
                        "value": f"[Live Dashboard]({API_URL}/ui)",
                        "inline": True,
                    },
                    {
                        "name": "📜 License",
                        "value": "Apache 2.0",
                        "inline": True,
                    },
                    {
                        "name": "🧪 Tests",
                        "value": "94 / 94 passing ✅",
                        "inline": True,
                    },
                    {
                        "name": "🏷️ Topics",
                        "value": "`eu-ai-act` `dora` `basel-iii` `regtech` `sovereign-ai`",
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": f"GENESIS v10.1 · {CHANNEL_NAME} · {ts[:10]}",
                },
                "thumbnail": {
                    "url": "https://raw.githubusercontent.com/Alvoradozerouno/GENESIS-v10.1/main/grafana/genesis-dashboard.json",
                },
            }
        ],
    }


# ── Sender ───────────────────────────────────────────────────────────────────

def post_to_discord(webhook_url: str, dry_run: bool = False) -> bool:
    payload = build_payload()
    if dry_run:
        print("── DRY RUN ────────────────────────────────────────────────────")
        print(json.dumps(payload, indent=2))
        print("───────────────────────────────────────────────────────────────")
        return True

    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            print(f"✅  Posted to Discord — HTTP {status}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"❌  Discord API error {e.code}: {body}", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"❌  Network error: {e.reason}", file=sys.stderr)
        return False


# ── Server setup guide ───────────────────────────────────────────────────────

SETUP_GUIDE = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GENESIS Discord Server Setup Guide
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CREATE SERVER
   → discord.com → + icon → Create My Own → For a club or community
   → Name: "GENESIS AI Compliance"

2. ADD CHANNELS
   #announcements  – project updates (read-only for members)
   #general        – community discussion
   #api-support    – technical help
   #risk-engine    – ML / scoring discussion
   #eu-regulations – GDPR · DORA · AI Act · Basel III

3. CREATE WEBHOOK
   → #announcements → ⚙️ Edit Channel → Integrations → Webhooks
   → New Webhook → Copy Webhook URL

4. CONFIGURE ENV VAR
   PowerShell:  $env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
   Linux/Mac:   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

5. POST ANNOUNCEMENT
   python scripts/setup_discord.py

6. INVITE LINK
   Server Settings → Invites → Create New (never expire)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    guide = "--guide" in sys.argv or "-g" in sys.argv

    if guide:
        print(SETUP_GUIDE)
        sys.exit(0)

    if not WEBHOOK_URL and not dry:
        print("⚠️  DISCORD_WEBHOOK_URL not set.\n")
        print("Options:")
        print("  1. Set it:   $env:DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/...'")
        print("  2. Dry run:  python scripts/setup_discord.py --dry-run")
        print("  3. Guide:    python scripts/setup_discord.py --guide")
        sys.exit(1)

    print(f"Posting GENESIS v10.1 announcement to Discord{' (DRY RUN)' if dry else ''}…")
    ok = post_to_discord(WEBHOOK_URL or "https://example.com", dry_run=dry)
    sys.exit(0 if ok else 1)
