import os
import sys
import json
import yaml
import datetime
import uuid
from mcp.server.fastmcp import FastMCP
from kibo_surface import KiboSurface

# Initialize FastMCP server
mcp = FastMCP("KIBO-OS")

# Workspace root
WORKSPACE_DIR = "/Users/iceman/Documents/Code/Kibo"

def get_surface():
    return KiboSurface(WORKSPACE_DIR)

def enforce_checks(client_name: str, action_type: str = "write", target_uri: str = "kibo://company/profile", specific_grant: str = None):
    """
    Enforces state contracts and scope checks.
    """
    surface = get_surface()
    
    # 1. State Contract Checks (forces read-only if any state file is missing)
    # Get all mapped paths
    uri_mappings = surface.config.get("uri_mappings", {})
    missing_files = []
    
    # Required core state files that must exist for system to be operational (not down-state)
    core_state_uris = [
        "kibo://company/profile",
        "kibo://brand/category",
        "kibo://growth/pipeline",
        "kibo://catalog",
        "kibo://autonomy/grants",
        "kibo://deployability/ladder",
        "kibo://corrections",
        "kibo://feedback/log",
        "kibo://evals/scores",
        "kibo://prompt/active"
    ]
    
    for uri in core_state_uris:
        if uri in uri_mappings:
            path = os.path.join(WORKSPACE_DIR, uri_mappings[uri])
            if not os.path.exists(path):
                missing_files.append(uri)
                
    if missing_files:
        if action_type == "write":
            raise ValueError(f"State contract violation: Missing state files {missing_files}. System is in read-only mode.")
            
    # 2. Section 8 Scope Checks (Data Grant Verification)
    if surface.config.get("surface_rules", {}).get("verify_grant_before_client_touch", False):
        grants_path = os.path.join(WORKSPACE_DIR, ".kibo/state/autonomy/grants.json")
        if not os.path.exists(grants_path):
            raise PermissionError("Access Denied: Grants file is missing.")
            
        with open(grants_path, 'r') as f:
            grants = json.load(f)
            
        if client_name not in grants:
            raise PermissionError(f"Access Denied: No grants found for client '{client_name}'.")
            
        client_grants = grants[client_name]
        
        # If a specific permission key is requested, verify it is true
        if specific_grant:
            if not client_grants.get(specific_grant, False):
                raise PermissionError(f"Access Denied: Client '{client_name}' lacks specific grant '{specific_grant}'.")
        else:
            # Otherwise check if the client has at least one active (True) permission
            if not any(client_grants.values()):
                raise PermissionError(f"Access Denied: Client '{client_name}' has no active grants.")

# --- Expose every kibo:// resource ---
@mcp.resource("kibo://{category}")
def resolve_category_resource(category: str) -> str:
    uri = f"kibo://{category}"
    return read_resource_content(uri)

@mcp.resource("kibo://{category}/{name}")
def resolve_nested_resource(category: str, name: str) -> str:
    uri = f"kibo://{category}/{name}"
    return read_resource_content(uri)

def read_resource_content(uri: str) -> str:
    surface = get_surface()
    try:
        resolved_path = surface.resolve_uri(uri)
    except ValueError as e:
        raise FileNotFoundError(str(e))
        
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Resource file not found at: {resolved_path}")
        
    if os.path.isdir(resolved_path):
        # Return listing for directories
        files = os.listdir(resolved_path)
        return json.dumps({"directory": resolved_path, "contents": files}, indent=2)
        
    # Read files based on extension
    _, ext = os.path.splitext(resolved_path)
    with open(resolved_path, 'r') as f:
        content = f.read()
        
    # Standard format conversion (YAML/JSON validation)
    if ext in ['.yaml', '.yml']:
        # Return formatted YAML
        data = yaml.safe_load(content)
        return yaml.safe_dump(data, sort_keys=False)
    elif ext == '.json':
        data = json.loads(content)
        return json.dumps(data, indent=2)
    else:
        return content

# Dynamically register all URI mappings as resources
def register_dynamic_resources(mcp, workspace_dir):
    surface = KiboSurface(workspace_dir)
    uri_mappings = surface.config.get("uri_mappings", {})
    
    for uri in uri_mappings.keys():
        def make_resolver(target_uri):
            def resolver() -> str:
                return read_resource_content(target_uri)
            return resolver
        
        resolver_func = make_resolver(uri)
        # Unique function name for each registration
        resolver_func.__name__ = f"resolve_{uri.replace('://', '_').replace('/', '_').replace('-', '_').replace('.', '_')}"
        mcp.resource(uri)(resolver_func)

register_dynamic_resources(mcp, WORKSPACE_DIR)

# --- Tools Implementation (§11) ---

@mcp.tool(name="resource.write")
def resource_write(client_name: str, uri: str, content: str) -> str:
    """
    Writes content to a kibo:// resource.
    """
    enforce_checks(client_name, action_type="write", target_uri=uri)
    
    surface = get_surface()
    try:
        resolved_path = surface.resolve_uri(uri)
    except ValueError as e:
        raise ValueError(str(e))
        
    _, ext = os.path.splitext(resolved_path)
    try:
        if ext in ['.yaml', '.yml']:
            data = yaml.safe_load(content)
            with open(resolved_path, 'w') as f:
                yaml.safe_dump(data, f, sort_keys=False)
        elif ext == '.json':
            data = json.loads(content)
            with open(resolved_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif ext == '.jsonl':
            for line in content.splitlines():
                if line.strip():
                    json.loads(line)
            with open(resolved_path, 'w') as f:
                f.write(content)
        else:
            with open(resolved_path, 'w') as f:
                f.write(content)
    except Exception as e:
        raise ValueError(f"Failed to write resource content in format {ext}: {str(e)}")
        
    return f"Successfully wrote content to resource: {uri}"

@mcp.tool(name="queue.for_human")
def queue_for_human(client_name: str, action: str, task_id: str = None, details: str = None) -> str:
    """
    Manages the human judgment queue (queue.for_human).
    action: 'list', 'push', or 'resolve'
    """
    action_type = "read" if action == "list" else "write"
    enforce_checks(client_name, action_type=action_type)
    
    queue_path = os.path.join(WORKSPACE_DIR, ".kibo/state/queue.json")
    
    if os.path.exists(queue_path):
        with open(queue_path, 'r') as f:
            q_data = json.load(f)
    else:
        q_data = {"queue": []}
        
    queue = q_data.get("queue", [])
    
    if action == "list":
        return json.dumps(queue, indent=2)
        
    elif action == "push":
        if not details:
            raise ValueError("Details are required to push to queue.")
        t_id = task_id or f"task_{str(uuid.uuid4())[:8]}"
        task = {
            "id": t_id,
            "status": "pending",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "details": details
        }
        queue.append(task)
        q_data["queue"] = queue
        with open(queue_path, 'w') as f:
            json.dump(q_data, f, indent=2)
        return f"Successfully pushed task {t_id} to judgment queue."
        
    elif action == "resolve":
        if not task_id:
            raise ValueError("task_id is required to resolve a task.")
        found = False
        for task in queue:
            if task.get("id") == task_id:
                task["status"] = "resolved"
                task["resolved_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                found = True
                break
        if not found:
            return f"Task ID {task_id} not found in the queue."
            
        q_data["queue"] = queue
        with open(queue_path, 'w') as f:
            json.dump(q_data, f, indent=2)
        return f"Successfully resolved task {task_id}."
        
    else:
        raise ValueError(f"Unknown action: {action}")

@mcp.tool(name="feedback.log")
def feedback_log(client_name: str, category: str, description: str, evidence: str, rubric_assessment: str) -> str:
    """
    Appends a new feedback entry to feedback/log.md.
    """
    enforce_checks(client_name, action_type="write")
    
    feedback_path = os.path.join(WORKSPACE_DIR, ".kibo/state/feedback/log.md")
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    fb_id = f"FB-{datetime.datetime.utcnow().strftime('%Y')}-{str(uuid.uuid4())[:4].upper()}"
    
    entry_md = f"""
## [{timestamp}] {fb_id} ({category})
- **Source:** {client_name}
- **Category:** {category}
- **Description:** {description}
- **Rubric Assessment:** {rubric_assessment}
- **Evidence:** {evidence}
"""
    with open(feedback_path, 'a') as f:
        f.write(entry_md)
        
    return f"Successfully recorded feedback with ID: {fb_id}"

@mcp.tool(name="eval.score")
def eval_score(client_name: str, feedback_id: str, boundary_violation: bool, claim_integrity: bool, performance: float, governance: float, operational: float) -> str:
    """
    Records an evaluation score in evals/scores.json.
    """
    enforce_checks(client_name, action_type="write")
    
    scores_path = os.path.join(WORKSPACE_DIR, ".kibo/state/evals/scores.json")
    if os.path.exists(scores_path):
        with open(scores_path, 'r') as f:
            data = json.load(f)
    else:
        data = {"scores": []}
        
    overall_score = round((performance + governance + operational) / 3.0, 2)
    score_record = {
        "feedback_id": feedback_id,
        "boundary_violation": boundary_violation,
        "claim_integrity": claim_integrity,
        "scores": {
            "performance": performance,
            "governance": governance,
            "operational": operational
        },
        "overall_score": overall_score
    }
    
    data["scores"].append(score_record)
    with open(scores_path, 'w') as f:
        json.dump(data, f, indent=2)
        
    return f"Successfully saved evaluation score for {feedback_id} (Overall Score: {overall_score})."

@mcp.tool(name="proposal.write")
def proposal_write(client_name: str, id: str, target: str, rationale: str, diff: str, evidence: list, expected_effect: dict, semver_bump: str, status: str) -> str:
    """
    Submits a new draft proposal.
    Enforces scope checks: status must not be 'promoted', and evidence must not be empty.
    """
    enforce_checks(client_name, action_type="write")
    
    if status == "promoted":
        raise ValueError("Scope check violation: Proposals cannot be auto-promoted (status must be 'proposed' or 'reviewed').")
    if not evidence or len(evidence) == 0:
        raise ValueError("Scope check violation: Proposals must contain supporting evidence.")
        
    proposal_dir = os.path.join(WORKSPACE_DIR, ".kibo/state/proposals/draft")
    os.makedirs(proposal_dir, exist_ok=True)
    
    proposal_path = os.path.join(proposal_dir, f"{id}.json")
    
    proposal_data = {
        "id": id,
        "target": target,
        "rationale": rationale,
        "diff": diff,
        "evidence": evidence,
        "expected_effect": expected_effect,
        "semver_bump": semver_bump,
        "status": status
    }
    
    with open(proposal_path, 'w') as f:
        json.dump(proposal_data, f, indent=2)
        
    return f"Successfully wrote draft proposal {id} to {proposal_path}."

@mcp.tool(name="crew.dispatch")
def crew_dispatch(client_name: str, crew_name: str, action: str) -> str:
    """
    Crew dispatcher. Loads respective crew's skill from .agents/skills/<crew_name>/SKILL.md,
    checks W-Method deployment flow, and routes to queue.for_human if gated by a human.
    """
    enforce_checks(client_name, action_type="write")
    
    # Load skill configuration
    skill_path = os.path.join(WORKSPACE_DIR, f".agents/skills/{crew_name}/SKILL.md")
    skill_content = ""
    if os.path.exists(skill_path):
        with open(skill_path, 'r') as f:
            skill_content = f.read()
            
    # Read W-Method deployment flow
    flow_path = os.path.join(WORKSPACE_DIR, ".kibo/config/deployment-flow.yaml")
    with open(flow_path, 'r') as f:
        flow_data = yaml.safe_load(f)
        
    steps = flow_data.get("deployment_flow", {}).get("steps", {})
    matching_step = None
    for step_num, step_info in steps.items():
         if step_info.get("crew") == crew_name:
             matching_step = step_info
             break
             
    if not matching_step:
        return f"Crew '{crew_name}' successfully executed action '{action}' (no W-Method step found)."
        
    gate_type = matching_step.get("gate_type")
    gate_name = matching_step.get("gate")
    step_name = matching_step.get("name")
    
    if gate_type == "human":
        # Route human gate task to queue.for_human
        details = f"Approve W-Method step '{step_name}' ({gate_name}) by crew '{crew_name}' for action: {action}"
        task_id = f"task_{crew_name}_{step_name.lower().replace(' ', '_')}"
        queue_for_human(
            client_name=client_name,
            action="push",
            task_id=task_id,
            details=details
        )
        return f"WARNING: Dispatch blocked by W-Method step '{step_name}' human gate ({gate_name}). Human gate task '{task_id}' has been pushed to queue.for_human."
    else:
        return f"Successfully dispatched crew '{crew_name}' for W-Method step '{step_name}'. Action '{action}' complete."

if __name__ == '__main__':
    mcp.run()
