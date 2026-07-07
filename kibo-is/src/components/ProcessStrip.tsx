import React, { useState } from 'react'

interface ProcessStripProps {
  onTabChange?: (tab: 'cockpit' | 'crews' | 'pipeline' | 'maturity' | 'governance' | 'docs') => void
}

interface StepBlock {
  id: number
  label: string
  detail: string
  targetTab: 'cockpit' | 'crews' | 'pipeline' | 'maturity' | 'governance' | 'docs'
  tooltip: string
}

const STEPS: StepBlock[] = [
  {
    id: 1,
    label: '1. AGENT PROPOSES',
    detail: 'Crews draft code/autonomy proposals',
    targetTab: 'cockpit',
    tooltip: 'Forge or other crews generate JSON proposals targeting autonomy or deployability steps.',
  },
  {
    id: 2,
    label: '2. SCORED (HARD-STOPS)',
    detail: 'Evaluations check boundaries & claims',
    targetTab: 'governance',
    tooltip: 'Every proposal undergoes strict rubric evaluations. Failures on claim integrity or boundary checks halt promotion.',
  },
  {
    id: 3,
    label: '3. JUDGMENT QUEUE',
    detail: 'Routes to human operator queue',
    targetTab: 'cockpit',
    tooltip: 'Human gates route direct actions (e.g. handshake, agreement signing) to the queue for manual approval.',
  },
  {
    id: 4,
    label: '4. YOU PROMOTE',
    detail: 'Manual promotion of active proposals',
    targetTab: 'cockpit',
    tooltip: 'Only the human operator has promotion authority. Agents propose, humans promote.',
  },
  {
    id: 5,
    label: '5. LADDER CLIMBS',
    detail: 'Changelog grows & autonomy widens',
    targetTab: 'maturity',
    tooltip: 'Successful promotion bumps semver, updates active prompt configs, and progresses steps up the deployability ladder.',
  },
]

export const ProcessStrip: React.FC<ProcessStripProps> = ({ onTabChange }) => {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <div className="flex flex-col w-full font-mono text-xs border border-bauhaus-mediumgrey bg-bauhaus-grey p-3 select-none">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-1.5 mb-2 text-[10px]">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2.5 h-2.5 bg-bauhaus-yellow" />
          <span className="text-bauhaus-lightgrey tracking-wider uppercase">HOW KIBO WORKS — CONTINUOUS IMPROVEMENT LOOP (§10)</span>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="text-bauhaus-lightgrey hover:text-bauhaus-white uppercase text-[9px] border border-bauhaus-mediumgrey px-1.5 py-0.5 hover:bg-bauhaus-black"
        >
          Dismiss
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-1.5">
        {STEPS.map((step, idx) => {
          return (
            <div
              key={step.id}
              onClick={() => onTabChange?.(step.targetTab)}
              className="group relative flex flex-col p-2.5 border border-bauhaus-mediumgrey hover:border-bauhaus-accent bg-transparent cursor-pointer hover:bg-bauhaus-black transition-all"
              title={step.tooltip}
            >
              <div className="absolute right-2 top-2 text-[9px] text-bauhaus-mediumgrey group-hover:text-bauhaus-accent font-bold">
                {idx < 4 ? '→' : '⟐'}
              </div>
              <div className="font-bold text-bauhaus-white uppercase tracking-wider text-[10px] mb-1">
                {step.label}
              </div>
              <div className="text-[9px] text-bauhaus-lightgrey leading-relaxed">
                {step.detail}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
