"""
MODULE 5 – Vendor Risk Management
Vendor assessment service: create, score, approve assessments.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import select

from core.models.vendor_assessment import VendorRiskAssessment as VendorAssessment, AssessmentResult, AssessmentEvidence
from core.events.domain_events import VendorAssessed


# ─── Risk scoring helpers ─────────────────────────────────────────────────────

def _compute_risk_level(score: float) -> str:
    if score >= 85:
        return 'critical'
    elif score >= 70:
        return 'high'
    elif score >= 50:
        return 'medium'
    return 'low'


# ─── Service ─────────────────────────────────────────────────────────────────

class VendorAssessmentService:
    """Handles assessment CRUD, risk scoring, and approval transitions."""

    def __init__(self, db: Session):
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────

    def create_assessment(
        self,
        vendor_id: str,
        assessment_type: str,
        framework: str,
        tenant_id: str,
        assessor_id: Optional[str] = None,
        template_id: Optional[str] = None,
    ) -> VendorAssessment:
        """Create a new assessment in draft status."""
        assessment = VendorAssessment(
            id=str(uuid4()),
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            assessment_type=assessment_type,
            framework=framework,
            status='draft',
            assessor_id=assessor_id,
            template_id=template_id,
            started_at=datetime.utcnow(),
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    # ── Add results ───────────────────────────────────────────────────────────

    def add_result(
        self,
        assessment_id: str,
        question_id: str,
        answer: str,
        score: float,
        evidence: Optional[str] = None,
        weight: float = 1.0,
        tenant_id: str = 'default',
    ) -> AssessmentResult:
        """Record an individual question answer and score."""
        result = AssessmentResult(
            id=str(uuid4()),
            tenant_id=tenant_id,
            assessment_id=assessment_id,
            question_id=question_id,
            answer=answer,
            score=score,
            weight=weight,
            evidence=evidence,
        )
        self.db.add(result)
        self.db.commit()
        return result

    # ── Scoring ───────────────────────────────────────────────────────────────

    def calculate_risk_score(self, assessment_id: str) -> Optional[dict]:
        """
        Calculate weighted risk score from all results.
        Returns dict with risk_score (0-100), risk_level, assessment_id.
        """
        assessment = self.db.get(VendorAssessment, assessment_id)
        if not assessment:
            return None

        results = (
            self.db.query(AssessmentResult)
            .filter(AssessmentResult.assessment_id == assessment_id)
            .all()
        )

        if not results:
            return None

        # Weighted average score (each score is 0-10, normalise to 0-100)
        total_weight = sum(r.weight for r in results)
        if total_weight == 0:
            return None

        weighted_sum = sum(r.score * r.weight for r in results)
        risk_score = (weighted_sum / total_weight) * 10  # scale to 0-100
        risk_level = _compute_risk_level(risk_score)

        assessment.risk_score = risk_score
        assessment.risk_level = risk_level
        assessment.status = 'completed'
        assessment.completed_at = datetime.utcnow()
        self.db.add(assessment)
        self.db.commit()

        return {
            'assessment_id': assessment_id,
            'risk_score': risk_score,
            'risk_level': risk_level,
        }

    # ── Approve ───────────────────────────────────────────────────────────────

    def approve_assessment(
        self,
        assessment_id: str,
        approved_by: str,
    ) -> Optional[VendorAssessment]:
        assessment = self.db.get(VendorAssessment, assessment_id)
        if not assessment:
            return None
        if assessment.status not in ('completed', 'conditional'):
            raise ValueError(f"Cannot approve assessment with status '{assessment.status}'")

        # Auto-approve or make conditional based on risk level
        if assessment.risk_level == 'critical':
            assessment.status = 'blocked'
        elif assessment.risk_level == 'high':
            assessment.status = 'conditional'
        else:
            assessment.status = 'approved'

        assessment.approved_by = approved_by
        assessment.approved_at = datetime.utcnow()
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_assessment(self, assessment_id: str) -> Optional[VendorAssessment]:
        return self.db.get(VendorAssessment, assessment_id)

    def list_by_vendor(self, vendor_id: str, tenant_id: str) -> List[VendorAssessment]:
        return (
            self.db.query(VendorAssessment)
            .filter(
                VendorAssessment.vendor_id == vendor_id,
                VendorAssessment.tenant_id == tenant_id,
            )
            .order_by(VendorAssessment.created_at.desc())
            .all()
        )

    # ── Vendor risk summary ───────────────────────────────────────────────────

    def get_vendor_risk_summary(self, vendor_id: str, tenant_id: str) -> Optional[dict]:
        """
        Return overall weighted risk across security / privacy / financial assessments.
        Weights: security=40%, privacy=35%, financial=25%.
        """
        assessments = (
            self.db.query(VendorAssessment)
            .filter(
                VendorAssessment.vendor_id == vendor_id,
                VendorAssessment.tenant_id == tenant_id,
                VendorAssessment.status.in_(['completed', 'approved', 'conditional']),
            )
            .order_by(VendorAssessment.completed_at.desc())
            .all()
        )

        if not assessments:
            return None

        type_score: dict[str, Optional[float]] = {'security': None, 'privacy': None, 'financial': None}
        for a in assessments:
            t = a.assessment_type
            if t in type_score and type_score[t] is None:
                type_score[t] = a.risk_score

        weights = {'security': 0.4, 'privacy': 0.35, 'financial': 0.25}
        overall = sum(
            (type_score[t] or 50.0) * w
            for t, w in weights.items()
        )

        return {
            'vendor_id': vendor_id,
            'overall_risk_score': round(overall, 2),
            'overall_risk_level': _compute_risk_level(overall),
            'security_risk': type_score['security'],
            'privacy_risk': type_score['privacy'],
            'financial_risk': type_score['financial'],
            'assessments': [
                {
                    'id': a.id,
                    'type': a.assessment_type,
                    'score': a.risk_score,
                    'level': a.risk_level,
                    'status': a.status,
                    'completed_at': a.completed_at.isoformat() if a.completed_at else None,
                }
                for a in assessments
            ],
        }
