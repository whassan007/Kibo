
import React, { useState, useEffect } from "react";
import { fetchTrustTiers, promoteAgent, type TrustTier } from "../services/trustService";

export const TrustTiers: React.FC = () => {
  const [tiers, setTiers] = useState<TrustTier[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [promoteReason, setPromoteReason] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("agent-alpha");

  useEffect(() => {
    fetchTrustTiers().then(data => {
      setTiers(data);
      setIsLoading(false);
    });
  }, []);

  const handlePromote = async () => {
    if (!promoteReason || promoteReason.length < 5) {
      setError("Please provide a valid justification (min 5 chars).");
      return;
    }

    if (!window.confirm(`Are you sure you want to promote ${selectedAgent}? This alters autonomy scope.`)) {
        return;
    }

    setActionLoading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const auditRef = await promoteAgent(selectedAgent, promoteReason);
      setSuccessMsg(`Successfully promoted agent. Audit Ref: ${auditRef}`);
      setPromoteReason("");
    } catch (err: any) {
      setError(err.message || "Failed to promote agent.");
    } finally {
      setActionLoading(false);
    }
  };

  if (isLoading) return <div className="p-8">Loading Trust Tiers...</div>;

  return (
    <div className="w-full max-w-5xl p-6">
      <h2 className="text-2xl font-bold mb-6">Autonomy Trust Tiers</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {tiers.map(tier => (
          <div key={tier.id} className="border p-4 rounded-lg shadow-sm bg-white">
            <h3 className="font-bold text-lg mb-2">{tier.name}</h3>
            <div className="text-sm text-gray-600 mb-2">Gate: <span className="font-semibold">{tier.gateType}</span></div>
            <div className="text-sm text-gray-600 mb-4">Active Agents: {tier.activeAgents}</div>
            
            <div className="text-sm font-semibold mb-1">Allowed Scopes:</div>
            <ul className="list-disc pl-5 text-sm">
              {tier.allowedScopes.map(s => <li key={s}>{s}</li>)}
            </ul>
          </div>
        ))}
      </div>

      <div className="border p-6 rounded-lg bg-gray-50 max-w-lg">
        <h3 className="font-bold text-lg mb-4 text-red-800">Agent Promotion Actions</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Target Agent</label>
            <input 
              className="w-full border p-2 rounded bg-white" 
              value={selectedAgent}
              onChange={e => setSelectedAgent(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Justification (Audited)</label>
            <textarea 
              className="w-full border p-2 rounded h-24 bg-white" 
              placeholder="Why is this agent being promoted..."
              value={promoteReason}
              onChange={e => setPromoteReason(e.target.value)}
            />
          </div>

          <button 
            className="w-full bg-red-700 text-white font-bold py-2 rounded disabled:opacity-50"
            onClick={handlePromote}
            disabled={actionLoading}
          >
            {actionLoading ? "Processing Promotion..." : "Promote Agent (Requires Sign-off)"}
          </button>
          
          {error && <div className="text-red-700 bg-red-50 p-2 rounded border border-red-200">{error}</div>}
          {successMsg && <div className="text-green-700 bg-green-50 p-2 rounded border border-green-200">{successMsg}</div>}
        </div>
      </div>
    </div>
  );
};
