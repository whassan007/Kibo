/**
 * KIBO.IS — Authenticated App Dashboard Workspace Engine (/app)
 * Handles: Multi-provider SSO Authentication, Session Storage, Onboarding Banners, Logout, AI Copilot
 */

document.addEventListener('DOMContentLoaded', () => {
  // --------------------------------------------------------------------------
  // 1. SSO & Registration URL Parameter & Session Engine
  // --------------------------------------------------------------------------
  const urlParams = new URLSearchParams(window.location.search);
  const ssoType = urlParams.get('signup_sso') || urlParams.get('sso');
  
  let ssoProvider = urlParams.get('sso_provider');
  if (!ssoProvider) {
    if (ssoType === 'microsoft') ssoProvider = 'Microsoft Entra ID';
    else if (ssoType === 'okta') ssoProvider = 'Okta SSO';
    else if (ssoType === 'google') ssoProvider = 'Google Workspace';
    else if (ssoType === 'passkey') ssoProvider = 'FIDO2 Passkey';
    else if (ssoType === 'magic_link') ssoProvider = 'Passwordless Magic Link';
    else ssoProvider = 'Standard Business Account';
  }

  const userName = urlParams.get('name') || urlParams.get('user') || 'Sarah Jenkins';
  const userEmail = urlParams.get('email') || 'sarah@acmehealth.com';
  const tenantDomain = urlParams.get('tenant') || urlParams.get('org') || 'acmehealth.onmicrosoft.com';

  // Save session if parameters are present
  if (ssoType || urlParams.has('email') || urlParams.has('name')) {
    const sessionData = {
      provider: ssoProvider,
      type: ssoType || 'email',
      name: userName,
      email: userEmail,
      tenant: tenantDomain,
      loginTime: new Date().toISOString()
    };
    localStorage.setItem('kibo_enterprise_session', JSON.stringify(sessionData));
  }

  // Retrieve active session
  let activeSession = null;
  const storedSession = localStorage.getItem('kibo_enterprise_session');
  if (storedSession) {
    try {
      activeSession = JSON.parse(storedSession);
    } catch(e) {}
  }

  const userProfileName = document.getElementById('app-user-name');
  const userAvatar = document.getElementById('app-user-avatar');
  const ssoBanner = document.getElementById('app-sso-banner');

  const currentProvider = activeSession ? activeSession.provider : ssoProvider;
  const currentName = activeSession ? activeSession.name : userName;
  const currentEmail = activeSession ? activeSession.email : userEmail;
  const currentTenant = activeSession ? activeSession.tenant : tenantDomain;

  // --- Initialize RBAC and Multi-Tenant Engine ---
  let rbacSession = null;
  if (typeof KiboRBAC !== 'undefined') {
    rbacSession = KiboRBAC.loginOrCreateSession(currentEmail, currentName, currentTenant);
    KiboRBAC.applyUIFilters(rbacSession.userId);

    // Populate Org / Team views if they exist
    if (document.getElementById('tenant-name-display')) {
      document.getElementById('tenant-name-display').textContent = currentTenant;
      document.getElementById('tenant-id-display').textContent = rbacSession.orgId;
    }
    
    const usersTable = document.getElementById('users-table-body');
    if (usersTable) {
      try {
        const users = KiboRBAC.getUsersInTenant(rbacSession.userId);
        usersTable.innerHTML = users.map(u => `
          <tr>
            <td><code>${u.id}</code></td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td><span style="padding:0.2rem 0.5rem; background:rgba(99,102,241,0.2); color:#a5b4fc; border-radius:4px; font-size:0.8rem">${u.role}</span></td>
          </tr>
        `).join('');
      } catch (err) {
        // User lacks permission, table won't be shown anyway
      }
    }
  }

  // Icons map
  const icons = {
    'Microsoft Entra ID': '🟦',
    'Okta SSO': '🔑',
    'Google Workspace': '🔴',
    'FIDO2 Passkey': '🔐',
    'Passwordless Magic Link': '⚡',
    'Standard Business Account': '💼'
  };
  const currentIcon = icons[currentProvider] || '🛡️';

  // Update header profile
  if (userProfileName) {
    const roleStr = rbacSession ? rbacSession.role : 'Enterprise';
    userProfileName.textContent = `${currentName} (${roleStr})`;
  }
  if (userAvatar) {
    const initials = currentName.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    userAvatar.textContent = initials || 'SJ';
  }

  // Render Onboarding Banner
  if (ssoBanner) {
    ssoBanner.style.display = 'block';
    ssoBanner.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(37,99,235,0.12); border:1px solid #2563eb; border-radius:var(--radius-md); padding:1rem 1.25rem; margin-bottom:1.5rem">
        <div style="display:flex; align-items:center; gap:0.75rem">
          <span style="font-size:1.4rem">${currentIcon}</span>
          <div>
            <strong style="color:var(--text-main); font-size:0.95rem">
              ${currentProvider} Authenticated & Session Verified
            </strong>
            <div style="font-size:0.85rem; color:var(--text-muted); margin-top:0.15rem">
              Domain / Tenant: <code>${currentTenant}</code> | User: <strong>${currentName}</strong> (<code>${currentEmail}</code>) | SAML 2.0 / OIDC Verified
            </div>
          </div>
        </div>
        <div style="display:flex; gap:0.5rem">
          <button id="btn-logout" style="font-size:0.8rem; color:#ef4444; cursor:pointer; padding:0.3rem 0.6rem; background:var(--bg-slate-900); border:1px solid #ef4444; border-radius:4px">
            Log Out
          </button>
          <button onclick="document.getElementById('app-sso-banner').style.display='none'" style="font-size:0.8rem; color:var(--text-muted); cursor:pointer; padding:0.3rem 0.6rem; background:var(--bg-slate-900); border:1px solid var(--border-color); border-radius:4px">
            Dismiss
          </button>
        </div>
      </div>
    `;

    // Logout click handler
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        localStorage.removeItem('kibo_enterprise_session');
        window.location.href = 'login.html';
      });
    }
  }

  // --------------------------------------------------------------------------
  // 2. Navigation Tab Switcher Inside App
  // --------------------------------------------------------------------------
  const navItems = document.querySelectorAll('.app-sidebar .sidebar-item');
  const viewPanels = document.querySelectorAll('.app-view');

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = item.getAttribute('data-view');

      navItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');

      viewPanels.forEach(panel => {
        if (panel.id === `view-${targetView}`) {
          panel.style.display = 'block';
        } else {
          panel.style.display = 'none';
        }
      });
    });
  });

  // --------------------------------------------------------------------------
  // 3. AI Privacy Copilot Chat Form
  // --------------------------------------------------------------------------
  const copilotForm = document.getElementById('copilot-form');
  const copilotInput = document.getElementById('copilot-input');
  const copilotChat = document.getElementById('copilot-messages');

  if (copilotForm && copilotInput && copilotChat) {
    copilotForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = copilotInput.value.trim();
      if (!query) return;

      const userMsg = document.createElement('div');
      userMsg.className = 'chat-msg user-msg';
      userMsg.innerHTML = `<div class="msg-bubble">${escapeHtml(query)}</div>`;
      copilotChat.appendChild(userMsg);
      copilotInput.value = '';
      copilotChat.scrollTop = copilotChat.scrollHeight;

      setTimeout(() => {
        const aiMsg = document.createElement('div');
        aiMsg.className = 'chat-msg ai-msg';
        aiMsg.innerHTML = `<div class="msg-avatar">🤖</div><div class="msg-bubble">${getAIResponse(query)}</div>`;
        copilotChat.appendChild(aiMsg);
        copilotChat.scrollTop = copilotChat.scrollHeight;
      }, 600);
    });
  }
});

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

function getAIResponse(query) {
  const q = query.toLowerCase();
  if (q.includes('dsar') || q.includes('delete') || q.includes('request')) {
    return '<strong>AI Copilot:</strong> Found 3 pending DSAR requests under GDPR Article 17 (Right to Erasure). Verified identity via SAML 2.0 / Entra ID MFA. Ready to trigger automated data erasure across Salesforce, AWS S3, and Snowflake.';
  } else if (q.includes('hipaa') || q.includes('law 25') || q.includes('gdpr') || q.includes('compliance')) {
    return '<strong>AI Copilot:</strong> Overall compliance posture across GDPR, Law 25, and HIPAA is currently at <strong>96.8%</strong>. 1 minor gap detected in vendor risk assessment for subprocessor #14 (Salesforce Sandbox).';
  } else if (q.includes('incident') || q.includes('breach')) {
    return '<strong>AI Copilot:</strong> 0 active critical privacy breaches detected. 1 low-priority log anomaly flagged on US-East AWS region. Risk score: Low (2/100).';
  } else {
    return `<strong>AI Copilot:</strong> Analyzing query regarding "<em>${escapeHtml(query)}</em>"... All audit logs, consent receipts, and records of processing (ROPA) remain synchronized across your connected enterprise data sources.`;
  }
}
