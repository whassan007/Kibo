"""
Tests for MODULE 5 – Vendor Risk Management
Covers: VendorAssessmentService, DPAManagementService, SubprocessorService,
        VendorOnboardingWorkflow, and risk scoring logic.
"""

import pytest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models.base import Base


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    # Import all models so tables are registered
    import core.models  # noqa: F401
    import core.modules.vendor_risk.models  # noqa: F401  (registers 'vendors' table)
    Base.metadata.create_all(engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


# ─── VendorAssessmentService ──────────────────────────────────────────────────

class TestVendorAssessmentService:
    """Tests for assessment lifecycle: create → add results → score → approve."""

    def test_create_assessment(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        assessment = svc.create_assessment(
            vendor_id="vendor-001",
            assessment_type="security",
            framework="ISO27001",
            tenant_id="test_tenant",
        )
        assert assessment is not None
        assert assessment.id is not None
        assert assessment.status == "draft"
        assert assessment.assessment_type == "security"
        assert assessment.framework == "ISO27001"

    def test_add_result_and_score(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        assessment = svc.create_assessment(
            vendor_id="vendor-002",
            assessment_type="privacy",
            framework="Custom",
            tenant_id="test_tenant",
        )

        # Add several results with varying scores and weights
        svc.add_result(assessment.id, "q1", "Yes", score=8.0, weight=2.0, tenant_id="test_tenant")
        svc.add_result(assessment.id, "q2", "Partial", score=5.0, weight=1.0, tenant_id="test_tenant")
        svc.add_result(assessment.id, "q3", "No", score=2.0, weight=1.0, tenant_id="test_tenant")

        result = svc.calculate_risk_score(assessment.id)
        assert result is not None
        assert "risk_score" in result
        assert "risk_level" in result
        # Weighted avg = (8*2 + 5*1 + 2*1) / (2+1+1) = 23/4 = 5.75 → *10 = 57.5
        assert 55 <= result["risk_score"] <= 60

        # Check assessment was marked completed
        updated = svc.get_assessment(assessment.id)
        assert updated.status == "completed"
        assert updated.completed_at is not None

    def test_approve_assessment_low_risk(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        assessment = svc.create_assessment(
            vendor_id="vendor-003",
            assessment_type="financial",
            framework="Custom",
            tenant_id="test_tenant",
        )
        svc.add_result(assessment.id, "q1", "Yes", score=3.0, weight=1.0, tenant_id="test_tenant")
        svc.calculate_risk_score(assessment.id)

        approved = svc.approve_assessment(assessment.id, approved_by="dpo@test.com")
        assert approved is not None
        # Score = 3.0 * 10 = 30 → low risk → approved
        assert approved.status == "approved"
        assert approved.approved_at is not None

    def test_approve_assessment_critical_risk_gets_blocked(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        assessment = svc.create_assessment(
            vendor_id="vendor-004",
            assessment_type="security",
            framework="Custom",
            tenant_id="test_tenant",
        )
        svc.add_result(assessment.id, "q1", "Critical", score=9.0, weight=1.0, tenant_id="test_tenant")
        svc.calculate_risk_score(assessment.id)

        result = svc.approve_assessment(assessment.id, approved_by="cpo@test.com")
        # Score = 9.0 * 10 = 90 → critical → blocked
        assert result.status == "blocked"

    def test_approve_on_draft_raises(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        assessment = svc.create_assessment(
            vendor_id="vendor-005",
            assessment_type="security",
            framework="Custom",
            tenant_id="test_tenant",
        )
        with pytest.raises(ValueError, match="Cannot approve"):
            svc.approve_assessment(assessment.id, approved_by="admin")

    def test_vendor_risk_summary_multi_type(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService

        svc = VendorAssessmentService(db_session)
        vid = "vendor-006"

        for atype, score_val in [("security", 4.0), ("privacy", 6.0), ("financial", 3.0)]:
            a = svc.create_assessment(vendor_id=vid, assessment_type=atype, framework="Custom", tenant_id="t1")
            svc.add_result(a.id, "q1", "Yes", score=score_val, weight=1.0, tenant_id="t1")
            svc.calculate_risk_score(a.id)

        summary = svc.get_vendor_risk_summary(vendor_id=vid, tenant_id="t1")
        assert summary is not None
        assert summary["vendor_id"] == vid
        assert "overall_risk_score" in summary
        assert summary["security_risk"] is not None
        assert summary["privacy_risk"] is not None
        assert summary["financial_risk"] is not None


# ─── DPAManagementService ────────────────────────────────────────────────────

class TestDPAManagementService:
    """Tests for DPA lifecycle: create → approve → expiry monitoring."""

    def test_create_and_approve_dpa(self, db_session):
        from core.services.dpa_management_service import DPAManagementService

        svc = DPAManagementService(db_session)
        dpa = svc.create_dpa(
            vendor_id="vendor-100",
            tenant_id="test_tenant",
            dpa_type="standard",
            effective_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365),
            document_path="/docs/dpa_vendor100.pdf",
        )
        assert dpa.status == "draft"

        approved = svc.approve_dpa(dpa.id, approved_by="legal@test.com")
        assert approved is not None
        assert approved.status == "executed"
        assert approved.approved_at is not None

    def test_dpa_expiry_check_30_day_window(self, db_session):
        from core.services.dpa_management_service import DPAManagementService

        svc = DPAManagementService(db_session)
        # Create DPA expiring in 25 days (inside the 30-day window)
        dpa = svc.create_dpa(
            vendor_id="vendor-101",
            tenant_id="test_tenant",
            dpa_type="standard",
            effective_date=datetime.utcnow() - timedelta(days=340),
            expiry_date=datetime.utcnow() + timedelta(days=25),
            document_path="/docs/dpa_expiring.pdf",
        )
        # Approve it first so it's in 'executed' status
        svc.approve_dpa(dpa.id, approved_by="legal@test.com")

        triggered = svc.check_dpa_expiry("test_tenant")
        assert len(triggered) >= 1
        assert any(t["dpa_id"] == dpa.id and t["window"] == "30_days" for t in triggered)

    def test_dpa_expiry_check_is_idempotent(self, db_session):
        from core.services.dpa_management_service import DPAManagementService

        svc = DPAManagementService(db_session)
        dpa = svc.create_dpa(
            vendor_id="vendor-102",
            tenant_id="test_tenant",
            dpa_type="standard",
            effective_date=datetime.utcnow() - timedelta(days=340),
            expiry_date=datetime.utcnow() + timedelta(days=25),
            document_path="/docs/dpa_idempotent.pdf",
        )
        svc.approve_dpa(dpa.id, approved_by="legal@test.com")

        first_run = svc.check_dpa_expiry("test_tenant")
        second_run = svc.check_dpa_expiry("test_tenant")

        # Second run should not re-trigger the same 30_days window
        first_ids = {t["dpa_id"] for t in first_run if t["window"] == "30_days"}
        second_ids = {t["dpa_id"] for t in second_run if t["window"] == "30_days"}
        assert dpa.id not in second_ids

    def test_list_expiring_dpas(self, db_session):
        from core.services.dpa_management_service import DPAManagementService

        svc = DPAManagementService(db_session)
        # Expiring in 10 days
        dpa1 = svc.create_dpa(
            vendor_id="vendor-103",
            tenant_id="test_tenant",
            dpa_type="standard",
            effective_date=datetime.utcnow() - timedelta(days=355),
            expiry_date=datetime.utcnow() + timedelta(days=10),
            document_path="/docs/exp10.pdf",
        )
        svc.approve_dpa(dpa1.id, approved_by="legal@test.com")

        # Expiring in 60 days (outside default 30 window)
        dpa2 = svc.create_dpa(
            vendor_id="vendor-104",
            tenant_id="test_tenant",
            dpa_type="standard",
            effective_date=datetime.utcnow() - timedelta(days=305),
            expiry_date=datetime.utcnow() + timedelta(days=60),
            document_path="/docs/exp60.pdf",
        )
        svc.approve_dpa(dpa2.id, approved_by="legal@test.com")

        expiring_30 = svc.list_expiring("test_tenant", within_days=30)
        assert any(d.id == dpa1.id for d in expiring_30)
        assert not any(d.id == dpa2.id for d in expiring_30)

    def test_add_scc_to_dpa(self, db_session):
        from core.services.dpa_management_service import DPAManagementService

        svc = DPAManagementService(db_session)
        dpa = svc.create_dpa(
            vendor_id="vendor-105",
            tenant_id="test_tenant",
            dpa_type="cross_border",
            effective_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=365),
            document_path="/docs/dpa_scc.pdf",
            cross_border=True,
        )
        scc = svc.add_scc(
            dpa_id=dpa.id,
            tenant_id="test_tenant",
            clause_type="module_2",
            module_description="Controller-to-Processor",
            exporter_role="controller",
            importer_role="processor",
        )
        assert scc.id is not None
        assert scc.clause_type == "module_2"


# ─── SubprocessorService ─────────────────────────────────────────────────────

class TestSubprocessorService:
    """Tests for subprocessor registry and data transfers."""

    def test_register_and_list(self, db_session):
        from core.services.subprocessor_service import SubprocessorService

        svc = SubprocessorService(db_session)
        sp = svc.register_subprocessor(
            vendor_id="vendor-200",
            tenant_id="test_tenant",
            name="SubCloud Inc",
            service="Data Storage",
            country_of_processing="US",
            data_categories=["PersonalInformation", "ContactDetails"],
        )
        assert sp.id is not None
        assert sp.status == "active"

        listed = svc.list_by_vendor("vendor-200", "test_tenant")
        assert len(listed) == 1
        assert listed[0].subprocessor_name == "SubCloud Inc"

    def test_terminate_subprocessor(self, db_session):
        from core.services.subprocessor_service import SubprocessorService

        svc = SubprocessorService(db_session)
        sp = svc.register_subprocessor(
            vendor_id="vendor-201",
            tenant_id="test_tenant",
            name="OldProcessor Co",
            service="Analytics",
            country_of_processing="DE",
            data_categories=["BehavioralData"],
        )
        terminated = svc.terminate_subprocessor(sp.id)
        assert terminated is not None
        assert terminated.status == "terminated"
        assert terminated.terminated_at is not None

        # Terminated subprocessor should not appear in active_only list
        active = svc.list_by_vendor("vendor-201", "test_tenant", active_only=True)
        assert len(active) == 0

    def test_add_data_transfer(self, db_session):
        from core.services.subprocessor_service import SubprocessorService

        svc = SubprocessorService(db_session)
        sp = svc.register_subprocessor(
            vendor_id="vendor-202",
            tenant_id="test_tenant",
            name="TransferHub",
            service="CDN",
            country_of_processing="IE",
            data_categories=["PersonalInformation"],
        )
        dt = svc.add_data_transfer(
            subprocessor_id=sp.id,
            tenant_id="test_tenant",
            transfer_mechanism="SCC",
            source_country="DE",
            destination_country="US",
            data_categories=["PersonalInformation"],
            safeguard_type="standard_contractual_clauses",
        )
        assert dt.id is not None
        assert dt.transfer_mechanism == "SCC"

        transfers = svc.list_transfers(sp.id)
        assert len(transfers) == 1


# ─── VendorOnboardingWorkflow ─────────────────────────────────────────────────

class TestVendorOnboardingWorkflow:
    """Tests for the end-to-end vendor onboarding pipeline."""

    def test_onboarding_runs_to_completion(self, db_session):
        from core.services.vendor_assessment_service import VendorAssessmentService
        from core.services.dpa_management_service import DPAManagementService
        from core.workflows.vendor_onboarding import VendorOnboardingWorkflow

        assessment_svc = VendorAssessmentService(db_session)
        dpa_svc = DPAManagementService(db_session)

        wf = VendorOnboardingWorkflow(
            assessment_service=assessment_svc,
            dpa_service=dpa_svc,
        )

        state = wf.run(
            vendor_id="wf-vendor-001",
            tenant_id="test_tenant",
            vendor_name="WorkflowTest Corp",
            service_type="SaaS",
        )

        assert state["error"] is None
        assert state["approval_status"] in ("approved", "conditional", "blocked")
        assert "security_assessment_id" in state["assessment_results"]
        assert "privacy_assessment_id" in state["assessment_results"]
