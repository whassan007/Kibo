import React from 'react'
import { X, ChevronRight, ChevronLeft, HelpCircle } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'

const TOUR_STEPS = [
  {
    title: '1. The Judgment Queue',
    text: 'This is the main inbox for the single human operator. Every ambiguous or irreversible crew request halts here. Labeled recommendations, costs of waiting, and delegate details are generated autonomously by the crews. Protect your attention: Approve, Reject, or Defer in one click.',
    target: 'queue'
  },
  {
    title: '2. North-Star Metrics',
    text: 'Your business health is distilled into two key metrics up top: Cost-to-Acquire-and-Trust (CAC) per deployment and Human Gates (⟐) per deployment. Lowering CAC (via Herald category brand authority) and gates (via Forge autonomy proposals) represents the growth core.',
    target: 'metrics'
  },
  {
    title: '3. Proposal Inbox',
    text: 'This is where agent crews submit proposals to climb the deployability ladder or expand their autonomy. Review rationales, code diffs, and evidence log telemetry. Promoting a proposal commits a versioned semver bump to the changelog.',
    target: 'proposals'
  },
  {
    title: '4. Crew Board',
    text: 'See your seven active agent crews. Monitor their current missions, recent feedback scores, and permission grants. Drill down into individual crew configs to adjust scopes.',
    target: 'crews'
  },
  {
    title: '5. Deployment Pipeline',
    text: 'Tracks client engagements from ATTRACT to COMPOUND. Human gates (⟐) block auto-progression and route decisions to your queue to secure client trust boundaries.',
    target: 'pipeline'
  },
  {
    title: '6. W-Method Maturity Map',
    text: 'Visualizes client layer assessments (0 to 4). Evaluates foundation levels (foundation compute, VPN tunnels, local telemetry) before enabling value-adding model and vector database features.',
    target: 'maturity'
  },
  {
    title: '7. Governance Inspector',
    text: 'Audit client trust records, telemetry parameters, active grants, and the historical changelog. This ensures the operating system is strictly data-sovereign and local-first.',
    target: 'governance'
  }
]

export const TourOverlay: React.FC = () => {
  const { showTour, tourStep, setShowTour, setTourStep, setTab } = useKiboStore()

  if (!showTour) return null

  const step = TOUR_STEPS[tourStep]

  const handleNext = () => {
    if (tourStep < TOUR_STEPS.length - 1) {
      setTourStep(tourStep + 1)
      // Automatically switch tabs to show relevant section
      const tabMap: Record<number, any> = {
        0: 'cockpit',
        1: 'cockpit',
        2: 'cockpit',
        3: 'crews',
        4: 'pipeline',
        5: 'maturity',
        6: 'governance'
      }
      setTab(tabMap[tourStep + 1])
    } else {
      setShowTour(false)
    }
  }

  const handlePrev = () => {
    if (tourStep > 0) {
      setTourStep(tourStep - 1)
      const tabMap: Record<number, any> = {
        0: 'cockpit',
        1: 'cockpit',
        2: 'cockpit',
        3: 'crews',
        4: 'pipeline',
        5: 'maturity',
        6: 'governance'
      }
      setTab(tabMap[tourStep - 1])
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-bauhaus-grey border border-bauhaus-white w-full max-w-lg p-8 relative">
        <button 
          onClick={() => setShowTour(false)} 
          className="absolute top-4 right-4 text-bauhaus-lightgrey hover:text-bauhaus-white"
        >
          <X size={20} />
        </button>
        
        <div className="flex items-center space-x-2 text-bauhaus-accent mb-4">
          <HelpCircle size={20} />
          <span className="font-bold text-xs uppercase tracking-widest">Operator Onboarding Tour</span>
        </div>

        <h3 className="text-2xl font-bold uppercase tracking-tight text-bauhaus-white mb-3">
          {step.title}
        </h3>
        
        <p className="text-sm text-bauhaus-lightgrey leading-relaxed mb-8">
          {step.text}
        </p>

        <div className="flex justify-between items-center border-t border-bauhaus-mediumgrey pt-6">
          <div className="text-xs text-bauhaus-lightgrey">
            Step {tourStep + 1} of {TOUR_STEPS.length}
          </div>
          <div className="flex space-x-4">
            {tourStep > 0 && (
              <button 
                onClick={handlePrev}
                className="flex items-center space-x-1 text-xs text-bauhaus-white hover:text-bauhaus-accent"
              >
                <ChevronLeft size={16} />
                <span>Prev</span>
              </button>
            )}
            <button 
              onClick={handleNext}
              className="flex items-center space-x-1 text-xs bg-bauhaus-accent text-white px-4 py-2 hover:bg-opacity-80"
            >
              <span>{tourStep === TOUR_STEPS.length - 1 ? 'Finish Tour' : 'Next'}</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
