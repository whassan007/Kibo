import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Shield, AlertTriangle, Clock, Ban, Check, Undo2,
  ChevronDown, ChevronUp, Terminal, ShieldAlert, UserCheck, Search,
  HardDrive, Database, Network, FileCheck, Layers, RefreshCw, AlertOctagon,
  Users, Briefcase, Eye, Globe, User, Radio, FileUp, Sparkles, Send, Trash2,
  Activity, Server, Mail, Settings, Plus, CheckSquare, Square, Edit, Save, List
} from 'lucide-react';

const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? 'http://localhost:8000'
  : window.location.origin;

const App = () => {
  // --- Core State ---
  const [securityMode, setSecurityMode] = useState('expert'); // public, employee, expert, psr
  const [activeTab, setActiveTab] = useState('dashboard'); // for Expert mode
  const [activeJurisdiction, setActiveJurisdiction] = useState('ontario');
  const [jurConfig, setJurConfig] = useState({
    code: "ontario",
    flag: "🇨🇦",
    name: "Ontario (Public Sector) - FIPPA",
    access_request_term: "Freedom of Information Request",
    access_request_abbr: "FOI",
    data_subject_term: "Requester",
    regulator: "Information and Privacy Commissioner of Ontario (IPC)",
    primary_statute: "FIPPA",
    access_deadline_days: 30,
    breach_notification: "IPC + affected individuals (extendable clock)",
    assessment_types: ["PIA", "TRA"],
    training_track: "fippa"
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
  const [trainingCompliance, setTrainingCompliance] = useState(null);

  // --- PSR Committee Mode State ---
  const [psrMeetings, setPsrMeetings] = useState([]);
  const [psrRiskQueue, setPsrRiskQueue] = useState([]);
  const [psrSelectedRisk, setPsrSelectedRisk] = useState(null);
  const [psrVote, setPsrVote] = useState('approve');
  const [psrRecommendation, setPsrRecommendation] = useState('');

  // --- Canadian Onboarding & CASL State ---
  const [onboardingTasks, setOnboardingTasks] = useState([]);
  const [caslRegistry, setCaslRegistry] = useState([]);
  const [caslLogs, setCaslLogs] = useState([
    "[SYSTEM] Consent enforcement loop initialized.",
    "[SYSTEM] Awaiting sunset automation trigger..."
  ]);
  const [isSunsetting, setIsSunsetting] = useState(false);
  const [editingNotesTaskId, setEditingNotesTaskId] = useState(null);
  const [editingNotesText, setEditingNotesText] = useState("");

  // --- AI Onboarding Agent State ---
  const [onboardingSubMode, setOnboardingSubMode] = useState('checklist'); // 'checklist' or 'ai_agent'
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
          files: ["Data Governance Policy.docx", "Terms of Reference.docx", "Data Inventory.xlsx", "Information Management Policy.docx", "Risk Register.xlsx", "Privacy Policy.docx"]
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
          <div className="flex items-center space-x-2">
            <Globe size={14} className="text-blue-600" />
            <select
              value={activeJurisdiction}
              onChange={(e) => handleJurisdictionChange(e.target.value)}
              className="bg-white border border-[#E5E7EB] text-xs text-[#111827] px-3 py-1.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-all cursor-pointer shadow-xs"
            >
              {jurisdictionsList.map(j => (
                <option key={j.code} value={j.code}>
                  {j.flag} {j.name} ({j.primary_statute})
                </option>
              ))}
            </select>
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

              <div className="border-t border-[#E5E7EB] pt-4 text-[10px] text-gray-500 space-y-1.5 font-medium">
                <div>Statute: <span className="text-gray-700">{jurConfig.primary_statute}</span></div>
                <div>Regulator: <span className="text-gray-700">{jurConfig.regulator}</span></div>
                <div>Deadline: <span className="text-gray-700">{jurConfig.access_deadline_days} days</span></div>
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
                        <Clock size={16} className="text-blue-600 animate-pulse" />
                        <span className="text-lg font-extrabold text-[#111827]">{jurConfig.access_deadline_days} Days</span>
                      </div>
                      <div className="text-[9px] text-gray-400">Response deadline for active {jurConfig.access_request_abbr} requests.</div>
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
                                <div className="text-[10px] text-gray-500 leading-relaxed">{g.details}</div>
                              </div>
                              <button
                                onClick={() => setActiveTab('onboarding')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all"
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
                                <div className="text-[10px] text-gray-500 leading-relaxed">{h.details}</div>
                              </div>
                              <button
                                onClick={() => setActiveTab('cpo_agents')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all"
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
                            className="w-full text-left bg-white hover:bg-gray-50 text-gray-700 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
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
                            className="w-full text-left bg-white hover:bg-gray-550 text-gray-750 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
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
                          onClick={() => setSelectedEmail(email)}
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
                  <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl min-h-[300px] shadow-xs">
                    {selectedEmail ? (
                      <div className="space-y-4 text-xs">
                        <div className="border-b border-[#E5E7EB] pb-3 space-y-1.5">
                          <div className="flex justify-between">
                            <span className="text-gray-500 uppercase font-semibold">From:</span>
                            <span className="text-[#111827] font-medium">{selectedEmail.sender}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500 uppercase font-semibold">Subject:</span>
                            <span className="text-[#111827] font-medium">{selectedEmail.subject}</span>
                          </div>
                        </div>

                        <div className="text-gray-800 whitespace-pre-wrap leading-relaxed py-2 bg-gray-50 p-3.5 rounded-lg border border-[#E5E7EB] font-mono text-[12px]">
                          {selectedEmail.body}
                        </div>

                        <div className="flex space-x-3 pt-2">
                          {selectedEmail.status === 'unread' ? (
                            <button
                              onClick={() => handleTriageEmail(selectedEmail.email_id)}
                              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg uppercase text-[10px] tracking-wide shadow-sm transition-all cursor-pointer"
                            >
                              Triage into Transaction
                            </button>
                          ) : (
                            <div className="text-emerald-750 font-bold flex items-center space-x-1.5">
                              <Check size={14} />
                              <span>Triaged and converted to thread</span>
                            </div>
                          )}
                        </div>
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
                                <div className="border border-dashed border-gray-250 p-4 rounded-lg text-center bg-gray-50/50">
                                  <FileUp size={18} className="mx-auto text-gray-450 mb-1" />
                                  <div className="text-[10px] text-gray-650 font-bold">6 Target Documents Selected</div>
                                  <div className="text-[9px] text-gray-400 mt-0.5">Information Management, Data Inventory XLS, Terms of Reference, etc.</div>
                                </div>
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
          <div className="flex-1 flex overflow-hidden">
            
            {/* Left Column: Meetings & Materials */}
            <div className="w-1/2 border-r border-[#E5E7EB] p-6 space-y-6 overflow-y-auto bg-[#FAFAFA]">
              
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
                        <div className="text-gray-700 bg-gray-50 border border-[#E5E7EB] p-3 rounded-lg mt-1 font-mono text-[11px]">
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
              <div className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-gray-550">Advisory Review Materials</div>
                <div className="grid grid-cols-1 gap-2.5">
                  <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                    <span className="font-semibold text-[#111827]">Quebec Law 25 Diagnostic Posture.pdf</span>
                    <button className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
                  </div>
                  <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                    <span className="font-semibold text-[#111827]">Cross-Border Transfer TIA v1.docx</span>
                    <button className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-all cursor-pointer shadow-xs">Download</button>
                  </div>
                  <div className="bg-white border border-[#E5E7EB] p-3.5 rounded-xl text-xs flex justify-between items-center shadow-xs">
                    <span className="font-semibold text-[#111827]">Canadian Privacy Commissioner Rulings Newsletter (July 2026).md</span>
                    <a href="/canadian_privacy_newsletter.md" target="_blank" rel="noopener noreferrer" className="text-blue-600 text-[10px] font-bold uppercase border border-[#E5E7EB] hover:bg-gray-550 px-3 py-1.5 rounded-lg text-center transition-all shadow-xs">View</a>
                  </div>
                </div>
              </div>

              {/* Research & Regulatory Libraries */}
              <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
                <div className="text-xs font-bold uppercase tracking-wider text-gray-500">Commissioner Research Libraries</div>
                <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                  <a href="https://www.priv.gc.ca/en/opc-actions-and-decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                    <span>Federal (OPC) Actions</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                  <a href="https://www.cai.gouv.qc.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
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
                  <a href="https://www.ipc.on.ca/en/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-550 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                    <span>Ontario (IPC) Orders</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                  <a href="https://oipc.sk.ca/decisions/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                    <span>Saskatchewan (OIPC)</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                  <a href="https://oipc.novascotia.ca/decisions" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                    <span>Nova Scotia (OIPC)</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                  <a href="https://www.oipc.nl.ca/reports/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 hover:border-gray-350 flex justify-between items-center text-gray-700 transition-all shadow-xs">
                    <span>Newfoundland (OIPC)</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                  <a href="https://www.ombudsman.mb.ca/" target="_blank" rel="noopener noreferrer" className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg hover:bg-gray-555 hover:border-gray-350 flex justify-between items-center text-gray-700 col-span-2 transition-all shadow-xs">
                    <span>Manitoba Ombudsman Reports</span>
                    <Globe size={11} className="text-blue-600" />
                  </a>
                </div>
              </div>

            </div>

            {/* Right Column: Risk Advisory Queue */}
            <div className="w-1/2 p-6 overflow-y-auto space-y-6 bg-[#FAFAFA]">
              
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
        )}

      </div>
    </div>
  );
};

export default App;
