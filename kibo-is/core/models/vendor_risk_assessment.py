from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.models.base import Base, Timestamped

class Vendor(Base, Timestamped):
    __tablename__ = 'vendors'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    website = Column(String)
    # Relationships
    assessments = relationship('RiskAssessment', back_populates='vendor', cascade='all, delete-orphan')

class RiskAssessment(Base, Timestamped):
    __tablename__ = 'risk_assessments'
    id = Column(String, primary_key=True)
    vendor_id = Column(String, ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer)  # 0-100 risk score
    status = Column(String)  # e.g., pending, approved, rejected
    summary = Column(Text)
    # Relationships
    vendor = relationship('Vendor', back_populates='assessments')
    results = relationship('AssessmentResult', back_populates='assessment', cascade='all, delete-orphan')

class AssessmentResult(Base, Timestamped):
    __tablename__ = 'assessment_results'
    id = Column(String, primary_key=True)
    assessment_id = Column(String, ForeignKey('risk_assessments.id', ondelete='CASCADE'), nullable=False)
    category = Column(String)  # Security, Privacy, Financial, etc.
    rating = Column(Integer)   # 0-10 per category
    notes = Column(Text)
    assessment = relationship('RiskAssessment', back_populates='results')
