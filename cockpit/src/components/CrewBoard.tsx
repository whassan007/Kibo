import React, { useState } from 'react'
import { HelpCircle, Shield, Briefcase, FileText, CheckCircle2, AlertOctagon } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

export const CrewBoard: React.FC = () => {
  const { setHelpTopic } = useKiboStore()
  const [selectedCrew, setSelectedCrew] = useState<string | null>(null)

  // Hardcode crew general definitions alongside matching grants from grants.json
  const CREWS_DATA = [
    {
      id: 'scout',
      name: 'Scout',
      objective: 'Finds, filters, and qualifies mid-market businesses and Private Equity portfolio targets against the ICP.',
      mission: 'Identify and rank regional healthcare mid-market opportunities with headcount in [50, 500].',
      grants: { 'can_qualify': true, 'can_reach_out': false },
      skills: ['Targets Search Filtering', 'PE operating partners channel outreach', 'Fit scoring calculation']
    },
    {
      id: 'herald',
      name: 'Herald',
      objective: 'Turns KIBO OS into owned, citable category language; produces thought-leadership and proof artifacts to lower CAC.',
      mission: 'Draft weekly thought-leadership regarding in-boundary compliance metrics for regulated verticals.',
      grants: { 'can_draft_brand_claims': true, 'can_publish': false },
      skills: ['GTM & SEO strategy', 'Content Architecture mapping', 'Claim Library validation']
    },
    {
      id: 'diagnostician',
      name: 'Diagnostician',
      objective: 'Runs W-Method diagnostic audits for prospects: generates maturity maps and scoped installer plans.',
      mission: 'Assess prospective regional clinic group Layer 1-7 infrastructure and map maturity scores.',
      grants: { 'can_run_audit': true },
      skills: ['W-Method Diagnostic auditing', '7-layer grading', 'PII Redaction & sanitization']
    },
    {
      id: 'installer',
      name: 'Installer',
      objective: 'Installs KIBO OS: plugs modules into the client stack layer by layer, telemetry first, against scoped grants.',
      mission: 'Configure Layer 2 VPN networks and Layer 6 telemetry baselines on customer staging environment.',
      grants: { 'can_deploy_staging': true, 'can_deploy_production': false },
      skills: ['Module integration', 'Tailscale mesh routing', 'Staging deployment verification']
    },
    {
      id: 'operator',
      name: 'Operator',
      objective: 'Runs and governs deployed KIBO instances: cost chain-of-custody, eval-vs-baseline, and postmortems.',
      mission: 'Monitor active health evaluations, scoring metrics, and track resource spend quotas.',
      grants: { 'can_govern_telemetry': true },
      skills: ['Run-state governance', 'Cost auditing', 'Drift & regression triggers']
    },
    {
      id: 'steward',
      name: 'Steward',
      objective: 'Runs KIBO OS\'s own back office to the signature line (does not sign terms or move money).',
      mission: 'Draft value-share operability contracts and review bookkeeping logs.',
      grants: { 'can_draft_bookkeeping': true, 'can_sign': false },
      skills: ['Agreement drafting', 'Telemetry cost reconciliation', 'Bookkeeping ledger updates']
    },
    {
      id: 'forge',
      name: 'Forge',
      objective: 'Builds agents that build agents, driving KIBO OS toward partner/agent deployability.',
      mission: 'Scaffold skill configuration files and generate proposals to expand crew autonomy.',
      grants: { 'can_draft_agents': true, 'can_promote_grants': false },
      skills: ['Agent scaffolding', 'Deployability ladder engineering', 'Autonomy proposal formulation']
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>Crew Board</span>
          <span className="text-xs bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-extrabold">{CREWS_DATA.length}</span>
        </h2>
        <button 
          onClick={() => setHelpTopic('crews')} 
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1 text-xs"
        >
          <HelpCircle size={14} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Crews Spec</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CREWS_DATA.map(crew => (
          <div 
            key={crew.id} 
            onClick={() => setSelectedCrew(crew.id)}
            className={`border cursor-pointer transition-all p-6 space-y-4 hover:border-bauhaus-white ${selectedCrew === crew.id ? 'border-bauhaus-white bg-bauhaus-grey' : 'border-bauhaus-mediumgrey bg-bauhaus-grey/50'}`}
          >
            <div className="flex justify-between items-start">
              <h3 className="text-lg font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
                <span className="w-2.5 h-2.5 bg-bauhaus-accent"></span>
                <span>{crew.name}</span>
              </h3>
              <span className="text-[9px] border border-bauhaus-lightgrey text-bauhaus-lightgrey px-2 py-0.5 font-bold uppercase tracking-wider">
                Crew
              </span>
            </div>

            <p className="text-xs text-bauhaus-lightgrey leading-relaxed line-clamp-3">
              {crew.objective}
            </p>

            <div className="border-t border-bauhaus-mediumgrey pt-3">
              <div className="text-[9px] text-bauhaus-accent uppercase tracking-widest font-bold mb-1">
                Active Grants
              </div>
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(crew.grants).map(([key, val]) => (
                  <span 
                    key={key} 
                    className={`text-[9px] px-2 py-0.5 font-mono flex items-center space-x-1 ${val ? 'bg-bauhaus-mediumgrey text-bauhaus-white' : 'border border-bauhaus-mediumgrey text-bauhaus-lightgrey'}`}
                  >
                    {val ? <CheckCircle2 size={8} className="text-bauhaus-accent mr-1" /> : <AlertOctagon size={8} className="text-bauhaus-red mr-1" />}
                    <span>{key}</span>
                  </span>
                ))}
              </div>
            </div>

            <div className="border-t border-bauhaus-mediumgrey pt-3">
              <div className="text-[9px] text-bauhaus-yellow uppercase tracking-widest font-bold mb-0.5">
                Current Mission
              </div>
              <p className="text-xs text-bauhaus-white leading-normal font-medium">
                {crew.mission}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Crew Detail Drawer */}
      {selectedCrew && (() => {
        const crewObj = CREWS_DATA.find(c => c.id === selectedCrew)!
        return (
          <div className="border border-bauhaus-white bg-bauhaus-grey p-6 space-y-6">
            <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
              <h3 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
                <span className="w-3.5 h-3.5 bg-bauhaus-accent"></span>
                <span>{crewObj.name} Crew Config</span>
              </h3>
              <button 
                onClick={() => setSelectedCrew(null)}
                className="text-xs text-bauhaus-lightgrey hover:text-bauhaus-white uppercase font-bold tracking-wider"
              >
                Close Config
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-bauhaus-accent mb-1 flex items-center space-x-1.5">
                    <Briefcase size={14} />
                    <span>Operational Objective</span>
                  </h4>
                  <p className="text-xs text-bauhaus-lightgrey leading-relaxed">
                    {crewObj.objective}
                  </p>
                </div>
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-bauhaus-accent mb-1 flex items-center space-x-1.5">
                    <Shield size={14} />
                    <span>Autonomy Grants & Scopes</span>
                  </h4>
                  <ul className="space-y-1.5">
                    {Object.entries(crewObj.grants).map(([key, val]) => (
                      <li key={key} className="flex justify-between items-center text-xs border-b border-bauhaus-mediumgrey py-1">
                        <span className="font-mono text-bauhaus-lightgrey">{key}</span>
                        <span className={`font-bold px-2 py-0.5 uppercase text-[9px] ${val ? 'bg-bauhaus-accent text-bauhaus-black' : 'bg-bauhaus-red text-white'}`}>
                          {val ? 'Granted' : 'Gated'}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-bauhaus-accent mb-2 flex items-center space-x-1.5">
                    <FileText size={14} />
                    <span>Crew Skill Instructions (SKILL.md)</span>
                  </h4>
                  <ul className="space-y-2 text-xs text-bauhaus-lightgrey">
                    {crewObj.skills.map((skill, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-bauhaus-accent font-bold mt-0.5">·</span>
                        <span>{skill}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4 p-3 border border-bauhaus-mediumgrey bg-bauhaus-black text-[10px] text-bauhaus-lightgrey">
                    Governed by <code>.agents/skills/{crewObj.id}/SKILL.md</code>. Loaded dynamically as execution stubs by <code>crew.dispatch</code>.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })()}
    </div>
  )
}
