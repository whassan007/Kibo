import React from 'react';
import { 
  ShieldCheck, AlertTriangle, FileCheck, CheckSquare, ListChecks, ArrowUpRight, Check, Activity, Search,
  Server, Cpu, Database, Eye, Terminal, FileText, Lock, Globe, Shield, RefreshCw, Layers, Inbox, AlertCircle, Sparkles, Plus, Clock, Key,
  Mail, Users, Briefcase, List,
  BookOpen, ChevronDown, FileUp, FolderOpen, Network, Radio, Settings, ShieldAlert, UserCheck
} from 'lucide-react';

import OntologyVisualizer from '../components/OntologyVisualizer';
import ShadowRiskFeed from '../components/ShadowRiskFeed';
import ScopeActiveLegislations from '../components/ScopeActiveLegislations';
import CommissionerLinks from '../components/CommissionerLinks';

const ExpertMode = (props) => {
  const {
    activeTab, setActiveTab, activeJurisdiction, jurConfig, setSecurityMode, setAdminDiffMode,
    expertAssessments, expertMeetings, expertInbox, expertComplianceTraining,
    onboardingTasks, onbGaps, handleOnbGapSubmit, newGapDesc, setNewGapDesc, newGapSev, setNewGapSev,
    onboardingCasl, handleOnboardingTaskToggle, handleOnboardingNotesSave,
    editingTaskId, setEditingTaskId, editTaskNotes, setEditTaskNotes,
    handleOnboardingCaslSunset, simLogs, simIsRunning,
    complianceProgress, riskScore, riskTrend, assessmentCoverage, openIssues,
    employeeDataFlows, thirdPartyDataFlows, activeThreats, recentAudits, complianceTrendData,
    expertExpandedAssessments, toggleExpertAssessment, onboardingSubMode, setOnboardingSubMode,
    lessonsIsExpanded, setLessonsIsExpanded, agentLessons,
    hitlQueue, inboxEmails, agentLogs, isSimulatingLoop, isSystemOnline,
    activeLegislations, handleResolveHitlDecision,
    govDataInventory = [], govSubProcessors = [], govRoleHierarchy = [],
    agentsList = [], caslRegistry = [], caslLogs = [], caslDisclaimers = [], caslDataElements = [],
    meetingActionItems = [], inboxReplies = [], onbUploadedFiles = [], onbLogs = [], legalLibrary = [], onbProfile = {}
  } = props;

  const [queueFilter, setQueueFilter] = React.useState('all');

  // --- Local fallback state/handlers (were referenced but never declared) ---
  const [govIsExpanded, setGovIsExpanded] = React.useState(true);
  const [govSelectedTab, setGovSelectedTab] = React.useState('inventory');
  const [editingNotesTaskId, setEditingNotesTaskId] = React.useState(null);
  const [editingNotesText, setEditingNotesText] = React.useState('');
  const [isSunsetting, setIsSunsetting] = React.useState(false);
  const [onbGapInputs, setOnbGapInputs] = React.useState({});
  const [onbSectorVariant, setOnbSectorVariant] = React.useState('');
  const [onbSelectedProfileSection, setOnbSelectedProfileSection] = React.useState(null);
  const [onbStatus, setOnbStatus] = React.useState('');
  const [onbWebsiteUrl, setOnbWebsiteUrl] = React.useState('');
  const [trainingCompliance, setTrainingCompliance] = React.useState([]);
  const [meetingActionOwner, setMeetingActionOwner] = React.useState('');
  const [meetingActionTask, setMeetingActionTask] = React.useState('');
  const [meetingMinutes, setMeetingMinutes] = React.useState('');
  const [meetingsAgenda, setMeetingsAgenda] = React.useState('');
  const [meetingsDate, setMeetingsDate] = React.useState('');
  const [meetingsType, setMeetingsType] = React.useState('privacy_security_weekly');
  const [newLessonDomain, setNewLessonDomain] = React.useState('onboarding');
  const [newLessonNotes, setNewLessonNotes] = React.useState('');
  const [replyBody, setReplyBody] = React.useState('');
  const [selectedEmail, setSelectedEmail] = React.useState(null);
  const [selectedMeetingId, setSelectedMeetingId] = React.useState(null);
  const [simTriggerData, setSimTriggerData] = React.useState('');
  const [simTriggerType, setSimTriggerType] = React.useState('Regulatory_Update');
  const setMeetingActionItems = () => {};
  const setOnbLogs = () => {};
  const setOnbUploadedFiles = () => {};
  const handleAddActionItem = () => {};
  const handleAddLesson = () => {};
  const handleCreateMeeting = (e) => { if (e && e.preventDefault) e.preventDefault(); };
  const handleFinalizeOnbProfile = () => {};
  const handleRunCaslSunset = () => {};
  const handleStartOnboarding = (e) => { if (e && e.preventDefault) e.preventDefault(); };
  const handleTriggerSelfImprovement = () => {};

  return (
          <div className="flex-1 flex overflow-hidden">
            
            {/* Sidebar Tabs */}
            <aside className="w-56 bg-white border-r border-[#E5E7EB] p-4 flex flex-col justify-between">
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
                  <Sparkles size={14} className="text-blue-600 animate-pulse shrink-0" />
                  <span className="font-semibold text-blue-755 flex-1 text-left">CPO Agents Console</span>
                  {hitlQueue.filter(h => h.status === 'pending').length > 0 && (
                    <span className="bg-rose-100 text-rose-700 text-[10px] font-bold px-1.5 py-0.5 rounded-full shrink-0">
                      {hitlQueue.filter(h => h.status === 'pending').length}
                    </span>
                  )}
                </button>
                <button 
                  onClick={() => setActiveTab('inbox')}
                  className={`w-full text-left p-2.5 text-xs rounded-lg hover:bg-gray-100 flex items-center space-x-2.5 transition-all cursor-pointer ${
                    activeTab === 'inbox' ? 'bg-blue-50 text-blue-700 font-semibold shadow-xs' : 'text-gray-600'
                  }`}
                >
                  <Inbox size={14} className="shrink-0" />
                  <span className="flex-1 text-left">Privacy Inbox</span>
                  {inboxEmails.filter(e => e.status === 'unread').length > 0 && (
                    <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-1.5 py-0.5 rounded-full shrink-0">
                      {inboxEmails.filter(e => e.status === 'unread').length}
                    </span>
                  )}
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
                    <ListChecks size={14} className="shrink-0" />
                    <span className="flex-1 text-left">Onboarding Checklist</span>
                    {onbGaps.filter(g => g.status === 'pending').length > 0 && (
                      <span className="bg-amber-100 text-amber-700 text-[10px] font-bold px-1.5 py-0.5 rounded-full shrink-0">
                        {onbGaps.filter(g => g.status === 'pending').length}
                      </span>
                    )}
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
                    <span className="bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded font-bold uppercase font-mono">{activeJurisdiction}</span>
                  </div>
                  <div className="text-[9px] text-gray-400 space-y-1 font-mono leading-relaxed border-t border-indigo-100 pt-1.5">
                    <div>Statute: {jurConfig.primary_statute}</div>
                    <div>Regulator: {jurConfig.regulator}</div>
                    <div>Deadline: {jurConfig.access_deadline_days} days</div>
                    <div>Logical Lint: {activeJurisdiction}_rules.json</div>
                  </div>
                </div>
              </div>
            </aside>

            {/* MAIN CONTENT PANEL */}
            <main className="flex-1 p-6 overflow-y-auto space-y-6 bg-[#FAFAFA]">

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
                                <td className="p-3.5 text-blue-600 font-medium">{h.agent}</td>
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
                  
                  {/* P0-1: Summary / Indicators Bar as Clickable Filters */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    
                    <div 
                      onClick={() => setQueueFilter('all')}
                      className={`bg-white border ${queueFilter === 'all' ? 'border-blue-500 ring-1 ring-blue-500' : 'border-[#E5E7EB]'} p-5 rounded-xl shadow-xs space-y-1.5 cursor-pointer transition-all hover:border-blue-300`}
                    >
                      <div className="k-eyebrow">Statutory SLA Clock</div>
                      <div className="flex items-center space-x-2">
                        <Clock size={16} className={`animate-pulse ${jurConfig.code === 'eu' ? 'text-rose-600' : 'text-blue-600'}`} />
                        <span className="k-metric">
                          {jurConfig.code === 'eu' ? '72 Hours' : `${jurConfig.access_deadline_days} Days`}
                        </span>
                      </div>
                      <div className="k-body">
                        {jurConfig.code === 'eu' ? 'Supervisory Authority Notification Window' : `Response deadline for active ${jurConfig.access_request_abbr} requests.`}
                      </div>
                    </div>

                    <div 
                      onClick={() => setQueueFilter('gaps')}
                      className={`bg-white border ${queueFilter === 'gaps' ? 'border-amber-500 ring-1 ring-amber-500' : 'border-[#E5E7EB]'} p-5 rounded-xl shadow-xs space-y-1.5 cursor-pointer transition-all hover:border-amber-300`}
                    >
                      <div className="k-eyebrow">Onboarding Gaps</div>
                      <div className="flex items-center space-x-2">
                        <AlertTriangle size={16} className="text-amber-500" />
                        <span className="k-metric">{onbGaps.filter(g => g.status === 'pending').length} Actionable</span>
                      </div>
                      <div className="k-body">Gaps in organizational profile awaiting validation.</div>
                    </div>

                    <div 
                      onClick={() => setQueueFilter('hitl')}
                      className={`bg-white border ${queueFilter === 'hitl' ? 'border-rose-500 ring-1 ring-rose-500' : 'border-[#E5E7EB]'} p-5 rounded-xl shadow-xs space-y-1.5 cursor-pointer transition-all hover:border-rose-300`}
                    >
                      <div className="k-eyebrow">HITL Queue Tasks</div>
                      <div className="flex items-center space-x-2">
                        <ShieldAlert size={16} className="text-rose-500" />
                        <span className="k-metric">{hitlQueue.filter(h => h.status === 'pending').length} Decisions</span>
                      </div>
                      <div className="k-body">Agent audits and policy overrides pending CPO sign-off.</div>
                    </div>

                    <div 
                      onClick={() => setQueueFilter('inbox')}
                      className={`bg-white border ${queueFilter === 'inbox' ? 'border-blue-500 ring-1 ring-blue-500' : 'border-[#E5E7EB]'} p-5 rounded-xl shadow-xs space-y-1.5 cursor-pointer transition-all hover:border-blue-300`}
                    >
                      <div className="k-eyebrow">Unread Inbox Intake</div>
                      <div className="flex items-center space-x-2">
                        <Mail size={16} className="text-blue-600" />
                        <span className="k-metric">{inboxEmails.filter(e => e.status === 'unread').length} Inquiries</span>
                      </div>
                      <div className="k-body">Direct user requests or regulator letters requiring triage.</div>
                    </div>

                  </div>

                  {/* P0-1: Immediate Attention & Tasks Queue moved to top */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Left & Middle Column: Gaps & Actions */}
                    <div className="lg:col-span-2 space-y-6">
                      
                      {/* Flagged and Pending tasks requiring action */}
                      <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                        <h3 className="k-title flex items-center space-x-2">
                          <Activity size={16} className="text-blue-600" />
                          <span>Immediate Attention & Tasks Queue</span>
                        </h3>
                        
                        <div className="space-y-3">
                          {/* Onboarding Gaps */}
                          {(queueFilter === 'all' || queueFilter === 'gaps') && onbGaps.filter(g => g.status === 'pending').map(g => (
                            <div key={g.id} className="p-3.5 rounded-lg border border-amber-200 bg-amber-50/20 flex justify-between items-center gap-4">
                              <div className="space-y-1">
                                <div className="k-title flex items-center space-x-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                                  <span>{g.title}</span>
                                </div>
                                <div className="k-body">{g.details}</div>
                              </div>
                              {/* P0-3: Inline Action Example - in a full build we would have handleResolveGap here. For now we navigate to the tab as a fallback or if no inline action is specified */}
                              <button
                                onClick={() => setActiveTab('onboarding')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all shadow-xs"
                              >
                                View Details
                              </button>
                            </div>
                          ))}

                          {/* HITL Decisions */}
                          {(queueFilter === 'all' || queueFilter === 'hitl') && hitlQueue.filter(h => h.status === 'pending').map(h => (
                            <div key={h.id} className="p-3.5 rounded-lg border border-rose-200 bg-rose-50/20 flex justify-between items-center gap-4">
                              <div className="space-y-1">
                                <div className="k-title flex items-center space-x-1.5">
                                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
                                  <span>{h.title}</span>
                                </div>
                                <div className="k-body">{h.details}</div>
                              </div>
                              {/* P0-3: Inline approve/resolve */}
                              <div className="flex space-x-2 shrink-0">
                                <button
                                  onClick={() => handleResolveHitlDecision(h.id, 'approved')}
                                  disabled={!isSystemOnline}
                                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md font-semibold transition-all shadow-xs cursor-pointer disabled:opacity-50"
                                >
                                  Approve
                                </button>
                                <button
                                  onClick={() => handleResolveHitlDecision(h.id, 'rejected')}
                                  disabled={!isSystemOnline}
                                  className="bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-md font-semibold transition-all shadow-xs cursor-pointer disabled:opacity-50"
                                >
                                  Reject
                                </button>
                              </div>
                            </div>
                          ))}

                          {((queueFilter === 'all' || queueFilter === 'gaps') && onbGaps.filter(g => g.status === 'pending').length === 0) &&
                           ((queueFilter === 'all' || queueFilter === 'hitl') && hitlQueue.filter(h => h.status === 'pending').length === 0) && (
                            <div className="p-8 text-center text-gray-500 italic k-body">
                              ✓ All actionable items resolved. System is aligned with baseline.
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* P0-1: Jurisdictional High-Priority Indicators demoted below tasks */}
                      <div className="bg-indigo-50/15 border border-indigo-100 p-5 rounded-xl space-y-4">
                        <div className="flex justify-between items-center border-b border-indigo-100 pb-2">
                          <h4 className="k-eyebrow text-indigo-900 flex items-center space-x-1.5">
                            <ShieldAlert size={14} className="text-indigo-650" />
                            <span>Active Jurisdictional Regs ({activeJurisdiction.toUpperCase()})</span>
                          </h4>
                          <span className="text-[11px] font-mono text-indigo-700 bg-indigo-100/50 px-2 py-0.5 rounded border border-indigo-200">
                            Primary Logic: {activeJurisdiction}_rules.json
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {/* EU/GDPR Cards */}
                          {activeJurisdiction === 'eu' && (
                            <>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">Lawful Basis Mapping</span>
                                <div className="k-metric">Consent (64%)</div>
                                <p className="k-body">Continuous RoPA scanning matches operational activities to GDPR lawful bases.</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">Article 28 DPA Status</span>
                                <div className="k-metric text-emerald-700">100% Documented</div>
                                <p className="k-body">All data processors signed Standard Contractual Clauses (SCCs).</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">72-Hour SLA Status</span>
                                <div className="k-metric text-rose-700">0 Breaches Logged</div>
                                <p className="k-body">Statutory notification window monitor to Supervisory Authority is active.</p>
                              </div>
                            </>
                          )}

                          {/* Canada/Law 25 Cards */}
                          {(activeJurisdiction === 'canada' || activeJurisdiction === 'quebec' || activeJurisdiction === 'ontario') && (
                            <>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">Provincial Transfer Restrictions</span>
                                <div className="k-metric text-amber-700">PIAs Pending</div>
                                <p className="k-body">Ontario PHIPA & Quebec Law 25 compliance requirements restrict transfer routes.</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">30-Day DSAR SLA</span>
                                <div className="k-metric">4 Active Countdown</div>
                                <p className="k-body">Strict statutory deadline for response and validation processing.</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">RROSH Breach Threshold</span>
                                <div className="k-metric">Score: 0/10</div>
                                <p className="k-body">Real risk of significant harm calculation triggers automatically.</p>
                              </div>
                            </>
                          )}

                          {/* US/CPRA Cards */}
                          {activeJurisdiction === 'us' && (
                            <>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">Opt-Out of Sale/Sharing</span>
                                <div className="k-metric text-blue-700">89% Opt-Out Rate</div>
                                <p className="k-body">CCPA/CPRA Do Not Sell/Share signals parsed from CMP integration.</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">Sensitive Data Discovery</span>
                                <div className="k-metric">14 SPI Fields Mapped</div>
                                <p className="k-body">Automated classification of sensitive personal information tags.</p>
                              </div>
                              <div className="bg-white border border-[#E5E7EB] p-4 rounded-xl space-y-1.5 shadow-2xs">
                                <span className="k-eyebrow">45-Day SLA Clock</span>
                                <div className="k-metric">1 Active Request</div>
                                <p className="k-body">US State privacy rules govern response deadlines.</p>
                              </div>
                            </>
                          )}
                        </div>
                      </div>

                      {/* LOCALIZED JURISDICTION DASHBOARD MODULES */}
                      {activeLegislations.some(x => ['canada', 'quebec', 'ontario'].includes(x)) && (
                        <div className="space-y-6">
                          
                          {/* RROSH Assessment Tool */}
                          <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                            <h3 className="k-title flex items-center space-x-2">
                              <ShieldAlert size={16} className="text-blue-600" />
                              <span>Canada Breach Triage: RROSH Assessment Builder</span>
                            </h3>
                            <p className="k-body">
                              Assess if a security incident creates a <strong>"Real Risk of Significant Harm"</strong> (RROSH) under PIPEDA or Quebec Law 25.
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50/50 p-4 rounded-xl border border-gray-200">
                              <div className="space-y-1">
                                <span className="k-eyebrow">Harm Sensitivity</span>
                                <div className="k-title">High (Crisis Chat Logs, Medical)</div>
                              </div>
                              <div className="space-y-1 border-t md:border-t-0 md:border-l border-gray-200 pt-2.5 md:pt-0 md:pl-4">
                                <span className="k-eyebrow">Misuse Likelihood</span>
                                <div className="k-title text-amber-600">Possible (Unauthorized Access)</div>
                              </div>
                              <div className="space-y-1 border-t md:border-t-0 md:border-l border-gray-200 pt-2.5 md:pt-0 md:pl-4">
                                <span className="k-eyebrow">RROSH Verdict</span>
                                <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 text-[11px] font-bold border border-rose-200 inline-block mt-0.5">
                                  MANDATORY OPC REPORTING
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Data Transfers and Consent Trackers */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                              <h4 className="k-eyebrow flex items-center space-x-1">
                                <Globe size={14} className="text-purple-650" />
                                <span>Quebec/Canada Data Flow Restrictions</span>
                              </h4>
                              <div className="space-y-2 k-body">
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Aselo/Twilio Chat Route</span>
                                  <span className="text-[11px] font-bold text-rose-600 font-mono">Leaves Quebec (AWS US-East)</span>
                                </div>
                                <div className="flex justify-between border-b border-gray-150 pb-1.5">
                                  <span className="text-gray-600 font-medium">Blackbaud CRM Database</span>
                                  <span className="text-[11px] font-bold text-emerald-600 font-mono">In-Country (Canada East)</span>
                                </div>
                                <div className="text-[11px] text-gray-500 italic">Quebec Law 25 requires a Transfer Impact Assessment (TIA) for out-of-province storage.</div>
                              </div>
                            </div>

                            <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                              <h4 className="k-eyebrow">Clear Consent Opt-In Track</h4>
                              <div className="space-y-2">
                                <div className="flex justify-between items-center k-body">
                                  <span className="text-gray-500 font-semibold">Express Sensitive Opt-In</span>
                                  <span className="font-bold text-blue-600">89.4%</span>
                                </div>
                                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                                  <div className="bg-blue-600 h-full w-[89.4%]" />
                                </div>
                                <div className="flex justify-between items-center k-body pt-1">
                                  <span className="text-gray-500 font-semibold">Implied Marketing Opt-Out</span>
                                  <span className="font-bold text-amber-600">12.1%</span>
                                </div>
                              </div>
                            </div>

                          </div>
                        </div>
                      )}

                      {/* PHIPA Specific Health Custodian Panel */}
                      {activeLegislations.includes('phipa') && (
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h3 className="k-title flex items-center space-x-2">
                            <Activity size={16} className="text-emerald-600" />
                            <span>Ontario PHIPA: Health Information Custodian (HIC) Registry</span>
                          </h3>
                          <p className="k-body">
                            Ensures strict Circle of Care limits are maintained when clinical therapists handle personal health information (PHI).
                          </p>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-3.5 bg-emerald-50/20 border border-emerald-250 rounded-lg">
                              <div className="k-eyebrow text-emerald-800">Circle of Care Disclosures</div>
                              <div className="k-body font-semibold mt-1">Limited to authorized clinical supervisors</div>
                            </div>
                            <div className="p-3.5 bg-gray-50 border border-gray-200 rounded-lg">
                              <div className="k-eyebrow">HIC Safety Audits</div>
                              <div className="k-body font-semibold mt-1">Passed (Transcripts fully encrypted at rest)</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* CYFSA Specific Youth Consent Panel */}
                      {activeLegislations.includes('cyfsa') && (
                        <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                          <h3 className="k-title flex items-center space-x-2">
                            <UserCheck size={16} className="text-purple-600" />
                            <span>Ontario CYFSA: Child & Youth Capacity Boundaries</span>
                          </h3>
                          <p className="k-body">
                            Under the Child, Youth and Family Services Act, service users under the age of 16 possess explicit self-consent capacity for mental health assistance.
                          </p>
                          <div className="p-4 bg-purple-50/20 border border-purple-200 rounded-lg flex justify-between items-center">
                            <div>
                              <div className="k-title text-purple-950">Youth Self-Consent Capacity</div>
                              <div className="k-body text-purple-750">Self-consent capacity boundary: 16 years of age</div>
                            </div>
                            <span className="bg-purple-100 text-purple-800 border border-purple-250 k-eyebrow px-2 py-0.5 rounded">
                              ENFORCED AT GATEWAY
                            </span>
                          </div>
                        </div>
                      )}

                      {activeLegislations.includes('us') && (
                        <div className="space-y-6">
                          
                          {/* Multi-State Compliance Scorecard */}
                          <div className="bg-white border border-[#E5E7EB] p-6 rounded-xl space-y-4 shadow-xs">
                            <h3 className="k-title flex items-center space-x-2">
                              <Globe size={16} className="text-blue-600" />
                              <span>Multi-State Privacy Matrix (US State Legislation)</span>
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              {['California (CPRA)', 'Virginia (VCDPA)', 'Colorado (CPA)', 'Utah (UCPA)'].map((st, idx) => (
                                <div key={idx} className="border border-gray-200 rounded-lg p-3 text-center">
                                  <div className="text-lg mb-1">{idx === 3 ? '⏳' : '✓'}</div>
                                  <div className="k-eyebrow">{st}</div>
                                  <div className="k-body text-xs text-gray-500 mt-1">{idx === 3 ? 'Taking Effect 12/31' : 'Active & Mapped'}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                    </div>

                    {/* Right Column: Threats & Orchestration */}
                    <div className="space-y-6">
                      
                      {/* Section: Live Threat Intelligence */}
                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                        <h2 className="k-eyebrow flex items-center space-x-1.5">
                          <AlertCircle size={14} className="text-rose-600" />
                          <span>Live Threat Intelligence</span>
                        </h2>
                        <div className="space-y-2">
                          <button 
                            className="w-full text-left p-2 rounded-lg bg-gray-50 border border-gray-200 hover:border-gray-300 transition-all flex justify-between items-center"
                            onClick={() => setActiveTab('assessments')}
                          >
                            <span className="k-body">⚠️ Third-Party Sync Delay</span>
                            <ChevronDown size={14} className="text-gray-400" />
                          </button>
                          <button 
                            className="w-full text-left p-2 rounded-lg bg-rose-50 border border-rose-200 hover:border-rose-300 transition-all flex justify-between items-center"
                            onClick={() => setActiveTab('assessments')}
                          >
                            <span className="k-body text-rose-800">🚨 SIEM Data Anomaly Detected</span>
                            <ChevronDown size={14} className="text-gray-400" />
                          </button>
                        </div>
                      </div>

                      {/* Section: Live Trace Console */}
                      <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-3 shadow-xs">
                        <h2 className="k-eyebrow flex items-center space-x-1.5">
                          <Terminal size={14} className="text-blue-600" />
                          <span>Orchestration Loop Trace</span>
                        </h2>
                        <div className="bg-gray-900 text-emerald-400 p-4 rounded-lg font-mono text-[11px] h-48 overflow-y-auto space-y-1.5 shadow-inner">
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

                </div>
              )}

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
                                <td className="p-3.5 text-blue-600 font-medium">{h.agent}</td>
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
                                <div className="text-[10px] text-gray-500 leading-relaxed">{g.details}</div>
                              </div>
                              <button
                                onClick={() => setActiveTab('onboarding')}
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-500 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all shadow-xs"
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
                                className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-500 text-[10px] font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all shadow-xs"
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
                              <ShieldAlert size={14} className="text-blue-600" />
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
                              <Globe size={14} className="text-blue-600" />
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
                                <BookOpen size={12} className="text-blue-600" />
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
                                <span className="text-[9px] bg-blue-50 border border-blue-200 text-blue-600 px-2 py-0.5 rounded-full font-bold">{a.type}</span>
                              </div>
                              <div className="text-[10px] text-gray-500">Prepared by: {a.prepared_by} | Level: {a.level}</div>
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
                              if (res.ok) addToast("Audit session initialized on the blockchain ledger.", "info");
                            }}
                            className="w-full text-left bg-white hover:bg-gray-500 text-gray-700 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
                          >
                            <span>Run Blockchain Activities Audit</span>
                            <span className="text-[9px] text-gray-400 font-mono">POST /audit</span>
                          </button>

                          <button
                            onClick={async () => {
                              const res = await kiboFetch(`${API_BASE}/api/expert/soc-compliance`, { method: 'POST' });
                              if (res.ok) {
                                const data = await res.json();
                                addToast(`SOC Compliance Scan Status: ${data.status}`, "info");
                              }
                            }}
                            className="w-full text-left bg-white hover:bg-gray-500 text-gray-700 border border-[#E5E7EB] px-4 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer shadow-xs flex justify-between items-center"
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
                                <label className="text-[10px] font-bold text-gray-500 uppercase">Target Domain</label>
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
                                <label className="text-[10px] font-bold text-gray-500 uppercase">Lesson / Constraint Notes</label>
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
                                    <span className="text-indigo-800 font-mono">ID: {lesson.lesson_id}</span>
                                    <span className="uppercase bg-indigo-100/50 border border-indigo-200 text-indigo-800 px-2 py-0.5 rounded-md">
                                      Domain: {lesson.domain}
                                    </span>
                                  </div>
                                  <p className="text-xs text-gray-700 font-mono italic">"{lesson.feedback_notes}"</p>
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
                          <p className="text-[11px] text-gray-500 leading-relaxed">
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
                                  className="w-full bg-white border border-gray-300 rounded-lg p-2 text-xs text-gray-700 font-semibold focus:ring-1 focus:ring-blue-500 focus:outline-hidden"
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
                              <label className="text-[10px] font-bold text-gray-500 uppercase">LangGraph Cyclic Output Log</label>
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
                              onClick={() => addToast(`Escalated email thread ${selectedEmail.email_id} to Legal counsel.`, "info")}
                              className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-bold px-3 py-1.5 rounded-lg uppercase text-[9px] tracking-wider transition-all cursor-pointer"
                            >
                              Escalate to Legal
                            </button>
                            <button
                              onClick={() => addToast(`Flagged email thread ${selectedEmail.email_id} as Spam/Safe-Ignore.`, "info")}
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
                                className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-4 py-2 rounded-lg uppercase text-[9px] tracking-wider shadow-sm transition-all cursor-pointer"
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
                    <CommissionerLinks />
                  </div>

                  {/* Right: Record Minutes Panel */}
                  <div className="bg-white border border-[#E5E7EB] p-5 rounded-xl space-y-4 shadow-xs">
                    {selectedMeetingId ? (
                      <div className="space-y-4 text-xs">
                        <div className="text-blue-600 font-bold uppercase tracking-wider">Record Meeting Minutes & Action Items ({selectedMeetingId})</div>
                        
                        <div>
                          <label className="block text-[10px] text-gray-500 font-semibold uppercase mb-1">Meeting Minutes Summary</label>
                          <textarea 
                            value={meetingMinutes}
                            onChange={(e) => setMeetingMinutes(e.target.value)}
                            placeholder="Provide meeting summary here..."
                            className="w-full bg-white border border-[#E5E7EB] focus:border-blue-600 focus:ring-2 focus:ring-blue-500/20 p-2.5 text-xs text-[#111827] rounded-lg h-24 resize-none transition-all shadow-xs"
                          />
                        </div>

                        {/* Action items builder */}
                        <div className="space-y-3.5 border-t border-[#E5E7EB] pt-4">
                          <label className="block text-[10px] text-gray-500 font-semibold uppercase">Add Action Item</label>
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
                              className="bg-white hover:bg-gray-500 text-gray-700 px-4 text-xs rounded-lg border border-[#E5E7EB] transition-all cursor-pointer shadow-xs"
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
                            className="bg-white hover:bg-gray-500 text-gray-700 border border-[#E5E7EB] px-3 py-2 rounded text-[10px] shadow-xs"
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
                          <div className="text-[10px] text-gray-500 mt-1 uppercase font-medium">Completion Rate</div>
                        </div>
                        <div className="bg-gray-50 p-4 border border-[#E5E7EB] rounded-xl">
                          <div className="text-xl font-bold text-[#111827]">{trainingCompliance.completed_modules} / {trainingCompliance.total_modules}</div>
                          <div className="text-[10px] text-gray-500 mt-1 uppercase font-medium">Modules Complete</div>
                        </div>
                        <div className="bg-gray-50 p-4 border border-[#E5E7EB] rounded-xl">
                          <div className="text-xl font-bold text-rose-650">{trainingCompliance.overdue_staff_count}</div>
                          <div className="text-[10px] text-gray-500 mt-1 uppercase font-medium">Overdue Reminders</div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-gray-450 italic">Loading compliance data...</div>
                    )}

                    <div className="flex space-x-3 pt-2">
                      <button
                        onClick={() => handleTriggerTrainingAction('assign')}
                        className="flex-1 bg-white hover:bg-gray-500 text-gray-700 border border-[#E5E7EB] py-2.5 rounded-lg text-xs uppercase font-medium transition-all cursor-pointer shadow-xs"
                      >
                        Reset & Assign Courses
                      </button>
                      <button
                        onClick={() => handleTriggerTrainingAction('remind')}
                        className="flex-1 bg-white hover:bg-gray-500 text-gray-700 border border-[#E5E7EB] py-2.5 rounded-lg text-xs uppercase font-medium transition-all cursor-pointer shadow-xs"
                      >
                        Send Overdue Reminders
                      </button>
                    </div>
                    <p className="text-xs text-gray-600 mt-2">Our company policy mandates that each employee complete annual privacy training. The following official resources provide the required material.</p>
                    <div className="mt-4">
                      <h3 className="text-sm font-bold uppercase text-gray-800 mb-2">Training Resources</h3>
                      <ul className="list-disc list-inside text-xs text-blue-600">
                        <li><a href="https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/" target="_blank" rel="noopener noreferrer" className="underline">PIPEDA Overview</a></li>
                        <li><a href="https://www.cai.gouv.qc.ca/en/" target="_blank" rel="noopener noreferrer" className="underline">Quebec CAI (Law 25)</a></li>
                        <li><a href="https://www.fightspam.gc.ca" target="_blank" rel="noopener noreferrer" className="underline">CASL Official Portal</a></li>
                        <li><a href="https://www.ftc.gov/business-guidance/privacy-security" target="_blank" rel="noopener noreferrer" className="underline">FTC Privacy Guidance (US)</a></li>
                      </ul>
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
                                  <tr key={t.id} className="hover:bg-gray-500/50 transition-all">
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
                                            className="bg-emerald-600 text-white px-3 py-1 rounded text-[10px] font-bold cursor-pointer shadow-xs"
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
                                  <tr key={c.id} className="hover:bg-gray-500/50 transition-all">
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
                                  <span className="font-semibold text-blue-600">{d.jurisdiction}</span>
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
                            <div className="text-xl font-extrabold text-blue-600">{onbProfile ? onbProfile.completeness_pct : 0}%</div>
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
                                  <FileUp size={18} className="mx-auto text-blue-600 mb-1" />
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
                                <Network size={14} className="text-blue-600" />
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
                                      <div className="text-[9px] text-gray-500 leading-normal">Crawl codebase to detect new trackers & cookies dynamically.</div>
                                    </div>
                                    <div className="p-3 bg-white border border-rose-200 rounded-xl space-y-1 text-center">
                                      <div className="text-[10px] font-bold text-rose-800 uppercase">Enforce Opt-Outs</div>
                                      <div className="text-[9px] text-gray-500 leading-normal">Block unauthorized pixels and update compliance records.</div>
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
                                        <tr key={idx} className="hover:bg-gray-500/50">
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
            </main>
          </div>
  );
};

export default ExpertMode;
