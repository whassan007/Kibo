const fs = require('fs');

const code = fs.readFileSync('App.jsx', 'utf8');
const lines = code.split('\n');

const startIndex = lines.findIndex(l => l.includes("{/* EXPERT MODE */}"));
const endIndex = lines.findIndex((l, i) => i > startIndex && l.includes("{/* PSR COMMITTEE MODE */}"));

if (startIndex !== -1 && endIndex !== -1) {
  const expertLines = lines.slice(startIndex + 1, endIndex - 1);
  // remove the surrounding condition `{securityMode === 'expert' && (` and the closing `)}`
  // expertLines starts at index 1 of the block.
  // Actually let's just grab the JSX inside the parens.
  // The first line is `{securityMode === 'expert' && (` -> we want from index 2
  // The last line is `)}` -> we want up to expertLines.length - 1

  let jsx = expertLines.slice(1, -1).join('\n');
  
  // We need to figure out all props required for ExpertMode.
  // This is hard to do perfectly via AST without Babel, so we'll just pass a `props` object.
  // Wait, if we just pass `props` object we can spread it.

  const fileContent = `import React from 'react';
import { 
  ShieldCheck, AlertTriangle, FileCheck, CheckSquare, ListChecks, ArrowUpRight, Check, Activity, Search,
  Server, Cpu, Database, Eye, Terminal, FileText, Lock, Globe, Shield, RefreshCw, Layers, Inbox, AlertCircle, Sparkles, Plus, Clock, Key
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Legend, LineChart, Line } from 'recharts';
import PrivacyInbox from './PrivacyInbox';
import ComplianceCoverageMap from './ComplianceCoverageMap';
import OntologyVisualizer from './OntologyVisualizer';
import JurisdictionSelector from '../components/JurisdictionSelector';
import MetricCard from '../components/MetricCard';
import ProgressRing from '../components/ProgressRing';
import SimulationDashboard from '../components/SimulationDashboard';
import ShadowRiskFeed from '../components/ShadowRiskFeed';
import ScopeActiveLegislations from '../components/ScopeActiveLegislations';
import CommissionerLinks from '../components/CommissionerLinks';

const ExpertMode = (props) => {
  // Destructure everything from props for convenience
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
