from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SourcedField(BaseModel):
    value: Any
    confidence: float = 100.0  # 0 to 100
    source: str = "Unspecified"

class OrganizationInfo(BaseModel):
    name: SourcedField = Field(default_factory=lambda: SourcedField(value="Kids Help Phone", source="Terms of Reference"))
    entities: SourcedField = Field(default_factory=lambda: SourcedField(value=["KHP", "KHP Foundation"], source="Terms of Reference"))
    sector: SourcedField = Field(default_factory=lambda: SourcedField(value="Non-profit / Mental health crisis services", source="Terms of Reference"))
    populations_served: SourcedField = Field(default_factory=lambda: SourcedField(value=["youth", "service users", "donors", "staff", "volunteers"], source="Data Governance Policy"))

class GovernanceInfo(BaseModel):
    committee: SourcedField = Field(default_factory=lambda: SourcedField(value="Privacy, Security & Risk (PSR) Committee", source="Terms of Reference"))
    established: SourcedField = Field(default_factory=lambda: SourcedField(value="2020-02", source="Terms of Reference"))
    chair_role: SourcedField = Field(default_factory=lambda: SourcedField(value="Chief Privacy Officer", source="Terms of Reference"))
    roles: SourcedField = Field(default_factory=lambda: SourcedField(
        value=["Chair/CPO", "PSR Committee Member", "PSR Advisory Member", "Data Steward", "Data Administrator", "Data User"],
        source="Terms of Reference"
    ))
    reporting_to: SourcedField = Field(default_factory=lambda: SourcedField(value="IRMC", source="Terms of Reference"))
    cadence: SourcedField = Field(default_factory=lambda: SourcedField(
        value={
            "committee": "weekly",
            "advisory": "bi-monthly",
            "regulatory_update": "quarterly",
            "program_review": "annual"
        },
        source="Terms of Reference"
    ))
    review_cycle_years: SourcedField = Field(default_factory=lambda: SourcedField(value=2, source="Terms of Reference"))

class RegulatoryScope(BaseModel):
    federal: SourcedField = Field(default_factory=lambda: SourcedField(value=["PIPEDA"], source="Data Governance Policy"))
    provincial: SourcedField = Field(default_factory=lambda: SourcedField(value=["Alberta PIPA", "BC PIPA", "Quebec Law 25"], source="Data Governance Policy"))
    handles_foi: SourcedField = Field(default_factory=lambda: SourcedField(value=True, source="Data Governance Policy"))
    breach_notification: SourcedField = Field(default_factory=lambda: SourcedField(value="provincial + PIPEDA", source="Data Governance Policy"))
    cross_border: SourcedField = Field(default_factory=lambda: SourcedField(value=True, source="Data Governance Policy"))

class PolicyItem(BaseModel):
    name: str
    version: str
    owner: str
    status: str
    review: str
    citation: str
    confidence: float = 100.0

class VendorItem(BaseModel):
    name: str
    service: str
    data_types: str
    storage: str
    retention: str
    dpa_status: str
    citation: str
    confidence: float = 100.0

class DataInventoryItem(BaseModel):
    team: str
    asset: str
    owner: str
    storage: str
    retention: str
    disposal: str
    citation: str
    confidence: float = 100.0

class OrganizationalProfile(BaseModel):
    organization: OrganizationInfo = Field(default_factory=OrganizationInfo)
    governance: GovernanceInfo = Field(default_factory=GovernanceInfo)
    regulatory_scope: RegulatoryScope = Field(default_factory=RegulatoryScope)
    policies: List[PolicyItem] = Field(default_factory=list)
    vendors: List[VendorItem] = Field(default_factory=list)
    data_inventory: List[DataInventoryItem] = Field(default_factory=list)
    
    consent_practices: SourcedField = Field(default_factory=lambda: SourcedField(
        value={
            "model": "informed consent, revocable",
            "sensitive_data": "explicit consent required"
        },
        source="Data Governance Policy"
    ))
    ai_usage: SourcedField = Field(default_factory=lambda: SourcedField(
        value={
            "detected": [],
            "automated_decision_making": None
        },
        source="Website Crawl"
    ))
    security_controls: SourcedField = Field(default_factory=lambda: SourcedField(
        value={
            "pseudonymization": True,
            "encryption": True
        },
        source="Data Governance Policy RoPA section"
    ))
    completeness_pct: int = 0
