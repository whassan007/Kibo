import React, { useState } from 'react'
import { FileCode, CornerDownRight, ChevronDown, ChevronUp } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'
import { DeployabilityLadder } from './DeployabilityLadder'
import type { RungType } from './DeployabilityLadder'
import { WMethodStack } from './WMethodStack'

const getLayerForTarget = (target: string): number => {
  const t = target.toLowerCase()
  if (t.includes('forge') || t.includes('autonomy:promote')) return 7
  if (t.includes('operator') || t.includes('telemetry') || t.includes('monitor')) return 6
  if (t.includes('installer') || t.includes('staging') || t.includes('deploy:')) return 5
  if (t.includes('steward') || t.includes('agreement') || t.includes('handshake')) return 4
  if (t.includes('diagnostician') || t.includes('audit')) return 3
  if (t.includes('scout') || t.includes('reach_out') || t.includes('wedge')) return 2
  if (t.includes('herald') || t.includes('brand')) return 1
  return 1
}

const getTransitionForTarget = (target: string): { before: RungType; after: RungType } | undefined => {
  const t = target.toLowerCase()
  if (t.includes('reach_out') || t.includes('promote') || t.includes('handshake')) {
    return { before: 'waël-only', after: 'agent-deployable' }
  }
  return undefined
}

export const ProposalInbox: React.FC = () => {
  const { proposals, promoteProposal, rejectProposal } = useKiboStore()
  const [expandedDiffs, setExpandedDiffs] = useState<Record<string, boolean>>({})

  const toggleDiff = (id: string) => {
    setExpandedDiffs(prev => ({ ...prev, [id]: !prev[id] }))
  }

  // Filter for active proposed/reviewed items
  const activeProposals = proposals.filter(p => p.status === 'proposed' || p.status === 'reviewed')

  if (activeProposals.length === 0) {
    return (
      <div className="border border-bauhaus-mediumgrey p-12 bg-bauhaus-grey flex flex-col justify-center items-start">
        <div className="flex items-center space-x-2 text-bauhaus-accent mb-4">
          <FileCode size={20} />
          <h3 className="font-bold uppercase tracking-widest text-xs">Proposal Inbox Empty</h3>
        </div>
        <h4 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white mb-2">
          No Active Proposals
        </h4>
        <p className="text-xs text-bauhaus-lightgrey leading-relaxed max-w-lg mb-6">
          The Proposal Inbox (§10.4) displays proposals submitted by agent crews to climb the deployability ladder or expand autonomy grants based on validated telemetry feedback.
        </p>
        <div className="border-t border-bauhaus-mediumgrey pt-6 w-full">
          <h5 className="text-[10px] text-bauhaus-accent uppercase tracking-widest font-bold mb-2">
            How to Populate This Inbox
          </h5>
          <ol className="list-decimal list-inside text-[11px] text-bauhaus-lightgrey space-y-1.5 leading-normal">
            <li>Have the <code>forge</code> crew compile configuration modifications.</li>
            <li>Submit the proposal using the <code>proposal.write</code> tool containing supporting telemetry/feedback log IDs.</li>
            <li>The proposal draft will appear here as an unpromoted record.</li>
          </ol>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-2">
        <h2 className="text-xs font-bold uppercase tracking-widest text-bauhaus-lightgrey">
          Proposal Inbox ({activeProposals.length})
        </h2>
      </div>

      <div className="space-y-6">
        {activeProposals.map(prop => {
          const targetLayer = getLayerForTarget(prop.target)
          const transition = getTransitionForTarget(prop.target)
          const isExpanded = expandedDiffs[prop.id] || false

          return (
            <div key={prop.id} className="border border-bauhaus-mediumgrey bg-bauhaus-grey p-6 flex flex-col lg:flex-row gap-6 font-mono text-xs select-none">
              
              {/* Left Column: Metrics, Details, Actions */}
              <div className="flex-1 space-y-4">
                {/* Header */}
                <div className="border-b border-bauhaus-mediumgrey pb-3">
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider mb-0.5">
                    Proposal ID: {prop.id} · Semver Bump: <span className="text-bauhaus-accent font-bold uppercase">{prop.semver_bump}</span>
                  </div>
                  <h3 className="text-lg font-bold text-bauhaus-white uppercase tracking-tight">
                    Target: {prop.target}
                  </h3>
                </div>

                {/* Rationale */}
                <div>
                  <div className="text-bauhaus-accent font-bold uppercase tracking-wider text-[9px] mb-1">
                    Rationale
                  </div>
                  <p className="text-bauhaus-lightgrey leading-relaxed text-[11px]">
                    {prop.rationale}
                  </p>
                </div>

                {/* Metrics as visual blocks */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="border border-bauhaus-mediumgrey p-2.5 bg-bauhaus-black flex flex-col items-center justify-center text-center">
                    <span className="text-[8px] text-bauhaus-lightgrey uppercase tracking-wider mb-1">CAC EFFECT</span>
                    <span className="text-base font-bold text-bauhaus-accent flex items-center gap-0.5">
                      ↓ {prop.expected_effect.cac || '«placeholder»'}
                    </span>
                  </div>
                  <div className="border border-bauhaus-mediumgrey p-2.5 bg-bauhaus-black flex flex-col items-center justify-center text-center">
                    <span className="text-[8px] text-bauhaus-lightgrey uppercase tracking-wider mb-1">⟐ GATES</span>
                    <span className="text-base font-bold text-bauhaus-yellow flex items-center gap-0.5">
                      ↓ {prop.expected_effect.gates_per_deployment}
                    </span>
                  </div>
                  <div className="border border-bauhaus-mediumgrey p-2.5 bg-bauhaus-black flex flex-col items-center justify-center text-center">
                    <span className="text-[8px] text-bauhaus-lightgrey uppercase tracking-wider mb-1">FOUNDER DEP.</span>
                    <span className="text-base font-bold text-bauhaus-red flex items-center gap-0.5">
                      ↓ {prop.expected_effect.founder_dependence}
                    </span>
                  </div>
                </div>

                {/* Collapsible details section */}
                <div className="border border-bauhaus-mediumgrey">
                  <button
                    onClick={() => toggleDiff(prop.id)}
                    className="flex justify-between items-center w-full p-2.5 bg-bauhaus-black hover:bg-bauhaus-mediumgrey/30 transition-colors uppercase text-[9px] font-bold text-bauhaus-lightgrey"
                  >
                    <span>Proposed Diff & Supporting Telemetry</span>
                    {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>

                  {isExpanded && (
                    <div className="p-3 border-t border-bauhaus-mediumgrey bg-bauhaus-black space-y-3">
                      <div>
                        <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider mb-1">Proposed Code/Config Diff</div>
                        <pre className="bg-bauhaus-grey p-3 border border-bauhaus-mediumgrey overflow-x-auto text-[10px] text-bauhaus-lightgrey leading-relaxed">
                          {prop.diff}
                        </pre>
                      </div>

                      {prop.evidence && prop.evidence.length > 0 && (
                        <div>
                          <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider mb-1 flex items-center gap-1">
                            <CornerDownRight size={10} />
                            <span>Supporting Evidence Logs</span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {prop.evidence.map((ev, i) => (
                              <span key={i} className="bg-bauhaus-mediumgrey text-bauhaus-white px-2 py-0.5 text-[9px]">
                                {ev}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-2">
                  <button 
                    onClick={() => promoteProposal(prop.id)}
                    className="flex-1 bg-bauhaus-accent text-bauhaus-black py-2.5 font-bold uppercase text-[10px] tracking-widest hover:bg-opacity-80 transition-all border border-bauhaus-accent animate-pulse"
                  >
                    Promote (Human-Only Gate)
                  </button>
                  <button 
                    onClick={() => rejectProposal(prop.id)}
                    className="border border-bauhaus-red text-bauhaus-red px-6 py-2.5 font-bold uppercase text-[10px] tracking-widest hover:bg-bauhaus-red hover:text-bauhaus-black transition-all"
                  >
                    Reject
                  </button>
                </div>
              </div>

              {/* Right Column: Visual Sidebars / Locators */}
              <div className="w-full lg:w-48 flex flex-row lg:flex-col gap-4 border-t lg:border-t-0 lg:border-l border-bauhaus-mediumgrey pt-4 lg:pt-0 lg:pl-4">
                <div className="flex-1">
                  <WMethodStack activeLayer={targetLayer} />
                </div>
                {transition && (
                  <div className="flex-1">
                    <DeployabilityLadder transition={transition} />
                  </div>
                )}
              </div>

            </div>
          )
        })}
      </div>
    </div>
  )
}
