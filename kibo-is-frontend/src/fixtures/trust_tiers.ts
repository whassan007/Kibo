
// kibo-is-frontend/src/fixtures/trust_tiers.ts

export const MOCK_TRUST_TIERS = [
  {
    id: "t1",
    name: "Tier 1: Read-Only Triage",
    allowedScopes: ["Inbox Read", "Tagging", "Context Retrieval"],
    gateType: "Auto",
    activeAgents: 3
  },
  {
    id: "t2",
    name: "Tier 2: Mediated Drafting",
    allowedScopes: ["Draft Responses", "Propose Routes", "Schedule Meetings"],
    gateType: "Human",
    activeAgents: 2
  },
  {
    id: "t3",
    name: "Tier 3: Autonomous Exec",
    allowedScopes: ["All T1/T2", "Commit File Changes", "Deploy Configuration"],
    gateType: "Human",
    activeAgents: 0
  }
];
