import React, { useState, useRef } from 'react';
import {
  Inbox, Search, Bell, Zap, User, ChevronRight, ChevronDown,
  AlertTriangle, Clock, Shield, FileText, CheckCircle, XCircle, AlertOctagon,
  MessageSquare, Paperclip, Tag, Filter, Plus, MoreHorizontal,
  Send, Edit, Trash2, Archive, Globe, Lock, Database, Activity, Terminal, BookOpen,
  Download, Upload, Link, Check, Calendar, Sparkles, Brain, Server,
  ExternalLink, Layers, Hash, UserCheck
} from 'lucide-react';

const CASES = [
  {
    id: 'PRIV-2026-0847',
    subject: 'GDPR Article 15 — Access Request: Marketing Profiling Data',
    type: 'DSAR', subtype: 'Access',
    requester: 'Marie-Claire Fontaine', org: 'Individual', email: 'mc.fontaine@example.fr',
    jurisdiction: 'EU/GDPR', flag: '🇪🇺',
    risk: 'High', priority: 'Urgent',
    sla: { remaining: '2d 4h', status: 'warning', percent: 72 }, due: '2026-07-05',
    stage: 'Data Discovery', assigned: 'Waël Hassan', aiConfidence: 94,
    unread: true, attachments: 3, lastActivity: '18m ago', notes: 4, replies: 2, tags: ['gdpr','marketing','profiling'],
    regulation: ['GDPR Art.15','EDPB 01/2022'], systems: ['CRM','Analytics','Advertising'],
    status: 'In Progress', created: '2026-07-01 09:14',
    aiSummary: 'Customer submitted a GDPR Article 15 access request concerning marketing profiling data. Identity verification completed. CRM, Analytics and Advertising systems are impacted. Estimated completion 6 business days.',
    timeline: [
      { time: '2026-07-01 09:14', type: 'created', actor: 'System', text: 'Case created via web portal' },
      { time: '2026-07-01 10:02', type: 'assignment', actor: 'Kibo AI', text: 'Auto-assigned to Waël Hassan (CPO)' },
      { time: '2026-07-01 14:15', type: 'system', actor: 'Identity Agent', text: 'Identity verified. Confidence: 97%' },
      { time: '2026-07-02 09:00', type: 'note', actor: 'Waël Hassan', text: 'Initiated data discovery across CRM and Analytics systems' },
      { time: '2026-07-03 08:45', type: 'automation', actor: 'Discovery Agent', text: 'Found 1,247 records in Salesforce CRM matching requester profile' },
    ],
    workflow: ['Intake','Identity Verification','Data Discovery','Legal Review','Draft Response','Approval','Send','Close'],
    currentStep: 2,
    evidence: [
      { name: 'identity_verification.pdf', size: '245 KB', type: 'Identity', status: 'verified', added: '2026-07-01' },
      { name: 'crm_export_1247_records.xlsx', size: '1.2 MB', type: 'Data Export', status: 'pending_review', added: '2026-07-03' },
    ],
    messages: [
      { id: 1, from: 'Marie-Claire Fontaine', type: 'customer', time: '2026-07-01 09:14', body: 'I am submitting a formal request under GDPR Article 15 for access to all personal data you hold about me, particularly any profiling data used for marketing campaigns.' },
      { id: 2, from: 'Kibo AI', type: 'ai', time: '2026-07-01 10:02', body: 'Auto-acknowledgement sent. 30-day SLA clock started. Identity verification request queued.' },
      { id: 3, from: 'Waël Hassan', type: 'note', time: '2026-07-02 09:00', body: 'INTERNAL: Requested IT to run discovery query on Salesforce. Also checking Analytics platform for ad-targeting segments.' },
      { id: 4, from: 'Marie-Claire Fontaine', type: 'customer', time: '2026-07-02 14:22', body: 'I also want to include any data shared with third-party advertising partners in the scope of my request.' },
    ],
  },
  {
    id: 'PRIV-2026-0846',
    subject: 'Quebec Law 25 — Deletion Request: Account & Purchase History',
    type: 'DSAR', subtype: 'Deletion',
    requester: 'Jean-Paul Tremblay', org: 'Individual', email: 'jp.tremblay@example.qc.ca',
    jurisdiction: 'CA/Law25', flag: '🇨🇦',
    risk: 'Medium', priority: 'High',
    sla: { remaining: '8d 12h', status: 'ok', percent: 35 }, due: '2026-07-12',
    stage: 'Legal Review', assigned: 'Legal Team', aiConfidence: 88,
    unread: true, attachments: 1, lastActivity: '2h ago', notes: 2, replies: 3, tags: ['law25','deletion','quebec'],
    regulation: ['Law 25 Art.28','Quebec CAI'], systems: ['E-Commerce','CRM','Data Warehouse'],
    status: 'In Progress', created: '2026-07-01 14:30',
    aiSummary: 'Quebec Law 25 deletion request for account and purchase history. Legal team reviewing whether data retention obligations override deletion right.',
    timeline: [
      { time: '2026-07-01 14:30', type: 'created', actor: 'System', text: 'Case received via email' },
      { time: '2026-07-01 15:00', type: 'assignment', actor: 'Kibo AI', text: 'Routed to Legal Team for Law 25 assessment' },
      { time: '2026-07-02 11:00', type: 'note', actor: 'Legal Team', text: 'Reviewing tax record retention obligations (7 years) vs deletion right' },
    ],
    workflow: ['Intake','Identity Verification','Scope Assessment','Legal Review','Deletion Execution','Confirmation','Close'],
    currentStep: 3, evidence: [], messages: [
      { id: 1, from: 'Jean-Paul Tremblay', type: 'customer', time: '2026-07-01 14:30', body: 'Je demande la suppression de toutes mes donnees personnelles incluant mon compte et historique d\'achats.' },
      { id: 2, from: 'Kibo AI', type: 'ai', time: '2026-07-01 15:00', body: 'Request triaged. Law 25 deletion workflow initiated. 30-day response window applies.' },
    ],
  },
  {
    id: 'PRIV-2026-0845',
    subject: 'Regulator Inquiry — OPC Investigation File #2026-IR-448',
    type: 'Regulator Request', subtype: 'Investigation',
    requester: 'Office of the Privacy Commissioner', org: 'OPC Canada', email: 'investigations@priv.gc.ca',
    jurisdiction: 'CA/PIPEDA', flag: '🇨🇦',
    risk: 'Critical', priority: 'Urgent',
    sla: { remaining: '12d 0h', status: 'ok', percent: 15 }, due: '2026-07-15',
    stage: 'Evidence Preparation', assigned: 'Waël Hassan', aiConfidence: 99,
    unread: false, attachments: 7, lastActivity: '1d ago', notes: 8, replies: 5, tags: ['opc','regulator','investigation','critical'],
    regulation: ['PIPEDA S.11','PIPEDA S.7.3'], systems: ['All Systems'],
    status: 'Escalated', created: '2026-06-28 16:00',
    aiSummary: 'Formal OPC investigation regarding a PIPEDA complaint. Evidence package due July 15. Legal counsel engaged. Risk level: Critical.',
    timeline: [
      { time: '2026-06-28 16:00', type: 'created', actor: 'System', text: 'OPC inquiry received via registered mail' },
      { time: '2026-06-29 09:00', type: 'escalation', actor: 'Waël Hassan', text: 'Escalated to executive leadership. Legal counsel retained.' },
    ],
    workflow: ['Receipt','Legal Counsel Retained','Evidence Collection','Evidence Preparation','Legal Review','Submission','Response','Close'],
    currentStep: 3, evidence: [], messages: [],
  },
  {
    id: 'PRIV-2026-0844',
    subject: 'PHIPA Breach Notification — Unauthorized PHI Access (Clinical)',
    type: 'Privacy Incident', subtype: 'Breach',
    requester: 'Clinical IT Security', org: 'Kids Help Phone Clinical', email: 'security@khp-clinical.ca',
    jurisdiction: 'CA/PHIPA', flag: '🇨🇦',
    risk: 'Critical', priority: 'Urgent',
    sla: { remaining: '0d 6h', status: 'critical', percent: 97 }, due: '2026-07-03',
    stage: 'Regulatory Notification', assigned: 'Waël Hassan', aiConfidence: 97,
    unread: true, attachments: 5, lastActivity: '35m ago', notes: 12, replies: 8, tags: ['phipa','breach','phi','critical'],
    regulation: ['PHIPA S.12','IPC Ontario'], systems: ['Clinical EMR','Patient Portal'],
    status: 'Escalated', created: '2026-07-02 22:00',
    aiSummary: 'Suspected unauthorized access to PHI in clinical EMR. Approximately 340 patient records potentially exposed. PHIPA 72-hour notification window closes in 6 hours. Immediate IPC Ontario notification required.',
    timeline: [
      { time: '2026-07-02 22:00', type: 'created', actor: 'Security Team', text: 'Incident detected via SIEM alert.' },
      { time: '2026-07-02 22:15', type: 'escalation', actor: 'Kibo AI', text: 'CRITICAL: PHIPA 72h window triggered. Auto-escalated to CPO.' },
      { time: '2026-07-03 06:00', type: 'automation', actor: 'Compliance Agent', text: 'WARNING: 6 hours remaining before mandatory IPC notification deadline.' },
    ],
    workflow: ['Detection','Containment','RROSH Assessment','Documentation','Regulatory Notification','Individual Notification','Remediation','Post-Incident Review'],
    currentStep: 4, evidence: [], messages: [],
  },
  {
    id: 'PRIV-2026-0843',
    subject: 'Vendor Privacy Assessment — Salesforce Marketing Cloud Renewal',
    type: 'Vendor Review', subtype: 'DPIA',
    requester: 'IT Procurement', org: 'Kids Help Phone', email: 'procurement@khp.ca',
    jurisdiction: 'CA/PIPEDA + Law25', flag: '🇨🇦',
    risk: 'Medium', priority: 'Normal',
    sla: { remaining: '14d 0h', status: 'ok', percent: 10 }, due: '2026-07-17',
    stage: 'PIA Documentation', assigned: 'Privacy Analyst', aiConfidence: 82,
    unread: false, attachments: 2, lastActivity: '3d ago', notes: 3, replies: 1, tags: ['vendor','salesforce','dpia'],
    regulation: ['PIPEDA Principle 4.1','Law 25 Art.12'], systems: ['Marketing Cloud','Email Platform'],
    status: 'In Progress', created: '2026-06-28 10:00',
    aiSummary: 'Vendor privacy assessment for Salesforce Marketing Cloud renewal. Cross-border data transfers to US require adequacy assessment under Law 25.',
    timeline: [],
    workflow: ['Request','Scoping','Questionnaire Sent','PIA Documentation','Legal Review','Approval','Close'],
    currentStep: 3, evidence: [], messages: [],
  },
];

const SIDEBAR = [
  { section: 'My Work', items: [
    { id: 'inbox', label: 'Inbox', icon: Inbox, count: 3, dot: 'bg-blue-500' },
    { id: 'assigned', label: 'Assigned to Me', icon: User, count: 5 },
    { id: 'my_queue', label: 'My Queue', icon: Layers, count: 8 },
  ]},
  { section: 'Status', items: [
    { id: 'urgent', label: 'Urgent', icon: AlertOctagon, count: 2, dot: 'bg-rose-500' },
    { id: 'pending_approval', label: 'Pending Approval', icon: Clock, count: 4 },
    { id: 'awaiting_customer', label: 'Awaiting Customer', icon: User, count: 6 },
    { id: 'awaiting_legal', label: 'Awaiting Legal', icon: Shield, count: 3 },
    { id: 'escalated', label: 'Escalated', icon: AlertTriangle, count: 2, dot: 'bg-amber-400' },
  ]},
  { section: 'Request Types', items: [
    { id: 'dsar', label: 'DSAR', icon: FileText, count: 12 },
    { id: 'deletion', label: 'Deletion', icon: Trash2, count: 5 },
    { id: 'regulator', label: 'Regulator Requests', icon: Globe, count: 2 },
    { id: 'vendor', label: 'Vendor Reviews', icon: Database, count: 7 },
    { id: 'incidents', label: 'Privacy Incidents', icon: AlertOctagon, count: 3 },
    { id: 'pia', label: 'PIA / DPIA', icon: Shield, count: 4 },
  ]},
  { section: 'Smart Views', items: [
    { id: 'high_risk', label: 'High Risk', icon: AlertTriangle, count: 4, dot: 'bg-rose-500' },
    { id: 'expiring', label: 'Expiring Today', icon: Clock, count: 2, dot: 'bg-amber-400' },
    { id: 'gdpr', label: 'GDPR Requests', icon: Globe, count: 8 },
    { id: 'overdue', label: 'Overdue', icon: XCircle, count: 1, dot: 'bg-rose-500' },
  ]},
  { section: 'Archive', items: [
    { id: 'archived', label: 'Archived', icon: Archive, count: 247 },
  ]},
];

const CASE_TABS = ['Overview','Timeline','Replies','Evidence','Workflow','Knowledge','Automation'];

const RiskBadge = ({ risk }) => {
  const m = { Critical:'bg-rose-500/15 text-rose-400 border-rose-500/30', High:'bg-orange-500/15 text-orange-400 border-orange-500/30', Medium:'bg-amber-500/15 text-amber-400 border-amber-500/30', Low:'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' };
  return <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${m[risk]||m.Medium}`}>{risk}</span>;
};

const SLABar = ({ sla }) => {
  const c = sla.status==='critical'?'bg-rose-500':sla.status==='warning'?'bg-amber-400':'bg-emerald-500';
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between text-[8px]">
        <span className={sla.status==='critical'?'text-rose-400 font-bold animate-pulse':'text-gray-500'}>{sla.remaining}</span>
        <span className="text-gray-600">{sla.percent}%</span>
      </div>
      <div className="h-1 bg-[#1E294B] rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${c}`} style={{width:`${sla.percent}%`}} />
      </div>
    </div>
  );
};

const TypeBadge = ({ type }) => {
  const m = { 'DSAR':'bg-blue-500/10 text-blue-400', 'Vendor Review':'bg-purple-500/10 text-purple-400', 'Regulator Request':'bg-amber-500/10 text-amber-400', 'Privacy Incident':'bg-rose-500/10 text-rose-400' };
  return <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${m[type]||'bg-gray-500/10 text-gray-400'}`}>{type}</span>;
};

const TLIcon = ({ type }) => {
  const m = { created:{Icon:Plus,c:'text-blue-400 bg-blue-500/10 border-blue-500/20'}, assignment:{Icon:User,c:'text-purple-400 bg-purple-500/10 border-purple-500/20'}, note:{Icon:Edit,c:'text-amber-400 bg-amber-500/10 border-amber-500/20'}, system:{Icon:Terminal,c:'text-gray-400 bg-gray-500/10 border-gray-500/20'}, automation:{Icon:Zap,c:'text-blue-300 bg-blue-500/10 border-blue-500/20'}, escalation:{Icon:AlertTriangle,c:'text-rose-400 bg-rose-500/10 border-rose-500/20'} };
  const {Icon,c} = m[type]||m.system;
  return <div className={`w-6 h-6 rounded-full border flex items-center justify-center shrink-0 ${c}`}><Icon size={10}/></div>;
};

export default function PrivacyInbox() {
  const [view, setView] = useState('inbox');
  const [sel, setSel] = useState(CASES[0]);
  const [tab, setTab] = useState('Overview');
  const [q, setQ] = useState('');
  const [replyText, setReplyText] = useState('');
  const [replyMode, setReplyMode] = useState('reply');
  const [expanded, setExpanded] = useState({'My Work':true,'Status':true,'Request Types':true,'Smart Views':false,'Archive':false});
  const toggle = s => setExpanded(p=>({...p,[s]:!p[s]}));

  const cases = q ? CASES.filter(c=>c.subject.toLowerCase().includes(q.toLowerCase())||c.id.toLowerCase().includes(q.toLowerCase())||c.requester.toLowerCase().includes(q.toLowerCase())) : CASES;

  return (
    <div className="flex bg-[#060912] text-white font-sans overflow-hidden" style={{height:'82vh'}}>

      {/* SIDEBAR */}
      <div className="w-52 shrink-0 bg-[#0A0F1E] border-r border-[#1E294B] flex flex-col overflow-y-auto">
        <div className="p-3 border-b border-[#1E294B] space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center"><Shield size={12} className="text-white"/></div>
              <span className="text-[10px] font-extrabold text-white uppercase tracking-wider">Privacy Ops</span>
            </div>
            <button className="relative text-gray-400 hover:text-white cursor-pointer"><Bell size={13}/><span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 bg-rose-500 rounded-full"/></button>
          </div>
          <div className="relative">
            <Search size={10} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500"/>
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search cases..." className="w-full bg-[#0E1325] border border-[#1E294B] rounded-lg pl-7 pr-2 py-1.5 text-[10px] text-gray-300 placeholder-gray-600 focus:outline-none focus:border-blue-500/50"/>
          </div>
        </div>
        <div className="px-3 pt-2.5 pb-1">
          <button className="w-full flex items-center justify-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold py-1.5 rounded-lg transition-all cursor-pointer"><Plus size={10}/><span>New Case</span></button>
        </div>
        <nav className="flex-1 px-2 py-2 space-y-0.5">
          {SIDEBAR.map(({section,items})=>(
            <div key={section} className="space-y-0.5">
              <button onClick={()=>toggle(section)} className="w-full flex items-center justify-between px-2 py-1.5 text-[8px] font-bold uppercase tracking-widest text-gray-600 hover:text-gray-400 transition-colors cursor-pointer">
                <span>{section}</span>
                {expanded[section]?<ChevronDown size={8}/>:<ChevronRight size={8}/>}
              </button>
              {expanded[section]&&items.map(item=>{
                const Icon=item.icon; const active=view===item.id;
                return <button key={item.id} onClick={()=>setView(item.id)} className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-[10px] cursor-pointer transition-all group ${active?'bg-blue-600/20 text-blue-300':'text-gray-400 hover:text-gray-200 hover:bg-white/5'}`}>
                  <div className="flex items-center space-x-2">
                    {item.dot&&<span className={`w-1.5 h-1.5 rounded-full ${item.dot}`}/>}
                    <Icon size={11}/><span className="truncate">{item.label}</span>
                  </div>
                  {item.count>0&&<span className={`text-[8px] font-bold px-1.5 py-0.5 rounded-full ${active?'bg-blue-500/30 text-blue-300':'bg-white/8 text-gray-500'}`}>{item.count}</span>}
                </button>;
              })}
            </div>
          ))}
        </nav>
        <div className="p-3 border-t border-[#1E294B]">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-[10px] font-bold">WH</div>
            <div className="flex-1 min-w-0"><div className="text-[9px] font-bold text-white truncate">Waël Hassan</div><div className="text-[8px] text-gray-500 truncate">Chief Privacy Officer</div></div>
          </div>
        </div>
      </div>

      {/* CASE LIST */}
      <div className="w-80 shrink-0 border-r border-[#1E294B] flex flex-col overflow-hidden">
        <div className="p-3 border-b border-[#1E294B] flex items-center justify-between bg-[#0A0F1E]/60">
          <div><h2 className="text-[11px] font-extrabold text-white uppercase tracking-wider">Inbox</h2><p className="text-[8px] text-gray-500">{cases.length} cases · 3 unread</p></div>
          <div className="flex items-center space-x-1">
            <button className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer"><Filter size={12}/></button>
            <button className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 cursor-pointer"><MoreHorizontal size={12}/></button>
          </div>
        </div>
        <div className="mx-2 mt-2 p-2 rounded-lg bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 cursor-pointer hover:border-blue-400/40 transition-all">
          <div className="flex items-center space-x-1.5"><Sparkles size={10} className="text-blue-400"/><span className="text-[9px] text-blue-300 font-medium">AI Search: natural language queries...</span></div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1.5 pb-4">
          {cases.map(c=>{
            const isSelected=sel?.id===c.id;
            return <div key={c.id} onClick={()=>{setSel(c);setTab('Overview');}} className={`p-3 rounded-xl border cursor-pointer transition-all group space-y-2 ${isSelected?'bg-blue-600/15 border-blue-500/50 ring-1 ring-blue-500/20':'bg-[#0E1325] border-[#1E294B] hover:border-gray-500/50 hover:bg-white/3'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1.5">
                  {c.unread&&<span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0"/>}
                  <span className="text-[8px] font-mono text-gray-500">{c.id}</span>
                  <TypeBadge type={c.type}/>
                </div>
                <span className="text-[7px] text-gray-600">{c.lastActivity}</span>
              </div>
              <p className={`text-[10px] leading-snug font-semibold ${c.unread?'text-white':'text-gray-300'}`}>{c.subject}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1"><span className="text-[9px]">{c.flag}</span><span className="text-[9px] text-gray-400 truncate max-w-[110px]">{c.requester}</span></div>
                <RiskBadge risk={c.risk}/>
              </div>
              <SLABar sla={c.sla}/>
              <div className="flex items-center justify-between">
                <span className="text-[8px] text-blue-400 font-mono">{c.stage}</span>
                <div className="flex items-center space-x-2 text-[8px] text-gray-600">
                  {c.attachments>0&&<span className="flex items-center space-x-0.5"><Paperclip size={8}/><span>{c.attachments}</span></span>}
                  {c.notes>0&&<span className="flex items-center space-x-0.5"><Hash size={8}/><span>{c.notes}</span></span>}
                  {c.replies>0&&<span className="flex items-center space-x-0.5"><MessageSquare size={8}/><span>{c.replies}</span></span>}
                </div>
              </div>
              <div className="hidden group-hover:flex items-center space-x-1 pt-1 border-t border-[#1E294B]/50">
                {['Reply','Note','Assign','Escalate'].map(a=><button key={a} className="text-[8px] text-gray-400 hover:text-blue-400 px-1.5 py-0.5 rounded hover:bg-blue-500/10 transition-all cursor-pointer">{a}</button>)}
              </div>
            </div>;
          })}
        </div>
      </div>

      {/* CASE WORKSPACE */}
      {sel?(
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          {/* Header */}
          <div className="bg-[#0A0F1E] border-b border-[#1E294B] px-5 py-3 space-y-2">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0 space-y-1">
                <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                  <span className="text-[9px] font-mono text-gray-500">{sel.id}</span>
                  <TypeBadge type={sel.type}/><RiskBadge risk={sel.risk}/>
                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${sel.status==='Escalated'?'bg-rose-500/10 text-rose-400':sel.status==='In Progress'?'bg-blue-500/10 text-blue-400':'bg-gray-500/10 text-gray-400'}`}>{sel.status}</span>
                  <span className="text-[9px]">{sel.flag}</span><span className="text-[9px] text-gray-500">{sel.jurisdiction}</span>
                </div>
                <h1 className="text-sm font-bold text-white leading-snug">{sel.subject}</h1>
              </div>
              <div className="flex items-center space-x-1 shrink-0">
                {['Reply','Note','Escalate','Close'].map((a,i)=><button key={a} className={`px-2.5 py-1.5 rounded-lg text-[10px] font-bold transition-all cursor-pointer border ${i===0?'bg-blue-600 hover:bg-blue-500 text-white border-blue-600':'bg-transparent hover:bg-white/5 text-gray-300 border-[#1E294B]'}`}>{a}</button>)}
                <button className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 border border-[#1E294B] cursor-pointer"><MoreHorizontal size={13}/></button>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-[9px] text-gray-500 flex-wrap gap-y-1">
              <span className="flex items-center space-x-1"><User size={9}/><span>{sel.requester}</span></span>
              <span className="flex items-center space-x-1"><Calendar size={9}/><span>Due: {sel.due}</span></span>
              <span className={`flex items-center space-x-1 ${sel.sla.status==='critical'?'text-rose-400 font-bold animate-pulse':''}`}><Clock size={9}/><span>{sel.sla.remaining} remaining</span></span>
              <span className="flex items-center space-x-1"><User size={9}/><span>Assigned: {sel.assigned}</span></span>
              <span className="flex items-center space-x-1"><Brain size={9}/><span className="text-blue-400">AI: {sel.aiConfidence}%</span></span>
              <div className="flex items-center space-x-1">
                {sel.regulation.map(r=><span key={r} className="text-[8px] bg-purple-500/10 text-purple-400 px-1.5 py-0.5 rounded border border-purple-500/20">{r}</span>)}
              </div>
            </div>
          </div>
          {/* Tabs */}
          <div className="border-b border-[#1E294B] bg-[#0A0F1E]/50 px-5 flex overflow-x-auto">
            {CASE_TABS.map(t=><button key={t} onClick={()=>setTab(t)} className={`px-4 py-2.5 text-[10px] font-bold whitespace-nowrap transition-all cursor-pointer border-b-2 -mb-px ${tab===t?'border-blue-500 text-blue-400':'border-transparent text-gray-500 hover:text-gray-300'}`}>{t}</button>)}
          </div>
          {/* Content */}
          <div className="flex-1 overflow-y-auto">

            {tab==='Overview'&&(
              <div className="p-5 space-y-4">
                <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl p-4 space-y-2">
                  <div className="flex items-center space-x-2"><Brain size={13} className="text-blue-400"/><span className="text-[10px] font-bold text-blue-300 uppercase tracking-wider">AI Case Summary</span><span className="text-[8px] text-blue-400/70 font-mono">Confidence: {sel.aiConfidence}%</span></div>
                  <p className="text-xs text-gray-300 leading-relaxed">{sel.aiSummary}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-3">
                    <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Case Details</h3>
                    {[['Status',sel.status,true],['Type',`${sel.type} — ${sel.subtype}`],['Jurisdiction',sel.jurisdiction],['Risk',sel.risk],['Priority',sel.priority],['Created',sel.created],['Due',sel.due],['Assigned',sel.assigned],['Stage',sel.stage]].map(([l,v,h])=>(
                      <div key={l} className="flex justify-between text-xs"><span className="text-gray-500 shrink-0">{l}</span><span className={`text-right font-medium ml-2 ${h?'text-blue-300':'text-gray-300'}`}>{v}</span></div>
                    ))}
                  </div>
                  <div className="space-y-3">
                    <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-2">
                      <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Impacted Systems</h3>
                      <div className="flex flex-wrap gap-1.5">
                        {sel.systems.map(s=><span key={s} className="text-[9px] bg-[#151C33] border border-[#1E294B] text-gray-300 px-2 py-1 rounded-lg flex items-center space-x-1"><Server size={8} className="text-blue-400"/><span>{s}</span></span>)}
                      </div>
                    </div>
                    <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-2">
                      <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">SLA Status</h3>
                      <SLABar sla={sel.sla}/>
                      <p className={`text-[9px] ${sel.sla.status==='critical'?'text-rose-400 font-bold':''}`}>{sel.sla.remaining} · {sel.sla.percent}% elapsed</p>
                    </div>
                    <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-2">
                      <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Tags</h3>
                      <div className="flex flex-wrap gap-1">{sel.tags.map(t=><span key={t} className="text-[8px] font-mono bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded">#{t}</span>)}</div>
                    </div>
                  </div>
                </div>
                {/* AI Recommended Actions */}
                <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-3">
                  <div className="flex items-center space-x-2"><Sparkles size={13} className="text-amber-400"/><h3 className="text-[10px] font-bold text-white uppercase tracking-wider">AI Recommended Actions</h3></div>
                  <div className="grid grid-cols-2 gap-3">
                    {[{step:'Next Step',action:'Complete Data Discovery',confidence:'97%',reason:'Identity verified. CRM export ready.',legal:sel.regulation[0],duration:'~12 min',col:'emerald'},{step:'Parallel',action:'Notify Legal Team',confidence:'89%',reason:'Third-party advertising scope requires legal review.',legal:sel.regulation[0],duration:'~2 min',col:'blue'}].map((rec,i)=>(
                      <div key={i} className={`border rounded-xl p-3 space-y-2 ${rec.col==='emerald'?'border-emerald-500/30 bg-emerald-500/5':'border-blue-500/30 bg-blue-500/5'}`}>
                        <div className="flex items-center justify-between">
                          <span className={`text-[8px] font-bold uppercase ${rec.col==='emerald'?'text-emerald-400':'text-blue-400'}`}>{rec.step}</span>
                          <span className="text-[8px] text-gray-500 font-mono">Confidence: {rec.confidence}</span>
                        </div>
                        <div className="text-[10px] font-bold text-white">{rec.action}</div>
                        <p className="text-[9px] text-gray-400 leading-relaxed">{rec.reason}</p>
                        <div className="flex items-center justify-between text-[8px] text-gray-500"><span>{rec.legal}</span><span>{rec.duration}</span></div>
                        <button className={`w-full text-[9px] font-bold py-1.5 rounded-lg cursor-pointer transition-all ${rec.col==='emerald'?'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30':'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'}`}>Run Action</button>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Action Grid */}
                <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-4 space-y-3">
                  <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">All Actions</h3>
                  <div className="grid grid-cols-4 gap-2">
                    {[{l:'Verify Identity',I:UserCheck,c:'text-emerald-400'},{l:'Start Discovery',I:Search,c:'text-blue-400'},{l:'Generate Response',I:FileText,c:'text-purple-400'},{l:'Notify Legal',I:Shield,c:'text-amber-400'},{l:'Run Risk Assessment',I:AlertTriangle,c:'text-rose-400'},{l:'Generate DPIA',I:FileText,c:'text-blue-400'},{l:'Merge Cases',I:Link,c:'text-gray-400'},{l:'Escalate',I:AlertOctagon,c:'text-rose-400'}].map(a=>(
                      <button key={a.l} className="bg-[#151C33] border border-[#1E294B] rounded-xl p-3 text-center space-y-2 hover:border-blue-500/30 hover:bg-blue-500/5 transition-all cursor-pointer group">
                        <a.I size={16} className={`${a.c} mx-auto`}/><div className="text-[8px] text-gray-400 group-hover:text-gray-200 leading-snug">{a.l}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {tab==='Timeline'&&(
              <div className="p-5 space-y-3">
                <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Case Timeline</h3>
                <div className="relative space-y-4 pl-8">
                  <div className="absolute left-3 top-0 bottom-0 w-px bg-[#1E294B]"/>
                  {sel.timeline.map((ev,i)=>(
                    <div key={i} className="relative flex items-start space-x-3">
                      <div className="absolute -left-5"><TLIcon type={ev.type}/></div>
                      <div className="flex-1 bg-[#0E1325] border border-[#1E294B] rounded-xl p-3 space-y-1">
                        <div className="flex items-center justify-between"><span className="text-[9px] font-bold text-gray-300">{ev.actor}</span><span className="text-[8px] text-gray-600 font-mono">{ev.time}</span></div>
                        <p className="text-[10px] text-gray-400 leading-relaxed">{ev.text}</p>
                      </div>
                    </div>
                  ))}
                  {sel.timeline.length===0&&<div className="text-center py-8 text-gray-600 text-xs italic">No timeline events yet</div>}
                </div>
              </div>
            )}

            {tab==='Replies'&&(
              <div className="flex flex-col h-full">
                <div className="flex-1 overflow-y-auto p-5 space-y-3">
                  {sel.messages.map(msg=>{
                    const s={customer:{bg:'bg-[#0E1325] border-[#1E294B]',lc:'text-emerald-400',lbl:'Customer'},ai:{bg:'bg-blue-500/5 border-blue-500/20',lc:'text-blue-400',lbl:'Kibo AI'},note:{bg:'bg-amber-500/5 border-amber-500/20',lc:'text-amber-400',lbl:'Internal'},legal:{bg:'bg-purple-500/5 border-purple-500/20',lc:'text-purple-400',lbl:'Legal'}}[msg.type]||{bg:'bg-[#0E1325] border-[#1E294B]',lc:'text-gray-400',lbl:'System'};
                    return <div key={msg.id} className={`border ${s.bg} rounded-xl p-4 space-y-2`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2"><span className={`text-[8px] font-bold ${s.lc} uppercase`}>{s.lbl}</span><span className="text-[9px] font-semibold text-gray-300">{msg.from}</span></div>
                        <span className="text-[8px] text-gray-600 font-mono">{msg.time}</span>
                      </div>
                      <p className="text-xs text-gray-300 leading-relaxed">{msg.body}</p>
                    </div>;
                  })}
                  {sel.messages.length===0&&<div className="text-center py-12 text-gray-600 text-xs italic">No messages yet</div>}
                </div>
                <div className="border-t border-[#1E294B] p-4 space-y-3 bg-[#0A0F1E]">
                  <div className="flex items-center space-x-1">
                    {[{id:'reply',label:'Reply',c:'text-emerald-400'},{id:'note',label:'Internal Note',c:'text-amber-400'},{id:'ai',label:'AI Draft',c:'text-blue-400'}].map(m=><button key={m.id} onClick={()=>setReplyMode(m.id)} className={`text-[9px] font-bold px-2.5 py-1.5 rounded-lg transition-all cursor-pointer ${replyMode===m.id?`${m.c} bg-white/8`:'text-gray-500 hover:text-gray-300'}`}>{m.label}</button>)}
                    <div className="flex-1"/>
                    <button className="text-[8px] text-blue-400 hover:text-blue-300 cursor-pointer flex items-center space-x-1"><Sparkles size={10}/><span>Generate AI Draft</span></button>
                  </div>
                  <textarea value={replyText} onChange={e=>setReplyText(e.target.value)} rows={3} placeholder={replyMode==='note'?'Add an internal note...':replyMode==='ai'?'Describe what the AI should generate...':'Write a reply to the requester...'} className="w-full bg-[#0E1325] border border-[#1E294B] rounded-xl px-3 py-2.5 text-xs text-gray-300 placeholder-gray-600 focus:outline-none focus:border-blue-500/40 resize-none"/>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <button className="text-gray-500 hover:text-gray-300 cursor-pointer"><Paperclip size={13}/></button>
                      <button className="text-gray-500 hover:text-gray-300 cursor-pointer"><Link size={13}/></button>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-[8px] text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">Approval required before sending</span>
                      <button className="flex items-center space-x-1.5 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg transition-all cursor-pointer"><Send size={11}/><span>Send for Approval</span></button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {tab==='Evidence'&&(
              <div className="p-5 space-y-4">
                <div className="flex items-center justify-between"><h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Evidence & Documents</h3><button className="flex items-center space-x-1 text-[9px] font-bold text-blue-400 hover:text-blue-300 cursor-pointer"><Upload size={11}/><span>Upload</span></button></div>
                {sel.evidence.length>0?(
                  <div className="space-y-2">{sel.evidence.map((e,i)=>(
                    <div key={i} className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-3 flex items-center justify-between">
                      <div className="flex items-center space-x-3"><div className="w-8 h-8 bg-blue-500/10 rounded-lg flex items-center justify-center"><FileText size={14} className="text-blue-400"/></div><div><div className="text-[10px] font-medium text-white">{e.name}</div><div className="text-[8px] text-gray-500 font-mono">{e.type} · {e.size} · {e.added}</div></div></div>
                      <div className="flex items-center space-x-2"><span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${e.status==='verified'?'bg-emerald-500/10 text-emerald-400 border-emerald-500/20':'bg-amber-500/10 text-amber-400 border-amber-500/20'}`}>{e.status.replace('_',' ')}</span><button className="text-gray-500 hover:text-gray-300 cursor-pointer"><Download size={12}/></button></div>
                    </div>
                  ))}</div>
                ):(
                  <div className="border-2 border-dashed border-[#1E294B] rounded-xl p-8 text-center space-y-2"><Upload size={24} className="text-gray-600 mx-auto"/><p className="text-xs text-gray-500">Drop files here or click to upload</p></div>
                )}
              </div>
            )}

            {tab==='Workflow'&&(
              <div className="p-5 space-y-4">
                <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Compliance Workflow</h3>
                <div className="space-y-2">
                  {sel.workflow.map((step,i)=>{
                    const done=i<sel.currentStep; const cur=i===sel.currentStep;
                    return <div key={i} className={`flex items-center space-x-3 p-3 rounded-xl border transition-all ${cur?'bg-blue-500/10 border-blue-500/30 ring-1 ring-blue-500/20':done?'bg-emerald-500/5 border-emerald-500/20':'bg-[#0E1325] border-[#1E294B]'}`}>
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[9px] font-bold ${done?'bg-emerald-500 text-white':cur?'bg-blue-500 text-white animate-pulse':'bg-[#1E294B] text-gray-600'}`}>{done?<Check size={12}/>:i+1}</div>
                      <div className="flex-1"><span className={`text-xs font-medium ${done?'text-emerald-400 line-through':cur?'text-white':'text-gray-500'}`}>{step}</span></div>
                      {cur&&<span className="text-[8px] text-blue-400 font-bold uppercase animate-pulse">Active</span>}
                      {done&&<CheckCircle size={13} className="text-emerald-500"/>}
                    </div>;
                  })}
                </div>
                <div className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-3">
                  <div className="flex justify-between text-[9px] text-gray-400 mb-2"><span>Overall Progress</span><span>{Math.round((sel.currentStep/sel.workflow.length)*100)}%</span></div>
                  <div className="h-2 bg-[#151C33] rounded-full overflow-hidden"><div className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full transition-all" style={{width:`${(sel.currentStep/sel.workflow.length)*100}%`}}/></div>
                </div>
              </div>
            )}

            {tab==='Knowledge'&&(
              <div className="p-5 space-y-4">
                <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Relevant Knowledge</h3>
                <div className="grid grid-cols-2 gap-3">
                  {[{title:`${sel.regulation[0]} — Full Text`,type:'Regulation',icon:'⚖️'},{title:'EDPB Guidelines 01/2022 on Data Subject Rights',type:'Guidance',icon:'📋'},{title:`${sel.type} Response Template`,type:'Template',icon:'📄'},{title:'Identity Verification SOP v2.3',type:'Procedure',icon:'🔐'},{title:'Data Discovery Playbook',type:'Playbook',icon:'🔍'},{title:'Similar Case: PRIV-2025-0621 (Closed)',type:'Case',icon:'📁'}].map((k,i)=>(
                    <div key={i} className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-3 space-y-1.5 hover:border-blue-500/30 transition-all cursor-pointer">
                      <div className="flex items-center justify-between"><span className="text-lg">{k.icon}</span><span className="text-[8px] text-gray-600 font-mono">{k.type}</span></div>
                      <p className="text-[10px] font-medium text-gray-300 leading-snug">{k.title}</p>
                      <button className="text-[8px] text-blue-400 hover:text-blue-300 flex items-center space-x-1"><ExternalLink size={8}/><span>Open</span></button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {tab==='Automation'&&(
              <div className="p-5 space-y-4">
                <h3 className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Active Automations</h3>
                <div className="space-y-2">
                  {[{name:'Identity Verification Agent',status:'completed',progress:100,result:'Verified with 97% confidence',time:'2026-07-01 14:15'},{name:'Data Discovery — Salesforce CRM',status:'completed',progress:100,result:'1,247 records found',time:'2026-07-03 08:45'},{name:'Data Discovery — Analytics Platform',status:'running',progress:68,result:'Scanning 3 of 7 data marts...',time:'Running now'},{name:'Data Discovery — Ad Platform',status:'waiting',progress:0,result:'Queued — pending CRM export review',time:'Pending'},{name:'Response Draft Generator',status:'waiting',progress:0,result:'Will trigger after data review complete',time:'Pending'}].map((a,i)=>{
                    const s={completed:{text:'text-emerald-400',bg:'bg-emerald-500/10',lbl:'✓ Completed'},running:{text:'text-blue-400',bg:'bg-blue-500/10',lbl:'⟳ Running'},waiting:{text:'text-gray-500',bg:'bg-gray-500/10',lbl:'⌛ Waiting'},failed:{text:'text-rose-400',bg:'bg-rose-500/10',lbl:'✗ Failed'}}[a.status];
                    return <div key={i} className="bg-[#0E1325] border border-[#1E294B] rounded-xl p-3 space-y-2">
                      <div className="flex items-center justify-between"><div className="flex items-center space-x-2"><Zap size={11} className={s.text}/><span className="text-[10px] font-medium text-white">{a.name}</span></div><span className={`text-[8px] font-bold px-1.5 py-0.5 rounded ${s.bg} ${s.text}`}>{s.lbl}</span></div>
                      {a.status==='running'&&<div className="h-1 bg-[#1E294B] rounded-full overflow-hidden"><div className="h-full bg-blue-500 rounded-full animate-pulse" style={{width:`${a.progress}%`}}/></div>}
                      <p className="text-[9px] text-gray-400">{a.result}</p>
                      <p className="text-[8px] text-gray-600 font-mono">{a.time}</p>
                    </div>;
                  })}
                </div>
              </div>
            )}

          </div>
        </div>
      ):(
        <div className="flex-1 flex items-center justify-center"><div className="text-center space-y-3"><Inbox size={32} className="text-gray-600 mx-auto"/><p className="text-gray-500 text-sm">Select a case to begin</p></div></div>
      )}
    </div>
  );
}
