
import React, { useState, useEffect } from "react";
import { fetchDeployLadder, submitDeployGate, type DeployStage } from "../services/deployService";

export const DeploymentCenter: React.FC = () => {
  const [stages, setStages] = useState<DeployStage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    fetchDeployLadder().then(data => {
      setStages(data);
      setIsLoading(false);
    });
  }, []);

  const handleSignOff = async (stage: DeployStage) => {
    const reason = window.prompt(`Enter justification for signing off on ${stage.name}:`);
    if (reason === null) return;
    
    if (reason.length < 5) {
      setError("Please provide a valid justification (min 5 chars).");
      return;
    }

    setActionLoading(stage.id);
    setError(null);
    setSuccessMsg(null);

    try {
      const auditRef = await submitDeployGate(stage.id, "Approve", reason);
      setSuccessMsg(`Successfully signed off ${stage.name}. Audit Ref: ${auditRef}`);
      
      // Update local state to reflect completion
      setStages(prev => prev.map(s => s.id === stage.id ? { ...s, status: "Completed" } : s));
    } catch (err: any) {
      setError(err.message || `Failed to sign off on ${stage.name}.`);
    } finally {
      setActionLoading(null);
    }
  };

  if (isLoading) return <div className="p-8">Loading Deployment Center...</div>;

  return (
    <div className="w-full max-w-6xl p-6">
      <h2 className="text-2xl font-bold mb-2">Deployment Center</h2>
      <p className="text-sm text-gray-500 mb-8">W-Method 7-layer deployment flow governance.</p>

      {error && <div className="mb-4 text-red-700 bg-red-50 p-3 rounded border border-red-200">{error}</div>}
      {successMsg && <div className="mb-4 text-green-700 bg-green-50 p-3 rounded border border-green-200">{successMsg}</div>}
      
      <div className="flex flex-col md:flex-row gap-4 overflow-x-auto pb-4">
        {stages.map((stage, index) => (
          <div key={stage.id} className="min-w-[200px] flex-1 border p-4 rounded-lg shadow-sm bg-white flex flex-col relative">
            <div className="text-xs font-bold text-gray-400 mb-1">STAGE {index + 1}</div>
            <h3 className="font-bold text-lg mb-2">{stage.name}</h3>
            
            <div className="mb-4">
              <span className={`px-2 py-1 text-xs rounded-full font-semibold
                ${stage.status === "Completed" ? "bg-green-100 text-green-800" : 
                  stage.status === "In Progress" ? "bg-blue-100 text-blue-800" : 
                  "bg-gray-100 text-gray-800"}`}>
                {stage.status}
              </span>
            </div>

            <div className="text-sm text-gray-600 mb-2">Gate: <span className="font-semibold">{stage.gateType}</span></div>
            {stage.currentAsset && <div className="text-sm text-indigo-700 font-medium mb-4 truncate">{stage.currentAsset}</div>}
            
            <div className="mt-auto pt-4">
                {stage.gateType === "Human" && stage.status !== "Completed" ? (
                    <button 
                        className="w-full bg-indigo-700 text-white font-bold py-2 rounded text-sm disabled:opacity-50"
                        onClick={() => handleSignOff(stage)}
                        disabled={actionLoading !== null}
                    >
                        {actionLoading === stage.id ? "Signing Off..." : "Sign Off"}
                    </button>
                ) : (
                    <div className="w-full text-center py-2 text-sm text-gray-400 border border-transparent">
                        {stage.gateType === "Auto" ? "Auto-Gated" : "Locked"}
                    </div>
                )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
