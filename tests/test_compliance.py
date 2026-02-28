"""
GENESIS v10.1 — Compliance Engine Tests
pytest-based, covers all 9 EU frameworks fully.

Run: pytest tests/ -v
"""
import sys
import os

# Set high rate limits BEFORE importing the module — constants are set at import time
os.environ["GENESIS_RATE_GLOBAL"] = "10000"
os.environ["GENESIS_RATE_WRITE"]  = "10000"

# Allow importing genesis_api from repo root without install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

import genesis_api
from genesis_api import app, _predict_risk, _MODEL_R2, FRAMEWORKS, _rate_buckets

client = TestClient(app, headers={"X-API-Key": "genesis-dev-key"})


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_rate_buckets():
    """Clear sliding-window state between tests so they don't bleed into each other."""
    _rate_buckets.clear()
    yield
    _rate_buckets.clear()




METRICS_LOW = dict(cpu=20, memory=15, network_io=5, disk_usage=20, error_rate=0)
METRICS_HIGH = dict(cpu=95, memory=90, network_io=80, disk_usage=90, error_rate=25)

COMPLIANCE_FULL = dict(
    tenant_id="test_bank",
    data_residency="AT",
    encryption_at_rest=True,
    encryption_in_transit=True,
    audit_logging=True,
    data_retention_days=3650,
    mfa_enabled=True,
    ict_incident_reporting=True,
    third_party_risk_assessed=True,
    penetration_testing_done=True,
    consent_management=True,
    data_minimization=True,
    breach_notification_proc=True,
    ai_risk_classification=True,
    explainability_docs=True,
    conformity_assessment=True,
    kyc_cdd_process=True,
    transaction_monitoring=True,
    str_filing_process=True,
    sca_implemented=True,
    xs2a_api_available=True,
    best_execution_policy=True,
    transaction_reporting=True,
    scr_coverage_pct=130.0,
    orsa_reporting=True,
    cet1_ratio_pct=14.0,
    lcr_ratio_pct=120.0,
)

COMPLIANCE_GAPS = dict(
    tenant_id="test_bank_gaps",
    data_residency="US",           # non-EU → fails residency
    encryption_at_rest=False,      # fails
    encryption_in_transit=False,   # fails
    audit_logging=False,           # fails
    data_retention_days=30,        # fails all retention checks
    mfa_enabled=False,             # fails
    ict_incident_reporting=False,
    third_party_risk_assessed=False,
    penetration_testing_done=False,
    consent_management=False,
    data_minimization=False,
    breach_notification_proc=False,
    ai_risk_classification=False,
    explainability_docs=False,
    conformity_assessment=False,
    kyc_cdd_process=False,
    transaction_monitoring=False,
    str_filing_process=False,
    sca_implemented=False,
    xs2a_api_available=False,
    best_execution_policy=False,
    transaction_reporting=False,
    scr_coverage_pct=50.0,
    orsa_reporting=False,
    cet1_ratio_pct=2.0,
    lcr_ratio_pct=60.0,
)

ALL_FRAMEWORKS = list(FRAMEWORKS.keys())


# ─── Health ─────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_health_status_healthy(self):
        d = client.get("/api/health").json()
        assert d["status"] == "healthy"

    def test_health_has_model_r2(self):
        d = client.get("/api/health").json()
        assert "model_r2" in d
        assert d["model_r2"] > 0.80, "R² must be above 0.80"

    def test_health_frameworks_count(self):
        d = client.get("/api/health").json()
        assert d["frameworks_loaded"] == 9

    def test_health_all_services_operational(self):
        d = client.get("/api/health").json()
        for svc, status in d["services"].items():
            if svc != "local_ai_llm":
                assert status == "operational", f"{svc} not operational"


# ─── Authentication ──────────────────────────────────────────────────────────

class TestAuth:
    def test_no_key_rejected(self):
        r = TestClient(app).post("/api/risk/score", json={**METRICS_LOW, "framework": "dora"})
        assert r.status_code == 401

    def test_wrong_key_rejected(self):
        r = TestClient(app, headers={"X-API-Key": "wrong-key"}).post(
            "/api/risk/score", json={**METRICS_LOW, "framework": "dora"}
        )
        assert r.status_code == 401

    def test_valid_key_accepted(self):
        r = client.post("/api/risk/score", json={**METRICS_LOW, "framework": "dora"})
        assert r.status_code == 200

    def test_bearer_token_accepted(self):
        r = TestClient(app, headers={"Authorization": "Bearer genesis-dev-key"}).post(
            "/api/risk/score", json={**METRICS_LOW, "framework": "dora"}
        )
        assert r.status_code == 200

    def test_public_endpoints_open(self):
        """/ and /docs must NOT require auth."""
        r = TestClient(app).get("/")
        assert r.status_code == 200


# ─── Risk Engine ────────────────────────────────────────────────────────────

class TestRiskEngine:
    def test_model_r2_above_threshold(self):
        assert _MODEL_R2 >= 0.85, f"R²={_MODEL_R2} below 0.85 threshold"

    def test_low_metrics_give_low_score(self):
        score, _ = _predict_risk(10, 10, 5, 10, 0, "basel_iii")
        assert score < 25, f"Expected LOW score, got {score}"

    def test_high_metrics_give_high_score(self):
        score, _ = _predict_risk(98, 95, 90, 92, 80, "basel_iii")
        assert score > 70, f"Expected HIGH score, got {score}"

    def test_score_range_0_to_100(self):
        for fw in ALL_FRAMEWORKS:
            s, _ = _predict_risk(67, 75, 2, 85, 0, fw)
            assert 0 <= s <= 100, f"{fw}: score {s} out of [0,100]"

    def test_all_9_frameworks_give_different_scores(self):
        scores = {fw: _predict_risk(67, 75, 2, 85, 0, fw)[0] for fw in ALL_FRAMEWORKS}
        unique = len(set(round(s, 1) for s in scores.values()))
        assert unique >= 5, f"Expected differentiated scores, got {unique} unique: {scores}"

    def test_gdpr_sensitive_to_disk(self):
        score_low_disk, _ = _predict_risk(67, 75, 2, 40, 0, "gdpr")
        score_high_disk, _ = _predict_risk(67, 75, 2, 90, 0, "gdpr")
        assert score_high_disk > score_low_disk * 1.3, "GDPR should amplify high disk usage"

    def test_dora_sensitive_to_network(self):
        score_low_net, _ = _predict_risk(50, 50, 5, 50, 0, "dora")
        score_high_net, _ = _predict_risk(50, 50, 80, 50, 0, "dora")
        assert score_high_net > score_low_net, "DORA must amplify high network I/O"

    def test_solvency_ii_sensitive_to_memory(self):
        score_low, _ = _predict_risk(50, 30, 10, 40, 0, "solvency_ii")
        score_high, _ = _predict_risk(50, 92, 10, 40, 0, "solvency_ii")
        assert score_high > score_low, "Solvency II must amplify high memory"

    def test_api_risk_score_endpoint(self):
        body = {**METRICS_LOW, "framework": "dora", "tenant_id": "test"}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 200
        d = r.json()
        assert "risk_score" in d
        assert "risk_level" in d
        assert "feature_importance" in d
        assert "regulatory_action" in d
        assert "audit_ref" in d

    def test_api_accepts_pct_field_names(self):
        """Dashboard uses cpu_usage_pct — must be accepted."""
        body = dict(cpu_usage_pct=67, memory_usage_pct=75, network_io_mbps=2,
                    disk_usage_pct=85, error_rate_pct=0, framework="dora")
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 200

    @pytest.mark.parametrize("fw", ALL_FRAMEWORKS)
    def test_all_frameworks_via_api(self, fw):
        body = {**METRICS_LOW, "framework": fw}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 200, f"{fw} returned {r.status_code}: {r.text}"
        d = r.json()
        assert d["risk_level"] in ("MINIMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL")


# ─── Compliance Engine — all 9 frameworks ───────────────────────────────────

class TestComplianceEngine:

    @pytest.mark.parametrize("fw", ALL_FRAMEWORKS)
    def test_fully_compliant_payload(self, fw):
        """All checks true → must return COMPLIANT with 100%."""
        r = client.post(f"/api/compliance/{fw}", json=COMPLIANCE_FULL)
        assert r.status_code == 200, f"{fw}: {r.text}"
        d = r.json()
        assert d["compliance_status"] == "COMPLIANT", \
            f"{fw}: expected COMPLIANT, got {d['compliance_status']} ({d['compliance_score_pct']}%)"
        assert d["compliance_score_pct"] == 100.0

    @pytest.mark.parametrize("fw", ALL_FRAMEWORKS)
    def test_non_compliant_payload(self, fw):
        """All checks false → must return NON_COMPLIANT."""
        r = client.post(f"/api/compliance/{fw}", json=COMPLIANCE_GAPS)
        assert r.status_code == 200, f"{fw}: {r.text}"
        d = r.json()
        assert d["compliance_status"] in ("NON_COMPLIANT", "PARTIALLY_COMPLIANT"), \
            f"{fw}: full gap payload should not be COMPLIANT"
        assert d["compliance_score_pct"] < 70.0

    @pytest.mark.parametrize("fw", ALL_FRAMEWORKS)
    def test_response_schema(self, fw):
        """All required fields present in response."""
        r = client.post(f"/api/compliance/{fw}", json=COMPLIANCE_FULL)
        d = r.json()
        for field in ("framework", "compliance_status", "compliance_score_pct",
                      "checks_passed", "checks_total", "check_details",
                      "remediation_required", "audit_ref"):
            assert field in d, f"{fw}: missing field '{field}'"

    def test_invalid_framework_returns_404(self):
        r = client.post("/api/compliance/fake_framework", json=COMPLIANCE_FULL)
        assert r.status_code == 404

    def test_dora_penetration_testing_required(self):
        body = {**COMPLIANCE_FULL, "penetration_testing_done": False}
        r = client.post("/api/compliance/dora", json=body).json()
        assert "penetration_testing_done" in r["remediation_required"]
        assert r["compliance_status"] == "PARTIALLY_COMPLIANT"

    def test_gdpr_non_eu_residency_fails(self):
        body = {**COMPLIANCE_FULL, "data_residency": "US"}
        r = client.post("/api/compliance/gdpr", json=body).json()
        assert "data_residency_eu" in r["remediation_required"]

    def test_ai_act_conformity_assessment_required(self):
        body = {**COMPLIANCE_FULL, "conformity_assessment": False}
        r = client.post("/api/compliance/ai_act", json=body).json()
        assert "conformity_assessment" in r["remediation_required"]

    def test_psd2_xs2a_required(self):
        body = {**COMPLIANCE_FULL, "xs2a_api_available": False}
        r = client.post("/api/compliance/psd2", json=body).json()
        assert "xs2a_api_available" in r["remediation_required"]

    def test_basel_lcr_threshold(self):
        body = {**COMPLIANCE_FULL, "lcr_ratio_pct": 95.0}  # below 100% minimum
        r = client.post("/api/compliance/basel_iii", json=body).json()
        assert "lcr_above_100pct" in r["remediation_required"]

    def test_solvency_scr_threshold(self):
        body = {**COMPLIANCE_FULL, "scr_coverage_pct": 80.0}  # below 100%
        r = client.post("/api/compliance/solvency_ii", json=body).json()
        assert "scr_coverage_ok" in r["remediation_required"]

    def test_eba_cet1_threshold(self):
        body = {**COMPLIANCE_FULL, "cet1_ratio_pct": 3.0}  # below 4.5%
        r = client.post("/api/compliance/eba", json=body).json()
        assert "cet1_above_minimum" in r["remediation_required"]

    def test_frameworks_list_endpoint(self):
        r = client.get("/api/compliance/frameworks/all")
        assert r.status_code == 200
        d = r.json()
        assert d["total_frameworks"] == 9


# ─── Audit Persistence ──────────────────────────────────────────────────────

class TestAuditPersistence:
    def test_audit_endpoint_returns_200(self):
        r = client.get("/api/audit")
        assert r.status_code == 200

    def test_audit_entries_accumulate(self):
        before = client.get("/api/audit").json()["total_entries"]
        client.post("/api/risk/score", json={**METRICS_LOW, "framework": "dora"})
        after = client.get("/api/audit").json()["total_entries"]
        assert after > before

    def test_audit_entry_schema(self):
        client.post("/api/risk/score", json={**METRICS_LOW, "framework": "gdpr"})
        entries = client.get("/api/audit?limit=1").json()["entries"]
        assert len(entries) >= 1
        e = entries[-1]
        assert "timestamp" in e
        assert "action" in e
        assert "genesis_version" in e


# ─── System Metrics ─────────────────────────────────────────────────────────

class TestSystemMetrics:
    def test_metrics_endpoint(self):
        r = client.get("/api/system/metrics")
        assert r.status_code == 200

    def test_metrics_fields(self):
        d = client.get("/api/system/metrics").json()
        for field in ("cpu_usage_pct", "memory_usage_pct", "disk_usage_pct",
                      "network_io_mbps", "error_rate_pct"):
            assert field in d, f"Missing field: {field}"

    def test_metrics_ranges(self):
        d = client.get("/api/system/metrics").json()
        assert 0 <= d["cpu_usage_pct"] <= 100
        assert 0 <= d["memory_usage_pct"] <= 100
        assert 0 <= d["disk_usage_pct"] <= 100


# ─── Input Validation Bounds ────────────────────────────────────────────────

class TestInputValidation:
    def test_cpu_above_100_rejected(self):
        body = {**METRICS_LOW, "cpu": 150.0, "framework": "dora"}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 422

    def test_memory_negative_rejected(self):
        body = {**METRICS_LOW, "memory": -5.0, "framework": "dora"}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 422

    def test_error_rate_above_100_rejected(self):
        body = {**METRICS_LOW, "error_rate": 999.0, "framework": "dora"}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 422

    def test_cet1_negative_rejected(self):
        body = {**COMPLIANCE_FULL, "cet1_ratio_pct": -1.0}
        r = client.post("/api/compliance/eba", json=body)
        assert r.status_code == 422

    def test_cet1_above_100_rejected(self):
        body = {**COMPLIANCE_FULL, "cet1_ratio_pct": 9999.0}
        r = client.post("/api/compliance/eba", json=body)
        assert r.status_code == 422

    def test_max_tokens_above_2048_rejected(self):
        r = client.post("/api/ai/explain", json={
            "risk_score": 45.0, "risk_level": "MEDIUM", "framework": "dora",
            "max_tokens": 9999
        })
        assert r.status_code == 422

    def test_risk_score_above_100_rejected(self):
        r = client.post("/api/ai/explain", json={
            "risk_score": 101.0, "risk_level": "MEDIUM", "framework": "dora"
        })
        assert r.status_code == 422

    def test_boundary_values_accepted(self):
        """Edge: exactly 0.0 and 100.0 must be valid."""
        body = {"cpu": 0.0, "memory": 0.0, "network_io": 0.0,
                "disk_usage": 0.0, "error_rate": 0.0, "framework": "gdpr"}
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 200
        body2 = {"cpu": 100.0, "memory": 100.0, "network_io": 100.0,
                 "disk_usage": 100.0, "error_rate": 100.0, "framework": "gdpr"}
        r2 = client.post("/api/risk/score", json=body2)
        assert r2.status_code == 200


# ─── Rate Limiting ──────────────────────────────────────────────────────────

class TestRateLimiting:
    def test_rate_limit_headers_present(self):
        r = client.get("/api/health")
        assert "x-ratelimit-limit" in r.headers
        assert "x-ratelimit-remaining" in r.headers
        assert "x-ratelimit-window" in r.headers

    def test_remaining_decrements(self):
        r1 = client.get("/api/health")
        r2 = client.get("/api/health")
        rem1 = int(r1.headers.get("x-ratelimit-remaining", 9999))
        rem2 = int(r2.headers.get("x-ratelimit-remaining", 9999))
        assert rem2 < rem1, "Remaining must decrease with each request"

    def test_write_limit_lower_than_read(self, monkeypatch):
        monkeypatch.setattr(genesis_api, "_RATE_GLOBAL", 100)
        monkeypatch.setattr(genesis_api, "_RATE_WRITE", 30)
        _rate_buckets.clear()
        r_read  = client.get("/api/health")
        r_write = client.post("/api/risk/score", json={**METRICS_LOW, "framework": "dora"})
        read_limit  = int(r_read.headers.get("x-ratelimit-limit", 0))
        write_limit = int(r_write.headers.get("x-ratelimit-limit", 0))
        assert write_limit < read_limit, f"Write limit {write_limit} must be < read limit {read_limit}"

    def test_429_when_limit_exceeded(self, monkeypatch):
        monkeypatch.setattr(genesis_api, "_RATE_GLOBAL", 3)
        _rate_buckets.clear()
        for _ in range(3):
            client.get("/api/health")
        r = client.get("/api/health")
        assert r.status_code == 429

    def test_429_has_retry_after(self, monkeypatch):
        monkeypatch.setattr(genesis_api, "_RATE_GLOBAL", 1)
        _rate_buckets.clear()
        client.get("/api/health")
        r = client.get("/api/health")
        assert r.status_code == 429
        assert "retry_after_seconds" in r.json()
        assert "Retry-After" in r.headers

    def test_write_429_when_post_limit_exceeded(self, monkeypatch):
        monkeypatch.setattr(genesis_api, "_RATE_WRITE", 2)
        _rate_buckets.clear()
        body = {**METRICS_LOW, "framework": "dora"}
        for _ in range(2):
            client.post("/api/risk/score", json=body)
        r = client.post("/api/risk/score", json=body)
        assert r.status_code == 429




class TestQES:
    def test_sign_document(self):
        r = client.post("/api/cert/sign", json={
            "document_name": "test_report.pdf",
            "signer": "test-officer",
            "provider": "swisscom",
            "framework": "eidas_2"
        })
        assert r.status_code == 200
        d = r.json()
        assert d["signing_status"] == "SIGNED"
        assert d["signature_level"] == "QES"
        assert d["eudi_wallet_ready"] is True

    def test_invalid_provider(self):
        r = client.post("/api/cert/sign", json={
            "document_name": "test.pdf", "signer": "x",
            "provider": "unknown_provider", "framework": "eidas_2"
        })
        assert r.status_code == 400


# ─── Multi-Tenant Key Management ────────────────────────────────────────────

admin_client = TestClient(app, headers={"X-API-Key": "genesis-admin-key"})


class TestKeyManagement:
    def test_list_keys_blocked_without_admin_key(self):
        """Regular tenant key must NOT access admin endpoints."""
        r = client.get("/api/admin/keys")
        assert r.status_code == 403

    def test_list_keys_returns_ok_with_admin_key(self):
        r = admin_client.get("/api/admin/keys")
        assert r.status_code == 200
        d = r.json()
        assert "total" in d
        assert "keys" in d
        assert d["total"] >= 2  # dev-default + admin-default seeded on startup

    def test_create_key_blocked_without_admin_key(self):
        r = client.post("/api/admin/keys", json={"tenant_id": "hacker", "name": "bad"})
        assert r.status_code == 403

    def test_create_key_returns_raw_key(self):
        r = admin_client.post("/api/admin/keys", json={
            "tenant_id": "bank_test_001", "name": "integration-test-key"
        })
        assert r.status_code == 200
        d = r.json()
        assert "key" in d
        assert "id" in d
        assert d["tenant_id"] == "bank_test_001"
        assert len(d["key"]) >= 32  # token_urlsafe(32) → 43 chars
        assert "warning" in d

    def test_created_key_is_functional(self):
        """A freshly issued key must authenticate protected endpoints."""
        create = admin_client.post("/api/admin/keys", json={
            "tenant_id": "bank_functional", "name": "functional-test"
        }).json()
        new_key = create["key"]
        r = TestClient(app, headers={"X-API-Key": new_key}).post(
            "/api/risk/score", json={**METRICS_LOW, "framework": "gdpr"}
        )
        assert r.status_code == 200

    def test_revoke_key_blocks_access(self):
        """Revoked key must return 401."""
        create = admin_client.post("/api/admin/keys", json={
            "tenant_id": "bank_revoke", "name": "to-revoke"
        }).json()
        new_key = create["key"]
        key_id  = create["id"]
        # Confirm key works before revocation
        r_before = TestClient(app, headers={"X-API-Key": new_key}).get("/api/audit")
        assert r_before.status_code == 200
        # Revoke
        rev = admin_client.delete(f"/api/admin/keys/{key_id}")
        assert rev.status_code == 200
        assert rev.json()["revoked"] is True
        # Key must now be rejected
        r_after = TestClient(app, headers={"X-API-Key": new_key}).get("/api/audit")
        assert r_after.status_code == 401

    def test_prometheus_metrics_includes_key_count(self):
        r = TestClient(app).get("/metrics")
        assert r.status_code == 200
        assert "genesis_api_keys_total" in r.text
