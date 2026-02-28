"""
GENESIS v10.1 — Compliance Engine Tests
pytest-based, covers all 9 EU frameworks fully.

Run: pytest tests/ -v
"""
import sys
import os

# Allow importing genesis_api from repo root without install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from genesis_api import app, _predict_risk, _MODEL_R2, FRAMEWORKS

client = TestClient(app, headers={"X-API-Key": "genesis-dev-key"})

# ─── Shared payloads ────────────────────────────────────────────────────────

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


# ─── QES / eIDAS ─────────────────────────────────────────────────────────────

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
