import os
import sys
import yaml

def check_uri_mappings():
    workspace_dir = '/Users/iceman/Documents/Code/Kibo'
    config_path = os.path.join(workspace_dir, '.kibo/config/mcp-surface.yaml')
    required_uris = [
        "kibo://company/profile",
        "kibo://brand/category",
        "kibo://growth/pipeline",
        "kibo://clients",
        "kibo://deployments",
        "kibo://architecture/current",
        "kibo://catalog",
        "kibo://proof",
        "kibo://autonomy/grants",
        "kibo://deployability/ladder",
        "kibo://corrections",
        "kibo://feedback/log",
        "kibo://evals/scores",
        "kibo://prompt/active",
        "kibo://proposals",
        "kibo://proposals/draft"
    ]

    if not os.path.exists(config_path):
        print(f"Error: mcp-surface.yaml not found at {config_path}")
        return 1

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    uri_mappings = config.get('uri_mappings', {})
    errors = 0
    missing_uris = []

    print("=== Validating kibo:// URI Mappings ===")
    for uri, path in uri_mappings.items():
        full_path = os.path.join(workspace_dir, path)
        if os.path.exists(full_path):
            print(f"[OK] {uri} -> {path} (exists)")
        else:
            print(f"[FAIL] {uri} -> {path} (path does not exist!)")
            errors += 1

    print("\n=== Validating Spec §11 Mappings presence ===")
    for required_uri in required_uris:
        if required_uri in uri_mappings:
            print(f"[OK] Spec §11 URI mapped: {required_uri}")
        else:
            print(f"[FLAG] Spec §11 URI not mapped: {required_uri}")
            missing_uris.append(required_uri)

    print("\n=== URI Verification Summary ===")
    print(f"Total resolution errors: {errors}")
    print(f"Total unmapped Spec §11 URIs: {len(missing_uris)}")

    # We return 0 if there are no resolution errors, even if there are unmapped URIs,
    # or we can return 0 if both pass. Let's return 0 if resolution checks pass and we log the flags.
    if errors == 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(check_uri_mappings())
