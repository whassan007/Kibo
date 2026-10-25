#!/usr/bin/env bash
# brief.sh - Weekly brief aggregator for KIBO OS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Execute the python brief generator
python3 "${WORKSPACE_DIR}/.kibo/tools/brief.py" "$@"
