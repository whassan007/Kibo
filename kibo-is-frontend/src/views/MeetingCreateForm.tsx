
import React, { useState, useCallback } from "react";
import { z } from "zod";
import { createMeeting } from "../services/meetingService";

export const MeetingCreateSchema = z.object({
  meetingTitle: z.string().min(3, "Title must be at least 3 characters").max(100),
  scheduledTime: z.string().min(1, "Scheduled time is required"),
  participants: z.string().min(3, "Must include at least one participant"),
  agenda: z.string().min(10, "Agenda must be at least 10 characters").max(2000),
});

type MeetingCreateFormValues = z.infer<typeof MeetingCreateSchema>;

export const MeetingCreateForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [formData, setFormData] = useState<MeetingCreateFormValues>({
    meetingTitle: "",
    scheduledTime: "",
    participants: "",
    agenda: ""
  });

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setIsSuccess(false);

    try {
      MeetingCreateSchema.parse(formData);
      await createMeeting(formData); 
      setIsSuccess(true);
    } catch (err: any) {
      if (err.errors) {
        setError(err.errors[0]?.message || "Validation Error");
      } else {
        setError(`Failed to create meeting: ${err.message || err}`);
      }
    } finally {
      setIsLoading(false);
    }
  }, [formData]);

  return (
    <div className="w-full max-w-2xl p-6 border rounded-lg shadow-sm bg-white">
      <h2 className="text-xl font-bold text-indigo-700 mb-2">Schedule Meeting</h2>
      <p className="text-sm text-gray-500 mb-6">Create a new compliance review session.</p>
      
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Meeting Title</label>
          <input 
            className="w-full border p-2 rounded" 
            placeholder="e.g., Q3 DSAR Review" 
            value={formData.meetingTitle}
            onChange={e => setFormData({...formData, meetingTitle: e.target.value})}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Scheduled Time</label>
          <input 
            type="datetime-local"
            className="w-full border p-2 rounded"
            value={formData.scheduledTime}
            onChange={e => setFormData({...formData, scheduledTime: e.target.value})}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Participants (Comma Separated Emails)</label>
          <input 
            className="w-full border p-2 rounded" 
            placeholder="e.g., dpo@kibo.is, legal@kibo.is" 
            value={formData.participants}
            onChange={e => setFormData({...formData, participants: e.target.value})}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Agenda</label>
          <textarea 
            className="w-full border p-2 rounded resize-none h-32" 
            placeholder="Detailed meeting agenda..." 
            value={formData.agenda}
            onChange={e => setFormData({...formData, agenda: e.target.value})}
          />
        </div>

        <div className="pt-4 flex items-center justify-between gap-3">
          <button 
            type="submit" 
            className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
            disabled={isLoading || isSuccess}
          >
            {isLoading ? "Scheduling..." : "Schedule Meeting"}
          </button>

          {isSuccess && <div className="text-green-700 bg-green-50 p-2 rounded border border-green-200">Success! Meeting scheduled.</div>}
          {error && <div className="text-red-700 bg-red-50 p-2 rounded border border-red-200">{error}</div>}
        </div>
      </form>
    </div>
  );
};
