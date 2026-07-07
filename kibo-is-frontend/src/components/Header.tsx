import React from 'react'
import { RefreshCw, Compass } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

export const Header: React.FC = () => {
  const { ladder, proposals, setHelpTopic, setShowTour, setTourStep, loadAll, loading } = useKiboStore()

  // Calculate Gates Count
  const gatesCount = ladder?.steps.filter(s => s.owner === 'waël-only').length ?? 4
  const baselineGates = 4
  const targetGates = 0
  const isGatesOnTrack = gatesCount < baselineGates

  // Calculate CAC
  const isCacLowered = proposals.some(p => p.status === 'promoted')
  const cacVal = isCacLowered ? 4200 : 5000
  const baselineCac = 5000
  const targetCac = 3000
  const isCacOnTrack = cacVal < baselineCac

  // Calculate position percentage along the journey track
  // For CAC: goes from 5000 (0% progress) to 3000 (100% progress)
  const cacProgress = Math.min(100, Math.max(0, ((baselineCac - cacVal) / (baselineCac - targetCac)) * 100))
  // For Gates: goes from 4 (0% progress) to 0 (100% progress)
  const gatesProgress = Math.min(100, Math.max(0, ((baselineGates - gatesCount) / (baselineGates - targetGates)) * 100))

  return (
    <header className="border-b border-bauhaus-mediumgrey py-6 px-8 flex flex-col md:flex-row justify-between items-start md:items-center bg-bauhaus-grey gap-6">
      {/* Brand Column */}
      <div>
        <div className="flex items-center space-x-3 mb-1">
          <div className="w-4 h-4 bg-bauhaus-accent"></div>
          <h1 className="text-xl font-bold uppercase tracking-widest text-bauhaus-white">KIBO OS</h1>
        </div>
        <p className="text-[10px] text-bauhaus-lightgrey uppercase tracking-wider font-bold">
          Chief AI Officer Cockpit · Wael Hassan System v5.1.0
        </p>
      </div>

      {/* Metric Journeys (The blocks carrying meaning) */}
      <div className="flex flex-wrap gap-8">
        {/* CAC Journey Card */}
        <div 
          onClick={() => setHelpTopic('metrics')}
          className="relative group cursor-pointer border border-bauhaus-mediumgrey p-3 bg-bauhaus-black w-60 font-mono text-xs select-none"
        >
          <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-2">
            CAC PER DEPLOYMENT
          </div>

          <div className="flex justify-between items-baseline mb-2">
            <span className="text-2xl font-bold text-bauhaus-white">${cacVal.toLocaleString()}</span>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 border ${
              isCacOnTrack ? 'border-bauhaus-accent text-bauhaus-accent' : 'border-bauhaus-red text-bauhaus-red'
            }`}>
              {isCacOnTrack ? '-16% ON TRACK' : 'BASELINE STABLE'}
            </span>
          </div>

          {/* Journey Track & Cursor */}
          <div className="relative py-3 mt-1 flex items-center">
            {/* The Track Line */}
            <div className="absolute left-0 right-0 h-[1px] bg-bauhaus-mediumgrey" />
            
            {/* Start point */}
            <div className="absolute left-0 w-1.5 h-1.5 bg-bauhaus-lightgrey" />

            {/* Target point (marked endpoint) */}
            <div className="absolute right-0 w-2.5 h-2.5 border border-bauhaus-accent bg-bauhaus-black" title="Target: $3,000" />

            {/* Current Cursor Position */}
            <div 
              className={`absolute w-[2px] h-4 -ml-[1px] transition-all duration-700 ${
                isCacOnTrack ? 'bg-bauhaus-accent' : 'bg-bauhaus-red'
              }`}
              style={{ left: `${cacProgress}%` }}
            />
          </div>

          <div className="flex justify-between text-[8px] text-bauhaus-lightgrey uppercase mt-1">
            <span>Base: $5k</span>
            <span className="font-bold text-bauhaus-accent">Goal: $3k</span>
          </div>

          <div className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity bg-bauhaus-grey border border-bauhaus-mediumgrey text-[9px] p-2.5 w-52 text-bauhaus-lightgrey z-10">
            Cost-to-Acquire-and-Trust. Lowering this ratio is the central bottleneck of mid-market scaling.
          </div>
        </div>

        {/* Gates Journey Card */}
        <div 
          onClick={() => setHelpTopic('metrics')}
          className="relative group cursor-pointer border border-bauhaus-mediumgrey p-3 bg-bauhaus-black w-60 font-mono text-xs select-none"
        >
          <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-2">
            HUMAN GATES (⟐)
          </div>

          <div className="flex justify-between items-baseline mb-2">
            <span className="text-2xl font-bold text-bauhaus-white">{gatesCount}</span>
            <span className={`text-[10px] font-bold px-1.5 py-0.5 border ${
              isGatesOnTrack ? 'border-bauhaus-accent text-bauhaus-accent' : 'border-bauhaus-red text-bauhaus-red'
            }`}>
              {isGatesOnTrack ? 'REDUCED' : 'STABLE BASELINE'}
            </span>
          </div>

          {/* Journey Track & Cursor */}
          <div className="relative py-3 mt-1 flex items-center">
            {/* The Track Line */}
            <div className="absolute left-0 right-0 h-[1px] bg-bauhaus-mediumgrey" />
            
            {/* Start point */}
            <div className="absolute left-0 w-1.5 h-1.5 bg-bauhaus-lightgrey" />

            {/* Target point (marked endpoint) */}
            <div className="absolute right-0 w-2.5 h-2.5 border border-bauhaus-yellow bg-bauhaus-black" title="Target: 0 gates" />

            {/* Current Cursor Position */}
            <div 
              className={`absolute w-[2px] h-4 -ml-[1px] transition-all duration-700 ${
                isGatesOnTrack ? 'bg-bauhaus-accent' : 'bg-bauhaus-red'
              }`}
              style={{ left: `${gatesProgress}%` }}
            />
          </div>

          <div className="flex justify-between text-[8px] text-bauhaus-lightgrey uppercase mt-1">
            <span>Base: 4 Gates</span>
            <span className="font-bold text-bauhaus-yellow">Goal: 0 Gates</span>
          </div>

          <div className="absolute right-0 top-0 opacity-0 group-hover:opacity-100 transition-opacity bg-bauhaus-grey border border-bauhaus-mediumgrey text-[9px] p-2.5 w-52 text-bauhaus-lightgrey z-10">
            Manual checkpoints. Lowering these via Forge autonomy promotions removes founder bottlenecks.
          </div>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex space-x-2 items-center font-mono">
        <button 
          onClick={() => {
            setTourStep(0)
            setShowTour(true)
          }}
          className="flex items-center space-x-1.5 text-[9px] border border-bauhaus-mediumgrey px-3 py-1.5 bg-bauhaus-grey text-bauhaus-white hover:bg-bauhaus-white hover:text-bauhaus-black transition-colors"
        >
          <Compass size={12} />
          <span className="font-bold uppercase tracking-wider">Tour</span>
        </button>
        <button 
          onClick={loadAll}
          disabled={loading}
          className="flex items-center space-x-1.5 text-[9px] border border-bauhaus-mediumgrey px-3 py-1.5 bg-bauhaus-grey text-bauhaus-white hover:bg-bauhaus-white hover:text-bauhaus-black transition-colors disabled:opacity-50"
        >
          <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
          <span className="font-bold uppercase tracking-wider">Sync</span>
        </button>
      </div>
    </header>
  )
}
