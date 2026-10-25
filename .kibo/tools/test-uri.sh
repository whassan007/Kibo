#!/usr/bin/env bash

# test-uri.sh - Verify that all required state files and configs exist and match expectations.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Run the python-based URI mappings checker
python3 "${WORKSPACE_DIR}/.kibo/tools/test_uri.py"
