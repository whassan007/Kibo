import React, { useEffect } from 'react'
import { useKiboStore, startPolling, stopPolling } from '../store/kiboStore'
import { Header } from '../components/Header'
import { JudgmentQueue } from '../components/JudgmentQueue'
import { ProposalInbox } from '../components/ProposalInbox'
import { CrewBoard } from '../components/CrewBoard'
import { DeploymentPipeline } from '../components/DeploymentPipeline'
import { MaturityMap } from '../components/MaturityMap'
import { GovernanceInspector } from '../components/GovernanceInspector'
import { Docs } from './Docs'
import { Tutorial } from './Tutorial'
import { TourOverlay } from '../components/TourOverlay'
import { HelpOverlay } from '../components/HelpOverlay'
import { ProcessStrip } from '../components/ProcessStrip'

export const Dashboard: React.FC = () => {
  const { activeTab, setTab, helpTopic, setHelpTopic, error, loading } = useKiboStore()

  useEffect(() => {
    // Start 5-second polling of local state files
    startPolling()
    return () => {
      stopPolling()
    }
  }, [])

  const renderTabContent = () => {
    switch (activeTab) {
      case 'cockpit':
        return (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-start">
            <div className="xl:col-span-2 space-y-6">
              <JudgmentQueue />
            </div>
            <div className="space-y-6">
              <ProposalInbox />
            </div>
          </div>
        )
      case 'crews':
        return <CrewBoard />
      case 'pipeline':
        return <DeploymentPipeline />
      case 'maturity':
        return <MaturityMap />
      case 'governance':
        return <GovernanceInspector />
      case 'docs':
        return <Docs />
      case 'tutorial':
        return <Tutorial />
      default:
        return <JudgmentQueue />
    }
  }

  return (
    <div className="min-h-screen bg-bauhaus-black text-bauhaus-white flex flex-col font-sans">
      <Header />

      {/* Main Grid Layout */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Navigation Sidebar */}
        <nav className="w-full lg:w-64 border-r border-bauhaus-mediumgrey flex flex-col justify-between p-6 bg-bauhaus-black">
          <div className="space-y-2">
            {[
              { id: 'cockpit', label: '1. Cockpit' },
              { id: 'crews', label: '2. Crew Board' },
              { id: 'pipeline', label: '3. Pipeline' },
              { id: 'maturity', label: '4. Maturity' },
              { id: 'governance', label: '5. Governance' },
              { id: 'docs', label: '6. Spec & Glossary' },
              { id: 'tutorial', label: '7. System Tutorial' }
            ].map(item => (
              <button
                key={item.id}
                onClick={() => setTab(item.id as any)}
                className={`w-full text-left font-bold uppercase tracking-widest text-xs px-4 py-3 border transition-all ${activeTab === item.id ? 'border-bauhaus-white bg-bauhaus-white text-bauhaus-black' : 'border-transparent text-bauhaus-lightgrey hover:text-bauhaus-white'}`}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="pt-6 border-t border-bauhaus-mediumgrey/50 text-[10px] text-bauhaus-lightgrey uppercase tracking-wider font-semibold space-y-1">
            <div>Owner: Waël Hassan</div>
            <div>Mode: Sovereign Localhost</div>
            <div>CORS: Enforced (Vite)</div>
          </div>
        </nav>

        <main className="flex-1 p-8 overflow-y-auto space-y-6">
          {/* How KIBO Works Process Strip */}
          <ProcessStrip onTabChange={setTab} />

          {/* Error Banner */}
          {error && (
            <div className="bg-bauhaus-red/10 border border-bauhaus-red text-bauhaus-red px-4 py-3 mb-6 text-xs flex justify-between items-center font-mono">
              <span><strong>ERROR:</strong> {error}</span>
              <button onClick={() => useKiboStore.setState({ error: null })} className="font-bold underline hover:no-underline">Dismiss</button>
            </div>
          )}

          {/* Loading Skeleton */}
          {loading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-8 bg-bauhaus-grey w-1/4"></div>
              <div className="h-32 bg-bauhaus-grey w-full"></div>
              <div className="h-32 bg-bauhaus-grey w-full"></div>
            </div>
          ) : (
            renderTabContent()
          )}
        </main>
      </div>

      {/* Overlays */}
      <TourOverlay />
      {helpTopic && (
        <HelpOverlay topic={helpTopic} onClose={() => setHelpTopic(null)} />
      )}
    </div>
  )
}
export default Dashboard
