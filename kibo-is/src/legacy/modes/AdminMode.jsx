import React from 'react';
import AdminDashboard from '../AdminDashboard';

const AdminMode = (props) => {
  const {
    API_BASE, activeJurisdiction, jurConfig, legalLibrary, agentLessons,
    fetchLessons, fetchLegalLibrary, simLogs, simIsRunning, setSimLogs, setSimIsRunning
  } = props;

  return (
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
  );
};

export default AdminMode;
