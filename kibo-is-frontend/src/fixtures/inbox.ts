
export const mockInboxItems = [
  { id: "1", type: "Breach", subject: "S3 Exposure", sender: "secops@kibo.local", received_at: "2026-07-06", sla_deadline: "61h", confidence: 0.95, suggested_route: "CPO", why: "PII exposed", body: "...", unread: 1, status: "pending" },
  { id: "2", type: "DSAR", subject: "Access Req", sender: "jdoe@test.com", received_at: "2026-07-01", sla_deadline: "27d", confidence: 0.88, suggested_route: "Agent", why: "Standard DSAR", body: "...", unread: 1, status: "pending" },
  { id: "3", type: "DSAR", subject: "Deletion", sender: "u@test.com", received_at: "2026-07-04", sla_deadline: "24d", confidence: 0.91, suggested_route: "Agent", why: "RTBF", body: "...", unread: 0, status: "pending" },
  { id: "4", type: "Opt-out", subject: "GPC Signal", sender: "sys@gpc.local", received_at: "2026-07-05", sla_deadline: "48h", confidence: 0.99, suggested_route: "Auto", why: "GPC flag", body: "...", unread: 1, status: "pending" },
  { id: "5", type: "Vendor", subject: "DPA Renewal", sender: "aws@aws.com", received_at: "2026-07-02", sla_deadline: "14d", confidence: 0.85, suggested_route: "Legal", why: "Annual DPA", body: "...", unread: 0, status: "pending" },
  { id: "6", type: "Unclassified", subject: "Urgent", sender: "unk@domain.com", received_at: "2026-07-06", sla_deadline: "72h", confidence: 0.41, suggested_route: "Triage", why: "Low confidence", body: "...", unread: 1, status: "pending" }
];
