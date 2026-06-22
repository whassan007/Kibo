import os
import sys
import json
import subprocess
import yaml
from jsonschema import validate, ValidationError
from kibo_surface import KiboSurface

# Schema definitions matching the KIBO OS scaffold structure
SCHEMAS = {
    'mcp-surface.yaml': {
        "type": "object",
        "properties": {
            "uri_mappings": {
                "type": "object",
                "additionalProperties": {"type": "string"}
            },
            "surface_rules": {
                "type": "object",
                "properties": {
                    "read_only_on_down_state": {"type": "boolean"},
                    "verify_grant_before_client_touch": {"type": "boolean"}
                },
                "required": ["read_only_on_down_state", "verify_grant_before_client_touch"]
            }
        },
        "required": ["uri_mappings", "surface_rules"]
    },
    'monitor.yaml': {
        "type": "object",
        "properties": {
            "monitor_drift_layer": {
                "type": "object",
                "properties": {
                    "triggers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "condition": {"type": "string"},
                                "action": {"type": "string"}
                            },
                            "required": ["name", "condition", "action"]
                        }
                    }
                },
                "required": ["triggers"]
            }
        },
        "required": ["monitor_drift_layer"]
    },
    'herald.yaml': {
        "type": "object",
        "properties": {
            "herald_crew": {
                "type": "object",
                "properties": {
                    "objective": {"type": "string"},
                    "brand_voice": {
                        "type": "object",
                        "properties": {
                            "category_exclusive": {"type": "boolean"},
                            "prevent_unverified_claims": {"type": "boolean"},
                            "use_placeholders": {"type": "boolean"}
                        },
                        "required": ["category_exclusive", "prevent_unverified_claims", "use_placeholders"]
                    },
                    "category_content": {
                        "type": "object",
                        "properties": {
                            "strategic_focus": {"type": "string"},
                            "proof_artifacts": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["strategic_focus", "proof_artifacts"]
                    },
                    "claim_library": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "claim": {"type": "string"},
                                "evidence_source": {"type": "string"},
                                "verified": {"type": "boolean"}
                            },
                            "required": ["claim", "evidence_source", "verified"]
                        }
                    }
                },
                "required": ["objective", "brand_voice", "category_content", "claim_library"]
            }
        },
        "required": ["herald_crew"]
    },
    'scout.yaml': {
        "type": "object",
        "properties": {
            "scout_crew": {
                "type": "object",
                "properties": {
                    "targets": {
                        "type": "object",
                        "properties": {
                            "primary_wedge": {"type": "string"},
                            "expansion_targets": {"type": "array", "items": {"type": "string"}},
                            "headcount_filter": {
                                "type": "object",
                                "properties": {
                                    "min_employees": {"type": "integer"},
                                    "max_employees": {"type": "integer"}
                                },
                                "required": ["min_employees", "max_employees"]
                            }
                        },
                        "required": ["primary_wedge", "expansion_targets", "headcount_filter"]
                    },
                    "qualification_rubric": {
                        "type": "object",
                        "properties": {
                            "inputs": {"type": "object"},
                            "formula": {"type": "string"},
                            "threshold": {"type": "number"}
                        },
                        "required": ["inputs", "formula", "threshold"]
                    },
                    "pe_channel_rubric": {
                        "type": "object"
                    }
                },
                "required": ["targets", "qualification_rubric", "pe_channel_rubric"]
            }
        },
        "required": ["scout_crew"]
    },
    'deployment-flow.yaml': {
        "type": "object",
        "properties": {
            "deployment_flow": {
                "type": "object",
                "properties": {
                    "steps": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "crew": {"type": "string"},
                                "gate": {"type": "string"},
                                "gate_type": {"type": "string", "enum": ["human", "artifact", "none"]}
                            },
                            "required": ["name", "crew", "gate", "gate_type"]
                        }
                    }
                },
                "required": ["steps"]
            }
        },
        "required": ["deployment_flow"]
    },
    'proposal-system.yaml': {
        "type": "object",
        "properties": {
            "proposal_system": {
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["object"]},
                            "properties": {"type": "object"},
                            "required": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["type", "properties", "required"]
                    },
                    "gates": {
                        "type": "object",
                        "properties": {
                            "promotion": {"type": "string"},
                            "validation": {"type": "string"}
                        },
                        "required": ["promotion", "validation"]
                    }
                },
                "required": ["schema", "gates"]
            }
        },
        "required": ["proposal_system"]
    },
    'company.yaml': {
        "type": "object",
        "properties": {
            "founder": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "credentials": {"type": "string"}
                },
                "required": ["name", "credentials"]
            },
            "product": {"type": "string"},
            "human_reserve": {"type": "array", "items": {"type": "string"}},
            "strategic_priorities": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["founder", "product", "human_reserve", "strategic_priorities"]
    },
    'brand.yaml': {
        "type": "object",
        "properties": {
            "brand": {"type": "string"},
            "tagline": {"type": "string"},
            "posture": {"type": "string"},
            "wedge": {"type": "string"},
            "channel": {"type": "string"},
            "gap_owned": {"type": "string"},
            "core_ip": {"type": "string"},
            "capture_model": {"type": "string"},
            "proof": {"type": "string"},
            "messaging": {
                "type": "object",
                "properties": {
                    "lead_with_mechanism": {"type": "string"},
                    "lead_with_governance": {"type": "string"}
                },
                "required": ["lead_with_mechanism", "lead_with_governance"]
            }
        },
        "required": ["brand", "tagline", "posture", "wedge", "channel", "gap_owned", "core_ip", "capture_model", "proof", "messaging"]
    },
    'catalog.yaml': {
        "type": "object",
        "properties": {
            "modules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "layer": {"type": "integer"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "reuse_count": {"type": "integer"},
                        "eval_score": {"type": "number"}
                    },
                    "required": ["id", "name", "layer", "description", "status"]
                }
            }
        },
        "required": ["modules"]
    },
    'corrections.yaml': {
        "type": "object",
        "properties": {
            "corrections": {
                "type": "array"
            }
        },
        "required": ["corrections"]
    },
    'prompt/active.yaml': {
        "type": "object",
        "properties": {
            "version": {"type": "string"},
            "thesis": {"type": "string"},
            "deployment_target": {"type": "string"},
            "last_updated": {"type": "string"},
            "status": {"type": "string"}
        },
        "required": ["version", "thesis", "deployment_target", "last_updated", "status"]
    },
    'autonomy/grants.json': {
        "type": "object",
        "additionalProperties": {
            "type": "object",
            "additionalProperties": {"type": "boolean"}
        }
    },
    'deployability/ladder.json': {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step": {"type": "string"},
                        "owner": {"type": "string"}
                    },
                    "required": ["step", "owner"]
                }
            }
        },
        "required": ["steps"]
    },
    'evals/scores.json': {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array"
            }
        },
        "required": ["scores"]
    },
    'growth/pipeline.jsonl': {
        "type": "object",
        "properties": {
            "client": {"type": "string"},
            "stage": {"type": "string"},
            "value": {"type": "number"}
        },
        "required": ["client", "stage"]
    }
}

def validate_schema(workspace_dir):
    failures = []
    
    # 1. Configs
    config_dir = os.path.join(workspace_dir, '.kibo/config')
    for filename in ['mcp-surface.yaml', 'monitor.yaml', 'herald.yaml', 'scout.yaml', 'deployment-flow.yaml', 'proposal-system.yaml']:
        file_path = os.path.join(config_dir, filename)
        if not os.path.exists(file_path):
            failures.append((filename, f"File does not exist: {file_path}"))
            continue
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            validate(instance=data, schema=SCHEMAS[filename])
        except Exception as e:
            failures.append((filename, str(e)))

    # 2. States
    state_dir = os.path.join(workspace_dir, '.kibo/state')
    for relative_path in ['company.yaml', 'brand.yaml', 'catalog.yaml', 'corrections.yaml', 'prompt/active.yaml', 'autonomy/grants.json', 'deployability/ladder.json', 'evals/scores.json', 'growth/pipeline.jsonl']:
        file_path = os.path.join(state_dir, relative_path)
        if not os.path.exists(file_path):
            failures.append((relative_path, f"File does not exist: {file_path}"))
            continue
        try:
            with open(file_path, 'r') as f:
                if relative_path.endswith('.yaml'):
                    data = yaml.safe_load(f)
                    validate(instance=data, schema=SCHEMAS[relative_path])
                elif relative_path.endswith('.json'):
                    data = json.load(f)
                    validate(instance=data, schema=SCHEMAS[relative_path])
                elif relative_path.endswith('.jsonl'):
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if line.strip():
                            data = json.loads(line)
                            validate(instance=data, schema=SCHEMAS[relative_path])
        except Exception as e:
            failures.append((relative_path, str(e)))

    return failures

def run_test_uri_sh(workspace_dir):
    try:
        script_path = os.path.join(workspace_dir, '.kibo/tools/test-uri.sh')
        res = subprocess.run(['bash', script_path], capture_output=True, text=True)
        return res.returncode == 0, res.stdout, res.stderr
    except Exception as e:
        return False, "", str(e)

def run_brief_sh(workspace_dir):
    try:
        script_path = os.path.join(workspace_dir, '.kibo/tools/brief.sh')
        res = subprocess.run(['bash', script_path, '--dry-run'], capture_output=True, text=True)
        if res.returncode != 0:
            return False, "Failed to run brief.sh", res.stderr
        
        output = res.stdout
        
        if "Cost-to-Acquire-and-Trust (CAC) per Deployment" not in output:
            return False, "Missing CAC per deployment KPI in brief output", output
        if "Human Gates (⟐) per Deployment" not in output:
            return False, "Missing Human Gates per deployment KPI in brief output", output
        
        cac_idx = output.find("Cost-to-Acquire-and-Trust (CAC) per Deployment")
        gates_idx = output.find("Human Gates (⟐) per Deployment")
        if cac_idx > gates_idx:
            return False, "KPI ordering is incorrect, CAC must lead gates", output
            
        return True, "Brief generated and KPIs correctly leading in markdown", output
    except Exception as e:
        return False, "Error executing brief.sh", str(e)

def run_state_contract_tests(workspace_dir):
    surface = KiboSurface(workspace_dir)
    original_mappings = surface.config['uri_mappings'].copy()
    
    mock_missing_uri = "kibo://mock/missing_file"
    surface.config['uri_mappings'][mock_missing_uri] = ".kibo/state/non_existent_file_test.yaml"
    
    write_allowed = surface.can_perform_action(
        client_name="scout",
        action_type="write",
        uri=mock_missing_uri
    )
    
    read_allowed = surface.can_perform_action(
        client_name="scout",
        action_type="read",
        uri=mock_missing_uri
    )
    
    surface.config['uri_mappings'] = original_mappings
    
    action_with_missing_grants = surface.can_perform_action(
        client_name="scout",
        action_type="write",
        uri="kibo://company/profile",
        mock_grants_missing=True
    )
    
    temp_grants_file = os.path.join(workspace_dir, '.kibo/state/autonomy/temp_grants.json')
    with open(temp_grants_file, 'w') as f:
        json.dump({"scout": {}}, f)
        
    action_with_empty_grants = surface.can_perform_action(
        client_name="scout",
        action_type="read",
        uri="kibo://company/profile",
        mock_grants_file_path=temp_grants_file
    )
    
    if os.path.exists(temp_grants_file):
        os.remove(temp_grants_file)
        
    down_state_write_blocked = (write_allowed == False)
    down_state_read_allowed = (read_allowed == True)
    missing_grant_blocked = (action_with_missing_grants == False)
    empty_grant_blocked = (action_with_empty_grants == False)
    
    success = down_state_write_blocked and down_state_read_allowed and missing_grant_blocked and empty_grant_blocked
    
    msgs = []
    msgs.append(f"Down-state write blocked: {down_state_write_blocked}")
    msgs.append(f"Down-state read allowed (forces read-only): {down_state_read_allowed}")
    msgs.append(f"Missing grants file blocks action: {missing_grant_blocked}")
    msgs.append(f"Empty client grants blocks action: {empty_grant_blocked}")
    
    return success, "\n".join(msgs)

def main():
    workspace_dir = '/Users/iceman/Documents/Code/Kibo'
    
    print("=" * 60)
    print("KIBO OS Scaffold Verification Suite - End-to-End")
    print("=" * 60)
    
    all_pass = True
    
    # 1. YAML/JSON Schema Validation
    print("\n[CHECK 1] YAML/JSON Schema Validation against specifications:")
    schema_failures = validate_schema(workspace_dir)
    if not schema_failures:
        print("  --> PASS: All YAML, JSON, and JSONL files match their schemas.")
    else:
        all_pass = False
        print("  --> FAIL: Schema validation failed:")
        for filename, error in schema_failures:
            print(f"    - {filename}: {error}")
            
    # 2. URI Mapping Resolution & Spec §11
    print("\n[CHECK 2] URI Mapping Resolution & Spec §11 check:")
    uri_success, uri_stdout, uri_stderr = run_test_uri_sh(workspace_dir)
    print(uri_stdout)
    if uri_success:
        print("  --> PASS: test-uri.sh completed successfully.")
    else:
        all_pass = False
        print(f"  --> FAIL: test-uri.sh execution failed:\n{uri_stderr}")

    # 3. Weekly Brief KPI Verification
    print("\n[CHECK 3] Weekly Brief KPI Verification:")
    brief_success, brief_msg, brief_out = run_brief_sh(workspace_dir)
    print(f"  Info: {brief_msg}")
    if brief_success:
        print("  --> PASS: Weekly brief leads with correct KPIs.")
    else:
        all_pass = False
        print(f"  --> FAIL: Weekly brief KPI verification failed:\n{brief_out}")

    # 4. State Contract Verification
    print("\n[CHECK 4] State Contract Verification:")
    contract_success, contract_details = run_state_contract_tests(workspace_dir)
    print("  Details:")
    for line in contract_details.split('\n'):
        print(f"    {line}")
    if contract_success:
        print("  --> PASS: State contract enforces read-only on down-state and blocks on missing data-grant.")
    else:
        all_pass = False
        print("  --> FAIL: State contract checks did not behave as expected.")

    print("\n" + "=" * 60)
    if all_pass:
        print("VERIFICATION SUCCESSFUL: ALL CHECKS PASSED.")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED: ONE OR MORE CHECKS FAILING.")
        sys.exit(1)

if __name__ == '__main__':
    main()
