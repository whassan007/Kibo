
export const MOCK_MEETINGS = [
  {
    id: "m1",
    title: "Weekly Privacy & Security Sync",
    type: "Weekly Sync",
    date: "2026-07-08T10:00:00Z",
    status: "Upcoming",
    attendees: ["CPO", "Engineering Lead"],
    agenda: ["Review open HITL tickets", "Discuss new FIPPA amendments"],
    minutes: "",
    actionItems: []
  },
  {
    id: "m2",
    title: "Q2 PSR Committee Review",
    type: "PSR Committee",
    date: "2026-06-15T14:00:00Z",
    status: "Completed",
    attendees: ["CPO", "External Auditor", "Legal Counsel"],
    agenda: ["Finalize Audit Report", "Approve Risk Exceptions"],
    minutes: "The committee reviewed the Q2 audit report. All risks accepted.",
    actionItems: [
      { id: "a1", assignee: "CPO", dueDate: "2026-07-01", linkedRisk: "RISK-092", status: "Closed" }
    ]
  }
];
