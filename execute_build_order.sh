#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- CONFIGURATION ---
DGX_HOST="http://waelbot:11434"
MAC_HOST="http://127.0.0.1:11434"

# Configuration options for Ollama API
TEMPERATURE=0.0
NUM_CTX=32768

# Output paths
LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

echo "================================================================"
echo "⚡ KIBO LOCAL FLEET AGENT ORCHESTRATOR — PRIVACY INBOX REDESIGN"
echo "================================================================"
echo "Timestamp: $(date)"
echo "Target Cluster: $DGX_HOST (DGX) & $MAC_HOST (Local Mac)"
echo "----------------------------------------------------------------"

# --- HELPER FUNCTION: CONTEXT LOADING & API CALL ---
# Arguments: host, model_name, log_file, system_prompt, context_files_space_separated
call_agent() {
    local host="$1"
    local model="$2"
    local logfile="$3"
    local system_instructions="$4"
    shift 4
    local context_files=("$@")

    # Accumulate file contents into a single markdown prompt payload
    local full_prompt=""
    full_prompt+="### SYSTEM DIRECTIVES & WORK ORDER\n${system_instructions}\n\n"
    full_prompt+="### GROUND TRUTH SOURCE CONTEXT\n"

    for file in "${context_files[@]}"; do
        if [ -f "$file" ]; then
            full_prompt+="\n--- START FILE: ${file} ---\n"
            full_prompt+=$(cat "$file" | sed 's/"/\\"/g' | sed 's/\\/\\\\/g' | awk '{printf "%s\\n", $0}')
            full_prompt+="\n--- END FILE: ${file} ---\n"
        elif [ -d "$file" ]; then
            full_prompt+="\n--- START DIRECTORY MAP: ${file} ---\n"
            full_prompt+=$(find "$file" -type f -not -path '*/.*' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}')
            full_prompt+="\n--- END DIRECTORY MAP ---\n"
        else
            echo "⚠️  Warning: Context file/path not found: $file" >&2
        fi
    done

    # Build JSON payload using robust format
    # Note: raw response streaming is disabled for structured log harvesting
    local payload=$(cat <<EOF
{
  "model": "$model",
  "prompt": "$full_prompt",
  "stream": false,
  "options": {
    "temperature": $TEMPERATURE,
    "num_ctx": $NUM_CTX
  }
}
EOF
)

    # Dispatch to Ollama
    curl -s -X POST "${host}/api/generate" \
        -H "Content-Type: application/json" \
        -d "$payload" > "$logfile"
}

# --- PARALLEL EXECUTION: PHASE 1 ---
echo "▶️ Launching Work Orders 1 and 2 in parallel on DGX ($DGX_HOST)..."

# WO-1 Prompt Construction
WO1_PROMPT="You are a Staff Frontend Engineer implementing the KIBO Privacy Inbox redesign. Deliver components/inbox/ components, views/PrivacyInbox.tsx, and services/inboxService.ts using rigid TypeScript, token variables from tokens.css, and handling proper loading/empty/error states. Use real HTML buttons and clear keyboard nav hooks. Zero alerts or cloud reliance allowed."
WO1_CONTEXT=("spec/review/privacy_inbox_redesign_spec.md" "kibo-is-frontend/src" "kibo-is/src/PrivacyInbox.jsx")

# WO-2 Prompt Construction
WO2_PROMPT="You are a Staff Backend Engineer adding the Privacy Inbox API to KIBO. Deliver inbox_store.py with the SQLite schema, add the paginated GET and POST decision endpoints to agent_gateway.py with anti-silent failure wrappers, and add a local classification stub calling run_agent_node. Adhere to baseline logging constraints."
WO2_CONTEXT=("spec/review/privacy_inbox_redesign_spec.md" "kibo-is/agent_gateway.py" "kibo-is/ontology_store.py")

# Spin up WO-1 (Frontend) Background Process
call_agent "$DGX_HOST" "qwen3-coder:30b" "$LOG_DIR/wo1_frontend.json" "$WO1_PROMPT" "${WO1_CONTEXT[@]}" &
PID_WO1=$!
echo "  ↳ [WO-1 Frontend] Dispatched to qwen3-coder:30b (PID: $PID_WO1)"

# Spin up WO-2 (Backend) Background Process
call_agent "$DGX_HOST" "devstral:24b" "$LOG_DIR/wo2_backend.json" "$WO2_PROMPT" "${WO2_CONTEXT[@]}" &
PID_WO2=$!
echo "  ↳ [WO-2 Backend] Dispatched to devstral:24b (PID: $PID_WO2)"

echo "⏳ Waiting for parallel compilation passes to complete..."
wait $PID_WO1
echo "✅ WO-1 Frontend engineering generation complete. Output saved to $LOG_DIR/wo1_frontend.json"

wait $PID_WO2
echo "✅ WO-2 Backend engineering generation complete. Output saved to $LOG_DIR/wo2_backend.json"

# --- SEQUENTIAL EXECUTION: PHASE 2 ---
echo "----------------------------------------------------------------"
echo "▶️ Launching Test Suite Synthesis (WO-3) on DGX..."

WO3_PROMPT="You are a Principal QA Automation Engineer. Follow spec/ANTIGRAVITY_TESTING_PROMPT.md exactly. Deliver tests/backend/test_inbox_api.py (pytest+httpx), tests/frontend/PrivacyInbox.test.tsx (RTL), and tests/e2e/inbox.spec.ts (Playwright with axe-core scan). Tag and mark requirements with xfail strict where baseline defects remain unmerged."
WO3_CONTEXT=("spec/ANTIGRAVITY_TESTING_PROMPT.md" "spec/TESTING_PLAN.md" "spec/review/privacy_inbox_redesign_spec.md")

call_agent "$DGX_HOST" "coder-core" "$LOG_DIR/wo3_tests.json" "$WO3_PROMPT" "${WO3_CONTEXT[@]}"
echo "✅ WO-3 Test Generation Complete. Output saved to $LOG_DIR/wo3_tests.json"

echo "----------------------------------------------------------------"
echo "🎉 All local fleet engineering runs complete. Checking files into workspace."

