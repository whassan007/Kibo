import React, { useState, useMemo } from 'react';
import {
  Shield, User, ShieldAlert, Users, Cpu, FileText, Globe, Key, AlertTriangle, CheckCircle,
  XCircle, Search, Filter, Play, Trash2, ArrowRight, UserCheck, Calendar, Clock, RefreshCw,
  Plus, Database, Eye, Terminal, BookOpen, Layers, Check, HelpCircle, AlertOctagon, Send
} from 'lucide-react';

// --- MOCK DATA ---
const INITIAL_ENTITIES = [
  {
    id: 'ent-1',
    type: 'user',
    name: 'Wael Hassan',
    role: 'Chief Privacy Officer (CPO)',
    organization: 'KIBO Core',
    riskTier: 'Low',
    riskScore: 12,
    accessLevel: 'L4 - Unrestricted',
    jurisdictionScope: 'Global (GDPR, HIPAA, Law 25, PIPEDA)',
    lastActivity: '2 mins ago',
    trustScore: 98,
    clearanceLevel: 'Top Secret / DPO Override',
    verificationStatus: 'Verified (MFA + Biometric)',
    employmentStatus: 'Full-Time Active',
    delegatedAuthorities: ['Policy Sign-Off', 'Emergency System Freeze', 'Global Exemption Approvals'],
    roleHistory: [
      { date: '2024-01-15', action: 'Promoted to CPO', actor: 'Board' },
      { date: '2022-06-10', action: 'Joined as DPO', actor: 'HR' }
    ],
    entitlements: [
      { id: 'ent-u1-1', system: 'KIBO Registry', dataset: 'SPI Database', workflow: 'Incident Management', approval: 'DPO Sign-off', region: 'Global', dataType: 'SPI / Health', justification: 'Required for global data breach response', legalBasis: 'GDPR Art. 32 / PIPEDA Sec. 7', approvalHistory: 'Approved by Board on 2024-01-15', expiration: 'Indefinite', lastUsage: '1 hour ago' },
      { id: 'ent-u1-2', system: 'Consent Analytics', dataset: 'User Preferences', workflow: 'Audit Review', approval: 'Self-Authorize', region: 'EU/CA', dataType: 'PII', justification: 'Regulatory compliance reporting and trends', legalBasis: 'GDPR Art. 6(1)(c)', approvalHistory: 'Auto-granted for role', expiration: 'Indefinite', lastUsage: '10 mins ago' }
    ],
    timeline: [
      { id: 't1-1', time: '2026-07-03 18:25', type: 'login', text: 'MFA Login from secure subnet 192.168.1.45', legalBasis: 'N/A', impact: 'None' },
      { id: 't1-2', time: '2026-07-03 17:40', type: 'approval', text: 'Approved Law 25 compliance layout update for KHP', legalBasis: 'Quebec Law 25 Sec 14', impact: 'System Configuration' },
      { id: 't1-3', time: '2026-07-03 15:10', type: 'access', text: 'Accessed SPI database for incident reporting', legalBasis: 'GDPR Art 33 Notification', impact: 'SPI Decrypted' }
    ],
    riskSignals: [
      { label: 'Access Risk', score: 10, trend: 'stable', desc: 'Authorized to access critical SPI, high privilege load.' },
      { label: 'Compliance Deviation', score: 5, trend: 'down', desc: 'Perfect adherence to security guidelines.' },
      { label: 'Behavioral Anomaly', score: 15, trend: 'stable', desc: 'Login timing and IP ranges match standard profile.' },
      { label: 'Privilege Escalation Risk', score: 8, trend: 'stable', desc: 'No unauthorized request for new privileges detected.' }
    ],
    aiInfluence: [
      { id: 'ai-inf-1', agent: 'Compliance Advisor Agent', suggestion: 'Suggested GDPR Article 30 report template structure based on new guidelines', time: '1 day ago', model: 'qwen3.6:latest', context: 'EDPB Guidelines 04/2026', approvalChain: 'Auto-applied by CPO' }
    ],
    status: 'active'
  },
  {
    id: 'ent-2',
    type: 'user',
    name: 'Sarah Jenkins',
    role: 'Privacy Analyst',
    organization: 'KIBO Compliance Ops',
    riskTier: 'Medium',
    riskScore: 48,
    accessLevel: 'L2 - Operational',
    jurisdictionScope: 'North America (PIPEDA, CCPA)',
    lastActivity: '15 mins ago',
    trustScore: 82,
    clearanceLevel: 'Confidential / Workflow Restricted',
    verificationStatus: 'Verified (MFA)',
    employmentStatus: 'Full-Time Active',
    delegatedAuthorities: ['DSAR Ingestion', 'Draft Consent Reviews'],
    roleHistory: [
      { date: '2025-03-01', action: 'Assigned Privacy Analyst', actor: 'Wael Hassan' }
    ],
    entitlements: [
      { id: 'ent-u2-1', system: 'DSAR Portal', dataset: 'Consumer Requests', workflow: 'DSAR Fullfilment', approval: 'DPO Peer Review', region: 'US/CA', dataType: 'PII', justification: 'Fulfilling consumer rights requests', legalBasis: 'CCPA Sec 1798.100 / PIPEDA Schedule 1', approvalHistory: 'Approved by Wael Hassan on 2025-03-02', expiration: '2027-03-01', lastUsage: '25 mins ago' }
    ],
    timeline: [
      { id: 't2-1', time: '2026-07-03 18:15', type: 'access', text: 'Exported 15 consumer record logs for DSAR request #902', legalBasis: 'CCPA Access Request', impact: 'Data Exported' },
      { id: 't2-2', time: '2026-07-03 16:30', type: 'policy', text: 'Requested temporary permission for EU region data view (Blocked)', legalBasis: 'N/A', impact: 'Access Policy Rejection' }
    ],
    riskSignals: [
      { label: 'Access Risk', score: 40, trend: 'up', desc: 'High frequency of consumer data exports due to recent backlog.' },
      { label: 'Compliance Deviation', score: 35, trend: 'up', desc: 'Attempted to access EU region records without active ticket association.' },
      { label: 'Behavioral Anomaly', score: 45, trend: 'up', desc: 'Login occurred from a domestic residential ISP instead of corporate VPN.' },
      { label: 'Privilege Escalation Risk', score: 30, trend: 'stable', desc: 'Normal range.' }
    ],
    aiInfluence: [
      { id: 'ai-inf-2', agent: 'DSAR Assistant Agent', suggestion: 'Auto-redacted phone numbers and clinical diagnostic tags in PDF export', time: '20 mins ago', model: 'qwen2.5-coder:32b', context: 'HIPAA Safe Harbor rules', approvalChain: 'Reviewed & approved by Sarah Jenkins' }
    ],
    status: 'active'
  },
  {
    id: 'ent-3',
    type: 'ai_agent',
    name: 'DSAR Agent (Auto-Redactor)',
    role: 'Automated Privacy Actor',
    organization: 'KIBO Agent Registry',
    riskTier: 'Medium',
    riskScore: 55,
    accessLevel: 'L3 - Delegated Write',
    jurisdictionScope: 'Multi-jurisdictional (GDPR, Law 25, CCPA)',
    lastActivity: '45 ms ago',
    trustScore: 91,
    clearanceLevel: 'Strict System Scoped',
    verificationStatus: 'Cryptographically Verified (SHA-256)',
    employmentStatus: 'System Service',
    delegatedAuthorities: ['Automated PII Redaction', 'Drafting DPA Audits'],
    modelVersion: 'qwen2.5-coder:32b (Fine-tuned)',
    promptTemplates: 'kibo-redaction-v4.2.system',
    allowedTools: ['PDF-Text-Extractor', 'Regex-PII-Scanner', 'Storage-Write-API'],
    allowedDataDomains: ['Customer Profiles (Archived)', 'DSAR Workspace Directory'],
    autonomyLevel: 'Level 3 - Conditional Autonomy (Requires human review on SPI)',
    hallucinationRisk: 'Low (2.4%)',
    failureHistory: [
      { date: '2026-06-20', error: 'Failed to extract text from scanned image (Handwritten)', action: 'Fell back to Human-in-the-loop queue' }
    ],
    entitlements: [
      { id: 'ent-a3-1', system: 'GCS Workspace Bucket', dataset: 'Temp Redactions', workflow: 'DSAR Processing', approval: 'System Rule Engine', region: 'Global', dataType: 'PII / SPI', justification: 'Removal of identifiers from request bundles', legalBasis: 'GDPR Art 15 / CCPA Right to Access', approvalHistory: 'System deployed approval', expiration: 'Indefinite', lastUsage: '1 min ago' }
    ],
    timeline: [
      { id: 'ta3-1', time: '2026-07-03 18:31', type: 'system', text: 'Redacted 24 occurrences of Social Security numbers from PDF file', legalBasis: 'GDPR Art 5 Data Minimization', impact: 'Storage updated' },
      { id: 'ta3-2', time: '2026-07-03 18:31', type: 'system', text: 'Flagged suspicious health classification tag as possible SPI requiring CPO sign-off', legalBasis: 'HIPAA Privacy Rule', impact: 'HITL Ticket Created' }
    ],
    riskSignals: [
      { label: 'Model Deviation Risk', score: 35, trend: 'stable', desc: 'Periodic check shows embedding semantic match score > 98%.' },
      { label: 'Autonomy Drift', score: 20, trend: 'stable', desc: 'No instances of executing actions without triggered workflows.' },
      { label: 'Tool Exploitation', score: 10, trend: 'stable', desc: 'Tool invocations match precise signature patterns.' }
    ],
    status: 'active'
  },
  {
    id: 'ent-4',
    type: 'vendor',
    name: 'FlokiNET Hosting Solutions',
    role: 'External Infrastructure Processor',
    organization: 'FlokiNET ISP (Iceland)',
    riskTier: 'High',
    riskScore: 78,
    accessLevel: 'L1 - Hard-walled Infrastructure',
    jurisdictionScope: 'Iceland (EEA / GDPR Compliant)',
    lastActivity: 'Continuous Sync',
    trustScore: 70,
    clearanceLevel: 'None (Data at rest encrypted)',
    contractualBasis: 'DPA-2025-V9 (Iceland Offshore Hosting)',
    dpaStatus: 'Compliant (Signed 2025-11-12)',
    allowedSystems: ['KIBO Backup Repository', 'Staging Mirror DB'],
    allowedWorkflows: ['Automated Mirror Backup Sync'],
    breachHistory: 'None reported. Minor downtime incident resolved in Feb 2026.',
    entitlements: [
      { id: 'ent-v4-1', system: 'Offshore Server Node', dataset: 'Encrypted Backups', workflow: 'Disaster Recovery Sync', approval: 'CPO Manual Sign-off', region: 'Iceland (EEA)', dataType: 'Encrypted SPI', justification: 'Secure off-grid privacy-first backup', legalBasis: 'GDPR Art. 32 (Security of Processing)', approvalHistory: 'Approved by Wael Hassan on 2025-11-12', expiration: '2028-11-12', lastUsage: '1 hour ago' }
    ],
    timeline: [
      { id: 'tv4-1', time: '2026-07-03 17:00', type: 'system', text: 'Transferred 1.2GB encrypted archive to Reykjavik datacenter', legalBasis: 'GDPR Art 32 / Disaster Preparedness', impact: 'Storage Updated' }
    ],
    riskSignals: [
      { label: 'Jurisdiction Risk', score: 85, trend: 'stable', desc: 'Icelandic hosting offers high sovereignty but subject to EU adequacy checks.' },
      { label: 'DPA Compliance Risk', score: 30, trend: 'stable', desc: 'Contract requires annual review in Nov 2026.' },
      { label: 'Access Isolation', score: 90, trend: 'stable', desc: 'No direct decrypted data access allowed. Key pair held locally.' }
    ],
    status: 'active'
  },
  {
    id: 'ent-5',
    type: 'regulator',
    name: 'Quebec CAI Officer (Auditor)',
    role: 'Regulatory External Auditor',
    organization: 'Commission d\'accès à l\'information du Québec',
    riskTier: 'Medium',
    riskScore: 50,
    accessLevel: 'L2 - Scoped Read-Only',
    jurisdictionScope: 'Quebec, Canada (Law 25)',
    lastActivity: '3 days ago',
    trustScore: 99,
    clearanceLevel: 'Statutory Right of Inspection',
    contractualBasis: 'Law 25 Sec 81 Statutory Audit Request',
    dpaStatus: 'N/A (Sovereign Regulator)',
    allowedSystems: ['Consent Management Telemetry', 'KIBO Decision Log Archive'],
    allowedWorkflows: ['Compliance Audit Logging'],
    breachHistory: 'N/A',
    entitlements: [
      { id: 'ent-r5-1', system: 'KIBO Log Registry', dataset: 'Quebec Consent Flags', workflow: 'Audit Review', approval: 'Statutory Right', region: 'Quebec, CA', dataType: 'De-identified Analytics', justification: 'Verification of Law 25 compliance protocols', legalBasis: 'Quebec Law 25 Sec. 81-83', approvalHistory: 'Registered on 2026-06-30', expiration: '2026-07-30 (Temporary)', lastUsage: '3 days ago' }
    ],
    timeline: [
      { id: 'tr5-1', time: '2026-06-30 11:20', type: 'access', text: 'Inspected 1,200 consent validation records from Quebec region', legalBasis: 'Law 25 Audit Request', impact: 'Read-Only Logs Viewed' }
    ],
    riskSignals: [
      { label: 'Data Leakage Risk', score: 65, trend: 'stable', desc: 'Providing raw logs to third parties, mitigated by hashing identifiers.' },
      { label: 'Jurisdiction Scope Match', score: 5, trend: 'stable', desc: 'Auditor strictly operating within Quebec boundary scope.' }
    ],
    status: 'active'
  }
];

// Graph Nodes layout calculations (statically mapped for stable, gorgeous layout)
const GRAPH_NODES = [
  { id: 'ent-1', label: 'Wael Hassan (CPO)', type: 'user', x: 250, y: 150 },
  { id: 'ent-2', label: 'Sarah Jenkins (Analyst)', type: 'user', x: 120, y: 280 },
  { id: 'ent-3', label: 'DSAR Agent (AI)', type: 'ai_agent', x: 260, y: 350 },
  { id: 'ent-4', label: 'FlokiNET (Vendor)', type: 'vendor', x: 420, y: 280 },
  { id: 'ent-5', label: 'Quebec CAI (Regulator)', type: 'regulator', x: 410, y: 100 },
  // Non-clickable context nodes representing Roles, Systems, Regulations
  { id: 'role-dpo', label: 'Role: DPO Office', type: 'role', x: 100, y: 80 },
  { id: 'sys-kibo', label: 'Sys: KIBO Core', type: 'system', x: 250, y: 250 },
  { id: 'jur-gdpr', label: 'Jur: GDPR (EU)', type: 'jurisdiction', x: 100, y: 180 },
  { id: 'jur-law25', label: 'Jur: Law 25 (QC)', type: 'jurisdiction', x: 420, y: 190 }
];

const GRAPH_EDGES = [
  { source: 'ent-1', target: 'role-dpo', label: 'Assigned' },
  { source: 'ent-1', target: 'sys-kibo', label: 'Controls' },
  { source: 'ent-1', target: 'jur-gdpr', label: 'Scope' },
  { source: 'ent-2', target: 'sys-kibo', label: 'Accesses' },
  { source: 'ent-2', target: 'jur-law25', label: 'Scope' },
  { source: 'ent-3', target: 'sys-kibo', label: 'Autonomous Work' },
  { source: 'ent-3', target: 'ent-2', label: 'Assists' },
  { source: 'ent-4', target: 'sys-kibo', label: 'Backups' },
  { source: 'ent-5', target: 'sys-kibo', label: 'Audits' },
  { source: 'ent-5', target: 'jur-law25', label: 'Enforces' }
];

export default function UserGovernanceCockpit() {
  const [entities, setEntities] = useState(INITIAL_ENTITIES);
  const [selectedEntityId, setSelectedEntityId] = useState('ent-1');
  const [activeTab, setActiveTab] = useState('identity');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Graph Filter state
  const [graphFilters, setGraphFilters] = useState({
    user: true,
    ai_agent: true,
    vendor: true,
    regulator: true,
    system: true,
    jurisdiction: true
  });

  // Permission Builder ABAC State
  const [rules, setRules] = useState([
    { id: 'R-1', text: 'Allow DSAR access only for EU residents, only for GDPR Article 15 cases, active workflow state, expires 48 hours.', active: true },
    { id: 'R-2', text: 'Require CPO dual-authorization for export of SPI or medical records exceeding 10 files.', active: true },
    { id: 'R-3', text: 'AI Agents are restricted to read-only metadata scanning on production database systems.', active: true }
  ]);
  const [newRule, setNewRule] = useState({ jurisdiction: 'GDPR', dataType: 'PII', system: 'KIBO Core', riskLimit: 'Medium', expiry: '48h', textRule: '' });

  // Bulk Operations State
  const [bulkAction, setBulkAction] = useState({ role: '', action: '', applied: false, report: '' });

  // Get currently active selected entity
  const selectedEntity = useMemo(() => {
    return entities.find(e => e.id === selectedEntityId) || entities[0];
  }, [entities, selectedEntityId]);

  // Compute overall stats
  const stats = useMemo(() => {
    return {
      activeUsers: entities.filter(e => e.type === 'user' && e.status === 'active').length,
      highRiskAccess: entities.filter(e => e.riskTier === 'High').length,
      vendors: entities.filter(e => e.type === 'vendor').length,
      regulators: entities.filter(e => e.type === 'regulator').length,
      aiAgents: entities.filter(e => e.type === 'ai_agent').length,
      pendingApprovals: 3 // Static demo state
    };
  }, [entities]);

  // Handle instant access revocation
  const handleRevoke = (id) => {
    setEntities(prev => prev.map(e => {
      if (e.id === id) {
        return {
          ...e,
          status: e.status === 'revoked' ? 'active' : 'revoked',
          riskScore: e.status === 'revoked' ? e.riskScore - 20 : 99,
          riskTier: e.status === 'revoked' ? 'Medium' : 'Critical'
        };
      }
      return e;
    }));
  };

  // Add a new ABAC rule
  const handleAddRule = (e) => {
    e.preventDefault();
    const compiledText = `Allow ${newRule.dataType} access under ${newRule.jurisdiction} for system [${newRule.system}] limited to ${newRule.riskLimit} risk levels, expires in ${newRule.expiry}.`;
    const newRuleObj = {
      id: `R-${rules.length + 1}`,
      text: newRule.textRule || compiledText,
      active: true
    };
    setRules(prev => [...prev, newRuleObj]);
    setNewRule({ jurisdiction: 'GDPR', dataType: 'PII', system: 'KIBO Core', riskLimit: 'Medium', expiry: '48h', textRule: '' });
  };

  // Trigger Bulk Action
  const handleBulkAction = (e) => {
    e.preventDefault();
    if (!bulkAction.action || !bulkAction.role) return;

    let targetCount = 0;
    setEntities(prev => prev.map(ent => {
      if (ent.type === bulkAction.role || (bulkAction.role === 'all')) {
        targetCount++;
        if (bulkAction.action === 'freeze') {
          return { ...ent, status: 'revoked', riskScore: 95 };
        } else if (bulkAction.action === 'mfa') {
          return { ...ent, verificationStatus: 'Verified (Enforced MFA)' };
        }
      }
      return ent;
    }));

    setBulkAction(prev => ({
      ...prev,
      applied: true,
      report: `Successfully executed [${prev.action.toUpperCase()}] on ${targetCount} matching actors. Affected components: User Workspace API gates.`
    }));

    setTimeout(() => {
      setBulkAction(prev => ({ ...prev, applied: false }));
    }, 5000);
  };

  // Filter nodes according to filters
  const filteredNodes = useMemo(() => {
    return GRAPH_NODES.filter(node => {
      if (node.type === 'role') return true; // always show context helper nodes
      return graphFilters[node.type] !== false;
    });
  }, [graphFilters]);

  const filteredEdges = useMemo(() => {
    const activeNodeIds = new Set(filteredNodes.map(n => n.id));
    return GRAPH_EDGES.filter(edge => activeNodeIds.has(edge.source) && activeNodeIds.has(edge.target));
  }, [filteredNodes]);

  return (
    <div className="flex-1 flex flex-col h-full bg-[#FAFAFA] overflow-hidden">
      
      {/* 1. TOP OVERVIEW SUMMARY PANEL */}
      <div className="grid grid-cols-6 gap-3 p-4 border-b border-[#E5E7EB] bg-white/80 backdrop-blur-xs">
        {[
          { label: 'Active Users', value: stats.activeUsers, color: 'text-emerald-700', icon: Users },
          { label: 'High Risk Access', value: stats.highRiskAccess, color: 'text-rose-700', icon: ShieldAlert },
          { label: 'External Vendors', value: stats.vendors, color: 'text-sky-700', icon: Globe },
          { label: 'Regulators Connected', value: stats.regulators, color: 'text-amber-700', icon: Shield },
          { label: 'AI Agents (Actors)', value: stats.aiAgents, color: 'text-purple-700', icon: Cpu },
          { label: 'Pending Approvals', value: stats.pendingApprovals, color: 'text-pink-400', icon: Clock }
        ].map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-gray-50 border border-[#E5E7EB] p-3 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-[#6B7280] font-bold uppercase tracking-wider">{stat.label}</p>
                <p className={`text-xl font-extrabold ${stat.color} mt-1`}>{stat.value}</p>
              </div>
              <Icon size={20} className="text-gray-500 opacity-60" />
            </div>
          );
        })}
      </div>

      <div className="flex-1 flex overflow-hidden">

        {/* 2. LEFT: IDENTITY RELATIONSHIP GRAPH */}
        <div className="w-[30%] bg-white border-r border-[#E5E7EB] flex flex-col overflow-hidden">
          {/* Panel Header & Filters */}
          <div className="p-3 border-b border-[#E5E7EB]">
            <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block mb-2">ACCESS IDENTITY GRAPH</span>
            <div className="flex items-center space-x-1.5 mb-2 bg-[#FAFAFA] border border-[#E5E7EB] px-2.5 py-1 rounded-md">
              <Search size={12} className="text-gray-500" />
              <input
                type="text"
                placeholder="Search graph..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  // Auto-focus matching entity if matched
                  const found = entities.find(ent => ent.name.toLowerCase().includes(e.target.value.toLowerCase()));
                  if (found) setSelectedEntityId(found.id);
                }}
                className="bg-transparent text-xs w-full outline-hidden text-[#111827] placeholder-gray-600"
              />
            </div>

            {/* Toggle filter pills */}
            <div className="flex flex-wrap gap-1 mt-2">
              {Object.keys(graphFilters).map((key) => (
                <button
                  key={key}
                  onClick={() => setGraphFilters(prev => ({ ...prev, [key]: !prev[key] }))}
                  className={`text-[9px] px-2 py-0.5 rounded-full border transition-all cursor-pointer ${
                    graphFilters[key]
                      ? 'bg-blue-600/20 text-blue-400 border-blue-500/40'
                      : 'bg-transparent text-gray-600 border-[#E5E7EB]'
                  }`}
                >
                  {key.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Canvas Map */}
          <div className="flex-1 relative overflow-hidden bg-[#F9FAFB] flex items-center justify-center">
            <svg className="w-full h-full" style={{ minHeight: '360px' }}>
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#1E294B" />
                </marker>
              </defs>

              {/* Edge Links */}
              {filteredEdges.map((edge, idx) => {
                const sourceNode = filteredNodes.find(n => n.id === edge.source);
                const targetNode = filteredNodes.find(n => n.id === edge.target);
                if (!sourceNode || !targetNode) return null;
                return (
                  <g key={idx}>
                    <line
                      x1={sourceNode.x}
                      y1={sourceNode.y}
                      x2={targetNode.x}
                      y2={targetNode.y}
                      stroke="#1E294B"
                      strokeWidth="1.5"
                      markerEnd="url(#arrow)"
                    />
                    <text
                      x={(sourceNode.x + targetNode.x) / 2}
                      y={(sourceNode.y + targetNode.y) / 2 - 4}
                      fill="#475569"
                      fontSize="7"
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {edge.label}
                    </text>
                  </g>
                );
              })}

              {/* Nodes */}
              {filteredNodes.map((node) => {
                const isFocused = node.id === selectedEntityId;
                let colorClass = 'fill-[#1E294B] stroke-[#334155]';
                let iconText = '👤';
                
                if (node.type === 'user') {
                  colorClass = isFocused ? 'fill-blue-900/60 stroke-blue-400' : 'fill-slate-800 stroke-slate-600';
                  iconText = '👤';
                } else if (node.type === 'ai_agent') {
                  colorClass = isFocused ? 'fill-purple-900/60 stroke-purple-400' : 'fill-purple-950/80 stroke-purple-800';
                  iconText = '🤖';
                } else if (node.type === 'vendor') {
                  colorClass = isFocused ? 'fill-sky-900/60 stroke-sky-400' : 'fill-sky-950/80 stroke-sky-800';
                  iconText = '🌐';
                } else if (node.type === 'regulator') {
                  colorClass = isFocused ? 'fill-amber-900/60 stroke-amber-400' : 'fill-amber-950/80 stroke-amber-800';
                  iconText = '🛡️';
                } else if (node.type === 'system') {
                  colorClass = 'fill-emerald-950/40 stroke-emerald-900';
                  iconText = '💽';
                } else if (node.type === 'jurisdiction') {
                  colorClass = 'fill-teal-950/40 stroke-teal-900';
                  iconText = '🗺️';
                }

                const isClickable = ['user', 'ai_agent', 'vendor', 'regulator'].includes(node.type);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onClick={() => isClickable && setSelectedEntityId(node.id)}
                    className={isClickable ? 'cursor-pointer group' : ''}
                  >
                    {/* Pulsing ring for selected focused node */}
                    {isFocused && (
                      <circle r="22" className="fill-none stroke-blue-500/40 stroke-1 animate-ping" />
                    )}
                    <circle r="16" className={`${colorClass} stroke-2 transition-all duration-300 group-hover:scale-110`} />
                    <text y="4" textAnchor="middle" className="text-xs pointer-events-none select-none">
                      {iconText}
                    </text>
                    <text
                      y="26"
                      textAnchor="middle"
                      fill={isFocused ? '#60A5FA' : '#94A3B8'}
                      fontSize="9"
                      fontWeight={isFocused ? 'bold' : 'normal'}
                      className="pointer-events-none select-none"
                    >
                      {node.label}
                    </text>
                  </g>
                );
              })}
            </svg>

            <div className="absolute bottom-2 right-2 bg-[#FAFAFA]/90 border border-[#E5E7EB] px-2 py-1 rounded text-[8px] text-gray-500 font-mono">
              Graph Coordinates: Real-time Access Edges
            </div>
          </div>

          {/* Simple List backup */}
          <div className="p-3 border-t border-[#E5E7EB]">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-2">LIST INDEX</span>
            <div className="space-y-1 max-h-36 overflow-y-auto">
              {entities.map(ent => (
                <button
                  key={ent.id}
                  onClick={() => setSelectedEntityId(ent.id)}
                  className={`w-full text-left px-2 py-1 text-[11px] rounded flex items-center justify-between cursor-pointer ${
                    ent.id === selectedEntityId ? 'bg-blue-600/10 border border-blue-500/20 text-blue-300' : 'text-[#6B7280] hover:bg-white'
                  }`}
                >
                  <span className="truncate">{ent.name}</span>
                  <span className={`text-[8px] uppercase px-1 rounded ${
                    ent.status === 'revoked' ? 'bg-rose-500/20 text-rose-700' : 'bg-slate-700/30 text-gray-500'
                  }`}>
                    {ent.status}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 3. CENTER: USER PROFILE WORKSPACE */}
        <div className="flex-1 flex flex-col bg-[#FAFAFA] overflow-y-auto">
          
          {/* Profile Header */}
          <div className="p-5 border-b border-[#E5E7EB] bg-white/40 flex items-start justify-between">
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="text-lg font-extrabold text-[#111827]">{selectedEntity.name}</span>
                <span className={`text-[9px] uppercase px-2 py-0.5 rounded-full font-bold border ${
                  selectedEntity.riskTier === 'High'
                    ? 'bg-rose-50 text-rose-700 border-rose-500/20'
                    : selectedEntity.riskTier === 'Medium'
                    ? 'bg-amber-50 text-amber-700 border-amber-500/20'
                    : 'bg-emerald-50 text-emerald-700 border-emerald-500/20'
                }`}>
                  {selectedEntity.riskTier} Risk
                </span>
                {selectedEntity.status === 'revoked' && (
                  <span className="text-[9px] bg-rose-950 text-rose-700 border border-rose-800/40 px-2 py-0.5 rounded-full font-bold uppercase">
                    Suspended / Revoked
                  </span>
                )}
              </div>
              <p className="text-xs text-blue-400 mt-1 font-mono">{selectedEntity.role} &bull; {selectedEntity.organization}</p>
              
              <div className="grid grid-cols-4 gap-x-6 gap-y-2 mt-4 text-[10px] text-[#6B7280]">
                <div>Jurisdiction Scope: <strong className="text-[#111827]">{selectedEntity.jurisdictionScope}</strong></div>
                <div>Access Level: <strong className="text-[#111827]">{selectedEntity.accessLevel}</strong></div>
                <div>Clearance: <strong className="text-[#111827]">{selectedEntity.clearanceLevel}</strong></div>
                <div>Trust Score: <strong className="text-[#111827]">{selectedEntity.trustScore}/100</strong></div>
                <div>Last Active: <strong className="text-[#111827]">{selectedEntity.lastActivity}</strong></div>
                <div>Security Verification: <strong className="text-[#111827]">{selectedEntity.verificationStatus}</strong></div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex space-x-2">
              <button
                onClick={() => handleRevoke(selectedEntity.id)}
                className={`text-[10px] font-bold px-3 py-1.5 rounded transition-all cursor-pointer flex items-center space-x-1 ${
                  selectedEntity.status === 'revoked'
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-[#111827]'
                    : 'bg-rose-600 hover:bg-rose-700 text-[#111827]'
                }`}
              >
                {selectedEntity.status === 'revoked' ? <CheckCircle size={12} /> : <XCircle size={12} />}
                <span>{selectedEntity.status === 'revoked' ? 'Re-Activate Access' : 'Instant Revoke Access'}</span>
              </button>
            </div>
          </div>

          {/* Profile Tabs */}
          <div className="border-b border-[#E5E7EB] bg-white/20 flex">
            {[
              { id: 'identity', label: 'Identity & Role' },
              { id: 'entitlements', label: 'Access Entitlements' },
              { id: 'timeline', label: 'Activity Timeline' },
              { id: 'risk', label: 'Risk Analytics' },
              { id: 'ai_influence', label: 'AI Influence Panel' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 text-xs font-bold transition-all border-b-2 cursor-pointer ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                    : 'border-transparent text-gray-500 hover:text-[#374151]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Workspaces */}
          <div className="p-5 flex-1 min-h-64">
            
            {/* TAB: IDENTITY & ROLE */}
            {activeTab === 'identity' && (
              <div className="space-y-6">
                <div className="bg-gray-50/40 border border-[#E5E7EB] p-4 rounded-xl">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block mb-3">Organizational Hierarchy & Integrity</span>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div className="space-y-1">
                      <p className="text-gray-500">Employment Status</p>
                      <p className="text-gray-200 font-bold">{selectedEntity.employmentStatus}</p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-gray-500">Identity Verification Gateway</p>
                      <p className="text-emerald-700 font-bold flex items-center space-x-1">
                        <CheckCircle size={12} className="inline mr-1" />
                        {selectedEntity.verificationStatus}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50/40 border border-[#E5E7EB] p-4 rounded-xl">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block mb-2">Delegated Authorities</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedEntity.delegatedAuthorities?.map((auth, idx) => (
                      <span key={idx} className="bg-slate-800 text-slate-300 text-[10px] font-mono px-2 py-1 rounded">
                        &bull; {auth}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-50/40 border border-[#E5E7EB] p-4 rounded-xl">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block mb-3">Role History Log</span>
                  <div className="space-y-2">
                    {selectedEntity.roleHistory?.map((hist, idx) => (
                      <div key={idx} className="text-xs flex items-center justify-between border-b border-[#E5E7EB] pb-2 last:border-0 last:pb-0">
                        <span className="text-[#6B7280]">{hist.date} - <strong className="text-[#111827]">{hist.action}</strong></span>
                        <span className="text-[10px] text-gray-500 font-mono">Approved: {hist.actor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: ACCESS ENTITLEMENTS */}
            {activeTab === 'entitlements' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest">Active System & Data Boundaries</span>
                  <button className="text-[9px] font-bold text-blue-400 hover:underline flex items-center space-x-1 cursor-pointer">
                    <Plus size={10} />
                    <span>Propose New Entitlement</span>
                  </button>
                </div>

                {selectedEntity.entitlements?.map((ent, idx) => (
                  <div key={idx} className="bg-gray-50 border border-[#E5E7EB] rounded-xl p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="bg-blue-900/40 text-blue-400 text-[9px] font-bold uppercase px-2 py-0.5 rounded border border-blue-800/40">
                          {ent.system} &bull; {ent.region}
                        </span>
                        <h4 className="text-sm font-extrabold text-[#111827] mt-2">{ent.dataset}</h4>
                      </div>
                      <span className="text-[10px] text-gray-500 font-mono">Expires: {ent.expiration}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-[11px] border-t border-[#E5E7EB] pt-2 text-[#6B7280]">
                      <div>
                        <p className="text-[9px] text-gray-500 uppercase font-bold">Justification</p>
                        <p className="text-[#374151] mt-0.5">{ent.justification}</p>
                      </div>
                      <div>
                        <p className="text-[9px] text-gray-500 uppercase font-bold">Legal / Compliance Basis</p>
                        <p className="text-emerald-700 font-bold mt-0.5">{ent.legalBasis}</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-gray-500 bg-[#F9FAFB] p-2 rounded border border-gray-900">
                      <span>Approval: <strong className="text-[#374151]">{ent.approvalHistory}</strong></span>
                      <span>Last Used: <strong className="text-[#374151]">{ent.lastUsage}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: ACTIVITY TIMELINE */}
            {activeTab === 'timeline' && (
              <div className="space-y-4">
                <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block mb-2">Immutable Governance Ledger</span>
                
                <div className="relative border-l border-[#E5E7EB] pl-4 ml-2 space-y-4">
                  {selectedEntity.timeline?.map((item, idx) => (
                    <div key={idx} className="relative">
                      {/* Timeline dot */}
                      <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 border border-[#090C15]" />
                      
                      <div className="bg-gray-50/40 border border-[#E5E7EB] p-3 rounded-lg">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="text-[#6B7280]">{item.time}</span>
                          <span className="text-blue-400 font-mono uppercase">{item.type}</span>
                        </div>
                        <p className="text-xs text-gray-200 mt-1">{item.text}</p>
                        <div className="flex justify-between text-[9px] text-gray-500 mt-2 border-t border-[#E5E7EB] pt-1">
                          <span>Legal Ground: {item.legalBasis}</span>
                          <span>Impact: {item.impact}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: RISK PROFILE */}
            {activeTab === 'risk' && (
              <div className="space-y-6">
                <div className="bg-gray-50/40 border border-[#E5E7EB] p-4 rounded-xl flex items-center justify-between">
                  <div>
                    <span className="text-[10px] text-[#6B7280] font-bold uppercase tracking-wider block">AGGREGATE RISK INDEX</span>
                    <p className="text-xs text-gray-500 mt-1">Weighted calculation of credentials, activity logs, and regulatory boundaries.</p>
                  </div>
                  <div className="text-center">
                    <span className={`text-4xl font-extrabold ${selectedEntity.riskScore > 70 ? 'text-rose-500' : selectedEntity.riskScore > 40 ? 'text-amber-500' : 'text-emerald-700'}`}>
                      {selectedEntity.riskScore}%
                    </span>
                    <p className="text-[9px] text-gray-500 uppercase tracking-widest mt-1">Risk Score</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {selectedEntity.riskSignals?.map((sig, idx) => (
                    <div key={idx} className="bg-gray-50 border border-[#E5E7EB] p-3.5 rounded-xl space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold text-[#111827]">{sig.label}</span>
                        <span className={`text-xs font-extrabold ${sig.score > 60 ? 'text-rose-700' : sig.score > 30 ? 'text-amber-700' : 'text-emerald-700'}`}>
                          {sig.score}/100
                        </span>
                      </div>
                      <div className="w-full bg-[#F9FAFB] h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${sig.score > 60 ? 'bg-rose-500' : sig.score > 30 ? 'bg-amber-500' : 'bg-emerald-400'}`}
                          style={{ width: `${sig.score}%` }}
                        />
                      </div>
                      <p className="text-[10px] text-[#6B7280] leading-relaxed">{sig.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: AI INFLUENCE PANEL */}
            {activeTab === 'ai_influence' && (
              <div className="space-y-4">
                <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block mb-2">Decision-making Co-pilot Logs</span>
                
                {selectedEntity.aiInfluence?.length > 0 ? (
                  selectedEntity.aiInfluence.map((inf, idx) => (
                    <div key={idx} className="bg-gray-50 border border-[#E5E7EB] rounded-xl p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center space-x-2">
                          <Cpu size={14} className="text-purple-700" />
                          <span className="text-xs font-bold text-[#111827]">{inf.agent}</span>
                        </div>
                        <span className="text-[10px] text-gray-500 font-mono">{inf.time}</span>
                      </div>

                      <div className="bg-[#FAFAFA] p-3 rounded border border-gray-900 text-xs text-[#374151]">
                        <p className="text-[9px] text-gray-500 font-bold uppercase tracking-wider mb-1">Suggested Prompt Action</p>
                        {inf.suggestion}
                      </div>

                      <div className="grid grid-cols-3 gap-2 text-[10px] text-gray-500">
                        <div>Model: <strong className="text-[#374151]">{inf.model}</strong></div>
                        <div>Context: <strong className="text-[#374151]">{inf.context}</strong></div>
                        <div>Chain: <strong className="text-[#374151]">{inf.approvalChain}</strong></div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500 text-xs">
                    No direct AI influence markers detected in this actor's workspace logs.
                  </div>
                )}
              </div>
            )}

          </div>

          {/* AI AGENT GOVERNANCE CARD (Conditional render when selected entity is an AI Agent) */}
          {selectedEntity.type === 'ai_agent' && (
            <div className="mx-5 mb-5 p-4 bg-purple-50/20 border border-purple-800/30 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cpu size={16} className="text-purple-700" />
                  <span className="text-xs font-extrabold text-[#111827] uppercase tracking-wider">AI Agent Controller Sandbox</span>
                </div>
                <span className="text-[10px] text-purple-700 bg-purple-900/25 px-2 py-0.5 rounded border border-purple-800/30">
                  Hallucination Risk: {selectedEntity.hallucinationRisk}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-xs text-[#374151]">
                <div className="bg-white/60 p-2.5 rounded border border-[#E5E7EB]">
                  <p className="text-[9px] text-gray-500 uppercase font-bold">Allowed Tools</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedEntity.allowedTools?.map((t, idx) => (
                      <span key={idx} className="bg-purple-900/30 text-purple-300 text-[8px] font-mono px-1.5 py-0.5 rounded">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-white/60 p-2.5 rounded border border-[#E5E7EB]">
                  <p className="text-[9px] text-gray-500 uppercase font-bold">Allowed Data Domains</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedEntity.allowedDataDomains?.map((d, idx) => (
                      <span key={idx} className="bg-slate-800 text-slate-300 text-[8px] font-mono px-1.5 py-0.5 rounded">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="bg-white/60 p-2.5 rounded border border-[#E5E7EB]">
                  <p className="text-[9px] text-gray-500 uppercase font-bold">Model Foundation</p>
                  <p className="text-[#111827] mt-1 text-[11px] font-mono">{selectedEntity.modelVersion}</p>
                </div>
              </div>
            </div>
          )}

          {/* EXTERNAL ACTOR GOVERNANCE CARD (Conditional render when selected entity is vendor or regulator) */}
          {(selectedEntity.type === 'vendor' || selectedEntity.type === 'regulator') && (
            <div className="mx-5 mb-5 p-4 bg-sky-50/20 border border-sky-800/30 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Globe size={16} className="text-sky-700" />
                  <span className="text-xs font-extrabold text-[#111827] uppercase tracking-wider">Third-Party Boundary Controls</span>
                </div>
                <span className="text-[10px] text-sky-700 bg-sky-900/25 px-2 py-0.5 rounded border border-sky-800/30">
                  DPA Status: {selectedEntity.dpaStatus || 'Statutory Basis'}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs text-[#374151]">
                <div className="bg-white/60 p-3 rounded border border-[#E5E7EB]">
                  <p className="text-[9px] text-gray-500 uppercase font-bold">Contract / Legal Authorization</p>
                  <p className="text-[#111827] mt-1 text-[11px] font-mono font-bold">{selectedEntity.contractualBasis}</p>
                </div>
                <div className="bg-white/60 p-3 rounded border border-[#E5E7EB]">
                  <p className="text-[9px] text-gray-500 uppercase font-bold">Allowed Workflows</p>
                  <p className="text-[#111827] mt-1 text-[11px]">{selectedEntity.allowedWorkflows?.join(', ')}</p>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* 4. RIGHT: ACCESS DECISION LAYER (Decision Panel) */}
        <div className="w-[30%] bg-white border-l border-[#E5E7EB] flex flex-col overflow-y-auto p-4 space-y-5">
          
          {/* Section: Permission Builder */}
          <div className="space-y-3">
            <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block">HYBRID ABAC/RBAC PERMISSION BUILDER</span>
            
            <form onSubmit={handleAddRule} className="bg-gray-50 border border-[#E5E7EB] p-3 rounded-xl space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="space-y-1">
                  <label className="text-[#6B7280]">Jurisdiction</label>
                  <select
                    value={newRule.jurisdiction}
                    onChange={(e) => setNewRule(prev => ({ ...prev, jurisdiction: e.target.value }))}
                    className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden cursor-pointer"
                  >
                    <option value="GDPR">GDPR (EU)</option>
                    <option value="Law 25">Law 25 (QC)</option>
                    <option value="CCPA">CCPA (CA)</option>
                    <option value="HIPAA">HIPAA (US)</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-[#6B7280]">Data Sensitivity</label>
                  <select
                    value={newRule.dataType}
                    onChange={(e) => setNewRule(prev => ({ ...prev, dataType: e.target.value }))}
                    className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden cursor-pointer"
                  >
                    <option value="PII">PII (Personal)</option>
                    <option value="SPI">SPI (Sensitive)</option>
                    <option value="Health Data">Health Records</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div className="space-y-1">
                  <label className="text-[#6B7280]">System Scope</label>
                  <input
                    type="text"
                    value={newRule.system}
                    onChange={(e) => setNewRule(prev => ({ ...prev, system: e.target.value }))}
                    className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden text-[10px]"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[#6B7280]">Access Expiry</label>
                  <input
                    type="text"
                    value={newRule.expiry}
                    onChange={(e) => setNewRule(prev => ({ ...prev, expiry: e.target.value }))}
                    className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden text-[10px]"
                  />
                </div>
              </div>

              <div className="space-y-1 text-[10px]">
                <label className="text-[#6B7280]">Natural Language Override (Optional)</label>
                <textarea
                  value={newRule.textRule}
                  onChange={(e) => setNewRule(prev => ({ ...prev, textRule: e.target.value }))}
                  placeholder="e.g. Allow DSAR read-only access only if CPO approves..."
                  className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden h-12 text-[10px]"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-[#111827] font-bold text-[10px] py-1.5 rounded transition-all cursor-pointer flex items-center justify-center space-x-1"
              >
                <Plus size={12} />
                <span>Deploy Compliance Policy</span>
              </button>
            </form>

            {/* List of active policies */}
            <div className="space-y-2 mt-2 max-h-48 overflow-y-auto">
              {rules.map((rule) => (
                <div key={rule.id} className="bg-gray-50/60 border border-[#E5E7EB] p-2.5 rounded-lg flex items-start justify-between">
                  <p className="text-[10px] text-[#374151] leading-relaxed pr-2">
                    <strong className="text-blue-400 font-mono block">{rule.id}</strong>
                    {rule.text}
                  </p>
                  <button
                    onClick={() => setRules(prev => prev.filter(r => r.id !== rule.id))}
                    className="text-gray-500 hover:text-rose-700 transition-colors cursor-pointer"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Section: Bulk Governance Operations */}
          <div className="space-y-3 pt-3 border-t border-[#E5E7EB]">
            <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block">BULK GOVERNANCE SYSTEM</span>
            
            <form onSubmit={handleBulkAction} className="bg-gray-50 border border-[#E5E7EB] p-3 rounded-xl space-y-3">
              <div className="space-y-1 text-[10px]">
                <label className="text-[#6B7280]">Target Role/Entity</label>
                <select
                  value={bulkAction.role}
                  onChange={(e) => setBulkAction(prev => ({ ...prev, role: e.target.value }))}
                  className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden text-[10px] cursor-pointer"
                >
                  <option value="">Select target...</option>
                  <option value="user">All Internal Users</option>
                  <option value="ai_agent">All AI Agents</option>
                  <option value="vendor">All External Vendors</option>
                  <option value="all">Every Risk Entity</option>
                </select>
              </div>

              <div className="space-y-1 text-[10px]">
                <label className="text-[#6B7280]">Governance Action</label>
                <select
                  value={bulkAction.action}
                  onChange={(e) => setBulkAction(prev => ({ ...prev, action: e.target.value }))}
                  className="w-full bg-[#FAFAFA] border border-[#E5E7EB] px-2 py-1 rounded text-[#111827] outline-hidden text-[10px] cursor-pointer"
                >
                  <option value="">Select action...</option>
                  <option value="freeze">Freeze access/credentials</option>
                  <option value="mfa">Enforce strict hardware MFA</option>
                  <option value="revoke">Revoke third-party syncs</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full bg-amber-600 hover:bg-amber-700 text-black font-bold text-[10px] py-1.5 rounded transition-all cursor-pointer flex items-center justify-center space-x-1"
              >
                <AlertTriangle size={12} className="text-black" />
                <span>Execute Bulk Control</span>
              </button>

              {bulkAction.applied && (
                <div className="bg-emerald-950/40 border border-emerald-800/40 p-2 rounded text-[10px] text-emerald-700">
                  {bulkAction.report}
                </div>
              )}
            </form>
          </div>

          {/* Section: Natural Language Query Sandbox */}
          <div className="space-y-3 pt-3 border-t border-[#E5E7EB]">
            <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block font-mono">NATURAL LANGUAGE COCKPIT QUERY</span>
            <div className="bg-gray-50 border border-[#E5E7EB] p-2.5 rounded-xl space-y-2">
              <div className="flex items-center space-x-2 bg-[#FAFAFA] px-2 py-1 border border-[#E5E7EB] rounded">
                <input
                  type="text"
                  placeholder="e.g. Who accessed health data in last 7 days?"
                  className="bg-transparent text-[10px] w-full outline-hidden text-[#111827] placeholder-gray-600"
                />
                <button type="button" className="text-blue-400 hover:text-blue-300 cursor-pointer">
                  <Send size={10} />
                </button>
              </div>
              <div className="space-y-1">
                <p className="text-[8px] text-gray-500 uppercase font-bold">Suggested Quick Queries</p>
                <button
                  onClick={() => setSearchQuery('vendor')}
                  className="block text-left text-[9px] text-blue-400 hover:underline cursor-pointer"
                >
                  &bull; "List high-risk vendors with active access"
                </button>
                <button
                  onClick={() => setSearchQuery('DSAR Agent')}
                  className="block text-left text-[9px] text-blue-400 hover:underline cursor-pointer"
                >
                  &bull; "Show AI agents with write permissions"
                </button>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
