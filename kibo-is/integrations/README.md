# KIBO Privacy OS — Corporate Collaboration Hub & AI Assistant Integrations

This directory contains the enterprise integration packages for embedding the **KIBO Privacy Office** into corporate AI collaboration hubs:

1. **Microsoft 365 Copilot & Microsoft Teams (`m365_copilot/`)**
   - `manifest.json` (Microsoft Teams / M365 App Manifest v1.17 with Microsoft Entra ID SSO `webApplicationInfo`)
   - `declarativeAgent.json` (Copilot Declarative Agent v1.2 with governed Privacy Office instructions and conversation starters)
   - `kibo-api-plugin.json` (Copilot API Plugin v2.1 with `OAuthPluginVault` authentication and AdaptiveCard confirmation gates for write tools)
   - `openapi.yaml` (OpenAPI 3.1.0 specification defining `BearerAuth`, `EntraOAuth2`, `X-Tenant-ID` propagation, and all 8 approved Privacy Office tools)

2. **Claude Enterprise Remote & Stdio MCP Server (`claude_mcp/`)**
   - `kibo_privacy_mcp.py` (`FastMCP("KIBO-Privacy-OS-Enterprise")` exposing all 8 approved Privacy Office tools over Stdio and HTTP/JSON-RPC)

3. **Google Cloud Vertex AI / Gemini Enterprise (`gemini_enterprise/`)**
   - `gemini_extension.json` (Gemini Enterprise Extension manifest referencing the OpenAPI 3.1.0 specification, `OIDC_WORKFORCE_IDENTITY_FEDERATION` authentication, and grounding/safety controls)

4. **Unified Corporate Hub Router (`../core/office/hub_router.py`)**
   - `GET /api/v1/integrations/status` — Package readiness, manifest versions, and security control status
   - `POST /api/v1/integrations/copilot/query` — Governed Privacy Office Assistant endpoint (Acceptance Test 12)
   - `POST /api/v1/integrations/mcp/invoke` — Authenticated MCP JSON-RPC tool dispatcher (Acceptance Test 11)

---

## Approved Privacy Office Tools (All 3 Ecosystems)

| # | Tool Name | Mode | Description |
|---|-----------|------|-------------|
| 1 | `get_privacy_guidance` | Read-Only | Governed Privacy Office Assistant: identifies the employee's organization, applicable US/Canada/EU legal obligations, company policies, vendor approval status, required assessments, and approval gates before responding. |
| 2 | `report_privacy_incident` | Consequential Write (Draft Only) | Intakes a suspected privacy or security incident, computes statutory notification clocks, and routes to DPO/Legal triage without external dispatch. |
| 3 | `initiate_privacy_assessment` | Consequential Write (Draft Only) | Initiates a draft PIA, DPIA, Quebec/Canadian TRA, EU TIA, LIA, or AI Impact Assessment (AIIA). |
| 4 | `lookup_privacy_tasks` | Read-Only | Looks up tenant-scoped open privacy tasks, DSAR deadlines, and assessment reviews. |
| 5 | `lookup_vendor_status` | Read-Only | Verifies third-party vendor or AI subprocessor DPA, HIPAA BAA, EU SCCs, Quebec Law 25 TRA, and risk tier. |
| 6 | `search_privacy_policies` | Read-Only | Searches tenant-scoped internal privacy policies, AI governance standards, and retention schedules. |
| 7 | `evaluate_regulatory_applicability` | Read-Only | Runs the Jurisdictional Regulatory Applicability Engine (JRAE) across US Federal & 50 States, Canada Federal & 13 Provinces/Territories, and EU 27 Member States. |
| 8 | `route_approval_decision` | Consequential Write (Approval Gate) | Routes a workflow item to the DPO, CPO, and Legal Counsel human approval queue with an immutable audit trail entry. |

---

## Mandatory Enterprise Security Controls (Section 11)

- **Organization-Aware Identity & Permissions**: Every tool call validates `tenant_id`, `user_id`, and `role` against the authenticated session principal.
- **Strict Tenant Isolation (Acceptance Test 11)**: Any attempt by a caller authenticated to `tenant-ca` to query or retrieve records belonging to `tenant-us` immediately raises `PermissionError("CROSS_TENANT_ACCESS_DENIED: Tenant isolation boundary enforced")` (or HTTP `403 Forbidden`) and writes a security denial entry to `MCP_SECURITY_AUDIT_LOG`.
- **Read-Only by Default**: Write tools (`report_privacy_incident`, `initiate_privacy_assessment`, `route_approval_decision`) require an authorized role and an explicit write grant (`write_grant=True`), and only create draft/pending-approval records. External regulatory notifications are never auto-dispatched.
