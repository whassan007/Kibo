
import { z } from "zod";

export const DeployStageSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(["Pending", "In Progress", "Completed", "Blocked"]),
  gateType: z.enum(["Human", "Auto"]),
  currentAsset: z.string().optional(),
});

export type DeployStage = z.infer<typeof DeployStageSchema>;

export const fetchDeployLadder = async (): Promise<DeployStage[]> => {
    return [
        { id: "s1", name: "Attract", status: "Completed", gateType: "Auto", currentAsset: "Telemetry Module" },
        { id: "s2", name: "Acquire", status: "Completed", gateType: "Auto", currentAsset: "Intake Hooks" },
        { id: "s3", name: "Diagnose", status: "Completed", gateType: "Auto", currentAsset: "W-Method Audit" },
        { id: "s4", name: "Agree", status: "Completed", gateType: "Human", currentAsset: "SLA Commitments" },
        { id: "s5", name: "Install", status: "In Progress", gateType: "Human", currentAsset: "KIBO Privacy Inbox" },
        { id: "s6", name: "Operate", status: "Pending", gateType: "Auto" },
        { id: "s7", name: "Compound", status: "Pending", gateType: "Auto" },
    ];
};

export const submitDeployGate = async (stepId: string, decision: string, reason: string): Promise<string> => {
    console.log(`[MOCK API]: Attempting to submit ${decision} for gate ${stepId} with reason: ${reason}`);

    const MOCK_LATENCY_MS = 1500; 
    await new Promise(resolve => setTimeout(resolve, MOCK_LATENCY_MS));

    if (reason.toLowerCase().includes("test")) {
        console.error("[MOCK API]: Validation failed at business layer.");
        throw new Error("Sign-off justification cannot contain placeholder \"Test\" values.");
    }

    if (reason.toLowerCase().includes("criticalfail")) {
        console.error("[MOCK API]: Connection pool exhausted.");
        throw new Error("Violation of KIBO boundary GT-6: Database unresponsive.");
    }

    return `DEPLOY-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
};
