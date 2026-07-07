"""
MODULE 5 – Vendor Risk Management
Vendor assessment models: templates, assessments, results, evidence.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from core.models.base import VersionedEntity, TenantScoped, generate_uuid_str


class AssessmentTemplate(VersionedEntity, TenantScoped):
    """Reusable assessment questionnaire template."""
    __tablename__ = 'assessment_templates'

    assessment_type = Column(String, nullable=False)  # security, privacy, financial, operational
    name = Column(String, nullable=False)
    description = Column(Text)
    questions = Column(JSON)        # {q_id: {text, weight, options: []}}
    scoring_rubric = Column(JSON)   # scoring logic per question

    # Risk thresholds (score 0-100)
    critical_threshold = Column(Float, default=85.0)
    high_threshold = Column(Float, default=70.0)
    medium_threshold = Column(Float, default=50.0)


class VendorRiskAssessment(VersionedEntity, TenantScoped):
    """Full vendor assessment lifecycle record (Phase 2 – richer than Phase 1 VendorAssessment)."""
    __tablename__ = 'vendor_risk_assessments'

    vendor_id = Column(String, ForeignKey('assets.id'), nullable=False, index=True)
    assessment_type = Column(String, nullable=False)   # security, privacy, financial, operational
    framework = Column(String)                          # ISO27001, SOC2, NIST, Custom
    template_id = Column(String, ForeignKey('assessment_templates.id'), nullable=True)

    # Status
    status = Column(String, default='draft')  # draft, in_progress, completed, approved, conditional, blocked
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)

    # Scoring
    risk_score = Column(Float, nullable=True)    # 0-100
    risk_level = Column(String, nullable=True)   # low, medium, high, critical

    # Assessment details
    assessor_id = Column(String, nullable=True)
    attestation_document = Column(String, nullable=True)  # File path

    # Evidence & findings
    findings = Column(JSON, default=list)           # [{"issue": ..., "severity": ...}]
    recommendations = Column(JSON, default=list)    # [{"action": ..., "priority": ...}]

    # Renewal
    expiry_date = Column(DateTime, nullable=True)
    renewal_triggered_at = Column(DateTime, nullable=True)

    # Relationships
    vendor = relationship('Vendor', foreign_keys=[vendor_id])
    results = relationship('AssessmentResult', back_populates='assessment', cascade='all, delete-orphan')
    evidence_items = relationship('AssessmentEvidence', back_populates='assessment', cascade='all, delete-orphan')
    template = relationship('AssessmentTemplate', foreign_keys=[template_id])

    __table_args__ = (
        Index('ix_vendor_risk_assessments_vendor_type', 'vendor_id', 'assessment_type'),
        Index('ix_vendor_risk_assessments_status', 'status'),
    )


class AssessmentResult(VersionedEntity, TenantScoped):
    """Individual question answer within an assessment."""
    __tablename__ = 'assessment_results'

    assessment_id = Column(String, ForeignKey('vendor_risk_assessments.id'), nullable=False, index=True)
    question_id = Column(String, nullable=False)
    answer = Column(String)       # Answer text
    score = Column(Float)         # 0-10 raw score
    weight = Column(Float, default=1.0)
    evidence = Column(Text)       # Supporting evidence text

    assessment = relationship('VendorRiskAssessment', back_populates='results')


class AssessmentEvidence(VersionedEntity, TenantScoped):
    """Documents and certificates attached to an assessment."""
    __tablename__ = 'assessment_evidence'

    assessment_id = Column(String, ForeignKey('vendor_risk_assessments.id'), nullable=False, index=True)
    evidence_type = Column(String, nullable=False)  # document, certificate, audit_report, attestation
    title = Column(String, nullable=False)
    file_path = Column(String)
    file_hash = Column(String)  # SHA256 for tamper-evidence

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String)
    expires_at = Column(DateTime, nullable=True)

    assessment = relationship('VendorRiskAssessment', back_populates='evidence_items')


class SOC2Certificate(VersionedEntity, TenantScoped):
    """SOC 2 certificate tracking (Type I / Type II)."""
    __tablename__ = 'soc2_certificates'

    vendor_id = Column(String, ForeignKey('assets.id'), nullable=False, index=True)
    soc2_type = Column(String, nullable=False)       # Type_I, Type_II
    audit_firm = Column(String)
    report_period_start = Column(DateTime)
    report_period_end = Column(DateTime)
    issued_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=True)
    report_path = Column(String)                      # File path to report
    is_current = Column(Boolean, default=True)

    vendor = relationship('Vendor', foreign_keys=[vendor_id])

    __table_args__ = (
        Index('ix_soc2_vendor', 'vendor_id', 'soc2_type'),
    )
