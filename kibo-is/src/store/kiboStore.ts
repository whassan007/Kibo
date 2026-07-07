import { create } from 'zustand'
import { KiboService } from '../services/kiboService'
import type {
  CompanyProfile,
  BrandCategory,
  CatalogState,
  DeployabilityLadder,
  ScoresState,
  QueueState,
  Proposal,
  DeploymentFlow,
  PipelineItem
} from '../services/kiboService'

interface KiboStoreState {
  // Server state
  company: CompanyProfile | null
  brand: BrandCategory | null
  catalog: CatalogState | null
  ladder: DeployabilityLadder | null
  scores: ScoresState | null
  queue: QueueState | null
  proposals: Proposal[]
  feedbackLog: string
  flow: DeploymentFlow | null
  pipeline: PipelineItem[]
  loading: boolean
  error: string | null

  // UI state
  activeTab: 'cockpit' | 'crews' | 'pipeline' | 'maturity' | 'governance' | 'docs' | 'tutorial'
  showTour: boolean
  tourStep: number
  helpTopic: string | null

  // Actions
  setTab: (tab: KiboStoreState['activeTab']) => void
  setShowTour: (show: boolean) => void
  setTourStep: (step: number) => void
  setHelpTopic: (topic: string | null) => void
  loadAll: () => Promise<void>
  resolveQueueItem: (taskId: string, status: 'resolved' | 'rejected' | 'pending') => Promise<void>
  promoteProposal: (proposalId: string) => Promise<void>
  rejectProposal: (proposalId: string) => Promise<void>
}

export const useKiboStore = create<KiboStoreState>((set) => ({
  company: null,
  brand: null,
  catalog: null,
  ladder: null,
  scores: null,
  queue: null,
  proposals: [],
  feedbackLog: '',
  flow: null,
  pipeline: [],
  loading: true,
  error: null,

  activeTab: 'cockpit',
  showTour: false,
  tourStep: 0,
  helpTopic: null,

  setTab: (activeTab) => set({ activeTab }),
  setShowTour: (showTour) => set({ showTour }),
  setTourStep: (tourStep) => set({ tourStep }),
  setHelpTopic: (helpTopic) => set({ helpTopic }),

  loadAll: async () => {
    try {
      const [company, brand, catalog, ladder, scores, queue, proposals, feedbackLog, flow, pipeline] = await Promise.all([
        KiboService.getCompany().catch(() => null),
        KiboService.getBrand().catch(() => null),
        KiboService.getCatalog().catch(() => null),
        KiboService.getLadder().catch(() => null),
        KiboService.getScores().catch(() => null),
        KiboService.getQueue().catch(() => null),
        KiboService.getProposals().catch(() => []),
        KiboService.getFeedbackLog().catch(() => ''),
        KiboService.getDeploymentFlow().catch(() => null),
        KiboService.getPipeline().catch(() => [])
      ])
      set({
        company,
        brand,
        catalog,
        ladder,
        scores,
        queue,
        proposals,
        feedbackLog,
        flow,
        pipeline,
        loading: false,
        error: null
      })
    } catch (e: any) {
      set({ error: e.message || 'Failed to load KIBO OS state files.', loading: false })
    }
  },

  resolveQueueItem: async (taskId, status) => {
    try {
      const updatedQueue = await KiboService.resolveQueueItem(taskId, status)
      set({ queue: updatedQueue })
    } catch (e: any) {
      set({ error: `Failed to resolve queue item: ${e.message}` })
    }
  },

  promoteProposal: async (proposalId) => {
    try {
      await KiboService.promoteProposal(proposalId)
      const [proposals, feedbackLog] = await Promise.all([
        KiboService.getProposals(),
        KiboService.getFeedbackLog()
      ])
      set({ proposals, feedbackLog })
    } catch (e: any) {
      set({ error: `Failed to promote proposal: ${e.message}` })
    }
  },

  rejectProposal: async (proposalId) => {
    try {
      await KiboService.rejectProposal(proposalId)
      const proposals = await KiboService.getProposals()
      set({ proposals })
    } catch (e: any) {
      set({ error: `Failed to reject proposal: ${e.message}` })
    }
  }
}))

// Auto-polling utility
let pollInterval: ReturnType<typeof setInterval> | null = null

export const startPolling = () => {
  if (pollInterval) return
  // Initial load
  useKiboStore.getState().loadAll()
  
  pollInterval = setInterval(() => {
    useKiboStore.getState().loadAll()
  }, 5000)
}

export const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}
