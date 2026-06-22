#!/usr/bin/env bash

# test-uri.sh - Verify that all required state files and configs exist and match expectations.

set -euo pipefail

WORKSPACE_DIR="/Users/iceman/Documents/Code/Kibo"

# Run the python-based URI mappings checker
uv run --with pyyaml python3 "${WORKSPACE_DIR}/.kibo/tools/test_uri.py"
