import React from 'react';
import { Check } from 'lucide-react';

const EmployeeMode = ({
  employeeRisks, employeeTraining, jurConfig, handleCompleteTraining,
  handleInventorySubmit, inventorySystem, setInventorySystem,
  inventoryDataTypes, setInventoryDataTypes, inventoryPurpose, setInventoryPurpose,
  inventoryRetention, setInventoryRetention, inventorySharing, setInventorySharing,
  inventoryStatus
}) => {
  return (
    <main className="flex-1 flex overflow-hidden bg-[#FAFAFA]">
      
      {/* Left side: My Risks & Training */}
      <div className="w-1/2 border-r border-[#E5E7EB] p-6 flex flex-col space-y-6 overflow-y-auto">
        
        {/* Risks Section */}
        <div className="space-y-3.5">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-500">My Assigned Compliance Risks</div>
          <div className="space-y-2.5">
            {employeeRisks.length === 0 ? (
              <div className="text-xs text-gray-400 italic">No risks currently assigned.</div>
            ) : (
              employeeRisks.map(r => (
                <div key={r.risk_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl text-[12px] space-y-2 shadow-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-blue-600 font-bold font-mono">{r.risk_id}</span>
                    <span className={`px-2 py-0.5 text-[9px] rounded-full uppercase font-bold border ${
                      r.risk_level === 'High' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                    }`}>{r.risk_level}</span>
                  </div>
                  <div className="text-[#111827]">{r.issue}</div>
                  <div className="flex justify-between text-gray-500 pt-2 text-[10px] border-t border-[#E5E7EB]">
                    <span>SLA Clock: {r.due_date}</span>
                    <span className="uppercase text-blue-600 font-semibold">Status: {r.status}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Training Section */}
        <div className="space-y-3.5">
          <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Assigned Role-Based Training ({jurConfig.primary_statute} Track)</div>
          <div className="space-y-2.5">
            {employeeTraining.map(mod => (
              <div key={mod.module_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl text-[12px] flex items-center justify-between shadow-xs">
                <div className="space-y-1">
                  <div className="font-semibold text-[#111827]">{mod.title}</div>
                  <div className="text-gray-500 text-[10px]">
                    Required: {mod.required ? 'YES' : 'NO'} | Duration: {mod.duration_min} min | Target: {mod.jurisdiction.toUpperCase()}
                  </div>
                </div>
                <div>
                  {mod.completed ? (
                    <span className="text-emerald-600 flex items-center space-x-1.5 font-semibold">
                      <Check size={14} />
                      <span>Done</span>
                    </span>
                  ) : (
                    <button
                      onClick={() => handleCompleteTraining(mod.module_id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-3 py-1.5 text-[9px] uppercase rounded-lg shadow-sm transition-all cursor-pointer"
                    >
                      Mark Done
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Right side: Data Inventory Contribution Form */}
      <div className="w-1/2 p-6 overflow-y-auto space-y-4">
        <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Data Inventory Contribution</div>
        <p className="text-xs text-gray-500 leading-relaxed">
          KIBO tracks all organizational storage systems. Log any files, systems, or tools that contain customer or employee datasets under your management.
        </p>
        
        <form onSubmit={handleInventorySubmit} className="space-y-4 max-w-md bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs">
          <div>
            <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">System/Database Name</label>
            <input 
              type="text" 
              required 
              value={inventorySystem}
              onChange={(e) => setInventorySystem(e.target.value)}
              className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
              placeholder="e.g. Clinical Records Cloud Store"
            />
          </div>
          <div>
            <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Data Types (Comma-separated)</label>
            <input 
              type="text" 
              required 
              value={inventoryDataTypes}
              onChange={(e) => setInventoryDataTypes(e.target.value)}
              className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
              placeholder="e.g. IP Address, Medical History, Full Name"
            />
          </div>
          <div>
            <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Purpose of Collection</label>
            <textarea 
              required 
              value={inventoryPurpose}
              onChange={(e) => setInventoryPurpose(e.target.value)}
              className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-16 resize-none transition-all shadow-xs" 
              placeholder="Provide description..."
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Retention Rule</label>
              <input 
                type="text" 
                required 
                value={inventoryRetention}
                onChange={(e) => setInventoryRetention(e.target.value)}
                className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                placeholder="e.g. 5 years"
              />
            </div>
            <div>
              <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Sharing / Third-Party Outflow</label>
              <input 
                type="text" 
                required 
                value={inventorySharing}
                onChange={(e) => setInventorySharing(e.target.value)}
                className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                placeholder="e.g. AnalyticsPro Inc."
              />
            </div>
          </div>
          <button 
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer"
          >
            Submit to Central Inventory
          </button>
        </form>

        {inventoryStatus === 'success' && (
          <div aria-live="polite" className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 text-[11px] rounded-lg font-semibold max-w-md">
            ✓ Inventory logged. Central system catalog updated.
          </div>
        )}

      </div>

    </main>
  );
};

export default EmployeeMode;
