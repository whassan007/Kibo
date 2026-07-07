
import { z } from "zod";
import { MeetingCreateSchema } from "../views/MeetingCreateForm";

export type MeetingCreatePayload = z.infer<typeof MeetingCreateSchema>;

export const createMeeting = async (payload: MeetingCreatePayload): Promise<void> => {
    console.log(`[MOCK API]: Attempting to schedule meeting: ${payload.meetingTitle}...`);

    const MOCK_LATENCY_MS = 1500; 
    await new Promise(resolve => setTimeout(resolve, MOCK_LATENCY_MS));

    if (payload.meetingTitle?.toLowerCase().includes("test")) {
        console.error("[MOCK API]: Validation failed at business layer.");
        throw new Error("The meeting title cannot contain placeholder \"Test\" values.");
    }

    if (payload.agenda?.toLowerCase().includes("criticalfail")) {
        console.error("[MOCK API]: Connection lost during write operation.");
        throw new Error("Connection pool exhaustion error. Cannot reach persistence layer.");
    }

    console.log(`[MOCK API]: Successfully scheduled meeting.`);
    return Promise.resolve();
};
