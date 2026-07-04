import React, { useState, useEffect, useMemo } from 'react';
import {
  Activity, Server, Database, Sparkles, AlertTriangle, Layers,
  Terminal, ShieldAlert, Cpu, BookOpen, Clock, Play, FileText, Check, CheckSquare,
  Square, Edit, Save, List, UserCheck, Shield, ChevronRight, X, ArrowRight, GitBranch,
  FileCode, CheckCircle, AlertOctagon, HelpCircle, HardDrive, RefreshCw, BarChart2,
  Lock, RefreshCcw, Download, Info, Search, Filter, Users, Globe, Trash2, ArrowLeftRight
} from 'lucide-react';
import { PRIVACY_GUIDE_DATA } from './privacy_guide_data';
import UserGovernanceCockpit from './UserGovernanceCockpit';
import ComplianceCoverageMap from './ComplianceCoverageMap';

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
  const [selectedNode, setSelectedNode] = useState('analysis');
  const [activeCycleStep, setActiveCycleStep] = useState(null);
  const [diffMode, setDiffMode] = useState(false);
  
  // Custom states for completed dashboards
  const [selectedAgent, setSelectedAgent] = useState(null); // For AI Agent Monitor Lifecycle drawer
  const [selectedRAGDomain, setSelectedRAGDomain] = useState('laws');
  const [ragSearchQuery, setRagSearchQuery] = useState('');
  const [selectedAuditFilter, setSelectedAuditFilter] = useState('all');
  const [auditSearch, setAuditSearch] = useState('');
  const [auditClientFilter, setAuditClientFilter] = useState('all');
  const [simReasoning, setSimReasoning] = useState([]);
  
  // HITL state
  const [hitlDecisionLog, setHitlDecisionLog] = useState({});
  const [hitlNote, setHitlNote] = useState('');
  
  // Telemetry window
  const [telemetryWindow, setTelemetryWindow] = useState('30d');
  const [telemetryClient, setTelemetryClient] = useState('all');

  const [notifications, setNotifications] = useState([
    { id: 1, type: 'critical', msg: 'Missing Legal Ground Truth Citation for new Cookie Regulation trigger.', time: '2 mins ago', status: 'active' },
    { id: 2, type: 'info', msg: 'LangGraph loop auto-adaptation evaluated with Score: 9/10.', time: '10 mins ago', status: 'active' },
    { id: 3, type: 'warning', msg: 'Model confidence score dropped below 85% on CPRA logic formulation.', time: '1 hour ago', status: 'active' }
  ]);

  const [triggers, setTriggers] = useState([
    { id: 'TR-101', timestamp: '2026-07-03 01:10', priority: 'high', source: 'EDPB Feed', framework: 'GDPR', jurisdiction: 'European Union', client: 'Kids Help Phone', confidence: '94%', impact: 'High', status: 'Triaged' },
    { id: 'TR-102', timestamp: '2026-07-03 01:12', priority: 'medium', source: 'CMP Telemetry', framework: 'Law 25', jurisdiction: 'Quebec, CA', client: 'KHP Foundation', confidence: '88%', impact: 'Medium', status: 'Pending Review' },
    { id: 'TR-103', timestamp: '2026-07-02 23:45', priority: 'critical', source: 'Privacy Officer Ticket', framework: 'PHIPA', jurisdiction: 'Ontario, CA', client: 'Clinical Portal', confidence: '99%', impact: 'High', status: 'Investigating' },
    { id: 'TR-104', timestamp: '2026-07-02 22:15', priority: 'low', source: 'ISO Auditer', framework: 'ISO 27701', jurisdiction: 'Global', client: 'All', confidence: '95%', impact: 'Low', status: 'Completed' }
  ]);

  const [agents, setAgents] = useState([
    { name: 'Ingestion Agent', version: 'v2.1.4', status: 'idle', queue: 0, runtime: '1.2s', cost: '$0.004', success: '99.8%', failure: '0.2%', memory: '124MB', cpu: '4%', tokens: '1.5k', stage: 'active' },
    { name: 'Adaptation Coder', version: 'v3.0.2', status: 'processing', queue: 1, runtime: '4.8s', cost: '$0.015', success: '97.2%', failure: '2.8%', memory: '512MB', cpu: '68%', tokens: '8.4k', stage: 'active' },
    { name: 'Self-Critique Auditor', version: 'v2.2.0', status: 'idle', queue: 0, runtime: '2.5s', cost: '$0.008', success: '98.5%', failure: '1.5%', memory: '256MB', cpu: '12%', tokens: '3.2k', stage: 'active' },
    { name: 'Deployment Controller', version: 'v1.8.1', status: 'waiting', queue: 2, runtime: '0.8s', cost: '$0.002', success: '99.9%', failure: '0.1%', memory: '96MB', cpu: '2%', tokens: '500', stage: 'active' }
  ]);

  const [deployments, setDeployments] = useState([
    { version: 'v2.8.4-rel', environment: 'production', status: 'active', proposed_by: 'Adaptation Coder', approved_by: 'CPO (HITL)', timestamp: '2026-07-03 01:16', commit: '89a0fcdb', health: 'Healthy', rollbackAvailable: true },
    { version: 'v2.8.3-rel', environment: 'production', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'System Admin', timestamp: '2026-07-03 00:05', commit: 'f45bdcca', health: 'Healthy', rollbackAvailable: true },
    { version: 'v2.8.4-rc1', environment: 'staging', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'Automatic (Score > 8)', timestamp: '2026-07-02 23:45', commit: 'c90cdbea', health: 'Healthy', rollbackAvailable: false }
  ]);

  const [audits, setAudits] = useState([
    {
      audit_id: 'AUDIT-2026-07-03-8892',
      timestamp: '2026-07-03 01:16 UTC',
      target_domain: 'GDPR',
      authoritative_source: 'EDPB Guidelines 03/2022 on Dark Patterns',
      citation_id: 'Section 3.1 - Obstructive UI',
      retrieval_hash: 'SHA256:d9b2089f21f1e29ad30e8c0901e9dbe88812c983ea0e932cdbe90cfdbea08a0e',
      kibo_rationale: "Current cookie banner utilizes a 'confirm-all' color scheme that violates EDPB accessibility standards.",
      decision_status: 'MANUAL_APPROVAL_REQUIRED',
      admin_user_id: 'Waël Hassan',
      approval_status: 'APPROVED',
      human_notes: 'Design team override color thresholds to pass AA contrast check.',
      deployment_version: 'UI Schema v4.2.1',
      pre_baseline: 'Average consent verification drop-off: 18.5%',
      post_verification: 'Completion rate improved by 12%',
      risk_category: 'Medium (UI/UX Compliance)',
      status: 'approved'
    },
    {
      audit_id: 'AUDIT-2026-07-03-8893',
      timestamp: '2026-07-03 01:12 UTC',
      target_domain: 'Law 25',
      authoritative_source: 'Quebec Law 25 (Act to modernize legislative provisions)',
      citation_id: 'Section 14 - Consent Campaigns',
      retrieval_hash: 'SHA256:b8c983ea9012a938be9cd828ff7208da01e2c983ea0e932cdbe90cfdbea08a0d',
      kibo_rationale: 'Quebec Law 25 enforces strict bilingual campaign consent parameters.',
      decision_status: 'AUTOMATIC_APPROVAL_SUCCESS',
      admin_user_id: 'System Agent',
      approval_status: 'APPROVED',
      human_notes: 'Fully auto-validated via RAG checks (Score: 9/10).',
      deployment_version: 'API Schema v2.8.4',
      pre_baseline: 'Manual consent validation delay: 4 hours',
      post_verification: 'Automated validation executed in 150ms',
      risk_category: 'Low (Code Automation)',
      status: 'success'
    }
  ]);

  const [clients, setClients] = useState([
    { name: 'Kids Help Phone', organization: 'KHP Canada', role: 'Data Controller', coverage: ['PIPEDA', 'Quebec Law 25', 'PHIPA'], users: 24, status: 'active' },
    { name: 'KHP Foundation', organization: 'KHP Foundation', role: 'Joint Controller', coverage: ['PIPEDA', 'CASL'], users: 8, status: 'active' },
    { name: 'Crisis Support Portal', organization: 'Clinical Services', role: 'Processor', coverage: ['PHIPA', 'CYFSA'], users: 12, status: 'active' }
  ]);

  const nodeStates = {
    trigger: { input: 'Regulatory Feed Event / Webhook', output: 'Trigger Data Object', messages: ['Ingesting Law 25 compliance rules updates.'], context: 'PIPEDA & Law 25 parameters loaded.', reasoning: 'Parsed Law 25 changes to target campaign templates.', cost: '$0.002', tokens: '1.2k', duration: '240ms', prompt: 'v1.4' },
    analysis: { input: 'Raw statutory triggers', output: 'Ingested compliance variables', messages: ['Matched keywords: bilingual, Quebec.'], context: 'LAW25-SEC14 (Quebec Law 25)', reasoning: 'Grounded trigger inside legal library.', cost: '$0.008', tokens: '3.5k', duration: '1.2s', prompt: 'v2.1' },
    adaptation: { input: 'Ingested context + rulesets', output: 'Proposed compliance logic code', messages: ['Inject strict Quebec Law 25 consent parameters.'], context: 'GDPR-ART28, PIPEDA.', reasoning: 'Formulated logic templates for review.', cost: '$0.024', tokens: '8.4k', duration: '4.5s', prompt: 'v3.2' },
    evaluation: { input: 'Adaptation proposal code', output: 'Critique Audit Report', messages: ['Grounded verification checks passed.'], context: 'RAG verification model.', reasoning: 'Grounded safety checks evaluated. Score: 9/10.', cost: '$0.012', tokens: '4.1k', duration: '2.3s', prompt: 'v2.2' },
    deploy: { input: 'Approved schema', output: 'Applied production configuration', messages: ['Vite production assets updated.'], context: 'VPS root directory.', reasoning: 'Triggered canary build and uvicorn hot reload.', cost: '$0.000', tokens: '0', duration: '50ms', prompt: 'N/A' }
  };

  // SSE Stream Simulation
  const handleSimulateCycle = () => {
    setSimIsRunning(true);
    setActiveCycleStep('trigger');
    setSimLogs(['[Agent Gateway] Ingesting dynamic client regulatory update...']);
    setSimReasoning(['[Ingestion] Event parsed successfully. Mapped to Law 25 framework.']);
    
    setTimeout(() => {
      setActiveCycleStep('analysis');
      setSimLogs(prev => [...prev, '[RAG Engine] Successfully retrieved 1 grounded clauses: LAW25-SEC14', '[Analysis Node] Ingestion metadata mapped.']);
      setSimReasoning(prev => [...prev, '[RAG] Found matching clause: Section 14 (Consent rules for bilingual campaigns).']);
    }, 1000);

    setTimeout(() => {
      setActiveCycleStep('adaptation');
      setSimLogs(prev => [...prev, '[Adaptation Node] Proposed compliance logic formulated.']);
      setSimReasoning(prev => [...prev, '[Adaptation] Generated python validator diff targeting bilingual_opt_in.']);
    }, 2000);

    setTimeout(() => {
      setActiveCycleStep('evaluation');
      setSimLogs(prev => [...prev, '[Evaluation Node] Verification critique complete. Score: 9/10 (APPROVED)']);
      setSimReasoning(prev => [...prev, '[Critique] Algorithmic compliance audit completed. Risk level: low. Approved.']);
    }, 3000);

    setTimeout(() => {
      setActiveCycleStep('deploy');
      setSimLogs(prev => [...prev, '[Deployment Controller] Live production deployment hot swap finished.']);
      setSimReasoning(prev => [...prev, '[Deployment] Vite static pages updated. API schema hot-swapped.']);
      setSimIsRunning(false);
    }, 4000);
  };

  const handleAcknowledgeAlert = (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, status: 'acknowledged' } : n));
  };

  const handleRollback = (version) => {
    if (confirm(`Are you sure you want to rollback to ${version}? This requires dual system authority.`)) {
      alert(`Rollback initiated. Hot reloading build and restoring commits. KIBO is reverting to ${version}.`);
      setDeployments(prev => prev.map(d => d.version === version ? { ...d, status: 'active' } : { ...d, status: 'completed' }));
    }
  };

  const handleToggleAgent = async (agentName) => {
    const action = selectedAgent?.status === 'idle' ? 'pause' : 'restart';
    try {
      const res = await fetch(`${API_BASE}/api/agents/${agentName}/${action}`, { method: 'POST' });
      if (res.ok) {
        setAgents(prev => prev.map(a => a.name === agentName ? { ...a, status: action === 'pause' ? 'waiting' : 'idle' } : a));
        alert(`Agent ${agentName} status updated to ${action === 'pause' ? 'paused' : 'active'}.`);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Filtered RAG Documents
  const filteredRAGDocs = useMemo(() => {
    const allItems = PRIVACY_GUIDE_DATA.sections.find(s => s.id === selectedRAGDomain)?.items || [];
    return allItems.filter(doc => 
      doc.name.toLowerCase().includes(ragSearchQuery.toLowerCase()) || 
      doc.scope.toLowerCase().includes(ragSearchQuery.toLowerCase())
    );
  }, [selectedRAGDomain, ragSearchQuery]);

  // Filtered Audits
  const filteredAuditsList = useMemo(() => {
    return audits.filter(a => {
      const matchesSearch = a.audit_id.toLowerCase().includes(auditSearch.toLowerCase()) || 
                            a.authoritative_source.toLowerCase().includes(auditSearch.toLowerCase()) ||
                            a.target_domain.toLowerCase().includes(auditSearch.toLowerCase());
      const matchesStatus = selectedAuditFilter === 'all' || a.status === selectedAuditFilter;
      return matchesSearch && matchesStatus;
    });
  }, [audits, auditSearch, selectedAuditFilter]);

  return (
    <div className="flex-1 flex bg-[#FAFAFA] text-[#111827] overflow-hidden font-sans">
      
      {/* Sidebar Nav (Light Theme Mode) */}
      <div className="w-60 bg-white border-r border-[#E5E7EB] p-4 flex flex-col justify-between">
        <div className="space-y-6">
          <div className="flex items-center space-x-2.5 px-2">
            <div className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-wider text-gray-800">AI Ops Mission Control</span>
          </div>

          <nav className="space-y-1">
            {[
              { id: 'dashboard', label: 'Executive Dashboard', icon: Activity },
              { id: 'engine', label: 'Improvement Engine', icon: Sparkles },
              { id: 'langgraph', label: 'LangGraph Visualizer', icon: GitBranch },
              { id: 'orchestration', label: 'Governance Orchestration', icon: List },
              { id: 'rag', label: 'RAG Knowledge Base', icon: BookOpen },
              { id: 'source_viewer', label: 'Authoritative Sources', icon: FileCode },
              { id: 'trust_tiers', label: 'Trust Tiers', icon: Shield },
              { id: 'hitl', label: 'HITL Governance Queue', icon: UserCheck },
              { id: 'deployment', label: 'Deployment Center', icon: Layers },
              { id: 'telemetry', label: 'UX Telemetry Feedback', icon: BarChart2 },
              { id: 'agents', label: 'AI Agent Monitor', icon: Cpu },
              { id: 'audits', label: 'Audit History', icon: FileText },
              { id: 'user_governance', label: 'User Governance Cockpit', icon: Users },
              { id: 'compliance_map', label: 'Compliance Coverage Map', icon: Globe }
            ].map(tab => {
              const Icon = tab.icon;
              const isActive = adminTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setAdminTab(tab.id)}
                  className={`w-full flex items-center space-x-2.5 px-3 py-2 text-xs rounded-lg transition-all cursor-pointer ${
                    isActive ? 'bg-blue-50 text-blue-600 font-semibold border border-blue-200/50' : 'text-gray-650 hover:text-black hover:bg-gray-100'
                  }`}
                >
                  <Icon size={14} className={isActive ? 'text-blue-600' : 'text-gray-500'} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Status Overlay Footer (Light styling) */}
        <div className="bg-gray-50 border border-[#E5E7EB] rounded-xl p-3 space-y-1.5 shadow-xs">
          <div className="text-[10px] font-bold text-blue-600 uppercase tracking-widest flex items-center space-x-1.5">
            <Lock size={10} />
            <span>Regime Authority</span>
          </div>
          <div className="flex justify-between items-center text-[10px] font-semibold text-gray-700">
            <span>Jurisdiction:</span>
            <span className="text-emerald-600 font-bold uppercase">{activeJurisdiction}</span>
          </div>
          <div className="text-[9px] text-gray-500 space-y-0.5 font-mono leading-relaxed border-t border-[#E5E7EB] pt-1.5">
            <div>Statute: {jurConfig.primary_statute}</div>
            <div>Logic Base: {activeJurisdiction}_rules.json</div>
            <div>Vector Store: SQLite RAG</div>
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col overflow-hidden bg-[#FAFAFA]">
        
        {/* Sub-header status bar */}
        <div className="h-14 border-b border-[#E5E7EB] bg-white px-6 flex items-center justify-between shadow-xs">
          <div className="flex items-center space-x-4">
            <h2 className="text-sm font-extrabold uppercase tracking-wider text-gray-900">
              {adminTab.replace('_', ' ')}
            </h2>
            <div className="h-4 w-px bg-[#E5E7EB]" />
            <div className="flex items-center space-x-2 text-[11px] text-gray-500">
              <span>Primary Engine Status:</span>
              <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold px-2 py-0.5 rounded-full uppercase text-[9px]">
                Online
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="text-gray-500 font-mono text-[11px]">SLA Monitor: 100% active</span>
          </div>
        </div>

        {/* Dashboard Workspace Router */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6">

          {/* TAB 1: EXECUTIVE DASHBOARD */}
          {adminTab === 'dashboard' && (
            <div className="space-y-6">
              
              {/* Executive summary cards - Clicking tile drills to detail screen */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { label: 'Active Loops', value: '1 Continuous Loop', icon: Sparkles, desc: 'Autonomous self-adaptation tracking trigger feeds.', color: 'text-blue-600', tab: 'engine' },
                  { label: 'RAG Retrieval Confidence', value: '96.8% Score', icon: BookOpen, desc: 'Average vector matching embedding confidence score.', color: 'text-emerald-600', tab: 'rag' },
                  { label: 'HITL Governance Queue', value: '3 Pending Decisions', icon: ShieldAlert, desc: 'Gaps pending privacy officer review & approvals.', color: 'text-rose-600', tab: 'hitl' },
                  { label: 'Canary Deployments', value: 'v2.8.4-rel (Active)', icon: Layers, desc: 'FastAPI hot swap build pipeline running on VPS.', color: 'text-purple-600', tab: 'deployment' }
                ].map((tile, i) => {
                  const Icon = tile.icon;
                  return (
                    <div
                      key={i}
                      onClick={() => setAdminTab(tile.tab)}
                      className="bg-white border border-[#E5E7EB] hover:border-blue-400 p-4.5 rounded-xl space-y-1.5 cursor-pointer shadow-xs transition-all hover:shadow-sm"
                    >
                      <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">{tile.label}</span>
                      <div className="flex items-center space-x-2">
                        <Icon size={16} className={tile.color} />
                        <span className="text-xl font-extrabold text-gray-900">{tile.value}</span>
                      </div>
                      <p className="text-[9px] text-gray-400 leading-normal">{tile.desc}</p>
                    </div>
                  );
                })}
              </div>

              {/* 90-Day Trend Strip (Workflows started vs. completed) */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">90-Day Loop Adaptation Activity (Workflows Started vs Completed)</span>
                <div className="h-20 flex items-end space-x-1.5 pt-4">
                  {Array.from({ length: 30 }).map((_, i) => {
                    const started = Math.floor(Math.sin(i * 0.5) * 15) + 20;
                    const completed = started - Math.floor(Math.random() * 3);
                    return (
                      <div key={i} className="flex-1 flex flex-col justify-end h-full group relative">
                        <div className="w-full bg-blue-500 hover:bg-blue-600" style={{ height: `${started * 2}%` }} />
                        <div className="w-full bg-emerald-500 hover:bg-emerald-600 mt-0.5" style={{ height: `${completed * 1.5}%` }} />
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block z-20 bg-gray-900 text-white text-[8px] p-1.5 rounded shadow-lg whitespace-nowrap">
                          Day {i * 3}: {started} Started / {completed} Completed
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="flex justify-between text-[9px] text-gray-400 font-mono">
                  <span>90 Days Ago</span>
                  <span>Today</span>
                </div>
              </div>

              {/* Real-time active regimes overview */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Active jurisdictions stats */}
                <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                    <Shield size={14} className="text-blue-600" />
                    <span>Authorized Client Organization Profiles</span>
                  </h3>
                  <div className="space-y-3">
                    {clients.map((c, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 border border-[#E5E7EB] rounded-lg flex justify-between items-center text-xs">
                        <div className="space-y-1">
                          <div className="font-bold text-gray-900">{c.name} ({c.organization})</div>
                          <div className="text-[10px] text-gray-500">Coverage: {c.coverage.join(', ')}</div>
                        </div>
                        <span className="text-[9px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full">{c.role}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Notifications log with Acknowledge/Source buttons */}
                <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                    <Terminal size={14} className="text-blue-600" />
                    <span>Active System Alerts & Ingestion Warnings</span>
                  </h3>
                  <div className="space-y-2.5">
                    {notifications.filter(n => n.status === 'active').map(n => (
                      <div key={n.id} className={`p-3 rounded-lg border text-xs flex justify-between items-center gap-3 ${
                        n.type === 'critical' ? 'bg-rose-50 border-rose-200 text-rose-700' :
                        n.type === 'warning' ? 'bg-amber-50 border-amber-200 text-amber-700' :
                        'bg-blue-50 border-blue-200 text-blue-700'
                      }`}>
                        <div className="space-y-1">
                          <div>{n.msg}</div>
                          <span className="text-[9px] text-gray-400">{n.time}</span>
                        </div>
                        <div className="flex space-x-2 shrink-0">
                          <button
                            onClick={() => handleAcknowledgeAlert(n.id)}
                            className="bg-white hover:bg-gray-100 text-gray-700 text-[9px] font-bold px-2 py-1 rounded border border-gray-300 cursor-pointer"
                          >
                            Acknowledge
                          </button>
                          <button
                            onClick={() => setAdminTab('source_viewer')}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-[9px] font-bold px-2 py-1 rounded cursor-pointer"
                          >
                            Triage
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: IMPROVEMENT ENGINE SIMULATOR */}
          {adminTab === 'engine' && (
            <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-6 shadow-xs">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-900">Trigger Loop Ingestor & Simulator</h3>
                <p className="text-xs text-gray-400 mt-1">Preset libraries and simulator controls to test adaptive logic generation.</p>
              </div>

              {/* Preset triggers library */}
              <div className="space-y-2">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">One-Click Preset Trigger Library</span>
                <div className="flex flex-wrap gap-2">
                  {[
                    { title: "Quebec Law 25 Consent Update", context: "Ingest Quebec Law 25 Section 14 bilingual campaign requirements." },
                    { title: "SaaS Subprocessor Breach", context: "Twilio webhook warning: SMS database leakage in US-East segment." },
                    { title: "Advancement Telemetry Friction Spike", context: "Friction alert: 78% drop-off detected on user consent registration." }
                  ].map((preset, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        document.getElementById('triggerContextInput').value = preset.context;
                      }}
                      className="bg-gray-50 hover:bg-gray-100 border border-gray-300 text-gray-700 text-[10px] font-bold px-2.5 py-1.5 rounded-lg cursor-pointer transition-all"
                    >
                      {preset.title}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-semibold uppercase">Trigger Type</label>
                    <select className="w-full bg-white border border-gray-300 rounded-lg px-3.5 py-2.5 text-xs text-gray-800 focus:outline-none focus:border-blue-500 cursor-pointer">
                      <option value="Regulatory_Update">Regulatory Update (Quebec Law 25 compliance rules)</option>
                      <option value="User_Friction">User Friction (CMP telemetry report)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs text-gray-400 font-semibold uppercase">Ingested Context data</label>
                    <textarea 
                      id="triggerContextInput"
                      rows={3} 
                      className="w-full bg-white border border-gray-300 rounded-lg p-3.5 text-xs text-gray-800 focus:outline-none focus:border-blue-500 font-mono"
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

                <div className="bg-[#090C15] border border-gray-800 rounded-xl p-4 flex flex-col h-64 overflow-hidden shadow-inner">
                  <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2 border-b border-gray-800 pb-1.5">Live Agent Logs (Streaming)</div>
                  <div className="flex-1 overflow-y-auto space-y-1.5 font-mono text-[11px] text-emerald-400">
                    {simLogs.map((log, idx) => (
                      <div key={idx} className="leading-relaxed border-l-2 border-blue-500/40 pl-2">{log}</div>
                    ))}
                    {simLogs.length === 0 && <div className="text-gray-600 italic">Logs will appear here once trigger is injected...</div>}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: LANGGRAPH FLOW DIAGRAM (Branching Conditional Visualizer) */}
          {adminTab === 'langgraph' && (
            <div className="space-y-4 font-sans">
              
              <div className="text-center space-y-0.5 py-2">
                <h2 className="text-base font-black text-gray-900 tracking-widest uppercase">KIBO Self-Improvement Loop</h2>
                <p className="text-[10px] font-bold text-blue-600 tracking-[0.3em] uppercase">Interactive LangGraph Orchestrator</p>
              </div>

              <div className="flex gap-4">
                
                {/* LEFT: TRIGGERS */}
                <div className="w-44 shrink-0 bg-white border border-[#E5E7EB] rounded-xl p-3 space-y-3 shadow-xs">
                  <div className="text-[9px] font-extrabold text-gray-500 uppercase tracking-widest border-b border-[#E5E7EB] pb-2">Triggers (Inputs)</div>
                  {[
                    { icon: '🏛️', label: 'Regulatory Update', color: 'text-blue-600', detail: 'New statutory code or guidelines parsed.', id: 'regulatory' },
                    { icon: '📊', label: 'User Telemetry', color: 'text-purple-600', detail: 'Friction threshold breaches.', id: 'telemetry' }
                  ].map(t => (
                    <div
                      key={t.id}
                      onClick={() => setSelectedNode(t.id)}
                      className={`p-2.5 rounded-lg border cursor-pointer transition-all space-y-1 ${
                        selectedNode === t.id ? 'bg-blue-50 border-blue-400' : 'bg-gray-50 border-[#E5E7EB] hover:border-gray-400'
                      }`}
                    >
                      <div className="flex items-center space-x-1.5">
                        <span className="text-sm">{t.icon}</span>
                        <span className={`text-[10px] font-bold ${t.color}`}>{t.label}</span>
                      </div>
                      <p className="text-[9px] text-gray-500 leading-normal">{t.detail}</p>
                    </div>
                  ))}
                </div>

                {/* CENTER: BRANCHING ORCHESTRATION LOOP */}
                <div className="flex-1 bg-white border border-[#E5E7EB] rounded-xl overflow-hidden shadow-xs">
                  <div className="bg-gray-50 border-b border-[#E5E7EB] px-4 py-2 flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full border-2 border-blue-600 animate-spin" style={{ animationDuration: '3s' }} />
                    <span className="text-[9px] font-extrabold text-gray-800 uppercase tracking-widest">Active State Nodes</span>
                  </div>

                  <div className="grid grid-cols-4 gap-0 border-b border-[#E5E7EB]">
                    {[
                      { id: 'analysis', title: '1. ANALYSIS', sub: 'Ingestion & Grounding', icon: '🧠', color: 'blue', status: activeCycleStep === 'analysis' ? 'running' : 'completed' },
                      { id: 'adaptation', title: '2. ADAPTATION', sub: 'Logic Proposer', icon: '⚙️', color: 'purple', status: activeCycleStep === 'adaptation' ? 'running' : 'completed' },
                      { id: 'evaluation', title: '3. SELF-CRITIQUE', sub: 'Auditor & Evaluation', icon: '🛡️', color: 'emerald', status: activeCycleStep === 'evaluation' ? 'running' : 'completed' },
                      { id: 'deploy', title: '4. DEPLOYMENT', sub: 'Production Canary', icon: '🚀', color: 'amber', status: activeCycleStep === 'deploy' ? 'running' : 'completed' }
                    ].map((node, i) => {
                      const isActive = activeCycleStep === node.id;
                      const isSelected = selectedNode === node.id;
                      const labelColor = node.color === 'blue' ? 'text-blue-600' : node.color === 'purple' ? 'text-purple-600' : node.color === 'emerald' ? 'text-emerald-600' : 'text-amber-600';
                      return (
                        <div
                          key={node.id}
                          onClick={() => setSelectedNode(node.id)}
                          className={`p-3 border-r border-[#E5E7EB] last:border-r-0 cursor-pointer transition-all space-y-2 ${
                            isActive ? 'bg-blue-50 border-2 border-blue-400' :
                            isSelected ? 'bg-gray-50 border-2 border-blue-400' : 'hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex justify-between items-center">
                            <span className={`text-[9px] font-bold ${labelColor}`}>{node.title}</span>
                            {isActive && <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />}
                          </div>
                          <p className="text-[10px] text-gray-500">{node.sub}</p>
                          <div className="text-xl text-center">{node.icon}</div>
                        </div>
                      );
                    })}
                  </div>

                  {/* BRANCHING LEGENDS */}
                  <div className="px-4 py-3 bg-gray-50 border-b border-[#E5E7EB] text-[10px] flex justify-between items-center font-mono">
                    <span className="text-gray-500 font-bold uppercase tracking-wider">Conditional Edges:</span>
                    <div className="flex space-x-3">
                      <span className="text-emerald-600">🟢 Approved (Score &gt; 8) → Deploy</span>
                      <span className="text-rose-600">🔴 Rejected (Score ≤ 8) → Loop back</span>
                      <span className="text-amber-600">🟡 Manual Review (HITL Queue)</span>
                    </div>
                  </div>

                  {/* LIVE SHARED STATE PANEL */}
                  <div className="p-4 bg-white border-b border-[#E5E7EB]">
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block mb-2">LangGraph Shared-State Object</span>
                    <div className="grid grid-cols-7 gap-2 text-[10px] font-mono">
                      {[
                        { label: 'workflow_id', val: 'WF-ADAPT-049' },
                        { label: 'current_framework', val: 'GDPR / Law 25' },
                        { label: 'trigger_type', val: 'Regulatory' },
                        { label: 'evaluation_score', val: '9' },
                        { label: 'is_approved', val: 'True' },
                        { label: 'current_node', val: activeCycleStep || 'idle' },
                        { label: 'retry_count', val: '0' }
                      ].map((field, idx) => (
                        <div key={idx} className="bg-gray-50 border border-[#E5E7EB] p-2 rounded text-center">
                          <div className="text-gray-400 text-[8px] uppercase">{field.label}</div>
                          <div className="text-gray-900 font-bold mt-1">{field.val}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Reasoning log */}
                  <div className="p-4">
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block mb-1">Live reasoning stream (SSE)</span>
                    <div className="h-20 bg-gray-950 text-emerald-400 rounded-lg p-2.5 font-mono text-[10px] overflow-y-auto leading-relaxed">
                      {simReasoning.map((r, i) => (
                        <div key={i}>{r}</div>
                      ))}
                      {simReasoning.length === 0 && <span className="text-gray-600 italic">Streaming logs idle. Inject trigger to begin...</span>}
                    </div>
                  </div>

                </div>

                {/* RIGHT: NODE INSPECTOR */}
                <div className="w-64 shrink-0 bg-white border border-[#E5E7EB] rounded-xl p-3 shadow-xs space-y-3">
                  <div className="text-[9px] font-extrabold text-gray-500 uppercase tracking-widest border-b border-[#E5E7EB] pb-2">Node Inspector</div>
                  {selectedNode && nodeStates[selectedNode] ? (
                    <div className="space-y-2 text-xs text-gray-700">
                      <div className="font-bold text-blue-600 uppercase text-[9px]">{selectedNode} Parameters</div>
                      <div><span className="font-bold text-gray-500 block uppercase text-[8px]">Inputs:</span> {nodeStates[selectedNode].input}</div>
                      <div><span className="font-bold text-gray-500 block uppercase text-[8px]">Outputs:</span> {nodeStates[selectedNode].output}</div>
                      <div><span className="font-bold text-gray-500 block uppercase text-[8px]">LLM / Cost:</span> {nodeStates[selectedNode].cost} ({nodeStates[selectedNode].tokens} tokens)</div>
                      <div><span className="font-bold text-gray-500 block uppercase text-[8px]">Latency / Prompt:</span> {nodeStates[selectedNode].duration} / {nodeStates[selectedNode].prompt}</div>
                      <div><span className="font-bold text-gray-500 block uppercase text-[8px]">Reasoning logic:</span> <span className="italic text-gray-600">"{nodeStates[selectedNode].reasoning}"</span></div>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400 italic">Select any node on the loop to audit inputs/outputs.</span>
                  )}
                </div>

              </div>

            </div>
          )}

          {/* TAB 4: GOVERNANCE ORCHESTRATION */}
          {adminTab === 'orchestration' && (
            <div className="space-y-6">
              
              <div className="bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-emerald-500/5 border border-blue-200 p-5 rounded-xl flex items-start justify-between gap-4 shadow-xs">
                <div className="space-y-1">
                  <h3 className="text-sm font-extrabold text-gray-900 tracking-wide">Agentic Secretariat — Communication & Workflow Intelligence</h3>
                  <p className="text-xs text-gray-500 leading-relaxed max-w-2xl">
                    Kibo monitors communication payloads, transcribes meetings, and escalates governance tasks to the PSR Committee.
                  </p>
                </div>
                <span className="text-[9px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full uppercase">3 Sub-Agents Active</span>
              </div>

              {/* Sub-Agent Pipeline */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">Sub-Agent Node Pipeline</span>
                <div className="grid grid-cols-4 gap-4">
                  {[
                    { label: 'Email Agent Node', detail: 'Extracts DPA and Vendor attachments from inbox', color: 'blue' },
                    { label: 'Meeting Agent Node', detail: 'Transcribes and highlights compliance risks', color: 'purple' },
                    { label: 'Governance Router', detail: 'Determines framework thresholds and schedules', color: 'amber' },
                    { label: 'KiboState Sync', detail: 'Mutates active RAG stores & schema files', color: 'emerald' }
                  ].map((node, idx) => (
                    <div key={idx} className="bg-gray-50 border border-[#E5E7EB] hover:border-blue-400 p-3 rounded-lg text-center cursor-pointer transition-all">
                      <div className="text-[9px] font-bold text-gray-800 uppercase">{node.label}</div>
                      <p className="text-[9px] text-gray-400 mt-1 leading-snug">{node.detail}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Three Agent Columns */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                
                {/* Email Extraction */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl overflow-hidden shadow-xs">
                  <div className="bg-blue-50 border-b border-blue-200 px-4 py-3">
                    <h4 className="text-xs font-extrabold text-blue-700 uppercase">Email Ingestion Agent</h4>
                  </div>
                  <div className="p-4 space-y-3">
                    {[
                      { from: 'legal@kidshelpphone.ca', preview: '"Updated contract with OpenText for Gen AI transition."', status: 'Vendor DPA' }
                    ].map((e, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 border border-[#E5E7EB] rounded-lg text-xs space-y-1">
                        <div className="font-bold text-gray-800">{e.from}</div>
                        <p className="text-[11px] text-gray-500 italic">"{e.preview}"</p>
                        <div className="text-[9px] text-blue-600 font-bold uppercase tracking-wider">{e.status}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Meeting Intelligence */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl overflow-hidden shadow-xs">
                  <div className="bg-purple-50 border-b border-purple-200 px-4 py-3">
                    <h4 className="text-xs font-extrabold text-purple-700 uppercase">Meeting Intelligence</h4>
                  </div>
                  <div className="p-4 space-y-3">
                    {[
                      { title: 'PSR Committee — May 27, 2026', details: 'Transition of Gen AI project from Nascent to OpenText. Approved.', audit_link: 'AUDIT-2026-07-03-8893' }
                    ].map((m, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 border border-[#E5E7EB] rounded-lg text-xs space-y-1.5">
                        <div className="font-bold text-gray-800">{m.title}</div>
                        <p className="text-[11px] text-gray-500 leading-normal">{m.details}</p>
                        <a href="#" onClick={(e) => { e.preventDefault(); setAdminTab('audits'); }} className="text-[9px] text-purple-600 hover:underline font-bold block">
                          → View Audit Link {m.audit_link}
                        </a>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Follow-up orchestration */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl overflow-hidden shadow-xs">
                  <div className="bg-amber-50 border-b border-amber-200 px-4 py-3">
                    <h4 className="text-xs font-extrabold text-amber-700 uppercase">Follow-up Agent</h4>
                  </div>
                  <div className="p-4 space-y-3">
                    {[
                      { to: 'Betty Zhang', task: 'DPIA #12 review', sla: '3 days overdue' }
                    ].map((f, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 border border-[#E5E7EB] rounded-lg text-xs flex justify-between items-center">
                        <div>
                          <div className="font-bold text-gray-800">{f.to}</div>
                          <span className="text-gray-500 text-[10px]">{f.task}</span>
                        </div>
                        <span className="text-rose-600 font-mono text-[9px] font-bold">{f.sla}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </div>
          )}

          {/* TAB 5: RAG KNOWLEDGE BASE */}
          {adminTab === 'rag' && (
            <div className="space-y-6">
              
              {/* Pipeline Health strip */}
              <div className="bg-white border border-[#E5E7EB] p-4.5 rounded-xl shadow-xs flex justify-between items-center">
                <div>
                  <h3 className="text-xs font-extrabold text-gray-900 uppercase">RAG Pipeline Health & Index metrics</h3>
                  <p className="text-[10px] text-gray-400 mt-0.5">Continuous embedding evaluation checks</p>
                </div>
                <div className="flex space-x-6 text-[10px] font-mono text-gray-500">
                  <span className="text-emerald-600">● Embedding Pipeline: HEALTHY</span>
                  <span>● Retrieval Latency: 42ms</span>
                  <span className="text-blue-600">● Grounding score: 98.4%</span>
                </div>
              </div>

              {/* Five Domain Cards */}
              <div className="grid grid-cols-5 gap-3">
                {[
                  { id: 'laws', title: 'Laws & Regulations', count: 24, sync: '2m ago', confidence: 98, color: 'border-blue-300' },
                  { id: 'guidance', title: 'Regulatory Guidance', count: 48, sync: '10m ago', confidence: 95, color: 'border-purple-300' },
                  { id: 'case_law', title: 'Case Law & Precedent', count: 18, sync: '1h ago', confidence: 92, color: 'border-amber-300' },
                  { id: 'policies', title: 'Internal Policies', count: 12, sync: '2h ago', confidence: 97, color: 'border-rose-300' },
                  { id: 'ux_patterns', title: 'Approved UX Patterns', count: 36, sync: '1d ago', confidence: 96, color: 'border-emerald-300' }
                ].map(domain => (
                  <div
                    key={domain.id}
                    onClick={() => setSelectedRAGDomain(domain.id)}
                    className={`bg-white border p-3.5 rounded-xl cursor-pointer shadow-xs transition-all ${
                      selectedRAGDomain === domain.id ? 'border-blue-500 ring-2 ring-blue-100' : 'border-[#E5E7EB] hover:border-gray-400'
                    }`}
                  >
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">{domain.title}</span>
                    <div className="text-lg font-black text-gray-900 mt-1">{domain.count} Documents</div>
                    <div className="flex justify-between items-center text-[9px] text-gray-400 mt-2 font-mono">
                      <span>Sync: {domain.sync}</span>
                      <span>{domain.confidence}% match</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Document search & list */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold uppercase text-gray-800 tracking-wider">Document browser</span>
                  <div className="flex items-center space-x-1.5 bg-gray-50 border border-gray-300 px-2 py-1 rounded-md">
                    <Search size={12} className="text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search RAG documents..."
                      value={ragSearchQuery}
                      onChange={(e) => setRagSearchQuery(e.target.value)}
                      className="bg-transparent text-xs outline-hidden w-40 text-gray-800"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {filteredRAGDocs.map((doc, idx) => (
                    <div key={idx} className="bg-gray-50 border border-[#E5E7EB] p-3 rounded-lg text-xs space-y-2">
                      <div className="font-bold text-gray-900">{doc.name}</div>
                      <div className="text-[10px] text-gray-500 font-mono">Effective: {doc.effective}</div>
                      <p className="text-[10px] text-gray-600 leading-relaxed">"{doc.details || doc.scope}"</p>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* TAB 6: AUTHORITATIVE SOURCES (Diff comparator + registry) */}
          {adminTab === 'source_viewer' && (
            <div className="space-y-6">
              
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
                <h3 className="text-xs font-bold uppercase text-gray-800 tracking-wider">Authoritative Source Registry</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-[#E5E7EB] text-gray-500">
                        <th className="pb-2">Source ID</th>
                        <th className="pb-2">Tier</th>
                        <th className="pb-2">Statute</th>
                        <th className="pb-2">Jurisdiction</th>
                        <th className="pb-2">Version</th>
                        <th className="pb-2">Verified</th>
                        <th className="pb-2 text-right">Commit hash</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { id: 'SRC-001', tier: 'Tier 1 - Binding Law', statute: 'Law 25', jurisdiction: 'Quebec, CA', version: '2023 Edition', date: '2026-07-01', hash: 'SHA256:b8c983ea' },
                        { id: 'SRC-002', tier: 'Tier 1 - Binding Law', statute: 'PIPEDA', jurisdiction: 'Canada (Federal)', version: 'Consolidated', date: '2026-07-02', hash: 'SHA256:d9b2089f' }
                      ].map((src, i) => (
                        <tr key={i} className="border-b border-gray-100 last:border-b-0">
                          <td className="py-2.5 font-bold font-mono text-blue-600">{src.id}</td>
                          <td className="py-2.5 text-purple-600">{src.tier}</td>
                          <td className="py-2.5 font-semibold text-gray-900">{src.statute}</td>
                          <td className="py-2.5">{src.jurisdiction}</td>
                          <td className="py-2.5 font-mono">{src.version}</td>
                          <td className="py-2.5">{src.date}</td>
                          <td className="py-2.5 text-right font-mono text-gray-400">{src.hash}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Diff Viewer */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
                <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-900">Change Detection & Diff Comparator</h3>
                  <button onClick={() => setDiffMode(!diffMode)} className="bg-gray-100 hover:bg-gray-200 border border-gray-300 text-gray-700 text-xs px-3 py-1.5 rounded-lg cursor-pointer">
                    {diffMode ? 'Visual Comparison' : 'Strict Code Diff'}
                  </button>
                </div>

                {diffMode ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                      <span className="text-[9px] font-bold text-rose-600 uppercase block mb-1">Pre-Adaptation Logic</span>
                      <pre className="font-mono text-xs text-gray-700">
{`def validate_consent(payload):
    if not payload.get("consent"):
        return False
    return True`}
                      </pre>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
                      <span className="text-[9px] font-bold text-emerald-600 uppercase block mb-1">AI Proposed Adaptation</span>
                      <pre className="font-mono text-xs text-gray-700">
{`def validate_consent(payload):
    if not payload.get("consent_bilingual"):
        log_warning("Bilingual consent missing")
        return False
    return True`}
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-950 text-gray-300 font-mono text-xs p-4 rounded-lg space-y-1">
                    <div>  def validate_consent(payload):</div>
                    <div className="text-rose-400 bg-rose-950/20 px-2 rounded">-     if not payload.get("consent"):</div>
                    <div className="text-emerald-400 bg-emerald-950/20 px-2 rounded">+     # Quebec Law 25 consent parameters</div>
                    <div className="text-emerald-400 bg-emerald-950/20 px-2 rounded">+     if not payload.get("consent_bilingual"):</div>
                    <div className="text-emerald-400 bg-emerald-950/20 px-2 rounded">+         log_warning("Bilingual consent missing")</div>
                    <div>          return False</div>
                    <div>      return True</div>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* TAB 7: TRUST TIERS */}
          {adminTab === 'trust_tiers' && (
            <div className="space-y-6">
              
              <div className="grid grid-cols-4 gap-4">
                {[
                  { tier: 'Tier 1', title: 'Binding Laws', count: 24, rule: 'Allowed to drive core logic mutations.', tags: ['PIPEDA', 'GDPR', 'Law 25'] },
                  { tier: 'Tier 2', title: 'Regulatory Guidance', count: 48, rule: 'Enforces parameter and validation triggers.', tags: ['EDPB Guidelines', 'ICO Advisories'] },
                  { tier: 'Tier 3', title: 'Internal Policies', count: 12, rule: 'Contextual references for DPIA templates.', tags: ['Company Standards'] },
                  { tier: 'Tier 4', title: 'External Knowledge', count: 36, rule: 'Auxiliary references, never used for direct rules.', tags: ['Privacy Blogs'] }
                ].map(t => (
                  <div key={t.tier} className="bg-white border border-[#E5E7EB] p-4.5 rounded-xl shadow-xs space-y-3">
                    <span className="text-[10px] font-bold text-blue-600 uppercase font-mono tracking-wider">{t.tier}</span>
                    <h4 className="text-xs font-bold text-gray-900 uppercase">{t.title}</h4>
                    <div className="text-[10px] text-gray-500 font-mono">{t.count} Grounded Documents</div>
                    <p className="text-[11px] text-gray-600 leading-normal">{t.rule}</p>
                    
                    <div className="flex flex-wrap gap-1 pt-2">
                      {t.tags.map(tag => (
                        <button
                          key={tag}
                          onClick={() => {
                            setSelectedRAGDomain('laws');
                            setRagSearchQuery(tag);
                            setAdminTab('rag');
                          }}
                          className="bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-600 text-[8px] font-bold px-1.5 py-0.5 rounded cursor-pointer"
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

            </div>
          )}

          {/* TAB 8: HITL APPROVAL CENTER */}
          {adminTab === 'hitl' && (
            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-900">Human-in-the-Loop approval queue</h3>
                <p className="text-xs text-gray-400 mt-1">Audit, approve, or escalate autonomous compliance improvements.</p>
              </div>

              <div className="space-y-4">
                {[
                  { id: 'QA-201', trigger: 'Trigger Ingestion - Law 25', score: '8.4', impact: 'High Risk', change: 'Enable automated bilingual consent templates for Quebec campaigns (LAW25-SEC14).', coSignNeeded: true, hallucination: '0.1%', grounding: '98.5%' },
                  { id: 'QA-202', trigger: 'User Friction - Vendor Form', score: '9.0', impact: 'Low Risk', change: 'Simplify vendor onboarding profile validations (GDPR-ART28).', coSignNeeded: false, hallucination: '0.0%', grounding: '99.9%' }
                ].map(item => {
                  const isApproved = hitlDecisionLog[item.id] === 'approved';
                  const isRejected = hitlDecisionLog[item.id] === 'rejected';
                  return (
                    <div key={item.id} className="p-4 bg-gray-50 border border-[#E5E7EB] rounded-xl text-xs space-y-3">
                      <div className="flex justify-between items-start">
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-extrabold text-gray-900 text-sm font-mono">{item.id}</span>
                            <span className="text-[10px] text-gray-500">{item.trigger}</span>
                            <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold uppercase ${
                              item.impact === 'High Risk' ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            }`}>{item.impact}</span>
                          </div>
                          <p className="text-gray-700 font-medium">"{item.change}"</p>
                        </div>
                        
                        {/* Status badge */}
                        <div className="text-right">
                          <span className="text-[10px] text-gray-500 font-bold block">Evaluation: {item.score}/10</span>
                          <span className="text-[9px] text-gray-400 font-mono">Grounding: {item.grounding} | Hal: {item.hallucination}</span>
                        </div>
                      </div>

                      {/* Co-signature indicator */}
                      {item.coSignNeeded && (
                        <div className="bg-amber-50 border border-amber-200 text-amber-800 p-2 rounded text-[10px] font-semibold">
                          ⚠️ Dual Approval Mandatory: Requires a second CPO co-signature before deploying to production.
                        </div>
                      )}

                      {/* Structured Rationale notes */}
                      {!isApproved && !isRejected && (
                        <div className="flex items-center space-x-3 pt-2">
                          <input
                            type="text"
                            placeholder="Add administrative review rationale..."
                            className="bg-white border border-gray-300 rounded px-2.5 py-1 text-xs w-72 text-gray-800"
                            onChange={(e) => setHitlNote(e.target.value)}
                          />
                          <button
                            onClick={() => {
                              setHitlDecisionLog(prev => ({ ...prev, [item.id]: 'approved' }));
                              alert(`Item ${item.id} approved. Logged in audit registry.`);
                            }}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-3 py-1.5 rounded cursor-pointer"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => {
                              setHitlDecisionLog(prev => ({ ...prev, [item.id]: 'rejected' }));
                              alert(`Item ${item.id} rejected. Redirected to adaptation node for refinement.`);
                            }}
                            className="bg-rose-600 hover:bg-rose-700 text-white font-bold px-3 py-1.5 rounded cursor-pointer"
                          >
                            Reject
                          </button>
                        </div>
                      )}

                      {(isApproved || isRejected) && (
                        <div className={`text-[11px] font-bold ${isApproved ? 'text-emerald-600' : 'text-rose-600'}`}>
                          ✓ Decision logged: {isApproved ? 'Approved' : 'Rejected'} &bull; Actor: Admin &bull; Note: "{hitlNote || 'Standard verification passed'}"
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 9: DEPLOYMENT CENTER */}
          {adminTab === 'deployment' && (
            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-900">Deployment Pipeline Center</h3>
                <p className="text-xs text-gray-400 mt-1">Canary deployments, validation logs, and rollback commands.</p>
              </div>

              <div className="space-y-4">
                {deployments.map((d, idx) => (
                  <div key={idx} className="p-4 bg-gray-50 border border-[#E5E7EB] rounded-xl text-xs space-y-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-extrabold text-gray-900 text-sm font-mono">{d.version}</span>
                          <span className="bg-blue-50 text-blue-700 border border-blue-200 text-[9px] px-1.5 py-0.5 rounded-full uppercase font-bold">{d.environment}</span>
                        </div>
                        <span className="text-[10px] text-gray-400">Proposed by: {d.proposed_by} | Approved by: {d.approved_by}</span>
                      </div>
                      
                      <div className="text-right font-mono">
                        <span className="text-[10px] text-gray-500 block">{d.timestamp}</span>
                        <span className="text-[9px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full uppercase mt-1 inline-block">Active</span>
                      </div>
                    </div>

                    {/* Canary / Staging progression visual bar */}
                    <div className="space-y-1">
                      <span className="text-[9px] text-gray-400 uppercase font-bold">Pipeline Stage progression</span>
                      <div className="flex items-center space-x-1.5">
                        <div className="flex-1 h-1.5 rounded-full bg-blue-600" />
                        <div className="flex-1 h-1.5 rounded-full bg-blue-600" />
                        <div className={`flex-1 h-1.5 rounded-full ${d.environment === 'production' ? 'bg-blue-600' : 'bg-gray-200'}`} />
                        <span className="text-[9px] font-mono text-gray-500">{d.environment === 'production' ? 'Production (100%)' : 'Canary (10%)'}</span>
                      </div>
                    </div>

                    {/* Rollback controls */}
                    {d.rollbackAvailable && (
                      <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                        <span className="text-[9px] text-gray-400 font-mono">Rollback commit ID: <code className="bg-gray-100 px-1 py-0.5 rounded text-gray-700">{d.commit}</code></span>
                        <button
                          onClick={() => handleRollback(d.version)}
                          className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-[10px] font-bold px-3 py-1 rounded cursor-pointer"
                        >
                          Rollback version
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 10: UX TELEMETRY FEEDBACK */}
          {adminTab === 'telemetry' && (
            <div className="space-y-6">
              
              {/* Friction Warning Banner */}
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl flex justify-between items-center shadow-xs">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="text-amber-600" size={18} />
                  <div>
                    <span className="text-xs font-bold text-amber-900 block">Friction Threshold Breach Detected</span>
                    <span className="text-[10px] text-amber-700">Drop-off rate on donor forms is 7.6% (Limit: 5.0%). Auto-created trigger TR-102.</span>
                  </div>
                </div>
                <button
                  onClick={() => setAdminTab('engine')}
                  className="bg-amber-600 hover:bg-amber-700 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg cursor-pointer"
                >
                  Inspect Trigger
                </button>
              </div>

              {/* Metric grid */}
              <div className="grid grid-cols-5 gap-3">
                {[
                  { label: 'Completion Rate', val: '92.4%', color: 'text-emerald-600', desc: 'Active consent rates' },
                  { label: 'Time on Task', val: '1m 14s', color: 'text-blue-600', desc: 'Average DSAR time' },
                  { label: 'Friction Drop-off', val: '7.6%', color: 'text-rose-600', desc: 'Form exits' },
                  { label: 'AI Acceptance Rate', val: '94.2%', color: 'text-purple-600', desc: 'Proposed logic accepts' },
                  { label: 'Human Overrides', val: '1.2%', color: 'text-amber-600', desc: 'Manual changes' }
                ].map((m, idx) => (
                  <div key={idx} className="bg-white border border-[#E5E7EB] p-4.5 rounded-xl shadow-xs">
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">{m.label}</span>
                    <div className={`text-xl font-black ${m.color} mt-1`}>{m.val}</div>
                    <p className="text-[9px] text-gray-400 mt-1 leading-snug">{m.desc}</p>
                  </div>
                ))}
              </div>

              {/* 30/90 Day Trend Lines */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-3">
                <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider block">Friction Deviation Trends (30/90 days)</span>
                <div className="h-28 flex items-end space-x-2 pt-4">
                  {[24, 30, 48, 52, 40, 20, 15, 30, 45, 60, 40, 30, 20, 10, 8].map((val, idx) => (
                    <div key={idx} className="flex-1 bg-gray-100 rounded h-full flex flex-col justify-end relative group">
                      <div className="w-full bg-blue-500 hover:bg-blue-600 rounded" style={{ height: `${val * 1.5}%` }} />
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-900 text-white text-[8px] px-1.5 py-0.5 rounded shadow whitespace-nowrap">
                        Week {idx}: {val}% Friction
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* TAB 11: AI AGENT MONITOR (Full Agent Lifecycle Viewer Drawer) */}
          {adminTab === 'agents' && (
            <div className="space-y-6 relative">
              
              <div className="bg-white border border-[#E5E7EB] rounded-xl overflow-hidden shadow-xs">
                <div className="p-4 border-b border-[#E5E7EB] flex justify-between items-center">
                  <h3 className="text-xs font-bold uppercase text-gray-800 tracking-wider">Active Autonomous AI Agents</h3>
                  <span className="text-[10px] text-gray-400 font-mono">Click agent row to audit full lifecycle drawer</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-gray-50 border-b border-[#E5E7EB] text-gray-500 uppercase text-[9px] tracking-wider">
                        <th className="p-3">Agent Name</th>
                        <th className="p-3">Version</th>
                        <th className="p-3">Lifecycle stage</th>
                        <th className="p-3 font-mono">Queue</th>
                        <th className="p-3">Runtime</th>
                        <th className="p-3">LLM Cost</th>
                        <th className="p-3">Success %</th>
                        <th className="p-3 font-mono">Memory</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E5E7EB] text-gray-700">
                      {agents.map((a, idx) => (
                        <tr
                          key={idx}
                          onClick={() => setSelectedAgent(a)}
                          className="hover:bg-gray-50 cursor-pointer"
                        >
                          <td className="p-3 font-bold text-gray-900">{a.name}</td>
                          <td className="p-3 font-mono text-[10px] text-gray-500">{a.version}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase bg-blue-50 text-blue-700 border border-blue-200">{a.stage}</span>
                          </td>
                          <td className="p-3 font-mono">{a.queue}</td>
                          <td className="p-3 font-mono">{a.runtime}</td>
                          <td className="p-3 font-mono text-emerald-600">{a.cost}</td>
                          <td className="p-3 font-mono text-emerald-600">{a.success}</td>
                          <td className="p-3 font-mono">{a.memory}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Agent Lifecycle Audit Drawer */}
              {selectedAgent && (
                <div className="fixed inset-y-0 right-0 w-96 bg-white border-l border-gray-200 shadow-2xl p-5 z-40 space-y-4 flex flex-col justify-between overflow-y-auto">
                  <div className="space-y-4">
                    <div className="flex justify-between items-start border-b border-gray-200 pb-3">
                      <div>
                        <h4 className="text-sm font-extrabold text-gray-950">{selectedAgent.name}</h4>
                        <span className="text-[10px] text-gray-400 font-mono">Active Version: {selectedAgent.version}</span>
                      </div>
                      <button onClick={() => setSelectedAgent(null)} className="text-gray-400 hover:text-black font-extrabold text-xs">✕</button>
                    </div>

                    {/* Timeline */}
                    <div className="space-y-1.5">
                      <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block">Agent Lifecycle Timeline</span>
                      <div className="space-y-2 text-[10px]">
                        {[
                          { date: '2026-07-01 09:00', title: 'Registered', desc: 'Agent initialized in system directory.' },
                          { date: '2026-07-02 10:15', title: 'Active', desc: 'Promoted to primary Loop workflow routing.' }
                        ].map((t, idx) => (
                          <div key={idx} className="border-l-2 border-blue-500 pl-2">
                            <span className="font-bold text-gray-800">{t.title}</span> <span className="text-[9px] text-gray-400 font-mono">{t.date}</span>
                            <p className="text-gray-500">{t.desc}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Model & Prompt Lineage */}
                    <div className="space-y-1">
                      <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block">Prompt & Model Lineage</span>
                      <div className="bg-gray-50 border border-gray-200 p-2.5 rounded text-xs font-mono">
                        <div>Prompt ID: <span className="text-blue-600 font-bold">p-104 (active)</span></div>
                        <div className="mt-1">Model Chain: <span className="text-purple-600">qwen2.5:7b → qwen3.6:latest</span></div>
                      </div>
                    </div>

                    {/* Health SLOs */}
                    <div className="space-y-1">
                      <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block">SLO Targets & Metrics</span>
                      <div className="flex justify-between text-xs font-mono">
                        <span>Success rate: <strong className="text-emerald-600">99.8%</strong></span>
                        <span>Latency p95: <strong>2.4s</strong></span>
                      </div>
                    </div>

                    {/* Action Controls */}
                    <div className="space-y-2 border-t border-gray-200 pt-3">
                      <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider block">Gated Admin Controls</span>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleToggleAgent(selectedAgent.name)}
                          className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-[10px] py-2 rounded-lg cursor-pointer text-center"
                        >
                          Pause Agent
                        </button>
                        <button
                          onClick={() => handleToggleAgent(selectedAgent.name)}
                          className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 border border-gray-300 font-bold text-[10px] py-2 rounded-lg cursor-pointer text-center"
                        >
                          Restart Node
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* TAB 12: AUDIT HISTORY (Fully cross-referenced filters) */}
          {adminTab === 'audits' && (
            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-4">
              
              <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-3">
                <div className="flex items-center space-x-4">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-gray-900">Immutable Ledger Audit Timeline</h3>
                  
                  {/* Client Filter */}
                  <select
                    value={auditClientFilter}
                    onChange={(e) => setAuditClientFilter(e.target.value)}
                    className="bg-white border border-gray-300 text-[10px] rounded px-2 py-1 text-gray-700 cursor-pointer"
                  >
                    <option value="all">All Clients</option>
                    <option value="Kids Help Phone">Kids Help Phone</option>
                    <option value="KHP Foundation">KHP Foundation</option>
                  </select>

                  <div className="flex bg-gray-50 border border-gray-300 p-0.5 rounded-lg text-[10px]">
                    {['all', 'success', 'approved', 'rejected'].map(filter => (
                      <button
                        key={filter}
                        onClick={() => setSelectedAuditFilter(filter)}
                        className={`px-2.5 py-1 rounded-md uppercase font-bold cursor-pointer transition-all ${
                          selectedAuditFilter === filter ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        {filter}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Search audits..."
                    value={auditSearch}
                    onChange={(e) => setAuditSearch(e.target.value)}
                    className="bg-white border border-gray-300 text-xs px-2.5 py-1 rounded-md text-gray-800"
                  />
                </div>
              </div>

              <div className="space-y-4">
                {filteredAuditsList.map((a, idx) => (
                  <div key={idx} className="bg-white border border-[#E5E7EB] rounded-xl p-5 space-y-4 text-xs shadow-xs">
                    <div className="flex justify-between items-center border-b border-gray-150 pb-2">
                      <span className="font-extrabold text-gray-900 text-sm font-mono">{a.audit_id}</span>
                      <span className="text-[10px] text-gray-400 font-mono">{a.timestamp}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="space-y-1">
                        <span className="text-gray-400 text-[9px] uppercase font-bold block">Compliance Provenance</span>
                        <div className="text-gray-900 font-semibold">{a.authoritative_source}</div>
                        <div className="text-gray-550 font-mono text-[10px]">{a.citation_id}</div>
                      </div>

                      <div className="space-y-1">
                        <span className="text-gray-400 text-[9px] uppercase font-bold block">Decisions & Deployments</span>
                        <div className="text-gray-900 font-semibold">{a.decision_status} &bull; {a.admin_user_id}</div>
                        <span className="text-blue-600 font-mono font-bold block">{a.deployment_version}</span>
                      </div>

                      <div className="space-y-1 text-right">
                        <span className="text-gray-400 text-[9px] uppercase font-bold block">Reciprocal crosslinks</span>
                        <a href="#" onClick={(e) => { e.preventDefault(); setAdminTab('langgraph'); }} className="text-blue-600 hover:underline block text-[10px]">
                          → View Workflow Visualizer
                        </a>
                        <a href="#" onClick={(e) => { e.preventDefault(); setAdminTab('hitl'); }} className="text-purple-600 hover:underline block text-[10px]">
                          → View HITL Decision
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {adminTab === 'user_governance' && (
            <UserGovernanceCockpit API_BASE={API_BASE} />
          )}

          {adminTab === 'compliance_map' && (
            <ComplianceCoverageMap API_BASE={API_BASE} />
          )}

        </div>

      </div>

    </div>
  );
}
