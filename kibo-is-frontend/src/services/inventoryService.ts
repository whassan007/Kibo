
import { z } from "zod";
import { DataInventorySchema } from "../views/DataInventoryForm";

export type InventoryUpdatePayload = z.infer<typeof DataInventorySchema>;

export const fetchAndUpdateInventory = async (payload: InventoryUpdatePayload): Promise<void> => {
    console.log(`[MOCK API]: Attempting to save inventory for Owner: ${payload.dataOwner}...`);

    const MOCK_LATENCY_MS = 1500; 
    await new Promise(resolve => setTimeout(resolve, MOCK_LATENCY_MS));

    if (payload.dataOwner?.toLowerCase().includes("test")) {
        console.error("[MOCK API]: Validation failed at business layer.");
        throw new Error("The provided Data Owner field cannot contain placeholder "Test" values during simulation rollout.");
    }

    if (payload.dataSourceSystem?.toLowerCase().includes("criticalfail")) {
        console.error("[MOCK API]: Connection lost during write operation.");
        throw new Error("Connection pool exhaustion error. Cannot reach persistence layer.");
    }

    console.log(`[MOCK API]: Successfully committed record for ${payload.dataSourceSystem}.`);
    return Promise.resolve();
};
