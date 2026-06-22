import os
import yaml
import json

class KiboSurface:
    def __init__(self, workspace_dir='/Users/iceman/Documents/Code/Kibo'):
        self.workspace_dir = workspace_dir
        self.config = {}
        self.load_config()

    def load_config(self):
        config_path = os.path.join(self.workspace_dir, '.kibo/config/mcp-surface.yaml')
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def resolve_uri(self, uri):
        if not uri.startswith('kibo://'):
            raise ValueError("URI must start with kibo://")
        
        uri_mappings = self.config.get('uri_mappings', {})
        mapped_path = uri_mappings.get(uri)
        if mapped_path is None:
            raise ValueError(f"URI {uri} is not mapped in the configuration.")
        
        return os.path.join(self.workspace_dir, mapped_path)

    def can_perform_action(self, client_name, action_type, uri, specific_grant=None, mock_grants_missing=False, mock_grants_file_path=None):
        try:
            resolved_path = self.resolve_uri(uri)
        except ValueError:
            return False
        
        surface_rules = self.config.get('surface_rules', {})
        
        # 1. State file contract check
        if surface_rules.get('read_only_on_down_state', False):
            # If the resolved path does not exist (down state)
            if not os.path.exists(resolved_path):
                # Force read-only (block write operations)
                if action_type == 'write':
                    return False

        # 2. Data grant contract check
        if surface_rules.get('verify_grant_before_client_touch', False):
            grants_path = mock_grants_file_path or os.path.join(self.workspace_dir, '.kibo/state/autonomy/grants.json')
            
            if mock_grants_missing or not os.path.exists(grants_path):
                # Missing grants file/missing data-grant blocks any client action
                return False
            
            try:
                with open(grants_path, 'r') as file:
                    grants = json.load(file)
            except Exception:
                return False

            if client_name not in grants:
                # Missing data-grant for this client blocks action
                return False
            
            client_grants = grants[client_name]
            if not isinstance(client_grants, dict) or not client_grants:
                return False
            
            # If a specific grant/permission is required, verify it is explicitly true
            if specific_grant:
                return client_grants.get(specific_grant, False)
            
            # Otherwise, verify that the client has at least one active permission grant
            # to verify that they are authorized for general actions
            return any(client_grants.values())

        return True
