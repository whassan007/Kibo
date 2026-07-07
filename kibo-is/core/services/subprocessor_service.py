"""
MODULE 5 – Vendor Risk Management
Subprocessor Service: CRUD for SubprocessorRegistry and DataTransfer records.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy.orm import Session

from core.models.subprocessor import SubprocessorRegistry, DataTransfer


class SubprocessorService:
    """Manages the sub-processor registry and data transfer records."""

    def __init__(self, db: Session):
        self.db = db

    # ── Subprocessor registry ─────────────────────────────────────────────────

    def register_subprocessor(
        self,
        vendor_id: str,
        tenant_id: str,
        name: str,
        service: str,
        country_of_processing: str,
        data_categories: List[str],
        risk_rating: str = 'medium',
        dpa_in_place: bool = False,
        dpa_reference: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> SubprocessorRegistry:
        sp = SubprocessorRegistry(
            id=str(uuid4()),
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            subprocessor_name=name,
            subprocessor_service=service,
            country_of_processing=country_of_processing,
            data_categories_processed=data_categories,
            risk_rating=risk_rating,
            dpa_in_place=dpa_in_place,
            dpa_reference=dpa_reference,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(sp)
        self.db.commit()
        self.db.refresh(sp)
        return sp

    def terminate_subprocessor(
        self,
        subprocessor_id: str,
        terminated_by: Optional[str] = None,
    ) -> Optional[SubprocessorRegistry]:
        sp = self.db.get(SubprocessorRegistry, subprocessor_id)
        if not sp:
            return None
        sp.status = 'terminated'
        sp.terminated_at = datetime.utcnow()
        sp.updated_by = terminated_by
        self.db.add(sp)
        self.db.commit()
        self.db.refresh(sp)
        return sp

    def list_by_vendor(self, vendor_id: str, tenant_id: str, active_only: bool = True) -> List[SubprocessorRegistry]:
        q = self.db.query(SubprocessorRegistry).filter(
            SubprocessorRegistry.vendor_id == vendor_id,
            SubprocessorRegistry.tenant_id == tenant_id,
        )
        if active_only:
            q = q.filter(SubprocessorRegistry.status == 'active')
        return q.order_by(SubprocessorRegistry.created_at.desc()).all()

    # ── Data transfers ────────────────────────────────────────────────────────

    def add_data_transfer(
        self,
        subprocessor_id: str,
        tenant_id: str,
        transfer_mechanism: str,
        source_country: str,
        destination_country: str,
        data_categories: List[str],
        transfer_frequency: str = 'continuous',
        safeguard_type: Optional[str] = None,
        safeguard_details: Optional[str] = None,
        adequacy_decision: Optional[bool] = None,
        scc_version: Optional[str] = None,
        bcr_reference: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> DataTransfer:
        dt = DataTransfer(
            id=str(uuid4()),
            tenant_id=tenant_id,
            subprocessor_id=subprocessor_id,
            transfer_mechanism=transfer_mechanism,
            source_country=source_country,
            destination_country=destination_country,
            data_categories=data_categories,
            transfer_frequency=transfer_frequency,
            safeguard_type=safeguard_type,
            safeguard_details=safeguard_details,
            adequacy_decision=adequacy_decision,
            scc_version=scc_version,
            bcr_reference=bcr_reference,
            created_by=created_by,
        )
        self.db.add(dt)
        self.db.commit()
        self.db.refresh(dt)
        return dt

    def list_transfers(
        self,
        subprocessor_id: str,
        active_only: bool = True,
    ) -> List[DataTransfer]:
        q = self.db.query(DataTransfer).filter(
            DataTransfer.subprocessor_id == subprocessor_id
        )
        if active_only:
            q = q.filter(DataTransfer.is_active == True)
        return q.all()
