import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Shield, AlertTriangle, Clock, Ban, Check, Undo2,
  ChevronDown, ChevronUp, Terminal, ShieldAlert, UserCheck, Search,
  HardDrive, Database, Network, FileCheck, Layers, RefreshCw, AlertOctagon,
  Users, Briefcase, Eye, Globe, User, Radio, FileUp, Sparkles, Send, Trash2,
  Activity, Server, Mail, Settings, Plus, CheckSquare, Square, Edit, Save, List,
  FolderOpen, Cpu, BookOpen
} from 'lucide-react';
import AdminDashboard from './AdminDashboard';

const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? 'http://localhost:8000'
  : window.location.origin;

const App = () => {
  // --- Core State ---
  const [securityMode, setSecurityMode] = useState('expert'); // public, employee, expert, psr
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // --- Agent Persistent Memory State ---
  const [agentLessons, setAgentLessons] = useState([]);
  const [newLessonNotes, setNewLessonNotes] = useState('');
  const [newLessonDomain, setNewLessonDomain] = useState('onboarding');
  const [lessonsIsExpanded, setLessonsIsExpanded] = useState(true); // for Expert mode
  const [simTriggerType, setSimTriggerType] = useState('Regulatory_Update');
  const [simTriggerData, setSimTriggerData] = useState('EDPB draft guidelines require Quebec Law 25 Consent matching.');
  const [simLogs, setSimLogs] = useState([]);
  const [simIsRunning, setSimIsRunning] = useState(false);
  const [legalLibrary, setLegalLibrary] = useState([]);
  
  // --- Admin Dashboard State ---
  const [adminActiveTab, setAdminActiveTab] = useState('dashboard');
  const [adminSelectedNode, setAdminSelectedNode] = useState(null);
  const [adminDiffMode, setAdminDiffMode] = useState(false);
  const [adminTriggers, setAdminTriggers] = useState([
    { id: 'TR-101', timestamp: '2026-07-03 01:10', priority: 'high', source: 'EDPB Feed', framework: 'GDPR', jurisdiction: 'European Union', client: 'Kids Help Phone', confidence: '94%', impact: 'High', status: 'Triaged' },
    { id: 'TR-102', timestamp: '2026-07-03 01:12', priority: 'medium', source: 'CMP Telemetry', framework: 'Law 25', jurisdiction: 'Quebec, CA', client: 'KHP Foundation', confidence: '88%', impact: 'Medium', status: 'Pending Review' },
    { id: 'TR-103', timestamp: '2026-07-02 23:45', priority: 'critical', source: 'Privacy Officer Ticket', framework: 'PHIPA', jurisdiction: 'Ontario, CA', client: 'Clinical Portal', confidence: '99%', impact: 'High', status: 'Investigating' },
    { id: 'TR-104', timestamp: '2026-07-02 22:15', priority: 'low', source: 'ISO Auditer', framework: 'ISO 27701', jurisdiction: 'Global', client: 'All', confidence: '95%', impact: 'Low', status: 'Completed' }
  ]);
  const [adminAgents, setAdminAgents] = useState([
    { name: 'Ingestion Agent', version: 'v2.1.4', status: 'idle', queue: 0, runtime: '1.2s', cost: '$0.004', success: '99.8%', failure: '0.2%', memory: '124MB', cpu: '4%', tokens: '1.5k' },
    { name: 'Adaptation Coder', version: 'v3.0.2', status: 'processing', queue: 1, runtime: '4.8s', cost: '$0.015', success: '97.2%', failure: '2.8%', memory: '512MB', cpu: '68%', tokens: '8.4k' },
    { name: 'Self-Critique Auditor', version: 'v2.2.0', status: 'idle', queue: 0, runtime: '2.5s', cost: '$0.008', success: '98.5%', failure: '1.5%', memory: '256MB', cpu: '12%', tokens: '3.2k' },
    { name: 'Deployment Controller', version: 'v1.8.1', status: 'waiting', queue: 2, runtime: '0.8s', cost: '$0.002', success: '99.9%', failure: '0.1%', memory: '96MB', cpu: '2%', tokens: '500' }
  ]);
  const [adminDeployments, setAdminDeployments] = useState([
    { version: 'v2.8.4-rel', environment: 'production', status: 'active', proposed_by: 'Adaptation Coder', approved_by: 'CPO (HITL)', timestamp: '2026-07-03 01:16', commit: '89a0fcdb' },
    { version: 'v2.8.3-rel', environment: 'production', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'System Admin', timestamp: '2026-07-03 00:05', commit: 'f45bdcca' },
    { version: 'v2.8.4-rc1', environment: 'staging', status: 'completed', proposed_by: 'Adaptation Coder', approved_by: 'Automatic (Score > 8)', timestamp: '2026-07-02 23:45', commit: 'c90cdbea' }
  ]);
  const [adminAudits, setAdminAudits] = useState([
    { timestamp: '2026-07-03 01:16', user: 'Waël Hassan', agent: 'Deployment Controller', llm: 'qwen2.5-coder:32b', action: 'Deploy UI adaptation template', hash: 'SHA256:d9b2089f', status: 'success' },
    { timestamp: '2026-07-03 01:15', user: 'LangGraph Engine', agent: 'Self-Critique Auditor', llm: 'qwen3.6:latest', action: 'Grounded RAG critique scoring (9/10)', hash: 'SHA256:b8c983ea', status: 'approved' },
    { timestamp: '2026-07-03 01:12', user: 'LangGraph Engine', agent: 'Self-Critique Auditor', llm: 'qwen3.6:latest', action: 'Grounded RAG critique scoring (5/10)', hash: 'SHA256:c0901e9d', status: 'rejected' }
  ]);
  const [adminClients, setAdminClients] = useState([
    { name: 'Kids Help Phone', organization: 'KHP Canada', role: 'Data Controller', coverage: ['PIPEDA', 'Quebec Law 25', 'PHIPA'], users: 24, status: 'active' },
    { name: 'KHP Foundation', organization: 'KHP Foundation', role: 'Joint Controller', coverage: ['PIPEDA', 'CASL'], users: 8, status: 'active' },
    { name: 'Crisis Support Portal', organization: 'Clinical Services', role: 'Processor', coverage: ['PHIPA', 'CYFSA'], users: 12, status: 'active' }
  ]);

  const [activeLegislations, setActiveLegislations] = useState(['canada', 'quebec', 'phipa', 'cyfsa']);
  const [activeJurisdiction, setActiveJurisdiction] = useState('canada');
  const [jurConfig, setJurConfig] = useState({
    code: "canada",
    flag: "🇨🇦",
    name: "Canada - PIPEDA",
    access_request_term: "Access to Information Request",
    access_request_abbr: "ATIP",
    data_subject_term: "Individual",
    regulator: "Office of the Privacy Commissioner of Canada (OPC)",
    primary_statute: "PIPEDA",
    access_deadline_days: 30,
    breach_notification: "OPC + affected individuals (RROSH)",
    assessment_types: ["PIA"],
    training_track: "pipeda"
  });

  const [jurisdictionsList, setJurisdictionsList] = useState([
    {
      code: "ontario",
      flag: "🇨🇦",
      name: "Ontario (Public Sector) - FIPPA",
      primary_statute: "FIPPA",
      access_request_abbr: "FOI"
    },
    {
      code: "canada",
      flag: "🇨🇦",
      name: "Canada - PIPEDA",
      primary_statute: "PIPEDA",
      access_request_abbr: "ATIP"
    },
    {
      code: "quebec",
      flag: "🇨🇦",
      name: "Quebec - Law 25",
      primary_statute: "Law 25",
      access_request_abbr: "AR"
    },
    {
      code: "phipa",
      flag: "🇨🇦",
      name: "Ontario Health - PHIPA",
      primary_statute: "PHIPA",
      access_request_abbr: "PHR"
    },
    {
      code: "cyfsa",
      flag: "🇨🇦",
      name: "Ontario Child/Youth - CYFSA",
      primary_statute: "CYFSA",
      access_request_abbr: "YAR"
    },
    {
      code: "us",
      flag: "🇺🇸",
      name: "United States - CCPA/CPRA",
      primary_statute: "CPRA",
      access_request_abbr: "DSAR"
    },
    {
      code: "eu",
      flag: "🇪🇺",
      name: "European Union - GDPR",
      primary_statute: "GDPR",
      access_request_abbr: "DSAR"
    },
    {
      code: "uk",
      flag: "🇬🇧",
      name: "United Kingdom - UK GDPR",
      primary_statute: "UK GDPR",
      access_request_abbr: "SAR"
    }
  ]);
  const [transactions, setTransactions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [rules, setRules] = useState([]);
  const [isSystemOnline, setIsSystemOnline] = useState(true);

  // --- Public Widget State ---
  const [widgetName, setWidgetName] = useState('');
  const [widgetEmail, setWidgetEmail] = useState('');
  const [widgetType, setWidgetType] = useState('access');
  const [widgetDesc, setWidgetDesc] = useState('');
  const [widgetStatus, setWidgetStatus] = useState('');
  const [widgetTrackId, setWidgetTrackId] = useState('');
  const [widgetCheckId, setWidgetCheckId] = useState('');
  const [widgetCheckResult, setWidgetCheckResult] = useState(null);

  // --- Employee Mode State ---
  const [employeeRisks, setEmployeeRisks] = useState([]);
  const [employeeTraining, setEmployeeTraining] = useState([]);
  const [inventorySystem, setInventorySystem] = useState('');
  const [inventoryDataTypes, setInventoryDataTypes] = useState('');
  const [inventoryPurpose, setInventoryPurpose] = useState('');
  const [inventoryRetention, setInventoryRetention] = useState('');
  const [inventorySharing, setInventorySharing] = useState('');
  const [inventoryStatus, setInventoryStatus] = useState('');

  // --- Expert Mode State ---
  const [expertAssessments, setExpertAssessments] = useState([]);
  const [expertMeetings, setExpertMeetings] = useState([]);
  const [meetingsAgenda, setMeetingsAgenda] = useState('');
  const [meetingsDate, setMeetingsDate] = useState('');
  const [meetingsType, setMeetingsType] = useState('privacy_security_weekly');
  const [selectedMeetingId, setSelectedMeetingId] = useState(null);
  const [meetingMinutes, setMeetingMinutes] = useState('');
  const [meetingActionTask, setMeetingActionTask] = useState('');
  const [meetingActionOwner, setMeetingActionOwner] = useState('');
  const [meetingActionItems, setMeetingActionItems] = useState([]);
  const [inboxEmails, setInboxEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [inboxReplies, setInboxReplies] = useState([]);
  const [replyBody, setReplyBody] = useState('');
  const [trainingCompliance, setTrainingCompliance] = useState(null);

  // --- Corporate Governance Registers State ---
  const [govSelectedTab, setGovSelectedTab] = useState('inventory');
  const [govIsExpanded, setGovIsExpanded] = useState(true);
  const [govDataInventory, setGovDataInventory] = useState([
    { system: 'Aselo Console', element: 'Chat Transcripts', population: 'Youth Chat Callers', retention: '90-day purge / indefinitely if local download', control: 'TLS 1.3, AES-256' },
    { system: 'Blackbaud CRM', element: 'Billing Details & Emails', population: 'Financial Donors', retention: '7 Years (Financial audit limit)', control: 'PCI-DSS Compliant Gateway' },
    { system: 'HR SharePoint', element: 'Police Vulnerable Screens', population: 'Volunteer Counselors', retention: 'Preserved during term of service + 1 year', control: 'Role-based access group (HR Only)' }
  ]);
  const [govSubProcessors, setGovSubProcessors] = useState([
    { name: 'Twilio Inc.', role: 'SMS Gateway Carrier', dpa: 'DPA Annex Signed', storage: 'AWS US-East', jurisdiction: 'United States (Cross-Border Transfer TIA approved)' },
    { name: 'Salesforce.com', role: 'Intake Support Routing CRM', dpa: 'Standard Contractual Clauses (SCC)', storage: 'Salesforce Canada East', jurisdiction: 'Canada (In-Country Local Storage)' },
    { name: 'Blackbaud Inc.', role: 'Donor Relationship DB', dpa: 'DPA Under Review', storage: 'Blackbaud Cloud', jurisdiction: 'Canada / US' }
  ]);
  const [govRoleHierarchy, setGovRoleHierarchy] = useState([
    { department: 'Clinical Operations', roles: ['Director of Counseling', 'Clinical Supervisor', 'Crisis Counselor', 'Volunteer Crisis Responder'] },
    { department: 'Development & Fundraising', roles: ['VP of Philanthropy', 'Donor Data Custodian', 'Intake Coordinator'] },
    { department: 'Security & Compliance (DPO)', roles: ['Chief Privacy Officer (Chair)', 'DPO Lead', 'Privacy Operations Analyst'] }
  ]);

  // --- PSR Committee Mode State ---
  const [psrMeetings, setPsrMeetings] = useState([]);
  const [psrRiskQueue, setPsrRiskQueue] = useState([]);
  const [psrSelectedRisk, setPsrSelectedRisk] = useState(null);
  const [psrVote, setPsrVote] = useState('approve');
  const [psrRecommendation, setPsrRecommendation] = useState('');
  
  // --- PSR Notes-derived State ---
  const [psrCopilotQuery, setPsrCopilotQuery] = useState('');
  const [psrCopilotAnswer, setPsrCopilotAnswer] = useState('');
  const [psrTransitionTasks, setPsrTransitionTasks] = useState([
    { id: 'T1', title: 'Revoke Nascent Access (IP/Data)', owner: 'Bryan / Neil', status: 'pending', notes: 'Confirm in writing that no IP or data remains with previous vendor.' },
    { id: 'T2', title: 'June 8 OpenText Demo LOI & NDA', owner: 'Betty', status: 'completed', notes: 'Outlining intent to collaborate with mutual NDA clauses.' },
    { id: 'T3', title: 'OpenText MOU Build Plan & PIA', owner: 'Betty / Bryan', status: 'pending', notes: 'Draft MOU and initiate Quebec Law 25 PIA after build plan received.' },
    { id: 'T4', title: 'Update Foundation Terms of Service', owner: 'Sofiya', status: 'pending', notes: 'Add KHP + Foundation privacy policy links; correct contact details.' },
    { id: 'T5', title: 'Onboard Danny (Finance/Privacy)', owner: 'Sofiya / Neil', status: 'pending', notes: 'Deliver onboarding package, brief on transition risks, & SharePoint.' }
  ]);

  // --- Canadian Onboarding & CASL State ---
  const [onboardingTasks, setOnboardingTasks] = useState([]);
  const [caslRegistry, setCaslRegistry] = useState([]);
  const [caslDisclaimers, setCaslDisclaimers] = useState([
    { id: 'DISC-001', target: 'Youth Crisis Chat Gateway', text: 'By launching this chat, you consent to our collection of IP address, browser headers, and conversation logs. Transcripts are preserved for safety audits and clinical supervision.', placement: '/chat/launch-gate', type: 'Express Consent', jurisdiction: 'PIPEDA / Law 25' },
    { id: 'DISC-002', target: 'Donor Transaction Page', text: 'Kids Help Phone collects donor names, billing details, and email addresses to process donations, issue official tax receipts, and send seasonal updates. Opt-out at any time.', placement: '/donate/checkout', type: 'Express (Consent Checkbox)', jurisdiction: 'PIPEDA / CASL' },
    { id: 'DISC-003', target: 'Volunteer Intake Form', text: 'We collect reference details, police background screens, and contact info to evaluate eligibility for volunteer counseling positions.', placement: '/careers/volunteer-apply', type: 'Express Consent', jurisdiction: 'Ontario FIPPA' }
  ]);
  const [caslDataElements, setCaslDataElements] = useState([
    { element: 'Phone Number', subject: 'SMS Support User', purpose: 'Immediate routing and delivery of SMS counseling sessions', disclaimer: 'DISC-001 (Gateway Notice)' },
    { element: 'Chat Transcripts', subject: 'Web Chat Caller', purpose: 'Clinical supervision, risk escalation review, and safety protocols', disclaimer: 'DISC-001 (Gateway Notice)' },
    { element: 'Credit Card Hash', subject: 'Financial Donor', purpose: 'Payment processing and tokenized recurring donation checks', disclaimer: 'DISC-002 (Donor Policy)' },
    { element: 'Criminal Records Check', subject: 'Volunteer Applicant', purpose: 'Vulnerable sector screening for youth counseling suitability', disclaimer: 'DISC-003 (Intake Disclaimer)' }
  ]);
  const [caslLogs, setCaslLogs] = useState([
    "[SYSTEM] Consent enforcement loop initialized.",
    "[SYSTEM] Awaiting sunset automation trigger..."
  ]);
  const [isSunsetting, setIsSunsetting] = useState(false);
  const [editingNotesTaskId, setEditingNotesTaskId] = useState(null);
  const [editingNotesText, setEditingNotesText] = useState("");

  // --- AI Onboarding Agent State ---
  const [onboardingSubMode, setOnboardingSubMode] = useState('checklist'); // 'checklist' or 'ai_agent'
  const [onbSectorVariant, setOnbSectorVariant] = useState('commercial'); // 'commercial', 'healthcare', 'tech_media'
  const [onbSessionId, setOnbSessionId] = useState(null);
  const [onbWebsiteUrl, setOnbWebsiteUrl] = useState('https://kidshelphone.ca');
  const [onbUploadedFiles, setOnbUploadedFiles] = useState([]);
  const [onbStatus, setOnbStatus] = useState('idle'); // 'idle', 'ingesting', 'normalizing', 'gap_review', 'validated'
  const [onbProgress, setOnbProgress] = useState(0);
  const [onbLogs, setOnbLogs] = useState([]);
  const [onbProfile, setOnbProfile] = useState(null);
  const [onbGaps, setOnbGaps] = useState([]);
  const [onbSelectedProfileSection, setOnbSelectedProfileSection] = useState('policies');
  const [onbGapInputs, setOnbGapInputs] = useState({}); // stores text values for answers

  // --- Agentic CPO Console State ---
  const [agentsList, setAgentsList] = useState([
    { id: "dsar", name: "DSAR Fulfillment Engine", status: "Listening", lastAction: "Scanned database tables; no new requests pending.", focus: "GDPR, CCPA/CPRA, Law 25" },
    { id: "pia", name: "PIA Agent", status: "Idle", lastAction: "Analyzed 'SaaS Telemetry Core' project; generated risk matrix.", focus: "DPIAs, FIPPA, PIPEDA" },
    { id: "vendor", name: "Vendor Compliance Agent", status: "Idle", lastAction: "Reviewed sub-processor agreements for Workday integration.", focus: "Data Processors, Accountability" },
    { id: "code", name: "Code Auditing Agent", status: "Monitoring", lastAction: "Verified 28 production API schemas; zero cleartext leaks detected.", focus: "Privacy by Design, Minimization" },
    { id: "watchdog", name: "Regulatory Watchdog Agent", status: "Active", lastAction: "Synchronized rulings from IPC Ontario; updated internal checklist.", focus: "Jurisdictional Mapping, Rulings" },
    { id: "incident", name: "Incident & Breach Agent", status: "Listening", lastAction: "SIEM access logs verified; no anomalous patterns detected.", focus: "Breach Notifications, Containment" },
    { id: "policy", name: "Policy & Consent Agent", status: "Idle", lastAction: "Verified public cookie preferences and CMP parameters.", focus: "CASL, Transparency, Disclosures" }
  ]);

  const [agentLogs, setAgentLogs] = useState([
    `[${new Date().toLocaleTimeString()}] Orchestration Loop initialized. Standing by for triggers...`,
    `[${new Date().toLocaleTimeString()}] Regulatory Watchdog connected to commissioner feeds.`
  ]);

  const [hitlQueue, setHitlQueue] = useState([
    {
      id: "HITL-001",
      title: "Approve Vendor Sub-processor Agreement (OpenAI DPA)",
      details: "Vendor Compliance Agent detected a high-risk data transfer clause sending PII to US-based systems under Ontario PHIPA jurisdiction. DPA requires execution of Standard Contractual Clauses (SCCs).",
      agent: "Vendor Compliance Agent",
      priority: "high",
      status: "pending"
    },
    {
      id: "HITL-002",
      title: "DSAR Redaction Package Approval (REQ-8291)",
      details: "DSAR Fulfillment Engine completed data collection for employee 'John Smith'. Package contains redacted corporate logs containing other employee emails. Requires human verification before export.",
      agent: "DSAR Fulfillment Engine",
      priority: "medium",
      status: "pending"
    }
  ]);

  const [isSimulatingLoop, setIsSimulatingLoop] = useState(false);

  // Helper fetch function to inject the X-Kibo-Scope header automatically
  const kiboFetch = async (url, options = {}) => {
    const headers = {
      ...options.headers,
      'X-Kibo-Scope': securityMode,
      'Content-Type': 'application/json'
    };
    try {
      const res = await fetch(url, { ...options, headers });
      setIsSystemOnline(true);
      return res;
    } catch (e) {
      setIsSystemOnline(false);
      throw e;
    }
  };

  const fetchJurisdictions = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/jurisdictions`);
      if (res.ok) {
        const data = await res.json();
        setJurisdictionsList(data);
        setIsSystemOnline(true);
      } else {
        setIsSystemOnline(false);
      }
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchActiveJurisdictionConfig = async (code) => {
    try {
      const res = await fetch(`${API_BASE}/api/jurisdictions/${code}/config`);
      if (res.ok) {
        const data = await res.json();
        setJurConfig(data);
        setIsSystemOnline(true);
      } else {
        setIsSystemOnline(false);
      }
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const handleJurisdictionChange = async (code) => {
    setActiveJurisdiction(code);
    await fetchActiveJurisdictionConfig(code);
    try {
      const res = await fetch(`${API_BASE}/api/user/jurisdiction`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jurisdiction: code })
      });
      if (res.ok) {
        setIsSystemOnline(true);
      } else {
        setIsSystemOnline(false);
      }
      // Refresh data
      fetchEmployeeData();
      fetchExpertData();
      fetchPsrData();
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchEmployeeData = async () => {
    try {
      const risksRes = await kiboFetch(`${API_BASE}/api/employee/employee-default/risks`);
      if (risksRes.ok) setEmployeeRisks(await risksRes.json());

      const trainingRes = await kiboFetch(`${API_BASE}/api/employee/employee-default/training`);
      if (trainingRes.ok) setEmployeeTraining(await trainingRes.json());
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchAgenticData = async () => {
    try {
      const agentsRes = await kiboFetch(`${API_BASE}/api/agents/sensing`);
      if (agentsRes.ok) {
        const rawAgents = await agentsRes.json();
        setAgentsList(prev => prev.map(pa => {
          const match = rawAgents.find(ra => ra.agent_id === pa.id);
          return match ? { ...pa, status: match.status === 'active' ? (pa.status === 'Running' || pa.status === 'Active' ? pa.status : 'Listening') : 'Idle' } : pa;
        }));
      }

      const updatesRes = await kiboFetch(`${API_BASE}/api/knowledge/updates`);
      if (updatesRes.ok) {
        const updates = await updatesRes.json();
        const pendingUpdates = updates.filter(u => u.status === 'pending_review');
        const queueItems = pendingUpdates.map(u => ({
          id: u.update_id,
          title: `Approve Knowledge Update: ${u.entity}`,
          details: `${u.impact_summary} (New Value: "${u.new_value}". Confidence: ${u.confidence}%. Source: ${u.source})`,
          agent: u.agent,
          priority: u.confidence < 90 ? "high" : "medium",
          status: "pending"
        }));
        setHitlQueue(queueItems);
      }
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchExpertData = async () => {
    try {
      const assessRes = await kiboFetch(`${API_BASE}/api/expert/assessments`);
      if (assessRes.ok) setExpertAssessments(await assessRes.json());

      const meetRes = await kiboFetch(`${API_BASE}/api/expert/meetings`);
      if (meetRes.ok) setExpertMeetings(await meetRes.json());

      const inboxRes = await kiboFetch(`${API_BASE}/api/expert/inbox`);
      if (inboxRes.ok) setInboxEmails(await inboxRes.json());

      const complianceRes = await kiboFetch(`${API_BASE}/api/expert/training/compliance`);
      if (complianceRes.ok) setTrainingCompliance(await complianceRes.json());

      // Fetch Onboarding and Agentic data
      fetchOnboardingData();
      fetchAgenticData();
      fetchLessons();
      fetchLegalLibrary();
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchPsrData = async () => {
    try {
      const meetingsRes = await kiboFetch(`${API_BASE}/api/psr/meetings`);
      if (meetingsRes.ok) setPsrMeetings(await meetingsRes.json());

      const queueRes = await kiboFetch(`${API_BASE}/api/psr/risk-queue`);
      if (queueRes.ok) setPsrRiskQueue(await queueRes.json());
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const fetchOnboardingData = async () => {
    try {
      const tasksRes = await kiboFetch(`${API_BASE}/api/onboarding/tasks`);
      if (tasksRes.ok) setOnboardingTasks(await tasksRes.json());
      
      const caslRes = await kiboFetch(`${API_BASE}/api/onboarding/casl`);
      if (caslRes.ok) setCaslRegistry(await caslRes.json());
    } catch (e) {
      console.error("Error fetching onboarding data:", e);
      setIsSystemOnline(false);
    }
  };

  const handleToggleOnboardingTask = async (taskId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/onboarding/tasks/${taskId}/toggle`, { method: 'POST' });
      if (res.ok) {
        fetchOnboardingData();
      }
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const handleUpdateTaskNotes = async (taskId, notesText) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/onboarding/tasks/${taskId}/notes`, {
        method: 'POST',
        body: JSON.stringify({ notes: notesText })
      });
      if (res.ok) {
        setEditingNotesTaskId(null);
        fetchOnboardingData();
      }
    } catch (e) {
      console.error(e);
      setIsSystemOnline(false);
    }
  };

  const handleRunCaslSunset = async () => {
    setIsSunsetting(true);
    setCaslLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] Requesting CASL Sunset Automation execution from DGX Spark server...`]);
    try {
      const res = await kiboFetch(`${API_BASE}/api/onboarding/casl/sunset`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setCaslLogs(prev => [...prev, ...data.logs]);
        fetchOnboardingData();
      } else {
        setCaslLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [ERROR] Failed to execute sunset. Status: ${res.status}`]);
      }
    } catch (e) {
      setCaslLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [ERROR] Connection error: ${e.message}`]);
      setIsSystemOnline(false);
    } finally {
      setIsSunsetting(false);
    }
  };

  useEffect(() => {
    fetchJurisdictions();
    fetchActiveJurisdictionConfig(activeJurisdiction);
  }, []);

  useEffect(() => {
    if (securityMode === 'employee') {
      fetchEmployeeData();
    } else if (securityMode === 'expert') {
      fetchExpertData();
    } else if (securityMode === 'psr') {
      fetchPsrData();
    } else if (securityMode === 'admin') {
      fetchExpertData();
      fetchLessons();
      fetchLegalLibrary();
    }
  }, [securityMode, activeJurisdiction]);

  // --- Submit Public Request ---
  const handlePublicSubmit = async (e) => {
    e.preventDefault();
    setWidgetStatus('submitting');
    try {
      const res = await fetch(`${API_BASE}/api/widget/khp-org/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: widgetName,
          email: widgetEmail,
          request_type: widgetType,
          description: widgetDesc
        })
      });
      if (res.ok) {
        const data = await res.json();
        setWidgetStatus('success');
        setWidgetTrackId(data.request_id);
        setWidgetName('');
        setWidgetEmail('');
        setWidgetDesc('');
      } else {
        setWidgetStatus('error');
      }
    } catch (err) {
      setWidgetStatus('error');
    }
  };

  // --- Check Public Request Status ---
  const handleWidgetCheckStatus = async (e) => {
    e.preventDefault();
    if (!widgetCheckId) return;
    try {
      const res = await fetch(`${API_BASE}/api/widget/khp-org/status/${widgetCheckId}`);
      if (res.ok) {
        setWidgetCheckResult(await res.json());
      } else {
        setWidgetCheckResult({ status: 'Not Found', deadline: 'N/A' });
      }
    } catch (err) {
      setWidgetCheckResult({ status: 'Error loading details', deadline: 'N/A' });
    }
  };

  // --- Submit Employee Data Inventory ---
  const handleInventorySubmit = async (e) => {
    e.preventDefault();
    setInventoryStatus('submitting');
    try {
      const res = await kiboFetch(`${API_BASE}/api/employee/employee-default/inventory`, {
        method: 'POST',
        body: JSON.stringify({
          system_name: inventorySystem,
          data_types: inventoryDataTypes.split(',').map(s => s.trim()),
          purpose: inventoryPurpose,
          retention: inventoryRetention,
          sharing: inventorySharing
        })
      });
      if (res.ok) {
        setInventoryStatus('success');
        setInventorySystem('');
        setInventoryDataTypes('');
        setInventoryPurpose('');
        setInventoryRetention('');
        setInventorySharing('');
      } else {
        setInventoryStatus('error');
      }
    } catch (err) {
      setInventoryStatus('error');
    }
  };

  // --- Complete Training Module ---
  const handleCompleteTraining = async (moduleId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/employee/employee-default/training/${moduleId}/complete`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchEmployeeData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // --- Create meeting ---
  const handleCreateMeeting = async (e) => {
    e.preventDefault();
    if (!meetingsAgenda) return;
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/meetings`, {
        method: 'POST',
        body: JSON.stringify({
          type: meetingsType,
          date: meetingsDate || new Date().toISOString(),
          agenda: meetingsAgenda.split('\n').filter(s => s.trim() !== ''),
          attendees: ["CPO Wael", "Betty", "Legal Team"],
          materials: ["System Data Flow.pdf"]
        })
      });
      if (res.ok) {
        setMeetingsAgenda('');
        fetchExpertData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // --- Add Action Item ---
  const handleAddActionItem = () => {
    if (!meetingActionTask || !meetingActionOwner) return;
    setMeetingActionItems([...meetingActionItems, {
      task: meetingActionTask,
      owner: meetingActionOwner,
      due: "Within 30 days"
    }]);
    setMeetingActionTask('');
    setMeetingActionOwner('');
  };

  // --- Save Meeting Minutes ---
  const handleSaveMinutes = async (meetingId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/meetings/${meetingId}/minutes`, {
        method: 'POST',
        body: JSON.stringify({
          minutes: meetingMinutes,
          action_items: meetingActionItems
        })
      });
      if (res.ok) {
        setSelectedMeetingId(null);
        setMeetingMinutes('');
        setMeetingActionItems([]);
        fetchExpertData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // --- Triage Inbox Email ---
  const handleTriageEmail = async (emailId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/inbox/${emailId}/triage`, {
        method: 'POST'
      });
      if (res.ok) {
        setSelectedEmail(null);
        fetchExpertData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchEmailReplies = async (emailId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/inbox/${emailId}/replies`);
      if (res.ok) {
        setInboxReplies(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLessons = async () => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/lessons`);
      if (res.ok) {
        setAgentLessons(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLegalLibrary = async () => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/lessons/legal_library`);
      if (res.ok) {
        setLegalLibrary(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddLesson = async () => {
    if (!newLessonNotes.trim()) return;
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/lessons/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: newLessonDomain, feedback_notes: newLessonNotes })
      });
      if (res.ok) {
        setNewLessonNotes('');
        await fetchLessons();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTriggerSelfImprovement = async () => {
    setSimIsRunning(true);
    setSimLogs(["[System] Dispatching trigger payload to LangGraph engine..."]);
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/lessons/trigger_improvement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          trigger_type: simTriggerType,
          trigger_data: simTriggerData
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSimLogs(data.logs);
        fetchLessons(); // Refresh memory list
      } else {
        setSimLogs(prev => [...prev, "[Error] Failed to execute self-critique loop on host gateway."]);
      }
    } catch (err) {
      setSimLogs(prev => [...prev, `[Error] ${err.toString()}`]);
    } finally {
      setSimIsRunning(false);
    }
  };

  const handleSendReply = async (emailId) => {
    if (!replyBody.trim()) return;
    try {
      const res = await kiboFetch(`${API_BASE}/api/expert/inbox/${emailId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ body: replyBody })
      });
      if (res.ok) {
        setReplyBody('');
        await fetchEmailReplies(emailId);
        fetchExpertData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // --- AI Onboarding Agent Handlers ---
  const handleStartOnboarding = async () => {
    setOnbStatus('ingesting');
    setOnbProgress(0.05);
    setOnbLogs(['[System Orchestrator] Initializing AI Onboarding Agent session...']);
    try {
      const startRes = await kiboFetch(`${API_BASE}/api/onboarding/start`, {
        method: 'POST',
        body: JSON.stringify({
          client_id: "KHP-Default",
          urls: [onbWebsiteUrl],
          files: onbUploadedFiles.length > 0 
            ? onbUploadedFiles.map(f => f.name) 
            : ["Data Governance Policy.docx", "Terms of Reference.docx", "Data Inventory.xlsx", "Information Management Policy.docx", "Risk Register.xlsx", "Privacy Policy.docx"]
        })
      });
      if (startRes.ok) {
        const startData = await startRes.json();
        const sid = startData.session_id;
        setOnbSessionId(sid);
        
        setOnbLogs(prev => [...prev, `[System Orchestrator] Session ${sid} created. Triggering website extraction...`]);
        const webRes = await kiboFetch(`${API_BASE}/api/onboarding/${sid}/website`, { method: 'POST' });
        if (webRes.ok) {
          const webData = await webRes.json();
          setOnbLogs(prev => [...prev, ...webData.logs]);
          setOnbProgress(0.30);
          
          setOnbLogs(prev => [...prev, `[System Orchestrator] Website crawl complete. Ingesting compliance documents and data inventory...`]);
          const docRes = await kiboFetch(`${API_BASE}/api/onboarding/${sid}/documents`, { method: 'POST' });
          if (docRes.ok) {
            const docData = await docRes.json();
            setOnbLogs(prev => [...prev, ...docData.logs]);
            setOnbProgress(0.85);
            setOnbStatus('gap_review');
            
            const profRes = await kiboFetch(`${API_BASE}/api/onboarding/${sid}/profile`);
            if (profRes.ok) setOnbProfile(await profRes.json());
            
            const gapsRes = await kiboFetch(`${API_BASE}/api/onboarding/${sid}/gaps`);
            if (gapsRes.ok) setOnbGaps(await gapsRes.json());
          }
        }
      }
    } catch (e) {
      console.error(e);
      setOnbLogs(prev => [...prev, `[ERROR] Onboarding failed: ${e.message}`]);
      setOnbStatus('idle');
    }
  };

  const handleResolveOnbGap = async (gapId, decision, value) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/onboarding/${onbSessionId}/gaps/${gapId}`, {
        method: 'POST',
        body: JSON.stringify({ decision, value })
      });
      if (res.ok) {
        setOnbGaps(prev => prev.map(g => g.id === gapId ? { ...g, status: decision } : g));
        
        const profRes = await kiboFetch(`${API_BASE}/api/onboarding/${onbSessionId}/profile`);
        if (profRes.ok) setOnbProfile(await profRes.json());
        
        const statusRes = await kiboFetch(`${API_BASE}/api/onboarding/${onbSessionId}/status`);
        if (statusRes.ok) {
          const sData = await statusRes.json();
          setOnbLogs(sData.logs);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleFinalizeOnbProfile = async () => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/onboarding/${onbSessionId}/finalize`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setOnbProfile(data.profile);
        setOnbStatus('validated');
        setOnbProgress(1.0);
        setOnbLogs(prev => [...prev, `[System] ONBOARDING COMPLETE. Baseline profile validated successfully.`]);
        alert("Organizational profile committed to downstream compliance pipelines!");
      }
    } catch (e) {
      console.error(e);
    }
  };

  // --- Agentic CPO Console Event Simulator ---
  const handleTriggerAgenticEvent = async (eventType) => {
    if (isSimulatingLoop) return;
    setIsSimulatingLoop(true);
    setAgentLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ⚡ Event Triggered: ${eventType}`]);

    const addLog = (msg) => {
      setAgentLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
    };

    let agentIdMap = {
      'git_push': 'regulatory',
      'dsar_filed': 'internal',
      'vendor_dpa': 'vendor',
      'siem_anomaly': 'threat'
    };
    
    const targetAgentId = agentIdMap[eventType] || 'regulatory';
    
    try {
      const res = await kiboFetch(`${API_BASE}/api/agents/sensing/${targetAgentId}/run`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        let delay = 0;
        data.logs.forEach(logLine => {
          setTimeout(() => {
            addLog(logLine);
          }, delay);
          delay += 800;
        });
        
        setTimeout(async () => {
          await fetchAgenticData();
          setIsSimulatingLoop(false);
        }, delay);
      } else {
        addLog(`[ERROR] Failed to execute sensing agent: ${res.status}`);
        setIsSimulatingLoop(false);
      }
    } catch (e) {
      addLog(`[ERROR] Connection error: ${e.message}`);
      setIsSimulatingLoop(false);
    }
  };

  const handleResolveHitlDecision = async (hitlId, action) => {
    try {
      const res = await kiboFetch(`${API_BASE}/api/knowledge/updates/${hitlId}/decision`, {
        method: 'POST',
        body: JSON.stringify({
          decision: action === 'approved' ? 'accept' : 'reject',
          notes: `Decision resolved by DPO as ${action}`
        })
      });
      if (res.ok) {
        setHitlQueue(prev => prev.map(item => item.id === hitlId ? { ...item, status: action } : item));
        setAgentLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ✅ DPO completed decision ${hitlId}: ${action.toUpperCase()}`]);
        await fetchAgenticData();
      }
    } catch (e) {
      console.error("Error resolving hitl decision:", e);
    }
  };

  // --- Remind/Assign Training (Expert Admin) ---
  const handleTriggerTrainingAction = async (action) => {
    try {
      await kiboFetch(`${API_BASE}/api/expert/training/${action}`, { method: 'POST' });
      fetchExpertData();
      alert(`Action '${action}' completed successfully.`);
    } catch (err) {
      console.error(err);
    }
  };

  // --- Submit PSR Recommendation ---
  const handlePsrRecommendationSubmit = async (e) => {
    e.preventDefault();
    if (!psrSelectedRisk || !psrRecommendation) return;
    try {
      const res = await kiboFetch(`${API_BASE}/api/psr/risk/${psrSelectedRisk.risk_id}/recommendation`, {
        method: 'POST',
        body: JSON.stringify({
          risk_id: psrSelectedRisk.risk_id,
          member: "PSR Member Betty",
          vote: psrVote,
          recommendation: psrRecommendation
        })
      });
      if (res.ok) {
        setPsrRecommendation('');
        setPsrSelectedRisk(null);
        fetchPsrData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="w-full h-screen bg-[#FAFAFA] text-[#111827] flex flex-col overflow-hidden">
      
      {/* HEADER */}
      <header className="w-full border-b border-[#E5E7EB] px-6 py-4 bg-white flex items-center justify-between shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 text-white px-3 py-1.5 rounded-lg font-bold tracking-tight text-sm flex items-center space-x-1.5 shadow-sm">
            <Shield size={16} />
            <span>KIBO.IS</span>
          </div>
          <span className="text-[10px] text-gray-400 font-semibold tracking-wider uppercase">Compliance Gateway</span>
        </div>

        {/* Global Selectors */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2 relative group">
            <Globe size={14} className="text-blue-600" />
            <div className="relative">
              <button className="bg-white border border-[#E5E7EB] text-xs text-[#111827] px-3 py-1.5 rounded-lg focus:outline-none transition-all cursor-pointer shadow-xs flex items-center space-x-2">
                <span className="font-semibold text-gray-800">Active Regs ({activeLegislations.length})</span>
                <span className="text-[10px] text-gray-400">▼</span>
              </button>
              
              <div className="absolute right-0 mt-1 w-64 bg-white border border-[#E5E7EB] rounded-xl shadow-xl p-3 z-50 hidden group-hover:block hover:block">
                <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Scope Active Legislations</div>
                <div className="space-y-2">
                  {jurisdictionsList.map(j => {
                    const isChecked = activeLegislations.includes(j.code);
                    return (
                      <label key={j.code} className="flex items-center space-x-2.5 text-xs text-gray-700 cursor-pointer hover:text-[#111827] select-none">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {
                            let next;
                            if (isChecked) {
                              next = activeLegislations.filter(x => x !== j.code);
                            } else {
                              next = [...activeLegislations, j.code];
                            }
                            if (next.length === 0) return; // keep at least one
                            setActiveLegislations(next);
                            setActiveJurisdiction(next[0]);
                            handleJurisdictionChange(next[0]);
                          }}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="font-medium">{j.flag} {j.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <User size={14} className="text-blue-600" />
            <select
              value={securityMode}
              onChange={(e) => setSecurityMode(e.target.value)}
              className="bg-white border border-[#E5E7EB] text-xs text-[#111827] px-3 py-1.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all cursor-pointer shadow-xs"
            >
              <option value="expert">Expert Mode (Super User)</option>
              <option value="employee">Employee Mode</option>
              <option value="psr">PSR Committee Member</option>
              <option value="public">Public Widget</option>
              <option value="admin">System Administration (AI Ops)</option>
            </select>
          </div>
        </div>
      </header>

      {/* OFFLINE BANNER */}
      {!isSystemOnline && (
        <div className="bg-rose-50 border-b border-rose-200 text-rose-800 px-6 py-2.5 text-xs flex justify-between items-center font-medium transition-all duration-300">
          <div className="flex items-center space-x-2">
            <AlertTriangle size={14} className="text-rose-600 animate-pulse" />
            <span>GATEWAY OFFLINE: PIPELINE SUSPENDED (SLA countdowns paused)</span>
          </div>
          <button 
            onClick={async () => {
              await fetchJurisdictions();
              await fetchActiveJurisdictionConfig(activeJurisdiction);
              if (securityMode === 'employee') fetchEmployeeData();
              else if (securityMode === 'expert') fetchExpertData();
              else if (securityMode === 'psr') fetchPsrData();
              else if (securityMode === 'admin') {
                fetchExpertData();
                fetchLessons();
                fetchLegalLibrary();
              }
            }}
            className="bg-white hover:bg-rose-100 border border-rose-300 text-rose-800 px-3 py-1 rounded shadow-xs text-[10px] transition-all cursor-pointer font-semibold"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* BODY CONTENT */}
      <div className="flex-1 flex overflow-hidden">

        {/* PUBLIC WIDGET MODE */}
        {securityMode === 'public' && (
          <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#F9FAFB] overflow-y-auto">
            <div className="w-full max-w-2xl bg-white border border-[#E5E7EB] rounded-2xl p-8 shadow-xs space-y-6">
              
              <div className="border-b border-[#E5E7EB] pb-5 text-center">
                <div className="text-blue-650 font-semibold text-[11px] uppercase tracking-widest">Embeddable Client Privacy Portal</div>
                <h1 className="text-2xl font-extrabold text-[#111827] mt-2 tracking-tight">KIBO Secure Compliance Widget</h1>
                <p className="text-xs text-gray-500 mt-2 leading-relaxed">
                  Renders as: <code className="bg-gray-100 px-2 py-0.5 rounded text-blue-600 text-[11px] font-mono">[kibo_privacy_widget jurisdiction="{activeJurisdiction}"]</code>
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                {/* Left side: Request Submission */}
                <div className="space-y-4">
                  <div className="text-xs text-[#111827] font-semibold border-b border-[#E5E7EB] pb-2">
                    File a new {jurConfig.access_request_abbr}
                  </div>
                  
                  <form onSubmit={handlePublicSubmit} className="space-y-3.5">
                    <div>
                      <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Your Full Name</label>
                      <input 
                        type="text" 
                        required 
                        value={widgetName}
                        onChange={(e) => setWidgetName(e.target.value)}
                        className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Email Address</label>
                      <input 
                        type="email" 
                        required 
                        value={widgetEmail}
                        onChange={(e) => setWidgetEmail(e.target.value)}
                        className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                        placeholder="john@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Request Type</label>
                      <select 
                        value={widgetType} 
                        onChange={(e) => setWidgetType(e.target.value)}
                        className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all cursor-pointer shadow-xs"
                      >
                        <option value="access">Access Personal Data</option>
                        <option value="deletion">Delete Personal Data</option>
                        <option value="opt-out">Opt-out of Profiling</option>
                        <option value="correction">Correct Data</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Request Specifications</label>
                      <textarea 
                        required
                        value={widgetDesc}
                        onChange={(e) => setWidgetDesc(e.target.value)}
                        className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg h-20 resize-none transition-all shadow-xs" 
                        placeholder="Details..."
                      />
                    </div>
                    <button 
                      type="submit" 
                      disabled={!isSystemOnline}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSystemOnline ? `Submit ${jurConfig.access_request_abbr}` : "Offline - Submission Blocked"}
                    </button>
                  </form>

                  {widgetStatus === 'success' && (
                    <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 text-[11px] rounded-lg space-y-1">
                      <div>✓ Request registered successfully.</div>
                      <div className="font-bold font-mono">Thread ID: {widgetTrackId}</div>
                    </div>
                  )}
                  {widgetStatus === 'error' && (
                    <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 text-[11px] rounded-lg">
                      ✕ Submission failed. Gatekeeper error.
                    </div>
                  )}
                </div>

                {/* Right side: Check Status & Info */}
                <div className="space-y-4">
                  <div className="text-xs text-[#111827] font-semibold border-b border-[#E5E7EB] pb-2">
                    Track Request Status
                  </div>
                  
                  <form onSubmit={handleWidgetCheckStatus} className="flex space-x-2">
                    <input 
                      type="text" 
                      required 
                      value={widgetCheckId}
                      onChange={(e) => setWidgetCheckId(e.target.value)}
                      placeholder="e.g. REQ-A12B34" 
                      className="flex-1 bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 px-3 py-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs"
                    />
                    <button type="submit" disabled={!isSystemOnline} className="bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] px-4 py-2 text-xs rounded-lg transition-all cursor-pointer shadow-xs disabled:opacity-50 disabled:cursor-not-allowed">
                      Track
                    </button>
                  </form>

                  {widgetCheckResult && (
                    <div className="bg-gray-50 border border-[#E5E7EB] p-4 rounded-xl text-[12px] space-y-2 text-gray-700">
                      <div className="text-blue-600 font-bold uppercase tracking-wide">Live Status Output:</div>
                      <div>ID: <span className="text-gray-900 font-mono">{widgetCheckResult.id}</span></div>
                      <div>Status: <span className="text-gray-900 font-medium">{widgetCheckResult.status}</span></div>
                      <div>SLA Limit: <span className="text-gray-900 font-medium">{widgetCheckResult.deadline}</span></div>
                    </div>
                  )}

                  <div className="border border-[#E5E7EB] p-4 bg-gray-50/50 rounded-xl text-[12px] space-y-2.5 text-gray-750">
                    <div className="text-gray-900 uppercase font-bold">Regulatory Notice</div>
                    <div>Statute: <span className="text-blue-600 font-medium">{jurConfig.primary_statute}</span></div>
                    <div>Regulator: <span className="text-gray-900">{jurConfig.regulator}</span></div>
                    <div>Max Response Clock: <span className="text-gray-900 font-medium">{jurConfig.access_deadline_days} Days</span></div>
                  </div>
                </div>

              </div>

            </div>
          </div>
        )}

        {/* EMPLOYEE MODE */}
        {securityMode === 'employee' && (
          <div className="flex-1 flex overflow-hidden bg-[#FAFAFA]">
            
            {/* Left side: My Risks & Training */}
            <div className="w-1/2 border-r border-[#E5E7EB] p-6 flex flex-col space-y-6 overflow-y-auto">
              
              {/* Risks Section */}
              <div className="space-y-3.5">
                <div className="text-xs font-bold uppercase tracking-wider text-gray-550">My Assigned Compliance Risks</div>
                <div className="space-y-2.5">
                  {employeeRisks.length === 0 ? (
                    <div className="text-xs text-gray-400 italic">No risks currently assigned.</div>
                  ) : (
                    employeeRisks.map(r => (
                      <div key={r.risk_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl text-[12px] space-y-2 shadow-xs">
                        <div className="flex justify-between items-center">
                          <span className="text-blue-600 font-bold font-mono">{r.risk_id}</span>
                          <span className={`px-2 py-0.5 text-[9px] rounded-full uppercase font-bold border ${
                            r.risk_level === 'High' ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-amber-50 text-amber-700 border-amber-200'
                          }`}>{r.risk_level}</span>
                        </div>
                        <div className="text-[#111827]">{r.issue}</div>
                        <div className="flex justify-between text-gray-500 pt-2 text-[10px] border-t border-[#E5E7EB]">
                          <span>SLA Clock: {r.due_date}</span>
                          <span className="uppercase text-blue-600 font-semibold">Status: {r.status}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Training Section */}
              <div className="space-y-3.5">
                <div className="text-xs font-bold uppercase tracking-wider text-gray-550">Assigned Role-Based Training ({jurConfig.primary_statute} Track)</div>
                <div className="space-y-2.5">
                  {employeeTraining.map(mod => (
                    <div key={mod.module_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl text-[12px] flex items-center justify-between shadow-xs">
                      <div className="space-y-1">
                        <div className="font-semibold text-[#111827]">{mod.title}</div>
                        <div className="text-gray-500 text-[10px]">
                          Required: {mod.required ? 'YES' : 'NO'} | Duration: {mod.duration_min} min | Target: {mod.jurisdiction.toUpperCase()}
                        </div>
                      </div>
                      <div>
                        {mod.completed ? (
                          <span className="text-emerald-600 flex items-center space-x-1.5 font-semibold">
                            <Check size={14} />
                            <span>Done</span>
                          </span>
                        ) : (
                          <button
                            onClick={() => handleCompleteTraining(mod.module_id)}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-3 py-1.5 text-[9px] uppercase rounded-lg shadow-sm transition-all cursor-pointer"
                          >
                            Mark Done
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Right side: Data Inventory Contribution Form */}
            <div className="w-1/2 p-6 overflow-y-auto space-y-4">
              <div className="text-xs font-bold uppercase tracking-wider text-gray-555">Data Inventory Contribution</div>
              <p className="text-xs text-gray-500 leading-relaxed">
                KIBO tracks all organizational storage systems. Log any files, systems, or tools that contain customer or employee datasets under your management.
              </p>
              
              <form onSubmit={handleInventorySubmit} className="space-y-4 max-w-md bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs">
                <div>
                  <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">System/Database Name</label>
                  <input 
                    type="text" 
                    required 
                    value={inventorySystem}
                    onChange={(e) => setInventorySystem(e.target.value)}
                    className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                    placeholder="e.g. Clinical Records Cloud Store"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Data Types (Comma-separated)</label>
                  <input 
                    type="text" 
                    required 
                    value={inventoryDataTypes}
                    onChange={(e) => setInventoryDataTypes(e.target.value)}
                    className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                    placeholder="e.g. IP Address, Medical History, Full Name"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Purpose of Collection</label>
                  <textarea 
                    required 
                    value={inventoryPurpose}
                    onChange={(e) => setInventoryPurpose(e.target.value)}
                    className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-16 resize-none transition-all shadow-xs" 
                    placeholder="Provide description..."
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Retention Rule</label>
                    <input 
                      type="text" 
                      required 
                      value={inventoryRetention}
                      onChange={(e) => setInventoryRetention(e.target.value)}
                      className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                      placeholder="e.g. 5 years"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Sharing / Third-Party Outflow</label>
                    <input 
                      type="text" 
                      required 
                      value={inventorySharing}
                      onChange={(e) => setInventorySharing(e.target.value)}
                      className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg transition-all shadow-xs" 
                      placeholder="e.g. AnalyticsPro Inc."
                    />
                  </div>
                </div>
                <button 
                  type="submit" 
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer"
                >
                  Submit to Central Inventory
                </button>
              </form>

              {inventoryStatus === 'success' && (
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 text-[11px] rounded-lg font-semibold max-w-md">
                  ✓ Inventory logged. Central system catalog updated.
                </div>
              )}

            </div>

          </div>
        )}
        {/* SYSTEM ADMIN MODE */}
        {securityMode === 'admin' && (
          <AdminDashboard
            API_BASE={API_BASE}
            activeJurisdiction={activeJurisdiction}
            jurConfig={jurConfig}
            legalLibrary={legalLibrary}
            agentLessons={agentLessons}
            fetchLessons={fetchLessons}
            fetchLegalLibrary={fetchLegalLibrary}
            simLogs={simLogs}
            simIsRunning={simIsRunning}
            setSimLogs={setSimLogs}
            setSimIsRunning={setSimIsRunning}
          />
        )}
        {/* EXPERT MODE */}
        {securityMode === 'expert' && (
          <div className="flex-1 flex overflow-hidden">
            
            {/* Sidebar Tabs */}
            <div className="w-56 bg-white border-r border-[#E5E7EB] p-4 flex flex-col justify-between">
              <nav className="space-y-1.5">
                <button 
                  onClick={() => setActiveTab('dashboard')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'dashboard' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Activity size={14} />
                  <span>Dashboard</span>
                </button>
                <button 
                  onClick={() => setActiveTab('cpo_agents')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'cpo_agents' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Sparkles size={14} className="text-blue-650 animate-pulse" />
                  <span className="font-semibold text-blue-755">CPO Agents Console</span>
                </button>
                <button 
                  onClick={() => setActiveTab('inbox')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'inbox' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Mail size={14} />
                  <span>Privacy Inbox</span>
                </button>
                <button 
                  onClick={() => setActiveTab('meetings')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'meetings' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Users size={14} />
                  <span>Meetings Planner</span>
                </button>
                <button 
                  onClick={() => setActiveTab('training_admin')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'training_admin' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Briefcase size={14} />
                  <span>Training Admin</span>
                </button>

                {(activeJurisdiction === 'canada' || activeJurisdiction === 'quebec' || activeJurisdiction === 'ontario') && (
                  <button 
                    onClick={() => setActiveTab('onboarding')}
                    className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                      activeTab === 'onboarding' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                    }`}
                  >
                    <List size={14} />
                    <span>Onboarding Checklist</span>
                  </button>
                )}
              </nav>

              <div className="border-t border-[#E5E7EB] pt-4 space-y-3">
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3 space-y-1.5 shadow-2xs">
                  <div className="text-[10px] font-bold text-indigo-900 uppercase tracking-wider flex items-center space-x-1.5">
                    <Shield size={11} className="text-indigo-600 animate-pulse" />
                    <span>Jurisdiction Status Overlay</span>
                  </div>
                  <div className="flex justify-between items-center text-[10px] font-semibold text-gray-700">
                    <span>Active Regime:</span>
                    <span className="bg-indigo-100 text-indigo-850 px-1.5 py-0.5 rounded font-bold uppercase font-mono">{activeJurisdiction}</span>
                  </div>
                  <div className="text-[9px] text-gray-400 space-y-1 font-mono leading-relaxed border-t border-indigo-100 pt-1.5">
                    <div>Statute: {jurConfig.primary_statute}</div>
                    <div>Regulator: {jurConfig.regulator}</div>
                    <div>Deadline: {jurConfig.access_deadline_days} days</div>
                    <div>Logical Lint: {activeJurisdiction}_rules.json</div>
                  </div>
                </div>
              </div>
            </div>

            {/* TAB CONTENT PANEL */}
            <div className="flex-1 p-6 overflow-y-auto space-y-6 bg-[#FAFAFA]">

              {activeTab === 'cpo_agents' && (
                <div className="space-y-6">
                  {/* Title Header */}
                  <div className="space-y-1">
                    <h1 className="text-lg font-bold text-[#111827] flex items-center space-x-2">
                      <Sparkles size={18} className="text-blue-600" />
                      <span>Autonomous CPO Agentic Control Center</span>
                    </h1>
                    <p className="text-xs text-gray-500 max-w-2xl leading-relaxed">
                      Maintains continuous compliance monitoring and enforcement by orchestrating specialized agents across data lifecycle steps, matching GDPR, PIPEDA, Law 25, and ISO 27701 frameworks.
                    </p>
                  </div>

                  {/* Main Grid: Agents & Controls */}
                  <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                    
                    {/* Left Column: CPO Agent Ontology (2/3 width) */}
                    <div className="xl:col-span-2 space-y-4">
                      <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center space-x-1.5">
                        <Server size={14} className="text-blue-600" />
                        <span>Active CPO Agent Ontology</span>
                      </h2>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {agentsList.map(a => (
                          <div key={a.id} className="bg-white border border-[#E5E7EB] p-4.5 rounded-xl space-y-3 hover:border-gray-300 transition-all shadow-xs flex flex-col justify-between">
                            <div className="space-y-2">
                              <div className="flex justify-between items-start">
                                <span className="font-semibold text-[#111827] text-xs">{a.name}</span>
                                <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${
                                  a.status === 'Active' || a.status === 'Running'
                                    ? 'bg-blue-50 border-blue-200 text-blue-700 animate-pulse'
                                    : a.status === 'Monitoring' || a.status === 'Listening'
                                    ? 'bg-emerald-50 border-emerald-250 text-emerald-700 font-semibold'
                                    : 'bg-gray-50 border-gray-200 text-gray-500'
                                }`}>
                                  {a.status}
                                </span>
                              </div>
                              <p className="text-[10px] text-gray-400 font-medium">Focus: {a.focus}</p>
                            </div>
                            <div className="bg-gray-50 p-2.5 rounded-lg border border-gray-100 mt-2">
                              <div className="text-[9px] text-gray-450 uppercase font-bold tracking-wider mb-0.5">Last System Action:</div>
                              <div className="text-[11px] text-gray-700 font-medium leading-relaxed font-mono">{a.lastAction}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Right Column: Execution Triggers & Loop Trace (1/3 width) */}
                    <div className="space-y-6">
                      
                      {/* Section: Simulator */}
                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                        <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center space-x-1.5">
                          <Radio size={14} className="text-blue-600" />
                          <span>Simulate Event Triggers</span>
                        </h2>
                        <p className="text-[11px] text-gray-500 leading-relaxed">
                          Trigger events to fire the event-driven orchestration loop. Agents will auto-triage and queue human approvals.
                        </p>
                        <div className="space-y-2 pt-1">
                          <button
                            onClick={() => handleTriggerAgenticEvent('git_push')}
                            disabled={isSimulatingLoop || !isSystemOnline}
                            className="w-full bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] py-2 px-3 rounded-lg text-xs font-semibold text-left transition-all flex items-center justify-between cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span>⚡ Git Commit Push (Code Audit)</span>
                            <ChevronDown size={12} className="text-gray-400" />
                          </button>
                          <button
                            onClick={() => handleTriggerAgenticEvent('dsar_filed')}
                            disabled={isSimulatingLoop || !isSystemOnline}
                            className="w-full bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] py-2 px-3 rounded-lg text-xs font-semibold text-left transition-all flex items-center justify-between cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span>📥 DSAR Filed (Data Deletion)</span>
                            <ChevronDown size={12} className="text-gray-400" />
                          </button>
                          <button
                            onClick={() => handleTriggerAgenticEvent('vendor_dpa')}
                            disabled={isSimulatingLoop || !isSystemOnline}
                            className="w-full bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] py-2 px-3 rounded-lg text-xs font-semibold text-left transition-all flex items-center justify-between cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span>📄 Third-Party DPA Uploaded</span>
                            <ChevronDown size={12} className="text-gray-400" />
                          </button>
                          <button
                            onClick={() => handleTriggerAgenticEvent('siem_anomaly')}
                            disabled={isSimulatingLoop || !isSystemOnline}
                            className="w-full bg-white hover:bg-gray-100 text-gray-700 border border-[#E5E7EB] py-2 px-3 rounded-lg text-xs font-semibold text-left transition-all flex items-center justify-between cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span>🚨 SIEM Data Anomaly Detected</span>
                            <ChevronDown size={12} className="text-gray-400" />
                          </button>
                        </div>
                      </div>

                      {/* Section: Live Trace Console */}
                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                        <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider flex items-center space-x-1.5">
                          <Terminal size={14} className="text-blue-600" />
                          <span>Orchestration Loop Trace</span>
                        </h2>
                        <div className="bg-gray-900 text-emerald-400 p-4 rounded-lg font-mono text-[10px] h-48 overflow-y-auto space-y-1.5 shadow-inner">
                          {agentLogs.map((log, index) => (
                            <div key={index} className="leading-normal">{log}</div>
                          ))}
                          {isSimulatingLoop && (
                            <div className="text-blue-400 animate-pulse">Running CPO Orchestration State Machine...</div>
                          )}
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* Bottom Panel: Human-in-the-Loop (HITL) Queue */}
                  <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                    <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-3">
                      <div>
                        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                          <UserCheck size={14} className="text-blue-600" />
                          <span>HITL Compliance Action Queue</span>
                        </h2>
                        <p className="text-[10px] text-gray-500 mt-1">
                          Decisions flagged by CPO Agents requiring mandatory human sign-off before operational execution.
                        </p>
                      </div>
                      <span className="text-[10px] font-bold bg-amber-50 border border-amber-250 text-amber-700 px-2.5 py-0.5 rounded-full">
                        {hitlQueue.filter(h => h.status === 'pending').length} Actions Pending
                      </span>
                    </div>

                    <div className="border border-[#E5E7EB] rounded-xl overflow-hidden">
                      <table className="w-full text-xs text-left border-collapse bg-white">
                        <thead>
                          <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[11px] uppercase tracking-wider">
                            <th className="p-3.5 w-24">ID</th>
                            <th className="p-3.5 w-1/4">Action Title</th>
                            <th className="p-3.5 w-44">Trigger Agent</th>
                            <th className="p-3.5">Details</th>
                            <th className="p-3.5 w-20">Priority</th>
                            <th className="p-3.5 w-52 text-right">Human Override Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#E5E7EB]">
                          {hitlQueue.length === 0 ? (
                            <tr>
                              <td colSpan="6" className="p-8 text-center text-gray-500 italic">No actions pending. All systems in compliance.</td>
                            </tr>
                          ) : (
                            hitlQueue.map(h => (
                              <tr key={h.id} className="hover:bg-gray-50/50 transition-all">
                                <td className="p-3.5 font-bold text-gray-400 font-mono">{h.id}</td>
                                <td className="p-3.5 font-semibold text-gray-900">{h.title}</td>
                                <td className="p-3.5 text-blue-650 font-medium">{h.agent}</td>
                                <td className="p-3.5 text-gray-600 leading-normal">{h.details}</td>
                                <td className="p-3.5">
                                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${
                                    h.priority === 'high' ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
                                  }`}>
                                    {h.priority}
                                  </span>
                                </td>
                                <td className="p-3.5 text-right">
                                  {h.status === 'pending' ? (
                                    <div className="flex justify-end space-x-1.5">
                                      <button
                                        onClick={() => handleResolveHitlDecision(h.id, 'approved')}
                                        disabled={!isSystemOnline}
                                        className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded font-semibold text-[10px] uppercase transition-all shadow-xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                      >
                                        Approve
                                      </button>
                                      <button
                                        onClick={() => handleResolveHitlDecision(h.id, 'legal')}
                                        disabled={!isSystemOnline}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1 rounded font-semibold text-[10px] uppercase transition-all shadow-xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                      >
                                        Flag Legal
                                      </button>
                                      <button
                                        onClick={() => handleResolveHitlDecision(h.id, 'rejected')}
                                        disabled={!isSystemOnline}
                                        className="bg-rose-600 hover:bg-rose-700 text-white px-2.5 py-1 rounded font-semibold text-[10px] uppercase transition-all shadow-xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                      >
                                        Reject
                                      </button>
                                    </div>
                                  ) : (
                                    <span className={`px-2.5 py-1 rounded text-[10px] font-bold uppercase tracking-wider border ${
                                      h.status === 'approved'
                                        ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
                                        : h.status === 'legal'
                                        ? 'bg-blue-50 border-blue-200 text-blue-700'
                                        : 'bg-rose-50 border-rose-300 text-rose-700'
                                    }`}>
                                      {h.status === 'approved' ? '✓ APPROVED & DEPLOYED' : h.status === 'legal' ? '⚖ SENT TO LEGAL' : '✕ REJECTED & BLOCKED'}
                                    </span>
                                  )}
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>

                </div>
              )}

              {activeTab === 'dashboard' && (
                <div className="space-y-6">
                  
                  {/* Summary / Indicators Bar */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    
                    <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-1.5">
                      <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Statutory SLA Clock</div>
                      <div className="flex items-center space-x-2">
                        <Clock size={16} className={`animate-pulse ${jurConfig.code === 'eu' ? 'text-rose-600' : 'text-blue-600'}`} />
                        <span className="text-lg font-extrabold text-[#111827]">
                          {jurConfig.code === 'eu' ? '72 Hours' : `${jurConfig.access_deadline_days} Days`}
                        </span>
                      </div>
                      <div className="text-[9px] text-gray-400">
                        {jurConfig.code === 'eu' ? 'Supervisory Authority Notification Window' : `Response deadline for active ${jurConfig.access_request_abbr} requests.`}
                      </div>
                    </div>

                    <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-1.5">
                      <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Onboarding Gaps</div>
                      <div className="flex items-center space-x-2">
                        <AlertTriangle size={16} className="text-amber-500" />
                        <span className="text-lg font-extrabold text-[#111827]">{onbGaps.filter(g => g.status === 'pending').length} Actionable</span>
                      </div>
                      <div className="text-[9px] text-gray-400">Gaps in organizational profile awaiting validation.</div>
                    </div>

                    <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-1.5">
                      <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">HITL Queue Tasks</div>
                      <div className="flex items-center space-x-2">
                        <ShieldAlert size={16} className="text-rose-500" />
                        <span className="text-lg font-extrabold text-[#111827]">{hitlQueue.filter(h => h.status === 'pending').length} Decisions</span>
                      </div>
                      <div className="text-[9px] text-gray-400">Agent audits and policy overrides pending CPO sign-off.</div>
                    </div>

                    <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs space-y-1.5">
                      <div className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Unread Inbox Intake</div>
                      <div className="flex items-center space-x-2">
                        <Mail size={16} className="text-blue-600" />
                        <span className="text-lg font-extrabold text-[#111827]">{inboxEmails.filter(e => e.status === 'unread').length} Inquiries</span>
                      </div>
                      <div className="text-[9px] text-gray-400">Direct user requests or regulator letters requiring triage.</div>
                    </div>

                  </div>

                  {/* Jurisdictional High-Priority Indicators (Dynamic) */}
                  <div className="bg-indigo-50/15 border border-indigo-100 p-5 rounded-xl space-y-4">
                    <div className="flex justify-between items-center border-b border-indigo-100 pb-2">
                      <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900 flex items-center space-x-1.5">
                        <ShieldAlert size={14} className="text-indigo-650" />
                        <span>Active Jurisdictional Regs Indicator ({activeJurisdiction.toUpperCase()})</span>
                      </h4>
                      <span className="text-[9px] font-mono text-indigo-700 bg-indigo-100/50 px-2 py-0.5 rounded border border-indigo-200">
                        Primary Logic: {activeJurisdiction}_rules.json
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                      {/* EU/GDPR Cards */}
                      {activeJurisdiction === 'eu' && (
                        <>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Lawful Basis Mapping</span>
                            <div className="text-lg font-bold text-gray-800">Consent (64%) | Legitimate Interest (36%)</div>
                            <p className="text-[10px] text-gray-400">Continuous RoPA scanning matches operational activities to GDPR lawful bases.</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Article 28 DPA Status</span>
                            <div className="text-lg font-bold text-emerald-700">100% Documented</div>
                            <p className="text-[10px] text-gray-400">All data processors signed Standard Contractual Clauses (SCCs).</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">72-Hour SLA Status</span>
                            <div className="text-lg font-bold text-rose-700">0 Breaches Logged</div>
                            <p className="text-[10px] text-gray-400">Statutory notification window monitor to Supervisory Authority is active.</p>
                          </div>
                        </>
                      )}

                      {/* Canada/Law 25 Cards */}
                      {(activeJurisdiction === 'canada' || activeJurisdiction === 'quebec' || activeJurisdiction === 'ontario') && (
                        <>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Provincial Transfer Restrictions</span>
                            <div className="text-lg font-bold text-amber-700">PIAs Pending Review</div>
                            <p className="text-[10px] text-gray-400">Ontario PHIPA & Quebec Law 25 compliance requirements restrict transfer routes.</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">30-Day DSAR SLA Clock</span>
                            <div className="text-lg font-bold text-gray-800">4 Active Countdown Timers</div>
                            <p className="text-[10px] text-gray-400">Strict statutory deadline for response and validation processing.</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">RROSH Breach Threshold</span>
                            <div className="text-lg font-bold text-gray-800">Risk Assessment Score: 0/10</div>
                            <p className="text-[10px] text-gray-400">Real risk of significant harm (RROSH) calculation triggers automatically.</p>
                          </div>
                        </>
                      )}

                      {/* US/CPRA Cards */}
                      {activeJurisdiction === 'us' && (
                        <>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Opt-Out of Sale/Sharing</span>
                            <div className="text-lg font-bold text-blue-700">89% Opt-Out Rate</div>
                            <p className="text-[10px] text-gray-400">CCPA/CPRA Do Not Sell/Share signals parsed from CMP integration.</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Sensitive Data (SPI) Discovery</span>
                            <div className="text-lg font-bold text-gray-800">14 SPI Fields Mapped</div>
                            <p className="text-[10px] text-gray-400">Automated classification of sensitive personal information tags.</p>
                          </div>
                          <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">45-Day SLA Clock</span>
                            <div className="text-lg font-bold text-gray-800">1 Active Request</div>
                            <p className="text-[10px] text-gray-400">US State privacy rules govern response deadlines.</p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Operational Action Center Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left & Middle Column: Gaps & Actions */}
                    <div className="lg:col-span-2 space-y-6">
                      
                      {/* Flagged and Pending tasks requiring action */}
                      <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                          <Activity size={14} className="text-blue-600" />
                          <span>Immediate Attention & Tasks Queue</span>
                        </h3>
                        
                        <div className="space-y-3">
                          {onbGaps.filter(g => g.status === 'pending').map(g => (
                            <div key={g.id} className="p-3.5 rounded-lg border border-amber-200 bg-amber-50/20 flex justify-between items-center gap-4">
                              <div className="space-y-1">
                                <div className="text-xs font-bold text-gray-850 flex items-center space-x-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                  <span>{g.title}</span>
                                </div>
                                <div className="text-[10px] text-gray-550 leading-relaxed">{g.details}</div>
                              </div>
                              <button
                                onClick={() => setActiveTab('onboarding')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-550 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all shadow-xs"
                              >
                                Resolve
                              </button>
                            </div>
                          ))}

                          {hitlQueue.filter(h => h.status === 'pending').map(h => (
                            <div key={h.id} className="p-3.5 rounded-lg border border-rose-200 bg-rose-50/20 flex justify-between items-center gap-4">
                              <div className="space-y-1">
                                <div className="text-xs font-bold text-gray-850 flex items-center space-x-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                                  <span>{h.title}</span>
                                </div>
                                <div className="text-[10px] text-gray-550 leading-relaxed">{h.details}</div>
                              </div>
                              <button
                                onClick={() => setActiveTab('cpo_agents')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-550 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all shadow-xs"
                              >
                                Approve
                              </button>
                            </div>
                          ))}

                          {onbGaps.filter(g => g.status === 'pending').length === 0 && hitlQueue.filter(h => h.status === 'pending').length === 0 && (
                            <div className="p-8 text-center text-xs text-gray-500 italic">
                              ✓ All onboarding gaps and agent decisions resolved. System is aligned with baseline.
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* LOCALIZED JURISDICTION DASHBOARD MODULES */}
                      {activeLegislations.some(x => ['canada', 'quebec', 'ontario'].includes(x)) && (
                        <div className="space-y-6">
                          
                          {/* RROSH Assessment Tool */}
                          <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                              <ShieldAlert size={14} className="text-blue-650" />
                              <span>Canada Breach Triage: RROSH Assessment Builder</span>
                            </h3>
                            <p className="text-xs text-gray-500">
                              Assess if a security incident creates a <strong>"Real Risk of Significant Harm"</strong> (RROSH) under PIPEDA or Quebec Law 25.
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-200">
                              <div className="space-y-1">
                                <span className="text-[10px] uppercase font-bold text-gray-400">Harm Sensitivity</span>
                                <div className="text-xs font-semibold text-gray-800">High (Crisis Chat Logs, Medical)</div>
                              </div>
                              <div className="space-y-1 border-t md:border-t-0 md:border-l border-gray-200 pt-2.5 md:pt-0 md:pl-4">
                                <span className="text-[10px] uppercase font-bold text-gray-400">Misuse Likelihood</span>
                                <div className="text-xs font-semibold text-amber-600">Possible (Unauthorized Access)</div>
                              </div>
                              <div className="space-y-1 border-t md:border-t-0 md:border-l border-gray-200 pt-2.5 md:pt-0 md:pl-4">
                                <span className="text-[10px] uppercase font-bold text-gray-400">RROSH Verdict</span>
                                <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 text-[10px] font-bold border border-rose-200 inline-block mt-0.5">
                                  MANDATORY OPC REPORTING
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Data Transfers and Consent Trackers */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700 flex items-center space-x-1">
                                <Globe size={12} className="text-purple-650" />
                                <span>Quebec/Canada Data Flow Restrictions</span>
                              </h4>
                              <div className="space-y-2 text-xs">
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Aselo/Twilio Chat Route</span>
                                  <span className="text-[10px] font-bold text-rose-600 font-mono">Leaves Quebec (AWS US-East)</span>
                                </div>
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Blackbaud CRM Database</span>
                                  <span className="text-[10px] font-bold text-emerald-600 font-mono">In-Country (Canada East)</span>
                                </div>
                                <div className="text-[10px] text-gray-400 italic">Quebec Law 25 requires a Transfer Impact Assessment (TIA) for out-of-province storage.</div>
                              </div>
                            </div>

                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700">Clear Consent Opt-In Track</h4>
                              <div className="space-y-2">
                                <div className="flex justify-between items-center text-xs">
                                  <span className="text-gray-500 font-semibold">Express Sensitive Opt-In</span>
                                  <span className="font-extrabold text-blue-600">89.4%</span>
                                </div>
                                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                  <div className="bg-blue-600 h-full w-[89.4%]" />
                                </div>
                                <div className="flex justify-between items-center text-xs pt-1">
                                  <span className="text-gray-500 font-semibold">Implied Marketing Opt-Out</span>
                                  <span className="font-extrabold text-amber-600">12.1%</span>
                                </div>
                              </div>
                            </div>

                          </div>
                        </div>
                      )}

                      {/* PHIPA Specific Health Custodian Panel */}
                      {activeLegislations.includes('phipa') && (
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                            <Activity size={14} className="text-emerald-600" />
                            <span>Ontario PHIPA: Health Information Custodian (HIC) Registry</span>
                          </h3>
                          <p className="text-xs text-gray-500">
                            Ensures strict Circle of Care limits are maintained when clinical therapists handle personal health information (PHI).
                          </p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-3.5 bg-emerald-50/20 border border-emerald-250 rounded-lg">
                              <div className="text-[10px] font-bold text-emerald-800 uppercase">Circle of Care Disclosures</div>
                              <div className="text-xs text-gray-700 font-semibold mt-1">Limited to authorized clinical supervisors</div>
                            </div>
                            <div className="p-3.5 bg-gray-50 border border-gray-200 rounded-lg">
                              <div className="text-[10px] font-bold text-gray-500 uppercase">HIC Safety Audits</div>
                              <div className="text-xs text-gray-700 font-semibold mt-1">Passed (Transcripts fully encrypted at rest)</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* CYFSA Specific Youth Consent Panel */}
                      {activeLegislations.includes('cyfsa') && (
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                            <UserCheck size={14} className="text-purple-600" />
                            <span>Ontario CYFSA: Child & Youth Capacity Boundaries</span>
                          </h3>
                          <p className="text-xs text-gray-500">
                            Under the Child, Youth and Family Services Act, service users under the age of 16 possess explicit self-consent capacity for mental health assistance.
                          </p>
                          <div className="p-4 bg-purple-50/20 border border-purple-200 rounded-lg flex justify-between items-center">
                            <div>
                              <div className="text-xs font-bold text-purple-950">Youth Self-Consent Capacity</div>
                              <div className="text-[10px] text-purple-750">Self-consent capacity boundary: 16 years of age</div>
                            </div>
                            <span className="bg-purple-100 text-purple-800 border border-purple-250 text-[10px] font-bold px-2 py-0.5 rounded">
                              ENFORCED AT GATEWAY
                            </span>
                          </div>
                        </div>
                      )}

                      {activeLegislations.includes('us') && (
                        <div className="space-y-6">
                          
                          {/* Multi-State Compliance Scorecard */}
                          <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                              <Globe size={14} className="text-blue-650" />
                              <span>Multi-State Privacy Matrix (US State Legislation)</span>
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              {['California (CPRA)', 'Virginia (VCDPA)', 'Colorado (CPA)', 'Utah (UCPA)'].map((st, idx) => (
                                <div key={st} className="p-3 bg-gray-50/50 rounded-lg border border-gray-200 text-center">
                                  <div className="text-[11px] font-semibold text-gray-800">{st}</div>
                                  <div className={`text-[10px] font-bold mt-1.5 ${idx === 0 ? 'text-blue-600' : 'text-emerald-600'}`}>
                                    {idx === 0 ? 'DPA Under Review' : '✓ Compliant'}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* US Opt-Out & Sensitive Data Widgets */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3.5 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700 flex items-center space-x-1.5">
                                <Activity size={12} className="text-rose-500" />
                                <span>CRR Opt-Out Request Logs</span>
                              </h4>
                              <div className="space-y-3 text-xs">
                                <div className="flex justify-between border-b border-gray-150 pb-2">
                                  <span className="text-gray-600 font-medium">Do Not Sell or Share My Info</span>
                                  <span className="font-bold font-mono text-[#111827]">214 active requests</span>
                                </div>
                                <div className="flex justify-between border-b border-gray-150 pb-2">
                                  <span className="text-gray-600 font-medium">Limit Sensitive Data Usage</span>
                                  <span className="font-bold font-mono text-[#111827]">45 active requests</span>
                                </div>
                                <div className="text-[9px] text-gray-400">California residents have a statutory right to limit the use of Sensitive Personal Information (SPI).</div>
                              </div>
                            </div>

                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700">Sensitive Personal Info (SPI) Scans</h4>
                              <div className="space-y-2 text-xs">
                                <div className="flex justify-between items-center bg-rose-50/50 border border-rose-100 p-2 rounded-lg">
                                  <span className="text-gray-700 font-semibold font-mono text-[10px]">Precise Geolocation Data</span>
                                  <span className="text-[9px] uppercase bg-rose-100 text-rose-800 font-bold px-2 py-0.5 rounded">Opt-In Enforced</span>
                                </div>
                                <div className="flex justify-between items-center bg-gray-50 border border-gray-200 p-2 rounded-lg">
                                  <span className="text-gray-700 font-semibold font-mono text-[10px]">Race & Ethnic Classifiers</span>
                                  <span className="text-[9px] uppercase bg-gray-250 text-gray-600 font-bold px-2 py-0.5 rounded">None Monitored</span>
                                </div>
                              </div>
                            </div>

                          </div>
                        </div>
                      )}

                      {activeLegislations.some(x => ['eu', 'uk'].includes(x)) && (
                        <div className="space-y-6">
                          
                          {/* EU Breach reporting timer */}
                          <div className="bg-rose-50/20 border border-rose-200 p-6 rounded-xl space-y-3.5 shadow-xs">
                            <div className="flex justify-between items-start">
                              <div className="space-y-1">
                                <h3 className="text-xs font-bold uppercase tracking-wider text-rose-800 flex items-center space-x-2">
                                  <ShieldAlert size={14} className="text-rose-600 animate-pulse" />
                                  <span>GDPR Article 33: 72-Hour Breach Clock</span>
                                </h3>
                                <p className="text-xs text-rose-700 leading-relaxed max-w-xl">
                                  GDPR mandates notification to the Supervisory Authority within 72 hours of becoming aware of a personal data breach unless the breach is unlikely to result in a risk.
                                </p>
                              </div>
                              <span className="bg-rose-100 border border-rose-250 text-rose-800 text-[10px] font-mono font-extrabold px-3 py-1 rounded">
                                ACTIVE WINDOW
                              </span>
                            </div>
                          </div>

                          {/* RoPA Completion Bar & Lawful Basis Mappers */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700 flex items-center space-x-1.5">
                                <BookOpen size={12} className="text-blue-650" />
                                <span>Article 30 Record of Processing (RoPA)</span>
                              </h4>
                              <div className="space-y-3 text-xs">
                                <div>
                                  <div className="flex justify-between text-[11px] mb-1 font-semibold text-gray-600">
                                    <span>Clinical Operations RoPA Status</span>
                                    <span className="text-blue-600 font-bold">100%</span>
                                  </div>
                                  <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                                    <div className="bg-blue-600 h-full w-[100%]" />
                                  </div>
                                </div>
                                <div>
                                  <div className="flex justify-between text-[11px] mb-1 font-semibold text-gray-600">
                                    <span>Donor & Fundraising RoPA Status</span>
                                    <span className="text-blue-600 font-bold">45%</span>
                                  </div>
                                  <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                                    <div className="bg-blue-600 h-full w-[45%]" />
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                              <h4 className="text-[11px] font-bold uppercase tracking-wider text-gray-700">Legal Basis of Processing Mapped</h4>
                              <div className="space-y-2 text-xs">
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Legitimate Interest (LI)</span>
                                  <span className="font-extrabold text-blue-600">62% of activities</span>
                                </div>
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Explicit Consent (Art. 6.1a)</span>
                                  <span className="font-extrabold text-blue-600">28% of activities</span>
                                </div>
                                <div className="flex justify-between pb-1">
                                  <span className="text-gray-600 font-medium">Performance of Contract</span>
                                  <span className="font-extrabold text-blue-600">10% of activities</span>
                                </div>
                              </div>
                            </div>

                          </div>
                        </div>
                      )}

                      {/* Active Assessments List */}
                      <div className="space-y-3.5">
                        <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Active {jurConfig.primary_statute} Compliance Assessments</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {expertAssessments.map(a => (
                            <div key={a.assessment_id} className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-2.5 hover:border-gray-300 transition-all shadow-xs">
                              <div className="flex justify-between items-start">
                                <span className="font-semibold text-[#111827] text-xs">{a.title}</span>
                                <span className="text-[9px] bg-blue-50 border border-blue-200 text-blue-650 px-2 py-0.5 rounded-full font-bold">{a.type}</span>
                              </div>
                              <div className="text-[10px] text-gray-550">Prepared by: {a.prepared_by} | Level: {a.level}</div>
                              <div className="flex justify-between items-center text-[10px] pt-2 border-t border-[#E5E7EB]">
                                <span className="text-emerald-700 font-semibold">✓ Status: {a.status}</span>
                                <span className="text-gray-500">Statute: {jurConfig.primary_statute}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                    </div>

                    {/* Right Column: Quick Operations & Blockchain Ledger */}
                    <div className="space-y-6">
                      
                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                          <Settings size={14} className="text-blue-600" />
                          <span>Quick Operations</span>
                        </h3>
                        
                        <div className="space-y-2">
                          <button
                            onClick={async () => {
                              const res = await kiboFetch(`${API_BASE}/api/expert/audit`, { method: 'POST' });
                              if (res.ok) alert("Audit session initialized on the blockchain ledger.");
                            }}
                            className="w-full text-left bg-white hover:bg-gray-550 text-gray-755 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
                          >
                            <span>Run Blockchain Activities Audit</span>
                            <span className="text-[9px] text-gray-400 font-mono">POST /audit</span>
                          </button>

                          <button
                            onClick={async () => {
                              const res = await kiboFetch(`${API_BASE}/api/expert/soc-compliance`, { method: 'POST' });
                              if (res.ok) {
                                const data = await res.json();
                                alert(`SOC Compliance Scan Status: ${data.status}`);
                              }
                            }}
                            className="w-full text-left bg-white hover:bg-gray-550 text-gray-755 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
                          >
                            <span>Evaluate SOC 1/SOC 2 Matrix</span>
                            <span className="text-[9px] text-gray-400 font-mono">POST /soc-scan</span>
                          </button>
                        </div>
                      </div>

                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                          <Terminal size={14} className="text-blue-600" />
                          <span>Sensing Agent Signals</span>
                        </h3>
                        <p className="text-[11px] text-gray-500 leading-relaxed">
                          Regulatory, threat, and internal discovery crawlers operate continuously on background schedulers. Trigger a manual sync on the CPO Console.
                        </p>
                        <button
                          onClick={() => setActiveTab('cpo_agents')}
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 text-xs rounded-lg shadow-sm transition-all text-center cursor-pointer block"
                        >
                          View Agent Console
                        </button>
                      </div>

                    </div>

                  </div>

                  {/* Collapsible Corporate Governance & Data Registries */}
                  <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-xs overflow-hidden mt-6">
                    <div 
                      onClick={() => setGovIsExpanded(!govIsExpanded)}
                      className="p-5 border-b border-[#E5E7EB] bg-gray-50/50 flex justify-between items-center cursor-pointer select-none hover:bg-gray-50 transition-all"
                    >
                      <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                        <FolderOpen size={14} className="text-blue-600" />
                        <span>Corporate Governance & Data Registries</span>
                      </h3>
                      <span className="text-xs text-gray-400 font-bold">{govIsExpanded ? 'Collapse ▲' : 'Expand ▼'}</span>
                    </div>

                    {govIsExpanded && (
                      <div className="p-6 space-y-6">
                        
                        {/* Tab selectors */}
                        <div className="flex space-x-2 border-b border-[#E5E7EB] pb-3">
                          {['inventory', 'processors', 'hierarchy'].map(tab => (
                            <button
                              key={tab}
                              onClick={() => setGovSelectedTab(tab)}
                              className={`px-4 py-2 rounded-lg text-xs font-bold border transition-all cursor-pointer ${
                                govSelectedTab === tab
                                  ? 'bg-blue-50 border-blue-200 text-blue-700 shadow-xs'
                                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                              }`}
                            >
                              {tab === 'inventory' ? 'Data Inventory' : tab === 'processors' ? 'Sub-processors & Contractors' : 'Role & Dept Hierarchy'}
                            </button>
                          ))}
                        </div>

                        {/* Inventory Tab */}
                        {govSelectedTab === 'inventory' && (
                          <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-white">
                            <table className="w-full text-xs text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[10px] uppercase">
                                  <th className="p-3.5">Storage System</th>
                                  <th className="p-3.5">Data Elements</th>
                                  <th className="p-3.5">Data Subjects</th>
                                  <th className="p-3.5">Retention Period</th>
                                  <th className="p-3.5">Security Controls</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#E5E7EB]">
                                {govDataInventory.map((item, idx) => (
                                  <tr key={idx} className="hover:bg-gray-50 transition-all">
                                    <td className="p-3.5 font-bold text-gray-800 font-mono text-[11px]">{item.system}</td>
                                    <td className="p-3.5 font-semibold text-gray-700">{item.element}</td>
                                    <td className="p-3.5 text-gray-600">{item.population}</td>
                                    <td className="p-3.5 text-gray-600 font-medium">{item.retention}</td>
                                    <td className="p-3.5 text-emerald-700 font-mono text-[10px] font-bold">✓ {item.control}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {/* Processors Tab */}
                        {govSelectedTab === 'processors' && (
                          <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-white">
                            <table className="w-full text-xs text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[10px] uppercase">
                                  <th className="p-3.5">Contractor / Sub-processor</th>
                                  <th className="p-3.5">Service Role</th>
                                  <th className="p-3.5">DPA Status (CPRA/GDPR)</th>
                                  <th className="p-3.5">Data Storage Location</th>
                                  <th className="p-3.5">Transfer Jurisdiction</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#E5E7EB]">
                                {govSubProcessors.map((proc, idx) => (
                                  <tr key={idx} className="hover:bg-gray-50 transition-all">
                                    <td className="p-3.5 font-bold text-gray-800">{proc.name}</td>
                                    <td className="p-3.5 text-gray-600 font-semibold">{proc.role}</td>
                                    <td className="p-3.5">
                                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                                        proc.dpa.includes('Signed') || proc.dpa.includes('SCC')
                                          ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                                          : 'bg-amber-50 border-amber-200 text-amber-800'
                                      }`}>
                                        {proc.dpa}
                                      </span>
                                    </td>
                                    <td className="p-3.5 font-mono text-[11px] text-gray-655">{proc.storage}</td>
                                    <td className="p-3.5 text-gray-500 italic">{proc.jurisdiction}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {/* Hierarchy Tab */}
                        {govSelectedTab === 'hierarchy' && (
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {govRoleHierarchy.map((dept, idx) => (
                              <div key={idx} className="p-5 rounded-xl border border-[#E5E7EB] bg-gray-50/30 space-y-3">
                                <div className="text-xs font-bold text-gray-800 uppercase tracking-wider border-b border-[#E5E7EB] pb-2 flex items-center space-x-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                                  <span>{dept.department}</span>
                                </div>
                                <div className="space-y-2">
                                  {dept.roles.map((role, rIdx) => (
                                    <div key={rIdx} className="flex items-center space-x-2 text-xs text-gray-655">
                                      <span className="text-gray-400 font-mono">L{rIdx + 1}:</span>
                                      <span className="font-medium text-gray-850">{role}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                      </div>
                    )}
                  </div>

                  {/* Collapsible Agent Self-Improvement & Persistent Memory */}
                  <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-xs overflow-hidden mt-6">
                    <div 
                      onClick={() => setLessonsIsExpanded(!lessonsIsExpanded)}
                      className="p-5 border-b border-[#E5E7EB] bg-gray-50/50 flex justify-between items-center cursor-pointer select-none hover:bg-gray-50 transition-all"
                    >
                      <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                        <Cpu size={14} className="text-indigo-600" />
                        <span>Agent Self-Improvement & Persistent Memory (Level 2)</span>
                      </h3>
                      <span className="text-xs text-gray-400 font-bold">{lessonsIsExpanded ? 'Collapse ▲' : 'Expand ▼'}</span>
                    </div>

                    {lessonsIsExpanded && (
                      <div className="p-6 space-y-6">
                        <p className="text-xs text-gray-500 leading-relaxed">
                          KIBO implements <strong>Level 2: SQLite-Backed Persistent Long-Term Memory</strong>. Reflection agents continuously record feedback and lessons, which are automatically retrieved and injected into the prompts of running active agents to ensure persistent self-improvement.
                        </p>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                          
                          {/* Write/Submit feedback panel */}
                          <div className="bg-gray-50/50 border border-gray-200 p-5 rounded-xl space-y-4 md:col-span-1">
                            <h4 className="text-xs font-bold uppercase text-gray-700 tracking-wider">Record Feedback / Lesson</h4>
                            <div className="space-y-3">
                              <div className="space-y-1.5">
                                <label className="text-[10px] font-bold text-gray-550 uppercase">Target Domain</label>
                                <select 
                                  value={newLessonDomain}
                                  onChange={(e) => setNewLessonDomain(e.target.value)}
                                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden text-gray-700 font-semibold"
                                >
                                  <option value="onboarding">Onboarding Agent</option>
                                  <option value="dsar">DSAR Fulfillment Agent</option>
                                  <option value="vendor">Vendor Agent</option>
                                  <option value="all">Universal / All Agents</option>
                                </select>
                              </div>
                              <div className="space-y-1.5">
                                <label className="text-[10px] font-bold text-gray-555 uppercase">Lesson / Constraint Notes</label>
                                <textarea
                                  value={newLessonNotes}
                                  onChange={(e) => setNewLessonNotes(e.target.value)}
                                  placeholder="E.g., Require a signed DPA prior to data exports..."
                                  rows={4}
                                  className="w-full border border-gray-300 rounded-lg p-3 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden font-mono bg-white shadow-xs resize-none"
                                />
                              </div>
                              <button 
                                onClick={handleAddLesson}
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 rounded-lg text-[10px] uppercase tracking-wider shadow-sm transition-all cursor-pointer"
                              >
                                Commit to Agent Memory
                              </button>
                            </div>
                          </div>

                          {/* Persistent Memory logs */}
                          <div className="md:col-span-2 space-y-3">
                            <h4 className="text-xs font-bold uppercase text-gray-700 tracking-wider">Active Memory Registers</h4>
                            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                              {agentLessons.map(lesson => (
                                <div key={lesson.lesson_id} className="p-4 rounded-xl border border-indigo-100 bg-indigo-50/10 space-y-2 hover:bg-indigo-50/20 transition-all shadow-xs">
                                  <div className="flex justify-between items-center text-[10px] font-bold">
                                    <span className="text-indigo-850 font-mono">ID: {lesson.lesson_id}</span>
                                    <span className="uppercase bg-indigo-100/50 border border-indigo-200 text-indigo-800 px-2 py-0.5 rounded-md">
                                      Domain: {lesson.domain}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-755 font-mono italic">"{lesson.feedback_notes}"</p>
                                  <div className="text-[9px] text-gray-400 font-medium">Recorded: {lesson.created_at}</div>
                                </div>
                              ))}
                              {agentLessons.length === 0 && (
                                <div className="p-8 text-center text-xs text-gray-400 italic">
                                  No active lessons in persistent memory registry.
                                </div>
                              )}
                            </div>
                          </div>

                        </div>

                        {/* Self-Improvement Simulator Block */}
                        <div className="border-t border-[#E5E7EB] pt-6 space-y-4">
                          <h4 className="text-xs font-bold uppercase text-gray-700 tracking-wider flex items-center space-x-1.5">
                            <Sparkles size={13} className="text-indigo-650 animate-pulse" />
                            <span>Simulate Self-Improvement Cycle (LangGraph Execution)</span>
                          </h4>
                          <p className="text-[11px] text-gray-550 leading-relaxed">
                            Simulate incoming regulatory frameworks or user friction telemetry to trigger the 3-stage cyclical LangGraph self-critique adaptation loop.
                          </p>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Input Form */}
                            <div className="bg-gray-50/30 border border-gray-200 p-4 rounded-xl space-y-3.5 md:col-span-1">
                              <div className="space-y-1">
                                <label className="text-[10px] font-bold text-gray-500 uppercase">Trigger Event Type</label>
                                <select 
                                  value={simTriggerType}
                                  onChange={(e) => setSimTriggerType(e.target.value)}
                                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-xs text-gray-750 font-semibold focus:ring-1 focus:ring-blue-500 focus:outline-hidden"
                                >
                                  <option value="Regulatory_Update">Regulatory Update (New Legislation)</option>
                                  <option value="User_Friction">User Friction Telemetry (Workflows)</option>
                                </select>
                              </div>
                              <div className="space-y-1">
                                <label className="text-[10px] font-bold text-gray-500 uppercase">Trigger Source / Telemetry Data</label>
                                <textarea
                                  value={simTriggerData}
                                  onChange={(e) => setSimTriggerData(e.target.value)}
                                  rows={3}
                                  className="w-full border border-gray-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden font-mono bg-white resize-none"
                                />
                              </div>
                              <button 
                                onClick={handleTriggerSelfImprovement}
                                disabled={simIsRunning}
                                className="w-full bg-indigo-650 hover:bg-indigo-700 text-white font-bold py-2 rounded-lg text-[10px] uppercase tracking-wider shadow-sm transition-all cursor-pointer flex items-center justify-center space-x-1.5"
                              >
                                {simIsRunning ? (
                                  <>
                                    <span className="w-3.5 h-3.5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                                    <span>Running critique...</span>
                                  </>
                                ) : (
                                  <span>Invoke LangGraph Loop</span>
                                )}
                              </button>
                            </div>

                            {/* Logs Display */}
                            <div className="md:col-span-2 space-y-2">
                              <label className="text-[10px] font-bold text-gray-550 uppercase">LangGraph Cyclic Output Log</label>
                              <div className="bg-gray-950 border border-gray-900 rounded-xl p-4 font-mono text-[11px] text-emerald-400 min-h-[160px] max-h-[220px] overflow-y-auto space-y-1.5 shadow-inner">
                                {simLogs.map((log, idx) => (
                                  <div key={idx} className={log.includes("REJECTED") ? "text-rose-455" : log.includes("APPROVED") ? "text-amber-400 font-bold" : "text-emerald-400"}>
                                    {log}
                                  </div>
                                ))}
                                {simLogs.length === 0 && (
                                  <div className="text-gray-500 italic">LangGraph self-improvement state logs will appear here. Click 'Invoke LangGraph Loop' to simulate.</div>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Ground Truth Legal Library Panel */}
                          <div className="bg-gray-50/20 border border-[#E5E7EB] rounded-xl p-4 space-y-3 mt-4">
                            <div className="flex justify-between items-center border-b border-gray-200 pb-2">
                              <span className="text-[10px] font-bold text-gray-700 uppercase tracking-wider flex items-center space-x-1.5">
                                <BookOpen size={12} className="text-blue-600" />
                                <span>Definitive Legal Library (RAG Grounding DB)</span>
                              </span>
                              <span className="text-[9px] text-gray-400 font-mono">SQLite: kibo_state.db -&gt; legal_ground_truth</span>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              {legalLibrary.map(clause => (
                                <div key={clause.clause_id} className="bg-white border border-gray-200 p-3 rounded-lg space-y-1.5 text-xs shadow-2xs">
                                  <div className="flex justify-between font-bold text-[10px]">
                                    <span className="text-blue-800 font-mono">{clause.clause_id}</span>
                                    <span className="uppercase text-gray-500 font-mono">{clause.legislation.replace('_', ' ')}</span>
                                  </div>
                                  <p className="text-[11px] text-gray-650 leading-relaxed italic">"{clause.clause_text}"</p>
                                  <div className="text-[9px] text-gray-400">
                                    Keywords: <code className="bg-gray-50 px-1 py-0.5 rounded border border-gray-150">{clause.keywords}</code>
                                  </div>
                                </div>
                              ))}
                              {legalLibrary.length === 0 && (
                                <div className="text-gray-400 text-center italic text-xs py-4 col-span-3">No legal reference clauses loaded in RAG database.</div>
                              )}
                            </div>
                          </div>
                        </div>

                      </div>
                    )}
                  </div>

                </div>
              )}

              {activeTab === 'inbox' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full items-start">
                  
                  {/* Email List */}
                  <div className="space-y-3.5">
                    <h2 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Secure Privacy Inbox</h2>
                    <div className="space-y-2.5">
                      {inboxEmails.map(email => (
                        <div
                          key={email.email_id}
                          onClick={async () => {
                            setSelectedEmail(email);
                            await fetchEmailReplies(email.email_id);
                          }}
                          className={`p-4 rounded-xl border text-[12px] cursor-pointer space-y-1.5 transition-all ${
                            selectedEmail?.email_id === email.email_id
                              ? 'bg-blue-50/50 border-blue-500 shadow-xs'
                              : 'bg-white border-[#E5E7EB] hover:border-gray-300 shadow-xs'
                          }`}
                        >
                          <div className="flex justify-between font-semibold">
                            <span>From: {email.sender}</span>
                            <span className="uppercase text-blue-600 text-[10px] font-bold">{email.category}</span>
                          </div>
                          <div className="text-gray-700 truncate">{email.subject}</div>
                          <div className="text-gray-500 text-[10px] flex justify-between pt-1 border-t border-gray-100">
                            <span>Status: {email.status}</span>
                            {email.converted_to_transaction && (
                              <span className="text-emerald-700 font-semibold">Linked: {email.converted_to_transaction}</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Email Detail Panel */}
                  <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl min-h-[400px] shadow-xs space-y-6">
                    {selectedEmail ? (
                      <div className="space-y-6 text-xs">
                        
                        {/* Headers */}
                        <div className="border-b border-[#E5E7EB] pb-3.5 space-y-2">
                          <div className="flex justify-between">
                            <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px]">Sender</span>
                            <span className="text-[#111827] font-semibold">{selectedEmail.sender}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px]">Subject</span>
                            <span className="text-[#111827] font-semibold">{selectedEmail.subject}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px]">Status</span>
                            <span className="uppercase text-blue-600 font-bold font-mono text-[10px]">{selectedEmail.status}</span>
                          </div>
                        </div>

                        {/* Incoming Body */}
                        <div className="space-y-1.5">
                          <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px]">Incoming Message Body</span>
                          <div className="text-gray-800 whitespace-pre-wrap leading-relaxed bg-gray-50 p-4 rounded-xl border border-[#E5E7EB] font-mono text-[12px] shadow-inner">
                            {selectedEmail.body}
                          </div>
                        </div>

                        {/* List of Actions */}
                        <div className="space-y-2 pt-2 border-t border-[#E5E7EB]">
                          <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px] block">List of Triage Actions</span>
                          <div className="flex flex-wrap gap-2.5">
                            {selectedEmail.status !== 'triaged' ? (
                              <button
                                onClick={() => handleTriageEmail(selectedEmail.email_id)}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-3 py-1.5 rounded-lg uppercase text-[9px] tracking-wider shadow-sm transition-all cursor-pointer"
                              >
                                Triage into Transaction
                              </button>
                            ) : (
                              <span className="text-emerald-700 font-bold bg-emerald-50 border border-emerald-250 px-3 py-1.5 rounded-lg text-[9px] uppercase tracking-wider flex items-center space-x-1">
                                <Check size={10} />
                                <span>Triaged</span>
                              </span>
                            )}
                            <button
                              onClick={() => alert(`Escalated email thread ${selectedEmail.email_id} to Legal counsel.`)}
                              className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-bold px-3 py-1.5 rounded-lg uppercase text-[9px] tracking-wider transition-all cursor-pointer"
                            >
                              Escalate to Legal
                            </button>
                            <button
                              onClick={() => alert(`Flagged email thread ${selectedEmail.email_id} as Spam/Safe-Ignore.`)}
                              className="bg-white border border-rose-200 hover:bg-rose-50 text-rose-700 font-bold px-3 py-1.5 rounded-lg uppercase text-[9px] tracking-wider transition-all cursor-pointer"
                            >
                              Flag as Spam
                            </button>
                          </div>
                        </div>

                        {/* Outgoing Message Reply Composer */}
                        <div className="space-y-2 pt-4 border-t border-[#E5E7EB]">
                          <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px] block">Compose Outgoing Reply</span>
                          <div className="space-y-2">
                            <textarea
                              value={replyBody}
                              onChange={(e) => setReplyBody(e.target.value)}
                              placeholder="Type your official response to send to the privacy sender..."
                              rows={4}
                              className="w-full border border-gray-300 rounded-xl p-3 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden font-mono bg-white shadow-xs resize-none"
                            />
                            <div className="flex justify-end">
                              <button
                                onClick={() => handleSendReply(selectedEmail.email_id)}
                                className="bg-emerald-650 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-lg uppercase text-[9px] tracking-wider shadow-sm transition-all cursor-pointer"
                              >
                                Send Outgoing Reply
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Outgoing Messages Thread Log */}
                        {inboxReplies.length > 0 && (
                          <div className="space-y-3.5 pt-4 border-t border-[#E5E7EB]">
                            <span className="text-gray-400 uppercase font-bold tracking-wider text-[9px] block">Outgoing Message History Log</span>
                            <div className="space-y-2.5">
                              {inboxReplies.map(reply => (
                                <div key={reply.reply_id} className="p-3 bg-emerald-50/20 border border-emerald-250/30 rounded-xl text-xs space-y-1 shadow-xs">
                                  <div className="flex justify-between text-[10px] font-bold text-emerald-800">
                                    <span>From: KIBO Compliance Office</span>
                                    <span>{reply.sent_at}</span>
                                  </div>
                                  <div className="text-gray-700 whitespace-pre-wrap font-mono">{reply.body}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-400 text-xs py-12 italic">
                        Select an email from the inbox to display details and triage actions.
                      </div>
                    )}
                  </div>

                </div>
              )}

              {activeTab === 'meetings' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                  
                  {/* Left: Meeting list & Agenda Creator */}
                  <div className="space-y-4">
                    <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                      <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                        <span>Create Compliance Meeting</span>
                      </h2>
                      
                      <form onSubmit={handleCreateMeeting} className="space-y-3.5">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Meeting Date</label>
                            <input 
                              type="datetime-local" 
                              value={meetingsDate}
                              onChange={(e) => setMeetingsDate(e.target.value)}
                              className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs"
                            />
                          </div>
                          <div>
                            <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Meeting Type</label>
                            <select 
                              value={meetingsType}
                              onChange={(e) => setMeetingsType(e.target.value)}
                              className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2 text-xs text-[#111827] rounded-lg cursor-pointer transition-all shadow-xs"
                            >
                              <option value="privacy_security_weekly">Weekly Privacy & Security</option>
                              <option value="psr_committee">PSR Committee Meeting</option>
                            </select>
                          </div>
                        </div>

                        <div>
                          <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Agenda Items (One per line)</label>
                          <textarea 
                            required
                            value={meetingsAgenda}
                            onChange={(e) => setMeetingsAgenda(e.target.value)}
                            placeholder="HIPAA S3 Config Review&#10;WhatsApp PIA sign-off"
                            className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-20 resize-none font-mono transition-all shadow-xs"
                          />
                        </div>

                        <button 
                          type="submit" 
                          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer"
                        >
                          Create Meeting
                        </button>
                      </form>
                    </div>

                    {/* Meetings List */}
                    <div className="space-y-2.5">
                      <div className="text-xs font-bold uppercase tracking-wider text-gray-800">Upcoming & Past Meetings</div>
                      {expertMeetings.map(m => (
                        <div
                          key={m.meeting_id}
                          onClick={() => {
                            setSelectedMeetingId(m.meeting_id);
                            setMeetingMinutes(m.minutes || '');
                            setMeetingActionItems(m.action_items || []);
                          }}
                          className={`p-4 rounded-xl border text-xs cursor-pointer space-y-2 transition-all bg-white border-[#E5E7EB] hover:border-gray-300 shadow-xs ${
                            selectedMeetingId === m.meeting_id ? 'bg-blue-50/50 border-blue-500' : ''
                          }`}
                        >
                          <div className="flex justify-between font-semibold">
                            <span>ID: {m.meeting_id}</span>
                            <span className="uppercase text-blue-600 text-[10px] font-bold">{m.type.replace('_', ' ')}</span>
                          </div>
                          <div className="text-gray-500 text-[11px]">Date: {m.date.replace('T', ' ')}</div>
                          <div className="text-gray-700 text-[11px] leading-relaxed">
                            Agenda: {m.agenda.join(' | ')}
                          </div>
                          {m.minutes && (
                            <div className="text-emerald-700 text-[10px] font-semibold flex items-center space-x-1">
                              <Check size={12} />
                              <span>Minutes & Action Items recorded</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Commissioner Research Libraries */}
                    <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-gray-500">Commissioner Research Libraries</div>
                      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                        <a href="https://www.priv.gc.ca/en/opc-actions-and-decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>Federal (OPC) Actions</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://www.cai.gouv.qc.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>Québec (CAI) Sanctions</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://www.oipc.bc.ca/rulings/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>BC (OIPC) Rulings</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://oipc.ab.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>Alberta (OIPC) Decisions</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://www.ipc.on.ca/en/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>Ontario (IPC) Orders</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://oipc.sk.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                          <span>Saskatchewan (OIPC)</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://oipc.novascotia.ca/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 flex justify-between items-center text-gray-750 transition-all shadow-xs">
                          <span>Nova Scotia (OIPC)</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://www.oipc.nl.ca/reports/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 flex justify-between items-center text-gray-750 transition-all shadow-xs">
                          <span>Newfoundland (OIPC)</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                        <a href="https://www.ombudsman.mb.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 flex justify-between items-center text-gray-750 col-span-2 transition-all shadow-xs">
                          <span>Manitoba Ombudsman Reports</span>
                          <Globe size={11} className="text-blue-600" />
                        </a>
                      </div>
                    </div>
                  </div>

                  {/* Right: Record Minutes Panel */}
                  <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                    {selectedMeetingId ? (
                      <div className="space-y-4 text-xs">
                        <div className="text-blue-600 font-bold uppercase tracking-wider">Record Meeting Minutes & Action Items ({selectedMeetingId})</div>
                        
                        <div>
                          <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Meeting Minutes Summary</label>
                          <textarea 
                            value={meetingMinutes}
                            onChange={(e) => setMeetingMinutes(e.target.value)}
                            placeholder="Provide meeting summary here..."
                            className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-24 resize-none transition-all shadow-xs"
                          />
                        </div>

                        {/* Action items builder */}
                        <div className="space-y-3.5 border-t border-[#E5E7EB] pt-4">
                          <label className="block text-[10px] text-gray-550 font-semibold uppercase">Add Action Item</label>
                          <div className="flex space-x-2">
                            <input 
                              type="text" 
                              placeholder="Task description..."
                              value={meetingActionTask}
                              onChange={(e) => setMeetingActionTask(e.target.value)}
                              className="flex-1 bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs"
                            />
                            <input 
                              type="text" 
                              placeholder="Owner..."
                              value={meetingActionOwner}
                              onChange={(e) => setMeetingActionOwner(e.target.value)}
                              className="w-24 bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2 text-xs text-[#111827] rounded-lg transition-all shadow-xs"
                            />
                            <button
                              type="button"
                              onClick={handleAddActionItem}
                              className="bg-white hover:bg-gray-550 text-gray-700 px-4 text-xs rounded-lg border border-[#E5E7EB] transition-all cursor-pointer shadow-xs"
                            >
                              Add
                            </button>
                          </div>

                          {/* Action Items List */}
                          <div className="space-y-1.5 pt-1">
                            {meetingActionItems.map((item, idx) => (
                              <div key={idx} className="bg-gray-50 p-2.5 rounded-lg border border-[#E5E7EB] text-[10px] flex justify-between font-mono text-gray-700 shadow-xs">
                                <span>{item.task} (Owner: {item.owner})</span>
                                <span className="text-blue-600 font-semibold">{item.due}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex space-x-2 pt-2">
                          <button
                            onClick={() => handleSaveMinutes(selectedMeetingId)}
                            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2.5 rounded-lg uppercase text-[10px] tracking-wide shadow-sm transition-all cursor-pointer"
                          >
                            Save Minutes & Notify Committee
                          </button>
                          <button
                            onClick={() => setSelectedMeetingId(null)}
                            className="bg-white hover:bg-gray-550 text-gray-700 border border-[#E5E7EB] px-3 py-2 rounded text-[10px] shadow-xs"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-gray-400 text-[10px] py-12 italic">
                        Select a meeting from the list to record minutes and assign action items.
                      </div>
                    )}
                  </div>

                </div>
              )}
                 {activeTab === 'training_admin' && (
                <div className="space-y-6 max-w-xl">
                  
                  {/* Training compliance card */}
                  <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800">Organization-wide Compliance Metrics</h2>
                    
                    {trainingCompliance ? (
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div className="bg-gray-50 p-4 border border-[#E5E7EB] rounded-xl">
                          <div className="text-xl font-bold text-blue-600">{trainingCompliance.compliance_percentage}%</div>
                          <div className="text-[10px] text-gray-550 mt-1 uppercase font-medium">Completion Rate</div>
                        </div>
                        <div className="bg-gray-50 p-4 border border-[#E5E7EB] rounded-xl">
                          <div className="text-xl font-bold text-[#111827]">{trainingCompliance.completed_modules} / {trainingCompliance.total_modules}</div>
                          <div className="text-[10px] text-gray-550 mt-1 uppercase font-medium">Modules Complete</div>
                        </div>
                        <div className="bg-gray-50 p-4 border border-[#E5E7EB] rounded-xl">
                          <div className="text-xl font-bold text-rose-650">{trainingCompliance.overdue_staff_count}</div>
                          <div className="text-[10px] text-gray-555 mt-1 uppercase font-medium">Overdue Reminders</div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-450 italic">Loading compliance data...</div>
                    )}

                    <div className="flex space-x-3 pt-2">
                      <button
                        onClick={() => handleTriggerTrainingAction('assign')}
                        className="flex-1 bg-white hover:bg-gray-550 text-gray-700 border border-[#E5E7EB] py-2.5 rounded-lg text-xs uppercase font-medium transition-all cursor-pointer shadow-xs"
                      >
                        Reset & Assign Courses
                      </button>
                      <button
                        onClick={() => handleTriggerTrainingAction('remind')}
                        className="flex-1 bg-white hover:bg-gray-550 text-gray-700 border border-[#E5E7EB] py-2.5 rounded-lg text-xs uppercase font-medium transition-all cursor-pointer shadow-xs"
                      >
                        Send Overdue Reminders
                      </button>
                    </div>
                  </div>

                </div>
              )}

              {/* Onboarding Checklist Workspace */}
              {activeTab === 'onboarding' && (
                <div className="space-y-6">
                  {/* Title and Intro */}
                  <div className="space-y-1">
                    <h1 className="text-lg font-bold text-[#111827] flex items-center space-x-2">
                      <Layers size={18} className="text-blue-600" />
                      <span>Canadian Privacy Onboarding Desk (PIPEDA & Law 25 Baseline)</span>
                    </h1>
                    <p className="text-xs text-gray-500 max-w-2xl leading-relaxed">
                      Law 25 (Provincial - Quebec) applies to any organization handling Quebec resident data, establishing a strict baseline. General requirements fall under PIPEDA (Federal).
                    </p>
                  </div>

                  {/* Mode Selector */}
                  <div className="flex border-b border-[#E5E7EB] mb-4">
                    <button
                      onClick={() => setOnboardingSubMode('checklist')}
                      className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                        onboardingSubMode === 'checklist'
                          ? 'border-blue-600 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      Dynamic Checklists
                    </button>
                    <button
                      onClick={() => setOnboardingSubMode('ai_agent')}
                      className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all cursor-pointer flex items-center space-x-1.5 ${
                        onboardingSubMode === 'ai_agent'
                          ? 'border-blue-600 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      <Sparkles size={12} className={onboardingSubMode === 'ai_agent' ? 'text-blue-600' : 'text-gray-400'} />
                      <span>AI Onboarding Agent</span>
                    </button>
                  </div>

                  {onboardingSubMode === 'checklist' ? (
                    <div className="space-y-6">
                      {/* Progress Indicators */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs">
                          <div className="flex justify-between text-xs font-semibold mb-2 text-gray-700">
                            <span>Federal (PIPEDA/CASL) Compliance</span>
                            <span className="text-blue-600 font-bold">
                              {Math.round((onboardingTasks.filter(t => t.scope === 'Federal' && t.status === 'completed').length / (onboardingTasks.filter(t => t.scope === 'Federal').length || 1)) * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden border border-gray-200">
                            <div 
                              className="bg-blue-600 h-full transition-all duration-500" 
                              style={{ width: `${(onboardingTasks.filter(t => t.scope === 'Federal' && t.status === 'completed').length / (onboardingTasks.filter(t => t.scope === 'Federal').length || 1)) * 100}%` }}
                            />
                          </div>
                          <div className="text-[10px] text-gray-500 mt-2">
                            {onboardingTasks.filter(t => t.scope === 'Federal' && t.status === 'completed').length} of {onboardingTasks.filter(t => t.scope === 'Federal').length} tasks completed
                          </div>
                        </div>

                        <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl shadow-xs">
                          <div className="flex justify-between text-xs font-semibold mb-2 text-gray-700">
                            <span>Provincial (Law 25/PIPA/FIPPA) Compliance</span>
                            <span className="text-blue-600 font-bold">
                              {Math.round((onboardingTasks.filter(t => t.scope === 'Provincial' && t.status === 'completed').length / (onboardingTasks.filter(t => t.scope === 'Provincial').length || 1)) * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden border border-gray-200">
                            <div 
                              className="bg-blue-600 h-full transition-all duration-500" 
                              style={{ width: `${(onboardingTasks.filter(t => t.scope === 'Provincial' && t.status === 'completed').length / (onboardingTasks.filter(t => t.scope === 'Provincial').length || 1)) * 100}%` }}
                            />
                          </div>
                          <div className="text-[10px] text-gray-500 mt-2">
                            {onboardingTasks.filter(t => t.scope === 'Provincial' && t.status === 'completed').length} of {onboardingTasks.filter(t => t.scope === 'Provincial').length} tasks completed
                          </div>
                        </div>
                      </div>

                      {/* Task Checklist Panel */}
                      <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                        <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                          <CheckSquare size={14} className="text-blue-600" />
                          <span>Dynamic Compliance Checklist</span>
                        </h2>

                        <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-white shadow-xs">
                          <table className="w-full text-xs text-left border-collapse">
                            <thead>
                              <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[11px] uppercase tracking-wider">
                                <th className="p-3.5 w-12 text-center">Status</th>
                                <th className="p-3.5 w-1/4">Task</th>
                                <th className="p-3.5 w-28">Category</th>
                                <th className="p-3.5 w-32">Scope & Region</th>
                                <th className="p-3.5">Guidance & Action Notes</th>
                                <th className="p-3.5 w-24 text-right">Actions</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-[#E5E7EB]">
                              {onboardingTasks.length === 0 ? (
                                <tr>
                                  <td colSpan="6" className="p-8 text-center text-gray-500 italic">
                                    {isSystemOnline 
                                      ? "No onboarding tasks loaded. Select a Canadian jurisdiction to view checklist." 
                                      : "System Offline - Unable to load compliance checklist."}
                                  </td>
                                </tr>
                              ) : (
                                onboardingTasks.map(t => (
                                  <tr key={t.id} className="hover:bg-gray-550/50 transition-all">
                                    <td className="p-3.5 text-center">
                                      <button 
                                        onClick={() => handleToggleOnboardingTask(t.id)}
                                        className={`p-1 rounded-md border transition-all cursor-pointer ${
                                          t.status === 'completed' 
                                            ? 'bg-emerald-50 border-emerald-300 text-emerald-700 hover:bg-emerald-100' 
                                            : 'bg-white border-[#E5E7EB] text-gray-400 hover:border-gray-300'
                                        }`}
                                      >
                                        <Check size={12} />
                                      </button>
                                    </td>
                                    <td className="p-3.5 font-semibold">
                                      <span className={t.status === 'completed' ? 'line-through text-gray-400 font-normal' : 'text-[#111827]'}>
                                        {t.task_name}
                                      </span>
                                    </td>
                                    <td className="p-3.5">
                                      <span className="px-2 py-0.5 rounded-full bg-gray-100 border border-gray-200 text-gray-650 text-[10px] uppercase font-bold">
                                        {t.category}
                                      </span>
                                    </td>
                                    <td className="p-3.5 space-y-0.5">
                                      <div className={`text-[10px] font-bold ${t.scope === 'Federal' ? 'text-blue-600' : 'text-purple-650'}`}>
                                        {t.scope.toUpperCase()}
                                      </div>
                                      <div className="text-[10px] text-gray-500">{t.jurisdiction}</div>
                                    </td>
                                    <td className="p-3.5">
                                      {editingNotesTaskId === t.id ? (
                                        <div className="flex space-x-2">
                                          <input 
                                            type="text" 
                                            value={editingNotesText}
                                            onChange={(e) => setEditingNotesText(e.target.value)}
                                            className="flex-1 bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-1 focus:ring-blue-500/20 p-1 rounded text-xs text-[#111827] font-mono"
                                          />
                                          <button 
                                            onClick={() => handleUpdateTaskNotes(t.id, editingNotesText)}
                                            className="bg-emerald-650 text-white px-3 py-1 rounded text-[10px] font-bold cursor-pointer shadow-xs"
                                          >
                                            Save
                                          </button>
                                        </div>
                                      ) : (
                                        <div className="text-gray-650 text-[11px] leading-relaxed">
                                          {t.notes || <span className="italic text-gray-400">No guidelines provided.</span>}
                                        </div>
                                      )}
                                    </td>
                                    <td className="p-3.5 text-right">
                                      <button 
                                        onClick={() => {
                                          setEditingNotesTaskId(t.id);
                                          setEditingNotesText(t.notes || '');
                                        }}
                                        className="text-blue-600 hover:text-blue-700 font-semibold hover:underline text-xs cursor-pointer"
                                      >
                                        Edit Info
                                      </button>
                                    </td>
                                  </tr>
                                ))
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* CASL Email Consent & Sunset Automation */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Left Column: CASL Registry */}
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 col-span-2 shadow-xs">
                          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                            <Users size={14} className="text-blue-600" />
                            <span>CASL Compliance Registry</span>
                          </h2>

                          <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-white shadow-xs">
                            <table className="w-full text-xs text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[11px] uppercase tracking-wider">
                                  <th className="p-3">Data Subject</th>
                                  <th className="p-3">Email</th>
                                  <th className="p-3">Consent Type</th>
                                  <th className="p-3">Obtained Source</th>
                                  <th className="p-3">Expiry Date</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#E5E7EB]">
                                {caslRegistry.map(c => (
                                  <tr key={c.id} className="hover:bg-gray-550/50 transition-all">
                                    <td className="p-3 text-[#111827] font-semibold">{c.name}</td>
                                    <td className="p-3 text-gray-600">{c.email}</td>
                                    <td className="p-3">
                                      <span className={`px-2 py-0.5 rounded-full text-[9px] uppercase font-bold border ${
                                        c.consent_status === 'Express' ? 'bg-emerald-50 border-emerald-250 text-emerald-800' :
                                        c.consent_status === 'Implied' ? 'bg-amber-50 border-amber-250 text-amber-800' :
                                        c.consent_status === 'Expired' ? 'bg-rose-50 border-rose-250 text-rose-800' :
                                        'bg-gray-100 border-gray-200 text-gray-600'
                                      }`}>
                                        {c.consent_status}
                                      </span>
                                    </td>
                                    <td className="p-3 text-gray-500">{c.consent_source}</td>
                                    <td className="p-3 text-gray-700 font-semibold">
                                      {c.expiry_date ? c.expiry_date.split('T')[0] : <span className="text-emerald-700">Never (Unlimited)</span>}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                        {/* Right Column: Sunset Automation Console */}
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 flex flex-col justify-between shadow-xs">
                          <div className="space-y-3">
                            <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                              <Terminal size={14} className="text-blue-600" />
                              <span>CASL Sunset Loop</span>
                            </h2>
                            <p className="text-xs text-gray-500 leading-relaxed">
                              Enforces CASL rules: implied consent expires in 6 or 24 months. Automatically warns subjects near expiry and suppresses expired records.
                            </p>

                            <button 
                              onClick={handleRunCaslSunset}
                              disabled={isSunsetting}
                              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs rounded-lg shadow-sm transition-all flex items-center justify-center space-x-2 cursor-pointer"
                            >
                              <RefreshCw size={12} className={isSunsetting ? 'animate-spin' : ''} />
                              <span>Run Sunset Automation</span>
                            </button>
                          </div>

                          <div className="flex-1 mt-4 bg-gray-950 border border-gray-900 rounded-xl p-3.5 text-[10px] text-gray-300 h-40 overflow-y-auto space-y-1.5 select-none font-mono">
                            {caslLogs.map((log, index) => (
                              <div key={index} className={
                                log.includes('[ERROR]') ? 'text-rose-400 font-semibold' : 
                                log.includes('EXPIRED:') ? 'text-rose-300' : 
                                log.includes('WARNING:') ? 'text-amber-400' : 
                                'text-gray-400'
                              }>
                                {log}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Consent Disclaimers & Data Mappings (CASL Obligation Tracker) */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                        
                        {/* Consent Disclaimers Registry */}
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                            <BookOpen size={14} className="text-blue-600" />
                            <span>Consent Disclaimers Registry</span>
                          </h2>
                          <div className="space-y-3.5">
                            {caslDisclaimers.map(d => (
                              <div key={d.id} className="p-3.5 rounded-lg border border-gray-200 bg-gray-50/50 space-y-2">
                                <div className="flex justify-between items-center">
                                  <span className="font-bold text-xs text-gray-800">{d.target}</span>
                                  <span className="text-[9px] bg-blue-50 border border-blue-200 text-blue-700 px-2 py-0.5 rounded-full font-bold">{d.type}</span>
                                </div>
                                <p className="text-[11px] text-gray-650 italic leading-relaxed">"{d.text}"</p>
                                <div className="flex justify-between items-center text-[10px] text-gray-400 pt-1 border-t border-gray-200">
                                  <span>Placement: <code className="font-mono text-gray-600">{d.placement}</code></span>
                                  <span className="font-semibold text-blue-650">{d.jurisdiction}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Data Element Purpose Map */}
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h2 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                            <Database size={14} className="text-blue-600" />
                            <span>Data Element Purpose Map</span>
                          </h2>
                          <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-white shadow-xs">
                            <table className="w-full text-xs text-left border-collapse">
                              <thead>
                                <tr className="bg-gray-50 text-gray-500 border-b border-[#E5E7EB] font-semibold text-[10px] uppercase">
                                  <th className="p-3">Data Element</th>
                                  <th className="p-3">Subject Class</th>
                                  <th className="p-3">Stated Purpose</th>
                                  <th className="p-3">Governing Consent</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-[#E5E7EB]">
                                {caslDataElements.map((e, idx) => (
                                  <tr key={idx} className="hover:bg-gray-50 transition-all">
                                    <td className="p-3 font-semibold text-gray-850 font-mono text-[11px]">{e.element}</td>
                                    <td className="p-3 text-gray-600">{e.subject}</td>
                                    <td className="p-3 text-gray-600 leading-relaxed">{e.purpose}</td>
                                    <td className="p-3 font-medium text-blue-700 text-[10px]">{e.disclaimer}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                      </div>

                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Overview completeness card */}
                      <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div className="space-y-1">
                          <h2 className="text-sm font-bold text-gray-800">Kids Help Phone Compliance Profile Ingestion</h2>
                          <p className="text-xs text-gray-500 font-medium">Automated extraction from public website, internal policies, risk registers, and team data inventories.</p>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="text-xs text-gray-500 font-semibold">Profile Completeness</div>
                            <div className="text-xl font-extrabold text-blue-650">{onbProfile ? onbProfile.completeness_pct : 0}%</div>
                          </div>
                          <div className="w-24 bg-gray-155 h-2.5 rounded-full overflow-hidden border border-gray-200">
                            <div className="bg-blue-600 h-full transition-all duration-500" style={{ width: `${onbProfile ? onbProfile.completeness_pct : 0}%` }} />
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Left column: Ingestion parameters */}
                        <div className="space-y-6 lg:col-span-1">
                          <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                              <Globe size={14} className="text-blue-600" />
                              <span>Multi-Source Ingestion</span>
                            </h3>

                            <div className="space-y-3">
                              <div className="space-y-1.5">
                                <label className="text-[10px] font-bold text-gray-600 uppercase">Onboarding Sector Flow</label>
                                <select
                                  value={onbSectorVariant}
                                  onChange={(e) => {
                                    setOnbSectorVariant(e.target.value);
                                    setOnbLogs(prev => [...prev, `[System] Switched onboarding sector focus to: ${
                                      e.target.value === 'commercial' ? 'Bank / Commercial Institution' : 
                                      e.target.value === 'healthcare' ? 'Physiotherapy Clinic / Healthcare' : 
                                      'IT Company / Publishing House'
                                    }`]);
                                  }}
                                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden font-semibold text-gray-700"
                                >
                                  <option value="commercial">Bank / Commercial (Client DSAR Workflow)</option>
                                  <option value="healthcare">Physiotherapy / Healthcare (Patient PHI & Breach Flow)</option>
                                  <option value="tech_media">IT / Publishing (Client Consent & Tracker Audit)</option>
                                </select>
                                <div className="text-[9px] text-gray-400">customizes the ingestion parser and active privacy workflows.</div>
                              </div>

                              <div className="space-y-1.5">
                                <label className="text-[10px] font-bold text-gray-600 uppercase">Authorized Site URL</label>
                                <div className="flex gap-2">
                                  <input
                                    type="text"
                                    value={onbWebsiteUrl}
                                    onChange={(e) => setOnbWebsiteUrl(e.target.value)}
                                    disabled={onbStatus !== 'idle' && onbStatus !== 'validated'}
                                    className="flex-1 bg-white border border-[#E5E7EB] p-2 rounded-lg text-xs font-mono"
                                  />
                                  <button
                                    onClick={handleStartOnboarding}
                                    disabled={onbStatus === 'ingesting' || onbStatus === 'normalizing'}
                                    className="bg-blue-600 text-white px-3 rounded-lg text-xs font-bold hover:bg-blue-700 disabled:opacity-50 transition-all cursor-pointer"
                                  >
                                    Ingest
                                  </button>
                                </div>
                                <div className="text-[9px] text-gray-400">crawls privacy policies, cookie notices, and AI systems securely.</div>
                              </div>

                               <div className="space-y-1.5 pt-2">
                                <label className="text-[10px] font-bold text-gray-600 uppercase">Corporate Compliance Corpus</label>
                                <input
                                  type="file"
                                  multiple
                                  accept=".docx,.xlsx,.xls,.pdf"
                                  className="hidden"
                                  id="onb-file-upload"
                                  onChange={(e) => {
                                    if (e.target.files) {
                                      const filesArray = Array.from(e.target.files);
                                      setOnbUploadedFiles(filesArray);
                                      setOnbLogs(prev => [...prev, `[USER] Selected ${filesArray.length} document(s) for ingestion.`]);
                                    }
                                  }}
                                />
                                <label
                                  htmlFor="onb-file-upload"
                                  className="border border-dashed border-gray-250 p-4 rounded-lg text-center bg-gray-50/50 block cursor-pointer hover:bg-gray-100 hover:border-blue-300 transition-all"
                                >
                                  <FileUp size={18} className="mx-auto text-blue-650 mb-1" />
                                  <div className="text-[10px] text-gray-650 font-bold">
                                    {onbUploadedFiles.length > 0 ? `${onbUploadedFiles.length} file(s) selected` : "Select files (.pdf, .docx, .xlsx)"}
                                  </div>
                                  <div className="text-[9px] text-gray-400 mt-0.5 max-h-12 overflow-y-auto">
                                    {onbUploadedFiles.length > 0
                                      ? onbUploadedFiles.map(f => f.name).join(', ')
                                      : "Click to upload policy documents, inventories, risk matrices"}
                                  </div>
                                </label>
                              </div>
                            </div>
                          </div>

                          <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                              <Terminal size={14} className="text-blue-600" />
                              <span>Onboarding Trace Logs</span>
                            </h3>
                            <div className="bg-gray-950 text-[#38BDF8] p-3.5 rounded-lg font-mono text-[10px] h-48 overflow-y-auto space-y-1 scrollbar-thin">
                              {onbLogs.length === 0 ? (
                                <div className="text-gray-500 italic">Awaiting ingestion trigger...</div>
                              ) : (
                                onbLogs.map((log, idx) => (
                                  <div key={idx} className="leading-relaxed">{log}</div>
                                ))
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Right column: profile review & gap solver */}
                        <div className="lg:col-span-2 space-y-6">
                          
                          {/* Active Onboarding Privacy Process Flow */}
                          <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-5 shadow-xs">
                            <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-3.5">
                              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                                <Network size={14} className="text-blue-650" />
                                <span>Active Privacy Process Flow (DOT Variant)</span>
                              </h3>
                              <span className="text-[10px] font-mono font-bold bg-blue-50 border border-blue-200 text-blue-800 px-2.5 py-0.5 rounded-md">
                                {onbSectorVariant.toUpperCase()}
                              </span>
                            </div>

                            {/* Flowchart Rendering */}
                            {onbSectorVariant === 'commercial' && (
                              <div className="space-y-4">
                                <p className="text-xs text-gray-500">
                                  <strong>Variant 1: Bank / Commercial Institution (Client DSAR Workflow)</strong>. Maps a client's request through core banking discovery, sub-processor checks, PII redactions, and encrypted delivery.
                                </p>
                                <div className="flex flex-wrap items-center gap-3 p-4 bg-gray-50/50 rounded-xl border border-gray-200 justify-center">
                                  <div className="px-3 py-1.5 rounded-full bg-indigo-100 border border-indigo-300 text-indigo-800 text-[10px] font-bold">Bank Client</div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-900 text-[10px] font-semibold text-center leading-tight">DSAR Intake<br/><span className="text-[9px] text-gray-450 font-normal">(Portal/App)</span></div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-900 text-[10px] font-semibold text-center leading-tight">Identity Verify<br/><span className="text-[9px] text-gray-450 font-normal">(MFA/Crypto)</span></div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-900 text-[10px] font-semibold text-center leading-tight">Core Discovery<br/><span className="text-[9px] text-gray-450 font-normal">(Structured DB)</span></div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-900 text-[10px] font-semibold text-center leading-tight">Vendor Audit<br/><span className="text-[9px] text-gray-450 font-normal">(Contract Check)</span></div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-900 text-[10px] font-semibold text-center leading-tight">Redaction<br/><span className="text-[9px] text-gray-450 font-normal">(PII Strip)</span></div>
                                  <span className="text-gray-400 font-bold">→</span>
                                  <div className="px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-800 text-[10px] font-bold">Encrypted Delivery</div>
                                </div>
                              </div>
                            )}

                            {onbSectorVariant === 'healthcare' && (
                              <div className="space-y-4">
                                <p className="text-xs text-gray-500">
                                  <strong>Variant 2: Physiotherapy Clinic / Healthcare (Patient PHI Lifecycle & Breach)</strong>. Logs access and containment triggers under PHIPA Health Custodian regulations.
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {/* Normal Flow */}
                                  <div className="flex flex-col items-center gap-2.5 p-4 bg-teal-50/20 border border-teal-200 rounded-xl">
                                    <span className="text-[9px] uppercase font-bold text-teal-800 tracking-wider">Patient Data Lifecycle</span>
                                    <div className="px-3 py-1 bg-teal-100 border border-teal-300 rounded-full text-[10px] font-bold text-teal-900">Physio Patient</div>
                                    <span className="text-teal-500 font-bold">↓</span>
                                    <div className="p-2 rounded-lg bg-white border border-teal-200 text-center text-[10px] font-semibold w-full leading-tight">PHI Intake & Consent<br/><span className="text-[9px] text-gray-450 font-normal">(Treatment Purposes)</span></div>
                                    <span className="text-teal-500 font-bold">↓</span>
                                    <div className="p-2 rounded-lg bg-white border border-teal-200 text-center text-[10px] font-semibold w-full leading-tight">EMR Storage<br/><span className="text-[9px] text-gray-450 font-normal">(Encryption at Rest)</span></div>
                                    <span className="text-teal-500 font-bold">↓</span>
                                    <div className="p-2 rounded-lg bg-white border border-teal-200 text-center text-[10px] font-semibold w-full leading-tight">Continuous Access Logging<br/><span className="text-[9px] text-gray-450 font-normal">(Audit Trails)</span></div>
                                  </div>
                                  {/* Incident Loop */}
                                  <div className="flex flex-col items-center gap-2.5 p-4 bg-rose-50/20 border border-rose-200 rounded-xl">
                                    <span className="text-[9px] uppercase font-bold text-rose-800 tracking-wider">Suspected PHI Breach Loop</span>
                                    <div className="p-2 rounded-lg bg-rose-100 border border-rose-350 text-center text-[10px] font-bold text-rose-900 w-full animate-pulse leading-tight">Anomaly Detection<br/><span className="text-[9px] text-rose-750 font-semibold">(Suspected PHI Breach)</span></div>
                                    <span className="text-rose-500 font-bold">↓</span>
                                    <div className="p-2 rounded-lg bg-white border border-rose-200 text-center text-[10px] font-semibold w-full leading-tight">Containment<br/><span className="text-[9px] text-gray-455 font-normal">(Access Revocation)</span></div>
                                    <span className="text-rose-500 font-bold">↓</span>
                                    <div className="grid grid-cols-2 gap-2 w-full">
                                      <div className="p-2 rounded bg-white border border-rose-200 text-center text-[9px] font-bold text-rose-850">Patient Alert</div>
                                      <div className="p-2 rounded bg-white border border-rose-200 text-center text-[9px] font-bold text-rose-850">IPC Breach Log</div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {onbSectorVariant === 'tech_media' && (
                              <div className="space-y-4">
                                <p className="text-xs text-gray-500">
                                  <strong>Variant 3: IT Company / Publishing (Client Consent & Tracking)</strong>. Captures user preferences and crawls backend repositories to find new trackers.
                                </p>
                                <div className="space-y-3 bg-orange-50/20 border border-orange-200 p-4 rounded-xl">
                                  <div className="flex flex-wrap justify-center items-center gap-2.5">
                                    <div className="px-3 py-1 bg-orange-100 border border-orange-300 rounded-full text-[10px] font-bold text-orange-900">Digital Reader</div>
                                    <span className="text-orange-400 font-bold">→</span>
                                    <div className="p-2 bg-white border border-orange-200 rounded text-[10px] font-semibold leading-tight">Platform Interaction</div>
                                    <span className="text-orange-400 font-bold">→</span>
                                    <div className="p-2 bg-white border border-orange-200 rounded text-[10px] font-semibold leading-tight">Consent Platform (CMP)</div>
                                  </div>
                                  <div className="flex justify-center"><span className="text-orange-400 font-bold">↓</span></div>
                                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="p-3 bg-white border border-orange-200 rounded-xl space-y-1 text-center">
                                      <div className="text-[10px] font-bold text-orange-850 uppercase">Continuous Code Audit</div>
                                      <div className="text-[9px] text-gray-550 leading-normal">Crawl codebase to detect new trackers & cookies dynamically.</div>
                                    </div>
                                    <div className="p-3 bg-white border border-rose-200 rounded-xl space-y-1 text-center">
                                      <div className="text-[10px] font-bold text-rose-800 uppercase">Enforce Opt-Outs</div>
                                      <div className="text-[9px] text-gray-550 leading-normal">Block unauthorized pixels and update compliance records.</div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* DOT Specification Accordion */}
                            <div className="border border-[#E5E7EB] rounded-lg overflow-hidden">
                              <details className="group">
                                <summary className="p-3 bg-gray-50 text-[10px] font-bold text-gray-600 uppercase tracking-wider cursor-pointer list-none flex justify-between items-center select-none hover:bg-gray-100 transition-all">
                                  <span>View Graphviz DOT Specification</span>
                                  <span className="text-[9px] text-gray-400 group-open:rotate-180 transition-transform">▼</span>
                                </summary>
                                <div className="p-4 bg-gray-950 text-gray-300 font-mono text-[9px] overflow-x-auto whitespace-pre-wrap border-t border-[#E5E7EB]">
                                  {onbSectorVariant === 'commercial' && `digraph Bank_Client_Privacy {\n    rankdir=LR;\n    node [shape=box, style=filled, fillcolor="#E8EAF6", fontname="Helvetica"];\n    edge [color="#283593", penwidth=1.5];\n\n    Client [shape=ellipse, fillcolor="#C5CAE9", label="Bank Client"];\n    DSAR_Intake [label="DSAR Intake\\n(Portal/App)"];\n    ID_Verify [label="Strict Identity Verification\\n(MFA/Cryptographic)"];\n    Internal_Discover [label="Core Banking Discovery\\n(Structured Data)"];\n    Vendor_Audit [label="Vendor Supply-Chain Check\\n(Sub-processors)"];\n    Redact [label="Algorithmic Redaction\\n(Third-Party PII)"];\n    Fulfill [label="Encrypted Delivery\\nto Client"];\n\n    Client -> DSAR_Intake;\n    DSAR_Intake -> ID_Verify -> Internal_Discover;\n    Internal_Discover -> Vendor_Audit -> Redact -> Fulfill;\n}`}
                                  {onbSectorVariant === 'healthcare' && `digraph Healthcare_Patient_Privacy {\n    rankdir=TB;\n    node [shape=Mrecord, style=filled, fillcolor="#E0F2F1", fontname="Helvetica"];\n    edge [color="#00695C", penwidth=1.5];\n\n    Patient [shape=ellipse, fillcolor="#B2DFDB", label="Physiotherapy Patient"];\n    Intake [label="PHI Intake & Consent\\n(Treatment Purposes)"];\n    EMR_Storage [label="Secure EMR Storage\\n(Encryption at Rest)"];\n    Audit_Log [label="Continuous Access Logging\\n(User, Time, Date)"];\n    \n    node [fillcolor="#FFEBEE", color="#C62828"]\n    Breach_Detect [label="Anomaly Detection\\n(Suspected PHI Breach)"];\n    Containment [label="Automated Containment\\n(Revoke Access)"];\n    Notify_Patient [label="Patient Notification\\n(First Reasonable Opportunity)"];\n    IPC_Report [label="Authority Log\\n(IPC Breach Protocol)"];\n\n    Patient -> Intake -> EMR_Storage -> Audit_Log;\n    Audit_Log -> Breach_Detect [style=dashed, label="If anomaly detected"];\n    Breach_Detect -> Containment -> Notify_Patient;\n    Containment -> IPC_Report;\n}`}
                                  {onbSectorVariant === 'tech_media' && `digraph IT_Publisher_Privacy {\n    rankdir=LR;\n    node [shape=note, style=filled, fillcolor="#FFF3E0", fontname="Helvetica"];\n    edge [color="#E65100", penwidth=1.5];\n\n    Client [shape=ellipse, fillcolor="#FFE0B2", label="Digital Client / Reader"];\n    Platform [label="Platform Interaction\\n(Web/App)"];\n    CMP [label="Consent Management\\n(Opt-in / CCPA Opt-out)"];\n    Code_Scan [label="Continuous Code Auditing\\n(Detect New Trackers)"];\n    Enforce_OptOut [label="Enforce Opt-Outs\\n(Across Ad-Tech Stack)"];\n    Dynamic_RoPA [label="Dynamic RoPA Update\\n& Policy Generation"];\n\n    Client -> Platform -> CMP;\n    CMP -> Enforce_OptOut;\n    Platform -> Code_Scan [style=dashed, label="Background monitoring"];\n    Code_Scan -> Dynamic_RoPA;\n    Code_Scan -> Enforce_OptOut [color="#D32F2F", label="Block unauthorized trackers"];\n}`}
                                </div>
                              </details>
                            </div>
                          </div>

                          {/* Gaps card stack */}
                          {onbGaps.length > 0 && (
                            <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                                <AlertTriangle size={14} className="text-amber-500" />
                                <span>Targeted Onboarding Gaps ({onbGaps.filter(g => g.status === 'pending').length} active)</span>
                              </h3>

                              <div className="space-y-3">
                                {onbGaps.map(g => (
                                  <div key={g.id} className={`p-4 rounded-xl border transition-all ${
                                    g.status === 'pending' ? 'bg-amber-50/30 border-amber-200' : 'bg-gray-50 border-gray-200 opacity-60'
                                  }`}>
                                    <div className="flex justify-between items-start gap-4">
                                      <div className="space-y-1">
                                        <div className="flex items-center space-x-2">
                                          <span className={`text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded-md border ${
                                            g.priority === 'high' ? 'bg-rose-50 border-rose-200 text-rose-700' : 'bg-amber-50 border-amber-200 text-amber-700'
                                          }`}>
                                            {g.priority} priority
                                          </span>
                                          <h4 className="text-xs font-bold text-gray-850">{g.title}</h4>
                                        </div>
                                        <p className="text-xs text-gray-650 leading-relaxed pt-1">{g.details}</p>
                                      </div>

                                      {g.status === 'pending' ? (
                                        <div className="flex flex-col gap-1.5">
                                          <div className="flex gap-1.5">
                                            <input
                                              type="text"
                                              placeholder="Type answer..."
                                              value={onbGapInputs[g.id] || ''}
                                              onChange={(e) => setOnbGapInputs({...onbGapInputs, [g.id]: e.target.value})}
                                              className="bg-white border border-gray-300 rounded px-2.5 py-1 text-xs focus:border-blue-600 focus:outline-none"
                                            />
                                            <button
                                              onClick={() => handleResolveOnbGap(g.id, 'answer', onbGapInputs[g.id] || '')}
                                              className="bg-blue-600 text-white text-[10px] font-bold px-3 py-1 rounded hover:bg-blue-700 cursor-pointer"
                                            >
                                              Submit
                                            </button>
                                          </div>
                                          <div className="flex justify-end gap-1.5">
                                            <button
                                              onClick={() => handleResolveOnbGap(g.id, 'accept', 'Accepted Default')}
                                              className="text-gray-500 hover:text-gray-700 text-[10px] font-bold border border-gray-300 px-2.5 py-1 rounded bg-white hover:bg-gray-50 cursor-pointer"
                                            >
                                              Accept Default
                                            </button>
                                          </div>
                                        </div>
                                      ) : (
                                        <span className="text-[10px] text-emerald-600 font-bold uppercase flex items-center space-x-1">
                                          <Check size={12} />
                                          <span>Resolved</span>
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Profile review tree */}
                          {onbProfile && (
                            <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                              <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-3">
                                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-2">
                                  <Database size={14} className="text-blue-600" />
                                  <span>Normalized Organizational Profile</span>
                                </h3>
                                <div className="flex space-x-2">
                                  {['policies', 'vendors', 'data_inventory'].map(sec => (
                                    <button
                                      key={sec}
                                      onClick={() => setOnbSelectedProfileSection(sec)}
                                      className={`px-3 py-1 rounded-md text-[10px] font-bold border transition-all cursor-pointer ${
                                        onbSelectedProfileSection === sec
                                          ? 'bg-blue-50 border-blue-200 text-blue-700'
                                          : 'bg-white border-gray-205 text-gray-600 hover:bg-gray-50'
                                      }`}
                                    >
                                      {sec.replace('_', ' ').toUpperCase()}
                                    </button>
                                  ))}
                                </div>
                              </div>

                              <div className="border border-gray-200 rounded-xl overflow-hidden bg-gray-50/30">
                                {onbSelectedProfileSection === 'policies' && (
                                  <table className="w-full text-xs text-left border-collapse bg-white">
                                    <thead>
                                      <tr className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold text-[10px] uppercase">
                                        <th className="p-3">Policy Module</th>
                                        <th className="p-3">Version</th>
                                        <th className="p-3">Owner</th>
                                        <th className="p-3">Status</th>
                                        <th className="p-3">Review Period</th>
                                        <th className="p-3">Source Citation</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-150">
                                      {onbProfile.policies.map((p, idx) => (
                                        <tr key={idx} className="hover:bg-gray-50/50">
                                          <td className="p-3 font-semibold text-[#111827]">{p.name}</td>
                                          <td className="p-3 font-mono text-[10px]">{p.version}</td>
                                          <td className="p-3">{p.owner}</td>
                                          <td className="p-3">
                                            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px]">
                                              {p.status}
                                            </span>
                                          </td>
                                          <td className="p-3">{p.review}</td>
                                          <td className="p-3 text-gray-450 italic text-[10px]">{p.citation}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                )}

                                {onbSelectedProfileSection === 'vendors' && (
                                  <table className="w-full text-xs text-left border-collapse bg-white">
                                    <thead>
                                      <tr className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold text-[10px] uppercase">
                                        <th className="p-3">Vendor / Integration</th>
                                        <th className="p-3">Service Role</th>
                                        <th className="p-3">Data Processed</th>
                                        <th className="p-3">Storage Provider</th>
                                        <th className="p-3">Retention Policy</th>
                                        <th className="p-3">DPA Status</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-150">
                                      {onbProfile.vendors.map((v, idx) => (
                                        <tr key={idx} className="hover:bg-gray-50/50">
                                          <td className="p-3 font-semibold text-[#111827]">{v.name}</td>
                                          <td className="p-3">{v.service}</td>
                                          <td className="p-3">{v.data_types}</td>
                                          <td className="p-3 font-mono text-[11px]">{v.storage}</td>
                                          <td className="p-3">{v.retention}</td>
                                          <td className="p-3">
                                            <span className={`px-2 py-0.5 rounded-full text-[10px] ${
                                              v.dpa_status.includes('Annex') || v.dpa_status.includes('Validated')
                                                ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
                                                : 'bg-amber-50 border border-amber-200 text-amber-700'
                                            }`}>
                                              {v.dpa_status}
                                            </span>
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                )}

                                {onbSelectedProfileSection === 'data_inventory' && (
                                  <table className="w-full text-xs text-left border-collapse bg-white">
                                    <thead>
                                      <tr className="bg-gray-50 text-gray-500 border-b border-gray-200 font-semibold text-[10px] uppercase">
                                        <th className="p-3">Internal Team</th>
                                        <th className="p-3">Data Asset</th>
                                        <th className="p-3">Accountable Owner</th>
                                        <th className="p-3">Storage Console</th>
                                        <th className="p-3">Retention Claim</th>
                                        <th className="p-3">Disposal Pipeline</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-150">
                                      {onbProfile.data_inventory.map((d, idx) => (
                                        <tr key={idx} className="hover:bg-gray-550/50">
                                          <td className="p-3 font-semibold text-[#111827]">{d.team}</td>
                                          <td className="p-3 font-semibold">{d.asset}</td>
                                          <td className="p-3">{d.owner}</td>
                                          <td className="p-3 font-mono text-[11px]">{d.storage}</td>
                                          <td className="p-3">{d.retention}</td>
                                          <td className="p-3">{d.disposal}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                )}
                              </div>

                              {onbStatus === 'gap_review' && onbGaps.filter(g => g.status === 'pending').length === 0 && (
                                <div className="flex justify-end pt-3">
                                  <button
                                    onClick={handleFinalizeOnbProfile}
                                    className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold px-4 py-2 rounded-lg cursor-pointer shadow-xs transition-all"
                                  >
                                    Commit Validated Baseline Profile
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        )}

        {/* PSR COMMITTEE MODE */}
        {securityMode === 'psr' && (
          <div className="flex-1 overflow-y-auto bg-gray-50/50 p-6 space-y-6">
            
            {/* Top row: Side-by-side panels */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
              
              {/* Left Column: Meetings & Materials */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-6 shadow-xs">
                
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-gray-800">PSR Committee Meetings</div>
                  <div className="space-y-2.5">
                    {psrMeetings.map(m => (
                      <div key={m.meeting_id} className="bg-white border border-[#E5E7EB] p-4 rounded-xl text-xs space-y-2 shadow-xs">
                        <div className="flex justify-between font-semibold">
                          <span>Meeting ID: {m.meeting_id}</span>
                          <span className="text-blue-600 uppercase text-[10px] font-bold">{m.type.replace('_', ' ')}</span>
                        </div>
                        <div className="text-gray-700 leading-relaxed">Agenda: {m.agenda.join(' | ')}</div>
                        {m.minutes ? (
                          <div className="text-gray-700 bg-gray-50 p-3.5 rounded-lg border border-[#E5E7EB] mt-1 font-mono text-[11px]">
                            Minutes: {m.minutes}
                          </div>
                        ) : (
                          <div className="text-gray-400 italic text-[10px]">Minutes pending recording by CPO</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Materials */}
                <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
                  <div className="text-xs font-bold uppercase tracking-wider text-gray-550">Advisory Review Materials</div>
                  <div className="grid grid-cols-1 gap-2.5">
                    <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                      <span className="font-semibold text-[#111827]">Quebec Law 25 Diagnostic Posture.pdf</span>
                      <button className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-550 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
                    </div>
                    <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                      <span className="font-semibold text-[#111827]">Cross-Border Transfer TIA v1.docx</span>
                      <button className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-550 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
                    </div>
                    <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                      <span className="font-semibold text-[#111827]">Privacy Commissioner Rulings (July 2026).md</span>
                      <a href="/canadian_privacy_newsletter.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-550 px-3 py-1.5 rounded-lg text-center transition-all shadow-xs">View</a>
                    </div>
                  </div>
                </div>

                {/* Research & Regulatory Libraries */}
                <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
                  <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Commissioner Research Libraries</div>
                  <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                    <a href="https://www.priv.gc.ca/en/opc-actions-and-decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                      <span>Federal (OPC) Actions</span>
                      <Globe size={11} className="text-blue-600" />
                    </a>
                    <a href="https://www.cai.gouv.qc.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                      <span>Québec (CAI) Sanctions</span>
                      <Globe size={11} className="text-blue-600" />
                    </a>
                    <a href="https://www.oipc.bc.ca/rulings/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                      <span>BC (OIPC) Rulings</span>
                      <Globe size={11} className="text-blue-600" />
                    </a>
                    <a href="https://oipc.ab.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                      <span>Alberta (OIPC) Decisions</span>
                      <Globe size={11} className="text-blue-600" />
                    </a>
                  </div>
                </div>

              </div>

              {/* Right Column: Risk Advisory Queue */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-6 shadow-xs">
                
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-gray-800">Risk Advisory Queue</div>
                  <div className="space-y-2.5">
                    {psrRiskQueue.map(risk => (
                      <div
                        key={risk.risk_id}
                        onClick={() => setPsrSelectedRisk(risk)}
                        className={`p-4 rounded-xl border text-xs cursor-pointer space-y-2.5 transition-all bg-white border-[#E5E7EB] hover:border-gray-300 shadow-xs ${
                          psrSelectedRisk?.risk_id === risk.risk_id ? 'bg-blue-50/50 border-blue-500' : ''
                        }`}
                      >
                        <div className="flex justify-between font-semibold">
                          <span className="text-blue-600 font-bold font-mono">{risk.risk_id}</span>
                          <span className="uppercase text-gray-500 text-[10px]">{risk.status}</span>
                        </div>
                        <div className="text-[#111827] leading-relaxed">{risk.issue}</div>
                        
                        {risk.recommendations && risk.recommendations.length > 0 && (
                          <div className="border-t border-[#E5E7EB] pt-2.5 space-y-1.5">
                            <div className="text-[10px] font-semibold text-gray-500 uppercase">PSR Recommendations:</div>
                            {risk.recommendations.map((r, i) => (
                              <div key={i} className="text-[10px] text-blue-700 leading-relaxed font-mono">
                                • {r.member} ({r.vote.toUpperCase()}): "{r.recommendation}"
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Advisory recommendation submittal */}
                {psrSelectedRisk && (
                  <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                    <div className="text-xs font-bold uppercase tracking-wider text-[#111827]">Submit Recommendation ({psrSelectedRisk.risk_id})</div>
                    
                    <form onSubmit={handlePsrRecommendationSubmit} className="space-y-4 text-xs">
                      <div>
                        <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Advisory Vote</label>
                        <select 
                          value={psrVote}
                          onChange={(e) => setPsrVote(e.target.value)}
                          className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2 text-xs text-[#111827] rounded-lg cursor-pointer transition-all shadow-xs"
                        >
                          <option value="approve">Approve (Operational clearance)</option>
                          <option value="conditional">Conditional Approval (Mitigation required)</option>
                          <option value="reject">Reject (Action needed)</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[10px] text-gray-550 font-semibold uppercase mb-1">Detailed Recommendation Notes</label>
                        <textarea 
                          required
                          value={psrRecommendation}
                          onChange={(e) => setPsrRecommendation(e.target.value)}
                          placeholder="Provide detailed compliance guidance for the CPO..."
                          className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-20 resize-none transition-all shadow-xs"
                        />
                      </div>

                      <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 text-xs tracking-wide rounded-lg shadow-sm transition-all cursor-pointer">
                        Submit Recommendation
                      </button>
                    </form>
                  </div>
                )}

              </div>

            </div>

            {/* Bottom Row: Dynamic Notes-derived Tracker Cockpit (Full Width) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Gen AI Procurement Gateways & Revocation */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
                  <ShieldAlert size={14} className="text-indigo-650" />
                  <span>Gen AI Procurement & IP Security Gates</span>
                </h3>
                <p className="text-[11px] text-gray-550 leading-relaxed">
                  Innovative Procurement Model (Ontario approved): Sequential gates mapping the transition from Nascent to OpenText/Cohere technical builds.
                </p>
                <div className="space-y-3">
                  <div className="p-3 bg-indigo-50/15 border border-indigo-200 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-[10px] font-bold">
                      <span className="text-indigo-900 uppercase">Nascent Access Revocation</span>
                      <span className="text-emerald-700 bg-emerald-50 border border-emerald-250 px-2 py-0.5 rounded">Verified</span>
                    </div>
                    <p className="text-[10px] text-gray-600">Neil & Bryan confirmed in writing that all IP, keys, and database credentials have been fully revoked from the previous developer.</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-semibold text-gray-655">
                      <span>Innovative Procurement Progression</span>
                      <span className="text-blue-655 font-bold">Stage 1 of 3</span>
                    </div>
                    <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden border border-gray-200">
                      <div className="bg-blue-600 h-full w-[33.3%]" />
                    </div>
                    <div className="grid grid-cols-3 text-[9px] text-gray-400 font-bold uppercase pt-1 text-center">
                      <span className="text-blue-700">LOI (June 8)</span>
                      <span>MOU (Build Plan)</span>
                      <span>DPA (Contract)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* PSR Advisory Tasks List */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
                  <BookOpen size={14} className="text-blue-650" />
                  <span>PSR Advisory Action Registry</span>
                </h3>
                <p className="text-[11px] text-gray-550">Action items assigned during May 27 & Oct 8 committee meetings.</p>
                <div className="space-y-2.5 max-h-[220px] overflow-y-auto pr-1">
                  {psrTransitionTasks.map(t => (
                    <div key={t.id} className="p-3 bg-gray-50 border border-gray-200 rounded-xl space-y-1.5 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-gray-800">{t.title}</span>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                          t.status === 'completed' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-amber-50 text-amber-800 border border-amber-200'
                        }`}>
                          {t.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-gray-550 leading-relaxed">{t.notes}</p>
                      <div className="flex justify-between items-center text-[9px] text-gray-400 pt-1 border-t border-gray-150">
                        <span>Owner: <code className="font-mono">{t.owner}</code></span>
                        <span>ID: {t.id}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Copilot FAQ Audit Tool */}
              <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs lg:col-span-1">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-800 flex items-center space-x-1.5">
                  <Terminal size={14} className="text-indigo-650" />
                  <span>SharePoint Copilot FAQ Auditer</span>
                </h3>
                <p className="text-[11px] text-gray-550">
                  Audit AI responses to secure SharePoint directories before wide staff rollout.
                </p>
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      placeholder="Ask PSR Copilot (e.g. when to contact PSR...)"
                      value={psrCopilotQuery}
                      onChange={(e) => setPsrCopilotQuery(e.target.value)}
                      className="flex-1 bg-white border border-gray-300 rounded-lg p-2 text-xs focus:ring-1 focus:ring-blue-500 focus:outline-hidden"
                    />
                    <button 
                      onClick={() => {
                        if (psrCopilotQuery.toLowerCase().includes('when')) {
                          setPsrCopilotAnswer("PSR Copilot: Staff should contact the PSR Committee when starting any new technical project processing personal info, initiating SaaS vendor onboarding, or if a potential confidentiality incident or PHI breach is suspected.");
                        } else if (psrCopilotQuery.toLowerCase().includes('breach')) {
                          setPsrCopilotAnswer("PSR Copilot: SUSPECTED BREACH PROTOCOL: Revoke credentials immediately to contain access. Conduct RROSH risk screening. Log details in the internal confidentiality incident register. Alert the OPC/IPC and affected individuals at first reasonable opportunity.");
                        } else {
                          setPsrCopilotAnswer("PSR Copilot: Request parsed. Response generated from verified SharePoint compliance directory (ver. 1.04).");
                        }
                      }}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1.5 rounded-lg text-xs transition-all cursor-pointer shadow-xs"
                    >
                      Audit
                    </button>
                  </div>
                  {psrCopilotAnswer && (
                    <div className="p-3 bg-gray-950 text-gray-300 font-mono text-[10px] rounded-lg border border-gray-900 leading-normal max-h-[100px] overflow-y-auto">
                      {psrCopilotAnswer}
                    </div>
                  )}
                  <div className="text-[9px] text-gray-400 italic">
                    Note: A strict disclaimer message will accompany all staff-facing Copilot interfaces.
                  </div>
                </div>
              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
};

export default App;
