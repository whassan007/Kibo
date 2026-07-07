import React, { useState, useEffect, useRef } from 'react';
import { JurisdictionProvider, loadPack } from './jurisdiction/useJurisdiction';
import {
  FileText, Shield, AlertTriangle, Clock, Ban, Check, Undo2,
  ChevronDown, ChevronUp, Terminal, ShieldAlert, UserCheck, Search,
  HardDrive, Database, Network, FileCheck, Layers, RefreshCw, AlertOctagon,
  Users, Briefcase, Eye, Globe, User, Radio, FileUp, Sparkles, Send, Trash2,
  Activity, Server, Mail, Settings, Plus, CheckSquare, Square, Edit, Save, List,
  FolderOpen, Cpu, BookOpen
} from 'lucide-react';
import AdminDashboard from './AdminDashboard';
import ShadowRiskFeed from './components/ShadowRiskFeed';

import ScopeActiveLegislations from './components/ScopeActiveLegislations';
import PublicMode from './modes/PublicMode';
import EmployeeMode from './modes/EmployeeMode';
import PsrMode from './modes/PsrMode';
import ExpertMode from './modes/ExpertMode';
import AdminMode from './modes/AdminMode';

const API_BASE = window.location.port === '5173' || window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : window.location.origin;

import { useLocation, useNavigate } from 'react-router-dom';
import { useToast } from "../components/ui/ToastContext";

const App = () => {
  const { addToast } = useToast();
  const location = useLocation();
  const navigate = useNavigate();

  // --- Derived State from URL ---
  const pathParts = location.pathname.split('/').filter(Boolean);
  
  // URL Structure: /{mode}/{tab}
  // If mode is missing, default to 'public'
  const currentMode = pathParts[0] || 'public';
  // Map '/' to 'public' and preserve other modes
  const securityMode = ['employee', 'expert', 'psr', 'admin'].includes(currentMode) ? currentMode : 'public';
  
  // Active Tab defaults to 'dashboard' if in expert or admin mode
  const activeTab = pathParts[1] || 'dashboard';

  const setSecurityMode = (mode) => {
    if (mode === 'public') navigate('/');
    else navigate(`/${mode}`);
  };

  const setActiveTab = (tab) => {
    navigate(`/${securityMode}/${tab}`);
  };

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
  // Fallback state for ExpertMode props that were referenced but never declared
  // (previously caused a ReferenceError that white-screened /expert).
  const [expertInbox, setExpertInbox] = useState([]);
  const [expertComplianceTraining, setExpertComplianceTraining] = useState([]);
  const [expertExpandedAssessments, setExpertExpandedAssessments] = useState({});
  const toggleExpertAssessment = (id) => setExpertExpandedAssessments(prev => ({ ...prev, [id]: !prev?.[id] }));
  const [complianceProgress, setComplianceProgress] = useState(0);
  const [riskScore, setRiskScore] = useState(0);
  const [riskTrend, setRiskTrend] = useState(0);
  const [assessmentCoverage, setAssessmentCoverage] = useState(0);
  const [openIssues, setOpenIssues] = useState(0);
  const [employeeDataFlows, setEmployeeDataFlows] = useState([]);
  const [thirdPartyDataFlows, setThirdPartyDataFlows] = useState([]);
  const [activeThreats, setActiveThreats] = useState([]);
  const [recentAudits, setRecentAudits] = useState([]);
  const [complianceTrendData, setComplianceTrendData] = useState([]);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editTaskNotes, setEditTaskNotes] = useState('');
  const [newGapDesc, setNewGapDesc] = useState('');
  const [newGapSev, setNewGapSev] = useState('Medium');
  const [onboardingCasl, setOnboardingCasl] = useState([]);
  const handleOnbGapSubmit = (e) => { if (e && e.preventDefault) e.preventDefault(); };
  const handleOnboardingCaslSunset = () => {};
  const handleOnboardingNotesSave = () => {};
  const handleOnboardingTaskToggle = () => {};
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

  const fetchCompanyJurisdiction = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/company/jurisdiction`);
      if (res.ok) {
        const data = await res.json();
        const packId = data.jurisdiction;
        setActiveJurisdiction(packId);
        const pack = loadPack(packId);
        setJurConfig({
          code: pack.id,
          flag: pack.meta.flag || "🌍",
          name: pack.meta.displayName,
          access_request_term: pack.terminology.accessRequest || "Request",
          access_request_abbr: pack.terminology.accessRequestAbbr || "REQ",
          data_subject_term: pack.terminology.individual || "Individual",
          regulator: pack.legislation.regulator || "Regulator",
          primary_statute: pack.legislation.primaryStatute || "Statute",
          access_deadline_days: pack.timelines.accessDeadlineDays || 30,
          breach_notification: pack.timelines.breachNotificationWindow || "72 hours",
          assessment_types: pack.assessments.map(a => a.id),
          training_track: "default"
        });
        setIsSystemOnline(true);
      } else {
        setIsSystemOnline(false);
      }
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
    fetchCompanyJurisdiction();
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
    if (!window.confirm('Are you sure you want to mark this training module as done?')) return;
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
        addToast("Organizational profile committed to downstream compliance pipelines!", "info");
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
    if (action === 'rejected') {
      if (!window.confirm('Are you sure you want to reject this HITL decision? This action is destructive and cannot be undone.')) return;
    }
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
    if (!window.confirm(`Are you sure you want to execute '${action}'?`)) return;
    try {
      await kiboFetch(`${API_BASE}/api/expert/training/${action}`, { method: 'POST' });
      fetchExpertData();
      addToast(`Action '${action}' completed successfully.`, "info");
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
    <JurisdictionProvider packId={activeJurisdiction}>
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
          <div className="flex items-center space-x-3">
            <label htmlFor="security-mode-select" className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">
              Viewing As:
            </label>
            <select
              id="security-mode-select"
              value={securityMode}
              onChange={(e) => setSecurityMode(e.target.value)}
              className="bg-gray-50 border border-gray-200 text-xs font-semibold text-gray-800 px-3 py-1.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all cursor-pointer shadow-xs hover:bg-gray-100"
            >
              <option value="expert">Privacy Officer (CPO)</option>
              <option value="employee">Staff Member</option>
              <option value="psr">Risk Committee (PSR)</option>
              <option value="public">Public End-User</option>
              <option value="admin">System Admin</option>
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
          <PublicMode 
            jurConfig={jurConfig} activeJurisdiction={activeJurisdiction} widgetName={widgetName} setWidgetName={setWidgetName}
            widgetEmail={widgetEmail} setWidgetEmail={setWidgetEmail} widgetType={widgetType} setWidgetType={setWidgetType}
            widgetDesc={widgetDesc} setWidgetDesc={setWidgetDesc} isSystemOnline={isSystemOnline} handlePublicSubmit={handlePublicSubmit}
            widgetStatus={widgetStatus} widgetTrackId={widgetTrackId} handleWidgetCheckStatus={handleWidgetCheckStatus}
            widgetCheckId={widgetCheckId} setWidgetCheckId={setWidgetCheckId} widgetCheckResult={widgetCheckResult}
          />
        )}

        {/* EMPLOYEE MODE */}
        {securityMode === 'employee' && (
          <EmployeeMode 
            employeeRisks={employeeRisks} employeeTraining={employeeTraining} jurConfig={jurConfig}
            handleCompleteTraining={handleCompleteTraining} handleInventorySubmit={handleInventorySubmit}
            inventorySystem={inventorySystem} setInventorySystem={setInventorySystem}
            inventoryDataTypes={inventoryDataTypes} setInventoryDataTypes={setInventoryDataTypes}
            inventoryPurpose={inventoryPurpose} setInventoryPurpose={setInventoryPurpose}
            inventoryRetention={inventoryRetention} setInventoryRetention={setInventoryRetention}
            inventorySharing={inventorySharing} setInventorySharing={setInventorySharing}
            inventoryStatus={inventoryStatus}
          />
        )}
        {/* SYSTEM ADMIN MODE */}
        {securityMode === 'admin' && (
          <AdminMode 
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
          <ExpertMode 
            activeTab={activeTab} setActiveTab={setActiveTab} activeJurisdiction={activeJurisdiction} jurConfig={jurConfig} setSecurityMode={setSecurityMode} setAdminDiffMode={setAdminDiffMode}
            expertAssessments={expertAssessments} expertMeetings={expertMeetings} expertInbox={expertInbox} expertComplianceTraining={expertComplianceTraining}
            onboardingTasks={onboardingTasks} onbGaps={onbGaps} handleOnbGapSubmit={handleOnbGapSubmit} newGapDesc={newGapDesc} setNewGapDesc={setNewGapDesc} newGapSev={newGapSev} setNewGapSev={setNewGapSev}
            onboardingCasl={onboardingCasl} handleOnboardingTaskToggle={handleOnboardingTaskToggle} handleOnboardingNotesSave={handleOnboardingNotesSave}
            editingTaskId={editingTaskId} setEditingTaskId={setEditingTaskId} editTaskNotes={editTaskNotes} setEditTaskNotes={setEditTaskNotes}
            handleOnboardingCaslSunset={handleOnboardingCaslSunset} simLogs={simLogs} simIsRunning={simIsRunning}
            complianceProgress={complianceProgress} riskScore={riskScore} riskTrend={riskTrend} assessmentCoverage={assessmentCoverage} openIssues={openIssues}
            employeeDataFlows={employeeDataFlows} thirdPartyDataFlows={thirdPartyDataFlows} activeThreats={activeThreats} recentAudits={recentAudits} complianceTrendData={complianceTrendData}
            expertExpandedAssessments={expertExpandedAssessments} toggleExpertAssessment={toggleExpertAssessment} onboardingSubMode={onboardingSubMode} setOnboardingSubMode={setOnboardingSubMode}
            lessonsIsExpanded={lessonsIsExpanded} setLessonsIsExpanded={setLessonsIsExpanded} agentLessons={agentLessons}
            hitlQueue={hitlQueue} inboxEmails={inboxEmails} agentLogs={agentLogs} isSimulatingLoop={isSimulatingLoop} isSystemOnline={isSystemOnline}
            activeLegislations={activeLegislations} handleResolveHitlDecision={handleResolveHitlDecision}
            govDataInventory={govDataInventory} govSubProcessors={govSubProcessors} govRoleHierarchy={govRoleHierarchy}
            agentsList={agentsList} caslRegistry={caslRegistry} caslLogs={caslLogs} caslDisclaimers={caslDisclaimers} caslDataElements={caslDataElements}
            meetingActionItems={meetingActionItems} inboxReplies={inboxReplies} onbUploadedFiles={onbUploadedFiles} onbLogs={onbLogs} legalLibrary={legalLibrary} onbProfile={onbProfile}
          />
        )}
        {/* PSR COMMITTEE MODE */}
        {securityMode === 'psr' && (
          <PsrMode 
            psrMeetings={psrMeetings} psrRiskQueue={psrRiskQueue} psrSelectedRisk={psrSelectedRisk} setPsrSelectedRisk={setPsrSelectedRisk}
            psrVote={psrVote} setPsrVote={setPsrVote} psrRecommendation={psrRecommendation} setPsrRecommendation={setPsrRecommendation}
            handlePsrRecommendationSubmit={handlePsrRecommendationSubmit} psrTransitionTasks={psrTransitionTasks}
            psrCopilotQuery={psrCopilotQuery} setPsrCopilotQuery={setPsrCopilotQuery} psrCopilotAnswer={psrCopilotAnswer} setPsrCopilotAnswer={setPsrCopilotAnswer}
          />
        )}

      </div>
    </div>
    </JurisdictionProvider>
  );
};

export default App;
