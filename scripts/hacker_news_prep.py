"""
GENESIS v10.1 — Hacker News "Show HN" submission preparer.

Run:  python scripts/hacker_news_prep.py
Then: copy-paste the output into https://news.ycombinator.com/submit

HN rules for Show HN:
  - Title must start with "Show HN:"
  - Be factual, no marketing adjectives
  - First comment = technical explanation (run immediately after posting)
  - Post at: Tuesday–Thursday, 9–11 AM Eastern US time for max visibility
"""

TITLE = "Show HN: Open-source EU compliance API – 9 frameworks (GDPR, DORA, eIDAS 2.0)"

URL = "https://github.com/Alvoradozerouno/GENESIS-v10.1"

FIRST_COMMENT = """\
GENESIS v10.1 is a FastAPI-based compliance engine I built for EU banking \
and RegTech. It covers 9 regulatory frameworks in a single deployment.

What it does:
- Risk scoring via Gradient Boosting (R²=0.8955), 5-dimensional input
- Compliance checks: Basel III/IV, MiFID II, GDPR, AI Act, AML6, DORA, PSD2, Solvency II, EBA
- Qualified Electronic Signatures (QES) — SHA-256 + HMAC-SHA256, eIDAS 2.0 PAdES-B-LT
- Multi-tenant API key management (SHA-256 hashed, SQLite-backed)
- Rate limiting (sliding window), Pydantic input validation, append-only audit trail
- Prometheus /metrics, structured JSON logging, nginx TLS
- Local LLM explanations via llama.cpp (Qwen2.5-0.5B-Instruct Q4_K_M)
- 94 tests, GitHub Actions CI (Python 3.12 + 3.13)
- Kubernetes operator (CRD: GenesisTenant) + docker-compose stack

Stack: Python 3.12, FastAPI, NumPy, scikit-learn, cryptography, SQLite, nginx, llama.cpp

Background: EU banks are locked into proprietary compliance platforms (SAP, \
Oracle) that cost €5M+ and take 18 months to deploy. I wanted to see how much \
of that could be done open-source in a deployable afternoon.

Honest caveats:
- The QES signing is cryptographically sound (HMAC-SHA256) but for legal-weight \
signatures you'd wire in a real QTSP (Swisscom, D-Trust, Entrust) via the \
QTSP_* env vars
- The risk ML engine is a Gradient Boosting model trained on synthetic regulatory \
calibration data — not a production-calibrated actuarial model
- The "15-minute deployment" assumes a working Kubernetes cluster

Happy to answer questions on the compliance logic, the ML engine, or the eIDAS \
architecture.

GitHub: https://github.com/Alvoradozerouno/GENESIS-v10.1
Docs/API reference: https://github.com/Alvoradozerouno/GENESIS-v10.1/blob/main/docs/api-reference.md
Architecture: https://github.com/Alvoradozerouno/GENESIS-v10.1/blob/main/docs/architecture.md
"""

TIMING_ADVICE = """
BEST POSTING TIMES (Eastern US):
  Tuesday  09:00–11:00 ET  ← recommended
  Wednesday 09:00–11:00 ET
  Thursday  09:00–11:00 ET

  Avoid: Friday PM, Saturday, Sunday morning
  Current EU time offset: ET = CET-6 (so 09:00 ET = 15:00 CET)

STEPS:
  1. Go to https://news.ycombinator.com/submit
  2. Paste TITLE (below)
  3. Paste URL (below)
  4. Submit
  5. Open your submission immediately
  6. Post FIRST COMMENT (below) as your first reply to your own post
     — this is the technical explanation; HN community expects it
  7. Respond to every comment within the first 2 hours
"""

def main():
    sep = "─" * 72
    print(sep)
    print("HACKER NEWS SUBMISSION — GENESIS v10.1")
    print(sep)
    print(TIMING_ADVICE)
    print(sep)
    print("TITLE (copy exactly — 80 chars max, no trailing space):")
    print()
    print(TITLE)
    print(f"  ({len(TITLE)} chars)")
    print()
    print(sep)
    print("URL:")
    print()
    print(URL)
    print()
    print(sep)
    print("FIRST COMMENT (post immediately after submission):")
    print()
    print(FIRST_COMMENT)
    print(sep)
    print(f"Title length check: {len(TITLE)} chars {'✅' if len(TITLE) <= 80 else '❌ TOO LONG'}")
    print(sep)


if __name__ == "__main__":
    main()
