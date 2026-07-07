const fs = require('fs');

const code = fs.readFileSync('App.jsx', 'utf8');
const lines = code.split('\n');

const startIndex = lines.findIndex(l => l.includes("{/* EXPERT MODE */}"));
const endIndex = lines.findIndex((l, i) => i > startIndex && l.includes("{/* PSR COMMITTEE MODE */}"));

if (startIndex !== -1 && endIndex !== -1) {
  const expertLines = lines.slice(startIndex + 1, endIndex - 1);
  let jsx = expertLines.slice(1, -1).join('\n');
  
  const fileContent = `import React from 'react';
import { 
  ShieldCheck, AlertTriangle, FileCheck, CheckSquare, ListChecks, ArrowUpRight, Check, Activity, Search,
  Server, Cpu, Database, Eye, Terminal, FileText, Lock, Globe, Shield, RefreshCw, Layers, Inbox, AlertCircle, Sparkles, Plus, Clock, Key
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend, LineChart, Line } from 'recharts';
import PrivacyInbox from '../components/PrivacyInbox';
import ComplianceCoverageMap from '../components/ComplianceCoverageMap';
import OntologyVisualizer from '../components/OntologyVisualizer';
import JurisdictionSelector from '../components/JurisdictionSelector';
import MetricCard from '../components/MetricCard';
import ProgressRing from '../components/ProgressRing';
import SimulationDashboard from '../components/SimulationDashboard';
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
    lessonsIsExpanded, setLessonsIsExpanded, agentLessons
  } = props;

  return (
${jsx}
  );
};

export default ExpertMode;
`;

  fs.writeFileSync('modes/ExpertMode.jsx', fileContent);
  console.log("ExpertMode extracted.");
} else {
  console.log("Could not find boundaries", startIndex, endIndex);
}
