import React, { useState } from 'react'
import { HelpCircle, Info, CheckSquare } from 'lucide-react'
import { useKiboStore } from '../store/kiboStore'
import { WMethodStack } from './WMethodStack'

export const MaturityMap: React.FC = () => {
  const { setHelpTopic } = useKiboStore()
  const [selectedLayer, setSelectedLayer] = useState<number | null>(null)

  // Hardcode 7 layers as per W-Method specification (§6)
  const LAYERS_DATA = [
    {
      num: 1,
      name: 'Foundation & Compute',
      module: 'Reference-rack Spec',
      description: 'Sovereign inference infrastructure, right-sized (DGX Spark, MBP/Mac Studio, isolated VPS).',
      metric: 'Telemetry active, local compute allocation matches demand.',
      status: 'Standardized',
      level: 2
    },
    {
      num: 2,
      name: 'Security & Transport',
      module: 'KIBO Net (kibo-net)',
      description: 'Zero-trust network layer creating isolated payloads utilizing Tailscale mesh and Firewalla VPN routing.',
      metric: '100% network packets pass local firewall; encrypted client boundaries confirmed.',
      status: 'Standardized',
      level: 2
    },
    {
      num: 3,
      name: 'Knowledge / RAG',
      module: 'KIBO Knowledge (kibo-rag)',
      description: 'In-boundary local grounding with vector databases (e.g. Postgres pgvector), embeddings, and custom parsers.',
      metric: 'Document parsing latency < 2s; zero external cloud calls.',
      status: 'Instrumented',
      level: 3
    },
    {
      num: 4,
      name: 'Model Services',
      module: 'KIBO Gateway (kibo-gateway)',
      description: 'Local gateway routing inference calls to the cheapest-capable model (Ollama, LM Studio, vLLM).',
      metric: 'Average cost per token matches local baseline; load balancing active.',
      status: 'Standardized',
      level: 2
    },
    {
      num: 5,
      name: 'Protocol & Interface',
      module: 'KIBO Connect (kibo-connect)',
      description: 'MCP servers, registries, and secure APIs linking client terminals and workflows.',
      metric: 'FastMCP surface operational; tool validation schemas strictly checked.',
      status: 'Instrumented',
      level: 3
    },
    {
      num: 6,
      name: 'Operate',
      module: 'KIBO Telemetry (kibo-telemetry)',
      description: 'Run-state auditing, spend checks, evaluations, and baseline drift checks.',
      metric: 'Telemetry database tracking scores; alerts configured.',
      status: 'Standardized',
      level: 2
    },
    {
      num: 7,
      name: 'Orchestration & Apps',
      module: 'Vertical Agents (Regentic/WFair)',
      description: 'Objectives transformed into multi-agent workflows executing in isolated sandboxes.',
      metric: 'Autonomous workflow completion rate: 94%.',
      status: 'Ad-hoc',
      level: 1
    }
  ]

  const scores: Record<number, number> = {
    1: 2,
    2: 2,
    3: 3,
    4: 2,
    5: 3,
    6: 2,
    7: 1
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center border-b border-bauhaus-mediumgrey pb-3">
        <h2 className="text-xl font-bold uppercase tracking-tight text-bauhaus-white flex items-center space-x-2">
          <span>W-Method Maturity Map</span>
          <span className="text-xs bg-bauhaus-accent text-bauhaus-black px-2 py-0.5 font-extrabold">Level 0-4 Stack</span>
        </h2>
        <button 
          onClick={() => setHelpTopic('maturity')} 
          className="text-bauhaus-lightgrey hover:text-bauhaus-white flex items-center space-x-1 text-xs"
        >
          <HelpCircle size={14} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Maturity Spec</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 font-mono text-xs">
        {/* W-Method Architecture Stack */}
        <div className="lg:col-span-2 space-y-4">
          <div className="text-xs text-bauhaus-lightgrey mb-4">
            Click a layer in the stack below to audit active configurations, software modules, and parameters.
          </div>
          
          <WMethodStack 
            scores={scores} 
            activeLayer={selectedLayer || undefined} 
            onLayerClick={(layer) => setSelectedLayer(layer)} 
          />
        </div>

        {/* Selected Layer Detail Sidebar */}
        <div className="border border-bauhaus-mediumgrey p-6 bg-bauhaus-grey h-full flex flex-col justify-between">
          {selectedLayer !== null ? (() => {
            const layer = LAYERS_DATA.find(l => l.num === selectedLayer)!
            return (
              <div className="space-y-6 select-none">
                <div>
                  <div className="text-[9px] text-bauhaus-accent uppercase tracking-widest font-bold mb-1">
                    Layer Audit Detail
                  </div>
                  <h3 className="text-lg font-bold uppercase tracking-tight text-bauhaus-white">
                    {layer.name}
                  </h3>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-1">
                    KIBO Install Module
                  </div>
                  <div className="text-xs text-bauhaus-white font-mono font-bold flex items-center space-x-1.5">
                    <CheckSquare size={12} className="text-bauhaus-accent" />
                    <span>{layer.module}</span>
                  </div>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-1">
                    Functional Description
                  </div>
                  <p className="text-[10px] text-bauhaus-lightgrey leading-relaxed">
                    {layer.description}
                  </p>
                </div>

                <div>
                  <div className="text-[9px] text-bauhaus-lightgrey uppercase tracking-wider font-bold mb-1">
                    Active Verification Metrics
                  </div>
                  <p className="text-[10px] text-bauhaus-lightgrey leading-relaxed">
                    {layer.metric}
                  </p>
                </div>
              </div>
            )
          })() : (
            <div className="flex flex-col items-center justify-center h-64 text-center space-y-4">
              <Info size={24} className="text-bauhaus-mediumgrey" />
              <div className="text-[10px] text-bauhaus-lightgrey font-bold uppercase tracking-wider">
                Select a W-Method layer to inspect.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
