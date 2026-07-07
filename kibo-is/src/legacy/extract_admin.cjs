const fs = require('fs');

const code = fs.readFileSync('kibo-is/src/legacy/App.jsx', 'utf8');
const lines = code.split('\n');

const startIndex = lines.findIndex(l => l.includes("{/* ADMIN DASHBOARD */}"));
const modeStartLine = lines.findIndex((l, i) => i > startIndex && l.includes("{securityMode === 'admin' && ("));

let openCount = 0;
let modeEndLine = -1;
for (let i = modeStartLine; i < lines.length; i++) {
  const l = lines[i];
  openCount += (l.match(/\(/g) || []).length;
  openCount -= (l.match(/\)/g) || []).length;
  
  if (openCount === 0 && l.includes(")}")) {
     modeEndLine = i;
     break;
  }
}

if (modeStartLine !== -1 && modeEndLine !== -1) {
  const jsx = lines.slice(modeStartLine + 1, modeEndLine).join('\n');
  
  const fileContent = `import React from 'react';

const AdminMode = (props) => {
  const {
    adminMode, adminDiffMode, setAdminDiffMode, deployPhase, setDeployPhase, 
    handleAdminCutover, setAdminMode
  } = props;

  return (
${jsx}
  );
};

export default AdminMode;
`;

  fs.writeFileSync('kibo-is/src/legacy/modes/AdminMode.jsx', fileContent);
  console.log("AdminMode extracted.");
  
  const newContent = [
    ...lines.slice(0, modeStartLine),
    `        {securityMode === 'admin' && (`,
    `          <AdminMode `,
    `            adminMode={adminMode} adminDiffMode={adminDiffMode} setAdminDiffMode={setAdminDiffMode} deployPhase={deployPhase} setDeployPhase={setDeployPhase}`,
    `            handleAdminCutover={handleAdminCutover} setAdminMode={setAdminMode}`,
    `          />`,
    `        )}`,
    ...lines.slice(modeEndLine + 1)
  ];
  
  fs.writeFileSync('kibo-is/src/legacy/App.jsx', newContent.join('\n'));
  console.log("App.jsx updated with AdminMode component.");

}
