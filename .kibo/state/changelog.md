# KIBO OS Changelog

## 5.1.0 — 2026-06-22

- **Proposal**: prop_01hqsplitmonitor1234567890 (Promoted)
- **Target**: autonomy:herald
- **Changes**:
  - Rebuilt `.kibo/config/herald.yaml` to focus exclusively on category authority, brand positioning, and lowering CAC under the `brand_voice` guardrail rules.
  - Created `.kibo/config/monitor.yaml` to isolate telemetry monitoring triggers (`degraded_evals`, `safety_drift` -> `halt_autonomy`, `high_cac`) as the §10.5 drift layer.
- **Expected Effect**:
  - CAC: -10% vs baseline $5,000
  - Human Gates: 0
  - Founder Dependence: 0
- **Regression Test**: Registered `test_suite.py::test_monitor_yaml_schema` and `test_suite.py::test_herald_split_integrity`.

## 5.0.0 — 2026-06-21

- Rebranded the entity from "Wael LLC" to KIBO OS; the product IS the operating system we install.
- Namespaced state to kibo://; reframed the W-Method as the KIBO OS architecture.
- Productized the deployable catalog into the KIBO module family (KIBO Net / Knowledge / Gateway / Connect / Telemetry; Regentic & WFair as L7 verticals).
- Case study zero restated: "KIBO OS runs on KIBO OS."

## 4.0.0 — 2026-05-15

- B2B reframe: install the engine into mid-tier (esp. regulated) companies; acquisition is the throttle; Herald + PE channel + deployability ladder + mechanism-not-jackpot discipline.

## 3.0.0 — 2026-03-10

- One-person billion-dollar company; agent workforce; autonomy-expansion throttle; judgment queue.

## 2.0.0 — 2026-01-20

- AI-native transformation consultancy; W-Method 7-layer stack; deployable MCP catalog.

## 1.0.0 — 2025-11-01

- Executive AI function; scope boundaries; improvement loop; MCP/service contract.
