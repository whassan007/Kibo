"""
KIBO Privacy OS — Section 15: Mandatory Acceptance Tests (Tests 1 through 15)
Uses synthetic organizations and legally reviewed expected outcomes to verify:
- US (Federal + 50 States + DC + territories)
- Canada (Federal + 10 Provinces + 3 Territories)
- European Union (EU-wide + 27 Member States)
- JRAE Multi-Jurisdictional Applicability Engine
- Privacy Office Modules A–J
- Corporate AI Integrations (Microsoft 365 Copilot, Claude Enterprise MCP, Gemini Enterprise)
- Strict Multi-Tenant Isolation & Offline-LLM Resilience
"""

import os
import sys
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_gateway import app, SessionLocal
from core.models.tenant import Tenant, TenantMembership


@pytest.fixture(scope="module")
def client():
    db = SessionLocal()
    try:
        for tid, tname in [
            ("default", "Default Enterprise Tenant"),
            ("tenant-ca", "Canadian Healthcare & Retail Enterprise"),
            ("tenant-us", "US Financial & Technology Corp"),
        ]:
            t = db.get(Tenant, tid)
            if not t:
                db.add(Tenant(id=tid, name=tname, is_active=True, subscription_tier="enterprise"))
        for tid, uid, role in [
            ("default", "user_expert", "admin"),
            ("tenant-ca", "ca_dpo", "dpo"),
            ("tenant-us", "us_cpo", "cpo"),
        ]:
            mem = db.query(TenantMembership).filter_by(tenant_id=tid, user_id=uid).first()
            if not mem:
                db.add(TenantMembership(tenant_id=tid, user_id=uid, role=role, is_active=True))
        db.commit()
    finally:
        db.close()
    return TestClient(app)


# ---------------------------------------------------------------------------
# Test 1: California Healthcare Organization
# ---------------------------------------------------------------------------
def test_01_california_healthcare_organization(client):
    """
    A hospital adopts an external AI diagnostic assistant.
    Verify applicability of HIPAA, California health/privacy rules, vendor requirements
    and relevant AI obligations without assuming every law applies automatically.
    """
    payload = {
        "organization": {
            "name": "Pacific Coast Medical Center",
            "industry": "healthcare",
            "organization_type": "healthcare_covered_entity",
            "hipaa_status": "covered_entity",
            "employee_count": 1200,
            "annual_revenue_usd": 450000000,
            "establishments": ["US-CA"],
        },
        "activity": {
            "purpose": "External AI radiology diagnostic assistant processing patient EHR",
            "data_categories": ["health_information", "phi", "personal_information"],
            "subject_locations": ["US-CA"],
            "processing_locations": ["US-CA"],
            "third_party_processors": True,
            "involves_ai_or_admt": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}
    exempt_ids = {i["regulation_id"] for i in data["exempt_or_preempted_instruments"]}

    # HIPAA Privacy/Security/Breach and California CMIA must apply
    assert any("HIPAA" in rid for rid in applicable_ids)
    assert "US-CA-CMIA" in applicable_ids
    # AI / ADMT rules evaluated in California
    assert any("ADMT" in rid or "AI" in rid for rid in applicable_ids | {i["regulation_id"] for i in data["future_preparation_obligations"]})
    # Unrelated federal sectoral laws (FERPA, GLBA, Federal Privacy Act of 1974) must NOT apply automatically
    assert "US-FED-FERPA" not in applicable_ids
    assert "US-FED-GLBA-PRIVACY" not in applicable_ids
    assert "US-FED-PRIVACY-ACT-1974" not in applicable_ids
    # CCPA PHI data-level carve-out must be documented
    all_outcomes = data["applicable_instruments"] + data["exempt_or_preempted_instruments"]
    ccpa_outcomes = [o for o in all_outcomes if "CCPA" in o["regulation_id"] or "CPRA" in o["regulation_id"]]
    assert len(ccpa_outcomes) >= 1
    assert any("HIPAA" in o["applicability_reasoning"] or o["exemptions_evaluated"] for o in ccpa_outcomes)


# ---------------------------------------------------------------------------
# Test 2: New York Financial Institution
# ---------------------------------------------------------------------------
def test_02_new_york_financial_institution(client):
    """
    A bank introduces a cloud analytics provider.
    Evaluate applicable federal financial privacy requirements, New York obligations,
    third-party risks and relevant supervisory requirements.
    """
    payload = {
        "organization": {
            "name": "Hudson Metro Bank",
            "industry": "financial_institution",
            "organization_type": "financial_institution",
            "employee_count": 650,
            "establishments": ["US-NY"],
        },
        "activity": {
            "purpose": "Cloud analytics provider for retail banking transaction risk",
            "data_categories": ["financial_data", "personal_information"],
            "subject_locations": ["US-NY"],
            "processing_locations": ["US-NY"],
            "third_party_processors": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    # Federal GLBA + New York NYDFS 23 NYCRR 500 + NY SHIELD Act must apply even though NY lacks a consumer CCPA clone
    assert any("GLBA" in rid for rid in applicable_ids)
    assert any("NYDFS" in rid for rid in applicable_ids)
    assert any("SHIELD" in rid or "US-NY-BREACH" in rid for rid in applicable_ids)
    # HIPAA must NOT apply
    assert not any("HIPAA" in rid for rid in applicable_ids)


# ---------------------------------------------------------------------------
# Test 3: Ontario Hospital
# ---------------------------------------------------------------------------
def test_03_ontario_hospital(client):
    """
    A hospital transfers patient information to a cloud processor.
    Evaluate Ontario PHIPA, applicable federal considerations and contractual and transfer obligations.
    """
    payload = {
        "organization": {
            "name": "Trillium Health Network Ontario",
            "industry": "healthcare",
            "organization_type": "health_information_custodian",
            "employee_count": 2100,
            "establishments": ["CA-ON"],
        },
        "activity": {
            "purpose": "Cloud EHR scheduling and clinical note processor",
            "data_categories": ["health_information", "phi"],
            "subject_locations": ["CA-ON"],
            "processing_locations": ["CA-ON"],
            "third_party_processors": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert "CA-ON-PHIPA" in applicable_ids
    assert "PHIPA_TRA" in data["required_assessments"]
    assert any("agent" in c.lower() or "service provider" in c.lower() for c in data["mandatory_controls"])


# ---------------------------------------------------------------------------
# Test 4: Quebec Enterprise
# ---------------------------------------------------------------------------
def test_04_quebec_enterprise(client):
    """
    A company transfers customer information internationally.
    Apply the relevant Quebec transfer assessment and privacy requirements.
    """
    payload = {
        "organization": {
            "name": "Saint-Laurent Commerce Inc.",
            "industry": "retail",
            "organization_type": "private",
            "employee_count": 180,
            "establishments": ["CA-QC"],
        },
        "activity": {
            "purpose": "International cloud CRM and customer analytics transfer to US",
            "data_categories": ["personal_information"],
            "subject_locations": ["CA-QC"],
            "processing_locations": ["CA-QC", "US-VA"],
            "transfer_destinations": ["US-VA"],
            "third_party_processors": True,
            "involves_cross_border_transfer": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert "CA-QC-LAW25" in applicable_ids
    assert "Law25_TIA" in data["required_assessments"] or "TIA" in data["required_assessments"]
    assert data["cross_border_transfer_analysis"]["quebec_tia_required"] is True


# ---------------------------------------------------------------------------
# Test 5: German Healthcare Organization
# ---------------------------------------------------------------------------
def test_05_german_healthcare_organization(client):
    """
    A hospital deploys AI-assisted scheduling.
    Apply GDPR, relevant German federal and state rules, health-data requirements
    and competent supervisory authority rules.
    """
    payload = {
        "organization": {
            "name": "Klinikum München Süd",
            "industry": "healthcare",
            "organization_type": "private",
            "employee_count": 950,
            "establishments": ["EU-DE"],
            "subnational_regions": ["DE-BY-PRIV"],
        },
        "activity": {
            "purpose": "AI-assisted patient triage and appointment scheduling",
            "data_categories": ["health_information", "personal_information"],
            "subject_locations": ["EU-DE"],
            "processing_locations": ["EU-DE"],
            "involves_ai_or_admt": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert "EU-GDPR" in applicable_ids
    assert any(rid.startswith("EU-DE") for rid in applicable_ids)
    assert "EU-AI-ACT" in applicable_ids or any("AI-ACT" in o["regulation_id"] for o in data["future_preparation_obligations"])
    # Verify Bavarian supervisory authority routing (BayLDA / BayLfD)
    authorities = [a["authority"] for a in data["responsible_authorities"]]
    assert any("BayLDA" in auth or "Bayern" in auth or "Bavaria" in auth or "BfDI" in auth for auth in authorities)


# ---------------------------------------------------------------------------
# Test 6: French Retail Enterprise
# ---------------------------------------------------------------------------
def test_06_french_retail_enterprise(client):
    """
    An organization deploys website analytics and targeted advertising.
    Evaluate GDPR, French electronic communications requirements, consent or other
    applicable requirements and relevant CNIL guidance.
    """
    payload = {
        "organization": {
            "name": "Maison Lumière Retail SA",
            "industry": "retail",
            "organization_type": "private",
            "employee_count": 320,
            "establishments": ["EU-FR"],
        },
        "activity": {
            "purpose": "Website behavioral analytics and targeted advertising trackers",
            "data_categories": ["personal_information", "online_identifiers"],
            "subject_locations": ["EU-FR"],
            "processing_locations": ["EU-FR"],
            "involves_targeted_advertising_or_cookies": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert "EU-GDPR" in applicable_ids
    assert any(rid.startswith("EU-FR") for rid in applicable_ids)
    assert "EU-EPRIVACY" in applicable_ids

    # Also verify Consent module directly enforces CNIL Art. 82 rules
    consent_resp = client.post(
        "/api/v1/office/consent/evaluate-regime",
        json={
            "jurisdiction": "EU-FR",
            "activity": "website_analytics_and_targeted_advertising",
            "data_categories": ["online_identifiers", "browsing_history"],
        },
    )
    assert consent_resp.status_code == 200
    c_data = consent_resp.json()
    assert "CNIL" in str(c_data)
    assert c_data.get("requires_prior_opt_in") is True
    assert c_data.get("requires_symmetric_refuse_all_button") is True


# ---------------------------------------------------------------------------
# Test 7: Irish SaaS Company
# ---------------------------------------------------------------------------
def test_07_irish_saas_company(client):
    """
    An Irish company processes data for customers in multiple EU member states.
    Evaluate processor/controller roles, GDPR obligations, data transfers and
    competent supervisory authority questions.
    """
    payload = {
        "organization": {
            "name": "Liffey Cloud Enterprise Ltd.",
            "industry": "technology",
            "organization_type": "private",
            "role": "processor",
            "employee_count": 410,
            "establishments": ["EU-IE"],
            "main_eu_establishment": "EU-IE",
        },
        "activity": {
            "purpose": "Multi-tenant B2B SaaS platform processing customer employee records across EU",
            "data_categories": ["personal_information"],
            "subject_locations": ["EU-IE", "EU-DE", "EU-FR", "EU-ES"],
            "processing_locations": ["EU-IE"],
            "transfer_destinations": ["US-VA"],
            "third_party_processors": True,
            "involves_cross_border_transfer": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert "EU-GDPR" in applicable_ids
    assert any(rid.startswith("EU-IE") for rid in applicable_ids)
    # Lead Supervisory Authority must identify Ireland DPC under Art. 56
    assert data["lead_supervisory_authority"] is not None
    assert data["lead_supervisory_authority"]["jurisdiction_id"] == "EU-IE"
    assert "Data Protection Commission" in data["lead_supervisory_authority"]["authority"]
    # Processor Art. 28 controls + Cross-border TIA
    assert any("Art. 28" in c for c in data["mandatory_controls"])
    assert "GDPR_TIA" in data["required_assessments"] or "TIA" in data["required_assessments"]


# ---------------------------------------------------------------------------
# Test 8: Multinational Privacy Breach
# ---------------------------------------------------------------------------
def test_08_multinational_privacy_breach(client):
    """
    An organization suffers a breach affecting California, Ontario, Quebec, France and Germany.
    The system must:
    - Create one incident.
    - Identify independently applicable regimes.
    - Evaluate jurisdiction-specific reporting thresholds.
    - Compute applicable deadlines.
    - Identify notification recipients.
    - Prevent duplicate or contradictory workflow actions.
    - Preserve a common evidence timeline.
    - Route legal notification decisions for approval.
    """
    breach_payload = {
        "title": "Multinational Cloud Storage Exfiltration Incident",
        "description": "Unauthorized access to multi-region customer & patient database cluster",
        "discovered_at": "2026-10-25T08:00:00Z",
        "affected_jurisdictions": ["US-CA", "CA-ON", "CA-QC", "EU-FR", "EU-DE"],
        "affected_counts_by_jurisdiction": {
            "US-CA": 1250,
            "CA-ON": 420,
            "CA-QC": 600,
            "EU-FR": 890,
            "EU-DE": 1100,
        },
        "data_categories": ["personal_information", "health_information", "financial_data"],
        "involves_phi": True,
        "risk_of_harm_level": "high",
        " german_land_code": "DE-BY-PRIV",
    }
    resp = client.post(
        "/api/v1/office/incidents",
        headers={"X-Tenant-ID": "default", "X-User-ID": "user_expert"},
        json=breach_payload,
    )
    assert resp.status_code == 200, resp.text
    inc = resp.json()

    # 1. Single incident ID
    assert inc.get("incident_id") is not None
    # 2. Independently applicable regimes across US-CA, CA-ON, CA-QC, EU-FR, EU-DE
    regimes = inc.get("applicable_regimes", [])
    jur_codes = {r["jurisdiction_id"] for r in regimes}
    assert {"US-CA", "CA-ON", "CA-QC", "EU-FR", "EU-DE"}.issubset(jur_codes)
    # 3. Deadlines computed (72h for GDPR FR/DE)
    fr_regime = next(r for r in regimes if r["jurisdiction_id"] == "EU-FR")
    assert fr_regime.get("regulator_deadline_hours") == 72
    # 4. Recipients identified (CNIL, CAI, IPC, CA AG, German DPA)
    recipients_blob = str(regimes)
    for expected_reg in ["CNIL", "CAI", "IPC", "Attorney General"]:
        assert expected_reg in recipients_blob
    # 5. Deduplicated workflow tasks & common evidence timeline
    assert len(inc.get("deduplicated_tasks", [])) >= 3
    assert len(inc.get("evidence_timeline", [])) >= 1
    # 6. Mandatory human legal approval before sending notifications (auto_send_blocked)
    drafts = inc.get("notification_drafts", [])
    assert len(drafts) >= 5
    assert all(d.get("auto_send_blocked") is True for d in drafts)
    assert all("pending" in d.get("status", "").lower() for d in drafts)


# ---------------------------------------------------------------------------
# Test 9: Cross-Border Data Rights Request
# ---------------------------------------------------------------------------
def test_09_cross_border_data_rights_request(client):
    """
    A person residing in Germany requests deletion of information from a US-headquartered
    company with operations in Canada.
    Determine which obligations apply based on the actual facts.
    Do not assume GDPR applicability solely from nationality or residence.
    """
    # Part A: Check via JRAE Applicability Engine
    eval_payload = {
        "organization": {
            "name": "NorthStar Logistics Corp",
            "industry": "logistics",
            "organization_type": "private",
            "employee_count": 300,
            "establishments": ["US-TX", "CA-ON"],
        },
        "activity": {
            "purpose": "North American B2B freight contact management",
            "data_categories": ["personal_information"],
            "subject_locations": ["EU-DE"],
            "processing_locations": ["US-TX", "CA-ON"],
            "targets_goods_or_services_to_subjects": False,
            "monitors_subject_behavior": False,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=eval_payload)
    assert resp.status_code == 200
    data = resp.json()
    applicable_ids = {i["regulation_id"] for i in data["applicable_instruments"]}
    exempt_ids = {i["regulation_id"] for i in data["exempt_or_preempted_instruments"]}

    # GDPR must NOT be in applicable_instruments when Art. 3(1) and Art. 3(2) are false
    assert "EU-GDPR" not in applicable_ids
    assert "EU-GDPR" in exempt_ids

    # Part B: Check via Rights Management Module D
    rights_resp = client.post(
        "/api/v1/office/rights/evaluate-request",
        json={
            "subject_residence": "EU-DE",
            "subject_nationality": "DE",
            "request_type": "deletion",
            "organization_establishments": ["US-TX", "CA-ON"],
            "processing_locations": ["US-TX", "CA-ON"],
            "targets_subject_jurisdiction": False,
            "monitors_subject_behavior": False,
            "data_categories": ["personal_information"],
        },
    )
    assert rights_resp.status_code == 200
    r_data = rights_resp.json()
    assert r_data["gdpr_applicable"] is False
    assert "Art. 3" in r_data["gdpr_territorial_reasoning"]


# ---------------------------------------------------------------------------
# Test 10: Regulatory Change
# ---------------------------------------------------------------------------
def test_10_regulatory_change(client):
    """
    A state privacy law is amended.
    The system must identify affected organizations, applicable processing activities,
    existing assessments, policies, controls and deadlines.
    """
    amendment_payload = {
        "regulation_id": "US-CA-CCPA-CPRA",
        "previous_version": "2026.1.0",
        "new_version": "2026.10.2",
        "amendment_summary": "CalPrivacy ADMT risk assessment & shortened 30-day consumer DSAR deadline amendment",
        "source_evidence": "https://cppa.ca.gov/regulations/admt_final_text.pdf",
        "legal_interpretation": "Requires pre-use ADMT notice, risk assessment for automated profiling, and updates DSAR SLA.",
        "effective_date": "2027-01-01",
        "affected_fields": ["response_deadlines", "required_assessments", "mandatory_controls"],
        "reviewer": "General Counsel",
        "approval_decision": "pending_legal_review",
    }
    resp = client.post(
        "/api/v1/office/regulatory-intelligence/amendments",
        headers={"X-Tenant-ID": "default", "X-User-ID": "user_expert"},
        json=amendment_payload,
    )
    assert resp.status_code == 200, resp.text
    impact = resp.json()

    assert impact["previous_version"] == "2026.1.0"
    assert impact["new_version"] == "2026.10.2"
    blast = impact.get("blast_radius", {})
    assert len(blast.get("affected_organizations_and_establishments", [])) >= 1
    assert len(blast.get("affected_processing_activities", [])) >= 1
    assert len(blast.get("assessments_requiring_reevaluation", [])) >= 1
    assert len(blast.get("affected_policies", [])) >= 1
    assert len(blast.get("affected_controls", [])) >= 1
    assert len(blast.get("updated_statutory_deadlines", [])) >= 1
    assert impact.get("production_obligations_updated") is False
    assert impact.get("llm_direct_alteration_blocked") is True


# ---------------------------------------------------------------------------
# Test 11: Jurisdiction & Tenant Isolation
# ---------------------------------------------------------------------------
def test_11_jurisdiction_and_tenant_isolation(client):
    """
    A Canadian tenant must not retrieve another tenant's US privacy records,
    even through MCP, AI retrieval or background processing.
    """
    # 1. Create an assessment record in US tenant ('tenant-us')
    create_us = client.post(
        "/api/v1/office/assessments",
        headers={"X-Tenant-ID": "tenant-us", "X-User-ID": "us_cpo"},
        json={
            "title": "US Confidential Wall Street GLBA Assessment",
            "assessment_type": "PIA",
            "jurisdictions": ["US-NY", "US-FED"],
            "data_categories": ["financial_data"],
            "processing_activities": ["cloud_analytics"],
        },
    )
    assert create_us.status_code == 200
    us_assessment_id = create_us.json()["assessment_id"]

    # 2. Canadian tenant ('tenant-ca') lists assessments -> must NOT see US record
    list_ca = client.get(
        "/api/v1/office/assessments",
        headers={"X-Tenant-ID": "tenant-ca", "X-User-ID": "ca_dpo"},
    )
    assert list_ca.status_code == 200
    ca_items = list_ca.json() if isinstance(list_ca.json(), list) else list_ca.json().get("assessments", [])
    ca_ids = [a["assessment_id"] for a in ca_items]
    assert us_assessment_id not in ca_ids

    # 3. Canadian tenant attempts direct GET on US assessment -> 404/403
    direct_ca = client.get(
        f"/api/v1/office/assessments/{us_assessment_id}",
        headers={"X-Tenant-ID": "tenant-ca", "X-User-ID": "ca_dpo"},
    )
    assert direct_ca.status_code in (403, 404)

    # 4. Canadian user attempts to spoof X-Tenant-ID: tenant-us -> 403 Forbidden from TenantIsolationMiddleware
    spoof_resp = client.get(
        "/api/v1/office/assessments",
        headers={"X-Tenant-ID": "tenant-us", "X-User-ID": "ca_dpo"},
    )
    assert spoof_resp.status_code == 403

    # 5. Canadian tenant attempts cross-tenant query via MCP integration endpoint -> 403 Forbidden
    mcp_cross_tenant = client.post(
        "/api/v1/integrations/mcp/invoke",
        headers={"X-Tenant-ID": "tenant-ca", "X-User-ID": "ca_dpo"},
        json={
            "tool_name": "lookup_privacy_tasks",
            "tenant_id": "tenant-ca",
            "user_id": "ca_dpo",
            "role": "DPO",
            "arguments": {"target_tenant_id": "tenant-us"},
        },
    )
    assert mcp_cross_tenant.status_code == 403


# ---------------------------------------------------------------------------
# Test 12: Corporate Copilot
# ---------------------------------------------------------------------------
def test_12_corporate_copilot(client):
    """
    An employee asks: "Can I send customer information to this third-party AI provider?"
    KIBO must identify the employee's organization, applicable legal obligations and
    company policies before responding.
    """
    resp = client.post(
        "/api/v1/integrations/copilot/query",
        headers={"X-Tenant-ID": "tenant-ca", "X-User-ID": "ca_dpo"},
        json={
            "hub": "m365_copilot",
            "question": "Can I send customer information to this third-party AI provider?",
            "organization_establishments": ["CA-ON", "CA-QC", "US-CA"],
            "industry": "healthcare",
            "vendor_name": "External GenAI Analytics Co.",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["organization_context"]["tenant_id"] == "tenant-ca"
    assert len(body["organization_context"]["active_jurisdictions"]) >= 2
    assert len(body["applicable_laws"]) >= 1
    assert len(body["company_policies"]) >= 1
    assert body["vendor_governance_check"] is not None
    assert len(body["required_assessments"]) >= 1
    assert len(body["mandatory_controls"]) >= 1
    assert len(body["citations"]) >= 1
    assert "DO_NOT_PROCEED" in body["decision_status"]
    assert "DPO" in body["guidance_summary"]


# ---------------------------------------------------------------------------
# Test 13: Law Not Yet Effective
# ---------------------------------------------------------------------------
def test_13_law_not_yet_effective(client):
    """
    A new state law has been enacted but is not yet effective.
    The platform must distinguish future preparation tasks from present legal obligations.
    """
    payload = {
        "organization": {
            "name": "Midwest Manufacturing Enterprise",
            "industry": "technology",
            "organization_type": "private",
            "annual_revenue_usd": 120000000,
            "consumer_records_count": 250000,
            "establishments": ["US-IN", "US-KY", "US-RI", "US-CO"],
        },
        "activity": {
            "purpose": "Automated consumer profiling and high-risk AI credit scoring",
            "data_categories": ["personal_information", "financial_data"],
            "subject_locations": ["US-IN", "US-KY", "US-RI", "US-CO"],
            "processing_locations": ["US-IN"],
            "involves_ai_or_admt": True,
        },
        "evaluation_date": "2025-06-01",
        "include_non_effective_laws": True,
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    future_ids = {i["regulation_id"] for i in data["future_preparation_obligations"]}
    present_ids = {i["regulation_id"] for i in data["applicable_instruments"]}

    assert len(future_ids) >= 1
    assert len(present_ids) >= 1
    assert future_ids.isdisjoint(present_ids)
    assert all(i["applicability_status"] == "applicable_future_preparation" for i in data["future_preparation_obligations"])


# ---------------------------------------------------------------------------
# Test 14: Conflicting or Ambiguous Rules
# ---------------------------------------------------------------------------
def test_14_conflicting_or_ambiguous_rules(client):
    """
    Two regulations produce potentially overlapping or conflicting instructions.
    The system must show both sources, explain the uncertainty and route the conflict
    for authorized legal review. Do not invent legal priority rules.
    """
    payload = {
        "organization": {
            "name": "Transatlantic Medical & Financial Group",
            "industry": "healthcare",
            "organization_type": "healthcare_covered_entity",
            "hipaa_status": "covered_entity",
            "establishments": ["US-CA", "CA-ON", "CA-QC", "EU-DE"],
        },
        "activity": {
            "purpose": "Cross-border patient medical billing and erasure request handling",
            "data_categories": ["health_information", "phi", "financial_data", "personal_information"],
            "subject_locations": ["US-CA", "CA-ON", "CA-QC", "EU-DE"],
            "processing_locations": ["CA-ON", "EU-DE"],
            "transfer_destinations": ["US-CA"],
            "involves_cross_border_transfer": True,
        },
    }
    resp = client.post("/api/v1/compliance/applicability/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    conflicts = data.get("conflicts_and_escalations", [])
    assert len(conflicts) >= 1
    assert data["requires_legal_review"] is True
    multi_reg_conflicts = [c for c in conflicts if len(c["regulations_involved"]) >= 2]
    assert len(multi_reg_conflicts) >= 1
    for c in multi_reg_conflicts:
        assert len(c["regulations_involved"]) >= 2
        assert len(c["sources"]) >= 2
        assert c["requires_legal_review"] is True


# ---------------------------------------------------------------------------
# Test 15: LLM Unavailable
# ---------------------------------------------------------------------------
def test_15_llm_unavailable(client, monkeypatch):
    """
    Disable all configured LLMs.
    Verify that core case management, deterministic rules, statutory deadlines
    and audit history continue to function.
    """
    monkeypatch.setenv("KIBO_DISABLE_LLMS", "1")
    monkeypatch.setenv("OLLAMA_LOCAL_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("OLLAMA_DGX_URL", "http://127.0.0.1:1")

    # 1. Deterministic JRAE evaluation works with LLMs disabled
    eval_resp = client.post(
        "/api/v1/compliance/applicability/evaluate",
        json={
            "organization": {"industry": "healthcare", "organization_type": "private", "establishments": ["CA-ON", "US-CA"]},
            "activity": {"purpose": "Patient scheduling", "data_categories": ["health_information"], "subject_locations": ["CA-ON"]},
        },
    )
    assert eval_resp.status_code == 200
    assert len(eval_resp.json()["applicable_instruments"]) >= 1

    # 2. Deterministic statutory deadline calculation works with LLMs disabled
    dl_resp = client.post(
        "/api/v1/compliance/deadlines/calculate",
        json={"workflow_type": "dsar", "jurisdiction_id": "CA-QC", "request_type": "access"},
    )
    assert dl_resp.status_code == 200
    assert dl_resp.json()["initial_days"] == 30

    # 3. Deterministic Assessment creation & approval audit trail works with LLMs disabled
    asm_resp = client.post(
        "/api/v1/office/assessments",
        headers={"X-Tenant-ID": "default", "X-User-ID": "user_expert"},
        json={
            "title": "Offline LLM Resilience Assessment",
            "assessment_type": "TRA",
            "jurisdictions": ["CA-ON"],
            "data_categories": ["health_information"],
            "processing_activities": ["cloud_hosting"],
        },
    )
    assert asm_resp.status_code == 200
    asm_id = asm_resp.json()["assessment_id"]

    approve_resp = client.post(
        f"/api/v1/office/assessments/{asm_id}/approve",
        headers={"X-Tenant-ID": "default", "X-User-ID": "user_expert"},
        json={"approver_id": "user_expert", "approver_role": "CPO", "rationale": "Verified deterministically while LLMs offline"},
    )
    assert approve_resp.status_code == 200
    approved_body = approve_resp.json()
    assert len(approved_body.get("approvals", [])) >= 1
    assert approved_body["approvals"][0].get("cryptographic_hash") is not None
