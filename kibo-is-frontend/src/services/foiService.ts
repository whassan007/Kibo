
import { z } from "zod";
import { FoiSubmitSchema } from "../views/FOISubmitForm";

export type FoiSubmitPayload = z.infer<typeof FoiSubmitSchema>;

export const submitFoiRequest = async (payload: FoiSubmitPayload): Promise<void> => {
    console.log(`[MOCK API]: Attempting to submit FOI request for ${payload.requesterName}...`);

    const MOCK_LATENCY_MS = 1500; 
    await new Promise(resolve => setTimeout(resolve, MOCK_LATENCY_MS));

    if (payload.requesterName?.toLowerCase().includes("test")) {
        console.error("[MOCK API]: Validation failed at business layer.");
        throw new Error("The requester name cannot contain placeholder \"Test\" values.");
    }

    if (payload.requestDescription?.toLowerCase().includes("criticalfail")) {
        console.error("[MOCK API]: Connection lost during write operation.");
        throw new Error("Connection pool exhaustion error. Cannot reach persistence layer.");
    }

    console.log(`[MOCK API]: Successfully committed FOI request.`);
    return Promise.resolve();
};
