
import React, { useState, useCallback } from "react";
import { z } from "zod";
import { fetchAndUpdateInventory } from "../services/inventoryService";

export const DataInventorySchema = z.object({
  dataOwner: z.string().min(2).max(100),
  dataSourceSystem: z.string().min(3).max(150),
  dataScopeDescription: z.string().min(10).max(500).optional(),
});

type DataInventoryFormValues = z.infer<typeof DataInventorySchema>;

export const DataInventoryForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const [formData, setFormData] = useState<DataInventoryFormValues>({
    dataOwner: "",
    dataSourceSystem: "",
    dataScopeDescription: ""
  });

  const onSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setIsSuccess(false);

    try {
      DataInventorySchema.parse(formData);
      await fetchAndUpdateInventory(formData); 
      setIsSuccess(true);
    } catch (err: any) {
      setError(err.errors ? "Validation Error" : `Failed to save inventory: ${err.message || err}`);
    } finally {
      setIsLoading(false);
    }
  }, [formData]);

  return (
    <div className="w-full max-w-2xl p-6 border rounded-lg shadow-sm bg-white">
      <h2 className="text-xl font-bold text-indigo-700 mb-2">Data Inventory Registration</h2>
      <p className="text-sm text-gray-500 mb-6">Establish End-to-End Data Flow Simulation</p>
      
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Data Owner</label>
          <input 
            className="w-full border p-2 rounded" 
            placeholder="e.g., Business Intelligence Dept." 
            value={formData.dataOwner}
            onChange={e => setFormData({...formData, dataOwner: e.target.value})}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Source System</label>
          <input 
            className="w-full border p-2 rounded" 
            placeholder="e.g., Snowflake/CRM_API" 
            value={formData.dataSourceSystem}
            onChange={e => setFormData({...formData, dataSourceSystem: e.target.value})}
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Data Scope Description</label>
          <textarea 
            className="w-full border p-2 rounded resize-none" 
            placeholder="Detailed description of data included..." 
            value={formData.dataScopeDescription}
            onChange={e => setFormData({...formData, dataScopeDescription: e.target.value})}
          />
        </div>

        <div className="pt-4 flex items-center justify-between gap-3">
          <button 
            type="submit" 
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
            disabled={isLoading || isSuccess}
          >
            {isLoading ? "Processing..." : "Submit & Update Inventory Record"}
          </button>

          {isSuccess && <div className="text-green-700 bg-green-50 p-2 rounded">Success! Simulation recorded.</div>}
          {error && <div className="text-red-700 bg-red-50 p-2 rounded">{error}</div>}
        </div>
      </form>
    </div>
  );
};
