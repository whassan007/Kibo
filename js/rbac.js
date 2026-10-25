/**
 * KIBO.IS — Enterprise RBAC & Multi-Tenant Identity Engine
 * Simulates backend authorization, tenant isolation, and UI permission filtering.
 */

const KiboRBAC = (function() {
  // --- 1. RBAC & Permission Data Model ---
  const PERMISSIONS = {
    ORG_MANAGE: 'organization.manage',
    USERS_CREATE: 'users.create',
    USERS_UPDATE: 'users.update',
    USERS_DELETE: 'users.delete',
    USERS_INVITE: 'users.invite',
    ROLES_ASSIGN: 'roles.assign',
    CASES_READ: 'cases.read',
    CASES_WRITE: 'cases.write',
    DSAR_MANAGE: 'dsar.manage',
    INCIDENTS_MANAGE: 'incidents.manage',
    REPORTS_VIEW: 'reports.view',
    AUDIT_VIEW: 'audit.view',
    SETTINGS_MANAGE: 'settings.manage'
  };

  const ROLES = {
    SUPER_ADMIN: [
      PERMISSIONS.ORG_MANAGE, PERMISSIONS.USERS_CREATE, PERMISSIONS.USERS_UPDATE, 
      PERMISSIONS.USERS_DELETE, PERMISSIONS.USERS_INVITE, PERMISSIONS.ROLES_ASSIGN,
      PERMISSIONS.CASES_READ, PERMISSIONS.CASES_WRITE, PERMISSIONS.DSAR_MANAGE,
      PERMISSIONS.INCIDENTS_MANAGE, PERMISSIONS.REPORTS_VIEW, PERMISSIONS.AUDIT_VIEW,
      PERMISSIONS.SETTINGS_MANAGE
    ],
    PRIVACY_ADMIN: [
      PERMISSIONS.CASES_READ, PERMISSIONS.CASES_WRITE, PERMISSIONS.DSAR_MANAGE,
      PERMISSIONS.INCIDENTS_MANAGE, PERMISSIONS.REPORTS_VIEW, PERMISSIONS.AUDIT_VIEW
    ],
    DPO: [
      PERMISSIONS.CASES_READ, PERMISSIONS.DSAR_MANAGE, PERMISSIONS.INCIDENTS_MANAGE,
      PERMISSIONS.REPORTS_VIEW, PERMISSIONS.AUDIT_VIEW
    ],
    PRIVACY_ANALYST: [
      PERMISSIONS.CASES_READ, PERMISSIONS.CASES_WRITE, PERMISSIONS.DSAR_MANAGE,
      PERMISSIONS.INCIDENTS_MANAGE
    ],
    LEGAL_COUNSEL: [
      PERMISSIONS.CASES_READ, PERMISSIONS.REPORTS_VIEW, PERMISSIONS.AUDIT_VIEW
    ],
    EMPLOYEE: [
      PERMISSIONS.CASES_READ
    ]
  };

  // --- 2. In-Memory Database Simulation ---
  let db = {
    organizations: {},
    users: {}
  };

  function loadDB() {
    const saved = localStorage.getItem('kibo_enterprise_db');
    if (saved) db = JSON.parse(saved);
  }

  function saveDB() {
    localStorage.setItem('kibo_enterprise_db', JSON.stringify(db));
  }

  // --- 3. Core Engine API ---
  return {
    init: function() {
      loadDB();
    },

    provisionTenant: function(userName, userEmail, orgName) {
      loadDB();
      const orgId = 'org_' + Math.random().toString(36).substr(2, 9);
      const userId = 'usr_' + Math.random().toString(36).substr(2, 9);

      // 1. Create Organization (Tenant Isolation)
      db.organizations[orgId] = {
        id: orgId,
        name: orgName,
        createdAt: new Date().toISOString(),
        settings: {
          jurisdictions: ['US', 'EU', 'CA'],
          ssoEnabled: false
        }
      };

      // 2. Provision Super Administrator
      db.users[userId] = {
        id: userId,
        orgId: orgId,
        name: userName,
        email: userEmail,
        role: 'SUPER_ADMIN',
        status: 'ACTIVE'
      };

      saveDB();
      return { orgId, userId };
    },

    getUser: function(userId) {
      return db.users[userId];
    },

    hasPermission: function(userId, permission) {
      const user = db.users[userId];
      if (!user) return false;
      const rolePerms = ROLES[user.role] || [];
      return rolePerms.includes(permission);
    },

    getUsersInTenant: function(callerUserId) {
      const caller = db.users[callerUserId];
      if (!caller) throw new Error("Unauthorized");
      if (!this.hasPermission(callerUserId, PERMISSIONS.ORG_MANAGE)) {
        throw new Error("Missing users.read permission");
      }
      
      // Strict Tenant Isolation Enforcement
      return Object.values(db.users).filter(u => u.orgId === caller.orgId);
    },

    inviteUser: function(callerUserId, newEmail, newName, role) {
      const caller = db.users[callerUserId];
      if (!caller) throw new Error("Unauthorized");
      if (!this.hasPermission(callerUserId, PERMISSIONS.USERS_INVITE)) {
        throw new Error("Missing users.invite permission");
      }
      if (!ROLES[role]) throw new Error("Invalid Role");

      const newUserId = 'usr_' + Math.random().toString(36).substr(2, 9);
      db.users[newUserId] = {
        id: newUserId,
        orgId: caller.orgId, // Strict isolation (must match inviter's org)
        name: newName,
        email: newEmail,
        role: role,
        status: 'INVITED'
      };
      saveDB();
      return newUserId;
    },

    applyUIFilters: function(userId) {
      // Find all DOM elements requiring a specific permission
      document.querySelectorAll('[data-permission]').forEach(el => {
        const requiredPerm = el.getAttribute('data-permission');
        if (!this.hasPermission(userId, requiredPerm)) {
          el.style.display = 'none'; // Hide unauthorized navigation or actions
        } else {
          el.style.display = '';
        }
      });
    },

    loginOrCreateSession: function(email, name, orgName) {
      loadDB();
      let user = Object.values(db.users).find(u => u.email === email);
      if (!user) {
        // Auto-provision tenant on first signup (as requested)
        const provisioned = this.provisionTenant(name, email, orgName);
        user = db.users[provisioned.userId];
      }
      
      // Enforce isolation in session
      const session = {
        userId: user.id,
        orgId: user.orgId,
        role: user.role,
        email: user.email,
        name: user.name
      };
      localStorage.setItem('kibo_active_session', JSON.stringify(session));
      return session;
    },

    getCurrentSession: function() {
      const s = localStorage.getItem('kibo_active_session');
      return s ? JSON.parse(s) : null;
    },

    PERMISSIONS,
    ROLES
  };
})();

// Auto-init on load
KiboRBAC.init();
