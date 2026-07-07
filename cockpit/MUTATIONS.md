# KIBO OS Cockpit - Mutation Semantics

To ensure the local file-access layer and the eventual KIBO MCP server remain fully synchronized, the following write semantics are strictly defined and implemented:

## 1. Proposal Promotion (Promote)
- **Target File**: `.kibo/state/proposals/draft/{proposal_id}.json` (and eventually appending to active grants/ladder if specified).
- **Semantics**:
  - The proposal status key is overwritten from `"proposed"` or `"reviewed"` to `"promoted"`.
  - An entry is appended to `.kibo/state/feedback/log.md` recording the promotion as a verification event.
  - The version block in `.kibo/state/prompt/active.yaml` or relevant configuration is updated if the proposal entails a semver bump.

## 2. Human Judgment Resolution (Approve / Reject / Defer)
- **Target File**: `.kibo/state/queue.json`
- **Semantics**:
  - The queue record containing the target `id` is retrieved.
  - The `"status"` key is overwritten:
    - `Approve` -> `"resolved"` (with `"resolved_at"` timestamp).
    - `Reject` -> `"rejected"` (with `"resolved_at"` timestamp).
    - `Defer` -> `"pending"` (updated timestamp).

## 3. Feedback Creation
- **Target File**: `.kibo/state/feedback/log.md`
- **Semantics**:
  - A new Markdown block is **appended** to the end of the file.
  - It MUST NOT overwrite any existing content.
  - Format:
    ```markdown
    ## [Timestamp] FB-YYYY-XXXX (Category)
    - **Source:** {client_name}
    - **Category:** {category}
    - **Description:** {description}
    - **Rubric Assessment:** {rubric}
    - **Evidence:** {evidence}
    ```
