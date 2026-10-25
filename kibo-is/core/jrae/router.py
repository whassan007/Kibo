"""
KIBO Privacy OS — Compliance & Applicability Engine Router
Exposes:
- POST /api/v1/compliance/applicability/evaluate (Required by Section 7)
- GET  /api/v1/compliance/jurisdictions
- GET  /api/v1/compliance/regulations
- POST /api/v1/compliance/deadlines/calculate
- POST /api/v1/compliance/regulatory-changes/simulate
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.jrae.schemas import (
    ApplicabilityEvaluationRequest,
    ApplicabilityEvaluationResponse,
    CanonicalRegulation,
    JurisdictionEntry,
)
from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code

router = APIRouter(prefix="/api/v1/compliance", tags=["JRAE Multi-Jurisdictional Applicability Engine"])


class DeadlineCalculationRequest(BaseModel):
    workflow_type: str = Field(..., description="dsar or breach")
    jurisdiction_id: Optional[str] = None
    jurisdictions: List[str] = Field(default_factory=list)
    request_type: str = "access"
    trigger_timestamp: Optional[datetime] = None
    is_complex_or_extended: bool = False
    affected_counts_by_jurisdiction: Dict[str, int] = Field(default_factory=dict)
    involves_phi: bool = False
    involves_financial: bool = False
    is_critical_infrastructure: bool = False
    risk_of_harm_level: str = "high"


class RegulatoryChangeSimulationRequest(BaseModel):
    regulation_id: str
    amendment_summary: str
    new_version: str = "2026.11.0"
    affected_fields: List[str] = Field(default_factory=lambda: ["response_deadlines", "required_assessments"])
    effective_date: Optional[str] = None
    reviewer: Optional[str] = None
    approval_decision: str = "pending_legal_review"


def _get_engine():
    from core.jrae.engine import JurisdictionalApplicabilityEngine
    return JurisdictionalApplicabilityEngine()


@router.post("/applicability/evaluate", response_model=ApplicabilityEvaluationResponse)
def evaluate_applicability(payload: ApplicabilityEvaluationRequest, request: Request):
    """
    Evaluate multi-jurisdictional regulatory applicability across US (Federal + 50 States + DC + territories),
    Canada (Federal + 10 Provinces + 3 Territories), and European Union (EU-wide + 27 Member States).
    """
    engine = _get_engine()
    return engine.evaluate(payload)


@router.get("/jurisdictions")
def list_jurisdictions(
    country: Optional[str] = Query(default=None),
    production_enabled_only: bool = Query(default=False),
) -> Dict[str, Any]:
    items = list(GLOBAL_JURISDICTION_REGISTRY.values())
    if country:
        items = [j for j in items if j.country.upper() == country.upper() or j.jurisdiction_id.startswith(country.upper())]
    if production_enabled_only:
        items = [j for j in items if j.production_enabled]
    return {
        "total": len(items),
        "jurisdictions": [j.model_dump() for j in items],
    }


@router.get("/regulations")
def list_canonical_regulations(
    jurisdiction_id: Optional[str] = Query(default=None),
    domain_category: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    engine = _get_engine()
    regs = engine.get_all_regulations()
    if jurisdiction_id:
        norm = normalize_jurisdiction_code(jurisdiction_id)
        regs = [r for r in regs if r.jurisdiction_id == norm]
    if domain_category:
        regs = [r for r in regs if r.domain_category == domain_category]
    return {
        "total": len(regs),
        "regulations": [r.model_dump(mode="json") for r in regs],
    }


@router.post("/deadlines/calculate")
def calculate_deadlines_endpoint(payload: DeadlineCalculationRequest) -> Dict[str, Any]:
    from core.jrae.deadlines import calculate_dsar_deadline, calculate_breach_deadlines

    ts = payload.trigger_timestamp or datetime.utcnow()
    if payload.workflow_type.lower() == "dsar":
        jur = normalize_jurisdiction_code(payload.jurisdiction_id or (payload.jurisdictions[0] if payload.jurisdictions else "EU"))
        return calculate_dsar_deadline(
            jurisdiction_id=jur,
            request_type=payload.request_type,
            received_at=ts,
            is_complex_or_extended=payload.is_complex_or_extended,
        )
    elif payload.workflow_type.lower() == "breach":
        jurs = [normalize_jurisdiction_code(j) for j in (payload.jurisdictions or ([payload.jurisdiction_id] if payload.jurisdiction_id else ["EU"]))]
        return calculate_breach_deadlines(
            jurisdictions=jurs,
            discovery_time=ts,
            affected_counts_by_jurisdiction=payload.affected_counts_by_jurisdiction,
            involves_phi=payload.involves_phi,
            involves_financial=payload.involves_financial,
            is_critical_infrastructure=payload.is_critical_infrastructure,
            risk_of_harm_level=payload.risk_of_harm_level,
        )
    raise HTTPException(status_code=400, detail=f"Unsupported workflow_type: {payload.workflow_type}")


@router.post("/regulatory-changes/simulate")
def simulate_regulatory_change_endpoint(payload: RegulatoryChangeSimulationRequest) -> Dict[str, Any]:
    engine = _get_engine()
    return engine.simulate_regulatory_change(
        regulation_id=payload.regulation_id,
        amendment_summary=payload.amendment_summary,
        new_version=payload.new_version,
        affected_fields=payload.affected_fields,
        reviewer=payload.reviewer,
        approval_decision=payload.approval_decision,
    )
