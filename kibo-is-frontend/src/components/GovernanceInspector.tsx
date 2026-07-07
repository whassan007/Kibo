import { useState } from 'react'
import { HelpCircle } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

export const GovernanceInspector: React.FC = () => {
  const { catalog, proposals, feedbackLog, setHelpTopic } = useKiboStore()
  const [activeSubTab, setActiveSubTab] = useState<'grants' | 'catalog' | 'log' | 'proposals'>('grants')

  // Parse markdown log lines to render them cleanly
  const parseLogs = (logText: string) => {
    if (!logText) return []
    // Split by Markdown headings
    const entries = logText.split('## ').filter(Boolean)
    return entries.map(entry => {
      const lines = entry.split('\n').filter(Boolean)
      const title = lines[0] || 'Log Entry'
      const details = lines.slice(1).map(l => l.replace(/^- \*\*[^*]+\:\*\*/, '').trim())
      return { title, details }
    })
  }

  const logsList = parseLogs(feedbackLog)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>Governance Inspector</span>
        </h2>
        <button 
          onClick={() => setHelpTopic('governance')} 
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1 text-xs"
        >
          <HelpCircle size={14} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Inspector Spec</span>
        </button>
      </div>

      {/* Sub tabs navigation */}
      <div className="flex space-x-8 border-b border-bauhaus-mediumgrey pb-2">
        {(['grants', 'catalog', 'log', 'proposals'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveSubTab(tab)}
            className={`font-bold uppercase tracking-widest text-[10px] pb-2 transition-all ${activeSubTab === tab ? 'text-bauhaus-accent border-b-2 border-b-bauhaus-accent' : 'text-bauhaus-lightgrey hover:text-bauhaus-white'}`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Sub tab content */}
      <div className="space-y-4">
        {activeSubTab === 'grants' && (
          <div className="space-y-4">
            <h3 className="text-base font-extrabold uppercase tracking-tight text-bauhaus-white">
              Active Autonomy Grants & Scopes
            </h3>
            <p className="text-xs text-bauhaus-lightgrey leading-relaxed max-w-xl">
              Inspect current permission rules mapping what actions crews can dispatch autonomously. Gated items are routed to the operator's judgment queue.
            </p>
            
            <div className="border border-bauhaus-mediumgrey overflow-hidden bg-bauhaus-grey">
              <table className="w-full text-xs text-left text-bauhaus-lightgrey">
                <thead className="bg-bauhaus-black text-[9px] uppercase tracking-widest font-bold border-b border-bauhaus-mediumgrey">
                  <tr>
                    <th className="p-4">W-Method Crew</th>
                    <th className="p-4">Autonomy Scope / Rule Key</th>
                    <th className="p-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-bauhaus-mediumgrey font-mono">
                  <tr>
                    <td className="p-4 text-bauhaus-white font-bold">Scout</td>
                    <td className="p-4">can_qualify</td>
                    <td className="p-4 text-right text-bauhaus-accent font-bold">GRANTED</td>
                  </tr>
                  <tr className="bg-bauhaus-black/20">
                    <td className="p-4 text-bauhaus-white font-bold">Scout</td>
                    <td className="p-4">can_reach_out</td>
                    <td className="p-4 text-right text-bauhaus-red font-bold">GATED (Waël-Only)</td>
                  </tr>
                  <tr>
                    <td className="p-4 text-bauhaus-white font-bold">Herald</td>
                    <td className="p-4">can_draft_brand_claims</td>
                    <td className="p-4 text-right text-bauhaus-accent font-bold">GRANTED</td>
                  </tr>
                  <tr className="bg-bauhaus-black/20">
                    <td className="p-4 text-bauhaus-white font-bold">Herald</td>
                    <td className="p-4">can_publish</td>
                    <td className="p-4 text-right text-bauhaus-red font-bold">GATED (Waël-Only)</td>
                  </tr>
                  <tr>
                    <td className="p-4 text-bauhaus-white font-bold">Installer</td>
                    <td className="p-4">can_deploy_staging</td>
                    <td className="p-4 text-right text-bauhaus-accent font-bold">GRANTED</td>
                  </tr>
                  <tr className="bg-bauhaus-black/20">
                    <td className="p-4 text-bauhaus-white font-bold">Installer</td>
                    <td className="p-4">can_deploy_production</td>
                    <td className="p-4 text-right text-bauhaus-red font-bold">GATED (Waël-Only)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeSubTab === 'catalog' && (
          <div className="space-y-4">
            <h3 className="text-base font-extrabold uppercase tracking-tight text-bauhaus-white">
              KIBO Module Catalog (kibo://catalog)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {catalog?.modules.map(mod => (
                <div key={mod.id} className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-grey space-y-2">
                  <div className="flex justify-between items-center">
                    <h4 className="font-bold text-bauhaus-white uppercase text-sm">{mod.name}</h4>
                    <span className="text-[9px] bg-bauhaus-mediumgrey text-bauhaus-white px-2 py-0.5 font-mono">Layer 0{mod.layer}</span>
                  </div>
                  <p className="text-xs text-bauhaus-lightgrey leading-relaxed">{mod.description}</p>
                  <div className="flex justify-between items-center text-[10px] text-bauhaus-lightgrey pt-2 border-t border-bauhaus-mediumgrey/50">
                    <span>Status: <strong className="text-bauhaus-white uppercase">{mod.status}</strong></span>
                    <span>Reuse Count: <strong className="text-bauhaus-white">{mod.reuse_count}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSubTab === 'log' && (
          <div className="space-y-4">
            <h3 className="text-base font-extrabold uppercase tracking-tight text-bauhaus-white">
              System Feedback Audit Log (kibo://feedback/log)
            </h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              {logsList.slice().reverse().map((log, idx) => (
                <div key={idx} className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-grey text-xs leading-normal">
                  <h4 className="font-bold text-bauhaus-white uppercase mb-2 border-b border-bauhaus-mediumgrey/50 pb-1">
                    {log.title}
                  </h4>
                  <ul className="space-y-1 text-bauhaus-lightgrey text-[11px] font-mono">
                    {log.details.map((line, lIdx) => (
                      <li key={lIdx} className="line-clamp-2">
                        · {line}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSubTab === 'proposals' && (
          <div className="space-y-4">
            <h3 className="text-base font-extrabold uppercase tracking-tight text-bauhaus-white">
              Changelog & Historical Proposals
            </h3>
            <div className="space-y-4">
              {proposals.filter(p => p.status === 'promoted').map(prop => (
                <div key={prop.id} className="border border-bauhaus-mediumgrey p-4 bg-bauhaus-grey text-xs">
                  <div className="flex justify-between items-start border-b border-bauhaus-mediumgrey pb-1.5 mb-2">
                    <div>
                      <h4 className="font-bold text-bauhaus-white">PROMOTED: {prop.target}</h4>
                      <span className="text-[9px] text-bauhaus-accent font-bold uppercase">{prop.semver_bump} bump · {prop.id}</span>
                    </div>
                    <span className="text-[9px] bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-bold uppercase">Active</span>
                  </div>
                  <p className="text-bauhaus-lightgrey leading-relaxed">{prop.rationale}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
