import React, { useState } from 'react'
import { Search, Book, HelpCircle } from 'lucide-react'
import { ProcessStrip } from '../components/ProcessStrip'

const GLOSSARY_ITEMS = [
  {
    term: '⟐ gate',
    definition: 'A human validation checkpoint that blocks automatic crew execution and routes decisions directly to the operator\'s queue to protect boundaries.',
    section: '§9 Client Lifecycle'
  },
  {
    term: 'Judgment Queue',
    definition: 'A batched, decision-ready list protecting the operator\'s attention from minor crew notifications. Labeled recommendations and wait-costs are required.',
    section: '§13 Judgment Queue'
  },
  {
    term: 'Deployability Ladder',
    definition: 'A map grading KIBO OS steps from waël-only -> agent-deployable -> partner-certifiable to structurally de-bottleneck the founder.',
    section: '§11.4 Deployability Ladder'
  },
  {
    term: 'CAC',
    definition: 'Cost-to-Acquire-and-Trust. The central scaling bottleneck of the mid-market vertical, lowered structurally by category brand authority.',
    section: '§4 Leverage Doctrine'
  },
  {
    term: 'Agent Crew',
    definition: 'A specialized, isolated crew of agents dispatched to carry out specific business phases (Scout, Herald, Diagnostician, Installer, Operator, Steward, Forge).',
    section: '§5 The Agent Workforce'
  },
  {
    term: 'KIBO Module',
    definition: 'A productized, sovereign, and observable software package installed at a specific client layer (e.g. kibo-net, kibo-rag, kibo-gateway).',
    section: '§6 KIBO OS Architecture'
  }
]

export const Docs: React.FC = () => {
  const [search, setSearch] = useState('')

  const filteredGlossary = GLOSSARY_ITEMS.filter(item =>
    item.term.toLowerCase().includes(search.toLowerCase()) ||
    item.definition.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>Searchable Glossary & Documentation</span>
        </h2>
      </div>

      <ProcessStrip />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Searchable Glossary Sidebar */}
        <div className="space-y-6">
          <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey space-y-4">
            <h3 className="text-base font-extrabold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
              <HelpCircle size={16} className="text-bauhaus-accent" />
              <span>KIBO OS Glossary</span>
            </h3>
            
            <div className="relative">
              <Search className="absolute left-3 top-2.5 text-bauhaus-lightgrey" size={16} />
              <input
                type="text"
                placeholder="Search terms..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full bg-bauhaus-black border border-bauhaus-mediumgrey pl-10 pr-4 py-2 text-xs text-bauhaus-white placeholder-bauhaus-lightgrey focus:border-bauhaus-accent focus:outline-none font-mono"
              />
            </div>

            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
              {filteredGlossary.map((item, idx) => (
                <div key={idx} className="border-b border-bauhaus-mediumgrey/50 pb-3 last:border-b-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-bauhaus-white text-xs">{item.term}</span>
                    <span className="text-[8px] bg-bauhaus-black text-bauhaus-accent px-1.5 py-0.5 font-bold uppercase tracking-wider font-mono border border-bauhaus-mediumgrey">
                      {item.section}
                    </span>
                  </div>
                  <p className="text-[11px] text-bauhaus-lightgrey leading-relaxed">
                    {item.definition}
                  </p>
                </div>
              ))}
              {filteredGlossary.length === 0 && (
                <div className="text-xs text-bauhaus-lightgrey italic text-center py-4">
                  No matching terms found.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Spec Content Viewer */}
        <div className="lg:col-span-2 border border-bauhaus-mediumgrey p-8 bg-bauhaus-grey space-y-6">
          <div className="flex items-center space-x-2 border-b border-bauhaus-mediumgrey pb-4">
            <Book className="text-bauhaus-accent" size={20} />
            <h3 className="text-lg font-bold uppercase tracking-tight text-bauhaus-white">
              System Specification (kibo-os-v5.md)
            </h3>
          </div>
          
          <div className="max-h-[600px] overflow-y-auto text-xs text-bauhaus-lightgrey leading-relaxed space-y-4 pr-4 font-mono">
            <h4 className="text-sm font-bold text-bauhaus-white uppercase tracking-wider">
              KIBO OS — Chief AI Officer (Autonomous Operating Brain)
            </h4>
            <p>
              Thesis: KIBO OS is the operating system we install into mid-tier companies so they run like they're 10x their size — delivered by agents, proven on ourselves.
            </p>
            <h5 className="font-bold text-bauhaus-white uppercase border-b border-bauhaus-mediumgrey/50 pb-1 mt-6">
              Three rules that keep this safe and credible at scale:
            </h5>
            <ul className="list-disc list-inside space-y-2 pl-2">
              <li>
                <strong>Agents propose; the human promotes.</strong> No agent expands its authority, edits this prompt, moves money, deploys to client production, or speaks for the brand without the human.
              </li>
              <li>
                <strong>Promise the mechanism, never the jackpot.</strong> We sell operating like 10x, not a guaranteed outcome. No claim ships without evidence. No fabricated proof, ever.
              </li>
              <li>
                <strong>Client data stays in the client's boundary.</strong> Sovereign, governed, telemetry-from-hour-one — the product and the moat, not a constraint.
              </li>
            </ul>
            
            <h5 className="font-bold text-bauhaus-white uppercase border-b border-bauhaus-mediumgrey/50 pb-1 mt-6">
              Strategic priorities (the brain ranks all work against this):
            </h5>
            <ul className="list-disc list-inside space-y-1.5 pl-2">
              <li>Drive cost-to-acquire-and-trust per deployment down — that ratio is the business.</li>
              <li>Build KIBO OS into an owned category so buyers arrive pre-sold (lowers CAC structurally).</li>
              <li>Keep delivery near-zero-marginal-cost via the agent workforce; expand recurring operation (LTV).</li>
              <li>Protect governance/sovereignty credibility — the wedge and the price premium.</li>
              <li>De-bottleneck from the human: make KIBO OS agent- and partner-deployable, not Waël-deployable.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
