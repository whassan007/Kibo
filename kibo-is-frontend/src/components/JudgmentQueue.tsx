import React from 'react'
import { AlertCircle, Check, X, AlertTriangle, HelpCircle } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

export const JudgmentQueue: React.FC = () => {
  const { queue, resolveQueueItem, setHelpTopic } = useKiboStore()

  // Filter for pending items
  const pendingItems = queue?.queue.filter(item => item.status === 'pending') || []

  if (pendingItems.length === 0) {
    return (
      <div className="border border-bauhaus-mediumgrey p-12 bg-bauhaus-grey flex flex-col justify-center items-start">
        <div className="flex items-center space-x-2 text-bauhaus-accent mb-4">
          <AlertCircle size={20} />
          <h3 className="font-bold uppercase tracking-widest text-xs">Judgment Queue Empty</h3>
        </div>
        <h4 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white mb-2">
          No Pending Human Gates
        </h4>
        <p className="text-xs text-bauhaus-lightgrey leading-relaxed max-w-lg mb-6">
          The Judgment Queue (§13) lists batched, decision-ready tasks that require human operator approval. Currently, no crews are blocked on human gates.
        </p>
        <div className="border-t border-bauhaus-mediumgrey pt-6 w-full">
          <h5 className="text-[10px] text-bauhaus-accent uppercase tracking-widest font-bold mb-2">
            How to Populate This Queue
          </h5>
          <ol className="list-decimal list-inside text-[11px] text-bauhaus-lightgrey space-y-1.5 leading-normal">
            <li>Ensure a crew step is flagged with <code>gate_type: human</code> in <code>deployment-flow.yaml</code>.</li>
            <li>Dispatch a crew (e.g. <code>scout</code>, <code>installer</code>) to execute a gated action.</li>
            <li>The system will automatically halt execution and push the approval item to <code>queue.json</code>.</li>
          </ol>
        </div>
      </div>
    )
  }

  // Parse helper to enrich pending items with spec-based recommendations and details
  const getEnrichedDetails = (details: string) => {
    if (details.includes('Acquire') || details.includes('scout')) {
      return {
        recommendation: 'APPROVE',
        delegateReason: 'Requires human-to-human relationship handshake with PE partner (governed by §2 human reserve).',
        costOfWaiting: '+12% Acquire cycle time latency; delays platform pipeline acceleration.',
        options: ['Proceed with PE Handshake & warm introductions', 'Reject target and log feedback', 'Request additional Scout data analysis']
      }
    }
    if (details.includes('Install') || details.includes('installer')) {
      return {
        recommendation: 'APPROVE',
        delegateReason: 'Production cutover touches live customer data and represents an irreversible action (§8 boundary).',
        costOfWaiting: '+24h staging to production delay; client installation metrics stall.',
        options: ['Authorize production deploy cutover', 'Reject and halt staging deploy', 'Defer and request secondary telemetry audit']
      }
    }
    return {
      recommendation: 'APPROVE',
      delegateReason: 'Ambiguous or critical boundary action needing manual operator validation.',
      costOfWaiting: 'Stalls current crew action loop.',
      options: ['Approve and execute action', 'Reject and cancel crew mission', 'Defer to next weekly session']
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>Judgment Queue</span>
          <span className="text-xs bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-extrabold">{pendingItems.length}</span>
        </h2>
        <button 
          onClick={() => setHelpTopic('queue')} 
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1 text-xs"
        >
          <HelpCircle size={14} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Queue Spec</span>
        </button>
      </div>

      <div className="space-y-4">
        {pendingItems.map(item => {
          const enriched = getEnrichedDetails(item.details)
          return (
            <div key={item.id} className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey flex flex-col md:flex-row justify-between items-start md:items-stretch animate-fade-in">
              
              {/* Left Column: Decision Details */}
              <div className="flex-1 space-y-4 pr-6">
                <div>
                  <div className="text-[10px] text-bauhaus-lightgrey uppercase tracking-wider mb-1">
                    Decision ID: {item.id} · Received {new Date(item.timestamp).toLocaleTimeString()}
                  </div>
                  <h3 className="text-lg font-bold text-bauhaus-white uppercase tracking-tight leading-snug">
                    {item.details}
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <div className="text-bauhaus-accent font-bold uppercase tracking-wider text-[10px] mb-1">
                      Why Human Gated
                    </div>
                    <p className="text-bauhaus-lightgrey leading-relaxed">
                      {enriched.delegateReason}
                    </p>
                  </div>
                  <div>
                    <div className="text-bauhaus-yellow font-bold uppercase tracking-wider text-[10px] mb-1">
                      Cost of Waiting
                    </div>
                    <p className="text-bauhaus-lightgrey leading-relaxed">
                      {enriched.costOfWaiting}
                    </p>
                  </div>
                </div>

                {/* Labeled Options */}
                <div>
                  <div className="text-[10px] text-bauhaus-lightgrey uppercase tracking-widest font-bold mb-2">
                    Action Options
                  </div>
                  <ul className="space-y-1 text-xs text-bauhaus-lightgrey">
                    {enriched.options.map((opt, idx) => (
                      <li key={idx} className="flex items-center space-x-2">
                        <span className="w-1.5 h-1.5 bg-bauhaus-lightgrey"></span>
                        <span>{opt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Right Column: Labeled Recommendation & CTA Buttons */}
              <div className="w-full md:w-64 border-t md:border-t-0 md:border-l border-bauhaus-mediumgrey pt-4 md:pt-0 md:pl-6 flex flex-col justify-between items-stretch">
                <div>
                  <div className="text-[10px] text-bauhaus-lightgrey uppercase tracking-widest font-bold mb-1">
                    System Recommendation
                  </div>
                  <div className="flex items-center space-x-1.5 mb-4">
                    <AlertTriangle size={14} className="text-bauhaus-accent" />
                    <span className="text-sm font-extrabold text-bauhaus-accent tracking-wider uppercase">
                      {enriched.recommendation}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <button 
                    onClick={() => resolveQueueItem(item.id, 'resolved')}
                    className="w-full bg-bauhaus-accent text-bauhaus-black py-2 font-bold uppercase text-[10px] tracking-widest hover:bg-opacity-80 transition-all flex items-center justify-center space-x-1 border border-bauhaus-accent"
                  >
                    <Check size={12} />
                    <span>Approve</span>
                  </button>
                  <button 
                    onClick={() => resolveQueueItem(item.id, 'rejected')}
                    className="w-full border border-bauhaus-red text-bauhaus-red py-2 font-bold uppercase text-[10px] tracking-widest hover:bg-bauhaus-red hover:text-bauhaus-black transition-all flex items-center justify-center space-x-1"
                  >
                    <X size={12} />
                    <span>Reject</span>
                  </button>
                  <button 
                    onClick={() => resolveQueueItem(item.id, 'pending')}
                    className="w-full border border-bauhaus-lightgrey text-bauhaus-lightgrey py-2 font-bold uppercase text-[10px] tracking-widest hover:bg-bauhaus-white hover:text-bauhaus-black transition-all"
                  >
                    <span>Defer Action</span>
                  </button>
                </div>
              </div>

            </div>
          )
        })}
      </div>
    </div>
  )
}
