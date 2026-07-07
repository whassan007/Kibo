import React from 'react'

export type RungType = 'waël-only' | 'agent-deployable' | 'partner-certifiable'

interface DeployabilityLadderProps {
  currentRung?: RungType
  transition?: {
    before: RungType
    after: RungType
  }
}

const RUNGS: { type: RungType; label: string; description: string }[] = [
  {
    type: 'partner-certifiable',
    label: 'PARTNER CERTIFIABLE',
    description: 'Tier-3: Certified third-party integration & operation without Kibo core oversight.',
  },
  {
    type: 'agent-deployable',
    label: 'AGENT DEPLOYABLE',
    description: 'Tier-2: Autonomous agent execution inside sovereign client sandbox boundaries.',
  },
  {
    type: 'waël-only',
    label: 'WAËL ONLY',
    description: 'Tier-1: Human-in-the-loop manual action gates. Strict founder sovereignty.',
  },
]

export const DeployabilityLadder: React.FC<DeployabilityLadderProps> = ({
  currentRung,
  transition,
}) => {
  return (
    <div className="flex flex-col w-full font-mono text-xs p-4 border border-bauhaus-mediumgrey bg-bauhaus-grey">
      <div className="text-[10px] uppercase tracking-wider text-bauhaus-lightgrey mb-4 border-b border-bauhaus-mediumgrey pb-1">
        Deployability Ladder Climb
      </div>

      <div className="relative flex flex-col gap-4">
        {/* Ladder Left & Right Vertical Spine Rails */}
        <div className="absolute left-8 top-0 bottom-0 w-[1px] bg-bauhaus-mediumgrey" />
        <div className="absolute left-[36%] top-0 bottom-0 w-[1px] bg-bauhaus-mediumgrey hidden sm:block" />

        {RUNGS.map((rung) => {
          const isCurrent = currentRung === rung.type
          const isBefore = transition?.before === rung.type
          const isAfter = transition?.after === rung.type
          
          let borderStyle = 'border-bauhaus-mediumgrey'
          let bgStyle = 'bg-transparent'
          let textStyle = 'text-bauhaus-lightgrey'
          let marker = ''

          if (isCurrent) {
            borderStyle = 'border-bauhaus-accent'
            bgStyle = 'bg-bauhaus-black'
            textStyle = 'text-bauhaus-white font-bold'
            marker = '⟐ ACTIVE'
          } else if (isBefore) {
            borderStyle = 'border-bauhaus-red'
            bgStyle = 'bg-bauhaus-black'
            textStyle = 'text-bauhaus-red'
            marker = 'FROM'
          } else if (isAfter) {
            borderStyle = 'border-bauhaus-accent border-dashed'
            bgStyle = 'bg-bauhaus-black/50'
            textStyle = 'text-bauhaus-accent font-bold animate-pulse'
            marker = 'TO'
          }

          return (
            <div
              key={rung.type}
              className={`relative flex items-center justify-between border p-3 pl-12 min-h-[70px] ${borderStyle} ${bgStyle} transition-colors`}
            >
              {/* Horizontal Rung Bar Segment inside the Ladder Rails */}
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-8 h-[1px] bg-bauhaus-mediumgrey" />

              <div className="flex flex-col gap-0.5">
                <span className={`text-[10px] tracking-wider uppercase ${textStyle}`}>
                  {rung.label}
                </span>
                <span className="text-[9px] text-bauhaus-lightgrey leading-relaxed max-w-md">
                  {rung.description}
                </span>
              </div>

              {marker && (
                <span className={`text-[9px] font-bold px-2 py-0.5 border ${
                  isBefore ? 'border-bauhaus-red text-bauhaus-red' : 'border-bauhaus-accent text-bauhaus-accent'
                }`}>
                  {marker}
                </span>
              )}
            </div>
          )
        })}

        {/* Transition Path Vector / Arrow */}
        {transition && (
          <div className="absolute left-[3%] top-1/2 -translate-y-1/2 flex flex-col items-center gap-1">
            <span className="text-[14px] text-bauhaus-accent font-bold">↑</span>
            <span className="text-[8px] text-bauhaus-accent uppercase tracking-tighter rotate-90 my-1 font-bold">CLIMB</span>
          </div>
        )}
      </div>
    </div>
  )
}
