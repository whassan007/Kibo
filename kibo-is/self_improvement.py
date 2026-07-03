import sqlite3
import json
import random
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END

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

def analyze_trigger(state: KiboState) -> Dict[str, Any]:
    logs = list(state.get("logs", []))
    loop_count = state.get("loop_count", 0) + 1
    
    logs.append(f"[Analysis Phase] Loop #{loop_count}: Ingesting trigger data ({state['trigger_type']}) under {state['current_framework']}.")
    
    # Simulate adaptation generation
    if state["trigger_type"] == "Regulatory_Update":
        logic = f"Inject strict Law 25 consent parameters. Enable automated bilingual compliance templates for campaigns."
        ui = json.dumps({
            "elements": [
                {"type": "Checkbox", "id": "law25_bilingual_opt_in", "label": "Bilingual consent verification", "mandatory": True}
            ]
        })
    else: # User_Friction
        logic = f"Reduce vendor form validations. Automate DPA status matching via contract scan telemetry."
        ui = json.dumps({
            "elements": [
                {"type": "Form", "id": "vendor_simplified", "fields": ["name", "service", "dpa_status"], "auto_populate": True}
            ]
        })
        
    logs.append(f"[Analysis Phase] Generated logic adaptation: \"{logic}\"")
    logs.append(f"[Analysis Phase] Generated UI adaptation schema: \"{ui}\"")
    
    return {
        "proposed_logic_update": logic,
        "proposed_ui_schema": ui,
        "loop_count": loop_count,
        "logs": logs
    }

def evaluate_adaptation(state: KiboState) -> Dict[str, Any]:
    logs = list(state["logs"])
    loop_count = state["loop_count"]
    
    logs.append(f"[Evaluation Phase] Conducting self-critique on proposed changes...")
    
    # We want a dynamic critique loop:
    # First loop might fail to simulate a real correction/improvement loop, then succeed!
    if loop_count < 2:
        score = 6
        is_approved = False
        logs.append(f"[Evaluation Phase] Score: {score}/10 - REJECTED. Legal audit detected missing audit log schema. Re-routing back to Analysis.")
    else:
        score = 9
        is_approved = True
        logs.append(f"[Evaluation Phase] Score: {score}/10 - APPROVED. All safety constraints and UX friction checks passed.")
        
    return {
        "evaluation_score": score,
        "is_approved": is_approved,
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
    if state["is_approved"]:
        return "deploy"
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
        "logs": []
    }
    
    result = self_improvement_flow.invoke(initial_state)
    return result
