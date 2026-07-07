# core/services/vendor_risk_service.py
"""Service layer for Vendor Risk Management.
Provides CRUD operations and risk scoring.
"""

from typing import List, Optional
from uuid import uuid4
from datetime import date

from sqlalchemy.orm import Session

from core.models.assets import Vendor
from core.models.vendor_assessment import VendorRiskAssessment as VendorAssessment
from core.models.subprocessor import SubprocessorRegistry as Subprocessor
from core.modules.vendor_risk.schemas import (
    VendorCreate,
    VendorRead,
    VendorUpdate,
    VendorAssessmentCreate,
    VendorAssessmentRead,
    SubprocessorCreate,
    SubprocessorRead,
)


def _vendor_to_read(vendor: Vendor) -> VendorRead:
    """Convert Vendor ORM instance to Pydantic read model."""
    return VendorRead(
        vendor_id=vendor.id,
        name=vendor.name,
        service=vendor.service,
        risk_rating=vendor.risk_rating.value if hasattr(vendor.risk_rating, "value") else vendor.risk_rating,
        dpa_status=vendor.dpa_status.value if hasattr(vendor.dpa_status, "value") else vendor.dpa_status,
        dpa_expiration_date=vendor.dpa_expiration_date,
        sccs_in_place=vendor.sccs_in_place,
        soc2_type=vendor.soc2_type.value if hasattr(vendor.soc2_type, "value") else vendor.soc2_type,
        cross_border=vendor.cross_border,
        status=vendor.status,
        next_review_date=vendor.next_review_date,
    )


def create_vendor(db: Session, payload: VendorCreate) -> VendorRead:
    vendor = Vendor(
        id=str(uuid4()),
        name=payload.name,
        service=payload.service,
        risk_rating=payload.risk_rating,
        dpa_status=payload.dpa_status,
        dpa_expiration_date=payload.dpa_expiration_date,
        sccs_in_place=payload.sccs_in_place,
        soc2_type=payload.soc2_type,
        cross_border=payload.cross_border,
        status=payload.status,
        next_review_date=payload.next_review_date,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return _vendor_to_read(vendor)


def get_vendor(db: Session, vendor_id: str) -> Optional[VendorRead]:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    return _vendor_to_read(vendor) if vendor else None


def list_vendors(db: Session, skip: int = 0, limit: int = 100) -> List[VendorRead]:
    vendors = db.query(Vendor).offset(skip).limit(limit).all()
    return [_vendor_to_read(v) for v in vendors]


def update_vendor(db: Session, vendor_id: str, payload: VendorUpdate) -> Optional[VendorRead]:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return None
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(vendor, attr, value)
    db.commit()
    db.refresh(vendor)
    return _vendor_to_read(vendor)


def delete_vendor(db: Session, vendor_id: str) -> bool:
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        return False
    db.delete(vendor)
    db.commit()
    return True

# Assessment helpers

def _assessment_to_read(assmt: VendorAssessment) -> VendorAssessmentRead:
    return VendorAssessmentRead(
        assessment_id=assmt.id,
        vendor_id=assmt.vendor_id,
        score=assmt.score,
        notes=assmt.notes,
    )


def create_assessment(db: Session, payload: VendorAssessmentCreate) -> VendorAssessmentRead:
    assessment = VendorAssessment(
        id=str(uuid4()),
        vendor_id=payload.vendor_id,
        score=payload.score,
        notes=payload.notes,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return _assessment_to_read(assessment)


def list_assessments(db: Session, vendor_id: str) -> List[VendorAssessmentRead]:
    assessments = db.query(VendorAssessment).filter(VendorAssessment.vendor_id == vendor_id).all()
    return [_assessment_to_read(a) for a in assessments]

# Subprocessor helpers

def _subprocessor_to_read(sp: Subprocessor) -> SubprocessorRead:
    return SubprocessorRead(
        subprocessor_id=sp.id,
        vendor_id=sp.vendor_id,
        name=sp.name,
        service=sp.service,
        risk_rating=sp.risk_rating.value if hasattr(sp.risk_rating, "value") else sp.risk_rating,
    )


def create_subprocessor(db: Session, payload: SubprocessorCreate) -> SubprocessorRead:
    sp = Subprocessor(
        id=str(uuid4()),
        vendor_id=payload.vendor_id,
        name=payload.name,
        service=payload.service,
        risk_rating=payload.risk_rating,
    )
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return _subprocessor_to_read(sp)


def list_subprocessors(db: Session, vendor_id: str) -> List[SubprocessorRead]:
    subs = db.query(Subprocessor).filter(Subprocessor.vendor_id == vendor_id).all()
    return [_subprocessor_to_read(s) for s in subs]

# Simple risk scoring algorithm (0-100) based on enum weights.
RISK_WEIGHT = {"low": 20, "medium": 50, "high": 80, "critical": 100}


def calculate_risk_score(vendor: Vendor) -> int:
    base = RISK_WEIGHT.get(vendor.risk_rating.value if hasattr(vendor.risk_rating, "value") else vendor.risk_rating, 0)
    if vendor.cross_border:
        base += 10
    if vendor.sccs_in_place:
        base -= 5
    return max(0, min(100, base))


def get_vendor_dashboard(db: Session) -> List[dict]:
    """Return a simple heatmap data structure for all vendors.
    Each entry includes vendor_id, name, and risk_score.
    """
    vendors = db.query(Vendor).all()
    result = []
    for v in vendors:
        score = calculate_risk_score(v)
        result.append({"vendor_id": v.id, "name": v.name, "risk_score": score})
    return result
