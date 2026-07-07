import React, { useState } from 'react'
import { HelpCircle, Layers, UserCheck } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'
import { LifecycleTrack } from './LifecycleTrack'

export const DeploymentPipeline: React.FC = () => {
  const { setHelpTopic, pipeline } = useKiboStore()
  const [selectedStep, setSelectedStep] = useState<number | null>(null)

  // Mapped steps from deployment-flow.yaml
  const STEPS_DATA = [
    { num: 1, name: 'Attract', crew: 'herald', gate: 'none', gateType: 'none', desc: 'Category-exclusive brand building & thought leadership' },
    { num: 2, name: 'Acquire', crew: 'scout', gate: 'human_handshake', gateType: 'human', desc: 'Identify & qualify mid-market targets, establish contact' },
    { num: 3, name: 'Diagnose', crew: 'diagnostician', gate: 'audit_report_generation', gateType: 'artifact', desc: 'Run W-Method diagnostics, generate local stack maturity map' },
    { num: 4, name: 'Agree', crew: 'steward', gate: 'human_signs_terms', gateType: 'human', desc: 'Establish pricing, scopes, and sign Agrement' },
    { num: 5, name: 'Install', crew: 'installer', gate: 'human_approves_production', gateType: 'human', desc: 'Surgical software module staging and target client production integration' },
    { num: 6, name: 'Operate', crew: 'operator', gate: 'telemetry_baseline', gateType: 'artifact', desc: 'Continuous telemetry logging, evaluations, and baseline security verification' },
    { num: 7, name: 'Compound', crew: 'forge', gate: 'human_promotes_proposal', gateType: 'human', desc: 'Continuous improvement loop, self-improving code proposals' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>Deployment Pipeline</span>
          <span className="text-xs bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-extrabold">7 Steps Track</span>
        </h2>
        <button 
          onClick={() => setHelpTopic('pipeline')} 
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1 text-xs"
        >
          <HelpCircle size={14} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Pipeline Spec</span>
        </button>
      </div>

      {/* Visual Lifecycle Track at the top */}
      <LifecycleTrack 
        deployments={pipeline} 
        activeStep={selectedStep || undefined}
        onNodeClick={(step) => setSelectedStep(step)}
      />

      {/* Pipeline Description & Step Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono text-xs select-none">
        <div className="lg:col-span-2 space-y-4">
          <p className="text-xs text-bauhaus-lightgrey leading-relaxed">
            The KIBO OS client lifecycle (§9) executes bottom-up foundation stabilization (Layers 1, 2, 6) first, followed by top-down value delivery (Layers 3, 4, 5, 7). All steps flagged with a human gate (⟐) automatically pause agent autonomy and route directly to the Judgment Queue. Click any node above to drill down.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {STEPS_DATA.map((step) => {
              const isHuman = step.gateType === 'human'
              const isSelected = selectedStep === step.num

              return (
                <div 
                  key={step.num}
                  onClick={() => setSelectedStep(step.num)}
                  className={`border p-3 flex flex-col justify-between cursor-pointer transition-all ${
                    isSelected 
                      ? 'border-bauhaus-white bg-bauhaus-black' 
                      : isHuman 
                        ? 'border-bauhaus-accent/50 bg-bauhaus-black/40' 
                        : 'border-bauhaus-mediumgrey bg-bauhaus-black/20'
                  }`}
                >
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[9px] text-bauhaus-lightgrey">Step 0{step.num}</span>
                    {isHuman && (
                      <span className="text-[8px] bg-bauhaus-accent text-bauhaus-black px-1.5 py-0.5 font-bold uppercase tracking-wider">
                        ⟐ Gate
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-sm font-bold uppercase tracking-tight text-bauhaus-white mb-0.5">
                    {step.name}
                  </h3>
                  
                  <span className="text-[8px] text-bauhaus-lightgrey uppercase font-bold">
                    Crew: {step.crew}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Selected Step Detail Panel */}
        <div className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-black flex flex-col justify-between min-h-[220px]">
          {selectedStep !== null ? (() => {
            const step = STEPS_DATA.find(s => s.num === selectedStep)!
            const isHuman = step.gateType === 'human'
            
            return (
              <div className="space-y-4">
                <div>
                  <div className="text-[9px] text-bauhaus-accent uppercase tracking-widest font-bold mb-1">
                    Step Detail Audit
                  </div>
                  <h3 className="text-base font-bold uppercase tracking-tight text-bauhaus-white">
                    {step.name} Stage
                  </h3>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-0.5">
                    Assigned Agent Crew
                  </div>
                  <span className="text-xs text-bauhaus-white font-bold block">{step.crew.toUpperCase()} CREW</span>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-0.5">
                    Description
                  </div>
                  <p className="text-[10px] text-bauhaus-lightgrey leading-relaxed">
                    {step.desc}
                  </p>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-0.5">
                    Checkpoint Rule
                  </div>
                  <span className="text-[10px] text-bauhaus-white block uppercase">
                    {step.gate === 'none' ? 'None (Autonomous)' : step.gate}
                  </span>
                  {isHuman && (
                    <div className="text-[8px] text-bauhaus-yellow font-bold uppercase flex items-center space-x-1 mt-1">
                      <UserCheck size={10} />
                      <span>Routes to human judgment queue</span>
                    </div>
                  )}
                </div>
              </div>
            )
          })() : (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <Layers size={20} className="text-bauhaus-mediumgrey" />
              <div className="text-[9px] text-bauhaus-lightgrey font-bold uppercase tracking-wider">
                Select a stage node to inspect checkpoint rules.
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Workflow Legend */}
      <div className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-grey text-[10px] text-bauhaus-lightgrey leading-relaxed flex items-start space-x-2 font-mono">
        <Layers size={14} className="text-bauhaus-accent mt-0.5 flex-shrink-0" />
        <p>
          <strong>System Flow Checklist:</strong> All steps are fully automated. When a crew is dispatched to a step marked with a <strong>⟐ Human Gate</strong>, the active MCP server halts the process automatically and pushes the authorization task to the Judgment Queue for Waël Hassan's sign-off.
        </p>
      </div>
    </div>
  )
}
