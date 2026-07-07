import React from 'react'
import { X, HelpCircle, BookOpen } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

interface HelpOverlayProps {
  topic: string
  onClose: () => void
}

const SPEC_HELP_MAP: Record<string, { title: string; section: string; text: string }> = {
  queue: {
    title: 'Judgment Queue',
    section: '§13 The Judgment Queue',
    text: 'Batched, decision-ready list protecting the founder\'s scarce attention. Options are loaded with labeled recommendations, delegate rationale, and the cost of waiting. Every recurring item requires a §10.4 proposal to retire itself.'
  },
  metrics: {
    title: 'North-Star Metrics',
    section: '§9 Client Lifecycle & §4 Leverage Doctrine',
    text: 'Two metrics define the business: Cost-to-Acquire-and-Trust (CAC) per deployment (lowered by category authority) and Human Gates (⟐) per deployment (lowered by autonomy expansions).'
  },
  proposals: {
    title: 'Proposal Inbox',
    section: '§10.4 Two Throttles (Human-Gated)',
    text: 'The growth engine of KIBO OS. Used to expand crew autonomy or advance steps on the deployability ladder based on evaluation evidence. Promotion compiles a patch/minor/major semver bump and records to the changelog.'
  },
  crews: {
    title: 'Agent Crews',
    section: '§5 The Agent Workforce',
    text: 'The seven specialized agent crews (Scout, Herald, Diagnostician, Installer, Operator, Steward, Forge) that perform operational tasks. Each crew operates under restricted grants and uses spec-defined tools.'
  },
  pipeline: {
    title: 'Deployment Pipeline',
    section: '§9 The Client Lifecycle',
    text: 'The 7-stage W-Method lifecycle (Attract, Acquire, Diagnose, Agree, Install, Operate, Compound). Human gates (⟐) are flagged to halt automatic dispatch and route directly to the operator\'s queue.'
  },
  maturity: {
    title: 'W-Method Maturity Map',
    section: '§6 KIBO OS Architecture (W-Method)',
    text: 'A bottom-up assessment heatmap of the client\'s 7 architectural layers (0 to 4 grading system). Stabilize bottom foundation layers (compute, network, telemetry) before delivering value top-down.'
  },
  governance: {
    title: 'Governance Inspector',
    section: '§8 Scope Boundaries & §11 Surface',
    text: 'Allows auditing the active grants, data-grants, and client constraints. Ensures compliance with local-first, in-boundary rules, and validates what actions agents are permitted to carry out.'
  }
}

export const HelpOverlay: React.FC<HelpOverlayProps> = ({ topic, onClose }) => {
  const specHelp = SPEC_HELP_MAP[topic]
  if (!specHelp) return null

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-bauhaus-grey border border-bauhaus-lightgrey p-6 z-50 transition-all duration-300">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-2 text-bauhaus-accent">
          <HelpCircle size={18} />
          <span className="font-bold text-xs uppercase tracking-widest">KIBO System Spec</span>
        </div>
        <button onClick={onClose} className="text-bauhaus-lightgrey hover:text-bauhaus-white">
          <X size={16} />
        </button>
      </div>
      <h3 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white mb-1">
        {specHelp.title}
      </h3>
      <div className="text-xs text-bauhaus-accent font-semibold mb-3">{specHelp.section}</div>
      <p className="text-xs text-bauhaus-lightgrey leading-relaxed mb-4">
        {specHelp.text}
      </p>
      <div className="flex items-center space-x-1.5 text-xs text-bauhaus-white font-bold hover:underline cursor-pointer"
           onClick={() => {
             useKiboStore.getState().setTab('docs')
             onClose()
           }}>
        <BookOpen size={14} />
        <span>Open Canonical Spec (kibo-os-v5.md)</span>
      </div>
    </div>
  )
}
