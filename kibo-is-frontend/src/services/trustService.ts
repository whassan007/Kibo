
import { z } from "zod";

export const TierSchema = z.object({
  id: z.string(),
  name: z.string(),
  allowedScopes: z.array(z.string()),
  gateType: z.enum(["Human", "Auto"]),
  activeAgents: z.number(),
});

export type TrustTier = z.infer<typeof TierSchema>;

export const fetchTrustTiers = async (): Promise<TrustTier[]> => {
    return [
        { id: "t1", name: "Tier 1: Read-Only Triage", allowedScopes: ["Inbox Read", "Tagging"], gateType: "Auto", activeAgents: 3 },
        { id: "t2", name: "Tier 2: Mediated Drafting", allowedScopes: ["Draft Responses", "Propose Routes"], gateType: "Human", activeAgents: 2 },
        { id: "t3", name: "Tier 3: Autonomous Exec", allowedScopes: ["All T1/T2", "Commit Changes"], gateType: "Human", activeAgents: 0 },
    ];
};

export const promoteAgent = async (agentId: string, reason: string): Promise<string> => {
    console.log(`[MOCK API]: Attempting to promote agent ${agentId} for reason: ${reason}`);

    const MOCK_LATENCY_MS = 1500; 
    await new Promise(resolve => setTimeout(resolve, MOCK_LATENCY_MS));

    if (reason.toLowerCase().includes("test")) {
        console.error("[MOCK API]: Validation failed at business layer.");
        throw new Error("Promotion justification cannot contain placeholder \"Test\" values.");
    }

    if (agentId.toLowerCase().includes("criticalfail")) {
        console.error("[MOCK API]: Autonomy boundary validation failed.");
        throw new Error("Violation of KIBO boundary #5: Agent blocklisted.");
    }

    return `AUDIT-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
};
