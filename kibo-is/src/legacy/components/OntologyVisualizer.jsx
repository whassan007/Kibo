import React, { useState, useEffect, useMemo } from 'react';
import { Network, Search, Filter, ArrowRight, BookOpen, Layers, Shield, RefreshCw } from 'lucide-react';

export default function OntologyVisualizer({ API_BASE }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [hoveredNodeId, setHoveredNodeId] = useState(null);
  const [selectedClass, setSelectedClass] = useState('all');

  const fetchOntology = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/ontology/export`, {
        headers: {
          'x-kibo-scope': 'expert',
          'Authorization': `Bearer ${localStorage.getItem('kibo_token') || 'mock-expert-token'}`
        }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        console.error(`Ontology export API returned ${res.status}. Using mock data.`);
        setData({
          "@context": "https://schema.org/",
          "@graph": [
            { "@id": "Law25", "@type": "Legislation", "name": "Quebec Law 25", "description": "Privacy legislation for Quebec." },
            { "@id": "PIA", "@type": "Requirement", "name": "Privacy Impact Assessment", "mandatedBy": "Law25" },
            { "@id": "CPRA", "@type": "Legislation", "name": "California Privacy Rights Act" },
            { "@id": "OptOut", "@type": "Requirement", "name": "Do Not Sell/Share", "mandatedBy": "CPRA" },
            { "@id": "PII", "@type": "DataType", "name": "Personally Identifiable Information", "protectedBy": ["Law25", "CPRA"] }
          ]
        });

      }
    } catch (e) {
        console.error("Error fetching ontology data:", e);

        setData({
          "@context": "https://schema.org/",
          "@graph": [
            { "@id": "Law25", "@type": "Legislation", "name": "Quebec Law 25", "description": "Privacy legislation for Quebec." },
            { "@id": "PIA", "@type": "Requirement", "name": "Privacy Impact Assessment", "mandatedBy": "Law25" },
            { "@id": "CPRA", "@type": "Legislation", "name": "California Privacy Rights Act" },
            { "@id": "OptOut", "@type": "Requirement", "name": "Do Not Sell/Share", "mandatedBy": "CPRA" },
            { "@id": "PII", "@type": "DataType", "name": "Personally Identifiable Information", "protectedBy": ["Law25", "CPRA"] }
          ]
        });

      } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOntology();
  }, [API_BASE]);

  // Parse JSON-LD into graph structures
  const graph = useMemo(() => {
    if (!data || !data['@graph']) return { nodes: [], edges: [], nodesById: {} };

    const nodes = [];
    const edges = [];
    const nodesById = {};

    // First pass: extract all instance nodes
    data['@graph'].forEach(item => {
      const id = item['@id'] ? item['@id'].replace('kibo:', '') : '';
      const type = item['@type'] ? item['@type'].replace('kibo:', '') : '';
      const label = item['label'] || id;

      if (id && type) {
        const properties = {};
        Object.keys(item).forEach(k => {
          if (k.startsWith('kibo:') && k !== 'kibo:type') {
            properties[k.replace('kibo:', '')] = item[k];
          }
        });

        const node = { id, type, label, properties };
        nodes.push(node);
        nodesById[id] = node;
      }
    });

    // Second pass: extract relationships/edges
    data['@graph'].forEach(item => {
      const srcId = item['@id'] ? item['@id'].replace('kibo:', '') : '';
      if (!srcId) return;

      Object.keys(item).forEach(pred => {
        if (pred.startsWith('kibo:') && pred !== 'kibo:type' && typeof item[pred] === 'object' && item[pred]['@id']) {
          const predicate = pred.replace('kibo:', '');
          const targetId = item[pred]['@id'].replace('kibo:', '');
          
          // Verify both ends exist
          if (nodesById[srcId] && nodesById[targetId]) {
            edges.push({
              source: srcId,
              target: targetId,
              predicate: predicate,
              id: `${srcId}-${targetId}-${predicate}`
            });
          }
        }
      });
    });

    return { nodes, edges, nodesById };
  }, [data]);

  // Classify nodes into logical UI layers
  const LAYERS = [
    { id: 'cluster_input', label: 'Inputs & Triggers', prefix: 'In_' },
    { id: 'cluster_hidden1', label: 'Statutes & Frameworks', prefix: 'H1_' },
    { id: 'cluster_torts', label: 'Privacy Torts', prefix: 'T_' },
    { id: 'cluster_hidden2', label: 'Governance Controls', prefix: 'H2_' },
    { id: 'cluster_cert', label: 'Certifications', prefix: 'Cert_' },
    { id: 'cluster_hidden3', label: 'Operational Controls', prefix: 'H3_' },
    { id: 'cluster_penalty', label: 'Penalties & Infractions', prefix: 'Pen_' },
    { id: 'cluster_output', label: 'Mandatory Artifacts', prefix: 'Out_' }
  ];

  // Helper to color layers
  const getLayerColor = (layerId) => {
    switch (layerId) {
      case 'cluster_input': return 'border-blue-500 bg-blue-50/50 text-blue-800';
      case 'cluster_hidden1': return 'border-purple-500 bg-purple-50/50 text-purple-800';
      case 'cluster_torts': return 'border-red-500 bg-red-50/50 text-red-800';
      case 'cluster_hidden2': return 'border-indigo-500 bg-indigo-50/50 text-indigo-800';
      case 'cluster_cert': return 'border-cyan-500 bg-cyan-50/50 text-cyan-800';
      case 'cluster_hidden3': return 'border-emerald-500 bg-emerald-50/50 text-emerald-800';
      case 'cluster_penalty': return 'border-amber-600 bg-amber-50/50 text-amber-900';
      case 'cluster_output': return 'border-teal-500 bg-teal-50/50 text-teal-800';
      default: return 'border-gray-300 bg-gray-50 text-gray-800';
    }
  };

  // Node filtering
  const filteredNodesByLayer = useMemo(() => {
    const layerMap = {};
    LAYERS.forEach(l => { layerMap[l.id] = [] });
    layerMap['other'] = [];

    graph.nodes.forEach(node => {
      // Check search filter
      if (searchQuery && !node.label.toLowerCase().includes(searchQuery.toLowerCase()) && !node.id.toLowerCase().includes(searchQuery.toLowerCase())) {
        return;
      }
      // Check class filter
      if (selectedClass !== 'all' && node.type !== selectedClass) {
        return;
      }

      let assigned = false;
      for (const layer of LAYERS) {
        if (node.id.startsWith(layer.prefix)) {
          layerMap[layer.id].push(node);
          assigned = true;
          break;
        }
      }
      if (!assigned) {
        layerMap['other'].push(node);
      }
    });

    return layerMap;
  }, [graph, searchQuery, selectedClass]);

  // Identify active connections for highlighting
  const activeConnections = useMemo(() => {
    const targetId = hoveredNodeId || selectedNodeId;
    if (!targetId) return { sources: new Set(), targets: new Set(), edges: new Set() };

    const sources = new Set();
    const targets = new Set();
    const activeEdges = new Set();

    graph.edges.forEach(edge => {
      if (edge.source === targetId) {
        targets.add(edge.target);
        activeEdges.add(edge.id);
      }
      if (edge.target === targetId) {
        sources.add(edge.source);
        activeEdges.add(edge.id);
      }
    });

    return { sources, targets, edges: activeEdges };
  }, [graph, hoveredNodeId, selectedNodeId]);

  const selectedNodeDetails = useMemo(() => {
    if (!selectedNodeId) return null;
    return graph.nodesById[selectedNodeId] || null;
  }, [graph, selectedNodeId]);

  return (
    <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6 shadow-xs flex flex-col h-[calc(100vh-12rem)] min-h-[500px]">
      
      {/* Header controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-[#E5E7EB] pb-4 mb-4 gap-4">
        <div>
          <h2 className="text-sm font-black text-gray-900 uppercase tracking-widest flex items-center gap-2">
            <Network className="text-blue-600" size={16} />
            Compliance Net Ontology Visualizer
          </h2>
          <p className="text-[10px] text-gray-400 mt-0.5">
            Semantic mapping of triggers, statutory frameworks, torts, and output artifacts in kibo_state.db
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2 text-gray-450" size={12} />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="bg-gray-50 border border-[#E5E7EB] text-[10px] rounded-lg pl-8 pr-3 py-1.5 focus:outline-none focus:border-blue-500 w-44"
            />
          </div>

          <select
            value={selectedClass}
            onChange={e => setSelectedClass(e.target.value)}
            className="bg-gray-50 border border-[#E5E7EB] text-[10px] rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Classes</option>
            <option value="Jurisdiction">Jurisdiction</option>
            <option value="LegalFramework">LegalFramework</option>
            <option value="DataCategory">DataCategory</option>
            <option value="ProcessingActivity">ProcessingActivity</option>
            <option value="ComplianceObligation">ComplianceObligation</option>
            <option value="AssessmentArtifact">AssessmentArtifact</option>
          </select>

          <button 
            onClick={fetchOntology}
            className="p-1.5 text-gray-500 hover:text-blue-600 bg-gray-50 hover:bg-blue-50 border border-[#E5E7EB] rounded-lg transition-all"
          >
            <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-grow flex items-center justify-center">
          <div className="flex flex-col items-center space-y-2">
            <RefreshCw size={24} className="text-blue-600 animate-spin" />
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Loading Ontology Graph...</span>
          </div>
        </div>
      ) : (
        <div className="flex-grow flex gap-4 overflow-hidden">
          
          {/* Layered Columns Container */}
          <div className="flex-grow overflow-x-auto overflow-y-hidden pb-2 flex gap-4 pr-2">
            {LAYERS.map(layer => {
              const nodesInLayer = filteredNodesByLayer[layer.id] || [];
              if (nodesInLayer.length === 0 && !searchQuery) return null;

              return (
                <div key={layer.id} className="flex-shrink-0 w-64 border border-[#E5E7EB] rounded-xl bg-gray-50/30 flex flex-col h-full max-h-full">
                  <div className="p-3 border-b border-[#E5E7EB] bg-gray-50 flex items-center justify-between">
                    <span className="text-[10px] font-black text-gray-700 uppercase tracking-wider">{layer.label}</span>
                    <span className="bg-gray-200 text-[9px] font-extrabold text-gray-600 px-1.5 py-0.5 rounded-full">
                      {nodesInLayer.length}
                    </span>
                  </div>
                  
                  {/* Nodes list in Layer */}
                  <div className="p-3 flex-grow overflow-y-auto space-y-2">
                    {nodesInLayer.map(node => {
                      const isSelected = selectedNodeId === node.id;
                      const isHovered = hoveredNodeId === node.id;
                      const isDirectSource = activeConnections.sources.has(node.id);
                      const isDirectTarget = activeConnections.targets.has(node.id);
                      
                      let borderClass = 'border-[#E5E7EB]';
                      let bgClass = 'bg-white';
                      
                      if (isSelected || isHovered) {
                        borderClass = 'border-blue-500 ring-1 ring-blue-500/20';
                        bgClass = 'bg-blue-50/30';
                      } else if (isDirectSource) {
                        borderClass = 'border-amber-400 border-dashed';
                        bgClass = 'bg-amber-50/10';
                      } else if (isDirectTarget) {
                        borderClass = 'border-emerald-400 border-dashed';
                        bgClass = 'bg-emerald-50/10';
                      }

                      return (
                        <div
                          key={node.id}
                          onClick={() => setSelectedNodeId(node.id)}
                          onMouseEnter={() => setHoveredNodeId(node.id)}
                          onMouseLeave={() => setHoveredNodeId(null)}
                          className={`border rounded-lg p-2.5 cursor-pointer transition-all hover:shadow-xs flex flex-col space-y-1.5 ${borderClass} ${bgClass}`}
                        >
                          <div className="flex items-start justify-between gap-1">
                            <span className="text-[10px] font-black text-gray-900 leading-snug">{node.label}</span>
                            <span className="text-[7px] font-mono text-gray-400 bg-gray-100 px-1 rounded uppercase flex-shrink-0">
                              {node.type.replace('Compliance', '')}
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between text-[7px] text-gray-400 font-mono">
                            <span>ID: {node.id}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Details Sidebar */}
          <div className="w-80 border-l border-[#E5E7EB] pl-4 flex-shrink-0 flex flex-col h-full max-h-full">
            {selectedNodeDetails ? (
              <div className="space-y-4 flex flex-col h-full overflow-y-auto pr-1">
                <div>
                  <div className="text-[9px] font-mono text-blue-600 bg-blue-50 border border-blue-200/50 rounded px-1.5 py-0.5 inline-block uppercase tracking-wider mb-2">
                    {selectedNodeDetails.type}
                  </div>
                  <h3 className="text-xs font-black text-gray-900 uppercase tracking-wide leading-tight">
                    {selectedNodeDetails.label}
                  </h3>
                  <span className="text-[9px] font-mono text-gray-400 block mt-1">ID: {selectedNodeDetails.id}</span>
                </div>

                {/* Edges analysis */}
                <div className="space-y-3">
                  <div>
                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest block border-b border-[#E5E7EB] pb-1 mb-2">
                      Inbound Dependencies
                    </span>
                    <div className="space-y-1">
                      {graph.edges.filter(e => e.target === selectedNodeId).map(edge => {
                        const src = graph.nodesById[edge.source];
                        return (
                          <div 
                            key={edge.id} 
                            onClick={() => setSelectedNodeId(edge.source)}
                            className="text-[9px] text-gray-600 hover:text-blue-600 cursor-pointer flex items-center gap-1.5 p-1 hover:bg-gray-50 rounded"
                          >
                            <span className="font-mono text-gray-400">[{edge.source}]</span>
                            <ArrowRight size={10} className="transform rotate-180 text-gray-400" />
                            <span className="font-semibold text-gray-800 truncate">{src ? src.label : edge.source}</span>
                          </div>
                        );
                      })}
                      {graph.edges.filter(e => e.target === selectedNodeId).length === 0 && (
                        <span className="text-[9px] text-gray-400 italic block p-1">No inbound connections</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest block border-b border-[#E5E7EB] pb-1 mb-2">
                      Outbound Triggers
                    </span>
                    <div className="space-y-1">
                      {graph.edges.filter(e => e.source === selectedNodeId).map(edge => {
                        const dst = graph.nodesById[edge.target];
                        return (
                          <div 
                            key={edge.id}
                            onClick={() => setSelectedNodeId(edge.target)}
                            className="text-[9px] text-gray-600 hover:text-blue-600 cursor-pointer flex items-center gap-1.5 p-1 hover:bg-gray-50 rounded"
                          >
                            <span className="font-semibold text-gray-800 truncate">{dst ? dst.label : edge.target}</span>
                            <ArrowRight size={10} className="text-gray-400" />
                            <span className="font-mono text-gray-400">[{edge.target}]</span>
                          </div>
                        );
                      })}
                      {graph.edges.filter(e => e.source === selectedNodeId).length === 0 && (
                        <span className="text-[9px] text-gray-400 italic block p-1">No outbound triggers</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-center p-4">
                <div className="space-y-1">
                  <Network className="text-gray-300 mx-auto" size={32} />
                  <span className="text-[10px] text-gray-400 font-bold block uppercase tracking-wider">Select a node</span>
                  <span className="text-[9px] text-gray-400 block leading-normal">
                    Click any node in the grid columns to trace its inbound dependencies and downstream controls.
                  </span>
                </div>
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
}
