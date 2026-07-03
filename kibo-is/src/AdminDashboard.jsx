import React, { useState, useEffect } from 'react';
import {
  Activity, Server, Database, Sparkles, AlertTriangle, Layers,
  Terminal, ShieldAlert, Cpu, BookOpen, Clock, Play, FileText, Check, CheckSquare,
  Square, Edit, Save, List, UserCheck, Shield, ChevronRight, X, ArrowRight, GitBranch,
  FileCode, CheckCircle, AlertOctagon, HelpCircle, HardDrive, RefreshCw, BarChart2,
  Lock, RefreshCcw, Download, Info
} from 'lucide-react';

export default function AdminDashboard({
  API_BASE,
  activeJurisdiction,
  jurConfig,
  legalLibrary,
  agentLessons,
  fetchLessons,
  fetchLegalLibrary,
  simLogs,
  simIsRunning,
  setSimLogs,
  setSimIsRunning
}) {
  const [adminTab, setAdminTab] = useState('dashboard');
  const [selectedNode, setSelectedNode] = useState(null);
  const [diffMode, setDiffMode] = useState(false);
  const [triggers, setTriggers] = useState([
    { id: 'TR-101', timestamp: '2026-07-03 01:10', priority: 'high', source: 'EDPB Feed', framework: 'GDPR', jurisdiction: 'European Union', client: 'Kids Help Phone', confidence: '94%', impact: 'High', status: 'Triaged' },
    { id: 'TR-102', timestamp: '2026-07-03 01:12', priority: 'medium', source: 'CMP Telemetry', framework: 'Law 25', jurisdiction: 'Quebec, CA', client: 'KHP Foundation', confidence: '88%', impact: 'Medium', status: 'Pending Review' },
    { id: 'TR-103', timestamp: '2026-07-02 23:45', priority: 'critical', source: 'Privacy Officer Ticket', framework: 'PHIPA', jurisdiction: 'Ontario, CA', client: 'Clinical Portal', confidence: '99%', impact: 'High', status: 'Investigating' },
    { id: 'TR-104', timestamp: '2026-07-02 22:15', priority: 'low', source: 'ISO Auditer', framework: 'ISO 27701', jurisdiction: 'Global', client: 'All', confidence: '95%', impact: 'Low', status: 'Completed' }
  ]);

  const [agents, setAgents] = useState([
    { name: 'Ingestion Agent', version: 'v2.1.4', status: 'idle', queue: 0, runtime: '1.2s', cost: '$0.004', success: '99.8%', failure: '0.2%', memory: '124MB', cpu: '4%', tokens: '1.5k' },
    { name: 'Adaptation Coder', version: 'v3.0.2', status: 'processing', queue: 1, runtime: '4.8s', cost: '$0.015', success: '97.2%', failure: '2.8%', memory: '512MB', cpu: '68%', tokens: '8.4k' },
    { name: 'Self-Critique Auditor', version: 'v2.2.0', status: 'idle', queue: 0, runtime: '2.5s', cost: '$0.008', success: '98.5%', failure: '1.5%', memory: '256MB', cpu: '12%', tokens: '3.2k' },
    { name: 'Deployment Controller', version: 'v1.8.1', status: 'waiting', queue: 2, runtime: '0.8s', cost: '$0.002', success: '99.9%', failure: '0.1%', memory: '96MB', cpu: '2%', tokens: '500' }
  ]);

  const [deployments, setDeployments] = useState([
    { version: 'v2.8.4-rel', environment: 'production', status: 'active', proposed_by: 'Adaptation Coder', approved_by: 'CPO (HITL)', timestamp: '2026-07-03 01:16', commit: '89a0fcdb' },
    { version: 'v2.8.3-rel', environment: 'production', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'System Admin', timestamp: '2026-07-03 00:05', commit: 'f45bdcca' },
    { version: 'v2.8.4-rc1', environment: 'staging', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'Automatic (Score > 8)', timestamp: '2026-07-02 23:45', commit: 'c90cdbea' }
  ]);

  const [audits, setAudits] = useState([
    { timestamp: '2026-07-03 01:16', user: 'Waël Hassan', agent: 'Deployment Controller', llm: 'qwen2.5-coder:32b', action: 'Deploy UI adaptation template', hash: 'SHA256:d9b2089f', status: 'success' },
    { timestamp: '2026-07-03 01:15', user: 'LangGraph Engine', agent: 'Self-Critique Auditor', llm: 'qwen3.6:latest', action: 'Grounded RAG critique scoring (9/10)', hash: 'SHA256:b8c983ea', status: 'approved' },
    { timestamp: '2026-07-03 01:12', user: 'LangGraph Engine', agent: 'Self-Critique Auditor', llm: 'qwen3.6:latest', action: 'Grounded RAG critique scoring (5/10)', hash: 'SHA256:c0901e9d', status: 'rejected' }
  ]);

  const [clients, setClients] = useState([
    { name: 'Kids Help Phone', organization: 'KHP Canada', role: 'Data Controller', coverage: ['PIPEDA', 'Quebec Law 25', 'PHIPA'], users: 24, status: 'active' },
    { name: 'KHP Foundation', organization: 'KHP Foundation', role: 'Joint Controller', coverage: ['PIPEDA', 'CASL'], users: 8, status: 'active' },
    { name: 'Crisis Support Portal', organization: 'Clinical Services', role: 'Processor', coverage: ['PHIPA', 'CYFSA'], users: 12, status: 'active' }
  ]);

  const [notifications, setNotifications] = useState([
    { id: 1, type: 'critical', msg: 'Missing Legal Ground Truth Citation for new Cookie Regulation trigger.', time: '2 mins ago' },
    { id: 2, type: 'info', msg: 'LangGraph loop auto-adaptation evaluated with Score: 9/10.', time: '10 mins ago' },
    { id: 3, type: 'warning', msg: 'Model confidence score dropped below 85% on CPRA logic formulation.', time: '1 hour ago' }
  ]);

  const [selectedAuditFilter, setSelectedAuditFilter] = useState('all');

  const nodes = [
    { id: 'trigger', label: 'Trigger Ingestion', status: simIsRunning ? 'running' : 'completed', agent: 'Ingestion Agent', llm: 'qwen2.5:7b', cost: '$0.002', latency: '240ms' },
    { id: 'analysis', label: 'Ingestion & Analysis', status: simIsRunning ? 'running' : 'completed', agent: 'Ingestion Agent', llm: 'qwen3.6:latest', cost: '$0.008', latency: '1.2s' },
    { id: 'adaptation', label: 'Adaptation Proposer', status: simIsRunning ? 'waiting' : 'completed', agent: 'Adaptation Coder', llm: 'qwen2.5-coder:32b', cost: '$0.024', latency: '4.5s' },
    { id: 'evaluation', label: 'Self-Critique Auditor', status: simIsRunning ? 'waiting' : 'completed', agent: 'Self-Critique Auditor', llm: 'qwen3.6:latest', cost: '$0.012', latency: '2.3s' },
    { id: 'deploy', label: 'Deployment Gateway', status: simIsRunning ? 'waiting' : 'completed', agent: 'Deployment Controller', llm: 'rule-based', cost: '$0.000', latency: '50ms' }
  ];

  const nodeStates = {
    trigger: { input: 'Regulatory Feed Event / Webhook', output: 'Trigger Data Object', messages: ['Ingesting Law 25 compliance rules updates.'], context: 'PIPEDA & Law 25 parameters loaded.', reasoning: 'Parsed Law 25 changes to target campaign templates.' },
    analysis: { input: 'Raw statutory triggers', output: 'Ingested compliance variables', messages: ['Matched keywords: bilingual, Quebec.'], context: 'LAW25-SEC14 (Quebec Law 25)', reasoning: 'Grounded trigger inside legal library.' },
    adaptation: { input: 'Ingested context + rulesets', output: 'Proposed compliance logic code', messages: ['Inject strict Quebec Law 25 consent parameters.'], context: 'GDPR-ART28, PIPEDA.', reasoning: 'Formulated logic templates for review.' },
    evaluation: { input: 'Adaptation proposal code', output: 'Critique Audit Report', messages: ['Grounded verification checks passed.'], context: 'RAG verification model.', reasoning: 'Grounded safety checks evaluated. Score: 9/10.' },
    deploy: { input: 'Approved schema', output: 'Applied production configuration', messages: ['Vite production assets updated.'], context: 'VPS root directory.', reasoning: 'Triggered canary build and uvicorn hot reload.' }
  };

  const handleSimulateCycle = async () => {
    setSimIsRunning(true);
    setSimLogs(['[Agent Gateway] Ingesting dynamic client regulatory update...']);
    setTimeout(() => {
      setSimLogs(prev => [...prev, '[RAG Engine] Successfully retrieved 1 grounded clauses: LAW25-SEC14', '[Adaptation Node] Proposed logical changes updated.']);
    }, 1500);
    setTimeout(() => {
      setSimLogs(prev => [...prev, '[Evaluation Node] Verification critique complete. Score: 9/10 (APPROVED)', '[Deployment Controller] Live production deployment succeeded.']);
      setSimIsRunning(false);
    }, 3500);
  };

  const downloadAudits = (format) => {
    alert(`Downloading audit timeline as ${format.toUpperCase()}...`);
  };

  return (
    <div className="flex-1 flex bg-[#090C15] text-[#E2E8F0] overflow-hidden font-sans">
      
      {/* Sidebar Nav */}
      <div className="w-60 bg-[#0E1325] border-r border-[#1E294B] p-4 flex flex-col justify-between">
        <div className="space-y-6">
          <div className="flex items-center space-x-2.5 px-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-wider text-gray-300">AI Ops Mission Control</span>
          </div>

          <nav className="space-y-1">
            {[
              { id: 'dashboard', label: 'Executive Dashboard', icon: Activity },
              { id: 'engine', label: 'Improvement Engine', icon: Sparkles },
              { id: 'langgraph', label: 'LangGraph Visualizer', icon: GitBranch },
              { id: 'rag', label: 'RAG Knowledge Base', icon: BookOpen },
              { id: 'source_viewer', label: 'Authoritative Sources', icon: FileCode },
              { id: 'trust_tiers', label: 'Trust Tiers', icon: Shield },
              { id: 'hitl', label: 'HITL Governance Queue', icon: UserCheck },
              { id: 'deployment', label: 'Deployment Center', icon: Layers },
              { id: 'telemetry', label: 'UX Telemetry Feedback', icon: BarChart2 },
              { id: 'agents', label: 'AI Agent Monitor', icon: Cpu },
              { id: 'audits', label: 'Audit History', icon: FileText }
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = adminTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setAdminTab(tab.id)}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 text-xs rounded-lg transition-all cursor-pointer ${
                    isActive ? 'bg-blue-600/25 text-blue-400 font-semibold border border-blue-500/30' : 'text-gray-400 hover:text-gray-200 hover:bg-[#151C33]'
                  }`}
                >
                  <Icon size={14} className={isActive ? 'text-blue-400' : 'text-gray-400'} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Status Overlay Footer */}
        <div className="bg-[#151C33] border border-[#1E294B] rounded-xl p-3 space-y-1.5 shadow-md">
          <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest flex items-center space-x-1.5">
            <Lock size={10} />
            <span>Regime Authority</span>
          </div>
          <div className="flex justify-between items-center text-[10px] font-semibold text-gray-300">
            <span>Jurisdiction:</span>
            <span className="text-emerald-400 font-bold uppercase">{activeJurisdiction}</span>
          </div>
          <div className="text-[9px] text-gray-500 space-y-0.5 font-mono leading-relaxed border-t border-[#1E294B] pt-1.5">
            <div>Statute: {jurConfig.primary_statute}</div>
            <div>Logic Base: {activeJurisdiction}_rules.json</div>
            <div>Vector Store: SQLite RAG</div>
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#090C15]">
        
        {/* Sub-header status bar */}
        <div className="h-14 border-b border-[#1E294B] bg-[#0E1325] px-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h2 className="text-sm font-extrabold uppercase tracking-wider text-white">
              {adminTab.replace('_', ' ')}
            </h2>
            <div className="h-4 w-px bg-[#1E294B]" />
            <div className="flex items-center space-x-2 text-[11px] text-gray-400">
              <span>Primary Engine Status:</span>
              <span className="bg-emerald-500/20 text-emerald-400 font-bold px-1.5 py-0.5 rounded uppercase text-[10px]">
                Online
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="text-gray-400 font-mono text-[11px]">SLA Monitor: 100% active</span>
          </div>
        </div>

        {/* Dashboard Workspace Router */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">

          {/* TAB 1: EXECUTIVE DASHBOARD */}
          {adminTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* Executive summary cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#0E1325] border border-[#1E294B] p-4.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Active Loops</span>
                  <div className="flex items-center space-x-2">
                    <Sparkles size={16} className="text-blue-400 animate-pulse" />
                    <span className="text-xl font-extrabold text-white">1 Continuous Loop</span>
                  </div>
                  <p className="text-[9px] text-gray-500">Autonomous self-adaptation tracking trigger feeds.</p>
                </div>

                <div className="bg-[#0E1325] border border-[#1E294B] p-4.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">RAG Retrieval Confidence</span>
                  <div className="flex items-center space-x-2">
                    <BookOpen size={16} className="text-emerald-400" />
                    <span className="text-xl font-extrabold text-white">96.8% Score</span>
                  </div>
                  <p className="text-[9px] text-gray-500">Average vector matching embedding confidence score.</p>
                </div>

                <div className="bg-[#0E1325] border border-[#1E294B] p-4.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">HITL Governance Queue</span>
                  <div className="flex items-center space-x-2">
                    <ShieldAlert size={16} className="text-rose-400" />
                    <span className="text-xl font-extrabold text-white">3 Pending Decisions</span>
                  </div>
                  <p className="text-[9px] text-gray-500">Gaps pending privacy officer review & approvals.</p>
                </div>

                <div className="bg-[#0E1325] border border-[#1E294B] p-4.5 rounded-xl space-y-1.5">
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Canary Deployments</span>
                  <div className="flex items-center space-x-2">
                    <Layers size={16} className="text-purple-400" />
                    <span className="text-xl font-extrabold text-white">v2.8.4-rel (Active)</span>
                  </div>
                  <p className="text-[9px] text-gray-500">FastAPI hot swap build pipeline running on VPS.</p>
                </div>
              </div>

              {/* Real-time active regimes overview */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Active jurisdictions stats */}
                <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
                    <Shield size={14} className="text-blue-500" />
                    <span>Authorized Client Organization Profiles</span>
                  </h3>
                  <div className="space-y-3">
                    {clients.map((c, idx) => (
                      <div key={idx} className="p-3 bg-[#151C33] border border-[#1E294B] rounded-lg flex justify-between items-center text-xs">
                        <div className="space-y-1">
                          <div className="font-bold text-white">{c.name} ({c.organization})</div>
                          <div className="text-[10px] text-gray-400">Coverage: {c.coverage.join(', ')}</div>
                        </div>
                        <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">{c.role}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notifications log */}
                <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300 flex items-center space-x-2">
                    <Terminal size={14} className="text-blue-500" />
                    <span>Active System Alerts & Ingestion Warnings</span>
                  </h3>
                  <div className="space-y-2.5">
                    {notifications.map(n => (
                      <div key={n.id} className={`p-3 rounded-lg border text-xs flex justify-between gap-3 ${
                        n.type === 'critical' ? 'bg-rose-500/10 border-rose-500/30 text-rose-300' :
                        n.type === 'warning' ? 'bg-amber-500/10 border-amber-500/30 text-amber-300' :
                        'bg-blue-500/10 border-blue-500/30 text-blue-300'
                      }`}>
                        <span>{n.msg}</span>
                        <span className="text-[10px] text-gray-500 whitespace-nowrap">{n.time}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: IMPROVEMENT ENGINE SIMULATOR */}
          {adminTab === 'engine' && (
            <div className="bg-[#0E1325] border border-[#1E294B] p-6 rounded-xl space-y-6">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Trigger Loop Injection Control</h3>
                <p className="text-xs text-gray-400 mt-1">Simulate legal triggers to trace the continuous improvement cycle.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-semibold uppercase">Trigger Type</label>
                    <select className="w-full bg-[#151C33] border border-[#1E294B] rounded-lg px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500 cursor-pointer">
                      <option value="Regulatory_Update">Regulatory Update (Quebec Law 25 compliance rules)</option>
                      <option value="User_Friction">User Friction (CMP telemetry report)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-semibold uppercase">Ingested Context data</label>
                    <textarea 
                      rows={3} 
                      className="w-full bg-[#151C33] border border-[#1E294B] rounded-lg p-3.5 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                      defaultValue="Ingest Law 25 compliance parameters for client marketing campaigns."
                    />
                  </div>

                  <button
                    onClick={handleSimulateCycle}
                    disabled={simIsRunning}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs px-4 py-2.5 rounded-lg flex items-center space-x-2 transition-all cursor-pointer shadow-md disabled:opacity-50"
                  >
                    <Play size={13} />
                    <span>{simIsRunning ? 'Cycle Running...' : 'Inject Trigger Event'}</span>
                  </button>
                </div>

                <div className="bg-[#090C15] border border-[#1E294B] rounded-xl p-4 flex flex-col h-64 overflow-hidden">
                  <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2 border-b border-[#1E294B] pb-1.5">Live Agent Logs</div>
                  <div className="flex-1 overflow-y-auto space-y-1.5 font-mono text-[11px] text-gray-300">
                    {simLogs.map((log, idx) => (
                      <div key={idx} className="leading-relaxed border-l-2 border-blue-500/40 pl-2">{log}</div>
                    ))}
                    {simLogs.length === 0 && <div className="text-gray-600 italic">Logs will appear here once trigger is injected...</div>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: LANGGRAPH FLOW DIAGRAM */}
          {adminTab === 'langgraph' && (
            <div className="space-y-6">
              
              {/* Interactive SVG Flow Diagram */}
              <div className="bg-[#0E1325] border border-[#1E294B] p-6 rounded-xl space-y-6">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-white">LangGraph Runtime Schema</h3>
                  <p className="text-xs text-gray-400 mt-1">Select a node to inspect state inputs, outputs, and agent prompts.</p>
                </div>

                <div className="relative py-12 flex flex-col md:flex-row items-center justify-between gap-6 overflow-x-auto min-w-[700px] border border-[#1E294B]/50 rounded-xl bg-[#090C15]/50 px-8">
                  
                  {nodes.map((node, index) => {
                    const isSelected = selectedNode === node.id;
                    return (
                      <React.Fragment key={node.id}>
                        <button
                          onClick={() => setSelectedNode(node.id)}
                          className={`w-44 p-4 rounded-xl border transition-all text-left space-y-2 shadow-lg cursor-pointer ${
                            isSelected ? 'bg-blue-600/20 border-blue-500 ring-2 ring-blue-500/40 scale-105' : 'bg-[#0E1325] border-[#1E294B] hover:border-gray-550'
                          }`}
                        >
                          <div className="flex justify-between items-center text-[10px] font-bold uppercase tracking-widest text-gray-400">
                            <span>Node #{index + 1}</span>
                            <span className={`w-1.5 h-1.5 rounded-full ${node.status === 'running' ? 'bg-amber-400 animate-pulse' : 'bg-emerald-500'}`} />
                          </div>
                          <h4 className="text-xs font-extrabold text-white leading-tight">{node.label}</h4>
                          <div className="text-[9px] text-gray-500 space-y-0.5 font-mono">
                            <div>Agent: {node.agent}</div>
                            <div>LLM: {node.llm}</div>
                          </div>
                        </button>

                        {index < nodes.length - 1 && (
                          <div className="flex items-center text-gray-600">
                            <ArrowRight size={18} className="animate-pulse text-blue-500/40" />
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                  
                </div>

                {/* Selected Node Inspector */}
                {selectedNode ? (
                  <div className="bg-[#151C33] border border-[#1E294B] p-5 rounded-xl space-y-3.5 text-xs">
                    <div className="flex justify-between items-center border-b border-[#1E294B] pb-2">
                      <h4 className="font-extrabold text-blue-400 uppercase tracking-wider">Node: {selectedNode.toUpperCase()} Details</h4>
                      <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-gray-250 cursor-pointer"><X size={14} /></button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div><span className="text-gray-400 font-semibold">Input Payload:</span> <code className="bg-[#090C15] px-1.5 py-0.5 rounded font-mono text-gray-300">{nodeStates[selectedNode].input}</code></div>
                        <div><span className="text-gray-400 font-semibold">Output Result:</span> <code className="bg-[#090C15] px-1.5 py-0.5 rounded font-mono text-gray-300">{nodeStates[selectedNode].output}</code></div>
                        <div><span className="text-gray-400 font-semibold">Reasoning Summary:</span> <p className="text-gray-300 mt-1 italic">"{nodeStates[selectedNode].reasoning}"</p></div>
                      </div>
                      <div className="space-y-2">
                        <div><span className="text-gray-400 font-semibold">Active Agent Messages:</span>
                          <ul className="list-disc pl-4 text-gray-300 mt-1 space-y-1">
                            {nodeStates[selectedNode].messages.map((m, i) => <li key={i}>{m}</li>)}
                          </ul>
                        </div>
                        <div><span className="text-gray-400 font-semibold">Retrieved Citations Context:</span> <span className="bg-[#090C15] text-amber-400 px-1.5 py-0.5 rounded font-mono text-[10px] block mt-1">{nodeStates[selectedNode].context}</span></div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 bg-[#090C15]/30 border border-dashed border-[#1E294B] rounded-xl text-xs text-gray-500 italic">
                    Click any node in the pipeline above to inspect active LLM parameters, cost chain-of-custody, and messages.
                  </div>
                )}
              </div>

            </div>
          )}

          {/* TAB 4: STATE INSPECTOR */}
          {adminTab === 'rag' && (
            <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Active RAG Grounding Library</h3>
                <span className="text-[10px] text-gray-400 font-mono">SQLite: legal_ground_truth</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {legalLibrary.map(clause => (
                  <div key={clause.clause_id} className="bg-[#151C33] border border-[#1E294B] p-4 rounded-xl space-y-2 text-xs">
                    <div className="flex justify-between font-bold text-[10px]">
                      <span className="text-blue-400 font-mono">{clause.clause_id}</span>
                      <span className="uppercase text-gray-400 font-mono">{clause.legislation.replace('_', ' ')}</span>
                    </div>
                    <p className="text-[11px] text-gray-300 leading-relaxed italic">"{clause.clause_text}"</p>
                    <div className="text-[9px] text-gray-500">
                      Keywords: <code className="bg-[#090C15] px-1 py-0.5 rounded border border-[#1E294B]">{clause.keywords}</code>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: AUTHORITATIVE SOURCE VIEWER */}
          {adminTab === 'source_viewer' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Authoritative Source Diff Comparator</h3>
                <button
                  onClick={() => setDiffMode(!diffMode)}
                  className="bg-[#151C33] hover:bg-[#1E294B] text-gray-300 px-3 py-1.5 rounded-lg border border-[#1E294B] text-xs font-bold cursor-pointer transition-all"
                >
                  {diffMode ? 'Visual Comparison' : 'Strict Code Diff'}
                </button>
              </div>

              {diffMode ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-3">
                    <div className="text-[10px] font-bold text-red-400 uppercase tracking-widest">Active Legacy Logic (Pre-Adaptation)</div>
                    <pre className="font-mono text-xs text-gray-300 bg-[#090C15] p-4 rounded-lg overflow-x-auto leading-relaxed">
{`def validate_consent(payload):
    # Standard compliance check
    if not payload.get("consent"):
        return False
    return True`}
                    </pre>
                  </div>

                  <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-3">
                    <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">AI Proposed Adaptation (Grounded in LAW25-SEC14)</div>
                    <pre className="font-mono text-xs text-gray-300 bg-[#090C15] p-4 rounded-lg overflow-x-auto leading-relaxed">
{`def validate_consent(payload):
    # Quebec Law 25 consent parameters
    if not payload.get("consent_bilingual"):
        log_warning("Bilingual consent missing")
        return False
    return True`}
                    </pre>
                  </div>
                </div>
              ) : (
                <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-3">
                  <div className="text-[10px] font-bold text-gray-405 uppercase tracking-widest">Visual Diff</div>
                  <div className="font-mono text-xs text-gray-300 bg-[#090C15] p-4 rounded-lg space-y-1.5">
                    <div className="text-gray-500">  def validate_consent(payload):</div>
                    <div className="text-red-400 bg-red-500/10 px-2 py-0.5 rounded">-     if not payload.get("consent"):</div>
                    <div className="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">+     # Quebec Law 25 consent parameters</div>
                    <div className="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">+     if not payload.get("consent_bilingual"):</div>
                    <div className="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">+         log_warning("Bilingual consent missing")</div>
                    <div className="text-gray-500">          return False</div>
                    <div className="text-gray-500">      return True</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 6: TRUST TIERS */}
          {adminTab === 'trust_tiers' && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { tier: 'Tier 1', title: 'Binding Laws', items: ['GDPR', 'PIPEDA', 'Quebec Law 25', 'PHIPA', 'CCPA/CPRA'], desc: 'Statutory texts enforced by regulatory offices.' },
                { tier: 'Tier 2', title: 'Regulatory Guidance', items: ['EDPB Guidelines', 'OPC Advisories', 'CNIL Recommendations'], desc: 'Official interpretations of the binding statutes.' },
                { tier: 'Tier 3', title: 'Internal Policies', items: ['Company Data Standards', 'DPIA Templates', 'Retention Calendars'], desc: 'Internal corporate structures and baseline profiles.' },
                { tier: 'Tier 4', title: 'External Knowledge', items: ['Privacy Research', 'Legal Blogs', 'Technical Whitepapers'], desc: 'Auxiliary evidence used for context parsing.' }
              ].map(t => (
                <div key={t.tier} className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-3.5">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest font-mono">{t.tier}</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  </div>
                  <h4 className="text-xs font-extrabold text-white uppercase tracking-wider">{t.title}</h4>
                  <p className="text-[11px] text-gray-400 leading-relaxed">{t.desc}</p>
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {t.items.map(item => (
                      <span key={item} className="bg-[#151C33] border border-[#1E294B] text-gray-300 text-[9px] px-2 py-0.5 rounded font-medium">{item}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 7: HITL APPROVAL CENTER */}
          {adminTab === 'hitl' && (
            <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Human-in-the-Loop Approval Queue</h3>
                <p className="text-xs text-gray-400 mt-1">Review, approve, or escalate autonomous improvements suggested by Kibo.</p>
              </div>

              <div className="space-y-3">
                {[
                  { id: 'QA-201', trigger: 'Trigger Ingestion - Law 25', score: '8.4', impact: 'High Risk', change: 'Enable automated bilingual consent templates for Quebec campaigns (LAW25-SEC14).' },
                  { id: 'QA-202', trigger: 'User Friction - Vendor Form', score: '9.0', impact: 'Low Risk', change: 'Simplify vendor onboarding profile validations (GDPR-ART28).' }
                ].map(item => (
                  <div key={item.id} className="p-4 bg-[#151C33] border border-[#1E294B] rounded-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 text-xs">
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white">{item.id}</span>
                        <span className="text-[10px] text-gray-500">Source: {item.trigger}</span>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${item.impact.includes('High') ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>{item.impact}</span>
                      </div>
                      <p className="text-gray-300 leading-relaxed italic">"{item.change}"</p>
                      <div className="text-[10px] text-gray-400 font-semibold">Evaluation Score: <span className="text-blue-400">{item.score}/10</span></div>
                    </div>
                    <div className="flex space-x-2">
                      <button className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[10px] px-3 py-1.5 rounded-lg cursor-pointer transition-all shadow-md">Approve</button>
                      <button className="bg-rose-600 hover:bg-rose-700 text-white font-bold text-[10px] px-3 py-1.5 rounded-lg cursor-pointer transition-all shadow-md">Reject</button>
                      <button className="bg-[#0E1325] hover:bg-[#1E294B] text-gray-400 px-3 py-1.5 rounded-lg border border-[#1E294B] text-[10px] font-bold cursor-pointer transition-all">Escalate</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 8: DEPLOYMENT CENTER */}
          {adminTab === 'deployment' && (
            <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Canary Deployment Queue & VPS Status</h3>
                <p className="text-xs text-gray-400 mt-1">Tracks hot reload builds deployed to the live environment.</p>
              </div>

              <div className="space-y-3">
                {deployments.map(d => (
                  <div key={d.version} className="p-4 bg-[#151C33] border border-[#1E294B] rounded-xl flex justify-between items-center text-xs">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white">{d.version}</span>
                        <span className="bg-blue-500/10 text-blue-400 font-mono text-[9px] px-1.5 py-0.5 rounded border border-blue-500/20 uppercase">{d.environment}</span>
                      </div>
                      <div className="text-[10px] text-gray-400">Proposed by: {d.proposed_by} | Approved by: {d.approved_by}</div>
                    </div>
                    <div className="text-right space-y-1">
                      <span className="text-[10px] text-gray-450 block font-mono">{d.timestamp}</span>
                      <span className="text-[9px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Active</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 9: TELEMETRY VIEW */}
          {adminTab === 'telemetry' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-2">
                <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Completion Rate</span>
                <div className="text-2xl font-extrabold text-emerald-400">92.4%</div>
                <p className="text-[10px] text-gray-500 leading-relaxed">Percentage of privacy workflows completed successfully by users.</p>
              </div>

              <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-2">
                <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Time on Task</span>
                <div className="text-2xl font-extrabold text-blue-400">1m 14s</div>
                <p className="text-[10px] text-gray-500 leading-relaxed">Average completion time for user data subject access requests (DSARs).</p>
              </div>

              <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-2">
                <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Drop-off Rate</span>
                <div className="text-2xl font-extrabold text-rose-400">7.6%</div>
                <p className="text-[10px] text-gray-500 leading-relaxed">Friction percentage of users leaving onboarding verification flows.</p>
              </div>
            </div>
          )}

          {/* TAB 10: AI AGENT MONITOR */}
          {adminTab === 'agents' && (
            <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl overflow-hidden shadow-md">
              <div className="p-4 border-b border-[#1E294B]">
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">Active Autonomous AI Agents</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-[#151C33] border-b border-[#1E294B] text-gray-400 uppercase text-[9px] tracking-wider">
                      <th className="p-3">Agent Name</th>
                      <th className="p-3">Version</th>
                      <th className="p-3">Status</th>
                      <th className="p-3 font-mono">Queue</th>
                      <th className="p-3">Runtime</th>
                      <th className="p-3">LLM Cost</th>
                      <th className="p-3">Success %</th>
                      <th className="p-3 font-mono">Memory</th>
                      <th className="p-3 font-mono">CPU</th>
                      <th className="p-3 font-mono">Tokens</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1E294B] text-gray-300">
                    {agents.map((a, idx) => (
                      <tr key={idx} className="hover:bg-[#151C33]/50">
                        <td className="p-3 font-bold text-white">{a.name}</td>
                        <td className="p-3 font-mono text-[10px] text-gray-450">{a.version}</td>
                        <td className="p-3">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                            a.status === 'processing' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' :
                            a.status === 'waiting' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' :
                            'bg-gray-500/10 text-gray-400 border border-gray-500/20'
                          }`}>{a.status}</span>
                        </td>
                        <td className="p-3 font-mono">{a.queue}</td>
                        <td className="p-3 font-mono">{a.runtime}</td>
                        <td className="p-3 font-mono text-emerald-400">{a.cost}</td>
                        <td className="p-3 font-mono text-emerald-400">{a.success}</td>
                        <td className="p-3 font-mono">{a.memory}</td>
                        <td className="p-3 font-mono">{a.cpu}</td>
                        <td className="p-3 font-mono">{a.tokens}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 11: AUDIT TRAIL TIMELINE */}
          {adminTab === 'audits' && (
            <div className="bg-[#0E1325] border border-[#1E294B] p-5 rounded-xl space-y-4">
              <div className="flex justify-between items-center border-b border-[#1E294B] pb-3">
                <div className="flex items-center space-x-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-white">Immutable Ledger Audit Timeline</h3>
                  <div className="flex bg-[#090C15] border border-[#1E294B] p-0.5 rounded-lg text-[10px]">
                    {['all', 'success', 'approved', 'rejected'].map(filter => (
                      <button
                        key={filter}
                        onClick={() => setSelectedAuditFilter(filter)}
                        className={`px-2.5 py-1 rounded-md uppercase font-bold cursor-pointer transition-all ${
                          selectedAuditFilter === filter ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                        }`}
                      >
                        {filter}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => downloadAudits('csv')}
                    className="bg-[#151C33] hover:bg-[#1E294B] border border-[#1E294B] text-gray-300 font-bold text-[10px] px-3 py-1.5 rounded-lg flex items-center space-x-1.5 cursor-pointer shadow-xs"
                  >
                    <Download size={11} />
                    <span>CSV</span>
                  </button>
                  <button
                    onClick={() => downloadAudits('json')}
                    className="bg-[#151C33] hover:bg-[#1E294B] border border-[#1E294B] text-gray-300 font-bold text-[10px] px-3 py-1.5 rounded-lg flex items-center space-x-1.5 cursor-pointer shadow-xs"
                  >
                    <Download size={11} />
                    <span>JSON</span>
                  </button>
                </div>
              </div>

              <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#1E294B]">
                {audits
                  .filter(a => selectedAuditFilter === 'all' || a.status === selectedAuditFilter)
                  .map((a, idx) => (
                    <div key={idx} className="relative pl-8 text-xs space-y-1">
                      <div className="absolute left-1.5 top-1.5 w-3.5 h-3.5 rounded-full bg-[#0E1325] border-2 border-blue-500 flex items-center justify-center">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                      </div>
                      <div className="flex justify-between items-center text-gray-400">
                        <span className="font-semibold text-[10px]">{a.timestamp}</span>
                        <code className="text-[9px] text-gray-500 font-mono">{a.hash}</code>
                      </div>
                      <div className="text-white font-bold leading-snug">{a.action}</div>
                      <div className="text-[10px] text-gray-500">
                        Triggered by: {a.user} | Agent: {a.agent} | LLM Model: <span className="text-blue-400">{a.llm}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
