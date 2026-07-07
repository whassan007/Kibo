import * as jsYaml from 'js-yaml'

const API_URL = '/api/kibo'

export interface KiboFileContent {
  content?: string
  files?: string[]
  isDirectory?: boolean
  error?: string
}

export const fetchFile = async (relativePath: string): Promise<string> => {
  const response = await fetch(`${API_URL}?path=${encodeURIComponent(relativePath)}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch file: ${relativePath}`)
  }
  const data: KiboFileContent = await response.json()
  return data.content || ''
}

export const fetchDirectory = async (relativePath: string): Promise<string[]> => {
  const response = await fetch(`${API_URL}?path=${encodeURIComponent(relativePath)}`)
  if (!response.ok) {
    throw new Error(`Failed to fetch directory: ${relativePath}`)
  }
  const data: KiboFileContent = await response.json()
  return data.files || []
}

export const saveFile = async (relativePath: string, content: string): Promise<void> => {
  const response = await fetch(`${API_URL}?path=${encodeURIComponent(relativePath)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ content })
  })
  if (!response.ok) {
    throw new Error(`Failed to save file: ${relativePath}`)
  }
}

// Typed models
export interface CompanyProfile {
  founder: { name: string; credentials: string }
  product: string
  human_reserve: string[]
  strategic_priorities: string[]
}

export interface BrandCategory {
  brand: string
  tagline: string
  posture: string
  wedge: string
  channel: string
  gap_owned: string
  core_ip: string
  capture_model: string
  proof: string
  messaging: { lead_with_mechanism: string; lead_with_governance: string }
}

export interface KiboCatalogModule {
  id: string
  name: string
  layer: number
  description: string
  status: string
  reuse_count: number
  eval_score: number
}

export interface CatalogState {
  modules: KiboCatalogModule[]
}

export interface LadderStep {
  step: string
  owner: string
}

export interface DeployabilityLadder {
  steps: LadderStep[]
}

export interface ScoreMetric {
  performance: number
  governance: number
  operational: number
}

export interface EvaluationScore {
  feedback_id: string
  boundary_violation: boolean
  claim_integrity: boolean
  scores: ScoreMetric
  overall_score: number
}

export interface ScoresState {
  scores: EvaluationScore[]
}

export interface QueueItem {
  id: string
  status: 'pending' | 'resolved' | 'rejected'
  timestamp: string
  details: string
}

export interface QueueState {
  queue: QueueItem[]
}

export interface Proposal {
  id: string
  target: string
  rationale: string
  diff: string
  evidence: string[]
  expected_effect: { cac: string; gates_per_deployment: string; founder_dependence: string }
  semver_bump: 'patch' | 'minor' | 'major'
  status: 'proposed' | 'reviewed' | 'promoted' | 'rejected'
}

export interface DeploymentFlowStep {
  name: string
  crew: string
  gate: string
  gate_type: 'human' | 'artifact' | 'none'
}

export interface DeploymentFlow {
  deployment_flow: {
    steps: Record<string, DeploymentFlowStep>
  }
}

export interface PipelineItem {
  client: string
  stage: string
  value: number
}

export const KiboService = {
  getPipeline: async (): Promise<PipelineItem[]> => {
    try {
      const raw = await fetchFile('.kibo/state/growth/pipeline.jsonl')
      if (!raw.trim()) return []
      return raw.split('\n')
        .filter(line => line.trim())
        .map(line => JSON.parse(line) as PipelineItem)
    } catch (e) {
      console.error('Failed to parse pipeline.jsonl:', e)
      return []
    }
  },

  getCompany: async (): Promise<CompanyProfile> => {
    const raw = await fetchFile('.kibo/state/company.yaml')
    return jsYaml.load(raw) as CompanyProfile
  },

  getBrand: async (): Promise<BrandCategory> => {
    const raw = await fetchFile('.kibo/state/brand.yaml')
    return jsYaml.load(raw) as BrandCategory
  },

  getCatalog: async (): Promise<CatalogState> => {
    const raw = await fetchFile('.kibo/state/catalog.yaml')
    return jsYaml.load(raw) as CatalogState
  },

  getLadder: async (): Promise<DeployabilityLadder> => {
    const raw = await fetchFile('.kibo/state/deployability/ladder.json')
    return JSON.parse(raw) as DeployabilityLadder
  },

  getScores: async (): Promise<ScoresState> => {
    const raw = await fetchFile('.kibo/state/evals/scores.json')
    return JSON.parse(raw) as ScoresState
  },

  getQueue: async (): Promise<QueueState> => {
    const raw = await fetchFile('.kibo/state/queue.json')
    return JSON.parse(raw) as QueueState
  },

  getFeedbackLog: async (): Promise<string> => {
    return await fetchFile('.kibo/state/feedback/log.md')
  },

  getProposals: async (): Promise<Proposal[]> => {
    const filenames = await fetchDirectory('.kibo/state/proposals/draft')
    const proposals: Proposal[] = []
    for (const name of filenames) {
      if (name.endsWith('.json')) {
        const raw = await fetchFile(`.kibo/state/proposals/draft/${name}`)
        try {
          proposals.push(JSON.parse(raw) as Proposal)
        } catch (e) {
          console.error(`Failed to parse proposal ${name}:`, e)
        }
      }
    }
    return proposals
  },

  getDeploymentFlow: async (): Promise<DeploymentFlow> => {
    const raw = await fetchFile('.kibo/config/deployment-flow.yaml')
    return jsYaml.load(raw) as DeploymentFlow
  },

  resolveQueueItem: async (taskId: string, status: 'resolved' | 'rejected' | 'pending'): Promise<QueueState> => {
    const queueState = await KiboService.getQueue()
    const updatedQueue = queueState.queue.map(item => {
      if (item.id === taskId) {
        return {
          ...item,
          status,
          resolved_at: new Date().toISOString()
        }
      }
      return item
    })
    const payload = { queue: updatedQueue }
    await saveFile('.kibo/state/queue.json', JSON.stringify(payload, null, 2))
    return payload
  },

  promoteProposal: async (proposalId: string): Promise<void> => {
    const proposals = await KiboService.getProposals()
    const targetProposal = proposals.find(p => p.id === proposalId)
    if (!targetProposal) {
      throw new Error(`Proposal not found: ${proposalId}`)
    }
    // Flip status to promoted
    targetProposal.status = 'promoted'
    await saveFile(
      `.kibo/state/proposals/draft/${proposalId}.json`,
      JSON.stringify(targetProposal, null, 2)
    )

    // Append to feedback log.md
    const logEntry = `\n## [${new Date().toISOString()}] FB-PROMOTE-${proposalId.slice(-4).toUpperCase()} (Promotion)\n- **Source:** operator-ui\n- **Category:** Autonomy Promotion\n- **Description:** Operator promoted proposal ${proposalId} targeting ${targetProposal.target}.\n- **Rubric Assessment:** Sovereign Autonomy\n- **Evidence:** Human-operator authorized promotion.\n`
    const currentLog = await KiboService.getFeedbackLog()
    await saveFile('.kibo/state/feedback/log.md', currentLog + logEntry)
  },

  rejectProposal: async (proposalId: string): Promise<void> => {
    const proposals = await KiboService.getProposals()
    const targetProposal = proposals.find(p => p.id === proposalId)
    if (!targetProposal) {
      throw new Error(`Proposal not found: ${proposalId}`)
    }
    targetProposal.status = 'rejected'
    await saveFile(
      `.kibo/state/proposals/draft/${proposalId}.json`,
      JSON.stringify(targetProposal, null, 2)
    )
  },

  logFeedback: async (feedback: {
    client_name: string
    category: string
    description: string
    rubric: string
    evidence: string
  }): Promise<void> => {
    const timestamp = new Date().toISOString()
    const fbId = `FB-${new Date().getFullYear()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`
    const md = `\n## [${timestamp}] ${fbId} (${feedback.category})\n- **Source:** ${feedback.client_name}\n- **Category:** ${feedback.category}\n- **Description:** ${feedback.description}\n- **Rubric Assessment:** ${feedback.rubric}\n- **Evidence:** ${feedback.evidence}\n`
    const currentLog = await KiboService.getFeedbackLog()
    await saveFile('.kibo/state/feedback/log.md', currentLog + md)
  }
}
