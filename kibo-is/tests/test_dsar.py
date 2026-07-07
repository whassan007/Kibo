"""
Tests for MODULE 6 – DSAR Workflows
Covers: DsarIntakeService, DsarScopeService, DsarCollectionService,
        DsarRedactionService, DsarDeliveryService, DsarFulfillmentWorkflow.
"""

import pytest
import os
import sys
import json
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
    import core.models  # noqa: F401
    import core.modules.vendor_risk.models  # noqa: F401  (registers 'vendors' table)
    Base.metadata.create_all(engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


# ─── DsarIntakeService ───────────────────────────────────────────────────────

class TestDsarIntakeService:
    """Tests for DSAR intake: registration, verification, refusal, deadline queries."""

    def test_receive_request_gdpr_deadline(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService

        svc = DsarIntakeService(db_session)
        req = svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="user@example.com",
            requestor_email="user@example.com",
        )
        assert req.id is not None
        assert req.status == "received"
        assert req.jurisdiction == "GDPR"
        # GDPR = 30 days
        assert req.days_remaining == 30
        delta = req.deadline - req.received_at
        assert 29 <= delta.days <= 31

    def test_receive_request_ccpa_deadline(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService

        svc = DsarIntakeService(db_session)
        req = svc.receive_request(
            tenant_id="test_tenant",
            request_type="deletion",
            jurisdiction="CCPA",
            identifier_type="email",
            identifier_value="ccpa-user@example.com",
            requestor_email="ccpa-user@example.com",
        )
        # CCPA = 45 days
        assert req.days_remaining == 45

    def test_receive_request_creates_data_subject(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService
        from core.models.dsar_request import DataSubject

        svc = DsarIntakeService(db_session)
        req = svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="new-subject@example.com",
            requestor_email="new-subject@example.com",
        )
        subject = db_session.query(DataSubject).filter(
            DataSubject.identifier_value == "new-subject@example.com"
        ).first()
        assert subject is not None
        assert req.data_subject_id == subject.id

    def test_find_or_create_data_subject_idempotent(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService
        from core.models.dsar_request import DataSubject

        svc = DsarIntakeService(db_session)
        # Two requests for same subject
        req1 = svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="repeat@example.com",
            requestor_email="repeat@example.com",
        )
        req2 = svc.receive_request(
            tenant_id="test_tenant",
            request_type="portability",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="repeat@example.com",
            requestor_email="repeat@example.com",
        )
        assert req1.data_subject_id == req2.data_subject_id
        subjects = db_session.query(DataSubject).filter(
            DataSubject.identifier_value == "repeat@example.com"
        ).all()
        assert len(subjects) == 1

    def test_mark_verified(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService

        svc = DsarIntakeService(db_session)
        req = svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="verify-me@example.com",
            requestor_email="verify-me@example.com",
        )
        updated = svc.mark_verified(req.id, "government_id", verified_by="admin")
        assert updated.status == "scoping"

    def test_refuse_request(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService

        svc = DsarIntakeService(db_session)
        req = svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="refuse-me@example.com",
            requestor_email="refuse-me@example.com",
        )
        refused = svc.refuse_request(req.id, "manifestly_unfounded", "Third repeat within 6 months")
        assert refused.status == "refused"
        assert refused.refuse_reason == "manifestly_unfounded"

    def test_list_requests_by_status(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService

        svc = DsarIntakeService(db_session)
        for i in range(3):
            svc.receive_request(
                tenant_id="test_tenant",
                request_type="access",
                jurisdiction="GDPR",
                identifier_type="email",
                identifier_value=f"user{i}@example.com",
                requestor_email=f"user{i}@example.com",
            )
        all_reqs = svc.list_requests("test_tenant")
        assert len(all_reqs) == 3

        received = svc.list_requests("test_tenant", status="received")
        assert len(received) == 3


# ─── DsarScopeService ────────────────────────────────────────────────────────

class TestDsarScopeService:
    """Tests for scope determination and collection task generation."""

    def _make_request(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService
        svc = DsarIntakeService(db_session)
        return svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="scope-user@example.com",
            requestor_email="scope-user@example.com",
        )

    def test_determine_scope_with_defaults(self, db_session):
        from core.services.dsar_scope_service import DsarScopeService

        req = self._make_request(db_session)
        svc = DsarScopeService(db_session)
        scope = svc.determine_scope(
            request_id=req.id,
            systems_override=["crm", "billing"],
            scope_determined_by="dpo",
        )
        assert scope is not None
        assert "crm" in scope.systems_in_scope
        assert "billing" in scope.systems_in_scope
        # Default categories
        assert len(scope.data_categories) >= 5

    def test_determine_scope_creates_data_elements(self, db_session):
        from core.services.dsar_scope_service import DsarScopeService
        from core.models.dsar_request import RequestedDataElement

        req = self._make_request(db_session)
        svc = DsarScopeService(db_session)
        svc.determine_scope(
            request_id=req.id,
            systems_override=["sys_a", "sys_b"],
            categories_override=["PersonalInformation", "ContactDetails"],
        )
        elements = db_session.query(RequestedDataElement).filter(
            RequestedDataElement.request_id == req.id
        ).all()
        # 2 systems * 2 categories = 4 elements
        assert len(elements) == 4

    def test_mark_element_collected(self, db_session):
        from core.services.dsar_scope_service import DsarScopeService
        from core.models.dsar_request import RequestedDataElement

        req = self._make_request(db_session)
        svc = DsarScopeService(db_session)
        svc.determine_scope(
            request_id=req.id,
            systems_override=["sys_x"],
            categories_override=["PersonalInformation"],
        )
        elements = svc.list_pending_elements(req.id)
        assert len(elements) == 1

        updated = svc.mark_element_collected(elements[0].id, record_count=42, data_size_mb=1.5)
        assert updated.status == "collected"
        assert updated.actual_record_count == 42


# ─── DsarCollectionService ───────────────────────────────────────────────────

class TestDsarCollectionService:
    """Tests for data collection task management and aggregation."""

    def test_task_lifecycle(self, db_session):
        from core.services.dsar_collection_service import DsarCollectionService

        svc = DsarCollectionService(db_session)
        task = svc.create_collection_task(
            request_id="req-001",
            tenant_id="test_tenant",
            system_id="crm",
            system_name="CRM System",
            data_category="PersonalInformation",
        )
        assert task.status == "pending"

        started = svc.start_task(task.id)
        assert started.status == "in_progress"
        assert started.started_at is not None

        completed = svc.complete_task(
            task.id,
            records_found=100,
            data_size_mb=2.5,
            collection_output={"records": [{"name": "John"}]},
        )
        assert completed.status == "completed"
        assert completed.records_found == 100

    def test_fail_task(self, db_session):
        from core.services.dsar_collection_service import DsarCollectionService

        svc = DsarCollectionService(db_session)
        task = svc.create_collection_task(
            request_id="req-002",
            tenant_id="test_tenant",
            system_id="legacy",
            system_name="Legacy DB",
            data_category="ContactDetails",
        )
        failed = svc.fail_task(task.id, "Connection timeout after 30s")
        assert failed.status == "failed"
        assert failed.error_message == "Connection timeout after 30s"

    def test_aggregate_collected_data(self, db_session):
        from core.services.dsar_collection_service import DsarCollectionService

        svc = DsarCollectionService(db_session)
        rid = "req-003"
        for sys_id, cat, recs in [("crm", "PI", 10), ("billing", "Payment", 5)]:
            t = svc.create_collection_task(rid, "test_tenant", sys_id, sys_id, cat)
            svc.complete_task(t.id, recs, 0.5, {"data": f"{sys_id}_{cat}"})

        agg = svc.aggregate_collected_data(rid)
        assert agg["total_records"] == 15
        assert agg["systems_collected"] == 2
        assert "crm::PI" in agg["data"]

    def test_is_collection_complete(self, db_session):
        from core.services.dsar_collection_service import DsarCollectionService

        svc = DsarCollectionService(db_session)
        rid = "req-004"
        t1 = svc.create_collection_task(rid, "test_tenant", "s1", "S1", "PI")
        t2 = svc.create_collection_task(rid, "test_tenant", "s2", "S2", "PI")

        assert svc.is_collection_complete(rid) is False

        svc.complete_task(t1.id, 10, 1.0, {})
        assert svc.is_collection_complete(rid) is False

        svc.complete_task(t2.id, 5, 0.5, {})
        assert svc.is_collection_complete(rid) is True


# ─── DsarRedactionService ────────────────────────────────────────────────────

class TestDsarRedactionService:
    """Tests for PII redaction and audit logging."""

    def test_redact_email_field(self, db_session):
        from core.services.dsar_redaction_service import DsarRedactionService

        svc = DsarRedactionService(db_session)
        data = {
            "user": {
                "email": "john.doe@example.com",
                "name": "John Doe",
            }
        }
        redacted = svc.apply_redactions(
            request_id="r-100",
            tenant_id="test_tenant",
            data=data,
        )
        db_session.commit()

        # Email should be masked; name is not in the email_mask field list
        assert "***@" in redacted["user"]["email"]
        assert redacted["user"]["name"] == "John Doe"

    def test_redact_phone_field(self, db_session):
        from core.services.dsar_redaction_service import DsarRedactionService

        svc = DsarRedactionService(db_session)
        data = {"contact": {"phone": "+1-555-123-4567"}}
        redacted = svc.apply_redactions("r-101", "test_tenant", data)
        db_session.commit()

        assert redacted["contact"]["phone"] != "+1-555-123-4567"

    def test_redaction_creates_audit_trail(self, db_session):
        from core.services.dsar_redaction_service import DsarRedactionService
        from core.models.dsar_redaction import AppliedRedaction

        svc = DsarRedactionService(db_session)
        data = {"record": {"email": "audit-me@test.com"}}
        svc.apply_redactions("r-102", "test_tenant", data)
        db_session.commit()

        logs = db_session.query(AppliedRedaction).filter(
            AppliedRedaction.request_id == "r-102"
        ).all()
        assert len(logs) >= 1
        assert logs[0].field_name == "email"
        assert logs[0].original_value_hash is not None  # SHA256

    def test_redact_nested_data(self, db_session):
        from core.services.dsar_redaction_service import DsarRedactionService

        svc = DsarRedactionService(db_session)
        data = {
            "users": {
                "primary": {"email": "primary@corp.com"},
                "secondary": {"email": "secondary@corp.com"},
            }
        }
        redacted = svc.apply_redactions("r-103", "test_tenant", data)
        db_session.commit()

        assert "***@" in redacted["users"]["primary"]["email"]
        assert "***@" in redacted["users"]["secondary"]["email"]

    def test_create_custom_rule(self, db_session):
        from core.services.dsar_redaction_service import DsarRedactionService

        svc = DsarRedactionService(db_session)
        rule = svc.create_rule(
            tenant_id="test_tenant",
            name="Employee ID Mask",
            rule_type="employee_id_mask",
            pattern=r"EMP-\d{6}",
            replacement="EMP-******",
            fields=["employee_id"],
        )
        assert rule.id is not None
        assert rule.is_active is True

        rules = svc.list_rules("test_tenant")
        assert len(rules) >= 1


# ─── DsarDeliveryService ─────────────────────────────────────────────────────

class TestDsarDeliveryService:
    """Tests for package preparation, delivery, and download token validation."""

    def _make_request_for_delivery(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService
        svc = DsarIntakeService(db_session)
        return svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="deliver@example.com",
            requestor_email="deliver@example.com",
        )

    def test_prepare_package(self, db_session):
        from core.services.dsar_delivery_service import DsarDeliveryService
        import tempfile

        req = self._make_request_for_delivery(db_session)
        pkg_dir = tempfile.mkdtemp()
        svc = DsarDeliveryService(db_session, package_base_dir=pkg_dir)

        redacted_data = {"total_records": 42, "data": {"crm::PI": []}}
        package = svc.prepare_package(
            request_id=req.id,
            tenant_id="test_tenant",
            redacted_data=redacted_data,
        )
        assert package.id is not None
        assert package.status == "ready"
        assert package.file_hash is not None
        assert package.download_token is not None
        assert len(package.file_hash) == 64  # SHA256 hex length
        assert os.path.exists(package.file_path)

    def test_deliver_package(self, db_session):
        from core.services.dsar_delivery_service import DsarDeliveryService
        import tempfile

        req = self._make_request_for_delivery(db_session)
        pkg_dir = tempfile.mkdtemp()
        svc = DsarDeliveryService(db_session, package_base_dir=pkg_dir)
        svc.prepare_package(req.id, "test_tenant", {"total_records": 1, "data": {}})

        delivered = svc.deliver_package(
            request_id=req.id,
            delivery_method="email",
            delivery_address="deliver@example.com",
        )
        assert delivered.status == "delivered"
        assert delivered.delivered_at is not None

    def test_validate_download_token(self, db_session):
        from core.services.dsar_delivery_service import DsarDeliveryService
        import tempfile

        req = self._make_request_for_delivery(db_session)
        pkg_dir = tempfile.mkdtemp()
        svc = DsarDeliveryService(db_session, package_base_dir=pkg_dir)
        package = svc.prepare_package(req.id, "test_tenant", {"total_records": 1, "data": {}})

        # Valid token
        valid = svc.validate_download_token(req.id, package.download_token)
        assert valid is not None
        assert valid.id == package.id

        # Invalid token
        invalid = svc.validate_download_token(req.id, "wrong-token")
        assert invalid is None

    def test_package_verifications(self, db_session):
        from core.services.dsar_delivery_service import DsarDeliveryService
        import tempfile

        req = self._make_request_for_delivery(db_session)
        pkg_dir = tempfile.mkdtemp()
        svc = DsarDeliveryService(db_session, package_base_dir=pkg_dir)
        package = svc.prepare_package(req.id, "test_tenant", {"total_records": 5, "data": {}})

        verifications = svc.get_verifications(package.id)
        assert len(verifications) >= 4
        assert all(v.check_passed for v in verifications)


# ─── DsarFulfillmentWorkflow ─────────────────────────────────────────────────

class TestDsarFulfillmentWorkflow:
    """Tests for the end-to-end DSAR fulfillment pipeline."""

    def test_full_pipeline_runs_to_delivered(self, db_session):
        from core.services.dsar_intake_service import DsarIntakeService
        from core.services.dsar_scope_service import DsarScopeService
        from core.services.dsar_collection_service import DsarCollectionService
        from core.services.dsar_redaction_service import DsarRedactionService
        from core.services.dsar_delivery_service import DsarDeliveryService
        from core.workflows.dsar_fulfillment import DsarFulfillmentWorkflow
        import tempfile

        # Create a DSAR request
        intake_svc = DsarIntakeService(db_session)
        req = intake_svc.receive_request(
            tenant_id="test_tenant",
            request_type="access",
            jurisdiction="GDPR",
            identifier_type="email",
            identifier_value="workflow@example.com",
            requestor_email="workflow@example.com",
        )

        pkg_dir = tempfile.mkdtemp()
        workflow = DsarFulfillmentWorkflow(
            intake_service=intake_svc,
            scope_service=DsarScopeService(db_session),
            collection_service=DsarCollectionService(db_session),
            redaction_service=DsarRedactionService(db_session),
            delivery_service=DsarDeliveryService(db_session, package_base_dir=pkg_dir),
        )

        state = workflow.run(request_id=req.id, tenant_id="test_tenant")
        assert state["error"] is None
        assert state["status"] == "delivered"
        assert state["delivered"] is True
        assert state["package_id"] is not None
