
import React, { useState, useCallback } from "react";
import { z } from "zod";
import { submitFoiRequest } from "../services/foiService";

export const FoiSubmitSchema = z.object({
  requesterName: z.string().min(2, "Name must be at least 2 characters").max(100),
  requestType: z.enum(["Public Records", "Internal Communications", "Financial Data", "Other"]),
  requestDescription: z.string().min(20, "Description must be at least 20 characters").max(2000),
});

type FoiSubmitFormValues = z.infer<typeof FoiSubmitSchema>;

export const FOISubmitForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [formData, setFormData] = useState<FoiSubmitFormValues>({
    requesterName: "",
    requestType: "Public Records",
    requestDescription: ""
  });

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setIsSuccess(false);

    try {
      FoiSubmitSchema.parse(formData);
      await submitFoiRequest(formData); 
      setIsSuccess(true);
    } catch (err: any) {
      if (err.errors) {
        setError(err.errors[0]?.message || "Validation Error");
      } else {
        setError(`Failed to submit: ${err.message || err}`);
      }
    } finally {
      setIsLoading(false);
    }
  }, [formData]);

  return (
    <div className="w-full max-w-2xl p-6 border rounded-lg shadow-sm bg-white">
      <h2 className="text-xl font-bold text-red-700 mb-2">FOI Request Submission</h2>
      <p className="text-sm text-gray-500 mb-6">Freedom of Information Act processing simulation.</p>
      
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Requester Name</label>
          <input 
            className="w-full border p-2 rounded" 
            placeholder="e.g., Jane Doe" 
            value={formData.requesterName}
            onChange={e => setFormData({...formData, requesterName: e.target.value})}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Request Category</label>
          <select 
            className="w-full border p-2 rounded"
            value={formData.requestType}
            onChange={e => setFormData({...formData, requestType: e.target.value as any})}
          >
            <option value="Public Records">Public Records</option>
            <option value="Internal Communications">Internal Communications</option>
            <option value="Financial Data">Financial Data</option>
            <option value="Other">Other</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Request Description</label>
          <textarea 
            className="w-full border p-2 rounded resize-none h-32" 
            placeholder="Detailed description of the requested information (min 20 characters)..." 
            value={formData.requestDescription}
            onChange={e => setFormData({...formData, requestDescription: e.target.value})}
          />
        </div>

        <div className="pt-4 flex items-center justify-between gap-3">
          <button 
            type="submit" 
            className="bg-red-600 text-white px-4 py-2 rounded disabled:opacity-50"
            disabled={isLoading || isSuccess}
          >
            {isLoading ? "Processing..." : "Submit FOI Request"}
          </button>

          {isSuccess && <div className="text-green-700 bg-green-50 p-2 rounded border border-green-200">Success! Request filed.</div>}
          {error && <div className="text-red-700 bg-red-50 p-2 rounded border border-red-200">{error}</div>}
        </div>
      </form>
    </div>
  );
};
