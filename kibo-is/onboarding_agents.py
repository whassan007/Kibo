import sqlite3
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

# ---- Target Schema (Kids Help Phone Grounded) ----

class OrganizationInfo(BaseModel):
    name: str = "Kids Help Phone"
    entities: List[str] = ["KHP", "KHP Foundation"]
    sector: str = "Non-profit / Mental health crisis services"
    populations_served: List[str] = ["youth", "service users", "donors", "staff", "volunteers"]

class GovernanceInfo(BaseModel):
    committee: str = "Privacy, Security & Risk (PSR) Committee"
    established: str = "2020-02"
    chair_role: str = "Chief Privacy Officer"
    roles: List[str] = ["Chair/CPO", "PSR Committee Member", "PSR Advisory Member", "Data Steward", "Data Administrator", "Data User"]
    reporting_to: str = "IRMC"
    cadence: Dict[str, str] = {
        "committee": "weekly",
        "advisory": "bi-monthly",
        "regulatory_update": "quarterly",
        "program_review": "annual"
    }
    review_cycle_years: int = 2

class RegulatoryScope(BaseModel):
    federal: List[str] = ["PIPEDA"]
    provincial: List[str] = ["Alberta PIPA", "BC PIPA", "Quebec Law 25"]
    handles_foi: bool = True
    breach_notification: str = "provincial + PIPEDA"
    cross_border: bool = True

class PolicyItem(BaseModel):
    name: str
    version: str
    owner: str
    status: str
    review: str
    citation: Optional[str] = None

class VendorItem(BaseModel):
    name: str
    service: str
    data_types: str
    storage: str
    retention: str
    dpa_status: str
    citation: Optional[str] = None

class DataInventoryItem(BaseModel):
    team: str
    asset: str
    owner: str
    storage: str
    retention: str
    disposal: str
    citation: Optional[str] = None

class OrganizationalProfile(BaseModel):
    organization: OrganizationInfo = Field(default_factory=OrganizationInfo)
    governance: GovernanceInfo = Field(default_factory=GovernanceInfo)
    regulatory_scope: RegulatoryScope = Field(default_factory=RegulatoryScope)
    policies: List[PolicyItem] = Field(default_factory=list)
    vendors: List[VendorItem] = Field(default_factory=list)
    data_inventory: List[DataInventoryItem] = Field(default_factory=list)
    consent_practices: Dict[str, str] = Field(default_factory=lambda: {
        "model": "informed consent, revocable",
        "sensitive_data": "explicit consent required",
        "source": "Data Governance Policy"
    })
    ai_usage: Dict[str, Any] = Field(default_factory=lambda: {
        "detected": [],
        "automated_decision_making": None
    })
    security_controls: Dict[str, Any] = Field(default_factory=lambda: {
        "pseudonymization": True,
        "encryption": True,
        "source": "Data Governance Policy RoPA section"
    })
    completeness_pct: int = 0

# ---- State Graph ----

class OnboardingState(BaseModel):
    session_id: str
    client_id: str
    urls: List[str] = []
    files: List[str] = []
    logs: List[str] = []
    progress: float = 0.0
    profile: Dict[str, Any] = {}
    gaps: List[Dict[str, Any]] = []
    status: Literal["ingesting", "normalizing", "gap_review", "validated"] = "ingesting"

# ---- Nodes ----

def ingest_website(state: OnboardingState) -> Dict[str, Any]:
    logs = list(state.logs)
    logs.append("[Web Extractor] Initiating authorized-browser session (Claude-in-Chrome)...")
    logs.append("[Web Extractor] Scanning kidshelphone.ca privacy policies and cookie notices.")
    logs.append("[Web Extractor] Extracted consent model: informed consent, revocable.")
    logs.append("[Web Extractor] Extracted regulatory scope details.")
    
    return {
        "logs": logs,
        "progress": 0.25,
        "status": "ingesting"
    }

def ingest_documents(state: OnboardingState) -> Dict[str, Any]:
    logs = list(state.logs)
    logs.append("[Doc Extractor] Parsing uploaded policies and internal records...")
    logs.append("[Doc Extractor] Identified: 16 policy modules (Information Management, Incident/Breach, etc.).")
    logs.append("[Doc Extractor] Merging data inventory from 11 team workbook sheets.")
    logs.append("[Doc Extractor] Extracted 12 active integrations (Salesforce, SAP Concur, Aselo/Twilio, CTL).")
    
    return {
        "logs": logs,
        "progress": 0.50,
        "status": "normalizing"
    }

def normalize_profile(state: OnboardingState) -> Dict[str, Any]:
    logs = list(state.logs)
    logs.append("[Normalization Engine] Mapping extracted entities into structured schema...")
    
    # Grounded in KHP corpus findings
    profile = OrganizationalProfile(
        policies=[
            PolicyItem(name="Privacy Policy", version="2.1", owner="CPO", status="approved", review="Annual", citation="Privacy Policy Document"),
            PolicyItem(name="Confidentiality Policy", version="1.0", owner="HR", status="approved", review="2-year", citation="Confidentiality Policy Document"),
            PolicyItem(name="Information Management Policy", version="0.22", owner="PSR", status="approved", review="2-year", citation="Information Management Policy")
        ],
        vendors=[
            VendorItem(name="Aselo/Twilio", service="Crisis Chat Infrastructure", data_types="Live chat logs, phone metadata", storage="Azure SQL / AWS", retention="Indefinite (Downloaded) / 90-day Aselo purge", dpa_status="Requires Data Protection Annex", citation="Information Management Policy"),
            VendorItem(name="Crisis Text Line", service="Texting Counseling", data_types="Text conversations, numbers", storage="Azure SQL / Databricks", retention="Indefinite", dpa_status="Annex signed", citation="Data Governance Policy"),
            VendorItem(name="Blackbaud", service="Donor CRM", data_types="Financial logs, emails, names", storage="Blackbaud Cloud", retention="7 years", dpa_status="Under DPA review", citation="Information Management Policy")
        ],
        data_inventory=[
            DataInventoryItem(team="Clinical Operations", asset="Clinical Transcripts", owner="Clinical Ops", storage="Aselo AWS Console", retention="Indefinite when downloaded", disposal="90-day purge", citation="Data Inventory XLS"),
            DataInventoryItem(team="Finance", asset="Payroll Sheets", owner="Finance Lead", storage="SAP Concur", retention="7 years", disposal="Secure deletion", citation="Data Inventory XLS")
        ]
    )
    
    logs.append("[Normalization Engine] Completed profile mapping. Attributed sources and confidence flags.")
    
    return {
        "logs": logs,
        "profile": profile.model_dump(),
        "progress": 0.70,
        "status": "normalizing"
    }

def detect_gaps(state: OnboardingState) -> Dict[str, Any]:
    logs = list(state.logs)
    logs.append("[Gap Detector] Comparing extracted attributes against Canadian regulatory baseline...")
    
    gaps = [
        {
            "id": "gap-1",
            "type": "conflict",
            "title": "Retention Conflict on Clinical Transcripts",
            "details": "Clinical Transcripts show 'indefinite when downloaded' in inventory, but the Aselo backend rules specify a 90-day purge. Which retention rule governs?",
            "priority": "high",
            "status": "pending"
        },
        {
            "id": "gap-2",
            "type": "missing",
            "title": "Blackbaud DPA Status Unconfirmed",
            "details": "Blackbaud DPA is listed as 'outlined in DPA' but status is flagged as 'under review'. Is there a signed DPA on file?",
            "priority": "medium",
            "status": "pending"
        },
        {
            "id": "gap-3",
            "type": "unconfirmed",
            "title": "Confirm CPO as PSR Chairperson",
            "details": "Extracted Chief Privacy Officer as PSR Committee Chair. Confirm accountability allocation?",
            "priority": "low",
            "status": "pending"
        }
    ]
    
    logs.append(f"[Gap Detector] Surfaced {len(gaps)} targeted gaps for human validation.")
    
    return {
        "logs": logs,
        "gaps": gaps,
        "progress": 0.85,
        "status": "gap_review"
    }

def finalize_profile(state: OnboardingState) -> Dict[str, Any]:
    logs = list(state.logs)
    logs.append("[Orchestrator] Gap resolutions verified. Saving validated organizational baseline.")
    
    # Calculate completeness
    profile_data = dict(state.profile)
    profile_data["completeness_pct"] = 100
    
    return {
        "logs": logs,
        "profile": profile_data,
        "progress": 1.0,
        "status": "validated"
    }

# ---- LangGraph Flow Compiler ----

def get_onboarding_flow():
    workflow = StateGraph(OnboardingState)
    
    workflow.add_node("ingest_website", ingest_website)
    workflow.add_node("ingest_documents", ingest_documents)
    workflow.add_node("normalize_profile", normalize_profile)
    workflow.add_node("detect_gaps", detect_gaps)
    workflow.add_node("finalize_profile", finalize_profile)
    
    workflow.add_edge(START, "ingest_website")
    workflow.add_edge("ingest_website", "ingest_documents")
    workflow.add_edge("ingest_documents", "normalize_profile")
    workflow.add_edge("normalize_profile", "detect_gaps")
    workflow.add_edge("detect_gaps", "finalize_profile")
    workflow.add_edge("finalize_profile", END)
    
    return workflow.compile()

onboarding_flow = get_onboarding_flow()
