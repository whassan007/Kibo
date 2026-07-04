import sqlite3
import json
import random
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END

# Guardrails definition
ALLOWED_ADAPTATION_DOMAINS = [
    "tooltip_text_updates",
    "risk_weight_tuning",
    "sla_threshold_adjustments",
    "rule_engine_conditions",
]

class KiboState(TypedDict):
    current_framework: str      # E.g., "PIPEDA + Quebec Law 25"
    trigger_type: str           # "Regulatory_Update" or "User_Friction"
    trigger_data: str           # Telemetry or legal text
    proposed_logic_update: Optional[str]
    proposed_ui_schema: Optional[str]
    evaluation_score: int
    is_approved: bool
    loop_count: int
    logs: List[str]
    # Guardrail fields
    domain: str                 # Domain of proposed change
    decision: str               # "APPROVED", "REJECTED", "REJECTED_OUT_OF_BOUNDS", "SYSTEM_FATIGUE"
    justification: str          # Justification for decision

def analyze_trigger(state: KiboState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    loop_count = state.get("loop_count", 0) + 1
    
    logs.append(f"[Analysis Phase] Loop #{loop_count}: Ingesting trigger data ({state['trigger_type']}) under {state['current_framework']}.")
    
    # RAG Retrieval from legal_ground_truth database
    retrieved_clauses = []
    try:
        conn = sqlite3.connect("kibo_state.db")
        cursor = conn.cursor()
        cursor.execute("SELECT clause_id, legislation, clause_text, keywords FROM legal_ground_truth")
        all_clauses = cursor.fetchall()
        conn.close()
        
        trigger_lower = state["trigger_data"].lower()
        for cid, leg, text, keywords in all_clauses:
            for kw in keywords.split(","):
                if kw.strip().lower() in trigger_lower:
                    retrieved_clauses.append((cid, leg, text))
                    break
    except Exception as e:
        logs.append(f"[RAG Engine] Warning: could not access legal library ({str(e)})")
        
    if retrieved_clauses:
        logs.append(f"[RAG Engine] Successfully retrieved {len(retrieved_clauses)} grounded clauses: {', '.join([c[0] for c in retrieved_clauses])}")
        legal_context = "\n".join([f"[{c[0]} ({c[1]})]: {c[2]}" for c in retrieved_clauses])
        logs.append(f"[RAG Context Bound]: Using legal context for adaptation formulation.")
    else:
        logs.append(f"[RAG Engine] WARNING: No matching ground truth clauses found. Escalating to human legal review.")
        legal_context = "NO COVERAGE FOUND - REQUIRE HUMAN REVIEW"
        
    # Determine proposed domain based on trigger contents (to test out-of-bounds guardrail)
    proposed_domain = "risk_weight_tuning"
    if "create component" in trigger_lower or "react" in trigger_lower or "write code" in trigger_lower:
        proposed_domain = "core_platform_code" # Out-of-bounds!
    elif "sla" in trigger_lower:
        proposed_domain = "sla_threshold_adjustments"
    elif "tooltip" in trigger_lower:
        proposed_domain = "tooltip_text_updates"
        
    # Simulate adaptation generation with strict RAG context
    if "REQUIRE HUMAN REVIEW" in legal_context:
        logic = "HUMAN REVIEW REQUIRED - Adaptation halted due to missing legal safeguards in ground truth."
        ui = "{}"
    elif state["trigger_type"] == "Regulatory_Update":
        logic = f"Inject strict Law 25 consent parameters. Enable automated bilingual compliance templates for campaigns (Grounded in LAW25-SEC14)."
        ui = json.dumps({
            "elements": [
                {"type": "Checkbox", "id": "law25_bilingual_opt_in", "label": "Bilingual consent verification", "mandatory": True}
            ]
        })
    else: # User_Friction
        logic = f"Reduce vendor form validations. Automate DPA status matching via contract scan telemetry (Grounded in GDPR-ART28)."
        ui = json.dumps({
            "elements": [
                {"type": "Form", "id": "vendor_simplified", "fields": ["name", "service", "dpa_status"], "auto_populate": True}
            ]
        })
        
    logs.append(f"[Analysis Phase] Generated logic adaptation in domain '{proposed_domain}': \"{logic}\"")
    logs.append(f"[Analysis Phase] Generated UI adaptation schema: \"{ui}\"")
    
    return {
        "proposed_logic_update": logic,
        "proposed_ui_schema": ui,
        "loop_count": loop_count,
        "domain": proposed_domain,
        "logs": logs
    }

def evaluate_adaptation(state: KiboState) -> Dict[str, Any]:
    logs = list(state["logs"])
    loop_count = state["loop_count"]
    domain = state.get("domain", "risk_weight_tuning")
    
    logs.append(f"[Evaluation Phase] Conducting self-critique on proposed changes in domain '{domain}'...")
    
    # 1. Feature-Creep Rejector (Evaluation Gatekeeper)
    if domain not in ALLOWED_ADAPTATION_DOMAINS:
        logs.append(f"[Evaluation Phase] CRITICAL: Proposed change in domain '{domain}' is OUT OF BOUNDS. Adaptation blocked.")
        return {
            "evaluation_score": 0,
            "is_approved": False,
            "decision": "REJECTED_OUT_OF_BOUNDS",
            "justification": f"CRITICAL: Agent attempted to modify core platform features ('{domain}') or execute arbitrary code. Adaptation blocked.",
            "logs": logs
        }
        
    # 2. Retry Fatigue Limit
    if loop_count >= 3:
        logs.append("[Evaluation Phase] SYSTEM FATIGUE: Retry limit of 3 exceeded. Escalating to human CPO.")
        return {
            "evaluation_score": 0,
            "is_approved": False,
            "decision": "SYSTEM_FATIGUE",
            "justification": "System loop fatigue: 3 adaptation loops failed to reach approval threshold.",
            "logs": logs
        }
        
    # First loop fails to simulate improvement cycles, second loop succeeds
    if loop_count < 2:
        score = 6
        is_approved = False
        decision = "REJECTED"
        justification = "Legal audit detected missing audit log schema. Re-routing back to Analysis."
        logs.append(f"[Evaluation Phase] Score: {score}/10 - {decision}. {justification}")
    else:
        score = 9
        is_approved = True
        decision = "APPROVED"
        justification = "All safety constraints and UX friction checks passed."
        logs.append(f"[Evaluation Phase] Score: {score}/10 - {decision}. {justification}")
        
    return {
        "evaluation_score": score,
        "is_approved": is_approved,
        "decision": decision,
        "justification": justification,
        "logs": logs
    }

def deploy_update(state: KiboState) -> Dict[str, Any]:
    logs = list(state["logs"])
    logs.append(f"[Deployment Phase] Saving new adaptation schemas to kibo_state.db and reloading gateways.")
    
    try:
        conn = sqlite3.connect("kibo_state.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS agent_deployments (deployment_id INTEGER PRIMARY KEY AUTOINCREMENT, logic_update TEXT, ui_schema TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        cursor.execute("INSERT INTO agent_deployments (logic_update, ui_schema) VALUES (?, ?)", (state["proposed_logic_update"], state["proposed_ui_schema"]))
        conn.commit()
        conn.close()
        logs.append(f"[Deployment Phase] Production deployment complete. Framework successfully re-calibrated.")
    except Exception as e:
        logs.append(f"[Deployment Phase] Error writing deployment to database: {str(e)}")
        
    return {
        "logs": logs
    }

def route_evaluation(state: KiboState) -> str:
    decision = state.get("decision")
    if decision == "APPROVED":
        return "deploy"
    elif decision in ["REJECTED_OUT_OF_BOUNDS", "SYSTEM_FATIGUE"]:
        return "route_to_human_cpo"
    else:
        return "re_analyze"

def get_self_improvement_flow():
    workflow = StateGraph(KiboState)
    
    workflow.add_node("Analyze", analyze_trigger)
    workflow.add_node("Evaluate", evaluate_adaptation)
    workflow.add_node("Deploy", deploy_update)
    
    workflow.set_entry_point("Analyze")
    workflow.add_edge("Analyze", "Evaluate")
    
    workflow.add_conditional_edges(
        "Evaluate",
        route_evaluation,
        {
            "deploy": "Deploy",
            "route_to_human_cpo": END,
            "re_analyze": "Analyze"
        }
    )
    workflow.add_edge("Deploy", END)
    
    return workflow.compile()

self_improvement_flow = get_self_improvement_flow()

def run_self_improvement(trigger_type: str, trigger_data: str, current_framework: str = "PIPEDA + Law 25") -> Dict[str, Any]:
    initial_state = {
        "current_framework": current_framework,
        "trigger_type": trigger_type,
        "trigger_data": trigger_data,
        "proposed_logic_update": None,
        "proposed_ui_schema": None,
        "evaluation_score": 0,
        "is_approved": False,
        "loop_count": 0,
        "logs": [],
        "domain": "risk_weight_tuning",
        "decision": "pending",
        "justification": ""
    }
    
    result = self_improvement_flow.invoke(initial_state)
    return result
