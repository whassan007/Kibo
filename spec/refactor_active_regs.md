Refactor the "Active Regs" dropdown selection element shown in image_678ada.png. The current flat layout cannot scale to support the full, multi-tiered Canadian regulatory environment. You must re-engineer this component into a cascading, nested accordion tree layout. 

Maintain the strict KIBO V2 monochrome, high-contrast, zero-shadow E-ink design system (1px solid borders, monospace type, no smooth transition animations, pure black #000000 / white #FFFFFF / zinc grays).

========================================================================
1. DATA STRUCTURE EXPANSION (types/compliance.ts)
========================================================================
Expand the backend database models and frontend data arrays to support the complete Canadian privacy legal ontology. Update the structural data schema to map the following hierarchy:

- CANADA (Federal)
  ├── PIPEDA (Commercial Baseline)
  ├── Privacy Act (Federal Public Sector)
  └── CASL (Commercial Electronic Marketing)
- ONTARIO (Provincial)
  ├── FIPPA (Public Sector Baseline - as seen in image_678ada.png)
  └── PHIPA (Health Data Custodian Mandates)
- QUEBEC (Provincial)
  └── Law 25 (Comprehensive Private/Public - checked in image_678ada.png)
- ALBERTA (Provincial)
  ├── PIPA (Personal Information Protection Act)
  ├── FOIP (Freedom of Information & Protection of Privacy)
  └── HIA (Health Information Act)
- BRITISH COLUMBIA (Provincial)
  ├── PIPA (Private Sector)
  └── FIPPA (Freedom of Information & Protection of Privacy Act)

========================================================================
2. UI/UX RE-ENGINEERING (components/ScopeActiveLegislations.tsx)
========================================================================
Replace the flat popover container shown in image_678ada.png with a strict, hierarchical nested tree element.

2.1 Cascading Tree Interaction
- The top-level items in the picker must represent the macro jurisdictions (e.g., [ ] Canada, [ ] United States, [ ] European Union, [ ] United Kingdom).
- Clicking the flag or text of a macro jurisdiction must NOT instantly toggle it. Instead, render a clean inline monospace toggle glyph: `[ + ]` to expand, `[ - ]` to collapse.
- Expanding "Canada" must cleanly drop down an indented sub-list containing the distinct tiers: Federal, Ontario, Quebec, Alberta, British Columbia.

2.2 Indeterminate Checkbox Matrix
- Implement strict indeterminate checkbox logic for parent rows. 
- If an analyst checks "Quebec - Law 25" and "Canada (Federal) - PIPEDA", the top-level "Canada" checkbox must display an intermediate strike-through state `[-]` indicating a partial sub-selection.
- Checking a parent row completely (e.g., selecting the main "Ontario" node) must automatically cascade down and force-check all nested child frameworks (`FIPPA` + `PHIPA`).

2.3 Pure E-Ink Low-Latency Controls
- Forbid all sliding smooth height animations when sections drop down. Use immediate block display toggles (`display: block` / `display: none`) to prevent redraw screen ghosting.
- The tracking summary button at the top header (`Active Regs (4) ▾`) must update its count live in real-time as these nested boxes are checked.

========================================================================
3. INTEGRATION BACKEND ALIGNMENT
========================================================================
- Ensure that the resulting payload array from this picker (e.g., `active_frameworks: ["PIPEDA", "LAW_25", "PHIPA"]`) is instantly pushed via WebSocket or state dispatch to the LangGraph memory checkpointer state (`KiboAgentState`).
- This selection must immediately alter the active conditional edge routing metrics, turning on the specific parallel assessment nodes required for the enterprise scope.