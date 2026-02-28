#!/usr/bin/env python3
"""
GENESIS v10.1 — Reddit post automation
Usage:
    pip install praw
    env REDDIT_CLIENT_ID=... REDDIT_CLIENT_SECRET=... REDDIT_USERNAME=... REDDIT_PASSWORD=... python scripts/post_reddit.py

Required env vars:
    REDDIT_CLIENT_ID      — from https://www.reddit.com/prefs/apps  (script type)
    REDDIT_CLIENT_SECRET  — client secret of the same app
    REDDIT_USERNAME       — your Reddit username (no u/ prefix)
    REDDIT_PASSWORD       — account password
    REDDIT_USER_AGENT     — optional; defaults to "GENESIS-v10.1 post bot/1.0"
"""
import os
import sys
import time

try:
    import praw  # pip install praw
except ImportError:
    print("ERROR: praw not installed — run: pip install praw")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration — read from environment variables
# ---------------------------------------------------------------------------
CLIENT_ID     = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
USERNAME      = os.environ.get("REDDIT_USERNAME", "")
PASSWORD      = os.environ.get("REDDIT_PASSWORD", "")
USER_AGENT    = os.environ.get("REDDIT_USER_AGENT", "GENESIS-v10.1 post bot/1.0")

# ---------------------------------------------------------------------------
# Post content
# ---------------------------------------------------------------------------
TITLE = (
    "GENESIS v10.1 — Open-source EU Banking Compliance OS: "
    "multi-tenant API keys, 94 tests, Prometheus metrics"
)

BODY = """\
## GENESIS v10.1 — Sovereign AI OS for EU Banking Compliance

Hey,

I just pushed a new release of **GENESIS**, a fully open-source regtech
platform targeting EU banking & financial regulations. Here's what landed
in this release:

---

### What's new

| Feature | Details |
|---|---|
| **Multi-tenant API keys** | SQLite-backed, SHA-256-hashed; `/api/admin/keys` CRUD endpoints |
| **Role-based auth** | `X-API-Key` (tenant) + `GENESIS_ADMIN_KEY` (admin); Bearer fallback |
| **94 pytest tests** | Up from 87 — covers key creation, revocation, 401/403 flows |
| **Prometheus /metrics** | 7 metrics: `genesis_up`, `genesis_model_r2`, `genesis_frameworks_total`, `genesis_audit_entries_total`, `genesis_api_keys_total`, `genesis_rate_window_entries`, `genesis_rate_limit_global/write` |
| **Grafana dashboard** | 8-panel JSON in `grafana/genesis-dashboard.json` — import straight in |
| **Rate limiting** | Sliding-window per-IP (100 read / 20 write per min) |
| **Docker + nginx** | TLS 1.2+1.3, docker-compose one-liner |
| **Risk engine** | EU AI Act × CRR III × DORA × PSD2 (9 frameworks); R² = 0.8955 |
| **llama.cpp** | Local Qwen2.5-0.5B-Instruct inference, zero cloud dependency |

---

### Try it in 60 seconds

```bash
git clone https://github.com/Alvoradozerouno/GENESIS-v10.1
cd GENESIS-v10.1
docker-compose up -d

# Check health
curl http://localhost:8080/health

# Score a transaction
curl -X POST http://localhost:8080/api/risk/score \\
  -H "X-API-Key: genesis-dev-key" \\
  -H "Content-Type: application/json" \\
  -d '{"transaction_type":"SEPA","amount":50000,"counterparty_country":"DE"}'

# Create a new tenant API key (requires admin key)
curl -X POST http://localhost:8080/api/admin/keys \\
  -H "X-API-Key: genesis-admin-key" \\
  -H "Content-Type: application/json" \\
  -d '{"tenant_id":"acme","name":"acme-prod"}'

# Metrics
curl http://localhost:8080/metrics
```

---

### Links

- **GitHub**: https://github.com/Alvoradozerouno/GENESIS-v10.1
- **HuggingFace (risk model)**: https://huggingface.co/Alvoradozerouno/genesis-risk-ml
- **HuggingFace (quantum fraud)**: https://huggingface.co/Alvoradozerouno/genesis-quantum-fraud

Feedback, issues, and PRs welcome!
"""

# Subreddits to post to
SUBREDDITS = [
    {
        "name": "opensource",
        "flair": None,          # set to flair text if subreddit requires one
    },
    {
        "name": "selfhosted",
        "flair": None,
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_env() -> bool:
    missing = [v for v in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
                           "REDDIT_USERNAME", "REDDIT_PASSWORD")
               if not os.environ.get(v, "").strip()]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}")
        print("Set them before running:")
        for m in missing:
            print(f"  $env:{m} = 'YOUR_VALUE'   # PowerShell")
        return False
    return True


def _make_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD,
        user_agent=USER_AGENT,
    )


def post_to_subreddit(reddit: praw.Reddit, sub_cfg: dict) -> str | None:
    sub_name = sub_cfg["name"]
    flair    = sub_cfg.get("flair")
    print(f"\n  → posting to r/{sub_name} ...", flush=True)
    try:
        subreddit = reddit.subreddit(sub_name)

        kwargs: dict = dict(
            title=TITLE,
            selftext=BODY,
        )
        if flair:
            # Look up flair ID
            for fl in subreddit.flair.link_templates:
                if fl.get("text", "").lower() == flair.lower():
                    kwargs["flair_id"] = fl["id"]
                    break

        submission = subreddit.submit(**kwargs)
        url = f"https://www.reddit.com{submission.permalink}"
        print(f"  ✓ posted: {url}")
        return url
    except praw.exceptions.RedditAPIException as exc:
        print(f"  ✗ Reddit API error on r/{sub_name}: {exc}")
        return None
    except Exception as exc:
        print(f"  ✗ Unexpected error on r/{sub_name}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("GENESIS v10.1 — Reddit Poster")
    print("=" * 60)

    if not _check_env():
        sys.exit(1)

    reddit = _make_reddit()

    try:
        me = reddit.user.me()
        print(f"Authenticated as: u/{me.name}")
    except Exception as exc:
        print(f"ERROR: Authentication failed — {exc}")
        sys.exit(1)

    print(f"\nPosting to {len(SUBREDDITS)} subreddit(s):")
    posted_urls: list[str] = []

    for i, sub_cfg in enumerate(SUBREDDITS):
        url = post_to_subreddit(reddit, sub_cfg)
        if url:
            posted_urls.append(url)
        if i < len(SUBREDDITS) - 1:
            # Reddit rate-limiter: wait between posts
            delay = 10
            print(f"  (waiting {delay}s before next post...)")
            time.sleep(delay)

    print("\n" + "=" * 60)
    print(f"Done — {len(posted_urls)}/{len(SUBREDDITS)} posted successfully.")
    for u in posted_urls:
        print(f"  {u}")


if __name__ == "__main__":
    main()
