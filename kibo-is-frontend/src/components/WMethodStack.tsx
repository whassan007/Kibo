import React from 'react'

export interface LayerData {
  layer: number
  name: string
  crew: string
  module: string
}

const LAYERS: LayerData[] = [
  { layer: 7, name: 'Compound', crew: 'forge', module: 'KIBO Forge' },
  { layer: 6, name: 'Operate', crew: 'operator', module: 'KIBO Telemetry' },
  { layer: 5, name: 'Install', crew: 'installer', module: 'KIBO Net / Connect' },
  { layer: 4, name: 'Agree', crew: 'steward', module: 'KIBO Gateway' },
  { layer: 3, name: 'Diagnose', crew: 'diagnostician', module: 'KIBO Knowledge' },
  { layer: 2, name: 'Acquire', crew: 'scout', module: 'PE Channel' },
  { layer: 1, name: 'Attract', crew: 'herald', module: 'Category Brand' },
]

interface WMethodStackProps {
  activeLayer?: number
  scores?: Record<number, number>
  onLayerClick?: (layer: number) => void
}

export const WMethodStack: React.FC<WMethodStackProps> = ({
  activeLayer,
  scores,
  onLayerClick,
}) => {
  return (
    <div className="flex flex-col gap-1 w-full font-mono text-xs">
      <div className="text-[10px] uppercase tracking-wider text-bauhaus-lightgrey mb-2 border-b border-bauhaus-mediumgrey pb-1">
        W-Method Architecture Stack
      </div>
      <div className="flex flex-col border border-bauhaus-mediumgrey divide-y divide-bauhaus-mediumgrey">
        {LAYERS.map(({ layer, name, crew, module }) => {
          const score = scores ? scores[layer] : undefined
          const isActive = activeLayer === layer
          
          return (
            <div
              key={layer}
              onClick={() => onLayerClick?.(layer)}
              className={`p-3 transition-colors ${onLayerClick ? 'cursor-pointer hover:bg-bauhaus-black' : ''} ${
                isActive ? 'bg-bauhaus-black border-l-4 border-l-bauhaus-accent' : 'bg-transparent'
              }`}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <span className={`inline-flex items-center justify-center w-6 h-6 border ${isActive ? 'border-bauhaus-accent text-bauhaus-accent' : 'border-bauhaus-mediumgrey text-bauhaus-lightgrey'}`}>
                    L{layer}
                  </span>
                  <div>
                    <div className="font-bold text-bauhaus-white uppercase tracking-wide">{name}</div>
                    <div className="text-[10px] text-bauhaus-lightgrey uppercase">{crew} · {module}</div>
                  </div>
                </div>
                {score !== undefined && (
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-bauhaus-lightgrey">SCORE:</span>
                    <div className="flex gap-0.5 border border-bauhaus-mediumgrey p-0.5 bg-bauhaus-black w-24 h-4">
                      {Array.from({ length: 4 }).map((_, i) => {
                        const filled = score >= i + 1
                        return (
                          <div
                            key={i}
                            className={`flex-1 h-full ${
                              filled ? 'bg-bauhaus-accent' : 'bg-transparent'
                            }`}
                          />
                        )
                      })}
                    </div>
                    <span className="font-bold w-4 text-right text-bauhaus-white">{score}</span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
