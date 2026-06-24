import sqlite3
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# State definition
class OnboardingState(TypedDict):
    client_id: str
    mode: str
    status: str
    logs: List[str]
    progress: float
    findings: List[Dict[str, Any]]
    answers: Optional[Dict[str, Any]]

# Define nodes for Website Discovery Graph
def web_triage(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Triage Agent] Crawling domain for corporate legal entities, subsidiaries, and physical locations."],
        "progress": 0.2,
        "status": "in_progress"
    }

def web_privacy_extract(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Privacy Discovery Agent] Extracting privacy policies, cookie controls, AI transparency notices, and parental consent paths."],
        "progress": 0.45,
        "status": "in_progress"
    }

def web_regulatory_analysis(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Regulatory Agent] Parsing CPRA, GDPR, HIPAA, and Quebec Law 25 applicability indicators."],
        "progress": 0.70,
        "status": "in_progress"
    }

def web_tech_scan(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Tech Stack Agent] Mapping tracking pixels, cookie banner configuration, chatbots, and Consent Management Platforms."],
        "progress": 0.90,
        "status": "in_progress"
    }

# Document subgraphs
def doc_ingest(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Privacy Discovery Agent] Ingesting uploaded compliance docs, PIAs, risk assessments, and vendor contracts."],
        "progress": 0.35,
        "status": "in_progress"
    }

def doc_gap_assessment(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Regulatory Agent] Creating draft control framework, risk registry, and Gap Assessment Report."],
        "progress": 0.85,
        "status": "in_progress"
    }

# System subgraphs
def system_identity_scan(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Corporate Discovery Agent] Inventorying directory services: Active Directory, Okta, and Google Workspace user directories."],
        "progress": 0.30,
        "status": "in_progress"
    }

def system_cloud_scan(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Data Discovery Agent] Scanning AWS S3 buckets, Snowflake databases, and GCP BigQuery catalogs."],
        "progress": 0.65,
        "status": "in_progress"
    }

def system_flow_mapping(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Risk Discovery Agent] Mapping database retention schedules and compiling data flow diagrams."],
        "progress": 0.90,
        "status": "in_progress"
    }

# Guided subgraphs
def guided_evaluate(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Regulatory Agent] Inspecting CPO questionnaire answers for international data transfers and sensitive profiling."],
        "progress": 0.50,
        "status": "in_progress"
    }

def guided_map_obligations(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[Privacy Discovery Agent] Mapping responses to BIPA, COPPA, and GLBA compliance requirements."],
        "progress": 0.85,
        "status": "in_progress"
    }

# Final node
def compile_findings(state: OnboardingState) -> Dict[str, Any]:
    return {
        "logs": state.get("logs", []) + ["[System Orchestrator] Merging discover components into unified CPO dashboard registry."],
        "progress": 1.0,
        "status": "complete"
    }

# Compile Website Graph
web_graph = StateGraph(OnboardingState)
web_graph.add_node("triage", web_triage)
web_graph.add_node("privacy_extract", web_privacy_extract)
web_graph.add_node("regulatory_analysis", web_regulatory_analysis)
web_graph.add_node("tech_scan", web_tech_scan)
web_graph.add_node("compile", compile_findings)

web_graph.add_edge(START, "triage")
web_graph.add_edge("triage", "privacy_extract")
web_graph.add_edge("privacy_extract", "regulatory_analysis")
web_graph.add_edge("regulatory_analysis", "tech_scan")
web_graph.add_edge("tech_scan", "compile")
web_graph.add_edge("compile", END)
web_compiled = web_graph.compile()

# Compile Documents Graph
doc_graph = StateGraph(OnboardingState)
doc_graph.add_node("ingest", doc_ingest)
doc_graph.add_node("gap_assessment", doc_gap_assessment)
doc_graph.add_node("compile", compile_findings)

doc_graph.add_edge(START, "ingest")
doc_graph.add_edge("ingest", "gap_assessment")
doc_graph.add_edge("gap_assessment", "compile")
doc_graph.add_edge("compile", END)
doc_compiled = doc_graph.compile()

# Compile Systems Graph
sys_graph = StateGraph(OnboardingState)
sys_graph.add_node("identity_scan", system_identity_scan)
sys_graph.add_node("cloud_scan", system_cloud_scan)
sys_graph.add_node("flow_mapping", system_flow_mapping)
sys_graph.add_node("compile", compile_findings)

sys_graph.add_edge(START, "identity_scan")
sys_graph.add_edge("identity_scan", "cloud_scan")
sys_graph.add_edge("cloud_scan", "flow_mapping")
sys_graph.add_edge("flow_mapping", "compile")
sys_graph.add_edge("compile", END)
sys_compiled = sys_graph.compile()

# Compile Guided Graph
guided_graph = StateGraph(OnboardingState)
guided_graph.add_node("evaluate", guided_evaluate)
guided_graph.add_node("map_obligations", guided_map_obligations)
guided_graph.add_node("compile", compile_findings)

guided_graph.add_edge(START, "evaluate")
guided_graph.add_edge("evaluate", "map_obligations")
guided_graph.add_edge("map_obligations", "compile")
guided_graph.add_edge("compile", END)
guided_compiled = guided_graph.compile()
