#!/usr/bin/env bash
# brief.sh - Weekly brief aggregator for KIBO OS
set -euo pipefail

WORKSPACE_DIR="/Users/iceman/Documents/Code/Kibo"

# Execute the python brief generator
uv run --with pyyaml python3 "${WORKSPACE_DIR}/.kibo/tools/brief.py" "$@"
