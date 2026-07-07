import React from 'react'

export interface LifecycleNode {
  step: number
  name: string
  crew: string
  gate: string
  gate_type: 'human' | 'artifact' | 'none'
}

const NODES: LifecycleNode[] = [
  { step: 1, name: 'Attract', crew: 'herald', gate: 'none', gate_type: 'none' },
  { step: 2, name: 'Acquire', crew: 'scout', gate: 'human_handshake', gate_type: 'human' },
  { step: 3, name: 'Diagnose', crew: 'diagnostician', gate: 'audit_report_generation', gate_type: 'artifact' },
  { step: 4, name: 'Agree', crew: 'steward', gate: 'human_signs_terms', gate_type: 'human' },
  { step: 5, name: 'Install', crew: 'installer', gate: 'human_approves_production', gate_type: 'human' },
  { step: 6, name: 'Operate', crew: 'operator', gate: 'telemetry_baseline', gate_type: 'artifact' },
  { step: 7, name: 'Compound', crew: 'forge', gate: 'human_promotes_proposal', gate_type: 'human' },
]

interface DeploymentToken {
  client: string
  stage: string
  value: number
}

interface LifecycleTrackProps {
  activeStep?: number
  deployments?: DeploymentToken[]
  onNodeClick?: (step: number) => void
}

export const LifecycleTrack: React.FC<LifecycleTrackProps> = ({
  activeStep,
  deployments = [],
  onNodeClick,
}) => {
  return (
    <div className="flex flex-col w-full font-mono text-xs p-4 border border-bauhaus-mediumgrey bg-bauhaus-grey">
      <div className="text-[10px] uppercase tracking-wider text-bauhaus-lightgrey mb-6 border-b border-bauhaus-mediumgrey pb-1">
        Deployment Lifecycle Track (§9)
      </div>

      <div className="relative flex justify-between items-center w-full py-8">
        {/* Horizontal Connecting Line */}
        <div className="absolute left-0 right-0 h-[1px] bg-bauhaus-mediumgrey z-0" />

        {NODES.map((node) => {
          const isHuman = node.gate_type === 'human'
          const isArtifact = node.gate_type === 'artifact'
          const isActive = activeStep === node.step
          
          // Match deployments to this stage (case-insensitive name check)
          const matchedDeployments = deployments.filter(
            (d) => d.stage.toLowerCase() === node.name.toLowerCase()
          )

          return (
            <div
              key={node.step}
              onClick={() => onNodeClick?.(node.step)}
              className={`relative flex flex-col items-center z-10 select-none ${
                onNodeClick ? 'cursor-pointer' : ''
              }`}
              style={{ width: `${100 / NODES.length}%` }}
            >
              {/* Step Info Above Node */}
              <div className="absolute bottom-8 text-center flex flex-col items-center">
                <span className="text-[9px] text-bauhaus-lightgrey uppercase tracking-tighter">L{node.step}</span>
                <span className={`font-bold text-[10px] ${isActive ? 'text-bauhaus-accent' : 'text-bauhaus-white'}`}>
                  {node.name}
                </span>
              </div>

              {/* Node Geometry */}
              <div
                className={`w-7 h-7 flex items-center justify-center border transition-all ${
                  isActive
                    ? 'border-bauhaus-accent bg-bauhaus-black'
                    : 'border-bauhaus-mediumgrey bg-bauhaus-black'
                }`}
              >
                {isHuman ? (
                  /* Human Gate: filled square/triangle functional accent */
                  <div className="w-3.5 h-3.5 bg-bauhaus-accent" title="Human Gate" />
                ) : isArtifact ? (
                  /* Artifact Gate: simple outline box inside */
                  <div className="w-2.5 h-2.5 border border-bauhaus-lightgrey" title="Artifact Gate" />
                ) : (
                  /* Automatic/None: dot */
                  <div className="w-1.5 h-1.5 rounded-none bg-bauhaus-mediumgrey" title="Automated Stage" />
                )}
              </div>

              {/* Step Info Below Node */}
              <div className="absolute top-8 text-center flex flex-col items-center min-h-[30px]">
                <span className="text-[9px] text-bauhaus-lightgrey uppercase">{node.crew}</span>
                {node.gate_type === 'human' && (
                  <span className="text-[8px] text-bauhaus-accent font-bold mt-0.5">⟐ GATE</span>
                )}
              </div>

              {/* Deployment Tokens stacked on top of node */}
              {matchedDeployments.length > 0 && (
                <div className="absolute -top-12 flex flex-col gap-1 items-center">
                  {matchedDeployments.map((dep, idx) => (
                    <div
                      key={idx}
                      className="px-2 py-0.5 bg-bauhaus-accent text-bauhaus-white font-bold text-[9px] border border-bauhaus-mediumgrey whitespace-nowrap"
                      title={`${dep.client} ($${dep.value.toLocaleString()})`}
                    >
                      {dep.client.substring(0, 8)}..
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {deployments.length === 0 && (
        <div className="mt-8 p-3 border border-dashed border-bauhaus-mediumgrey text-bauhaus-lightgrey text-[10px] text-center">
          <span className="font-bold text-bauhaus-yellow">NO ACTIVE CLIENT DEPLOYMENTS</span>. To track client tokens here, append records to:
          <code className="block mt-1 bg-bauhaus-black p-1 text-[9px] text-bauhaus-white">
            .kibo/state/growth/pipeline.jsonl
          </code>
          Format: <code className="text-bauhaus-white">{"{\"client\": \"Acme Corp\", \"stage\": \"Acquire\", \"value\": 12000}"}</code>
        </div>
      )}
    </div>
  )
}
