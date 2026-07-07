#!/usr/bin/env bash
#
# run_tab_builds.sh — dispatch KIBO per-tab build orders to the LOCAL Ollama fleet.
# Runnable from anywhere. NO CLOUD MODELS.
#
#   ./run_tab_builds.sh list                 # show all work orders
#   ./run_tab_builds.sh run hitl             # run one work order
#   ./run_tab_builds.sh run meetings training # run several
#   ./run_tab_builds.sh all                  # run every work order in slot order
#   ./run_tab_builds.sh slot 1               # run one run-sheet slot
#
# Output: each order's generated response is written to
#   $KIBO_ROOT/spec/review/tabs/out/<id>.<model>.md
# You then review/apply the code the model proposes (this script does NOT
# auto-write source files — it captures the model's build output for you).
#
# Config via env (or edit defaults below):
#   KIBO_ROOT   repo root (auto-detected from git or common paths)
#   MAC_HOST    default http://127.0.0.1:11434
#   DGX_HOST    default http://waelbot:11434
#   DRY_RUN=1   print the plan without calling any model
set -uo pipefail

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MAC_HOST="${MAC_HOST:-http://127.0.0.1:11434}"
# DGX over Tailscale. The hostname 'waelbot' often doesn't resolve from the Mac,
# so default to the Tailscale IP. Override with DGX_HOST=... if yours differs.
DGX_HOST="${DGX_HOST:-http://100.113.62.112:11434}"
DRY_RUN="${DRY_RUN:-0}"

# zsh doesn't treat '#' as a comment in interactive pastes, so a pasted
# "run hitl   # note" arrives as extra args. Drop any arg from the first '#'.
_argv=(); for _a in "$@"; do [[ "$_a" == \#* ]] && break; _argv+=("$_a"); done
set -- "${_argv[@]}"

# Locate the repo root
detect_root() {
  if [[ -n "${KIBO_ROOT:-}" ]]; then echo "$KIBO_ROOT"; return; fi
  local g; g="$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ -n "$g" && -d "$g/kibo-is" ]]; then echo "$g"; return; fi
  for p in \
    "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Documents/Code/Kibo" \
    "$HOME/Code/Kibo" "$HOME/kibo" "$HOME/Kibo"; do
    [[ -d "$p/kibo-is" ]] && { echo "$p"; return; }
  done
  echo ""
}
KIBO_ROOT="$(detect_root)"
if [[ -z "$KIBO_ROOT" ]]; then
  echo "ERROR: cannot find KIBO repo. Set KIBO_ROOT=/path/to/Kibo" >&2; exit 1
fi
OUT_DIR="$KIBO_ROOT/spec/review/tabs/out"
mkdir -p "$OUT_DIR"

# ---------------------------------------------------------------------------
# Work-order registry:  id | host | model | title | reference-doc-section
# Prompts are assembled from the shared preamble + the per-order body below.
# ---------------------------------------------------------------------------
# Order in which `all` runs them (mirrors the run sheet in the build doc).
ORDER_IDS=(hitl map meetings training employee psr ontology sources trust deploy telemetry)

model_for() { # id -> "host|model"
  case "$1" in
    hitl|meetings|training|employee|psr|sources) echo "$DGX_HOST|qwen3-coder:30b" ;;
    map|ontology|deploy|telemetry)               echo "$DGX_HOST|gpt-oss:120b" ;;
    trust)                                        echo "$DGX_HOST|qwen3-coder:30b" ;;
    *) echo "" ;;
  esac
}

title_for() {
  case "$1" in
    hitl) echo "HITL Governance Queue";; map) echo "Compliance Coverage Map";;
    meetings) echo "Meetings Planner";; training) echo "Training Admin";;
    employee) echo "Employee Mode";; psr) echo "PSR Committee";;
    ontology) echo "Compliance Net Ontology";; sources) echo "Authoritative Sources";;
    trust) echo "Trust Tiers";; deploy) echo "Deployment Center";;
    telemetry) echo "UX Telemetry Feedback";; *) echo "";;
  esac
}

# Shared preamble prepended to every order.
read -r -d '' PREAMBLE <<'EOF'
You are a Staff Frontend/Backend Engineer on KIBO, a local-first privacy
compliance platform. HARD RULE: NO CLOUD MODELS or external LLM calls in any
code you write. Build INTO kibo-is-frontend/ (the TypeScript twin) using the
shared component library (Button, Panel, SectionHeader, Field, Select,
DataTable, Tag, Toast, ConfirmDialog, EmptyState, Skeleton, OfflineBanner,
SlaBadge). The legacy kibo-is/src JSX files are REFERENCE ONLY — never copy their
inline hex colors, alert(), or silent fetch failures. Constraints (regression
baseline): API base from VITE_API_BASE only, never a hardcoded URL (R-1);
non-2xx responses throw a typed error, never a silent 200-with-empty-array (R-5);
every view ships loading + empty + offline states reachable via props (R-2);
offline disables mutations and preserves unsent input; polling must not block the
main thread (pause on visibilitychange). No alert(), no window.confirm() — use
ConfirmDialog/Toast. Sentence case UI copy; two font weights (400/500). Every
mutating action returns visible feedback with an audit reference. New backend
endpoints go in agent_gateway.py; do NOT add sync sqlite3 writes inside async
handlers (R-3) — wrap in a thread executor or mark TODO(R-3). Log via the logging
module, not print() (R-8). Output a complete, buildable implementation.

OUTPUT FORMAT (STRICT — a script parses this): emit every file the change needs,
each wrapped EXACTLY as:
===FILE: relative/path/from/repo/root===
<full file contents, no markdown fences, no commentary inside>
===END FILE===
Paths are relative to the KIBO repo root (e.g. kibo-is-frontend/src/views/Foo.tsx
or kibo-is/agent_gateway.py). Do NOT wrap file blocks in ``` fences. Put any
prose, build/lint/seed commands, and the TEST HOOK mapping OUTSIDE and AFTER all
===FILE=== blocks. If you must modify an existing file, output its COMPLETE new
contents (the applier overwrites whole files; it does not patch).
EOF

body_for() {
  case "$1" in
    hitl) cat <<'EOF'
BUILD views/HitlQueue.tsx (replaces AdminDashboard 'hitl'), the product's core
loop. Queue DataTable bound to /api/transactions (pending only), sorted by SLA,
columns priority/jurisdiction/agent + live SlaBadge from real deadline data
(never client clock). Row -> decision pane that VISIBLY shows the ontology router
derivation (active_frameworks, mandated_controls, mandated_artifacts) plus the
5-action decision block: Approve now / Approve always (expands reasoning field ->
trains rule engine) / Flag to legal / Review later / Reject. POST
/api/transactions/{id}/decision; show the SHA-256 audit receipt after commit.
Offline disables decisions. TEST HOOK: GT-2, GT-3, S1, R-2, R-5.
EOF
;;
    map) cat <<'EOF'
Refactor kibo-is/src/ComplianceCoverageMap.jsx (1063 lines) into
kibo-is-frontend views/ComplianceCoverageMap.tsx split into map + gap-panel +
legend components. Choropleth/grid of jurisdictions (D3 or SVG, D3 from
cdnjs/jsdelivr only) bound to /api/compliance/coverage; color = coverage status
with a required legend. Click jurisdiction -> gap panel of uncovered obligations
with a "create task" action POST /api/compliance/gaps/create_task returning a
task ref that appears in the queue. BACKEND: ensure /api/compliance/coverage
derives from the ontology via derive_compliance_routing (real graph, not a static
list). Offline read-only. TEST HOOK: GT-3, GT-7, S1, R-2; coverage-reflects-
ontology is a named backend test.
EOF
;;
    meetings) cat <<'EOF'
BUILD views/MeetingsPlanner.tsx (replaces App.jsx 'meetings'). Create-meeting
form (styled date-time picker not raw native; type Weekly Privacy & Security /
PSR Committee / ad-hoc; attendees multi-select of roles; recurrence; repeatable
agenda rows) with full validation, required marks, inline errors, success toast +
meeting ref. Meetings DataTable (upcoming/past, sortable by date, status) ->
detail with minutes editor + action-item rows (assignee, due date, linked risk
id) that POST into the transaction/queue pipeline so actions become tracked work.
Keep the 9 commissioner links as a labeled resource-list component. BACKEND:
extend /api/expert/meetings + /api/psr/meetings with POST create, GET detail,
PATCH minutes, POST action-item (routes into intake, appends audit). TEST HOOK:
GT-5, S1, R-2, R-5.
EOF
;;
    training) cat <<'EOF'
BUILD views/TrainingAdmin.tsx (replaces App.jsx 'training_admin'), fixing the
"Loading compliance data..." infinite-spinner (R-2/R-5). Org metric cards
(completion %, overdue, at-risk) bound to /api/expert/training/compliance —
resolve to data/empty/error, never an endless spinner. Per-employee roster
DataTable (name, role, course, status, due) with sort/filter/search/CSV export.
Bulk "Reset & Assign Courses" and "Send Overdue Reminders" MUST open a
ConfirmDialog with scope preview ("assign 3 courses to 42 employees") and return
an audit ref. BACKEND: GET returns {metrics, roster}; POST assign + reminders
take an explicit id list, append audit, return {affected, audit_ref}. TEST HOOK:
GT-7, S1, R-2, R-5; confirm-dialog-on-bulk is a named frontend test.
EOF
;;
    employee) cat <<'EOF'
BUILD views/EmployeeHome.tsx (persona 'employee'). Three sections: (1) assigned
compliance risks DataTable (keep the existing good empty state); (2) role-based
FIPPA training cards with launch + completion bound to /api/employee/{id}/
training; (3) data-inventory contribution form (system name, data-type chips,
purpose, STRUCTURED retention duration picker not free text, third-party sharing)
-> on submit confirmation with reference id + append to a "My submissions" list;
draft auto-save to localStorage. ADD a "Report an incident" primary action
(currently missing, highest-value employee task) -> minimal form creates an
incident that surfaces in the Expert HITL queue. BACKEND: inventory POST returns
ref + persists; new POST /api/employee/{id}/incident creates incident + routes to
queue. TEST HOOK: GT-4, GT-7, S1, R-2, R-5.
EOF
;;
    psr) cat <<'EOF'
BUILD views/PsrCommittee.tsx (persona 'psr'). Advisory materials resource-list
(download/view) with version + review-status badges. Risk Advisory Queue
DataTable bound to /api/psr/risk-queue; each item opens a decision pane where a
committee member RECORDS AN OPINION — approve / request-changes / escalate /
comment — with a reasoning field (this workflow is missing today; persona is
read-only). POST /api/psr/risk/{id}/opinion {decision, reasoning} -> audit_ref,
feeds self_improvement ingestion (GT-2). Link PSR meetings (from Meetings
Planner) to materials here. Offline disables opinion submission. TEST HOOK: GT-2,
S1, R-2, R-5.
EOF
;;
    ontology) cat <<'EOF'
Refactor kibo-is/src/components/OntologyVisualizer.jsx into kibo-is-frontend
views/OntologyVisualizer.tsx. Force-directed graph (D3 from cdnjs/jsdelivr) of
the ~491-edge compliance graph bound to /api/ontology/export (JSON-LD); node
color by class (Jurisdiction/LegalFramework/PrivacyTort/GovernanceControl/
Certification/PenaltyExposure/AssessmentArtifact) with legend; click node ->
predicates in/out; path highlight for a transaction's derivation. Import is
GOVERNED: /api/ontology/import goes through confirm + validation preview with a
predicate census before/after — NEVER a silent wipe (defect R-6, the linksTo
incident). BACKEND: harden /api/ontology/import to reject/quarantine payloads
missing canonical predicates or introducing unknown ones, require a change-log
entry, enforce predicate census >= seed baseline. Virtualize/limit rendered
edges; don't block main thread. TEST HOOK: R-6 (import guard + census invariant,
strict xfail until guard ships), GT-1, S1, R-2.
EOF
;;
    sources) cat <<'EOF'
BUILD views/AuthoritativeSources.tsx (replaces AdminDashboard 'source_viewer').
Searchable/filterable DataTable of source-of-truth legal docs (title,
jurisdiction, type, version, last-checked) bound to /api/sources; row ->
side-by-side diff viewer (previous vs current) with changed clauses highlighted;
"route to Phase 1 / create task" action for material changes. Show each source's
provenance + last-verified timestamp (ties to R-6 integrity). Offline read-only.
TEST HOOK: S1, R-2, GT-1; diff-render correctness is a named frontend test with a
2-version fixture.
EOF
;;
    trust) cat <<'EOF'
BUILD views/TrustTiers.tsx (replaces AdminDashboard 'trust_tiers'). Tier cards
(tier name, allowed action scopes, gate type human/auto, agents at this tier)
from the autonomy/deployability ladder. Promote/demote controls behind a
ConfirmDialog (autonomy expansion is governed + audited, .kibo boundary #5).
BACKEND: GET /api/trust/tiers from .kibo/state/autonomy/grants.json +
deployability/ladder.json (validate grants before returning, R-6 discipline);
POST /api/trust/tiers/{agent}/promote {reason} -> audit_ref, routes the autonomy
change to the judgment queue (never silent). TEST HOOK: GT-6, S1, R-2, R-9.
EOF
;;
    deploy) cat <<'EOF'
BUILD views/DeploymentCenter.tsx (replaces AdminDashboard 'deployment'). The
W-Method 7-layer flow (Attract->Acquire->Diagnose->Agree->Install->Operate->
Compound) as a horizontal stage row; each stage card shows status + gate_type
human/auto; human-gate stages get a "sign off" action behind ConfirmDialog that
routes to the judgment queue. BACKEND: GET /api/deploy/ladder from
.kibo/config/deployment-flow.yaml + state; POST /api/deploy/{step}/gate
{decision, reason} -> audit_ref. Offline read-only. TEST HOOK: GT-6, S1, R-2.
EOF
;;
    telemetry) cat <<'EOF'
BUILD views/Telemetry.tsx (replaces AdminDashboard 'telemetry'). Operator
dashboard of UX/feedback signals feeding self-improvement: metric cards + charts
(Chart.js from cdnjs) for feedback volume, agent suggestion accept/override rate,
per-view friction; time-range selector (30/90/365d); anomaly flags. Charts render
the SAME numbers the API returned (no client recompute drift). Polling pauses on
visibilitychange (Resilience Rule 1). BACKEND: GET /api/telemetry/feedback?range=
-> {series, cards, anomalies} from feedback/log + evals/scores, read-only. TEST
HOOK: GT-7, S1, R-2; dashboard-number==API-number is a named test.
EOF
;;
    *) echo "";;
  esac
}

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
call_model() { # host model prompt -> stdout
  local host="$1" model="$2" prompt="$3"
  KIBO_HOST="$host" KIBO_MODEL="$model" KIBO_PROMPT="$prompt" python3 <<'PY'
import json,os,sys,urllib.request
host,model=os.environ["KIBO_HOST"],os.environ["KIBO_MODEL"]
prompt=os.environ["KIBO_PROMPT"]
req=urllib.request.Request(host.rstrip('/')+"/api/generate",
    data=json.dumps({"model":model,"prompt":prompt,"stream":False,
        "options":{"temperature":0.0,"num_ctx":32768}}).encode(),
    headers={"Content-Type":"application/json"})
try:
    with urllib.request.urlopen(req,timeout=1800) as r:
        print(json.loads(r.read()).get("response",""))
except Exception as e:
    print(f"__ERROR__ {e}",file=sys.stderr); sys.exit(1)
PY
}

run_one() {
  local id="$1"
  local hm; hm="$(model_for "$id")"
  if [[ -z "$hm" ]]; then echo "  ! unknown work order: $id" >&2; return 1; fi
  local host="${hm%%|*}" model="${hm##*|}" title; title="$(title_for "$id")"
  local prompt; prompt="$PREAMBLE

=== WORK ORDER: $title ($id) ===
$(body_for "$id")"
  local safe="${model//[:\/]/_}"
  local out="$OUT_DIR/${id}.${safe}.md"
  echo ">> $id — $title  [$model @ $host]"
  if [[ "$DRY_RUN" == "1" ]]; then echo "   (dry run) -> $out"; return 0; fi
  echo "# $title ($id) — generated by $model" > "$out"
  echo "" >> "$out"
  if call_model "$host" "$model" "$prompt" >> "$out"; then
    echo "   done -> $out ($(wc -l < "$out") lines)"
  else
    echo "   FAILED (see stderr). Is $host reachable and '$model' pulled?" >&2
    return 1
  fi
}

check_host() { curl -sf --max-time 5 "$1/api/tags" >/dev/null 2>&1; }

# ---------------------------------------------------------------------------
# Review / Apply
# ---------------------------------------------------------------------------
find_output() { # id -> newest captured output file for that id
  ls -t "$OUT_DIR/${1}."*.md 2>/dev/null | head -1
}

count_files() { # output-file -> number of ===FILE=== blocks
  grep -c '^===FILE: ' "$1" 2>/dev/null || echo 0
}

cmd_review() { # show the file blocks a captured output would write
  local id="$1" f; f="$(find_output "$id")"
  [[ -n "$f" ]] || { echo "No captured output for '$id'. Run it first." >&2; return 1; }
  echo "Output: $f"
  local n; n="$(count_files "$f")"
  echo "Proposes $n file(s):"
  grep '^===FILE: ' "$f" | sed 's/^===FILE: /  /; s/===$//'
  echo
  echo "Prose/notes (lines outside any file block):"
  awk '
    /^===FILE: /{inblk=1; next}
    /^===END FILE===/{inblk=0; next}
    !inblk{print}
  ' "$f" | awk 'NF{p=1} p' | sed 's/^/  /' | tail -40
  echo
  echo "To apply:  $0 apply $id      (writes files onto a new git branch, with backups)"
}

apply_output() { # id  [--force] -> write its ===FILE=== blocks to disk
  local id="$1" force="${2:-}"; local f; f="$(find_output "$id")"
  [[ -n "$f" ]] || { echo "  ! no captured output for '$id'" >&2; return 1; }
  local n; n="$(count_files "$f")"
  [[ "$n" -gt 0 ]] || { echo "  ! '$id' output has no ===FILE=== blocks (model didn't follow format)" >&2; return 1; }
  echo ">> apply $id  ($n files from $(basename "$f"))"
  KIBO_ROOT="$KIBO_ROOT" KIBO_SRC="$f" KIBO_DRY="$DRY_RUN" python3 <<'PY'
import os,re,sys,pathlib,datetime
root=pathlib.Path(os.environ["KIBO_ROOT"]).resolve()
src=pathlib.Path(os.environ["KIBO_SRC"]).read_text(errors="replace")
dry=os.environ.get("KIBO_DRY")=="1"
bak=root/"spec/review/tabs/backup"/datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
blocks=re.findall(r'^===FILE: (.+?)===\r?\n(.*?)^===END FILE===\r?$',src,re.S|re.M)
if not blocks: print("   no blocks parsed"); sys.exit(1)
wrote=0
for rel,content in blocks:
    rel=rel.strip()
    # safety: no absolute paths, no escaping the repo
    p=(root/rel).resolve()
    if not str(p).startswith(str(root)+os.sep):
        print(f"   REFUSED (escapes repo): {rel}"); continue
    if not (rel.startswith("kibo-is/") or rel.startswith("kibo-is-frontend/")
            or rel.startswith("tests/") or rel.startswith("cockpit/") or rel.startswith(".kibo/")):
        print(f"   REFUSED (unexpected target dir): {rel}"); continue
    if dry:
        print(f"   would write {rel} ({len(content)} bytes)"); wrote+=1; continue
    if p.exists():
        b=bak/rel; b.parent.mkdir(parents=True,exist_ok=True)
        b.write_text(p.read_text(errors="replace"),errors="replace")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(content)
    print(f"   wrote {rel} ({len(content)} bytes)"); wrote+=1
print(f"   {'(dry) ' if dry else ''}{wrote} file(s)"
      + ("" if dry else f"; backups of overwritten files in {bak.relative_to(root)}"))
PY
}

cmd_apply() { # [--all | id...] — apply on a dedicated git branch
  local branch="kibo/tab-builds-$(date +%Y%m%d-%H%M%S)"
  local ids=("$@")
  if [[ "${ids[0]:-}" == "--all" ]]; then ids=("${ORDER_IDS[@]}"); fi
  [[ ${#ids[@]} -ge 1 ]] || { echo "apply needs an id (or --all)"; return 1; }
  if [[ "$DRY_RUN" != "1" ]] && git -C "$KIBO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    if ! git -C "$KIBO_ROOT" diff --quiet 2>/dev/null || ! git -C "$KIBO_ROOT" diff --cached --quiet 2>/dev/null; then
      echo "WARN: working tree has uncommitted changes. Commit or stash first, or use DRY_RUN=1 to preview." >&2
    fi
    git -C "$KIBO_ROOT" checkout -b "$branch" >/dev/null 2>&1 \
      && echo "On new branch: $branch" \
      || echo "NOTE: staying on current branch (couldn't create $branch)"
  fi
  local rc=0; for id in "${ids[@]}"; do apply_output "$id" || rc=1; done
  [[ "$DRY_RUN" == "1" ]] || echo "Review with: git -C \"$KIBO_ROOT\" diff  (backups in spec/review/tabs/backup/)"
  return $rc
}

usage() {
  cat <<EOF
KIBO per-tab build runner (local fleet)  root: $KIBO_ROOT
Hosts: MAC=$MAC_HOST  DGX=$DGX_HOST

Workflow: run (generate) -> review (inspect) -> apply (write to a git branch).

  $0 list                 list all work orders + assigned model
  $0 run <id> [<id>...]   generate: dispatch orders, capture model output
  $0 slot <1-6>           generate one run-sheet slot
  $0 all                  generate every order (dependency order)
  $0 review <id>          show the files a captured output would write + notes
  $0 apply <id> [<id>...] write that output's files onto a new git branch (backs up overwrites)
  $0 apply --all          apply every captured output
  DRY_RUN=1 $0 apply <id> preview writes without touching disk

Work order ids: ${ORDER_IDS[*]}
Output:  $OUT_DIR/<id>.<model>.md
Backups: $KIBO_ROOT/spec/review/tabs/backup/<timestamp>/
EOF
}

cmd_list() {
  printf "%-11s %-22s %s\n" ID TITLE MODEL
  for id in "${ORDER_IDS[@]}"; do
    local hm; hm="$(model_for "$id")"
    printf "%-11s %-22s %s\n" "$id" "$(title_for "$id")" "${hm##*|} @ ${hm%%|*}"
  done
}

slot_ids() {
  case "$1" in
    1) echo "hitl map";; 2) echo "meetings training";;
    3) echo "employee psr";; 4) echo "ontology sources";;
    5) echo "trust deploy telemetry";; 6) echo "";;   # slot 6 = tests+review (manual)
    *) echo "";;
  esac
}

main() {
  local cmd="${1:-}"; shift || true
  case "$cmd" in
    list) cmd_list;;
    run)  [[ $# -ge 1 ]] || { usage; exit 1; }
          check_host "$DGX_HOST" || echo "WARN: $DGX_HOST unreachable — DGX orders will fail" >&2
          local rc=0; for id in "$@"; do run_one "$id" || rc=1; done; exit $rc;;
    slot) [[ -n "${1:-}" ]] || { usage; exit 1; }
          local ids; ids="$(slot_ids "$1")"
          [[ -n "$ids" ]] || { echo "Slot $1 has no automated orders (tests/review are manual)."; exit 0; }
          local rc=0; for id in $ids; do run_one "$id" || rc=1; done; exit $rc;;
    all)  check_host "$DGX_HOST" || echo "WARN: $DGX_HOST unreachable" >&2
          local rc=0; for id in "${ORDER_IDS[@]}"; do run_one "$id" || rc=1; done
          echo "All orders dispatched. Review: $0 review <id>  then apply: $0 apply <id>"; exit $rc;;
    review) [[ -n "${1:-}" ]] || { usage; exit 1; }; cmd_review "$1";;
    apply)  [[ $# -ge 1 ]] || { usage; exit 1; }; cmd_apply "$@";;
    ""|-h|--help|help) usage;;
    *) echo "Unknown command: $cmd" >&2; usage; exit 1;;
  esac
}
main "$@"
