const fs = require('fs');

const code = fs.readFileSync('App.jsx', 'utf8');
const lines = code.split('\n');

const startIndex = lines.findIndex(l => l.includes("{/* EXPERT MODE */}"));
const endIndex = lines.findIndex((l, i) => i > startIndex && l.includes("{/* PSR COMMITTEE MODE */}"));

if (startIndex !== -1 && endIndex !== -1) {
  const newContent = [
    ...lines.slice(0, startIndex + 1),
    `        {securityMode === 'expert' && (`,
    `          <ExpertMode `,
    `            activeTab={activeTab} setActiveTab={setActiveTab} activeJurisdiction={activeJurisdiction} jurConfig={jurConfig} setSecurityMode={setSecurityMode} setAdminDiffMode={setAdminDiffMode}`,
    `            expertAssessments={expertAssessments} expertMeetings={expertMeetings} expertInbox={expertInbox} expertComplianceTraining={expertComplianceTraining}`,
    `            onboardingTasks={onboardingTasks} onbGaps={onbGaps} handleOnbGapSubmit={handleOnbGapSubmit} newGapDesc={newGapDesc} setNewGapDesc={setNewGapDesc} newGapSev={newGapSev} setNewGapSev={setNewGapSev}`,
    `            onboardingCasl={onboardingCasl} handleOnboardingTaskToggle={handleOnboardingTaskToggle} handleOnboardingNotesSave={handleOnboardingNotesSave}`,
    `            editingTaskId={editingTaskId} setEditingTaskId={setEditingTaskId} editTaskNotes={editTaskNotes} setEditTaskNotes={setEditTaskNotes}`,
    `            handleOnboardingCaslSunset={handleOnboardingCaslSunset} simLogs={simLogs} simIsRunning={simIsRunning}`,
    `            complianceProgress={complianceProgress} riskScore={riskScore} riskTrend={riskTrend} assessmentCoverage={assessmentCoverage} openIssues={openIssues}`,
    `            employeeDataFlows={employeeDataFlows} thirdPartyDataFlows={thirdPartyDataFlows} activeThreats={activeThreats} recentAudits={recentAudits} complianceTrendData={complianceTrendData}`,
    `            expertExpandedAssessments={expertExpandedAssessments} toggleExpertAssessment={toggleExpertAssessment} onboardingSubMode={onboardingSubMode} setOnboardingSubMode={setOnboardingSubMode}`,
    `            lessonsIsExpanded={lessonsIsExpanded} setLessonsIsExpanded={setLessonsIsExpanded} agentLessons={agentLessons}`,
    `          />`,
    `        )}`,
    ...lines.slice(endIndex)
  ];
  
  fs.writeFileSync('App.jsx', newContent.join('\n'));
  console.log("App.jsx updated with ExpertMode component.");
} else {
  console.log("Could not find boundaries", startIndex, endIndex);
}
