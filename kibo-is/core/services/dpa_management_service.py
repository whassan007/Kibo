"""
MODULE 5 – Vendor Risk Management
DPA Management Service: lifecycle management, expiry checking, renewal workflow.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.vendor_dpa import DataProcessingAgreement, StandardContractualClause
from core.events.domain_events import VendorDPAExpiring


class DPAManagementService:
    """Handles DPA creation, approval, and automated expiry monitoring."""

    def __init__(self, db: Session):
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────

    def create_dpa(
        self,
        vendor_id: str,
        tenant_id: str,
        dpa_type: str,
        effective_date: datetime,
        expiry_date: datetime,
        document_path: str,
        cross_border: bool = False,
        source_jurisdiction: Optional[str] = None,
        destination_jurisdiction: Optional[str] = None,
        sccs: bool = False,
        sccs_version: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> DataProcessingAgreement:
        dpa = DataProcessingAgreement(
            id=str(uuid4()),
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            dpa_type=dpa_type,
            status='draft',
            effective_date=effective_date,
            expiry_date=expiry_date,
            agreement_document=document_path,
            cross_border_transfer=cross_border,
            source_jurisdiction=source_jurisdiction,
            destination_jurisdiction=destination_jurisdiction,
            standard_contractual_clauses=sccs,
            standard_contractual_clauses_version=sccs_version,
            renewal_notifications_sent={},
            created_by=created_by,
        )
        self.db.add(dpa)
        self.db.commit()
        self.db.refresh(dpa)
        return dpa

    # ── Approve ───────────────────────────────────────────────────────────────

    def approve_dpa(
        self,
        dpa_id: str,
        approved_by: str,
        dpo_review_date: Optional[datetime] = None,
    ) -> Optional[DataProcessingAgreement]:
        dpa = self.db.get(DataProcessingAgreement, dpa_id)
        if not dpa:
            return None
        dpa.status = 'executed'
        dpa.approved_by = approved_by
        dpa.approved_at = datetime.utcnow()
        dpa.execution_date = datetime.utcnow()
        if dpo_review_date:
            dpa.dpo_review_date = dpo_review_date
            dpa.dpo_approval = True
        self.db.add(dpa)
        self.db.commit()
        self.db.refresh(dpa)
        return dpa

    # ── Expiry monitoring ─────────────────────────────────────────────────────

    def check_dpa_expiry(self, tenant_id: str) -> List[dict]:
        """
        Scan executed DPAs for impending expiry (30-day and 7-day windows).
        Returns list of DPAs that triggered notifications.
        """
        now = datetime.utcnow()
        thirty_days_out = now + timedelta(days=30)

        expiring: List[DataProcessingAgreement] = (
            self.db.query(DataProcessingAgreement)
            .filter(
                DataProcessingAgreement.tenant_id == tenant_id,
                DataProcessingAgreement.status == 'executed',
                DataProcessingAgreement.expiry_date <= thirty_days_out,
                DataProcessingAgreement.expiry_date > now,
            )
            .all()
        )

        triggered = []
        for dpa in expiring:
            days_left = (dpa.expiry_date - now).days
            notifications = dict(dpa.renewal_notifications_sent or {})

            fire_30 = days_left <= 30 and '30_days' not in notifications
            fire_7 = days_left <= 7 and '7_days' not in notifications

            if fire_30:
                notifications['30_days'] = now.isoformat()
                triggered.append({'dpa_id': dpa.id, 'days_left': days_left, 'window': '30_days'})

            if fire_7:
                notifications['7_days'] = now.isoformat()
                triggered.append({'dpa_id': dpa.id, 'days_left': days_left, 'window': '7_days'})

            if fire_30 or fire_7:
                dpa.renewal_notifications_sent = notifications
                self.db.add(dpa)

        self.db.commit()
        return triggered

    # ── Add SCCs ──────────────────────────────────────────────────────────────

    def add_scc(
        self,
        dpa_id: str,
        tenant_id: str,
        clause_type: str,
        module_description: str,
        exporter_role: str,
        importer_role: str,
    ) -> StandardContractualClause:
        scc = StandardContractualClause(
            id=str(uuid4()),
            tenant_id=tenant_id,
            dpa_id=dpa_id,
            clause_type=clause_type,
            module_description=module_description,
            exporter_role=exporter_role,
            importer_role=importer_role,
        )
        self.db.add(scc)
        self.db.commit()
        self.db.refresh(scc)
        return scc

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_dpa(self, dpa_id: str) -> Optional[DataProcessingAgreement]:
        return self.db.get(DataProcessingAgreement, dpa_id)

    def list_by_vendor(self, vendor_id: str, tenant_id: str) -> List[DataProcessingAgreement]:
        return (
            self.db.query(DataProcessingAgreement)
            .filter(
                DataProcessingAgreement.vendor_id == vendor_id,
                DataProcessingAgreement.tenant_id == tenant_id,
            )
            .order_by(DataProcessingAgreement.created_at.desc())
            .all()
        )

    def list_expiring(self, tenant_id: str, within_days: int = 30) -> List[DataProcessingAgreement]:
        """Return all executed DPAs expiring within `within_days` days."""
        cutoff = datetime.utcnow() + timedelta(days=within_days)
        return (
            self.db.query(DataProcessingAgreement)
            .filter(
                DataProcessingAgreement.tenant_id == tenant_id,
                DataProcessingAgreement.status == 'executed',
                DataProcessingAgreement.expiry_date <= cutoff,
                DataProcessingAgreement.expiry_date > datetime.utcnow(),
            )
            .order_by(DataProcessingAgreement.expiry_date.asc())
            .all()
        )
