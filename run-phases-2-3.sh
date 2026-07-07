#!/bin/bash

# KIBO Phase 2 & 3 Complete Implementation Runner
# Routes each module to appropriate Ollama server (local vs Spark)
# Usage: ./run-phases-2-3.sh

set -e

KIBO_DIR="/Users/dr.wael/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/Kibo"
MODULES_DIR="$KIBO_DIR"

echo "🚀 KIBO PHASES 2 & 3 - COMPLETE IMPLEMENTATION"
echo "================================================"
echo ""

# Define modules with routing: module_name -> server (local|spark)
declare -A PHASE_2_MODULES=(
    ["MODULE_5_VENDOR_RISK"]="ollama-local"
    ["MODULE_6_DSAR_WORKFLOWS"]="ollama-spark"
    ["MODULE_7_INCIDENT_BREACH_MANAGEMENT"]="ollama-spark"
    ["MODULE_8_NOTIFICATION_ESCALATION"]="ollama-local"
)

declare -A PHASE_3_MODULES=(
    ["MODULE_9_KUBERNETES"]="ollama-spark"
    ["MODULE_10_ANALYTICS"]="ollama-spark"
    ["MODULE_11_REGULATORY_FEEDS"]="ollama-local"
    ["MODULE_12_ML_INTEGRATION"]="ollama-spark"
)

# Function to add MCP directive to module prompt
add_mcp_directive() {
    local module_file=$1
    local mcp_server=$2

    if [ ! -f "$module_file" ]; then
        echo "❌ File not found: $module_file"
        return 1
    fi

    # Extract the implementation prompt section
    local temp_file="/tmp/module_with_directive.txt"

    cat > "$temp_file" << EOF
@mcp-server: $mcp_server

$(cat "$module_file")
EOF

    echo "$temp_file"
}

# Function to display module instructions
show_module_instructions() {
    local module_name=$1
    local mcp_server=$2
    local week_range=$3

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 $module_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Server: $mcp_server"
    echo "Timeline: $week_range"
    echo ""
    echo "STEPS:"
    echo "1. Open Antigravity IDE"
    echo "2. Copy content from: $MODULES_DIR/${module_name}.md"
    echo "3. Add this directive at the TOP:"
    echo "   @mcp-server: $mcp_server"
    echo "4. Paste entire prompt into Antigravity"
    echo "5. Select Gemma4 as model"
    echo "6. Generate code to file structure"
    echo "7. Run tests in ./tests/"
    echo "8. ✅ Mark complete when acceptance criteria pass"
    echo ""
}

# Phase 2
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║             PHASE 2: ENTERPRISE FEATURES                   ║"
echo "║                    (Weeks 17-32)                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

for module in "${!PHASE_2_MODULES[@]}"; do
    server=${PHASE_2_MODULES[$module]}

    case $module in
        MODULE_5_VENDOR_RISK)
            week_range="Weeks 17-22"
            ;;
        MODULE_6_DSAR_WORKFLOWS)
            week_range="Weeks 19-28"
            ;;
        MODULE_7_INCIDENT_BREACH_MANAGEMENT)
            week_range="Weeks 23-30"
            ;;
        MODULE_8_NOTIFICATION_ESCALATION)
            week_range="Weeks 25-32"
            ;;
    esac

    show_module_instructions "$module" "$server" "$week_range"
done

echo "🎯 PHASE 2 CHECKPOINT (Week 32):"
echo "   ✅ All 4 modules integrated"
echo "   ✅ 20+ customers onboarded"
echo "   ✅ Ready for Phase 3"
echo ""

# Phase 3
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          PHASE 3: SCALING & OPTIMIZATION                   ║"
echo "║                    (Weeks 33-52)                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

for module in "${!PHASE_3_MODULES[@]}"; do
    server=${PHASE_3_MODULES[$module]}

    case $module in
        MODULE_9_KUBERNETES)
            week_range="Weeks 33-40"
            ;;
        MODULE_10_ANALYTICS)
            week_range="Weeks 39-46"
            ;;
        MODULE_11_REGULATORY_FEEDS)
            week_range="Weeks 43-50"
            ;;
        MODULE_12_ML_INTEGRATION)
            week_range="Weeks 45-52"
            ;;
    esac

    show_module_instructions "$module" "$server" "$week_range"
done

echo "🏆 PHASE 3 FINAL CHECKPOINT (Week 52):"
echo "   ✅ Global Kubernetes deployment"
echo "   ✅ Advanced analytics live"
echo "   ✅ Regulatory intelligence active"
echo "   ✅ AI/ML automation 80% workflows"
echo "   ✅ Market leader status"
echo "   ✅ Ready for Series C / IPO"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 MCP SERVER ROUTING SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "ollama-local (localhost:11434):"
echo "  - gemma4 / qwen2.5-coder:7b"
echo "  - Best for: Fast iteration, lightweight code"
echo "  - Modules: 5, 8, 11"
echo ""
echo "ollama-spark (dgx-spark.tail16d8d9.ts.net:11434):"
echo "  - qwen3-coder:30b / reasoning-core:latest"
echo "  - Best for: Complex logic, large files, ML"
echo "  - Modules: 6, 7, 9, 10, 12"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 EXECUTION CHECKLIST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "PHASE 2 (16 weeks):"
echo "  [ ] MODULE 5:  Vendor Risk (ollama-local)"
echo "  [ ] MODULE 6:  DSAR (ollama-spark)"
echo "  [ ] MODULE 7:  Incident & Breach (ollama-spark)"
echo "  [ ] MODULE 8:  Notifications (ollama-local)"
echo ""
echo "PHASE 3 (20 weeks):"
echo "  [ ] MODULE 9:  Kubernetes (ollama-spark)"
echo "  [ ] MODULE 10: Analytics (ollama-spark)"
echo "  [ ] MODULE 11: Regulatory Feeds (ollama-local)"
echo "  [ ] MODULE 12: ML Integration (ollama-spark)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Ready to start! Begin with MODULE 5."
echo "📖 See PHASE_2_SUMMARY_COMPLETE.md for full timeline"
echo ""
