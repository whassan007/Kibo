import React, { useState, useEffect, useRef } from 'react';
import {
  FileText, Shield, AlertTriangle, Clock, Ban, Check, Undo2,
  ChevronDown, ChevronUp, Terminal, ShieldAlert, UserCheck, Search,
  HardDrive, Database, Network, FileCheck, Layers, RefreshCw, AlertOctagon,
  Users, Briefcase, Eye, Globe, User, Radio, FileUp, Sparkles, Send, Trash2
} from 'lucide-react';

export const App = () => {
  // --- Core Security & Mode State ---
  // Modes: 'public', 'employee', 'expert'
  const [securityMode, setSecurityMode] = useState('expert');

  // Navigation state within modes
  const [activeTab, setActiveTab] = useState('dashboard'); // for Expert mode: queue, sensory, lifecycle, vault, onboarding
  
  // Data Stream Layers
  const [transactions, setTransactions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [rules, setRules] = useState([]);
  
  // Forms & Decision State
  const [reasoning, setReasoning] = useState('');
  const [sectoralInputs, setSectoralInputs] = useState({});
  
  // Auditing & Cryptography
  const [secureAuditHash, setSecureAuditHash] = useState('');
  const [auditReceipt, setAuditReceipt] = useState(null);
  
  // Resiliency & Anomaly Handlers
  const [isSystemOnline, setIsSystemOnline] = useState(true);
  const [isDbLocked, setIsDbLocked] = useState(false);
  const [offlineQueue, setOfflineQueue] = useState([]);
  const [syncAttempts, setSyncAttempts] = useState(0);
  const [simulatedLeak, setSimulatedLeak] = useState(false);
  
  // Selected vault path
  const [selectedVaultDoc, setSelectedVaultDoc] = useState(null);

  // --- Onboarding Systems State ---
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [findings, setFindings] = useState([]);
  const [selectedFindingId, setSelectedFindingId] = useState(null);
  const [report, setReport] = useState(null);
  const [newClientName, setNewClientName] = useState('');
  const [newClientUrl, setNewClientUrl] = useState('');
  const [newClientMode, setNewClientMode] = useState('website');
  const [newClientThreshold, setNewClientThreshold] = useState(0.70);
  const [isAddingClient, setIsAddingClient] = useState(false);

  // SSE discovery logging state
  const [discoveryLog, setDiscoveryLog] = useState([]);
  const [discoveryProgress, setDiscoveryProgress] = useState(0);
  const [discoveryAgent, setDiscoveryAgent] = useState('');
  const [isDiscovering, setIsDiscovering] = useState(false);

  // Onboarding mode states
  const [guidedAnswers, setGuidedAnswers] = useState({
    collect_customer_info: true,
    process_employee_info: true,
    operate_internationally: false,
    process_health_info: false,
    process_financial_info: false,
    collect_children_data: false,
    use_ai_systems: false,
    use_biometrics: false,
  });
  const [systemConnectors, setSystemConnectors] = useState({
    identity: false,
    productivity: false,
    cloud: false,
    data: false,
    hr: false,
  });
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Finding modify sub-states
  const [modifyTitle, setModifyTitle] = useState('');
  const [modifyDesc, setModifyDesc] = useState('');
  const [isModifyingFinding, setIsModifyingFinding] = useState(false);

  // --- Public Mode State ---
  const [publicQuery, setPublicQuery] = useState('');
  const [publicAnswer, setPublicAnswer] = useState('');
  const [publicDsarName, setPublicDsarName] = useState('');
  const [publicDsarEmail, setPublicDsarEmail] = useState('');
  const [publicDsarType, setPublicDsarType] = useState('access');
  const [publicDsarDescription, setPublicDsarDescription] = useState('');
  const [publicDsarStatus, setPublicDsarStatus] = useState('');

  // --- Employee Mode State ---
  const [employeeSearchQuery, setEmployeeSearchQuery] = useState('');
  const [employeePolicyResult, setEmployeePolicyResult] = useState('');
  const [incidentTitle, setIncidentTitle] = useState('');
  const [incidentDesc, setIncidentDesc] = useState('');
  const [incidentStatus, setIncidentStatus] = useState('');

  // --- Employee Mode Refactored State ---
  const [employeeIntakes, setEmployeeIntakes] = useState([]);
  const [employeeMitigations, setEmployeeMitigations] = useState([]);
  const [opcInquiries, setOpcInquiries] = useState([]);
  const [selectedOpcThreadId, setSelectedOpcThreadId] = useState(null);
  const [opcReplyText, setOpcReplyText] = useState('');
  
  const [intakeForm, setIntakeForm] = useState({
    id: '',
    project_name: '',
    purpose: '',
    data_classification: [],
    retention_value: 0,
    retention_unit: 'days'
  });
  const [isEditingIntake, setIsEditingIntake] = useState(false);
  const [intakeError, setIntakeError] = useState('');
  const [intakeSubmitStatus, setIntakeSubmitStatus] = useState('');
  const [mitigationUpdateStatus, setMitigationUpdateStatus] = useState('');
  
  const [isLoadingIntakes, setIsLoadingIntakes] = useState(false);
  const [isLoadingMitigations, setIsLoadingMitigations] = useState(false);
  const [isLoadingOpc, setIsLoadingOpc] = useState(false);
  const [offlineReplyQueue, setOfflineReplyQueue] = useState([]);
  const [networkErrorThreadId, setNetworkErrorThreadId] = useState(null);




  // --- RBAC and Vault State ---
  const [currentUserRole, setCurrentUserRole] = useState('CPO');
  const [isOffline, setIsOffline] = useState(false);
  const [syncQueue, setSyncQueue] = useState([]);
  const [vaultJobId, setVaultJobId] = useState(null);
  const [vaultJobStatus, setVaultJobStatus] = useState(null);
  const [vaultJobHash, setVaultJobHash] = useState(null);

  // AuthContext Capability Check
  const hasCapability = (role, action) => {
    if (role === 'CPO') return true;
    if (role === 'DPO' && ['approve_now', 'flag_legal', 'review_later', 'generate_vault'].includes(action)) return true;
    if (role === 'ANALYST' && ['submit_for_review', 'flag_dpo'].includes(action)) return true;
    return false;
  };


  const StrictRoute = ({ children, requiredRoles }) => {
    if (!requiredRoles.includes(currentUserRole)) {
      return (
        <div className="flex-1 flex flex-col items-center justify-center bg-slate-950 p-8 text-center h-full">
          <ShieldAlert className="text-red-500 mb-6" size={64} />
          <h1 className="text-4xl font-mono font-bold text-slate-200 mb-4 tracking-widest">[!] 403: INSUFFICIENT CLEARANCE</h1>
          <p className="font-mono text-red-500 bg-red-950/50 px-4 py-2 border border-red-900 rounded">
            REQUIRED: {requiredRoles.join(' OR ')}.<br/>CURRENT: {currentUserRole}.
          </p>
          <div className="mt-8 text-xs font-mono text-slate-500">
            Unauthorized access attempt has been logged.
          </div>
        </div>
      );
    }
    return children;
  };

  const RequireCapability = ({ action, children, fallback = null }) => {
    return hasCapability(currentUserRole, action) ? children : fallback;
  };

  // --- CPO Upgrade States ---
  const [dashboardPosture, setDashboardPosture] = useState(null);
  const [dashboardTrends, setDashboardTrends] = useState([]);
  const [reportsData, setReportsData] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [radarItems, setRadarItems] = useState([]);
  const [incidentsList, setIncidentsList] = useState([]);
  
  // Approval Matrix State
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [pendingDecision, setPendingDecision] = useState(null);
  const [approvalForm, setApprovalForm] = useState({
    identity_verified: false,
    systems_matched: 0,
    no_legal_hold: false,
    within_retention: false,
    note: ''
  });

  // --- CPO Command Deck State ---
  const [skillsMatrix, setSkillsMatrix] = useState({});
  const [cpoAllMitigations, setCpoAllMitigations] = useState([]);
  const [cpoOverrideStatus, setCpoOverrideStatus] = useState('');

  // Telemetry State
  const [telemetrySearch, setTelemetrySearch] = useState('');
  const [telemetrySearchResults, setTelemetrySearchResults] = useState([]);
  const [selectedTelemetryProject, setSelectedTelemetryProject] = useState(null);
  const [telemetryData, setTelemetryData] = useState(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [generatedReport, setGeneratedReport] = useState(null);


  // References
  const retryTimeoutRef = useRef(null);
  const eventSourceRef = useRef(null);

  // --- Risk Register State ---
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [risks, setRisks] = useState([]);
  const [selectedRisk, setSelectedRisk] = useState(null);
  const [riskForm, setRiskForm] = useState(null);
  const [riskAuditLog, setRiskAuditLog] = useState([]);
  const [riskFilterLevel, setRiskFilterLevel] = useState('ALL');
  const [riskFilterAssignee, setRiskFilterAssignee] = useState('ALL');
  const [riskFilterGap, setRiskFilterGap] = useState('ALL');
  const [riskFilterOverdue, setRiskFilterOverdue] = useState(false);
  const [riskSortCol, setRiskSortCol] = useState('risk_id');
  const [riskSortDir, setRiskSortDir] = useState('asc');
  const [riskEditStatus, setRiskEditStatus] = useState('');
  const [isLoadingRisks, setIsLoadingRisks] = useState(false);

  // Employee View state
  const [expandedRiskId, setExpandedRiskId] = useState(null);
  const [extensionRequestText, setExtensionRequestText] = useState('');
  const [extensionSuggestedDate, setExtensionSuggestedDate] = useState('');
  const [showExtensionId, setShowExtensionId] = useState(null);

  const queryParams = new URLSearchParams(window.location.search);
  const currentUser = queryParams.get('user') || 'Waël';

  const navigateTo = (path) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
  };

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
    ? "http://127.0.0.1:8000/api"
    : "http://waelbot.local:8000/api";

  // Mock data fallback if backend is offline
  const MOCK_TRANSACTIONS = [
    {
      id: "thread-101",
      type: "DSAR",
      client: "TechCorp Inc.",
      jurisdiction: "US-State Laws",
      priority: "critical",
      deadline: "48 hours",
      description: "Verify identity and process CCPA deletion request.",
      agent: "US DSAR Rights Agent",
      summary: "User authenticated. 3 systems matched. No legal hold.",
      raw: '{"systems": ["crm", "billing"], "confidence": 0.99, "request_type": "deletion", "opt_out_detected": true}'
    },
    {
      id: "thread-102",
      type: "Vendor",
      client: "CloudScale Inc.",
      jurisdiction: "US-Health",
      priority: "high",
      deadline: "12 hours",
      description: "Evaluate vendor GDPR DPA adequacy for analytics integration.",
      agent: "EU Data Transfer Auditor",
      summary: "Standard contractual clauses present. Sub-processors listed.",
      raw: '{"risk_level": "medium", "data_location": "Frankfurt", "phi_accessed": true}'
    },
    {
      id: "thread-103",
      type: "Breach",
      client: "HealthFirst Corp",
      jurisdiction: "US-Finance",
      priority: "critical",
      deadline: "24 hours",
      description: "Perform HIPAA compliance review on misconfigured S3 bucket.",
      agent: "Canada PHIPA Security Agent",
      summary: "Exposed files: 120 health charts. Exposure time: 14 hours.",
      raw: '{"affected_records": 120, "pii_exposed": true, "safeguards_tested": false}'
    }
  ];

  // Helper fetch function to inject the X-Kibo-Scope header automatically
  const kiboFetch = async (url, options = {}) => {
    const headers = {
      ...options.headers,
      'X-Kibo-Scope': securityMode
    };
    return fetch(url, { ...options, headers });
  };

  // Fetch core data from FastAPI agent_gateway
  const fetchData = async () => {
    try {
      const txRes = await kiboFetch(`${API_BASE}/transactions`);
      if (!txRes.ok) throw new Error('API server returned error');
      const txData = await txRes.json();
      
      setTransactions(txData);
      setIsSystemOnline(true);
      
      // Auto-select first pending transaction
      if (txData.length > 0 && !selectedId) {
        const firstPending = txData.find(t => t.status === 'pending');
        setSelectedId(firstPending ? firstPending.id : txData[0].id);
      }
      
      const rulesRes = await kiboFetch(`${API_BASE}/rules`);
      if (rulesRes.ok) {
        const rulesData = await rulesRes.json();
        setRules(rulesData);
      }

      // Fetch client list if in expert mode
      if (securityMode === 'expert') {
        const clientsRes = await kiboFetch(`${API_BASE}/clients`);
        if (clientsRes.ok) {
          const clientsData = await clientsRes.json();
          setClients(clientsData);
          if (clientsData.length > 0 && !selectedClientId) {
            setSelectedClientId(clientsData[0].id);
          }
        }
      }
    } catch (err) {
      console.warn("Backend connection offline or unauthorized. Using local simulated state.");
      setIsSystemOnline(false);
      if (transactions.length === 0) {
        setTransactions(MOCK_TRANSACTIONS.map(t => ({ ...t, status: 'pending' })));
        setSelectedId("thread-101");
      }
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // 10s passive polling
    return () => clearInterval(interval);
  }, [securityMode]);

  // Fetch specific client findings and report data
  useEffect(() => {
    if (securityMode === 'expert' && selectedClientId) {
      fetchClientDetails(selectedClientId);
    }
  }, [selectedClientId, securityMode]);

  const fetchClientDetails = async (clientId) => {
    try {
      const findingsRes = await kiboFetch(`${API_BASE}/clients/${clientId}/findings`);
      if (findingsRes.ok) {
        const findingsData = await findingsRes.ok ? await findingsRes.json() : [];
        setFindings(findingsData);
      }

      const reportRes = await kiboFetch(`${API_BASE}/clients/${clientId}/report`);
      if (reportRes.ok) {
        const reportData = await reportRes.json();
        setReport(reportData);
      }
    } catch (err) {
      console.error("Error fetching client details", err);
    }
  };

  const fetchEmployeeData = async () => {
    if (securityMode !== 'employee') return;
    setIsLoadingIntakes(true);
    setIsLoadingMitigations(true);
    setIsLoadingOpc(true);
    try {
      const intakeRes = await kiboFetch(`${API_BASE}/employee/intake`);
      if (intakeRes.ok) {
        setEmployeeIntakes(await intakeRes.json());
      }
      setIsLoadingIntakes(false);
      
      const mitRes = await kiboFetch(`${API_BASE}/employee/mitigation`);
      if (mitRes.ok) {
        setEmployeeMitigations(await mitRes.json());
      }
      setIsLoadingMitigations(false);
      
      const opcRes = await kiboFetch(`${API_BASE}/employee/opc-inquiries`);
      if (opcRes.ok) {
        const opcData = await opcRes.json();
        setOpcInquiries(opcData);
        if (opcData.length > 0 && !selectedOpcThreadId) {
          setSelectedOpcThreadId(opcData[0].thread_id);
        }
      }
      setIsLoadingOpc(false);
    } catch (err) {
      console.error("Error fetching employee data", err);
      setIsLoadingIntakes(false);
      setIsLoadingMitigations(false);
      setIsLoadingOpc(false);
    }
  };

  useEffect(() => {
    if (securityMode === 'employee') {
      fetchEmployeeData();
      const interval = setInterval(fetchEmployeeData, 10000);
      return () => clearInterval(interval);
    }
  }, [securityMode]);


  const fetchCPOData = async () => {
    try {
      const res1 = await kiboFetch('http://100.117.49.65:8000/api/cpo/skills-matrix', { headers: { 'x-kibo-scope': 'expert' }});
      if (res1.ok) setSkillsMatrix(await res1.json());
      const res2 = await kiboFetch('http://100.117.49.65:8000/api/cpo/mitigations', { headers: { 'x-kibo-scope': 'expert' }});
      if (res2.ok) setCpoAllMitigations(await res2.json());
    } catch(e) {}
  };

  const handleCPOOverride = async (employee_id, target_id, action, new_assignee) => {
    try {
      const res = await kiboFetch('http://100.117.49.65:8000/api/cpo/override', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-kibo-scope': 'expert' },
        body: JSON.stringify({ employee_id, target_id, action, new_assignee })
      });
      if (res.ok) {
        setCpoOverrideStatus('Override applied: ' + action);
        setTimeout(() => setCpoOverrideStatus(''), 3000);
        fetchCPOData();
      }
    } catch(e) {}
  };


  const handleTelemetrySearch = async (query) => {
    setTelemetrySearch(query);
    if (query.length > 1) {
      try {
        const res = await kiboFetch(`http://100.117.49.65:8000/api/cpo/projects/search?q=${query}`, { headers: { 'x-kibo-scope': 'expert' }});
        if (res.ok) setTelemetrySearchResults(await res.json());
      } catch (e) {}
    } else {
      setTelemetrySearchResults([]);
    }
  };

  const loadProjectTelemetry = async (projectId) => {
    try {
      const res = await kiboFetch(`http://100.117.49.65:8000/api/projects/${projectId}/telemetry`, { headers: { 'x-kibo-scope': 'expert' }});
      if (res.ok) setTelemetryData(await res.json());
      setSelectedTelemetryProject(projectId);
      setTelemetrySearchResults([]);
      setTelemetrySearch('');
    } catch (e) {}
  };

  const generateRiskReport = async () => {
    if (!telemetryData) return;
    setIsGeneratingReport(true);
    setGeneratedReport(null);
    try {
      const res = await kiboFetch(`http://100.117.49.65:8000/api/projects/${telemetryData.project_id}/report/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-kibo-scope': 'expert' },
        body: JSON.stringify({ requested_by: 'system_cpo', include_history: true })
      });
      if (res.ok) setGeneratedReport(await res.json());
    } catch (e) {}
    setIsGeneratingReport(false);
  };

  const triggerHorizon = async () => {
    try {
      const res = await kiboFetch('http://100.117.49.65:8000/api/horizon/re-evaluate', {
        method: 'POST',
        headers: { 'x-kibo-scope': 'expert' }
      });
      if (res.ok) {
        setCpoOverrideStatus('Horizon Expired: Re-evaluation triggered globally.');
        setTimeout(() => setCpoOverrideStatus(''), 3000);
      }
    } catch(e) {}
  };

  useEffect(() => {
    if (securityMode === 'expert' && activeTab === 'command_deck') {
      fetchCPOData();
    }
  }, [securityMode, activeTab]);


  const loadDashboard = async () => {
    try {
      const p = await kiboFetch('http://100.117.49.65:8000/api/dashboard/posture', {headers: {'x-kibo-scope': 'expert'}});
      if (p.ok) setDashboardPosture(await p.json());
      const t = await kiboFetch('http://100.117.49.65:8000/api/dashboard/trends', {headers: {'x-kibo-scope': 'expert'}});
      if (t.ok) setDashboardTrends(await t.json());
      const r = await kiboFetch('http://100.117.49.65:8000/api/radar', {headers: {'x-kibo-scope': 'expert'}});
      if (r.ok) setRadarItems(await r.json());
    } catch(e) {}
  };

  const loadHealth = async () => {
    try {
      const h = await kiboFetch('http://100.117.49.65:8000/api/system/health', {headers: {'x-kibo-scope': 'expert'}});
      if (h.ok) setHealthStatus(await h.json());
    } catch(e) {}
  };

  const loadReports = async () => {
    try {
      const r = await kiboFetch('http://100.117.49.65:8000/api/reports/query', {headers: {'x-kibo-scope': 'expert'}});
      if (r.ok) setReportsData(await r.json());
    } catch(e) {}
  };

  useEffect(() => {
    if (securityMode === 'expert') {
      if (activeTab === 'dashboard') loadDashboard();
      if (activeTab === 'health') loadHealth();
      if (activeTab === 'reports') loadReports();
    }
  }, [securityMode, activeTab]);

  // --- Risk Register Handlers ---
  const fetchRisks = async () => {
    setIsLoadingRisks(true);
    try {
      const isEmployeeView = window.location.pathname.includes('/my-risks') || window.location.pathname.includes('/risks/me');
      const url = isEmployeeView
        ? `${API_BASE}/risks/assigned/${currentUser}`
        : `${API_BASE}/risks`;
      const res = await kiboFetch(url);
      if (res.ok) {
        setRisks(await res.json());
      }
    } catch (err) {
      console.error("Error fetching risks", err);
    } finally {
      setIsLoadingRisks(false);
    }
  };

  const fetchRiskLog = async (riskId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/risks/${riskId}/log`);
      if (res.ok) {
        setRiskAuditLog(await res.json());
      }
    } catch (err) {
      console.error("Error fetching risk log", err);
    }
  };

  useEffect(() => {
    const path = window.location.pathname;
    if (path.includes('/risks') || path.includes('/risk-register') || path.includes('/my-risks')) {
      fetchRisks();
    }
  }, [currentPath, currentUser]);

  const handleSelectRisk = (risk) => {
    setSelectedRisk(risk);
    setRiskForm({ ...risk });
    fetchRiskLog(risk.risk_id);
    setRiskEditStatus('');
  };

  const handleNewRisk = () => {
    setSelectedRisk(null);
    setRiskForm({
      risk_id: 'AUTO-GENERATED',
      law_25_section: '',
      issue: '',
      source_document: '',
      source_id: '',
      source_title: '',
      gap_type: 'Operational Gap',
      likelihood: 3,
      impact: 3,
      original_risk_level: 'Medium',
      recommendation: '',
      khp_response: '',
      status_note: '',
      assigned_to: 'Waël',
      risk_assigned_date: new Date().toISOString().split('T')[0],
      next_review_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    });
    setRiskAuditLog([]);
    setRiskEditStatus('');
  };

  const handleSaveRisk = async (e) => {
    if (e) e.preventDefault();
    if (!riskForm) return;
    
    // Auto calculate level
    const score = riskForm.likelihood * riskForm.impact;
    let level = 'Low';
    if (score >= 15) level = 'High';
    else if (score >= 8) level = 'Medium';
    
    const formToSubmit = {
      ...riskForm,
      risk_score: score,
      risk_level: level
    };

    // Optimistic UI update
    setRisks(prev => {
      const idx = prev.findIndex(r => r.risk_id === riskForm.risk_id);
      if (idx > -1) {
        const copy = [...prev];
        copy[idx] = { ...copy[idx], ...formToSubmit };
        return copy;
      }
      return prev;
    });

    try {
      const isNew = riskForm.risk_id === 'AUTO-GENERATED';
      const method = isNew ? 'POST' : 'PUT';
      const url = isNew ? `${API_BASE}/risks` : `${API_BASE}/risks/${riskForm.risk_id}`;
      
      const res = await kiboFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formToSubmit)
      });
      
      if (res.ok) {
        const data = await res.json();
        setRiskEditStatus('Saved ✓');
        fetchRisks();
        if (isNew) {
          // If newly created, select it
          const createdRisk = { ...formToSubmit, risk_id: data.risk_id };
          setSelectedRisk(createdRisk);
          setRiskForm(createdRisk);
          fetchRiskLog(data.risk_id);
        } else {
          fetchRiskLog(riskForm.risk_id);
        }
      }
    } catch (err) {
      console.error("Error saving risk", err);
    }
  };

  const handleCloseRisk = async (riskId) => {
    // Optimistic UI update
    setRisks(prev => prev.map(r => r.risk_id === riskId ? { ...r, status: 'closed' } : r));
    try {
      const res = await kiboFetch(`${API_BASE}/risks/${riskId}/close`, { method: 'PATCH' });
      if (res.ok) {
        setRiskEditStatus('Resolved ✓');
        fetchRisks();
        fetchRiskLog(riskId);
        if (selectedRisk && selectedRisk.risk_id === riskId) {
          setSelectedRisk(prev => ({ ...prev, status: 'closed' }));
          setRiskForm(prev => ({ ...prev, status: 'closed' }));
        }
      }
    } catch (err) {
      console.error("Error closing risk", err);
    }
  };

  const handleDeleteRisk = async (riskId) => {
    if (!window.confirm("Are you sure you want to permanently delete this risk?")) return;
    
    // Optimistic UI update
    setRisks(prev => prev.filter(r => r.risk_id !== riskId));
    try {
      const res = await kiboFetch(`${API_BASE}/risks/${riskId}`, { method: 'DELETE' });
      if (res.ok) {
        setSelectedRisk(null);
        setRiskForm(null);
        fetchRisks();
      }
    } catch (err) {
      console.error("Error deleting risk", err);
    }
  };

  const handleAcknowledgeRisk = async (riskId) => {
    try {
      const res = await kiboFetch(`${API_BASE}/risks/${riskId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actor: currentUser, note: `Acknowledged review by ${currentUser}.` })
      });
      if (res.ok) {
        alert("Acknowledged review submitted successfully.");
        fetchRisks();
      }
    } catch (err) {
      console.error("Error acknowledging risk", err);
    }
  };

  const handleRequestExtension = async (riskId) => {
    if (!extensionSuggestedDate || !extensionRequestText) {
      alert("Please select a suggested date and specify the reason.");
      return;
    }
    try {
      const res = await kiboFetch(`${API_BASE}/risks/${riskId}/extension`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor: currentUser,
          suggested_date: extensionSuggestedDate,
          reason: extensionRequestText
        })
      });
      if (res.ok) {
        alert("Extension request submitted and routed to CPO decision queue.");
        setShowExtensionId(null);
        setExtensionRequestText('');
        setExtensionSuggestedDate('');
        fetchRisks();
      }
    } catch (err) {
      console.error("Error requesting extension", err);
    }
  };

  const handlePostIntake = async (e) => {
    e.preventDefault();
    setIntakeError('');
    setIntakeSubmitStatus('submitting');
    
    // Explicit validation before submission
    if (!intakeForm.project_name || !intakeForm.purpose || intakeForm.data_classification.length === 0 || !intakeForm.retention_value || !intakeForm.retention_unit) {
      setIntakeError('All fields are required, and at least one data classification must be selected.');
      setIntakeSubmitStatus('error');
      return;
    }
    
    const payload = {
      id: intakeForm.id || `intake-${Date.now().toString().slice(-6)}`,
      project_name: intakeForm.project_name,
      purpose: intakeForm.purpose,
      data_classification: intakeForm.data_classification,
      retention_value: parseInt(intakeForm.retention_value, 10),
      retention_unit: intakeForm.retention_unit
    };

    try {
      const response = await kiboFetch(`${API_BASE}/employee/intake`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        setIntakeSubmitStatus('success');
        setIsEditingIntake(false);
        setIntakeForm({ id: '', project_name: '', purpose: '', data_classification: [], retention_value: 0, retention_unit: 'days', status: 'draft' });
        fetchEmployeeData();
      } else {
        const errorDetail = await response.json();
        setIntakeError(errorDetail.detail || 'Submission rejected by compliance gateway.');
        setIntakeSubmitStatus('error');
      }
    } catch (err) {
      setIntakeError('Network connection failed. Form submission buffered locally.');
      setIntakeSubmitStatus('error');
    }
  };

  const handlePatchMitigation = async (planId, status) => {
    setMitigationUpdateStatus('updating');
    try {
      const response = await kiboFetch(`${API_BASE}/employee/mitigation/${planId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      
      if (response.ok) {
        setMitigationUpdateStatus('success');
        fetchEmployeeData();
      } else {
        setMitigationUpdateStatus('error');
      }
    } catch (err) {
      setMitigationUpdateStatus('error');
    }
  };

  const handlePostOpcReply = async (e) => {
    e.preventDefault();
    if (!opcReplyText || !selectedOpcThreadId) return;

    const messageId = `msg-reply-${Date.now().toString().slice(-6)}`;
    const payload = {
      message_id: messageId,
      body: opcReplyText
    };

    try {
      const response = await kiboFetch(`${API_BASE}/employee/opc-inquiries/${selectedOpcThreadId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setOpcReplyText('');
        fetchEmployeeData();
      } else {
        throw new Error('API server rejected message');
      }
    } catch (err) {
      console.warn("Connection timeout. Buffering message in offline queue.");
      const queuedMsg = { thread_id: selectedOpcThreadId, payload };
      setOfflineReplyQueue(prev => [...prev, queuedMsg]);
      setNetworkErrorThreadId(selectedOpcThreadId);
    }
  };

  const handleRetryOpcSync = async (threadId) => {
    const nextItem = offlineReplyQueue.find(item => item.thread_id === threadId);
    if (!nextItem) return;

    try {
      const response = await kiboFetch(`${API_BASE}/employee/opc-inquiries/${threadId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nextItem.payload)
      });

      if (response.ok) {
        setOfflineReplyQueue(prev => prev.filter(item => item.thread_id !== threadId));
        setNetworkErrorThreadId(null);
        setOpcReplyText('');
        fetchEmployeeData();
      }
    } catch (err) {
      console.error("Retry sync failed", err);
    }
  };

  // SHA-256 browser-native cryptographic generator
  const generateSHA256 = async (text) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  };

  // Keyboard navigation shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (document.activeElement?.tagName === 'TEXTAREA' || document.activeElement?.tagName === 'INPUT') {
        return;
      }
      if (e.key === 'j') {
        // Next transaction
        const idx = transactions.findIndex(t => t.id === selectedId);
        if (idx !== -1 && idx < transactions.length - 1) {
          setSelectedId(transactions[idx + 1].id);
        }
      } else if (e.key === 'k') {
        // Previous transaction
        const idx = transactions.findIndex(t => t.id === selectedId);
        if (idx > 0) {
          setSelectedId(transactions[idx - 1].id);
        }
      } else if (e.key === '1') {
        handleAction('approve_now');
      } else if (e.key === '2') {
        handleAction('approve_always');
      } else if (e.key === '3') {
        handleAction('flag_legal');
      } else if (e.key === '4') {
        handleAction('review_later');
      } else if (e.key === '5') {
        handleAction('reject');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedId, transactions]);

  // DB Sync retry handler
  const processOfflineQueue = async (queue) => {
    if (queue.length === 0) return;
    setIsDbLocked(true);
    const nextAction = queue[0];
    
    const delay = Math.min(1000 * Math.pow(2, nextAction.retries), 10000);
    setSyncAttempts(nextAction.retries + 1);

    if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
    
    retryTimeoutRef.current = setTimeout(async () => {
      try {
        const response = await kiboFetch(`${API_BASE}/transactions/${nextAction.txId}/decision`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: nextAction.action,
            reasoning: nextAction.reasoning
          })
        });
        
        if (!response.ok) throw new Error('Database locked');
        
        const remaining = queue.slice(1);
        setOfflineQueue(remaining);
        setIsDbLocked(false);
        setSyncAttempts(0);
        fetchData();
      } catch (err) {
        console.warn("DB synchronization trace blocked. Retrying with backoff...");
        const updated = [...queue];
        updated[0] = { ...nextAction, retries: nextAction.retries + 1 };
        setOfflineQueue(updated);
        processOfflineQueue(updated);
      }
    }, delay);
  };

  const handleAction = async (actionType) => {
    const currentTx = transactions.find(t => t.id === selectedId);
    if (!currentTx) return;

    // Generate cryptographic hash
    const stateSnapshotString = JSON.stringify({
      id: currentTx.id,
      client: currentTx.client,
      decision: actionType,
      reasoning: reasoning || "CPO manual decision.",
      sectoralInputs: sectoralInputs
    });
    const hash = await generateSHA256(stateSnapshotString);
    setSecureAuditHash(hash);
    setAuditReceipt({ txId: currentTx.id, hash });

    // Instantly reflect resolution inside CPO local UI
    setTransactions(prev => prev.map(t => {
      if (t.id === currentTx.id) {
        const resolvedLabelMap = {
          approve_now: "approved",
          approve_always: "auto_approved",
          flag_legal: "flagged_legal",
          review_later: "deferred",
          reject: "rejected"
        };
        return {
          ...t,
          status: resolvedLabelMap[actionType] || "completed",
          human_decision: actionType,
          human_reasoning: reasoning
        };
      }
      return t;
    }));

    // Queue action for backend serialization
    const actionPayload = {
      txId: currentTx.id,
      action: actionType,
      reasoning: reasoning || "CPO alignment gate cleared.",
      retries: 0
    };

    const newQueue = [...offlineQueue, actionPayload];
    setOfflineQueue(newQueue);
    setReasoning('');

    // Trigger database dispatcher
    if (isSystemOnline) {
      processOfflineQueue(newQueue);
    } else {
      console.warn("Local cache preserved. Device is operating in offline boundary mode.");
    }
  };

  // --- Client Onboarding Handlers ---
  const handleCreateClient = async (e) => {
    e.preventDefault();
    if (!newClientName) return;

    try {
      const response = await kiboFetch(`${API_BASE}/clients/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newClientName,
          url: newClientUrl,
          mode: newClientMode,
          threshold: newClientThreshold
        })
      });

      if (response.ok) {
        const data = await response.json();
        setNewClientName('');
        setNewClientUrl('');
        setIsAddingClient(false);
        fetchData();
        setSelectedClientId(data.client_id);
      }
    } catch (err) {
      console.error("Failed to create client", err);
    }
  };

  const handleStartDiscovery = async (clientId, mode) => {
    if (isDiscovering) return;
    
    try {
      if (mode === 'guided') {
        await kiboFetch(`${API_BASE}/clients/${clientId}/discover/guided`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(guidedAnswers)
        });
      } else {
        await kiboFetch(`${API_BASE}/clients/${clientId}/discover/${mode}`, {
          method: 'POST'
        });
      }
    } catch (err) {
      console.error("Failed to POST trigger discovery mode", err);
    }

    setIsDiscovering(true);
    setDiscoveryLog([]);
    setDiscoveryProgress(0);
    setDiscoveryAgent('');

    const url = `${API_BASE}/clients/${clientId}/discover/${mode}?x_kibo_scope=${securityMode}`;
    
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.progress !== undefined) {
        setDiscoveryProgress(data.progress * 100);
      }
      if (data.agent) {
        setDiscoveryAgent(data.agent);
      }
      if (data.log) {
        setDiscoveryLog(prev => [...prev, `[${data.agent || 'SYSTEM'}] ${data.log}`]);
      }
      if (data.status === 'completed') {
        es.close();
        setIsDiscovering(false);
        fetchClientDetails(clientId);
        fetchData();
      }
    };

    es.onerror = (err) => {
      console.error("EventSource error", err);
      es.close();
      setIsDiscovering(false);
    };
  };

  const handleFindingDecision = async (findingId, decision, customData = null) => {
    try {
      const payload = { decision };
      if (customData) {
        payload.title = customData.title;
        payload.description = customData.description;
      }

      const response = await kiboFetch(`${API_BASE}/clients/${selectedClientId}/findings/${findingId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        fetchClientDetails(selectedClientId);
        setIsModifyingFinding(false);
      }
    } catch (err) {
      console.error("Failed to submit finding decision", err);
    }
  };

  // --- Public View Handlers ---
  const handlePublicSearch = (e) => {
    e.preventDefault();
    if (!publicQuery) return;
    setPublicAnswer("Loading privacy registry...");
    setTimeout(() => {
      setPublicAnswer(`Based on the KIBO Corporate Privacy Registry: We do NOT sell or share your personal information. Our retention schedule mandates deletion of inactive accounts after 180 days. You have the right to request access, correction, or deletion at any time using the form below.`);
    }, 800);
  };

  const handlePublicDsarSubmit = async (e) => {
    e.preventDefault();
    if (!publicDsarName || !publicDsarEmail) return;

    setPublicDsarStatus("submitting");

    try {
      // Public scope allowed
      const response = await kiboFetch(`${API_BASE}/transactions/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: `public-dsar-${Date.now().toString().slice(-6)}`,
          type: "DSAR",
          client: "Public Intake System",
          jurisdiction: "US-State Laws",
          priority: "high",
          deadline: "45 days",
          description: `Consumer DSAR: Request for ${publicDsarType}. Submitted by ${publicDsarName} (${publicDsarEmail}).`,
          agent: "US DSAR Rights Agent",
          summary: `Web intake portal request. Details: ${publicDsarDescription || 'No additional details provided.'}`,
          raw: JSON.stringify({ name: publicDsarName, email: publicDsarEmail, type: publicDsarType, comments: publicDsarDescription })
        })
      });

      if (response.ok) {
        setPublicDsarStatus("success");
        setPublicDsarName('');
        setPublicDsarEmail('');
        setPublicDsarDescription('');
        fetchData();
      } else {
        setPublicDsarStatus("error");
      }
    } catch (err) {
      setPublicDsarStatus("error");
    }
  };

  // --- Employee View Handlers ---
  const handleEmployeeSearch = (e) => {
    e.preventDefault();
    if (!employeeSearchQuery) return;
    setEmployeePolicyResult("Loading policies...");
    setTimeout(() => {
      setEmployeePolicyResult(`POLICY-402 (Biometric Data Controls): Biometric identifiers must be cryptographically hashed before transmission. Standard consent notice BIPA-101 must be signed by the employee/customer prior to enrollment. Maximum retention is 1 year from last interaction.`);
    }, 600);
  };

  const handleEmployeeIncidentSubmit = async (e) => {
    e.preventDefault();
    if (!incidentTitle) return;
    setIncidentStatus("submitting");

    try {
      // Employee scope allowed
      const response = await kiboFetch(`${API_BASE}/transactions/new`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: `inc-${Date.now().toString().slice(-6)}`,
          type: "Breach",
          client: "Employee Reporting Portal",
          jurisdiction: "US-Finance",
          priority: "critical",
          deadline: "72 hours",
          description: `Incident Report: ${incidentTitle}`,
          agent: "Employee Reporting Agent",
          summary: `Internal employee flagged potential issue: ${incidentDesc}`,
          raw: JSON.stringify({ reporter: "Employee UI Profile", issue: incidentTitle, notes: incidentDesc })
        })
      });

      if (response.ok) {
        setIncidentStatus("success");
        setIncidentTitle('');
        setIncidentDesc('');
        fetchData();
      } else {
        setIncidentStatus("error");
      }
    } catch (err) {
      setIncidentStatus("error");
    }
  };

  const selectedTx = transactions.find(t => t.id === selectedId);

  // Helper to render sectoral questionnaires (from the original spec)
  const renderSectoralQuestionnaire = (tx) => {
    const isPending = tx.status === 'pending';
    const jurisdiction = tx.jurisdiction;

    if (jurisdiction === 'US-Health') {
      return (
        <div className="border border-amber-500/20 p-3 bg-slate-900/50 font-mono text-xs space-y-3 rounded">
          <p className="font-bold border-b border-amber-500/20 pb-1 uppercase tracking-wider text-amber-400">// HIPAA / HITECH Compliance Mandates</p>
          <div className="space-y-2">
            <label className="flex items-start space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_safe_harbor`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_safe_harbor`]: e.target.checked })}
                className="mt-0.5 border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Verify removal of 18 specific identifiers (Safe Harbor Rule).</span>
            </label>
            <div className="space-y-1">
              <span className="block text-[10px] text-slate-500">Expert Determination Statistical Certification:</span>
              <input 
                type="text"
                disabled={!isPending}
                value={sectoralInputs[`${tx.id}_expert_det`] || ''}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_expert_det`]: e.target.value })}
                placeholder="Upload path or paste statistical validation credentials..."
                className="w-full text-xs p-1 border border-slate-800 bg-slate-950 text-slate-100 rounded focus:outline-none focus:border-amber-500"
              />
            </div>
            <label className="flex items-start space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_baa`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_baa`]: e.target.checked })}
                className="mt-0.5 border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Confirm active Business Associate Agreements (BAAs) are signed.</span>
            </label>
          </div>
        </div>
      );
    }

    if (jurisdiction === 'US-State Laws') {
      return (
        <div className="border border-amber-500/20 p-3 bg-slate-900/50 font-mono text-xs space-y-3 rounded">
          <p className="font-bold border-b border-amber-500/20 pb-1 uppercase tracking-wider text-amber-400">// State Privacy Laws (CPRA / VCDPA / CPA)</p>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_profiling`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_profiling`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Profiling audit review completed.</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_admt`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_admt`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">ADMT transparency & opt-out metrics validated.</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_cybersecurity`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_cybersecurity`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Cybersecurity high-risk audit records archived.</span>
            </label>
          </div>
        </div>
      );
    }

    if (jurisdiction === 'US-Specialized') {
      return (
        <div className="border border-amber-500/20 p-3 bg-slate-900/50 font-mono text-xs space-y-3 rounded">
          <p className="font-bold border-b border-amber-500/20 pb-1 uppercase tracking-wider text-amber-400">// Specialized Regulatory (COPPA / BIPA)</p>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_coppa`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_coppa`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Verifiable Parental Consent (VPC) obtained for age &lt; 13.</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_bipa`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_bipa`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Biometric consent forms & statutory destruction schedule logged.</span>
            </label>
          </div>
        </div>
      );
    }

    if (jurisdiction === 'US-Finance') {
      return (
        <div className="border border-amber-500/20 p-3 bg-slate-900/50 font-mono text-xs space-y-3 rounded">
          <p className="font-bold border-b border-amber-500/20 pb-1 uppercase tracking-wider text-amber-400">// Financial Regulatory (GLBA / FCRA)</p>
          <div className="space-y-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_glba_notice`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_glba_notice`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Validate active Privacy Notice delivery pathways.</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_safeguards`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_safeguards`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Verify FTC Safeguards rule continuous auditing files.</span>
            </label>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input 
                type="checkbox" 
                disabled={!isPending}
                checked={sectoralInputs[`${tx.id}_fcra`] || false}
                onChange={(e) => setSectoralInputs({ ...sectoralInputs, [`${tx.id}_fcra`]: e.target.checked })}
                className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded" 
              />
              <span className="text-slate-300">Verify FCRA permitted purpose verification records.</span>
            </label>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="w-full h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-slate-100 font-sans flex flex-col overflow-hidden select-none">
      
      {/* --- TOP HEADER: SECURITY SCOPE SWITCHER & BRANDING --- */}
      <header className="w-full border-b border-slate-800 px-6 py-3.5 bg-slate-950 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-amber-500 text-slate-950 p-1.5 rounded font-black tracking-tighter text-sm flex items-center space-x-1 shadow-lg shadow-amber-500/10">
            <Shield size={16} />
            <span>KIBO.IS</span>
          </div>
        </div>
      </header>


      {/* Gateway Status Indicators */}
      {!isSystemOnline && (
        <div className="w-full border-b border-red-500/30 p-2 bg-red-950/40 text-red-400 font-mono text-[11px] uppercase flex justify-between items-center px-6">
          <div className="flex items-center space-x-2 font-bold tracking-wider">
            <AlertOctagon size={14} className="animate-pulse" />
            <span>[!] GATEWAY OFFLINE: PIPELINE SUSPENDED</span>
          </div>
          <span className="text-[9px] text-red-500/80">Offline queue buffered. Actions will serialize when restored.</span>
        </div>
      )}

      {isDbLocked && (
        <div className="w-full bg-slate-900 border-b border-slate-800 py-1.5 px-6 font-mono text-[10px] flex items-center justify-between text-amber-500">
          <div className="flex items-center space-x-2">
            <RefreshCw size={11} className="animate-spin" />
            <span>Serializing local actions queue... (Retrying with exponential backoff)</span>
          </div>
          <span>Attempt #{syncAttempts}</span>
        </div>
      )}
      {/* --- MAIN INTERFACE PANELS BASED ON SECURITY MODE --- */}
      <div className="flex-1 flex overflow-hidden">
        {((currentPath === '/risks' || currentPath === '/risk-register') && securityMode === 'expert') ? (
          <div className="flex-1 flex overflow-hidden bg-slate-950 text-slate-200">
            {/* Left Column: Filterable/Sortable Risk Register Table (65%) */}
            <div className="w-[65%] h-full border-r border-slate-800 flex flex-col p-6 space-y-4 overflow-y-auto select-text">
              <div className="flex justify-between items-center border-b border-slate-850 pb-3">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">// 1.0 CPO Privacy Risk Register</h2>
                  <p className="text-[10px] text-slate-500 font-mono">Full authority oversight & mapping dashboard</p>
                </div>
                <button
                  onClick={handleNewRisk}
                  className="bg-amber-500 text-slate-950 font-mono text-[10px] font-bold px-3 py-1.5 uppercase rounded hover:bg-amber-400"
                >
                  + Add Risk
                </button>
              </div>

              {/* Filters Bar */}
              <div className="flex flex-wrap gap-2 items-center bg-slate-900/30 p-3 border border-slate-850 rounded font-mono text-[10px]">
                <div className="flex flex-col space-y-1">
                  <span className="text-slate-500 uppercase text-[8px]">Level</span>
                  <select
                    value={riskFilterLevel}
                    onChange={(e) => setRiskFilterLevel(e.target.value)}
                    className="bg-slate-950 border border-slate-800 p-1 text-slate-300 rounded"
                  >
                    <option value="ALL">All Levels</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>

                <div className="flex flex-col space-y-1">
                  <span className="text-slate-500 uppercase text-[8px]">Assigned To</span>
                  <select
                    value={riskFilterAssignee}
                    onChange={(e) => setRiskFilterAssignee(e.target.value)}
                    className="bg-slate-950 border border-slate-800 p-1 text-slate-300 rounded"
                  >
                    <option value="ALL">All Assignees</option>
                    {Array.from(new Set(risks.map(r => r.assigned_to).filter(Boolean))).map(name => (
                      <option key={name} value={name}>{name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex flex-col space-y-1">
                  <span className="text-slate-500 uppercase text-[8px]">Gap Type</span>
                  <select
                    value={riskFilterGap}
                    onChange={(e) => setRiskFilterGap(e.target.value)}
                    className="bg-slate-950 border border-slate-800 p-1 text-slate-300 rounded"
                  >
                    <option value="ALL">All Gaps</option>
                    <option value="Operational Gap">Operational Gap</option>
                    <option value="Governance Gap">Governance Gap</option>
                    <option value="Design Gap">Design Gap</option>
                    <option value="Security">Security</option>
                    <option value="Compliance">Compliance</option>
                    <option value="Transparency">Transparency</option>
                    <option value="Training">Training</option>
                  </select>
                </div>

                <label className="flex items-center space-x-1.5 mt-4 cursor-pointer text-slate-300 select-none">
                  <input
                    type="checkbox"
                    checked={riskFilterOverdue}
                    onChange={(e) => setRiskFilterOverdue(e.target.checked)}
                    className="border border-slate-800 bg-slate-950 checked:bg-amber-500 rounded w-3 h-3"
                  />
                  <span>Overdue Only</span>
                </label>
              </div>

              {/* Risks Table */}
              <div className="flex-1 overflow-x-auto border border-slate-850 rounded bg-slate-950">
                <table className="w-full text-left font-mono text-[10px] divide-y divide-slate-850">
                  <thead className="bg-slate-900/60 sticky top-0 text-slate-400 uppercase text-[9px]">
                    <tr>
                      {['risk_id', 'risk_level', 'issue', 'assigned_to', 'next_review_date', 'gap_type', 'risk_score', 'status', 'source_document'].map(col => {
                        const isSorted = riskSortCol === col;
                        return (
                          <th
                            key={col}
                            onClick={() => {
                              if (riskSortCol === col) {
                                setRiskSortDir(riskSortDir === 'asc' ? 'desc' : 'asc');
                              } else {
                                setRiskSortCol(col);
                                setRiskSortDir('asc');
                              }
                            }}
                            className="p-3 cursor-pointer hover:bg-slate-800/50 hover:text-slate-200 select-none font-bold"
                          >
                            <span className="flex items-center space-x-1">
                              <span>{col.replace(/_/g, ' ')}</span>
                              {isSorted && (riskSortDir === 'asc' ? <ChevronUp size={10} /> : <ChevronDown size={10} />)}
                            </span>
                          </th>
                        );
                      })}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-850 text-slate-300">
                    {(() => {
                      let filtered = [...risks];
                      if (riskFilterLevel !== 'ALL') {
                        if (riskFilterLevel === 'closed') {
                          filtered = filtered.filter(r => r.status === 'closed');
                        } else {
                          filtered = filtered.filter(r => r.risk_level === riskFilterLevel && r.status !== 'closed');
                        }
                      }
                      if (riskFilterAssignee !== 'ALL') {
                        filtered = filtered.filter(r => r.assigned_to === riskFilterAssignee);
                      }
                      if (riskFilterGap !== 'ALL') {
                        filtered = filtered.filter(r => r.gap_type === riskFilterGap);
                      }
                      if (riskFilterOverdue) {
                        filtered = filtered.filter(r => r.status !== 'closed' && new Date(r.next_review_date) < new Date());
                      }

                      filtered.sort((a, b) => {
                        let valA = a[riskSortCol];
                        let valB = b[riskSortCol];
                        if (riskSortCol === 'risk_score') {
                          valA = Number(valA) || 0;
                          valB = Number(valB) || 0;
                        } else {
                          valA = String(valA || '').toLowerCase();
                          valB = String(valB || '').toLowerCase();
                        }
                        if (valA < valB) return riskSortDir === 'asc' ? -1 : 1;
                        if (valA > valB) return riskSortDir === 'asc' ? 1 : -1;
                        return 0;
                      });

                      if (filtered.length === 0) {
                        return (
                          <tr>
                            <td colSpan={9} className="p-10 text-center text-slate-500 italic">
                              // NO MATCHING COMPLIANCE RISKS FOUND
                            </td>
                          </tr>
                        );
                      }

                      return filtered.map(risk => {
                        const isSelected = selectedRisk && selectedRisk.risk_id === risk.risk_id;
                        const isClosed = risk.status === 'closed';
                        const reviewDate = new Date(risk.next_review_date);
                        const isOverdue = !isClosed && reviewDate < new Date();
                        const isAmber = !isClosed && !isOverdue && reviewDate <= new Date(Date.now() + 14 * 24 * 60 * 60 * 1000);

                        return (
                          <tr
                            key={risk.risk_id}
                            onClick={() => handleSelectRisk(risk)}
                            className={`cursor-pointer transition-colors ${
                              isSelected ? 'bg-slate-900 text-amber-500 font-bold' : 'hover:bg-slate-900/40'
                            }`}
                          >
                            <td className="p-3 font-bold">{risk.risk_id}</td>
                            <td className="p-3">
                              <span className={`px-1.5 py-0.5 rounded text-[8px] uppercase font-bold text-slate-950 ${
                                isClosed ? 'bg-slate-600' :
                                risk.risk_level === 'High' ? 'bg-red-600' :
                                risk.risk_level === 'Medium' ? 'bg-amber-600' : 'bg-green-600'
                              }`}>
                                {isClosed ? 'Closed' : risk.risk_level}
                              </span>
                            </td>
                            <td className="p-3 max-w-[200px] truncate leading-relaxed whitespace-pre-wrap">{risk.issue}</td>
                            <td className="p-3">{risk.assigned_to || 'Unassigned'}</td>
                            <td className={`p-3 font-semibold ${
                              isOverdue ? 'text-red-500' : isAmber ? 'text-amber-500' : 'text-slate-400'
                            }`}>
                              {risk.next_review_date}
                              {isOverdue && ' (Overdue)'}
                            </td>
                            <td className="p-3 text-slate-400">{risk.gap_type}</td>
                            <td className="p-3 font-bold text-center">{risk.risk_score}</td>
                            <td className="p-3 uppercase font-bold text-[9px]">{risk.status}</td>
                            <td className="p-3 text-slate-500">{risk.source_document || 'N/A'}</td>
                          </tr>
                        );
                      });
                    })()}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right Column: Risk Detail/Edit Panel (35%) */}
            <div className="w-[35%] h-full flex flex-col p-6 space-y-4 bg-slate-900/10 border-l border-slate-800 overflow-y-auto select-text">
              <div className="border-b border-slate-850 pb-2 flex justify-between items-center">
                <h3 className="text-xs font-bold uppercase tracking-wider text-amber-500">// Detail & Mitigation Form</h3>
                {riskEditStatus && <span className="text-[10px] text-emerald-400 font-mono animate-fade-in">{riskEditStatus}</span>}
              </div>

              {riskForm ? (
                <form onSubmit={handleSaveRisk} className="space-y-4 font-mono text-[10px] leading-relaxed">
                  
                  {/* Identity */}
                  <div className="space-y-3 bg-slate-950 p-3 border border-slate-850 rounded">
                    <div className="text-[9px] font-bold uppercase text-slate-500 border-b border-slate-900 pb-1">// Identity Mapping</div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-slate-500 uppercase text-[8px] mb-1">Risk ID</label>
                        <input
                          type="text"
                          readOnly
                          value={riskForm.risk_id}
                          className="w-full bg-slate-900 border border-slate-800 p-1.5 text-slate-400 rounded focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-500 uppercase text-[8px] mb-1">Law 25 Section</label>
                        <input
                          type="text"
                          value={riskForm.law_25_section || ''}
                          onChange={(e) => setRiskForm({ ...riskForm, law_25_section: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-slate-500 uppercase text-[8px] mb-1">Gap Type</label>
                        <select
                          value={riskForm.gap_type || 'Operational Gap'}
                          onChange={(e) => setRiskForm({ ...riskForm, gap_type: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                        >
                          <option value="Operational Gap">Operational Gap</option>
                          <option value="Governance Gap">Governance Gap</option>
                          <option value="Design Gap">Design Gap</option>
                          <option value="Security">Security</option>
                          <option value="Compliance">Compliance</option>
                          <option value="Transparency">Transparency</option>
                          <option value="Training">Training</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-slate-500 uppercase text-[8px] mb-1">Original Risk Level</label>
                        <select
                          value={riskForm.original_risk_level || 'Medium'}
                          onChange={(e) => setRiskForm({ ...riskForm, original_risk_level: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none"
                        >
                          <option value="High">High</option>
                          <option value="Medium">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-slate-500 uppercase text-[8px] mb-1">Source Document</label>
                      <input
                        type="text"
                        value={riskForm.source_document || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, source_document: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-500 uppercase text-[8px] mb-1">Source ID</label>
                      <input
                        type="text"
                        value={riskForm.source_id || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, source_id: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                      />
                    </div>
                  </div>

                  {/* Assessment */}
                  <div className="space-y-3 bg-slate-950 p-3 border border-slate-850 rounded">
                    <div className="text-[9px] font-bold uppercase text-slate-500 border-b border-slate-900 pb-1">// Risk Assessment Sliders</div>
                    
                    <div>
                      <label className="block text-slate-400 uppercase text-[8px] mb-1">Issue Description</label>
                      <textarea
                        rows={2}
                        required
                        value={riskForm.issue}
                        onChange={(e) => setRiskForm({ ...riskForm, issue: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 resize-none"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-[9px]">
                        <span className="text-slate-400 uppercase">Likelihood:</span>
                        <span className="font-bold text-amber-500">
                          {riskForm.likelihood} - {['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain'][riskForm.likelihood - 1]}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={riskForm.likelihood}
                        onChange={(e) => setRiskForm({ ...riskForm, likelihood: parseInt(e.target.value, 10) })}
                        className="w-full h-1 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-amber-500"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-[9px]">
                        <span className="text-slate-400 uppercase">Impact:</span>
                        <span className="font-bold text-amber-500">
                          {riskForm.impact} - {['Negligible', 'Minor', 'Moderate', 'Major', 'Catastrophic'][riskForm.impact - 1]}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={riskForm.impact}
                        onChange={(e) => setRiskForm({ ...riskForm, impact: parseInt(e.target.value, 10) })}
                        className="w-full h-1 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-amber-500"
                      />
                    </div>

                    <div className="flex justify-between items-center border-t border-slate-900 pt-2 text-slate-200">
                      <div className="flex flex-col">
                        <span className="text-slate-500 text-[8px] uppercase">Auto Calculated Risk Score</span>
                        <span className="text-xl font-bold font-mono text-amber-500">
                          {riskForm.likelihood * riskForm.impact}
                        </span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-slate-500 text-[8px] uppercase">Risk Level</span>
                        <span className={`px-2 py-0.5 rounded text-[9px] uppercase font-bold text-slate-950 ${
                          riskForm.status === 'closed' ? 'bg-slate-600' :
                          (riskForm.likelihood * riskForm.impact) >= 15 ? 'bg-red-600' :
                          (riskForm.likelihood * riskForm.impact) >= 8 ? 'bg-amber-600' : 'bg-green-600'
                        }`}>
                          {riskForm.status === 'closed' ? 'Closed' : get_risk_level_from_score(riskForm.likelihood * riskForm.impact)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Response */}
                  <div className="space-y-3 bg-slate-950 p-3 border border-slate-850 rounded">
                    <div className="text-[9px] font-bold uppercase text-slate-500 border-b border-slate-900 pb-1">// Response & Remediation</div>
                    <div>
                      <label className="block text-slate-500 uppercase text-[8px] mb-1">CPO Recommendation</label>
                      <textarea
                        rows={2}
                        value={riskForm.recommendation || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, recommendation: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 resize-none font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-500 uppercase text-[8px] mb-1">KHP Response</label>
                      <textarea
                        rows={2}
                        value={riskForm.khp_response || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, khp_response: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 resize-none font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 uppercase text-[8px] mb-1">Status / PSR Note</label>
                      <textarea
                        rows={2}
                        value={riskForm.status_note || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, status_note: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 resize-none font-mono"
                      />
                    </div>
                  </div>

                  {/* Assignment & Schedule */}
                  <div className="space-y-3 bg-slate-950 p-3 border border-slate-850 rounded">
                    <div className="text-[9px] font-bold uppercase text-slate-500 border-b border-slate-900 pb-1">// Assignment & Review Schedule</div>
                    <div>
                      <label className="block text-slate-400 uppercase text-[8px] mb-1">Assigned To</label>
                      <input
                        type="text"
                        value={riskForm.assigned_to || ''}
                        onChange={(e) => setRiskForm({ ...riskForm, assigned_to: e.target.value })}
                        className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-slate-500 uppercase text-[8px] mb-1">Assigned Date</label>
                        <input
                          type="date"
                          value={riskForm.risk_assigned_date || ''}
                          onChange={(e) => setRiskForm({ ...riskForm, risk_assigned_date: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-400 uppercase text-[8px] mb-1">Next Review Date</label>
                        <input
                          type="date"
                          required
                          value={riskForm.next_review_date || ''}
                          onChange={(e) => setRiskForm({ ...riskForm, next_review_date: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-1.5 text-slate-200 rounded focus:outline-none"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Actions Panel */}
                  <div className="flex flex-col space-y-2">
                    <button
                      type="submit"
                      className="w-full bg-blue-600 text-slate-100 font-bold p-2 uppercase rounded hover:bg-blue-500 transition-colors"
                    >
                      Save Changes
                    </button>
                    {riskForm.risk_id !== 'AUTO-GENERATED' && riskForm.status !== 'closed' && (
                      <button
                        type="button"
                        onClick={() => handleCloseRisk(riskForm.risk_id)}
                        className="w-full bg-slate-700 text-slate-200 font-bold p-2 uppercase rounded hover:bg-slate-600 transition-colors"
                      >
                        Close Risk
                      </button>
                    )}
                    {riskForm.risk_id !== 'AUTO-GENERATED' && (
                      <button
                        type="button"
                        onClick={() => handleDeleteRisk(riskForm.risk_id)}
                        className="w-full bg-red-950/40 text-red-400 border border-red-500/20 font-bold p-2 uppercase rounded hover:bg-red-500 hover:text-slate-950 transition-colors"
                      >
                        Delete Risk
                      </button>
                    )}
                  </div>

                  {/* Audit Trail */}
                  {riskAuditLog.length > 0 && (
                    <div className="space-y-2 bg-slate-950 p-3 border border-slate-850 rounded">
                      <div className="text-[9px] font-bold uppercase text-slate-500 border-b border-slate-900 pb-1">// Audit Trail (Last 5 Changes)</div>
                      <div className="space-y-2 divide-y divide-slate-900">
                        {riskAuditLog.slice(0, 5).map(log => (
                          <div key={log.log_id} className="pt-2 text-[9px] font-mono space-y-0.5">
                            <div className="flex justify-between text-slate-500">
                              <span>[{log.actor}] {log.action}</span>
                              <span>{log.timestamp.slice(11, 19)}</span>
                            </div>
                            {log.field_changed && (
                              <div className="text-slate-400">
                                Field <code className="text-amber-500">{log.field_changed}</code> changed: {log.old_value || 'None'} → {log.new_value}
                              </div>
                            )}
                            {log.note && <p className="text-slate-400 italic text-[8px]">"{log.note}"</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </form>
              ) : (
                <div className="flex-1 flex items-center justify-center text-slate-500 italic font-mono text-center">
                  Select a compliance risk to review details or click '+ Add Risk' to register a new vector.
                </div>
              )}
            </div>
          </div>
        ) : (currentPath === '/my-risks' || currentPath === '/risks/me') ? (
          <div className="flex-1 overflow-y-auto bg-slate-950 p-6 space-y-6 text-slate-200 select-text">
            {/* View 2: Employee Risk View */}
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="border-b border-slate-850 pb-4">
                <h1 className="text-sm font-bold uppercase tracking-wider text-amber-500">// My Risk Assignments</h1>
                <div className="flex justify-between items-center mt-2 font-mono text-xs text-slate-400">
                  <span>Showing risks assigned to: <strong className="text-slate-200">{currentUser}</strong></span>
                  <div className="flex space-x-3 text-[10px]">
                    <span className="bg-slate-900 px-2 py-0.5 border border-slate-800 rounded">
                      {risks.filter(r => r.status !== 'closed').length} open
                    </span>
                    <span className="bg-red-950/40 text-red-400 px-2 py-0.5 border border-red-900/30 rounded">
                      {risks.filter(r => r.status !== 'closed' && new Date(r.next_review_date) < new Date()).length} overdue
                    </span>
                    <span className="bg-amber-950/40 text-amber-400 px-2 py-0.5 border border-amber-900/30 rounded">
                      {risks.filter(r => r.status !== 'closed' && new Date(r.next_review_date) >= new Date() && new Date(r.next_review_date) <= new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)).length} due in 14d
                    </span>
                  </div>
                </div>
              </div>

              {(() => {
                const openRisks = [...risks].filter(r => r.status !== 'closed');
                
                // Sorting: Overdue first -> High risk -> Medium -> Low -> review date ascending
                openRisks.sort((a, b) => {
                  const now = Date.now();
                  const dateA = new Date(a.next_review_date).getTime();
                  const dateB = new Date(b.next_review_date).getTime();
                  const isOverdueA = dateA < now;
                  const isOverdueB = dateB < now;

                  if (isOverdueA && !isOverdueB) return -1;
                  if (!isOverdueA && isOverdueB) return 1;

                  const priorityMap = { 'High': 3, 'Medium': 2, 'Low': 1 };
                  const prioA = priorityMap[a.risk_level] || 0;
                  const prioB = priorityMap[b.risk_level] || 0;
                  if (prioA !== prioB) return prioB - prioA;

                  return dateA - dateB;
                });

                if (openRisks.length === 0) {
                  return (
                    <div className="border border-dashed border-slate-850 p-12 text-center text-slate-500 font-mono">
                      ✅ No open risks assigned to you.
                    </div>
                  );
                }

                return (
                  <div className="space-y-4">
                    {openRisks.map(risk => {
                      const isExpanded = expandedRiskId === risk.risk_id;
                      const reviewTime = new Date(risk.next_review_date).getTime();
                      const isOverdue = reviewTime < Date.now();
                      const daysRemaining = Math.ceil((reviewTime - Date.now()) / (24 * 60 * 60 * 1000));
                      const isAmber = !isOverdue && daysRemaining <= 14;

                      // Card color border class
                      const borderClass = risk.risk_level === 'High' ? 'border-l-4 border-l-red-600' :
                                          risk.risk_level === 'Medium' ? 'border-l-4 border-l-amber-600' :
                                          'border-l-4 border-l-green-600';

                      // Determine background color and text color overrides for card based on urgency
                      let cardStyle = {};
                      let textClass = "text-slate-300 font-mono";
                      let headerTextClass = "text-slate-200 font-mono";
                      let metadataTextClass = "text-slate-500 font-mono";
                      let detailBtnClass = "bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-850";

                      if (isOverdue) {
                        cardStyle = { backgroundColor: '#fee2e2' };
                        textClass = "text-[#7f1d1d] font-mono font-medium";
                        headerTextClass = "text-[#7f1d1d] font-mono font-bold";
                        metadataTextClass = "text-[#7f1d1d]/75 font-mono";
                        detailBtnClass = "bg-[#7f1d1d]/15 border border-[#7f1d1d]/30 text-[#7f1d1d] hover:bg-[#7f1d1d]/25";
                      } else if (isAmber) {
                        cardStyle = { backgroundColor: '#fef3c7' };
                        textClass = "text-[#78350f] font-mono font-medium";
                        headerTextClass = "text-[#78350f] font-mono font-bold";
                        metadataTextClass = "text-[#78350f]/75 font-mono";
                        detailBtnClass = "bg-[#78350f]/15 border border-[#78350f]/30 text-[#78350f] hover:bg-[#78350f]/25";
                      }

                      return (
                        <div
                          key={risk.risk_id}
                          style={cardStyle}
                          className={`p-5 border border-slate-850 rounded font-mono text-[11px] leading-relaxed transition-all duration-200 flex flex-col space-y-4 shadow-sm bg-slate-950 ${borderClass}`}
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex items-center space-x-2">
                              <span className={`px-1.5 py-0.5 rounded text-[9px] font-black uppercase text-slate-950 ${
                                risk.risk_level === 'High' ? 'bg-red-600' :
                                risk.risk_level === 'Medium' ? 'bg-amber-600' : 'bg-green-600'
                              }`}>
                                {risk.risk_level}
                              </span>
                              <span className={`font-bold ${headerTextClass}`}>{risk.risk_id}</span>
                            </div>
                            <div className="text-right">
                              <div className={`font-bold ${headerTextClass}`}>Due: {risk.next_review_date}</div>
                              {isOverdue ? (
                                <div className="text-red-700 font-extrabold uppercase text-[9px] mt-0.5 animate-pulse">⚠️ OVERDUE</div>
                              ) : isAmber ? (
                                <div className="text-amber-700 font-extrabold uppercase text-[9px] mt-0.5">⚠️ {daysRemaining} days remaining</div>
                              ) : (
                                <div className="text-slate-500 text-[9px] mt-0.5">{daysRemaining} days remaining</div>
                              )}
                            </div>
                          </div>

                          <div className={`text-xs font-bold leading-tight font-sans ${headerTextClass}`}>
                            {risk.issue}
                          </div>

                          <div className="space-y-1">
                            <div className={`font-bold uppercase text-[9px] ${metadataTextClass}`}>What you need to do:</div>
                            <p className={textClass}>{risk.recommendation || 'No specific CPO recommendations provided.'}</p>
                          </div>

                          <div className="space-y-1">
                            <div className={`font-bold uppercase text-[9px] ${metadataTextClass}`}>Current status:</div>
                            <p className={textClass}>{risk.status_note || 'No ongoing status update logged.'}</p>
                          </div>

                          <div className={`flex flex-wrap gap-x-4 gap-y-1 text-[9px] border-t border-slate-800/20 pt-2 ${metadataTextClass}`}>
                            <div>Gap Type: <strong className={headerTextClass}>{risk.gap_type}</strong></div>
                            {risk.law_25_section && risk.law_25_section !== 'None' && (
                              <div>Law 25 §{risk.law_25_section}</div>
                            )}
                          </div>

                          {/* Card Actions */}
                          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/10">
                            <button
                              onClick={() => handleAcknowledgeRisk(risk.risk_id)}
                              className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold px-3 py-1.5 uppercase rounded text-[10px] tracking-wide"
                            >
                              [ Mark as Updated ]
                            </button>
                            <button
                              onClick={() => setShowExtensionId(showExtensionId === risk.risk_id ? null : risk.risk_id)}
                              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-3 py-1.5 uppercase rounded text-[10px] tracking-wide"
                            >
                              [ Request Extension ]
                            </button>
                            <button
                              onClick={() => {
                                if (isExpanded) setExpandedRiskId(null);
                                else {
                                  setExpandedRiskId(risk.risk_id);
                                  fetchRiskLog(risk.risk_id);
                                }
                              }}
                              className={`px-3 py-1.5 uppercase rounded text-[10px] font-bold ${detailBtnClass}`}
                            >
                              {isExpanded ? 'Hide Details' : 'View Details'}
                            </button>
                          </div>

                          {/* Extension request form inline overlay */}
                          {showExtensionId === risk.risk_id && (
                            <div className="bg-slate-900 border border-slate-850 p-4 rounded space-y-3 mt-2 text-slate-200">
                              <div className="text-[10px] font-bold uppercase text-amber-500">// Request Deadline Extension</div>
                              <div className="grid grid-cols-1 gap-2">
                                <div>
                                  <label className="block text-[8px] text-slate-500 uppercase mb-1">Suggested Review Date</label>
                                  <input
                                    type="date"
                                    value={extensionSuggestedDate}
                                    onChange={(e) => setExtensionSuggestedDate(e.target.value)}
                                    className="bg-slate-950 border border-slate-800 p-1 text-xs text-slate-200 rounded w-full"
                                  />
                                </div>
                                <div>
                                  <label className="block text-[8px] text-slate-500 uppercase mb-1">Reason for Extension</label>
                                  <textarea
                                    rows={2}
                                    value={extensionRequestText}
                                    onChange={(e) => setExtensionRequestText(e.target.value)}
                                    placeholder="Explain why deadline variance is required..."
                                    className="bg-slate-950 border border-slate-800 p-2 text-xs text-slate-200 rounded w-full resize-none font-mono"
                                  />
                                </div>
                              </div>
                              <div className="flex space-x-2 justify-end">
                                <button
                                  type="button"
                                  onClick={() => handleRequestExtension(risk.risk_id)}
                                  className="bg-blue-600 text-slate-100 font-bold px-3 py-1 uppercase rounded text-[9px]"
                                >
                                  Submit Request
                                </button>
                                <button
                                  type="button"
                                  onClick={() => setShowExtensionId(null)}
                                  className="bg-slate-800 text-slate-400 font-bold px-3 py-1 uppercase rounded text-[9px]"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          )}

                          {/* Expanded Details Panel */}
                          {isExpanded && (
                            <div className="bg-slate-900/40 p-4 rounded border border-slate-850 mt-2 space-y-3">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <div className={`font-bold uppercase text-[8px] ${metadataTextClass}`}>Source Document</div>
                                  <p className={textClass}>{risk.source_document || 'N/A'}</p>
                                </div>
                                <div>
                                  <div className={`font-bold uppercase text-[8px] ${metadataTextClass}`}>Risk Score (Likelihood × Impact)</div>
                                  <p className={textClass}>{risk.likelihood} × {risk.impact} = <strong>{risk.risk_score}</strong></p>
                                </div>
                              </div>
                              
                              <div>
                                <div className={`font-bold uppercase text-[8px] ${metadataTextClass}`}>KHP Response</div>
                                <p className={textClass}>{risk.khp_response || 'No organizational response logged.'}</p>
                              </div>

                              {/* Log History */}
                              {riskAuditLog.length > 0 && (
                                <div className="space-y-2 pt-2 border-t border-slate-800/10">
                                  <div className={`font-bold uppercase text-[8px] ${metadataTextClass}`}>Change Log History</div>
                                  <div className="space-y-1.5 max-h-[100px] overflow-y-auto pr-1">
                                    {riskAuditLog.map(log => (
                                      <div key={log.log_id} className={`text-[8px] font-mono leading-snug flex justify-between ${textClass}`}>
                                        <span>[{log.actor}] {log.action} {log.note ? `- "${log.note}"` : ''}</span>
                                        <span className={metadataTextClass}>{log.timestamp.slice(0, 10)}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}

                        </div>
                      );
                    })}
                  </div>
                );
              })()}

            </div>
          </div>
        ) : (
          <>
            {securityMode === 'public' && (
              <div className="flex-1 flex flex-col md:flex-row overflow-hidden bg-slate-950">
            {/* Left Column: Public Q&A Search */}
            <div className="w-full md:w-1/2 p-8 border-r border-slate-800 flex flex-col space-y-6 overflow-y-auto">
              <div className="space-y-2">
                <div className="text-amber-500 font-mono text-xs uppercase tracking-widest">// 1.1 Privacy Registry Knowledge Lookup</div>
                <h2 className="text-xl font-bold">Public Privacy Information Registry</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Query the official KIBO corporate privacy registry regarding data collection practices, user rights, and global compliance regulations.
                </p>
              </div>

              <form onSubmit={handlePublicSearch} className="space-y-3">
                <div className="flex space-x-2">
                  <input 
                    type="text" 
                    value={publicQuery}
                    onChange={(e) => setPublicQuery(e.target.value)}
                    placeholder="Search policy. e.g. Do you sell my data? Or what is your data retention policy?"
                    className="flex-1 bg-slate-900 border border-slate-800 p-3 text-sm text-slate-100 rounded focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                  />
                  <button type="submit" className="bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 px-5 text-sm font-mono rounded flex items-center space-x-1.5">
                    <Search size={16} />
                    <span>Search</span>
                  </button>
                </div>
              </form>

              {publicAnswer && (
                <div className="border border-slate-800 bg-slate-900/50 p-5 rounded font-mono text-xs leading-relaxed space-y-2.5">
                  <div className="text-slate-400 font-bold border-b border-slate-800 pb-1.5 uppercase">// Registry Resolution Response</div>
                  <p className="text-slate-300">{publicAnswer}</p>
                </div>
              )}
            </div>

            {/* Right Column: Inbound DSAR Rights Intake Form */}
            <div className="w-full md:w-1/2 p-8 flex flex-col space-y-6 overflow-y-auto bg-slate-900/20">
              <div className="space-y-2">
                <div className="text-amber-500 font-mono text-xs uppercase tracking-widest">// 1.2 Data Subject Rights Request (DSAR) Intake</div>
                <h2 className="text-xl font-bold">Submit a Privacy Rights Request</h2>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Exercise your rights under CCPA, CPRA, GDPR, or state-specific laws. Your request will be queued in the CPO action interface for review.
                </p>
              </div>

              <form onSubmit={handlePublicDsarSubmit} className="space-y-4 max-w-xl">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="block text-xs font-mono uppercase text-slate-400">Full Name</label>
                    <input 
                      type="text" 
                      required
                      value={publicDsarName}
                      onChange={(e) => setPublicDsarName(e.target.value)}
                      placeholder="e.g. John Doe"
                      className="w-full bg-slate-900 border border-slate-800 p-2.5 text-xs text-slate-100 rounded focus:outline-none focus:border-amber-500"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="block text-xs font-mono uppercase text-slate-400">Email Address</label>
                    <input 
                      type="email" 
                      required
                      value={publicDsarEmail}
                      onChange={(e) => setPublicDsarEmail(e.target.value)}
                      placeholder="e.g. john@example.com"
                      className="w-full bg-slate-900 border border-slate-800 p-2.5 text-xs text-slate-100 rounded focus:outline-none focus:border-amber-500"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-mono uppercase text-slate-400">Request Type</label>
                  <select 
                    value={publicDsarType}
                    onChange={(e) => setPublicDsarType(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 p-2.5 text-xs text-slate-100 rounded focus:outline-none focus:border-amber-500"
                  >
                    <option value="access">Access Personal Data (Right to Know)</option>
                    <option value="deletion">Delete Personal Data (Right to be Forgotten)</option>
                    <option value="opt-out">Opt-out of Automated Profiling & Targeting</option>
                    <option value="correction">Correct Inaccurate Data</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-mono uppercase text-slate-400">Additional Specifications</label>
                  <textarea 
                    value={publicDsarDescription}
                    onChange={(e) => setPublicDsarDescription(e.target.value)}
                    placeholder="Provide specific details about your account, datasets, or the request reasoning..."
                    className="w-full bg-slate-900 border border-slate-800 p-2.5 text-xs text-slate-100 rounded focus:outline-none focus:border-amber-500 h-[100px] resize-none"
                  />
                </div>

                <button 
                  type="submit" 
                  disabled={publicDsarStatus === 'submitting'}
                  className="w-full bg-amber-500 text-slate-950 hover:bg-amber-400 font-bold p-3 text-xs uppercase tracking-wider rounded transition-all duration-200 disabled:bg-slate-800 disabled:text-slate-500"
                >
                  {publicDsarStatus === 'submitting' ? 'Submitting Request...' : 'Submit Rights Request'}
                </button>

                {publicDsarStatus === 'success' && (
                  <div className="border border-emerald-500/20 bg-emerald-950/20 text-emerald-400 p-3.5 text-xs rounded font-mono">
                    ✓ Request successfully submitted. Your privacy tracking thread ID is registered.
                  </div>
                )}
                {publicDsarStatus === 'error' && (
                  <div className="border border-red-500/20 bg-red-950/20 text-red-400 p-3.5 text-xs rounded font-mono">
                    ✕ Submission failed. Gateway rejected the public intake scope.
                  </div>
                )}
              </form>
            </div>
          </div>
        )}

        {/* ======================================================================= */}
        {/* 2.0 INTERNAL EMPLOYEE MODE INTERFACE                                    */}
        {/* ======================================================================= */}
        {securityMode === 'employee' && (
          <div className="flex-1 flex overflow-hidden bg-slate-950">
            {/* Left Column: Project Intake & Mitigation Plans (60%) */}
            <div className="w-[60%] h-full border-r border-slate-800 flex flex-col p-6 space-y-6 overflow-y-auto">
              
              {/* Project Intake Section */}
              <div className="space-y-3">
                <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                  <div>
                    <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">// 2.1 Project Privacy Intake Registry</h2>
                    <p className="text-[10px] text-slate-500 font-mono">Submit and Manage System Data Lifecycles</p>
                  </div>
                  {!isEditingIntake && (
                    <button
                      onClick={() => {
                        setIsEditingIntake(true);
                        setIntakeForm({ id: '', project_name: '', purpose: '', data_classification: [], retention_value: 0, retention_unit: 'days', status: 'draft' });
                      }}
                      className="bg-amber-500 text-slate-950 font-mono text-[10px] font-bold px-3 py-1 uppercase rounded"
                    >
                      + New Project Intake
                    </button>
                  )}
                </div>

                {isEditingIntake ? (
                  <form onSubmit={handlePostIntake} className="bg-slate-900/30 border border-slate-800 p-4 rounded space-y-4 font-mono text-[11px]">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="block text-slate-400 uppercase">Project Name</label>
                        <input
                          type="text"
                          required
                          value={intakeForm.project_name}
                          onChange={(e) => setIntakeForm({ ...intakeForm, project_name: e.target.value })}
                          disabled={intakeForm.status === 'Re-evaluation Required'}
                          className={`w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 ${intakeForm.status === 'Re-evaluation Required' ? 'opacity-50 cursor-not-allowed' : ''}`}

                        />
                      </div>
                      <div className="space-y-1">
                        <label className="block text-slate-400 uppercase">Purpose of Collection</label>
                        <input
                          type="text"
                          required
                          value={intakeForm.purpose}
                          onChange={(e) => setIntakeForm({ ...intakeForm, purpose: e.target.value })}
                          disabled={intakeForm.status === 'Re-evaluation Required'}
                          className={`w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500 ${intakeForm.status === 'Re-evaluation Required' ? 'opacity-50 cursor-not-allowed' : ''}`}

                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="block text-slate-400 uppercase">Data Classification (Select All That Apply)</label>
                      <div className="grid grid-cols-3 gap-2">
                        {["Health", "Financial", "Childrens", "Biometric", "Employee", "Sensitive PII"].map(cls => {
                          const checked = intakeForm.data_classification.includes(cls);
                          return (
                            <label key={cls} className="flex items-center space-x-2 bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setIntakeForm({ ...intakeForm, data_classification: [...intakeForm.data_classification, cls] });
                                  } else {
                                    setIntakeForm({ ...intakeForm, data_classification: intakeForm.data_classification.filter(c => c !== cls) });
                                  }
                                }}
                                className="border border-slate-700 bg-slate-900 checked:bg-amber-500 w-3 h-3 rounded"
                              />
                              <span className="text-slate-300 text-[10px]">{cls}</span>
                            </label>
                          );
                        })}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="block text-slate-400 uppercase">Retention Limit Value</label>
                        <input
                          type="number"
                          required
                          min="0"
                          value={intakeForm.retention_value}
                          onChange={(e) => setIntakeForm({ ...intakeForm, retention_value: parseInt(e.target.value, 10) })}
                          className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="block text-slate-400 uppercase">Retention Unit</label>
                        <select
                          value={intakeForm.retention_unit}
                          onChange={(e) => setIntakeForm({ ...intakeForm, retention_unit: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 p-2 text-slate-200 rounded focus:outline-none focus:border-amber-500"
                        >
                          {["days", "months", "years", "indefinite"].map(unit => (
                            <option key={unit} value={unit}>{unit}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {intakeError && <div className="text-red-400 text-[10px] font-bold">{intakeError}</div>}

                    <div className="flex space-x-2">
                      <button
                        type="submit"
                        className="bg-amber-500 text-slate-950 font-bold px-4 py-2 uppercase rounded hover:bg-amber-400"
                      >
                        {intakeForm.status === 'Re-evaluation Required' ? '[ RESUBMIT FOR PRIVACY AUDIT ]' : '[ SUBMIT RIGHTS REQUEST ]'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsEditingIntake(false)}
                        className="border border-slate-800 bg-slate-950 hover:bg-slate-900 text-slate-300 px-4 py-2 uppercase rounded"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                ) : null}

                {/* Skeletons for Loading Intakes */}
                {isLoadingIntakes ? (
                  <div className="space-y-2">
                    <div className="h-10 border border-slate-800 bg-transparent rounded animate-pulse"></div>
                    <div className="h-10 border border-slate-800 bg-transparent rounded animate-pulse"></div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {employeeIntakes.map(item => (
                      <div key={item.id} className="border border-slate-800 bg-slate-950 p-3 rounded font-mono text-[11px] flex justify-between items-start">
                        <div className="space-y-1.5">
                          <div className="flex items-center space-x-2">
                            <span className="font-bold text-slate-200">{item.project_name}</span>
                            <span className="text-[9px] border border-slate-800 px-1 rounded text-slate-400">{item.id}</span>
                          </div>
                          <p className="text-slate-400 text-[10px] leading-tight">{item.purpose}</p>
                          <div className="flex flex-wrap gap-1">
                            {item.data_classification.map(c => (
                              <span key={c} className="bg-slate-900 text-[9px] px-1 border border-slate-850 text-slate-300 rounded">{c}</span>
                            ))}
                          </div>
                          <div className="text-[9px] text-slate-500">
                            Retention: {item.retention_value} {item.retention_unit}
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                            item.status === 'draft' ? 'bg-slate-900 text-slate-400 border border-slate-800' :
                            item.status === 'submitted' ? 'bg-blue-950 text-blue-400 border border-blue-800/30' :
                            item.status === 'under_review' ? 'bg-purple-950 text-purple-400 border border-purple-800/30' :
                            'bg-emerald-950 text-emerald-400 border border-emerald-800/30'
                          }`}>
                            {item.status}
                          </span>
                          {item.status === 'draft' && (
                            <button
                              onClick={() => {
                                setIsEditingIntake(true);
                                setIntakeForm({
                                  id: item.id,
                                  project_name: item.project_name,
                                  purpose: item.purpose,
                                  data_classification: item.data_classification,
                                  retention_value: item.retention_value,
                                  retention_unit: item.retention_unit,
                                  status: item.status
                                });
                              }}
                              className="text-[9px] text-amber-500 hover:underline hover:text-amber-400 font-bold"
                            >
                              Edit Draft
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Remedial Mitigation Plans Section */}
              <div className="space-y-3 pt-4 border-t border-slate-800">
                <div>
                  <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">// 2.2 Active Remedial Mitigation Plans</h2>
                  <p className="text-[10px] text-slate-500 font-mono">Assigned Action Items & Technical Safeguard Worklists</p>
                </div>

                {isLoadingMitigations ? (
                  <div className="space-y-2">
                    <div className="h-10 border border-slate-800 bg-transparent rounded animate-pulse"></div>
                  </div>
                ) : employeeMitigations.length === 0 ? (
                  <div className="border border-dashed border-slate-850 p-6 text-center text-slate-500 font-mono text-[11px]">
                    // NO ACTIVE REMEDIAL MITIGATION PLANS ASSIGNED
                  </div>
                ) : (
                  <div className="space-y-2">
                    {employeeMitigations.map(item => {
                      const isClosed = item.status === 'closed';
                      return (
                        <div key={item.id} className="border border-slate-850 bg-slate-950 p-3 rounded font-mono text-[11px] flex justify-between items-center">
                          <div className="space-y-1 max-w-[70%]">
                            <div className="flex items-center space-x-2">
                              <span className={`font-bold ${isClosed ? 'line-through text-slate-500' : 'text-slate-200'}`}>{item.title}</span>
                              <span className="text-[9px] text-slate-500 border border-slate-800 px-1 rounded">{item.skill_category}</span>
                            </div>
                            <p className="text-slate-400 text-[10px] leading-tight">{item.description}</p>
                            <div className="text-[9px] text-slate-500 flex space-x-3">
                              <span>Project: <code className="text-amber-500/70">{item.project_id}</code></span>
                              <span>Target: <code className="text-slate-400">{item.framework_target}</code></span>
                              <span>SLA: <code className="text-slate-400">{item.sla_target}</code></span>
                              <span>Due: <code className="text-slate-400">{item.due_date}</code></span>
                            </div>
                          </div>

                          <div className="flex items-center space-x-3">
                            {item.status === 'overdue' && (
                              <span className="bg-red-950 text-red-400 text-[8px] font-black uppercase px-1 rounded animate-pulse">
                                OVERDUE SLA
                              </span>
                            )}
                            <select
                              disabled={isClosed}
                              value={item.status === 'overdue' ? 'open' : item.status}
                              onChange={(e) => handlePatchMitigation(item.id, e.target.value)}
                              className="bg-slate-900 border border-slate-800 text-[10px] text-slate-200 p-1 rounded font-mono focus:outline-none"
                            >
                              <option value="open">Open</option>
                              <option value="in_progress">In Progress</option>
                              <option value="closed">Closed</option>
                            </select>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

            </div>

            {/* Right Column: OPC Communications (40%) */}
            <div className="w-[40%] h-full flex flex-col p-6 space-y-4 bg-slate-900/10">
              <div className="border-b border-slate-800 pb-2">
                <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">// 2.3 OPC Regulatory Inquiry Channels</h2>
                <p className="text-[10px] text-slate-500 font-mono">Asynchronous Regulator Communication Vault</p>
              </div>

              
              {/* Skeletons for OPC */}
              {activeTab === 'command_deck' && generatedReport && (
                <div className="mt-4 p-4 bg-slate-950 border border-emerald-500/50 rounded font-mono text-[10px] space-y-2 shadow-lg shadow-emerald-500/10">
                  <h3 className="text-emerald-500 font-bold uppercase border-b border-emerald-500/30 pb-1">Vault D: Immutable Artifact Committed</h3>
                  <div className="space-y-1">
                    <p><span className="text-slate-500">Timestamp:</span> <span className="text-slate-300">{generatedReport.timestamp}</span></p>
                    <p><span className="text-slate-500">SHA-256:</span> <code className="text-emerald-400 break-all bg-emerald-950/50 px-1 rounded">{generatedReport.sha256_hash}</code></p>
                    <a href={"http://100.117.49.65:8000" + generatedReport.artifact_url} target="_blank" rel="noreferrer" className="block mt-2 text-center bg-emerald-950 hover:bg-emerald-900 text-emerald-400 border border-emerald-800 p-2 rounded uppercase font-bold transition-colors">
                      [ DOWNLOAD RAW REPORT ]
                    </a>
                  </div>
                </div>
              )}

              {isLoadingOpc ? (
                <div className="flex-1 space-y-2">
                  <div className="h-12 border border-slate-800 bg-transparent rounded animate-pulse"></div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col min-h-0 space-y-3">
                  
                  {/* Threads List */}
                  <div className="h-[30%] border border-slate-850 bg-slate-950 rounded divide-y divide-slate-850 overflow-y-auto select-none">
                    {opcInquiries.map(thread => {
                      const isSelected = selectedOpcThreadId === thread.thread_id;
                      
                      // Calculate unread overdue (created > 48 hours and read_status is unread)
                      const createdTime = new Date(thread.created_at).getTime();
                      const fortyEightHoursAgo = Date.now() - (48 * 60 * 60 * 1000);
                      const isOverdueUnread = thread.read_status === 'unread' && createdTime < fortyEightHoursAgo;
                      
                      return (
                        <div
                          key={thread.thread_id}
                          onClick={() => {
                            setSelectedOpcThreadId(thread.thread_id);
                            setNetworkErrorThreadId(null);
                          }}
                          className={`p-3 text-[11px] font-mono cursor-pointer transition-colors flex justify-between items-center ${
                            isSelected ? 'bg-slate-900/60 text-amber-500 font-bold' : 'hover:bg-slate-900/20 text-slate-300'
                          }`}
                        >
                          <div className="space-y-0.5 truncate flex-1 pr-2">
                            <div>{thread.subject}</div>
                            <div className="text-[8px] text-slate-500">Thread: {thread.thread_id}</div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            {isOverdueUnread && (
                              <span className="w-2.5 h-2.5 rounded-full bg-red-600 border border-slate-950 flex-shrink-0 animate-ping" title="Unread > 48h Regulator Warning" />
                            )}
                            <span className={`text-[8px] uppercase px-1 rounded font-bold ${
                              thread.read_status === 'unread' ? 'bg-amber-950 text-amber-400' : 'bg-slate-900 text-slate-500'
                            }`}>
                              {thread.read_status}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Messages History for Selected Thread */}
                  <div className="flex-1 border border-slate-850 bg-slate-950 p-4 rounded font-mono text-[10px] flex flex-col justify-between min-h-0">
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1 select-text">
                      {(() => {
                        const activeThread = opcInquiries.find(t => t.thread_id === selectedOpcThreadId);
                        if (!activeThread) return <div className="text-slate-500 italic text-center py-10">Select an active OPC inquiry thread.</div>;
                        
                        return activeThread.messages.map((m, idx) => {
                          const isCPO = m.sender === 'CPO';
                          return (
                            <div key={m.message_id || idx} className={`space-y-1 ${isCPO ? 'text-left' : 'text-right'}`}>
                              <div className="flex items-center space-x-2 text-[9px] text-slate-500 justify-start" style={{ justifyContent: isCPO ? 'flex-start' : 'flex-end' }}>
                                <span className={`font-bold ${isCPO ? 'text-amber-500' : 'text-slate-300'}`}>[{m.sender}]</span>
                                <span>{m.timestamp}</span>
                              </div>
                              <p className={`p-2 rounded max-w-[85%] inline-block text-left ${
                                isCPO ? 'bg-slate-900 text-slate-200 border border-slate-800' : 'bg-slate-950 text-slate-300 border border-slate-850'
                              }`}>
                                {m.body}
                              </p>
                            </div>
                          );
                        });
                      })()}
                    </div>

                    {/* Reply Form Area */}
                    {selectedOpcThreadId && (
                      <form onSubmit={handlePostOpcReply} className="border-t border-slate-850 pt-3 mt-2 space-y-2">
                        <textarea
                          rows={2}
                          value={opcReplyText}
                          onChange={(e) => setOpcReplyText(e.target.value)}
                          placeholder="Compose plain text reply..."
                          className="w-full bg-slate-900 border border-slate-800 p-2 text-[10px] text-slate-200 rounded focus:outline-none focus:border-amber-500 font-mono resize-none"
                        />
                        
                        <div className="flex justify-between items-center">
                          {networkErrorThreadId === selectedOpcThreadId ? (
                            <button
                              type="button"
                              onClick={() => handleRetryOpcSync(selectedOpcThreadId)}
                              className="text-red-400 hover:text-red-300 font-bold text-[9px] uppercase tracking-wider"
                            >
                              [ CONNECTION ERROR: RETRY SYNC ]
                            </button>
                          ) : (
                            <span className="text-[8px] text-slate-500">UTF-8 Plain Text Only</span>
                          )}
                          <button
                            type="submit"
                            className="bg-amber-500 text-slate-950 font-bold px-3 py-1 text-[10px] uppercase rounded hover:bg-amber-400"
                          >
                            [ SEND REPLY ]
                          </button>
                        </div>
                      </form>
                    )}
                  </div>

                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================================= */}
        {/* 3.0 EXPERT MODE (CPO CONTROL INTERFACE)                                 */}
        {/* ======================================================================= */}
        {securityMode === 'expert' && (
          <div className="flex-1 flex overflow-hidden">
            {/* LEFT PANE: GLOBAL NAVIGATION SIDEBAR (15%) */}
            <div className="w-[15%] h-full border-r border-slate-800 flex flex-col justify-between p-4 bg-slate-950">
              <div className="space-y-6">
                <div className="border-b border-slate-800 pb-3">
                  <h1 className="font-mono font-bold text-xs tracking-tight uppercase text-amber-500">CPO CONTROL</h1>
                  <div className="flex items-center space-x-1.5 mt-2">
                    <span className={`w-2 h-2 rounded-none border border-slate-700 ${isSystemOnline ? 'bg-amber-500 shadow-sm shadow-amber-500/50' : 'bg-transparent animate-pulse'}`}></span>
                    <span className="font-mono text-[9px] uppercase tracking-wider text-slate-500">
                      {isSystemOnline ? 'Gateway Connected' : 'Local Sandbox Mode'}
                    </span>
                  </div>
                </div>
                
                <nav className="flex flex-col space-y-1">
                  <button 
                    onClick={() => setActiveTab('onboarding')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'onboarding' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Briefcase size={13} />
                    <span>0.0 Onboarding</span>
                  </button>

                  <button 
                    onClick={() => setActiveTab('dashboard')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'dashboard' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Activity size={13} />
                    <span>0.1 Exec Dashboard</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab('command_deck')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'command_deck' ? 'bg-red-500/20 text-red-400 border-red-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <AlertOctagon size={13} className={activeTab === 'command_deck' ? 'text-red-500' : ''} />
                    <span>0.5 Command Deck</span>
                  </button>


                  <button 
                    onClick={() => setActiveTab('queue')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex justify-between items-center ${activeTab === 'queue' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <span className="flex items-center space-x-2">
                      <Terminal size={13} />
                      <span>2.0 Response Queue</span>
                    </span>
                    {transactions.filter(t => t.status === 'pending').length > 0 && (
                      <span className={`font-bold text-[9px] px-1 border rounded ${activeTab === 'queue' ? 'border-slate-950 text-slate-950' : 'border-amber-500/30 text-amber-400'}`}>
                        {transactions.filter(t => t.status === 'pending').length}
                      </span>
                    )}
                  </button>
                  <button 
                    onClick={() => setActiveTab('sensory')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'sensory' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Radio size={13} />
                    <span>1.0 Sensory Radar</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab('lifecycle')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'lifecycle' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Layers size={13} />
                    <span>3.0 Lifecycle Matx</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab('vault')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'vault' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Database size={13} />
                    <span>4.0 Evidence Vault</span>
                  </button>

                  <button 
                    onClick={() => setActiveTab('reports')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'reports' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <FileText size={13} />
                    <span>5.0 Reports Vault</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab('health')}
                    className={`w-full text-left font-mono text-xs uppercase p-2 border flex items-center space-x-2 ${activeTab === 'health' ? 'bg-amber-500 text-slate-950 border-amber-500 font-bold' : 'bg-slate-900 text-slate-300 border-transparent hover:border-slate-850'}`}
                  >
                    <Server size={13} />
                    <span>6.0 System Health</span>
                  </button>

                </nav>
              </div>

              <div className="border-t border-slate-800 pt-4 font-mono text-[9px] text-slate-500 space-y-1">
                <p>AUTHORITY: WAEL.CPO</p>
                <p>SPEC: ONBOARDING-CONSOLE v3.0</p>
              </div>
            </div>

            {/* CENTER CONSOLE: MAIN INTERACTIVE CONTROLS (55%) */}
            <div className="w-[55%] h-full overflow-y-auto p-5 flex flex-col bg-slate-900/40">
              
              {/* =================================================================== */}
              
              {/* =================================================================== */}
              {/* TAB 0.5: COMMAND DECK (CPO ONLY)                                    */}
              {/* =================================================================== */}
              {activeTab === 'command_deck' && (
                <div className="space-y-6 flex-1 flex flex-col">
                  <div className="border-b border-red-500/30 pb-2 flex justify-between items-end">
                    <div>
                      <h2 className="text-sm font-bold uppercase tracking-wider text-red-500 flex items-center space-x-2">
                        <AlertOctagon size={16} />
                        <span>Compliance Command Deck</span>
                      </h2>
                      <p className="text-[10px] text-red-400/70 font-mono mt-0.5">Global Master Override & Re-evaluation Engine</p>
                    </div>
                    <button onClick={triggerHorizon} className="bg-red-950 text-red-500 border border-red-900 hover:bg-red-900 font-mono text-xs px-3 py-1 font-bold uppercase rounded shadow-md shadow-red-500/10">
                      [ EXPIRE RISK HORIZON ]
                    </button>
                  </div>
                  
                  {cpoOverrideStatus && (
                    <div className="bg-red-500/20 border border-red-500/50 text-red-400 p-2 text-xs font-mono font-bold uppercase text-center rounded">
                      {cpoOverrideStatus}
                    </div>
                  )}

                  <div className="grid grid-cols-1 gap-6">
                    {/* Skills Matrix */}
                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-1">Human Resource Compliance Deployment</h3>
                      <div className="bg-slate-950 border border-slate-800 rounded p-4 font-mono text-[10px]">
                        {Object.keys(skillsMatrix).length === 0 ? (
                          <div className="text-slate-500 text-center">NO DATA AVAILABLE</div>
                        ) : (
                          <table className="w-full text-left border-collapse">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-400 uppercase">
                                <th className="py-2 px-2">Employee</th>
                                <th className="py-2 px-2">Skill Category</th>
                                <th className="py-2 px-2">Total Mitigations</th>
                                <th className="py-2 px-2">Open/InProgress</th>
                                <th className="py-2 px-2">Closed</th>
                                <th className="py-2 px-2">Overdue</th>
                              </tr>
                            </thead>
                            <tbody>
                              {Object.entries(skillsMatrix).map(([emp, skills]) => (
                                Object.entries(skills).map(([skill, stats]) => (
                                  <tr key={emp+skill} className="border-b border-slate-800/50 text-slate-300">
                                    <td className="py-2 px-2 text-amber-500">{emp}</td>
                                    <td className="py-2 px-2">{skill}</td>
                                    <td className="py-2 px-2">{stats.total}</td>
                                    <td className="py-2 px-2 text-blue-400">{stats.open + stats.in_progress}</td>
                                    <td className="py-2 px-2 text-emerald-400">{stats.closed}</td>
                                    <td className="py-2 px-2 text-red-400">{stats.overdue}</td>
                                  </tr>
                                ))
                              ))}
                            </tbody>
                          </table>
                        )}
                      </div>
                    </div>

                    
                    {/* PROJECT RISK TELEMETRY */}
                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-1">// PROJECT RISK TELEMETRY</h3>
                      <div className="bg-slate-950 border border-slate-800 rounded p-4 font-mono text-[10px] space-y-4">
                        <div className="relative">
                          <input 
                            type="text" 
                            placeholder="Query by project_id, client_name, or system_tag..."
                            value={telemetrySearch}
                            onChange={(e) => handleTelemetrySearch(e.target.value)}
                            className="w-full bg-slate-900 border border-amber-500 text-amber-500 p-2 rounded focus:outline-none placeholder:text-amber-500/30"
                          />
                          {telemetrySearchResults.length > 0 && (
                            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-amber-500/50 rounded max-h-40 overflow-y-auto z-10">
                              {telemetrySearchResults.map(res => (
                                <button 
                                  key={res.project_id} 
                                  onClick={() => loadProjectTelemetry(res.project_id)}
                                  className="w-full text-left p-2 hover:bg-amber-500/20 text-slate-300 flex justify-between"
                                >
                                  <span>{res.client_name}</span>
                                  <span className="text-slate-500">[{res.system_tag}]</span>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>

                        {telemetryData && (
                          <div className="border border-slate-800 rounded bg-slate-900/50 p-4 space-y-4">
                            <h4 className="text-amber-500 font-bold tracking-wider text-center">[ CURRENT RISK POSTURE ]</h4>
                            
                            <div className="grid grid-cols-2 gap-4">
                              <div className="bg-slate-950 p-2 border border-slate-800 rounded">
                                <span className="block text-slate-500 uppercase">Compliance Status</span>
                                <span className={`font-bold uppercase ${telemetryData.current_phase === 'Re-evaluation Required' ? 'text-red-500' : 'text-emerald-500'}`}>
                                  {telemetryData.current_phase}
                                </span>
                              </div>
                              <div className="bg-slate-950 p-2 border border-slate-800 rounded">
                                <span className="block text-slate-500 uppercase">Last Audit</span>
                                <span className="text-slate-300">{telemetryData.last_audit_timestamp}</span>
                              </div>
                            </div>

                            <div className="space-y-2">
                              <span className="text-slate-400 font-bold uppercase block border-b border-slate-800 pb-1">Active Unmitigated Risks</span>
                              {telemetryData.active_risks.length === 0 ? (
                                <span className="text-slate-500 block">NO ACTIVE THREAT VECTORS</span>
                              ) : (
                                telemetryData.active_risks.map(r => (
                                  <div key={r.risk_id} className="flex justify-between items-center text-[9px] bg-red-950/20 border border-red-900/50 p-1.5 rounded">
                                    <span className="text-red-400">{r.description}</span>
                                    <span className="px-1 bg-red-900 text-slate-200 rounded">{r.severity}</span>
                                  </div>
                                ))
                              )}
                            </div>

                            <div className="space-y-2">
                              <span className="text-slate-400 font-bold uppercase block border-b border-slate-800 pb-1">Mitigation Assignments</span>
                              {telemetryData.open_mitigations.length === 0 ? (
                                <span className="text-slate-500 block">ALL TASKS RESOLVED</span>
                              ) : (
                                telemetryData.open_mitigations.map(m => (
                                  <div key={m.task_id} className="flex justify-between text-[9px] bg-slate-950 border border-slate-800 p-1.5 rounded">
                                    <span className="text-slate-300">{m.task_id}</span>
                                    <span className="text-amber-500">Assignee: {m.assignee}</span>
                                  </div>
                                ))
                              )}
                            </div>

                            <div className="pt-2 flex flex-col space-y-2 items-center border-t border-slate-800">
                              {isGeneratingReport ? (
                                <div className="w-full bg-slate-950 border border-amber-500/50 text-amber-500/50 p-2 rounded text-center animate-pulse">
                                  COMPILING IMMUTABLE ARTIFACT...
                                </div>
                              ) : (
                                <button 
                                  onClick={generateRiskReport}
                                  className="w-full bg-slate-200 hover:bg-white text-slate-900 font-bold p-2 rounded uppercase transition-colors"
                                >
                                  [ GENERATE POINT-IN-TIME RISK REPORT ]
                                </button>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Master Ticket Override */}

                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-1">Master Ticket & Override Control</h3>
                      <div className="bg-slate-950 border border-slate-800 rounded font-mono text-[10px] overflow-hidden">
                        {cpoAllMitigations.length === 0 ? (
                          <div className="p-4 text-slate-500 text-center">NO ACTIVE TICKETS</div>
                        ) : (
                          <div className="divide-y divide-slate-800 max-h-96 overflow-y-auto">
                            {cpoAllMitigations.map(mit => (
                              <div key={mit.id} className="p-3 flex justify-between items-center hover:bg-slate-900/50">
                                <div className="space-y-1">
                                  <div className="flex space-x-2">
                                    <span className="font-bold text-slate-200">{mit.title}</span>
                                    <span className="text-slate-500">({mit.id})</span>
                                  </div>
                                  <div className="text-slate-400">
                                    Assignee: <span className="text-amber-500">{mit.employee_id}</span> | Status: <span className="uppercase">{mit.status}</span>
                                  </div>
                                </div>
                                <div className="flex space-x-2">
                                  <button onClick={() => {
                                      const newEmp = prompt("Enter new employee ID:");
                                      if(newEmp) handleCPOOverride('system_cpo', mit.id, 'MANUALLY RE-ROUTE TASK', newEmp);
                                    }} 
                                    className="px-2 py-1 bg-slate-900 border border-slate-700 hover:border-amber-500 text-slate-300 rounded uppercase">
                                    Re-Route
                                  </button>
                                  <button onClick={() => {
                                      if(confirm("Force risk acceptance and close this mitigation?")) {
                                        handleCPOOverride('system_cpo', mit.id, 'FORCED RISK ACCEPTANCE BY CPO', null);
                                      }
                                    }} 
                                    className="px-2 py-1 bg-red-950 border border-red-900 hover:bg-red-900 text-red-400 rounded uppercase">
                                    Force Accept
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 0.0: CLIENT ONBOARDING CENTER                                   */}
              {/* =================================================================== */}
              {activeTab === 'onboarding' && (
                <div className="space-y-6 flex-1 flex flex-col">
                  {/* Title Bar */}
                  <div className="border-b border-slate-800 pb-2 flex justify-between items-end">
                    <div>
                      <h2 className="text-sm font-bold uppercase tracking-wider text-amber-500">Client Onboarding System</h2>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">Automated Privacy Swarm Setup & Compilation</p>
                    </div>
                    <button 
                      onClick={() => setIsAddingClient(!isAddingClient)}
                      className="bg-amber-500 text-slate-950 hover:bg-amber-400 font-mono text-xs px-3 py-1 font-bold uppercase rounded shadow-md shadow-amber-500/10"
                    >
                      {isAddingClient ? 'Cancel' : '+ Onboard New Client'}
                    </button>
                  </div>

                  {/* Add Client Form */}
                  {isAddingClient && (
                    <form onSubmit={handleCreateClient} className="bg-slate-950 border border-slate-800 p-5 rounded space-y-4 font-mono text-xs">
                      <div className="text-amber-500 font-bold border-b border-slate-800 pb-2 uppercase tracking-wide">// Initialize Onboarding Client</div>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="block text-slate-400 uppercase">Client Name</label>
                          <input 
                            type="text" 
                            required
                            value={newClientName}
                            onChange={(e) => setNewClientName(e.target.value)}
                            placeholder="e.g. Acme Corp"
                            className="w-full bg-slate-900 border border-slate-800 p-2 text-slate-100 rounded focus:outline-none"
                          />
                        </div>
                        <div className="space-y-1.5">
                          <label className="block text-slate-400 uppercase">Domain URL (Optional)</label>
                          <input 
                            type="text" 
                            value={newClientUrl}
                            onChange={(e) => setNewClientUrl(e.target.value)}
                            placeholder="e.g. https://acme.com"
                            className="w-full bg-slate-900 border border-slate-800 p-2 text-slate-100 rounded focus:outline-none"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="block text-slate-400 uppercase">Primary Discovery Mode</label>
                          <select 
                            value={newClientMode}
                            onChange={(e) => setNewClientMode(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 p-2 text-slate-100 rounded focus:outline-none text-xs"
                          >
                            <option value="website">Website Scan (Pixels, Policies, Form Disclosures)</option>
                            <option value="documents">Document Audit (Vendor DPAs, Internal Policies)</option>
                            <option value="systems">System Audit (S3 Configurations, Database schemas)</option>
                            <option value="guided">Guided Assessment (Interactive questionnaire)</option>
                            <option value="random">Hybrid / Random Swarm (Aggregated multi-track)</option>
                          </select>
                        </div>
                        <div className="space-y-1.5">
                          <label className="block text-slate-400 uppercase">Risk Confidence Threshold ({newClientThreshold})</label>
                          <input 
                            type="range" 
                            min="0.5" 
                            max="0.99" 
                            step="0.05"
                            value={newClientThreshold}
                            onChange={(e) => setNewClientThreshold(parseFloat(e.target.value))}
                            className="w-full accent-amber-500 bg-slate-800 h-1 rounded"
                          />
                        </div>
                      </div>

                      <button type="submit" className="w-full bg-amber-500 text-slate-950 font-bold p-2.5 rounded uppercase hover:bg-amber-400 transition-colors">
                        Create Client & Lock Registry
                      </button>
                    </form>
                  )}

                  {/* Onboarding Clients Selection Grid */}
                  <div className="grid grid-cols-4 gap-3">
                    {clients.map(c => {
                      const isSelected = selectedClientId === c.id;
                      return (
                        <div 
                          key={c.id}
                          onClick={() => setSelectedClientId(c.id)}
                          className={`cursor-pointer p-3 border rounded text-left transition-all ${isSelected ? 'bg-slate-950 border-amber-500 shadow-md shadow-amber-500/5' : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'}`}
                        >
                          <div className="font-mono text-[9px] text-slate-500 flex justify-between">
                            <span>{c.id}</span>
                            <span className="uppercase text-amber-500 font-bold">{c.status}</span>
                          </div>
                          <div className="font-bold text-xs text-slate-200 mt-1 truncate">{c.name}</div>
                          <div className="font-mono text-[9px] text-slate-400 mt-1.5 uppercase tracking-wider">{c.onboarding_mode} mode</div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Active Client Details & Control Center */}
                  {selectedClientId ? (
                    (() => {
                      const clientObj = clients.find(c => c.id === selectedClientId) || { name: 'Acme Corp', onboarding_mode: 'website', status: 'idle' };
                      return (
                        <div className="space-y-4 mt-2">
                          
                          {/* Active Discovery Control Panel */}
                          <div className="bg-slate-950 border border-slate-800 rounded p-4 flex flex-col space-y-4">
                            <div className="flex justify-between items-center">
                              <div>
                                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wide">Swarm Agent Control: {clientObj.name}</h3>
                                <p className="text-[10px] font-mono text-slate-500">Execution Mode: {clientObj.onboarding_mode} // Target: {clientObj.url || 'No Domain URL'}</p>
                              </div>
                              <button 
                                onClick={() => handleStartDiscovery(selectedClientId, clientObj.onboarding_mode)}
                                disabled={isDiscovering || clientObj.status === 'running'}
                                className="bg-amber-500 hover:bg-amber-400 disabled:bg-slate-800 text-slate-950 disabled:text-slate-500 font-mono font-bold text-xs px-4 py-2 uppercase rounded flex items-center space-x-1.5"
                              >
                                <Sparkles size={13} />
                                <span>{isDiscovering ? 'Swarm Running...' : 'Deploy Discovery Swarm'}</span>
                              </button>
                            </div>

                            {/* Mode Specific Controls */}
                            {clientObj.onboarding_mode === 'website' && (
                              <div className="border border-slate-800 p-3 bg-slate-900/30 rounded font-mono text-[10px] space-y-2">
                                <span className="text-amber-500 font-bold uppercase block">// Website Discovery Options</span>
                                <div className="text-slate-300">
                                  Crawling Target: <code className="text-amber-400 font-bold">{clientObj.url || 'None Provided'}</code>
                                </div>
                              </div>
                            )}

                            {clientObj.onboarding_mode === 'documents' && (
                              <div className="border border-slate-800 p-3 bg-slate-900/30 rounded font-mono text-[10px] space-y-2">
                                <span className="text-amber-500 font-bold uppercase block">// Document Upload Zone</span>
                                <div className="border border-dashed border-slate-700 p-4 text-center text-slate-500 rounded bg-slate-950 hover:border-slate-500 transition-colors">
                                  Drag & drop compliance documents, policies, or DPAs here
                                </div>
                                <div className="flex space-x-2">
                                  <button
                                    type="button"
                                    onClick={() => setUploadedFiles(prev => [...prev, `dpa_contract_${Date.now().toString().slice(-4)}.pdf`])}
                                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 text-[10px] rounded uppercase"
                                  >
                                    + Add DPA Document
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => setUploadedFiles(prev => [...prev, `privacy_policy_internal_${Date.now().toString().slice(-4)}.docx`])}
                                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 text-[10px] rounded uppercase"
                                  >
                                    + Add Internal Policy
                                  </button>
                                </div>
                                {uploadedFiles.length > 0 && (
                                  <div className="space-y-1 mt-2">
                                    <span className="text-slate-500">Staged Files ({uploadedFiles.length}):</span>
                                    {uploadedFiles.map((f, i) => (
                                      <div key={i} className="flex justify-between items-center bg-slate-950 p-1.5 border border-slate-900 rounded">
                                        <span className="text-slate-300">{f}</span>
                                        <button 
                                          type="button"
                                          onClick={() => setUploadedFiles(prev => prev.filter((_, idx) => idx !== i))} 
                                          className="text-red-400 hover:text-red-300"
                                        >
                                          Delete
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}

                            {clientObj.onboarding_mode === 'systems' && (
                              <div className="border border-slate-800 p-3 bg-slate-900/30 rounded font-mono text-[10px] space-y-2">
                                <span className="text-amber-500 font-bold uppercase block">// Organizational Connectors</span>
                                <div className="grid grid-cols-2 gap-3 mt-1">
                                  <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 p-2 border border-slate-900 rounded">
                                    <input
                                      type="checkbox"
                                      checked={systemConnectors.identity}
                                      onChange={(e) => setSystemConnectors({ ...systemConnectors, identity: e.target.checked })}
                                      className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                    <span className="text-slate-300">Okta / Active Directory</span>
                                  </label>
                                  <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 p-2 border border-slate-900 rounded">
                                    <input
                                      type="checkbox"
                                      checked={systemConnectors.productivity}
                                      onChange={(e) => setSystemConnectors({ ...systemConnectors, productivity: e.target.checked })}
                                      className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                    <span className="text-slate-300">Microsoft 365 / Confluence</span>
                                  </label>
                                  <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 p-2 border border-slate-900 rounded">
                                    <input
                                      type="checkbox"
                                      checked={systemConnectors.cloud}
                                      onChange={(e) => setSystemConnectors({ ...systemConnectors, cloud: e.target.checked })}
                                      className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                    <span className="text-slate-300">AWS / GCP / Azure</span>
                                  </label>
                                  <label className="flex items-center space-x-2 cursor-pointer bg-slate-950 p-2 border border-slate-900 rounded">
                                    <input
                                      type="checkbox"
                                      checked={systemConnectors.data}
                                      onChange={(e) => setSystemConnectors({ ...systemConnectors, data: e.target.checked })}
                                      className="border border-slate-700 bg-slate-950 checked:bg-amber-500 checked:border-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                    <span className="text-slate-300">Snowflake / BigQuery</span>
                                  </label>
                                </div>
                              </div>
                            )}

                            {clientObj.onboarding_mode === 'guided' && (
                              <div className="border border-slate-800 p-3 bg-slate-900/30 rounded font-mono text-[10px] space-y-2">
                                <span className="text-amber-500 font-bold uppercase block">// Interactive Questionnaire</span>
                                <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you collect customer information?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.collect_customer_info}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, collect_customer_info: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you process employee information?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.process_employee_info}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, process_employee_info: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you operate internationally?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.operate_internationally}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, operate_internationally: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you process health information?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.process_health_info}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, process_health_info: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you process financial information?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.process_financial_info}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, process_financial_info: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you collect children's data?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.collect_children_data}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, collect_children_data: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you use AI systems?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.use_ai_systems}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, use_ai_systems: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                  <label className="flex items-center justify-between bg-slate-950 p-2 border border-slate-900 rounded cursor-pointer">
                                    <span className="text-slate-300">Do you use biometrics?</span>
                                    <input
                                      type="checkbox"
                                      checked={guidedAnswers.use_biometrics}
                                      onChange={(e) => setGuidedAnswers({ ...guidedAnswers, use_biometrics: e.target.checked })}
                                      className="border-slate-700 bg-slate-900 checked:bg-amber-500 w-3.5 h-3.5 rounded"
                                    />
                                  </label>
                                </div>
                              </div>
                            )}

                            {/* 1984 Hosting DNS Alert / Warning */}
                            {clientObj.onboarding_mode === 'website' && (
                              <div className="border border-amber-500/20 bg-amber-950/10 p-2.5 rounded font-mono text-[10px] flex items-center space-x-2 text-amber-400/90">
                                <AlertTriangle size={14} className="shrink-0 animate-pulse" />
                                <span><strong>Warning:</strong> 1984 Hosting API DNS keys are using static local credentials. Ensure keys are rotated before publishing DNS updates.</span>
                              </div>
                            )}

                            {/* Real-time SSE Stream Output Log */}
                            {(isDiscovering || discoveryLog.length > 0) && (
                              <div className="border border-slate-800 bg-slate-900/60 rounded p-3 font-mono text-[10px] space-y-2 flex flex-col h-[180px] overflow-hidden">
                                <div className="flex justify-between items-center text-slate-400 border-b border-slate-850 pb-1.5">
                                  <span className="flex items-center space-x-1">
                                    <Radio size={11} className="animate-pulse text-amber-400" />
                                    <span>Active Agent Workstream: {discoveryAgent || 'Idle'}</span>
                                  </span>
                                  <span>{Math.round(discoveryProgress)}%</span>
                                </div>
                                
                                {/* Progress Bar */}
                                <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                                  <div className="bg-amber-500 h-full transition-all duration-300" style={{ width: `${discoveryProgress}%` }}></div>
                                </div>

                                <div className="flex-1 overflow-y-auto space-y-1 text-slate-300 pr-1 select-text scrollbar-thin">
                                  {discoveryLog.map((log, index) => (
                                    <div key={index} className="leading-relaxed hover:bg-slate-850/50 p-0.5 rounded">{log}</div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Onboarding Findings Review Console */}
                          <div className="space-y-3">
                            <h3 className="font-mono font-bold text-[10px] text-slate-500 uppercase tracking-wider">// Findings Review Console (Separation of Duties Validation)</h3>
                            
                            <div className="border border-slate-800 bg-slate-950 rounded divide-y divide-slate-800">
                              {findings.length === 0 ? (
                                <p className="font-mono text-xs text-slate-500 italic p-6 text-center">No findings registered yet. Run the discovery swarm to populate the auditing log.</p>
                              ) : (
                                findings.map(f => {
                                  const isSelected = selectedFindingId === f.id;
                                  return (
                                    <div 
                                      key={f.id}
                                      onClick={() => {
                                        setSelectedFindingId(f.id);
                                        setModifyTitle(f.title);
                                        setModifyDesc(f.description || '');
                                      }}
                                      className={`p-4 transition-all duration-150 cursor-pointer ${isSelected ? 'bg-slate-900/50' : 'hover:bg-slate-900/20'}`}
                                    >
                                      <div className="flex justify-between items-start">
                                        <div className="space-y-1.5 flex-1 pr-4">
                                          <div className="flex items-center space-x-2">
                                            <span className="font-mono font-bold text-xs text-amber-500">{f.category}</span>
                                            <span className="font-mono text-[9px] bg-slate-905 border border-slate-800 text-slate-400 px-1 rounded">{f.source}</span>
                                            <span className={`font-mono text-[9px] font-bold px-1 rounded ${f.confidence >= 0.85 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/30' : 'bg-amber-950 text-amber-400 border border-amber-800/30'}`}>
                                              Confidence: {Math.round(f.confidence * 100)}%
                                            </span>
                                          </div>
                                          <div className="text-xs font-bold text-slate-200">{f.title}</div>
                                          <p className="text-[11px] text-slate-400 leading-snug">{f.description}</p>
                                        </div>

                                        {/* Status Tag */}
                                        <div className="flex flex-col items-end space-y-2">
                                          <span className={`font-mono text-[9px] uppercase px-1.5 py-0.5 rounded font-bold ${f.status === 'pending' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                                            {f.decision ? `Decision: ${f.decision}` : f.status}
                                          </span>
                                        </div>
                                      </div>

                                      {/* Accept / Reject / Modify selectors */}
                                      {isSelected && f.status === 'pending' && (
                                        <div className="mt-3.5 pt-3 border-t border-slate-800 flex justify-between items-center" onClick={(e) => e.stopPropagation()}>
                                          <div className="flex space-x-1.5">
                                            <button 
                                              onClick={() => handleFindingDecision(f.id, 'accept')}
                                              className="bg-emerald-500 text-slate-950 hover:bg-emerald-400 font-mono text-[10px] px-3 py-1 font-bold uppercase rounded flex items-center space-x-1"
                                            >
                                              <Check size={11} />
                                              <span>Accept</span>
                                            </button>
                                            <button 
                                              onClick={() => handleFindingDecision(f.id, 'reject')}
                                              className="bg-red-500 text-slate-950 hover:bg-red-450 font-mono text-[10px] px-3 py-1 font-bold uppercase rounded flex items-center space-x-1"
                                            >
                                              <Ban size={11} />
                                              <span>Reject</span>
                                            </button>
                                            <button 
                                              onClick={() => setIsModifyingFinding(!isModifyingFinding)}
                                              className="bg-slate-800 border border-slate-700 text-slate-200 hover:bg-slate-700 font-mono text-[10px] px-3 py-1 uppercase rounded"
                                            >
                                              Modify Finding
                                            </button>
                                          </div>
                                        </div>
                                      )}

                                      {/* Modify Form Drawer */}
                                      {isSelected && isModifyingFinding && (
                                        <div className="mt-3 bg-slate-950 border border-slate-800 p-3 rounded space-y-2.5 font-mono text-[10px]" onClick={(e) => e.stopPropagation()}>
                                          <div className="space-y-1">
                                            <label className="block text-slate-400 uppercase">Adjust Finding Title</label>
                                            <input 
                                              type="text" 
                                              value={modifyTitle}
                                              onChange={(e) => setModifyTitle(e.target.value)}
                                              className="w-full bg-slate-900 border border-slate-800 p-1.5 text-slate-100 rounded focus:outline-none"
                                            />
                                          </div>
                                          <div className="space-y-1">
                                            <label className="block text-slate-400 uppercase">Adjust Finding Description</label>
                                            <textarea 
                                              value={modifyDesc}
                                              onChange={(e) => setModifyDesc(e.target.value)}
                                              className="w-full bg-slate-900 border border-slate-800 p-1.5 text-slate-100 rounded focus:outline-none h-[60px] resize-none"
                                            />
                                          </div>
                                          <button 
                                            onClick={() => handleFindingDecision(f.id, 'modify', { title: modifyTitle, description: modifyDesc })}
                                            className="bg-amber-500 text-slate-950 font-bold px-3 py-1.5 rounded uppercase hover:bg-amber-400"
                                          >
                                            Commit & Recalculate
                                          </button>
                                        </div>
                                      )}
                                    </div>
                                  );
                                })
                              )}
                            </div>
                          </div>

                        </div>
                      );
                    })()
                  ) : (
                    <div className="flex-1 flex items-center justify-center border border-dashed border-slate-800 rounded p-12 text-center text-slate-500 italic font-mono text-xs">
                      No client profile selected. Choose or create a client profile from the top grid to access discovery swarms.
                    </div>
                  )}

                </div>
              )}

              {/* =================================================================== */}
              {/* TAB 1.0: SENSORY RADAR                                              */}
              {/* =================================================================== */}
              {activeTab === 'sensory' && (
                <div className="space-y-6 flex-1 flex flex-col">
                  <div className="border-b border-slate-800 pb-2 flex justify-between items-end">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">1.0 Sensory Radar // Regulatory & Intake Stream</h2>
                    <span className="font-mono text-[9px] text-slate-500">Live Scrapes Active</span>
                  </div>

                  {/* Legislative Horizon scanning */}
                  <div className="space-y-3">
                    <h3 className="font-mono font-bold text-[10px] text-slate-500 uppercase tracking-wider">// U.S. Patchwork Horizon Scanning Terminal</h3>
                    <div className="border border-slate-850 bg-slate-950 rounded divide-y divide-slate-800 font-mono text-[11px]">
                      <div className="p-3 bg-slate-900/10 hover:bg-slate-900/60 cursor-pointer transition-none space-y-1">
                        <div className="flex justify-between font-bold text-slate-200">
                          <span>CPRA (California) ADMT Amendment</span>
                          <span className="text-amber-500">2026-06-20</span>
                        </div>
                        <p className="text-slate-400">California Attorney General issues sweep targeting unvetted algorithmic profiling tools.</p>
                      </div>
                      <div className="p-3 hover:bg-slate-900/40 cursor-pointer transition-none space-y-1">
                        <div className="flex justify-between font-bold text-slate-200">
                          <span>TDPSA (Texas) Data Broker Rule</span>
                          <span className="text-amber-500">2026-06-18</span>
                        </div>
                        <p className="text-slate-400">Texas DPA enforces biometric tracking limits. Mandatory high-risk privacy assessments required.</p>
                      </div>
                      <div className="p-3 hover:bg-slate-900/40 cursor-pointer transition-none space-y-1">
                        <div className="flex justify-between font-bold text-slate-200">
                          <span>FTC Section 5 Deceptive Practices Sweep</span>
                          <span className="text-amber-500">2026-06-15</span>
                        </div>
                        <p className="text-slate-400">FTC targets companies storing consumer datasets indefinitely without a logged retention framework.</p>
                      </div>
                    </div>
                  </div>

                  {/* Intake & routing stream */}
                  <div className="space-y-3 flex-1 flex flex-col">
                    <h3 className="font-mono font-bold text-[10px] text-slate-500 uppercase tracking-wider">// Intake & Legal Routing Stream (Connected Automation)</h3>
                    <div className="border border-slate-850 bg-slate-950 rounded divide-y divide-slate-800 font-mono text-[11px] flex-1">
                      <div className="p-2.5 flex justify-between items-center text-slate-300">
                        <div>
                          <span className="font-bold text-slate-500">[Streamline AI]</span> Inbound Marketing Campaign Review Request
                        </div>
                        <span className="border border-slate-850 px-1.5 py-0.5 text-[9px] uppercase rounded text-slate-500">Tag: marketing</span>
                      </div>
                      <div className="p-2.5 flex justify-between items-center text-slate-300">
                        <div>
                          <span className="font-bold text-slate-500">[Tonkean]</span> DSAR Access Request: ID `req-7729`
                        </div>
                        <span className="border border-slate-850 px-1.5 py-0.5 text-[9px] uppercase rounded text-slate-500">Tag: rights</span>
                      </div>
                      <div className="p-2.5 flex justify-between items-center text-slate-300">
                        <div>
                          <span className="font-bold text-amber-500">[Git Webhook]</span> New LLM Inference Agent Deployment (Swarm-AI)
                        </div>
                        <span className="bg-amber-500 text-slate-950 px-1.5 py-0.5 text-[9px] uppercase font-bold rounded">Tag: model-service</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* =================================================================== */}
              {/* TAB 2.0: RESPONSE QUEUE (HITL Interruption Queue)                   */}
              {/* =================================================================== */}
              {activeTab === 'queue' && (
                <div className="flex-1 flex flex-col space-y-4">
                  <div className="border-b border-slate-850 pb-2 flex justify-between items-center">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">2.0 Action Queue // Interrupt Breakpoints</h2>
                    <div className="text-[9px] bg-amber-500 text-slate-950 px-1.5 py-0.5 font-mono uppercase font-bold rounded">
                      HITL Boundary Locked
                    </div>
                  </div>

                  <div className="space-y-2 overflow-y-auto flex-1 pr-1 border border-slate-850 p-3 bg-slate-950/60 rounded divide-y divide-slate-850">
                    {transactions.length === 0 ? (
                      <p className="font-mono text-xs text-slate-500 italic p-4 text-center">Zero active agent processes suspended in LangGraph checkpoint layer.</p>
                    ) : (
                      transactions.map((tx) => {
                        const isSelected = selectedId === tx.id;
                        return (
                          <div
                            key={tx.id}
                            onClick={() => setSelectedId(tx.id)}
                            className={`w-full text-left p-4 border rounded transition-all duration-150 cursor-pointer select-none flex justify-between items-start ${isSelected ? 'bg-slate-900/60 border-amber-500' : 'bg-slate-900/10 border-transparent hover:bg-slate-900/20'}`}
                          >
                            <div className="space-y-2 flex-1">
                              <div className="flex items-center space-x-2">
                                <span className="font-mono font-bold text-xs uppercase tracking-wider text-slate-200">
                                  {tx.id}
                                </span>
                                <span className="font-mono text-[9px] border border-slate-800 px-1.5 uppercase rounded text-slate-400">
                                  {tx.jurisdiction}
                                </span>
                                <span className={`font-mono text-[9px] px-1.5 uppercase font-bold rounded ${tx.priority === 'critical' ? 'bg-amber-500 text-slate-950 animate-pulse' : 'border border-slate-850 text-slate-300'}`}>
                                  {tx.priority}
                                </span>
                              </div>
                              
                              <p className="text-xs font-bold text-slate-200 leading-tight">{tx.description}</p>
                              
                              <div className="text-[10px] font-mono text-slate-500">
                                Agent: {tx.agent}
                              </div>

                              {isSelected && (
                                <div className="mt-4 pt-2 border-t border-slate-800 space-y-2" onClick={(e) => e.stopPropagation()}>
                                  {renderSectoralQuestionnaire(tx)}
                                </div>
                              )}
                            </div>

                            <div className="ml-4 font-mono text-[10px] uppercase font-bold border border-slate-850 px-2 py-0.5 rounded text-slate-400 bg-slate-950">
                              {tx.status}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}

              {/* =================================================================== */}
              {/* TAB 3.0: LIFECYCLE MONITOR                                          */}
              {/* =================================================================== */}
              {activeTab === 'lifecycle' && (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="border-b border-slate-850 pb-2 flex justify-between items-center">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">3.0 Lifecycle Monitor // 10-Phase Kanban Pipeline</h2>
                    
                    <button 
                      onClick={() => setSimulatedLeak(!simulatedLeak)}
                      className={`font-mono text-[9px] border border-slate-800 px-2 py-1 uppercase font-bold rounded transition-colors duration-200 ${simulatedLeak ? 'bg-amber-500 text-slate-950 border-amber-500' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'}`}
                    >
                      {simulatedLeak ? 'Disable Leak Anomaly' : 'Simulate Phase 8 Data Leakage Anomaly'}
                    </button>
                  </div>

                  {simulatedLeak && (
                    <div className="border border-red-500/20 p-3 bg-red-950/20 font-mono text-xs flex items-center justify-between text-red-400 rounded animate-pulse">
                      <div className="flex items-center space-x-2 font-bold">
                        <AlertTriangle size={14} />
                        <span>[ANOMALY TRIGGER] DATA LEAK DETECTED ON S3 BUCKET!</span>
                      </div>
                      <span>Dashed routing path bypass active: Phase 8 &rarr; Phase 9 Triage Container</span>
                    </div>
                  )}

                  {/* Horizontal 10-Phase Kanban layout */}
                  <div className="grid grid-cols-5 gap-2 flex-1 overflow-y-auto">
                    
                    {/* P1-P3: Governance & Ingest */}
                    <div className="border border-slate-850 p-2.5 font-mono text-[10px] space-y-3 bg-slate-950 rounded">
                      <div className="font-bold border-b border-slate-800 pb-1 uppercase text-slate-400 bg-slate-900 p-1 tracking-wider text-center">P1-P3: GOVERNANCE</div>
                      <div className="space-y-2">
                        <div className="border border-slate-850 p-1.5 space-y-1 rounded bg-slate-900/20">
                          <div className="font-bold text-slate-300">[App: Swarm-AI]</div>
                          <div className="text-slate-500">Phase 2: Inventory</div>
                          <div className="text-[9px] text-amber-500">Status: Mapping</div>
                        </div>
                        <div className="border border-slate-850 p-1.5 space-y-1 bg-slate-900/60 rounded">
                          <div className="font-bold text-slate-300">[App: API-Gateway]</div>
                          <div className="text-slate-500">Phase 3: Intake</div>
                          <div className="text-[9px] text-emerald-400">Status: Audited</div>
                        </div>
                      </div>
                    </div>

                    {/* P4-P5: Risk Assessment */}
                    <div className="border border-slate-850 p-2.5 font-mono text-[10px] space-y-3 bg-slate-950 rounded">
                      <div className="font-bold border-b border-slate-800 pb-1 uppercase text-slate-400 bg-slate-900 p-1 tracking-wider text-center">P4-P5: RISK ASMT</div>
                      <div className="space-y-2">
                        <div className="border border-slate-850 p-1.5 space-y-1 rounded bg-slate-900/20">
                          <div className="font-bold text-slate-300">[App: Core-CRM]</div>
                          <div className="text-slate-500">Phase 4: State DPA</div>
                          <div className="text-[9px] text-amber-500">Status: Assessing</div>
                        </div>
                      </div>
                    </div>

                    {/* P6-P8: Vendor & Launch */}
                    <div className="border border-slate-850 p-2.5 font-mono text-[10px] space-y-3 bg-slate-950 rounded relative">
                      <div className="font-bold border-b border-slate-800 pb-1 uppercase text-slate-400 bg-slate-900 p-1 tracking-wider text-center">P6-P8: LAUNCH & OPS</div>
                      <div className="space-y-2">
                        <div className={`border border-slate-850 p-1.5 space-y-1 rounded transition-all ${simulatedLeak ? 'border-dashed border-red-500 bg-red-950/10 opacity-50' : 'bg-slate-900/20'}`}>
                          <div className="font-bold text-slate-300">[App: HR-Portal]</div>
                          <div className="text-slate-500">Phase 8: Continuous</div>
                          <div className="text-[9px] text-emerald-400">Status: Active</div>
                        </div>
                      </div>
                      {simulatedLeak && (
                        <div className="absolute top-1/2 left-full w-full border-t-2 border-dashed border-red-500 z-10 -ml-2 select-none pointer-events-none flex justify-center items-center">
                          <span className="bg-red-500 text-slate-950 text-[8px] font-bold px-1 uppercase tracking-wider rounded">Breach Pipeline rerouting</span>
                        </div>
                      )}
                    </div>

                    {/* P9: Incidents & Breach */}
                    <div className={`border border-slate-850 p-2.5 font-mono text-[10px] space-y-3 bg-slate-950 rounded ${simulatedLeak ? 'border-red-500 bg-red-950/10 animate-pulse' : ''}`}>
                      <div className="font-bold border-b border-slate-800 pb-1 uppercase text-slate-400 bg-slate-900 p-1 tracking-wider text-center">P9: INCIDENTS</div>
                      <div className="space-y-2">
                        {simulatedLeak ? (
                          <div className="border border-red-500 p-1.5 space-y-1 bg-slate-950 rounded">
                            <div className="font-bold text-red-500">[App: HR-Portal]</div>
                            <div className="font-bold text-slate-300 text-[9px]">Phase 9: Breach Triage</div>
                            <div className="text-red-400 font-bold uppercase text-[8px] animate-pulse">! CRITICAL TRIAGE ACTIVE !</div>
                          </div>
                        ) : (
                          <div className="border border-slate-850 p-1.5 space-y-1 rounded bg-slate-900/20">
                            <div className="font-bold text-slate-300">[App: Legacy-S3]</div>
                            <div className="text-slate-500">Phase 9: Remediation</div>
                            <div className="text-[9px] text-slate-400">Status: Triage Complete</div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* P10: Assurance & Audit */}
                    <div className="border border-slate-850 p-2.5 font-mono text-[10px] space-y-3 bg-slate-950 rounded">
                      <div className="font-bold border-b border-slate-800 pb-1 uppercase text-slate-400 bg-slate-900 p-1 tracking-wider text-center">P10: AUDIT & VAULT</div>
                      <div className="space-y-2">
                        <div className="border border-slate-850 p-1.5 space-y-1 bg-slate-900/60 rounded">
                          <div className="font-bold text-slate-300">[App: Billing-Node]</div>
                          <div className="text-slate-500">Phase 10: Attested</div>
                          <div className="text-[9px] text-emerald-400">Status: Assured</div>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              )}

              {/* =================================================================== */}
              {/* TAB 4.0: EVIDENCE VAULT                                             */}
              {/* =================================================================== */}
              {activeTab === 'vault' && (
                <div className="space-y-4 flex-1 flex flex-col">
                  <div className="border-b border-slate-850 pb-2 flex justify-between items-end">
                    <h2 className="text-xs font-bold uppercase tracking-wider text-amber-500">4.0 Regulatory Evidence Vault // Immutable Audit Proofs</h2>
                    <span className="font-mono text-[9px] text-slate-500">Cryptographically Signed (SHA-256)</span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 flex-1 overflow-hidden">
                    {/* Left side: Folder Tree */}
                    <div className="border border-slate-850 divide-y divide-slate-850 font-mono text-xs overflow-y-auto bg-slate-950 rounded">
                      <div className="bg-slate-900 p-2 font-bold uppercase select-none tracking-wider text-slate-400">// Folder Tree Matrix</div>
                      
                      {/* Vault A */}
                      <div className="p-2 space-y-1">
                        <div className="font-bold text-slate-200">📁 VAULT A: GOVERNANCE & MAPPING LOGS</div>
                        <div className="pl-4 space-y-1 text-[11px] text-slate-400">
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_a_1')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_a_1' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 1. Privacy Management Program Doc [Phase 1]
                          </button>
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_a_2')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_a_2' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 2. AI Governance Program Baseline [Phase 1]
                          </button>
                        </div>
                      </div>

                      {/* Vault B */}
                      <div className="p-2 space-y-1">
                        <div className="font-bold text-slate-200">📁 VAULT B: ASSESSMENTS & APPROVALS</div>
                        <div className="pl-4 space-y-1 text-[11px] text-slate-400">
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_b_1')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_b_1' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 5. State Comprehensive Data Assessments [Phase 4]
                          </button>
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_b_2')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_b_2' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 6. Algorithmic Impact Assessment [Phase 4]
                          </button>
                        </div>
                      </div>

                      {/* Vault C */}
                      <div className="p-2 space-y-1">
                        <div className="font-bold text-slate-200">📁 VAULT C: SPECIALIZED & TECHNICAL LOGS</div>
                        <div className="pl-4 space-y-1 text-[11px] text-slate-400">
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_c_1')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_c_1' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 9. HIPAA Expert Determination Statistical Reports [ExpertDet]
                          </button>
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_c_2')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_c_2' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 11. COPPA & Biometric Notice Logs [Phase 5]
                          </button>
                        </div>
                      </div>

                      {/* Vault D */}
                      <div className="p-2 space-y-1">
                        <div className="font-bold text-slate-200">📁 VAULT D: OPERATIONS & ACCOUNTABILITY</div>
                        <div className="pl-4 space-y-1 text-[11px] text-slate-400">
                          <button 
                            onClick={() => setSelectedVaultDoc('vault_d_1')} 
                            className={`block text-left w-full hover:underline font-mono ${selectedVaultDoc === 'vault_d_1' ? 'font-bold text-amber-400 underline' : ''}`}
                          >
                            📄 13. 50-State Breach Assessment Evaluation Matrix [Phase 9]
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Right side: Reader Panel */}
                    <div className="border border-slate-850 bg-slate-950 p-4 font-mono text-[11px] flex flex-col justify-between overflow-y-auto rounded">
                      {selectedVaultDoc ? (
                        <div className="space-y-4">
                          <div className="border-b border-slate-800 pb-2">
                            <span className="font-bold uppercase tracking-wider block text-xs text-amber-500">Document Detail Viewer</span>
                            <span className="text-[10px] text-slate-500">Read-Only Secure Pipeline Vault</span>
                          </div>
                          
                          {selectedVaultDoc === 'vault_a_1' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: Privacy Management Program Documentation</p>
                              <p className="text-slate-400">Phase Ref: Phase 1 (Strategy & Governance)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                This document formalizes the corporate data steering framework. Annual Privacy Program approved by CPO on 2026-01-15. Scans are active across internal databases.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: e4f9e8a83d73b37ea31e13a96827aae41e4649b934ca495991b5c2d3b2e59178
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_a_2' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: AI Governance Program Baseline Framework</p>
                              <p className="text-slate-400">Phase Ref: Phase 1 (Strategy & Governance)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                Rules for LLM inference gateways, routing templates, and LLM safety filters. Restricts model deployments until formal DPIA checklists are cleared in Phase 4.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: b8a6234b3f81e3a96827aae41e4649b934ca495991b5c2d3b2e5917812f8a9ee
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_b_1' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: State Comprehensive Data Protection Assessments (DPAs)</p>
                              <p className="text-slate-400">Phase Ref: Phase 4 (Privacy Risk Assessment)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                Archived state DPAs mapping CPRA profiling restrictions and high-risk data cybersecurity audits. Evaluates compliance targets across CRM platforms.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: 98a3e74ca8f81e3a962768b3f81e3a96827aae41e4649b934ca495991b5c2d3a
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_b_2' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: Algorithmic Impact & AI Impact Assessments (AIA)</p>
                              <p className="text-slate-400">Phase Ref: Phase 4 (Privacy Risk Assessment)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                AIA audit report regarding the Swarm-AI autonomous workforce engine. Identifies re-identification risks and outlines mitigations via local-first computing clusters.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: c983dfa3f81e3a96827aae41e4649b934ca495991b5c2d3b2e59178f8a9ee12
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_c_1' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: HIPAA Expert Determination Statistical Reports</p>
                              <p className="text-slate-400">Phase Ref: ExpertDet Pipeline</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                Evaluations and certifications proving "very small" re-identification risk under HIPAA standards, bypassing Safe Harbor defaults for medical diagnostic telemetry.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: a6e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b5c2d3b
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_c_2' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: COPPA Compliance & Biometric Consent Logs</p>
                              <p className="text-slate-400">Phase Ref: Phase 5 (Privacy by Design)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                Verifiable parental consent audit logs and BIPA explicit notices. Details storage and destruction schedules for biometric signatures.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: 149afbf4c8996fb92427ae41e4649b934ca495991b5c2d3b2e59178a3c00fba
                              </p>
                            </div>
                          )}

                          {selectedVaultDoc === 'vault_d_1' && (
                            <div className="space-y-2">
                              <p className="font-bold text-slate-200">Title: 50-State Breach Assessment Evaluation Matrices</p>
                              <p className="text-slate-400">Phase Ref: Phase 9 (Incident Management)</p>
                              <p className="border border-slate-850 p-2 bg-slate-900/40 text-slate-300 leading-snug rounded">
                                Triage evaluation matrix testing regulatory breach reporting requirements across 50 US jurisdictions following database exposure events.
                              </p>
                              <p className="text-[10px] text-slate-500 font-mono break-all bg-slate-900 p-2 rounded">
                                SHA-256 Digest: 3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b5c2d3be3
                              </p>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="h-full flex items-center justify-center text-center text-slate-500 italic">
                          Select a vault document from the folder tree to inspect details.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* RIGHT PANE: LEGAL LINEAGE & COMPILED REPORT OR RAW PAYLOAD INSPECTOR (30%) */}
            <div className="w-[30%] h-full border-l border-slate-800 flex flex-col justify-between p-4 bg-slate-950 overflow-y-auto">
              
              {/* If active Tab is Client Onboarding, render the 16-deliverables Onboarding Report Summary */}
              {activeTab === 'onboarding' ? (
                <div className="flex-1 flex flex-col space-y-4 select-text">
                  <div className="space-y-1">
                    <h3 className="font-mono text-[10px] uppercase text-slate-500 tracking-wider">// Onboarding Deliverables Report</h3>
                    <div className="flex items-center justify-between border border-slate-800 p-3 bg-slate-900/20 rounded font-mono text-xs">
                      <div>
                        <span className="font-bold text-slate-200">Completion Status</span>
                        <div className="text-[10px] text-slate-500 mt-0.5">16 Mandatory Sections</div>
                      </div>
                      <span className="text-lg font-black text-amber-500">{report ? report.completion_percentage : 0}%</span>
                    </div>
                  </div>

                  {/* 16 Deliverables List */}
                  <div className="space-y-1.5 flex-1 overflow-y-auto pr-1">
                    {report && report.report_data ? (
                      Object.entries(report.report_data).map(([secTitle, data]) => (
                        <div key={secTitle} className="border border-slate-900 bg-slate-950 rounded p-2.5 font-mono text-[10px] space-y-1">
                          <div className="flex justify-between items-start font-bold">
                            <span className="text-slate-200 text-[11px] leading-tight">{secTitle}</span>
                            <span className={`shrink-0 text-[8px] px-1 rounded uppercase font-bold ${data.status === 'Ready' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/30' : 'bg-amber-950 text-amber-500 border border-amber-900/30'}`}>
                              {data.status}
                            </span>
                          </div>
                          
                          {data.findings && data.findings.length > 0 ? (
                            <div className="pt-1.5 space-y-1">
                              <span className="text-slate-500 block">Associated Findings ({data.findings.length}):</span>
                              {data.findings.map(f => (
                                <div key={f.id} className="bg-slate-900/40 p-1.5 border border-slate-900 rounded flex justify-between items-center">
                                  <span className="text-slate-300 truncate w-[75%]">{f.title}</span>
                                  <span className={`text-[8px] uppercase font-bold ${f.decision === 'accept' ? 'text-emerald-400' : 'text-amber-500'}`}>{f.decision || 'pending'}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <span className="text-slate-500 italic block text-[9px]">No associated anomalies discovered. Default templates generated.</span>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-500 italic text-center text-xs mt-12">Compile data or select a client profile to build deliverables.</p>
                    )}
                  </div>
                </div>
              ) : selectedTx ? (
                // Original Expert CPO Control Queue Details
                <div className="flex-1 flex flex-col space-y-5">
                  
                  {/* Legal Lineage panel */}
                  <div className="space-y-1.5">
                    <h3 className="font-mono text-[10px] uppercase text-slate-500 tracking-wider">// Legal Framework Lineage</h3>
                    <div className="border border-slate-800 p-3 bg-slate-900/20 font-mono text-[11px] space-y-1 rounded">
                      <p className="font-bold uppercase text-slate-200">{selectedTx.type} Verification Gate</p>
                      <p className="text-slate-400">Jurisdiction: {selectedTx.jurisdiction}</p>
                      <p className="text-slate-400">SLA Constraint: {selectedTx.deadline}</p>
                    </div>
                  </div>

                  {/* Summary panel */}
                  <div className="space-y-1.5">
                    <h3 className="font-mono text-[10px] uppercase text-slate-500 tracking-wider">// Summary Extraction</h3>
                    <div className="border border-slate-800 p-3 text-xs leading-relaxed bg-slate-950 text-slate-300 rounded">
                      {selectedTx.summary}
                    </div>
                  </div>

                  {/* Raw JSON Payload */}
                  <div className="space-y-1.5 flex-1 flex flex-col min-h-[140px]">
                    <h3 className="font-mono text-[10px] uppercase text-slate-500 tracking-wider">// Raw Context Telemetry Payload</h3>
                    <div className="flex-1 border border-slate-800 bg-slate-900/20 p-2.5 font-mono text-[10px] overflow-auto select-text rounded">
                      {typeof selectedTx.raw === 'string'
                        ? (() => {
                            try {
                              return JSON.stringify(JSON.parse(selectedTx.raw), null, 2);
                            } catch (e) {
                              return selectedTx.raw;
                            }
                          })()
                        : JSON.stringify(selectedTx.raw, null, 2)
                      }
                    </div>
                  </div>

                  {/* ACTION BLOCK: SEMANTIC HITL CONTROLS */}
                  <div className="space-y-3 pt-3 border-t border-slate-800 bg-slate-950 select-none">
                    <div className="space-y-1">
                      <label className="font-mono text-[9px] uppercase text-slate-500 font-bold">
                        Reasoning Configuration (Appends to Audit Ledger)
                      </label>
                      <textarea 
                        value={reasoning}
                        onChange={(e) => setReasoning(e.target.value)}
                        disabled={selectedTx.status !== 'pending'}
                        placeholder="Enter statutory justification, citations, or rationale context..."
                        className="w-full text-xs p-2 border border-slate-800 bg-slate-900 text-slate-200 focus:outline-none focus:border-amber-500 font-mono resize-none h-[65px] rounded disabled:bg-slate-900 disabled:text-slate-500"
                      />
                    </div>

                    {/* 5 High-Contrast Action Buttons */}
                    <div className="flex flex-col space-y-1 font-mono">
                      <div className="grid grid-cols-2 gap-1">
                        <button 
                          disabled={selectedTx.status !== 'pending'}
                          onClick={() => handleAction('approve_now')}
                          className="border border-slate-800 bg-slate-900 hover:bg-amber-500 hover:text-slate-950 p-2 text-xs uppercase font-bold rounded disabled:border-slate-850 disabled:text-slate-600 disabled:hover:bg-slate-900 disabled:hover:text-slate-600 cursor-pointer text-slate-200"
                        >
                          [ Approve Now ]
                        </button>
                        <button 
                          disabled={selectedTx.status !== 'pending'}
                          onClick={() => handleAction('approve_always')}
                          className="border border-slate-800 bg-slate-900 hover:bg-amber-500 hover:text-slate-950 p-2 text-xs uppercase font-bold rounded disabled:border-slate-850 disabled:text-slate-600 disabled:hover:bg-slate-900 disabled:hover:text-slate-600 cursor-pointer text-slate-200"
                        >
                          [ Approve Always ]
                        </button>
                      </div>
                      <div className="grid grid-cols-2 gap-1">
                        <button 
                          disabled={selectedTx.status !== 'pending'}
                          onClick={() => handleAction('flag_legal')}
                          className="border border-slate-800 bg-slate-900 hover:bg-amber-500 hover:text-slate-950 p-2 text-[10px] uppercase rounded disabled:border-slate-850 disabled:text-slate-600 disabled:hover:bg-slate-900 cursor-pointer text-slate-300"
                        >
                          [ Flag Legal ]
                        </button>
                        <button 
                          disabled={selectedTx.status !== 'pending'}
                          onClick={() => handleAction('review_later')}
                          className="border border-slate-800 bg-slate-900 hover:bg-amber-500 hover:text-slate-950 p-2 text-[10px] uppercase rounded disabled:border-slate-850 disabled:text-slate-600 disabled:hover:bg-slate-900 cursor-pointer text-slate-300"
                        >
                          [ Review Later ]
                        </button>
                      </div>
                      <button 
                        disabled={selectedTx.status !== 'pending'}
                        onClick={() => handleAction('reject')}
                        className="w-full border border-red-500/30 bg-red-950/20 text-red-400 hover:bg-red-500 hover:text-slate-950 p-2 text-xs uppercase font-bold mt-1 rounded disabled:border-slate-850 disabled:text-slate-600 disabled:hover:bg-slate-900 cursor-pointer"
                      >
                        [ REJECT & SUSPEND ]
                      </button>
                    </div>
                  </div>

                  {/* Secure Audit Receipt block showing SHA-256 Hash */}
                  {auditReceipt && auditReceipt.txId === selectedTx.id && (
                    <div className="border border-slate-800 p-3 bg-slate-950 font-mono text-[9px] space-y-1 rounded">
                      <div className="font-bold border-b border-slate-800 pb-0.5 uppercase tracking-wider flex items-center space-x-1 text-slate-300">
                        <FileCheck size={12} className="text-amber-500" />
                        <span>Secure Audit Block Generated</span>
                      </div>
                      <div>Tx ID: {auditReceipt.txId}</div>
                      <div>Trace: LANGGRAPH_HUMAN_RESUMED</div>
                      <div className="break-all font-bold text-amber-500">SHA-256: {auditReceipt.hash}</div>
                    </div>
                  )}

                </div>
              ) : (
                <div className="h-full flex items-center justify-center font-mono text-xs text-slate-500 text-center italic">
                  Select an active processing thread from the queue to inspect framework mappings.
                </div>
              )}
            </div>
          </div>
        )}
        </>
      )}
      </div>
    </div>
  );
};

export default App;
