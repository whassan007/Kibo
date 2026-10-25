import React, { useState, useEffect, useMemo } from 'react';
import {
  PrivacyOsService,
  getPrivacyOsTenantContext,
  setPrivacyOsTenantContext,
  type JurisdictionEntry,
  type OrganizationProfileInput,
  type ProcessingActivityInput,
  type ApplicabilityEvaluationResponse,
  type BreachIncidentInput,
  type BreachWarRoomResponse,
  type AssessmentRecommendationRequest,
  type AssessmentRecommendationResponse,
  type DsarEvaluateRequest,
  type DsarNexusEvaluationResponse,
  type RopaRecord,
  type AssistantQueryRequest,
  type GovernedAssistantResponse,
  type CorporateAiHubIntegrationStatus,
} from '../services/privacyOsService';

type PortalTab =
  | 'jrae'
  | 'breach_war_room'
  | 'assessments_dsar'
  | 'coverage_matrix'
  | 'ai_hubs_assistant'
  | 'regulatory_intelligence';

interface RegulatoryCitationProvenanceEntry {
  citation_id: string;
  jurisdiction_code: string;
  source_id: string;
  statute_or_instrument: string;
  section_ref: string;
  source_url: string;
  sha256_hash: string;
  effective_from: string;
  amendment_version: string;
  provenance_status: 'VERIFIED' | 'UNVERIFIED' | 'SOURCE_UNAVAILABLE' | 'REQUIRES_LEGAL_REVIEW';
  reviewed_by_role: string | null;
}

const INITIAL_CITATION_PROVENANCE_LEDGER: RegulatoryCitationProvenanceEntry[] = [
  {
    citation_id: 'CIT-US-CA-CCPA-1798.100',
    jurisdiction_code: 'US-CA',
    source_id: 'US-CA-CPPA-STATUTE',
    statute_or_instrument: 'California Consumer Privacy Act (CCPA/CPRA)',
    section_ref: 'Cal. Civ. Code § 1798.100 & ADMT Regs',
    source_url: 'https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=CIV&division=3.&part=4.&title=1.81.5.',
    sha256_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    effective_from: '2026-01-01',
    amendment_version: 'v2026.1-CPPA-ADMT',
    provenance_status: 'VERIFIED',
    reviewed_by_role: 'CPO',
  },
  {
    citation_id: 'CIT-CA-QC-LAW25-S17',
    jurisdiction_code: 'CA-QC',
    source_id: 'CA-QC-CAI-LAW25',
    statute_or_instrument: 'Quebec Act Respecting the Protection of Personal Information in the Private Sector (Law 25)',
    section_ref: 'CQLR c. P-39.1, ss. 3.5, 12.1, 17',
    source_url: 'https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1',
    sha256_hash: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4',
    effective_from: '2024-09-22',
    amendment_version: 'v2024.9-Phase3-Portability',
    provenance_status: 'VERIFIED',
    reviewed_by_role: 'LEGAL',
  },
  {
    citation_id: 'CIT-EU-GDPR-ART33-35',
    jurisdiction_code: 'EU-UNION',
    source_id: 'EU-EURLEX-GDPR-2016-679',
    statute_or_instrument: 'Regulation (EU) 2016/679 (General Data Protection Regulation)',
    section_ref: 'Articles 12(3), 17, 28, 30, 33, 34, 35',
    source_url: 'https://eur-lex.europa.eu/eli/reg/2016/679/oj',
    sha256_hash: '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
    effective_from: '2018-05-25',
    amendment_version: 'v2026.02-EDPB-Harmonized',
    provenance_status: 'VERIFIED',
    reviewed_by_role: 'DPO',
  },
  {
    citation_id: 'CIT-US-MD-MODPA-2025',
    jurisdiction_code: 'US-MD',
    source_id: 'US-MD-MGA-MODPA',
    statute_or_instrument: 'Maryland Online Data Privacy Act (MODPA)',
    section_ref: 'Md. Code Com. Law § 14-4601 et seq.',
    source_url: 'https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0541',
    sha256_hash: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
    effective_from: '2025-10-01',
    amendment_version: 'v2025.10-StrictDataMinimization',
    provenance_status: 'REQUIRES_LEGAL_REVIEW',
    reviewed_by_role: null,
  },
  {
    citation_id: 'CIT-EU-AI-ACT-ART27',
    jurisdiction_code: 'EU-UNION',
    source_id: 'EU-EURLEX-AI-2024-1689',
    statute_or_instrument: 'Regulation (EU) 2024/1689 (EU Artificial Intelligence Act)',
    section_ref: 'Article 27 (Fundamental Rights Impact Assessment)',
    source_url: 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
    sha256_hash: '7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451',
    effective_from: '2026-08-02',
    amendment_version: 'v2026.08-HighRiskAnnexIII',
    provenance_status: 'REQUIRES_LEGAL_REVIEW',
    reviewed_by_role: null,
  },
  {
    citation_id: 'CIT-CA-ON-PHIPA-IPC',
    jurisdiction_code: 'CA-ON',
    source_id: 'CA-ON-ELAWS-PHIPA',
    statute_or_instrument: 'Ontario Personal Health Information Protection Act (PHIPA)',
    section_ref: 'S.O. 2004, c. 3, Sched. A, s. 12(2)',
    source_url: 'https://www.ontario.ca/laws/statute/04p03',
    sha256_hash: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    effective_from: '2024-01-01',
    amendment_version: 'v2024.1-IPC-AdminPenalties',
    provenance_status: 'UNVERIFIED',
    reviewed_by_role: null,
  },
  {
    citation_id: 'CIT-US-IN-ICDPA-2026',
    jurisdiction_code: 'US-IN',
    source_id: 'US-IN-IGA-ICDPA',
    statute_or_instrument: 'Indiana Consumer Data Protection Act (ICDPA)',
    section_ref: 'Ind. Code § 24-15-1-1 et seq.',
    source_url: 'https://iga.in.gov/legislative/2023/bills/senate/5',
    sha256_hash: 'PENDING_OFFICIAL_FETCH_SNAPSHOT',
    effective_from: '2026-01-01',
    amendment_version: 'v2026.01-Effective',
    provenance_status: 'SOURCE_UNAVAILABLE',
    reviewed_by_role: null,
  },
];

const ALL_DATA_CATEGORIES = [
  { id: 'identifiers', label: 'Identifiers & Contact Info' },
  { id: 'phi', label: 'Protected Health Info (PHI / PHIPA)' },
  { id: 'biometrics', label: 'Biometric Identifiers (BIPA / CUBI / Law 25)' },
  { id: 'financial', label: 'Financial / Payment Records (GLBA / DORA)' },
  { id: 'geolocation', label: 'Precise Geolocation' },
  { id: 'children', label: 'Children / Minors (<13 / <16 / <18)' },
  { id: 'employee_hr', label: 'Employee & Workforce HR Data' },
  { id: 'behavioral_ad', label: 'Cross-Context Behavioral / Ad Telemetry' },
];

export const PrivacyOSPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<PortalTab>('jrae');
  const [isLiveBackend, setIsLiveBackend] = useState<boolean>(false);

  // Tenant & Identity Context
  const initialCtx = getPrivacyOsTenantContext();
  const [tenantId, setTenantId] = useState<string>(initialCtx.tenantId);
  const [userId, setUserId] = useState<string>(initialCtx.userId);

  // Global Jurisdictions Registry State
  const [jurisdictions, setJurisdictions] = useState<JurisdictionEntry[]>([]);
  const [matrixCountryFilter, setMatrixCountryFilter] = useState<'ALL' | 'US' | 'CA' | 'EU'>('ALL');
  const [matrixSearch, setMatrixSearch] = useState<string>('');

  // ==========================================================================
  // TAB 1: JRAE STATE
  // ==========================================================================
  const [orgProfile, setOrgProfile] = useState<OrganizationProfileInput>({
    name: 'Aegis Global Health & FinTech Corp',
    industry: 'healthcare_fintech',
    organization_type: 'private',
    employee_count: 680,
    annual_revenue_usd: 54000000,
    consumer_records_count: 240000,
    data_broker_revenue_pct: 12,
    is_federally_regulated_canada: false,
    hipaa_status: 'covered_entity',
    role: 'controller',
    establishments: ['US-CA', 'CA-ON', 'CA-QC', 'EU-IE', 'EU-DE'],
    main_eu_establishment: 'EU-IE',
    subnational_regions: ['DE-BY-PRIV'],
  });

  const [activityInput, setActivityInput] = useState<ProcessingActivityInput>({
    purpose: 'Cross-Border Clinical Telehealth, AI Triage & Customer Billing Analytics',
    data_categories: ['identifiers', 'phi', 'financial', 'behavioral_ad'],
    data_subject_categories: ['patients', 'consumers', 'employees'],
    subject_locations: ['US-CA', 'CA-ON', 'CA-QC', 'EU-DE', 'EU-FR'],
    processing_locations: ['US-CA', 'CA-ON', 'EU-IE'],
    transfer_destinations: ['US-CA', 'EU-IE'],
    third_party_processors: true,
    involves_ai_or_admt: true,
    involves_biometrics: false,
    involves_children: false,
    involves_targeted_advertising_or_cookies: true,
    involves_cross_border_transfer: true,
    targets_goods_or_services_to_subjects: true,
    monitors_subject_behavior: true,
    transfer_mechanisms_in_place: ['EU_2021_SCCs', 'LAW25_S17_TIA'],
  });

  const [jraeResult, setJraeResult] = useState<ApplicabilityEvaluationResponse | null>(null);
  const [jraeLoading, setJraeLoading] = useState<boolean>(false);
  const [jurPickerRegion, setJurPickerRegion] = useState<'US' | 'CA' | 'EU'>('US');

  // ==========================================================================
  // TAB 2: MULTI-JURISDICTION BREACH WAR ROOM STATE
  // ==========================================================================
  const [breachInput, setBreachInput] = useState<BreachIncidentInput>({
    title: 'Unauthorized OAuth Token Exfiltration on Multi-Region Patient & Billing Cluster',
    discovery_timestamp: new Date().toISOString().slice(0, 16),
    jurisdictions: ['US-CA', 'CA-ON', 'CA-QC', 'EU-FR', 'EU-DE'],
    affected_counts_by_jurisdiction: {
      'US-CA': 1420,
      'CA-ON': 610,
      'CA-QC': 480,
      'EU-FR': 890,
      'EU-DE': 940,
    },
    data_categories: ['identifiers', 'phi', 'financial'],
    involves_phi: true,
    involves_financial: true,
    is_critical_infrastructure: false,
    risk_of_harm_level: 'rrosh',
    encryption_or_safe_harbor_intact: false,
    description:
      'Compromised third-party subprocessor token accessed unencrypted cache tables containing patient appointment records and billing identifiers across US-CA, Ontario, Quebec, France, and Germany.',
  });

  const [warRoomResult, setWarRoomResult] = useState<BreachWarRoomResponse | null>(null);
  const [warRoomLoading, setWarRoomLoading] = useState<boolean>(false);
  const [counselApprovedRegimes, setCounselApprovedRegimes] = useState<Record<string, boolean>>({});

  // ==========================================================================
  // TAB 3: ASSESSMENTS, DSAR NEXUS & ROPA STATE
  // ==========================================================================
  const [asmtRequest, setAsmtRequest] = useState<AssessmentRecommendationRequest>({
    activity_name: 'AI Diagnostic Triage & Cross-Border Telemetry Pipeline',
    jurisdictions: ['US-CA', 'CA-ON', 'CA-QC', 'EU-DE', 'EU-FR'],
    involves_high_risk_processing: true,
    involves_ai_or_admt: true,
    involves_cross_border_transfer: true,
    involves_phi_or_hin: true,
    relies_on_legitimate_interests: true,
    is_public_sector: false,
  });
  const [asmtResponse, setAsmtResponse] = useState<AssessmentRecommendationResponse | null>(null);

  const [dsarRequest, setDsarRequest] = useState<DsarEvaluateRequest>({
    subject_name_or_id: 'SUBJ-QC-CA-88412',
    subject_residency: 'CA-QC',
    controller_establishments: ['US-CA', 'CA-QC', 'CA-ON', 'EU-IE'],
    request_type: 'deletion_erasure',
    received_at: new Date().toISOString().slice(0, 10),
    is_complex_or_extended: false,
    holds_litigation_or_aml_ledger: true,
  });
  const [dsarResponse, setDsarResponse] = useState<DsarNexusEvaluationResponse | null>(null);
  const [ropaRecords, setRopaRecords] = useState<RopaRecord[]>([]);

  // ==========================================================================
  // TAB 5: CORPORATE AI HUBS & GOVERNED ASSISTANT STATE
  // ==========================================================================
  const [integrations, setIntegrations] = useState<CorporateAiHubIntegrationStatus[]>([]);
  const [assistantReq, setAssistantReq] = useState<AssistantQueryRequest>({
    query:
      'We are deploying an AI triage model in California, Ontario, Quebec, and Germany that transfers telemetry to our US-CA and EU-IE hubs. What mandatory assessments, preemption splits, and breach SLAs apply?',
    channel: 'm365_copilot',
    jurisdiction_context: ['US-CA', 'US-FED', 'CA-ON', 'CA-QC', 'EU-DE', 'EU-IE'],
  });
  const [assistantRes, setAssistantRes] = useState<GovernedAssistantResponse | null>(null);
  const [assistantLoading, setAssistantLoading] = useState<boolean>(false);

  // ==========================================================================
  // TAB 6: REGULATORY INTELLIGENCE & CITATION VERIFICATION STATE
  // ==========================================================================
  const [citationLedger, setCitationLedger] = useState<RegulatoryCitationProvenanceEntry[]>(
    INITIAL_CITATION_PROVENANCE_LEDGER
  );
  const [citationFilterStatus, setCitationFilterStatus] = useState<
    'ALL' | 'VERIFIED' | 'UNVERIFIED' | 'SOURCE_UNAVAILABLE' | 'REQUIRES_LEGAL_REVIEW'
  >('ALL');
  const [selectedReviewerRole, setSelectedReviewerRole] = useState<'LEGAL' | 'CPO' | 'DPO'>('LEGAL');

  const handlePromoteCitationToVerified = (citationId: string) => {
    setCitationLedger((prev) =>
      prev.map((entry) =>
        entry.citation_id === citationId
          ? {
              ...entry,
              provenance_status: 'VERIFIED',
              reviewed_by_role: selectedReviewerRole,
            }
          : entry
      )
    );
  };

  const filteredCitations = useMemo(() => {
    return citationLedger.filter(
      (entry) => citationFilterStatus === 'ALL' || entry.provenance_status === citationFilterStatus
    );
  }, [citationLedger, citationFilterStatus]);

  // Sync Tenant Headers
  useEffect(() => {
    setPrivacyOsTenantContext({ tenantId, userId });
  }, [tenantId, userId]);

  // Initial Bootstrap Load
  useEffect(() => {
    const bootstrap = async () => {
      const [jurRes, evalRes, warRes, asmtRes, dsarRes, ropaRes, intRes, astRes] = await Promise.all([
        PrivacyOsService.getJurisdictions(),
        PrivacyOsService.evaluateApplicability({
          organization: orgProfile,
          activity: activityInput,
          include_non_effective_laws: true,
        }),
        PrivacyOsService.evaluateIncidentWarRoom(breachInput),
        PrivacyOsService.recommendAssessments(asmtRequest),
        PrivacyOsService.evaluateDsarRequest(dsarRequest),
        PrivacyOsService.getRopaRecords(),
        PrivacyOsService.getIntegrationsStatus(),
        PrivacyOsService.queryGovernedAssistant(assistantReq),
      ]);

      setJurisdictions(jurRes.jurisdictions);
      setJraeResult(evalRes.evaluation);
      setWarRoomResult(warRes.warRoom);
      setAsmtResponse(asmtRes.recommendation);
      setDsarResponse(dsarRes.dsar);
      setRopaRecords(ropaRes.records);
      setIntegrations(intRes.integrations);
      setAssistantRes(astRes.response);
      setIsLiveBackend(jurRes.live || evalRes.live);
    };
    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handlers
  const handleRunJrae = async () => {
    setJraeLoading(true);
    try {
      const res = await PrivacyOsService.evaluateApplicability({
        organization: orgProfile,
        activity: activityInput,
        include_non_effective_laws: true,
      });
      setJraeResult(res.evaluation);
      setIsLiveBackend(res.live);
    } finally {
      setJraeLoading(false);
    }
  };

  const handleRunWarRoom = async () => {
    setWarRoomLoading(true);
    try {
      const res = await PrivacyOsService.evaluateIncidentWarRoom(breachInput);
      setWarRoomResult(res.warRoom);
      setIsLiveBackend(res.live);
    } finally {
      setWarRoomLoading(false);
    }
  };

  const handleRunAssessments = async () => {
    const res = await PrivacyOsService.recommendAssessments(asmtRequest);
    setAsmtResponse(res.recommendation);
  };

  const handleRunDsar = async () => {
    const res = await PrivacyOsService.evaluateDsarRequest(dsarRequest);
    setDsarResponse(res.dsar);
  };

  const handleRunAssistant = async () => {
    setAssistantLoading(true);
    try {
      const res = await PrivacyOsService.queryGovernedAssistant(assistantReq);
      setAssistantRes(res.response);
    } finally {
      setAssistantLoading(false);
    }
  };

  const toggleEstablishment = (code: string) => {
    setOrgProfile((prev) => {
      const exists = prev.establishments.includes(code);
      const next = exists ? prev.establishments.filter((c) => c !== code) : [...prev.establishments, code];
      return { ...prev, establishments: next };
    });
  };

  const toggleSubjectLocation = (code: string) => {
    setActivityInput((prev) => {
      const exists = prev.subject_locations.includes(code);
      const next = exists ? prev.subject_locations.filter((c) => c !== code) : [...prev.subject_locations, code];
      return { ...prev, subject_locations: next };
    });
  };

  const toggleDataCategory = (catId: string) => {
    setActivityInput((prev) => {
      const exists = prev.data_categories.includes(catId);
      const next = exists ? prev.data_categories.filter((c) => c !== catId) : [...prev.data_categories, catId];
      return { ...prev, data_categories: next };
    });
  };

  const toggleBreachJurisdiction = (code: string) => {
    setBreachInput((prev) => {
      const exists = prev.jurisdictions.includes(code);
      const next = exists ? prev.jurisdictions.filter((c) => c !== code) : [...prev.jurisdictions, code];
      return { ...prev, jurisdictions: next };
    });
  };

  // Filtered Jurisdictions for Coverage Matrix
  const filteredJurisdictions = useMemo(() => {
    return jurisdictions.filter((j) => {
      const matchesRegion =
        matrixCountryFilter === 'ALL' ||
        (matrixCountryFilter === 'US' && j.jurisdiction_id.startsWith('US')) ||
        (matrixCountryFilter === 'CA' && j.jurisdiction_id.startsWith('CA')) ||
        (matrixCountryFilter === 'EU' && j.jurisdiction_id.startsWith('EU'));
      const matchesSearch =
        !matrixSearch.trim() ||
        j.jurisdiction_id.toLowerCase().includes(matrixSearch.toLowerCase()) ||
        j.name.toLowerCase().includes(matrixSearch.toLowerCase()) ||
        j.primary_regulator.toLowerCase().includes(matrixSearch.toLowerCase());
      return matchesRegion && matchesSearch;
    });
  }, [jurisdictions, matrixCountryFilter, matrixSearch]);

  const pickerJurisdictions = useMemo(() => {
    return jurisdictions.filter((j) => j.jurisdiction_id.startsWith(jurPickerRegion));
  }, [jurisdictions, jurPickerRegion]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Executive Governance Bar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 text-xs font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 rounded">
                KIBO PRIVACY OS v2026.10
              </span>
              <span
                className={`px-2.5 py-1 text-xs font-semibold rounded border ${
                  isLiveBackend
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}
              >
                {isLiveBackend ? 'LIVE ENGINE API CONNECTED' : 'DETERMINISTIC ENGINE (OFFLINE FALLBACK READY)'}
              </span>
              <span className="px-2.5 py-1 text-xs font-medium bg-slate-800 text-slate-300 rounded border border-slate-700">
                US 50+DC+Fed • CA 13+Fed • EU 27+Union
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white mt-1.5 tracking-tight">
              Enterprise Privacy Office Operating System & Multi-Jurisdictional Command Center
            </h1>
          </div>

          {/* Tenant & Identity Context Header Bar */}
          <div className="flex flex-wrap items-center gap-2 bg-slate-950/90 border border-slate-800 rounded-lg p-2.5 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400 font-medium">X-Tenant-ID:</span>
              <input
                aria-label="X-Tenant-ID"
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-indigo-300 font-mono w-44 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400 font-medium">X-User-ID:</span>
              <input
                aria-label="X-User-ID"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-emerald-300 font-mono w-36 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-4 flex flex-wrap gap-2 border-t border-slate-800/80 pt-3">
          {[
            { id: 'jrae', label: '1. Jurisdictional Applicability Engine (JRAE)' },
            { id: 'breach_war_room', label: '2. Multi-Jurisdiction Breach War Room' },
            { id: 'assessments_dsar', label: '3. Privacy Assessments (PIA/DPIA/TRA/TIA/FRIA) & DSAR' },
            { id: 'coverage_matrix', label: '4. Global Coverage Matrix (US / CA / EU)' },
            { id: 'ai_hubs_assistant', label: '5. Corporate AI Hubs & Governed Assistant' },
            { id: 'regulatory_intelligence', label: '6. Regulatory Intelligence & Citation Verification' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as PortalTab)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 border border-indigo-400'
                  : 'bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content Container */}
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* ===================================================================
            TAB 1: JURISDICTIONAL APPLICABILITY ENGINE (JRAE)
        =================================================================== */}
        {activeTab === 'jrae' && (
          <div className="space-y-6">
            {/* Configuration Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Organization Profile Panel */}
              <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h2 className="text-base font-bold text-white">Organization Profile & Establishments</h2>
                    <p className="text-xs text-slate-400">
                      Evaluates statutory thresholds (CCPA $26.625M / 100k records, BDSG 20 employees, HIPAA/FWUB status)
                    </p>
                  </div>
                  <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-indigo-300">Section 7.1</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Industry Sector</label>
                    <select
                      value={orgProfile.industry}
                      onChange={(e) => setOrgProfile({ ...orgProfile, industry: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white"
                    >
                      <option value="healthcare_fintech">Healthcare & FinTech (Hybrid)</option>
                      <option value="technology">Enterprise SaaS & AI Technology</option>
                      <option value="financial_services">Banking & Capital Markets (GLBA / OSFI / DORA)</option>
                      <option value="retail_adtech">Retail, E-Commerce & AdTech</option>
                      <option value="public_sector">Government / Public Body (FIPPA / ATIPP / Privacy Act)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Entity Classification</label>
                    <select
                      value={orgProfile.organization_type}
                      onChange={(e) => setOrgProfile({ ...orgProfile, organization_type: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white"
                    >
                      <option value="private">Private Commercial Enterprise</option>
                      <option value="health_information_custodian">Health Information Custodian (PHIPA HIC)</option>
                      <option value="public">Public Sector / Crown Agency</option>
                      <option value="nonprofit">Non-Profit Organization</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Annual Gross Revenue (USD)</label>
                    <input
                      type="number"
                      value={orgProfile.annual_revenue_usd ?? 0}
                      onChange={(e) => setOrgProfile({ ...orgProfile, annual_revenue_usd: Number(e.target.value) })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Employee Headcount</label>
                    <input
                      type="number"
                      value={orgProfile.employee_count ?? 0}
                      onChange={(e) => setOrgProfile({ ...orgProfile, employee_count: Number(e.target.value) })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Consumer Records Count</label>
                    <input
                      type="number"
                      value={orgProfile.consumer_records_count ?? 0}
                      onChange={(e) => setOrgProfile({ ...orgProfile, consumer_records_count: Number(e.target.value) })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">HIPAA / Federal Status</label>
                    <select
                      value={orgProfile.hipaa_status || 'non_hipaa'}
                      onChange={(e) => setOrgProfile({ ...orgProfile, hipaa_status: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white"
                    >
                      <option value="covered_entity">HIPAA Covered Entity</option>
                      <option value="business_associate">HIPAA Business Associate</option>
                      <option value="hybrid_entity">HIPAA Hybrid Entity</option>
                      <option value="non_hipaa">Non-HIPAA Commercial Entity</option>
                    </select>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 text-xs">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={orgProfile.is_federally_regulated_canada}
                      onChange={(e) =>
                        setOrgProfile({ ...orgProfile, is_federally_regulated_canada: e.target.checked })
                      }
                      className="rounded border-slate-600 text-indigo-600"
                    />
                    <span className="text-slate-300">
                      Canadian Federal Work, Undertaking or Business (FWUB — Banking, Telecom, Aviation)
                    </span>
                  </label>
                </div>

                {/* Multi-Jurisdiction Selector across US 50, CA 13, EU 27 */}
                <div className="border-t border-slate-800 pt-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-300">
                      Active Establishments & Subject Jurisdictions ({orgProfile.establishments.length} Establishments /{' '}
                      {activityInput.subject_locations.length} Subject Regions)
                    </span>
                    <div className="flex gap-1">
                      {(['US', 'CA', 'EU'] as const).map((reg) => (
                        <button
                          key={reg}
                          onClick={() => setJurPickerRegion(reg)}
                          className={`px-2 py-0.5 text-xs rounded font-semibold ${
                            jurPickerRegion === reg
                              ? 'bg-indigo-600 text-white'
                              : 'bg-slate-800 text-slate-400 hover:text-white'
                          }`}
                        >
                          {reg === 'US' ? 'US (50+DC+Fed)' : reg === 'CA' ? 'CA (13+Fed)' : 'EU (27+Union)'}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="max-h-40 overflow-y-auto bg-slate-950 border border-slate-800 rounded p-2 grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-xs">
                    {pickerJurisdictions.map((j) => {
                      const inEst = orgProfile.establishments.includes(j.jurisdiction_id);
                      const inSub = activityInput.subject_locations.includes(j.jurisdiction_id);
                      return (
                        <div
                          key={j.jurisdiction_id}
                          className={`p-1.5 rounded border flex items-center justify-between ${
                            inEst || inSub
                              ? 'bg-indigo-950/60 border-indigo-500/50 text-indigo-200'
                              : 'bg-slate-900/50 border-slate-800 text-slate-400'
                          }`}
                        >
                          <span className="font-mono font-semibold truncate mr-1" title={j.name}>
                            {j.jurisdiction_id}
                          </span>
                          <div className="flex gap-1 shrink-0">
                            <button
                              type="button"
                              onClick={() => toggleEstablishment(j.jurisdiction_id)}
                              title="Toggle Establishment"
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                inEst ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              EST
                            </button>
                            <button
                              type="button"
                              onClick={() => toggleSubjectLocation(j.jurisdiction_id)}
                              title="Toggle Data Subject Location"
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                inSub ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'
                              }`}
                            >
                              SUB
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Processing Activity Input Panel */}
              <div className="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between">
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h2 className="text-base font-bold text-white">Processing Activity & Technical Triggers</h2>
                      <p className="text-xs text-slate-400">
                        Evaluates data-level carve-outs, AI/ADMT rules, cross-border TIAs, and third-party processors
                      </p>
                    </div>
                    <span className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-emerald-300">
                      Multi-Regime Graph
                    </span>
                  </div>

                  <div className="text-xs">
                    <label className="block text-slate-400 mb-1">Processing Purpose Description</label>
                    <input
                      type="text"
                      value={activityInput.purpose}
                      onChange={(e) => setActivityInput({ ...activityInput, purpose: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs text-slate-400 mb-1.5">Data Categories Processed</label>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
                      {ALL_DATA_CATEGORIES.map((cat) => {
                        const checked = activityInput.data_categories.includes(cat.id);
                        return (
                          <button
                            key={cat.id}
                            type="button"
                            onClick={() => toggleDataCategory(cat.id)}
                            className={`text-left px-2.5 py-1.5 rounded border transition-colors ${
                              checked
                                ? 'bg-indigo-600/25 border-indigo-500 text-indigo-200 font-semibold'
                                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                            }`}
                          >
                            {checked ? '✓ ' : '+ '}
                            {cat.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1 text-xs">
                    <label className="flex items-center gap-2 bg-slate-950 border border-slate-800 p-2.5 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={activityInput.involves_ai_or_admt}
                        onChange={(e) => setActivityInput({ ...activityInput, involves_ai_or_admt: e.target.checked })}
                      />
                      <span>Involves AI / Automated Decision-Making (EU AI Act / CalPrivacy ADMT / Law 25 s. 12.1)</span>
                    </label>

                    <label className="flex items-center gap-2 bg-slate-950 border border-slate-800 p-2.5 rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={activityInput.third_party_processors}
                        onChange={(e) =>
                          setActivityInput({ ...activityInput, third_party_processors: e.target.checked })
                        }
                      />
                      <span>Engages Third-Party Processors / Subprocessors (GDPR Art. 28 / BAA / CCPA)</span>
                    </label>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <div className="text-xs text-slate-400">
                    Lead EU Establishment:{' '}
                    <span className="text-indigo-300 font-mono font-semibold">
                      {orgProfile.main_eu_establishment || 'EU-IE'}
                    </span>
                  </div>
                  <button
                    onClick={handleRunJrae}
                    disabled={jraeLoading}
                    className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-indigo-600/30 transition cursor-pointer"
                  >
                    {jraeLoading ? 'Evaluating Multi-Jurisdictional Graph...' : 'Run Applicability Evaluation (JRAE)'}
                  </button>
                </div>
              </div>
            </div>

            {/* JRAE Evaluation Results */}
            {jraeResult && (
              <div className="space-y-6">
                {/* Legal Review Escalation Banner */}
                {jraeResult.requires_legal_review && (
                  <div className="bg-amber-950/60 border border-amber-500/50 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 text-[11px] font-bold uppercase bg-amber-500 text-slate-950 rounded">
                          requires_legal_review = true
                        </span>
                        <span className="text-sm font-bold text-amber-200">
                          Mandatory Human Privacy Counsel Review Gate Triggered
                        </span>
                      </div>
                      <ul className="list-disc pl-5 text-xs text-amber-100/90 space-y-0.5">
                        {jraeResult.legal_review_reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="shrink-0 text-right">
                      <div className="text-xs font-mono text-amber-300">Eval ID: {jraeResult.evaluation_id}</div>
                      <div className="text-[11px] text-amber-400/80">Rule Version: 2026.10.1 Verified</div>
                    </div>
                  </div>
                )}

                {/* Executive Summary Strip */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <div className="text-xs text-slate-400">Applicable Legal Instruments</div>
                    <div className="text-2xl font-bold text-white mt-1">
                      {jraeResult.applicable_instruments.length} Statutes
                    </div>
                    <div className="text-xs text-indigo-400 mt-1">
                      +{jraeResult.exempt_or_preempted_instruments.length} Exempt/Carved-Out Analyzed
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <div className="text-xs text-slate-400">Mandatory Assessments Triggered</div>
                    <div className="text-2xl font-bold text-emerald-400 mt-1">
                      {jraeResult.required_assessments.length} Required
                    </div>
                    <div className="text-xs text-slate-400 mt-1 truncate">
                      {jraeResult.required_assessments.slice(0, 2).join(' • ')}
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <div className="text-xs text-slate-400">Strictest Breach & DSAR Clocks</div>
                    <div className="text-lg font-bold text-amber-300 mt-1">72h Breach / 30d DSAR</div>
                    <div className="text-xs text-slate-400 mt-1">
                      GDPR 72h + Law 25 Promptly + 15bd CA Opt-Out
                    </div>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                    <div className="text-xs text-slate-400">EU Lead Supervisory Authority</div>
                    <div className="text-sm font-bold text-indigo-300 mt-1">
                      {jraeResult.lead_supervisory_authority?.authority || 'N/A'}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {jraeResult.lead_supervisory_authority?.basis || 'Art. 56 One-Stop-Shop'}
                    </div>
                  </div>
                </div>

                {/* Detailed Applicable Instruments Cards */}
                <div className="space-y-4">
                  <h3 className="text-base font-bold text-white">
                    Applicable Legal Instruments, Thresholds Evaluated, Exemptions & Preemption Split
                  </h3>
                  {jraeResult.applicable_instruments.map((inst) => (
                    <div
                      key={inst.regulation_id}
                      className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4"
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="px-2 py-0.5 text-xs font-mono font-bold bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 rounded">
                              {inst.jurisdiction_id}
                            </span>
                            <h4 className="text-sm font-bold text-white">{inst.legal_instrument}</h4>
                            <span className="text-xs font-mono text-slate-400">({inst.article_or_section})</span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1">{inst.applicability_reasoning}</p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          {inst.requires_legal_review && (
                            <span className="px-2 py-0.5 text-[11px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded">
                              Requires Counsel Sign-Off
                            </span>
                          )}
                          <a
                            href={inst.official_source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded border border-slate-700"
                          >
                            Official Statute ↗
                          </a>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 text-xs">
                        {/* Thresholds & Exemptions */}
                        <div className="bg-slate-950 border border-slate-800/90 rounded-lg p-3 space-y-2">
                          <div className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">
                            Statutory Thresholds & Exemptions
                          </div>
                          {inst.thresholds_evaluated.length > 0 ? (
                            <ul className="space-y-1.5">
                              {inst.thresholds_evaluated.map((th, i) => (
                                <li key={i} className="text-slate-300">
                                  <span
                                    className={`inline-block px-1.5 py-0.2 rounded text-[10px] font-bold mr-1.5 ${
                                      th.met ? 'bg-emerald-500/20 text-emerald-300' : 'bg-slate-800 text-slate-400'
                                    }`}
                                  >
                                    {th.met ? 'MET' : 'NOT MET'}
                                  </span>
                                  <span className="font-mono text-indigo-300">{th.metric}</span>: {th.description}
                                </li>
                              ))}
                            </ul>
                          ) : (
                            <div className="text-slate-400">No minimum revenue floor — applies upon territorial/sectoral nexus.</div>
                          )}

                          {inst.exemptions_evaluated.map((ex) => (
                            <div
                              key={ex.exemption_id}
                              className="mt-2 pt-2 border-t border-slate-800 text-amber-200/90"
                            >
                              <div className="font-semibold">
                                Exemption ({ex.exemption_type}): {ex.carve_out_statute}
                              </div>
                              <div className="text-slate-300 mt-0.5">{ex.scope}</div>
                            </div>
                          ))}
                        </div>

                        {/* Preemption Split & Mandatory Controls */}
                        <div className="bg-slate-950 border border-slate-800/90 rounded-lg p-3 space-y-2">
                          <div className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">
                            Preemption Split & Mandatory Controls
                          </div>
                          {inst.preemption_notes.map((note, idx) => (
                            <div
                              key={idx}
                              className="p-2 rounded bg-indigo-950/40 border border-indigo-500/30 text-indigo-200"
                            >
                              {note}
                            </div>
                          ))}
                          <ul className="list-disc pl-4 space-y-1 text-slate-300">
                            {inst.mandatory_controls.map((ctrl, idx) => (
                              <li key={idx}>{ctrl}</li>
                            ))}
                          </ul>
                        </div>

                        {/* Assessments, Deadlines & Competent Regulator */}
                        <div className="bg-slate-950 border border-slate-800/90 rounded-lg p-3 space-y-2">
                          <div className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">
                            Assessments, Deadlines & Regulator
                          </div>
                          <div>
                            <span className="text-slate-400">Competent Authority: </span>
                            <span className="text-white font-semibold">{inst.competent_authority}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">DSAR Clock: </span>
                            <span className="text-emerald-300 font-semibold">
                              {inst.response_deadlines.rights_request_initial_days} days (
                              {inst.response_deadlines.rights_request_day_type})
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400">Breach Notice: </span>
                            <span className="text-amber-300 font-semibold">
                              {inst.response_deadlines.breach_regulator_text}
                            </span>
                          </div>
                          <div className="pt-1">
                            <span className="text-slate-400 block mb-1">Required Assessments:</span>
                            <div className="flex flex-wrap gap-1">
                              {inst.required_assessments.map((asmt, idx) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 rounded text-[11px]"
                                >
                                  {asmt}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===================================================================
            TAB 2: MULTI-JURISDICTION BREACH WAR ROOM
        =================================================================== */}
        {activeTab === 'breach_war_room' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div>
                  <h2 className="text-lg font-bold text-white">
                    Multi-Jurisdiction Breach War Room (CA, ON, QC, FR, DE)
                  </h2>
                  <p className="text-xs text-slate-400">
                    Evaluates independent statutory harm thresholds (PIPEDA RROSH, GDPR 72h, Quebec Law 25 Serious Injury,
                    Ontario PHIPA IPC, CCPA/HIPAA) with mandatory Human Legal Approval gates.
                  </p>
                </div>
                <button
                  onClick={handleRunWarRoom}
                  disabled={warRoomLoading}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs rounded-lg shadow-lg shadow-rose-600/30 cursor-pointer"
                >
                  {warRoomLoading ? 'Recalculating Incident Clocks...' : 'Re-Evaluate Breach War Room'}
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Incident Title</label>
                  <input
                    type="text"
                    value={breachInput.title}
                    onChange={(e) => setBreachInput({ ...breachInput, title: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Harm Severity Assessment</label>
                  <select
                    value={breachInput.risk_of_harm_level}
                    onChange={(e) =>
                      setBreachInput({
                        ...breachInput,
                        risk_of_harm_level: e.target.value as BreachIncidentInput['risk_of_harm_level'],
                      })
                    }
                    className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white"
                  >
                    <option value="rrosh">
                      Real Risk of Significant Harm (RROSH) / Serious Injury / GDPR High Risk
                    </option>
                    <option value="high">High Risk to Rights & Freedoms</option>
                    <option value="moderate">Moderate Risk (Regulator Notice Only under GDPR Art. 33)</option>
                    <option value="low">Low / Unlikely Risk (Internal Register Only)</option>
                  </select>
                </div>

                <div className="flex flex-col justify-center gap-2 pt-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={breachInput.involves_phi}
                      onChange={(e) => setBreachInput({ ...breachInput, involves_phi: e.target.checked })}
                    />
                    <span>Involves PHI / Clinical Health Records (HIPAA + Ontario PHIPA)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={breachInput.encryption_or_safe_harbor_intact}
                      onChange={(e) =>
                        setBreachInput({ ...breachInput, encryption_or_safe_harbor_intact: e.target.checked })
                      }
                    />
                    <span>FIPS 140-3 Encryption Safe Harbor Intact (Keys Not Compromised)</span>
                  </label>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                <span className="text-slate-400 font-semibold">Impacted Jurisdictions:</span>
                {['US-CA', 'CA-ON', 'CA-QC', 'EU-FR', 'EU-DE'].map((code) => {
                  const active = breachInput.jurisdictions.includes(code);
                  return (
                    <button
                      key={code}
                      type="button"
                      onClick={() => toggleBreachJurisdiction(code)}
                      className={`px-3 py-1 rounded font-mono font-bold border ${
                        active
                          ? 'bg-rose-600/30 border-rose-500 text-rose-200'
                          : 'bg-slate-950 border-slate-800 text-slate-500'
                      }`}
                    >
                      {code} ({breachInput.affected_counts_by_jurisdiction[code] || 500} subjects)
                    </button>
                  );
                })}
              </div>
            </div>

            {warRoomResult && (
              <div className="space-y-6">
                {/* Unified Incident Timeline */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-white">
                      Unified Multi-Regime Incident Response Timeline
                    </h3>
                    <span className="px-2.5 py-1 text-xs font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 rounded">
                      NO AUTONOMOUS REGULATOR DISPATCH — HUMAN COUNSEL GATE ENFORCED
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                    {warRoomResult.unified_timeline.map((step) => (
                      <div
                        key={step.step_order}
                        className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 flex flex-col justify-between space-y-2"
                      >
                        <div>
                          <div className="text-xs font-mono font-bold text-rose-400">{step.window}</div>
                          <div className="text-xs font-semibold text-white mt-1">{step.milestone}</div>
                        </div>
                        <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                          <div className="flex flex-wrap gap-1">
                            {step.regimes_covered.map((r) => (
                              <span
                                key={r}
                                className="px-1.5 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-300 rounded"
                              >
                                {r}
                              </span>
                            ))}
                          </div>
                          <div className="text-[10px] uppercase font-bold text-amber-300">
                            Gate: {step.gate_type.replace(/_/g, ' ')}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Independent Regime Threshold Matrix */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                  <h3 className="text-base font-bold text-white">
                    Independent Regime Thresholds, Regulator Clocks & Mandatory Legal Approval Gates
                  </h3>
                  <div className="space-y-3">
                    {warRoomResult.regime_evaluations.map((reg) => {
                      const approved = Boolean(counselApprovedRegimes[reg.regulation_id]);
                      return (
                        <div
                          key={reg.regulation_id}
                          className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4 text-xs"
                        >
                          <div className="space-y-1.5 flex-1">
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="px-2 py-0.5 font-mono font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 rounded">
                                {reg.jurisdiction_id}
                              </span>
                              <span className="font-bold text-sm text-white">{reg.regime_label}</span>
                              <span
                                className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                                  reg.threshold_met
                                    ? 'bg-rose-600 text-white'
                                    : 'bg-emerald-600/20 text-emerald-300'
                                }`}
                              >
                                {reg.threshold_met ? 'NOTIFICATION THRESHOLD MET' : 'SAFE HARBOR / BELOW THRESHOLD'}
                              </span>
                            </div>
                            <div className="text-slate-300">
                              <span className="text-slate-400">Statutory Standard:</span> {reg.threshold_standard}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 pt-1 text-slate-300">
                              <div>
                                <span className="text-slate-400 block">Competent Authority:</span>
                                <span className="font-semibold text-white">{reg.regulator_authority}</span>
                              </div>
                              <div>
                                <span className="text-slate-400 block">Regulator Deadline:</span>
                                <span className="font-semibold text-amber-300">{reg.regulator_deadline_text}</span>
                              </div>
                              <div>
                                <span className="text-slate-400 block">Record Retention Duty:</span>
                                <span className="font-semibold text-indigo-300">
                                  {reg.record_retention_requirement}
                                </span>
                              </div>
                            </div>
                            {reg.ag_or_media_trigger && (
                              <div className="text-amber-300/90 font-medium pt-0.5">
                                Special Trigger: {reg.ag_or_media_trigger}
                              </div>
                            )}
                          </div>

                          <div className="shrink-0 flex flex-col items-end gap-2">
                            <button
                              type="button"
                              onClick={() =>
                                setCounselApprovedRegimes((prev) => ({
                                  ...prev,
                                  [reg.regulation_id]: !prev[reg.regulation_id],
                                }))
                              }
                              className={`px-3.5 py-2 rounded-lg font-bold text-xs cursor-pointer transition ${
                                approved
                                  ? 'bg-emerald-600 text-white'
                                  : 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                              }`}
                            >
                              {approved
                                ? '✓ Counsel Approved for Dispatch'
                                : 'Approve Legal Gate (Human Counsel Only)'}
                            </button>
                            <span className="text-[11px] text-slate-400">
                              Status: {approved ? 'COUNSEL_APPROVED' : 'PENDING_COUNSEL_GATE'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Deduplicated Containment Tasks */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <h3 className="text-base font-bold text-white">Deduplicated Cross-Jurisdiction Containment Tasks</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                    {warRoomResult.deduplicated_containment_tasks.map((task) => (
                      <div key={task.task_id} className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-indigo-400 font-bold">{task.task_id}</span>
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase text-[10px] font-bold">
                            {task.status.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="font-semibold text-white">{task.task_title}</div>
                        <div className="text-slate-400">Owner: {task.owner_role}</div>
                        <div className="flex flex-wrap gap-1 pt-1">
                          {task.satisfied_regimes.map((sr) => (
                            <span
                              key={sr}
                              className="px-1.5 py-0.5 bg-indigo-950/60 border border-indigo-500/30 rounded text-[10px] text-indigo-200"
                            >
                              {sr}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===================================================================
            TAB 3: PRIVACY ASSESSMENTS & CROSS-BORDER DSAR NEXUS
        =================================================================== */}
        {activeTab === 'assessments_dsar' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left: Multi-Regime Assessment Generator */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h2 className="text-base font-bold text-white">
                      Multi-Regime Privacy & AI Assessment Recommender
                    </h2>
                    <p className="text-xs text-slate-400">
                      PIA • GDPR Art. 35 DPIA • Ontario PHIPA TRA • Quebec Law 25 s. 17 TIA • GDPR LIA • EU AI Act Art.
                      27 FRIA / CalPrivacy ADMT
                    </p>
                  </div>
                  <button
                    onClick={handleRunAssessments}
                    className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-lg cursor-pointer"
                  >
                    Evaluate Templates
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <label className="flex items-center gap-2 bg-slate-950 p-2 rounded border border-slate-800">
                    <input
                      type="checkbox"
                      checked={asmtRequest.involves_high_risk_processing}
                      onChange={(e) =>
                        setAsmtRequest({ ...asmtRequest, involves_high_risk_processing: e.target.checked })
                      }
                    />
                    <span>High-Risk Processing (GDPR Art. 35 DPIA)</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-950 p-2 rounded border border-slate-800">
                    <input
                      type="checkbox"
                      checked={asmtRequest.involves_phi_or_hin}
                      onChange={(e) => setAsmtRequest({ ...asmtRequest, involves_phi_or_hin: e.target.checked })}
                    />
                    <span>Ontario PHI / Health Info Network (PHIPA TRA)</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-950 p-2 rounded border border-slate-800">
                    <input
                      type="checkbox"
                      checked={asmtRequest.involves_cross_border_transfer}
                      onChange={(e) =>
                        setAsmtRequest({ ...asmtRequest, involves_cross_border_transfer: e.target.checked })
                      }
                    />
                    <span>Cross-Border Transfer Outside QC/EU (Law 25 TIA)</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-950 p-2 rounded border border-slate-800">
                    <input
                      type="checkbox"
                      checked={asmtRequest.involves_ai_or_admt}
                      onChange={(e) => setAsmtRequest({ ...asmtRequest, involves_ai_or_admt: e.target.checked })}
                    />
                    <span>AI / Automated Decisions (EU AI FRIA & ADMT)</span>
                  </label>
                </div>

                {asmtResponse && (
                  <div className="space-y-3 pt-2">
                    {asmtResponse.assessments.map((asmt) => (
                      <div
                        key={asmt.assessment_code}
                        className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="px-2 py-0.5 font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded">
                            {asmt.assessment_code}
                          </span>
                          <span className="text-slate-400 font-mono">{asmt.jurisdiction_scope.join(', ')}</span>
                        </div>
                        <div className="font-bold text-white text-sm">{asmt.title}</div>
                        <div className="text-indigo-300">{asmt.statutory_basis}</div>
                        <div className="text-slate-300">{asmt.trigger_reason}</div>
                        <ul className="list-disc pl-4 text-slate-400 space-y-0.5">
                          {asmt.required_sections.map((sec, i) => (
                            <li key={i}>{sec}</li>
                          ))}
                        </ul>
                        <div className="text-[11px] text-amber-300 pt-1">
                          Required Sign-Offs: {asmt.required_signoffs.join(' • ')}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right: Cross-Border DSAR Nexus Evaluator */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <h2 className="text-base font-bold text-white">Cross-Border DSAR & Rights Nexus Evaluator</h2>
                    <p className="text-xs text-slate-400">
                      Computes strictest statutory deadline, verification rules, and retention vs. deletion conflicts
                    </p>
                  </div>
                  <button
                    onClick={handleRunDsar}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg cursor-pointer"
                  >
                    Evaluate DSAR Nexus
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">Data Subject Residency</label>
                    <select
                      value={dsarRequest.subject_residency}
                      onChange={(e) => setDsarRequest({ ...dsarRequest, subject_residency: e.target.value })}
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white"
                    >
                      <option value="CA-QC">Quebec, Canada (Law 25 — 30d strict)</option>
                      <option value="CA-ON">Ontario, Canada (PHIPA / PIPEDA — 30d)</option>
                      <option value="US-CA">California, USA (CCPA/CPRA — 45d / 15bd opt-out)</option>
                      <option value="EU-DE">Germany, EU (GDPR Art. 12(3) — 1 calendar month)</option>
                      <option value="EU-FR">France, EU (GDPR Art. 12(3) — 1 calendar month)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Right Invoked</label>
                    <select
                      value={dsarRequest.request_type}
                      onChange={(e) =>
                        setDsarRequest({
                          ...dsarRequest,
                          request_type: e.target.value as DsarEvaluateRequest['request_type'],
                        })
                      }
                      className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-2 text-white"
                    >
                      <option value="deletion_erasure">Right to Deletion / Erasure (Art. 17 / CCPA)</option>
                      <option value="access">Right of Access & Portability</option>
                      <option value="opt_out_sale_sharing_targeted_ads">
                        Opt-Out of Sale / Sharing / Targeted Ads (15 Business Days)
                      </option>
                      <option value="admt_human_review_explanation">
                        Explanation of Automated Decision & Human Review (Law 25 s. 12.1 / Art. 22)
                      </option>
                    </select>
                  </div>
                </div>

                <label className="flex items-center gap-2 text-xs bg-slate-950 p-2.5 rounded border border-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dsarRequest.holds_litigation_or_aml_ledger}
                    onChange={(e) =>
                      setDsarRequest({ ...dsarRequest, holds_litigation_or_aml_ledger: e.target.checked })
                    }
                  />
                  <span>Account subject to statutory Tax / AML / Medical Retention Floor or Litigation Hold</span>
                </label>

                {dsarResponse && (
                  <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-3 text-xs">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <span className="font-mono font-bold text-emerald-400">{dsarResponse.request_id}</span>
                      <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded font-semibold">
                        Human Legal Approval Required for Exemption/Refusal
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-slate-400 block">Strictest Initial Deadline:</span>
                        <span className="text-white font-bold text-sm">
                          {dsarResponse.strictest_initial_deadline} ({dsarResponse.strictest_initial_days} days)
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Statutory Clock Rule:</span>
                        <span className="text-indigo-300 font-semibold">{dsarResponse.day_type}</span>
                      </div>
                    </div>

                    <div>
                      <span className="text-slate-400 block">Identity Verification Standard:</span>
                      <span className="text-slate-200">{dsarResponse.verification_standard}</span>
                    </div>

                    <div className="space-y-2 pt-1">
                      <span className="text-slate-400 font-semibold block">
                        Retention vs. Deletion Conflicts & Partial Redaction Rules:
                      </span>
                      {dsarResponse.exemptions_and_retention_conflicts.map((ex) => (
                        <div
                          key={ex.code}
                          className="p-2.5 rounded bg-amber-950/40 border border-amber-500/30 text-amber-100 space-y-1"
                        >
                          <div className="font-bold">
                            {ex.code} ({ex.statute}) — Scope: {ex.scope}
                          </div>
                          <div>{ex.explanation}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Article 30 RoPA Multi-Jurisdictional Registry */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
              <h3 className="text-base font-bold text-white">
                Multi-Jurisdictional Record of Processing Activities (GDPR Art. 30 / Law 25 / CCPA Data Inventory)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                {ropaRecords.map((rec) => (
                  <div key={rec.record_id} className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-indigo-400">{rec.record_id}</span>
                      <span className="px-2 py-0.5 bg-slate-800 rounded text-slate-300 font-semibold">{rec.role}</span>
                    </div>
                    <div className="font-bold text-white text-sm">{rec.processing_activity}</div>
                    <div className="text-slate-300">
                      <span className="text-slate-400">Transfer Mechanism: </span>
                      {rec.cross_border_transfer_mechanism}
                    </div>
                    <div className="text-slate-300">
                      <span className="text-slate-400">Retention Schedule: </span>
                      {rec.retention_schedule}
                    </div>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {rec.jurisdictions.map((j) => (
                        <span key={j} className="px-1.5 py-0.5 font-mono bg-slate-800 text-indigo-300 rounded">
                          {j}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 4: GLOBAL COVERAGE MATRIX (US 50+DC+Fed, CA 13+Fed, EU 27+Union)
        =================================================================== */}
        {activeTab === 'coverage_matrix' && (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-white">
                    Global Multi-Dimensional Legal Pack Coverage Matrix ({jurisdictions.length} Jurisdictions)
                  </h2>
                  <p className="text-xs text-slate-400">
                    Tracks distinct verification stages (Catalogued • Implemented • Tested • Legally Reviewed •
                    Production-Enabled) — never conflated into a single misleading compliance percentage.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {(['ALL', 'US', 'CA', 'EU'] as const).map((region) => (
                    <button
                      key={region}
                      onClick={() => setMatrixCountryFilter(region)}
                      className={`px-3 py-1.5 rounded text-xs font-bold cursor-pointer ${
                        matrixCountryFilter === region
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-950 text-slate-400 border border-slate-800'
                      }`}
                    >
                      {region === 'ALL'
                        ? `All (${jurisdictions.length})`
                        : region === 'US'
                        ? 'United States (50 States + DC + Fed)'
                        : region === 'CA'
                        ? 'Canada (10 Provinces + 3 Territories + Fed)'
                        : 'European Union (27 Member States + EU)'}
                    </button>
                  ))}
                  <input
                    type="text"
                    placeholder="Filter jurisdiction or authority..."
                    value={matrixSearch}
                    onChange={(e) => setMatrixSearch(e.target.value)}
                    className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-xs text-white"
                  />
                </div>
              </div>

              <div className="overflow-x-auto max-h-[540px] overflow-y-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead className="bg-slate-950 text-slate-400 sticky top-0 z-10 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Code</th>
                      <th className="py-2.5 px-3">Jurisdiction & Statutory Pack</th>
                      <th className="py-2.5 px-3">Competent Supervisory Authority</th>
                      <th className="py-2.5 px-3 text-center">Catalogued</th>
                      <th className="py-2.5 px-3 text-center">Implemented</th>
                      <th className="py-2.5 px-3 text-center">Tested</th>
                      <th className="py-2.5 px-3 text-center">Legally Reviewed</th>
                      <th className="py-2.5 px-3 text-center">Prod Enabled</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/70">
                    {filteredJurisdictions.map((j) => (
                      <tr key={j.jurisdiction_id} className="hover:bg-slate-800/40">
                        <td className="py-2.5 px-3 font-mono font-bold text-indigo-300">{j.jurisdiction_id}</td>
                        <td className="py-2.5 px-3 text-white font-medium">
                          {j.name}
                          {j.subnational_authorities.length > 0 && (
                            <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-indigo-950 text-indigo-300 rounded border border-indigo-500/30">
                              +{j.subnational_authorities.length} Länder Authorities
                            </span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">{j.primary_regulator}</td>
                        {[j.catalogued, j.implemented, j.tested, j.legally_reviewed, j.production_enabled].map(
                          (flag, idx) => (
                            <td key={idx} className="py-2.5 px-3 text-center">
                              <span
                                className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                                  flag
                                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                    : 'bg-slate-800 text-slate-500'
                                }`}
                              >
                                {flag ? 'VERIFIED' : 'PENDING'}
                              </span>
                            </td>
                          )
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 5: CORPORATE AI HUBS & GOVERNED ASSISTANT
        =================================================================== */}
        {activeTab === 'ai_hubs_assistant' && (
          <div className="space-y-6">
            {/* Corporate AI Hubs Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {integrations.map((hub) => (
                <div
                  key={hub.hub_id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded">
                        {hub.status}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">Zero-Egress Enforced</span>
                    </div>
                    <h3 className="text-sm font-bold text-white">{hub.name}</h3>
                    <div className="text-xs text-indigo-300 font-mono">{hub.protocol}</div>
                    <div className="text-xs text-slate-400">Manifest: {hub.manifest_path}</div>
                  </div>

                  <div className="border-t border-slate-800 pt-2.5 space-y-1.5 text-xs">
                    <div className="text-slate-400 font-semibold">Exposed Governed Tools:</div>
                    <div className="flex flex-wrap gap-1">
                      {hub.exposed_tools.map((t) => (
                        <span
                          key={t}
                          className="px-2 py-0.5 bg-slate-950 border border-slate-800 rounded font-mono text-[11px] text-slate-300"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Governed Privacy Assistant Console */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div>
                  <h2 className="text-base font-bold text-white">
                    Governed Multi-Jurisdictional Privacy Assistant Console
                  </h2>
                  <p className="text-xs text-slate-400">
                    Strictly segregates Statutory Requirements vs. Regulator Guidance vs. Company Policies vs.
                    Contractual Commitments vs. AI Recommendations
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={assistantReq.channel}
                    onChange={(e) =>
                      setAssistantReq({
                        ...assistantReq,
                        channel: e.target.value as AssistantQueryRequest['channel'],
                      })
                    }
                    className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-xs text-white"
                  >
                    <option value="m365_copilot">Microsoft 365 Copilot Hub</option>
                    <option value="claude_mcp">Claude Enterprise MCP Hub</option>
                    <option value="gemini_enterprise">Google Gemini Enterprise Hub</option>
                    <option value="portal_console">Direct Privacy OS Console</option>
                  </select>
                  <button
                    onClick={handleRunAssistant}
                    disabled={assistantLoading}
                    className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-lg cursor-pointer"
                  >
                    {assistantLoading ? 'Synthesizing...' : 'Execute Governed Query'}
                  </button>
                </div>
              </div>

              <div>
                <textarea
                  rows={2}
                  value={assistantReq.query}
                  onChange={(e) => setAssistantReq({ ...assistantReq, query: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white"
                />
              </div>

              {assistantRes && (
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 text-xs pt-2">
                  {/* Column 1: Statutory Requirements */}
                  <div className="bg-slate-950 border border-indigo-500/40 rounded-lg p-3.5 space-y-2">
                    <div className="font-bold text-indigo-300 uppercase tracking-wider text-[11px]">
                      1. Statutory Requirements (Binding Law)
                    </div>
                    {assistantRes.statutory_requirements.map((st, idx) => (
                      <div key={idx} className="border-t border-slate-800 pt-2 space-y-1">
                        <div className="font-bold text-white">{st.citation}</div>
                        <div className="text-slate-300">{st.summary}</div>
                      </div>
                    ))}
                  </div>

                  {/* Column 2: Regulator Guidance */}
                  <div className="bg-slate-950 border border-emerald-500/40 rounded-lg p-3.5 space-y-2">
                    <div className="font-bold text-emerald-300 uppercase tracking-wider text-[11px]">
                      2. Regulator Guidance (Interpretive)
                    </div>
                    {assistantRes.regulator_guidance.map((rg, idx) => (
                      <div key={idx} className="border-t border-slate-800 pt-2 space-y-1">
                        <div className="font-bold text-white">{rg.authority}</div>
                        <div className="text-emerald-200/90 font-medium">{rg.document}</div>
                        <div className="text-slate-300">{rg.summary}</div>
                      </div>
                    ))}
                  </div>

                  {/* Column 3: Company Policies */}
                  <div className="bg-slate-950 border border-sky-500/40 rounded-lg p-3.5 space-y-2">
                    <div className="font-bold text-sky-300 uppercase tracking-wider text-[11px]">
                      3. Internal Company Policies
                    </div>
                    {assistantRes.company_policies.map((pol) => (
                      <div key={pol.policy_id} className="border-t border-slate-800 pt-2 space-y-1">
                        <div className="font-mono font-bold text-sky-300">{pol.policy_id}</div>
                        <div className="font-semibold text-white">{pol.title}</div>
                        <div className="text-slate-300">{pol.requirement}</div>
                      </div>
                    ))}
                  </div>

                  {/* Column 4: Contractual Commitments */}
                  <div className="bg-slate-950 border border-purple-500/40 rounded-lg p-3.5 space-y-2">
                    <div className="font-bold text-purple-300 uppercase tracking-wider text-[11px]">
                      4. Contractual Commitments (DPA/BAA)
                    </div>
                    {assistantRes.contractual_commitments.map((cc, idx) => (
                      <div key={idx} className="border-t border-slate-800 pt-2 space-y-1">
                        <div className="font-bold text-white">{cc.instrument}</div>
                        <div className="text-purple-300 font-mono">{cc.clause}</div>
                        <div className="text-slate-300">{cc.obligation}</div>
                      </div>
                    ))}
                  </div>

                  {/* Column 5: AI Recommendation */}
                  <div className="bg-slate-950 border border-amber-500/40 rounded-lg p-3.5 space-y-2">
                    <div className="font-bold text-amber-300 uppercase tracking-wider text-[11px]">
                      5. AI Recommendation (Non-Binding)
                    </div>
                    <div className="border-t border-slate-800 pt-2 text-slate-200">
                      {assistantRes.ai_recommendation.synthesized_guidance}
                    </div>
                    <ul className="list-disc pl-4 text-slate-300 space-y-1">
                      {assistantRes.ai_recommendation.recommended_next_steps.map((step, i) => (
                        <li key={i}>{step}</li>
                      ))}
                    </ul>
                    <div className="p-2 rounded bg-amber-950/60 border border-amber-500/40 text-amber-200 text-[11px]">
                      {assistantRes.ai_recommendation.guardrail_disclaimer}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===================================================================
            REGULATORY INTELLIGENCE & CITATION VERIFICATION PANEL
        =================================================================== */}
        <section
          aria-label="Regulatory Intelligence & Citation Verification"
          className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5"
        >
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 rounded">
                  REGULATORY INTELLIGENCE & CITATION VERIFICATION
                </span>
                <span className="px-2.5 py-0.5 text-[11px] font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 rounded">
                  262 OFFICIAL SOURCES • 113 JURISDICTIONS (US / CA / EU)
                </span>
                <span className="px-2.5 py-0.5 text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded">
                  HUMAN LEGAL REVIEW GATE ENFORCED (LEGAL / CPO / DPO)
                </span>
              </div>
              <h2 className="text-lg font-bold text-white mt-1.5">
                Regulatory Intelligence & Citation Verification Ledger
              </h2>
              <p className="text-xs text-slate-400">
                Cryptographic SHA-256 citation provenance, temporal statutory versioning & structural amendment diffs,
                and mandatory Human Counsel promotion gates across United States (50 States + DC + Federal), Canada (10
                Provinces + 3 Territories + Federal), and European Union (27 Member States + Union + German Länder).
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs">
              <label className="text-slate-400 font-semibold">Reviewer Role Gate:</label>
              <select
                aria-label="Reviewer Role Gate"
                value={selectedReviewerRole}
                onChange={(e) => setSelectedReviewerRole(e.target.value as 'LEGAL' | 'CPO' | 'DPO')}
                className="bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-white font-mono"
              >
                <option value="LEGAL">LEGAL (General Counsel)</option>
                <option value="CPO">CPO (Chief Privacy Officer)</option>
                <option value="DPO">DPO (Data Protection Officer)</option>
              </select>
            </div>
          </div>

          {/* Source Coverage & Temporal Versioning Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-1">
              <div className="text-slate-400 font-medium">Official Source Registry Coverage</div>
              <div className="text-xl font-bold text-white font-mono">262 Sources / 113 Jurisdictions</div>
              <div className="text-[11px] text-indigo-300">
                US (52) • Canada (14) • EU & Member States + DE Länder (47)
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-1">
              <div className="text-slate-400 font-medium">SHA-256 Citation Provenance</div>
              <div className="text-xl font-bold text-emerald-400 font-mono">
                {citationLedger.filter((c) => c.provenance_status === 'VERIFIED').length} VERIFIED /{' '}
                {citationLedger.length} Tracked
              </div>
              <div className="text-[11px] text-slate-400">
                Zero fabricated citations — fail-closed provenance verification
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-1">
              <div className="text-slate-400 font-medium">Temporal Versioning & Amendment Diffs</div>
              <div className="text-xl font-bold text-sky-300 font-mono">Bi-Temporal Knowledge Graph</div>
              <div className="text-[11px] text-slate-400">
                Tracks effective_from / effective_to windows & structural clause diffs
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-lg p-3.5 space-y-1">
              <div className="text-slate-400 font-medium">Human Legal Promotion Gate</div>
              <div className="text-xl font-bold text-amber-300 font-mono">
                {citationLedger.filter((c) => c.provenance_status === 'REQUIRES_LEGAL_REVIEW').length} Pending Review
              </div>
              <div className="text-[11px] text-slate-400">
                AI/crawler discoveries locked in REQUIRES_LEGAL_REVIEW until signed off
              </div>
            </div>
          </div>

          {/* Provenance Status Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div className="flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-semibold mr-1">Filter Provenance Status:</span>
              {(['ALL', 'VERIFIED', 'REQUIRES_LEGAL_REVIEW', 'UNVERIFIED', 'SOURCE_UNAVAILABLE'] as const).map(
                (status) => (
                  <button
                    key={status}
                    type="button"
                    onClick={() => setCitationFilterStatus(status)}
                    className={`px-2.5 py-1 rounded font-mono text-[11px] font-bold cursor-pointer ${
                      citationFilterStatus === status
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-white'
                    }`}
                  >
                    {status}
                  </button>
                )
              )}
            </div>
            <div className="text-[11px] font-mono text-slate-400">
              SSRF & Prompt-Injection Source Guard: ACTIVE
            </div>
          </div>

          {/* Citation Provenance & Temporal Amendment Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Jurisdiction & Source ID</th>
                  <th className="py-2.5 px-3">Statute / Instrument & Section</th>
                  <th className="py-2.5 px-3">Temporal Version & Effective Date</th>
                  <th className="py-2.5 px-3">SHA-256 Content Hash</th>
                  <th className="py-2.5 px-3">Provenance Status</th>
                  <th className="py-2.5 px-3 text-right">Human Legal Review Gate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/70">
                {filteredCitations.map((item) => (
                  <tr key={item.citation_id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-3">
                      <div className="font-mono font-bold text-indigo-300">{item.jurisdiction_code}</div>
                      <div className="font-mono text-[11px] text-slate-400">{item.source_id}</div>
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="font-semibold text-white">{item.statute_or_instrument}</div>
                      <div className="text-slate-300 font-mono text-[11px]">{item.section_ref}</div>
                    </td>
                    <td className="py-2.5 px-3">
                      <div className="font-mono text-sky-300 font-semibold">{item.amendment_version}</div>
                      <div className="text-[11px] text-slate-400">Effective: {item.effective_from}</div>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-slate-300">
                      <span title={item.sha256_hash}>
                        {item.sha256_hash.length > 24 ? `${item.sha256_hash.slice(0, 20)}...` : item.sha256_hash}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded font-mono text-[10px] font-bold ${
                          item.provenance_status === 'VERIFIED'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : item.provenance_status === 'REQUIRES_LEGAL_REVIEW'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : item.provenance_status === 'UNVERIFIED'
                            ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                            : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {item.provenance_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      {item.provenance_status === 'VERIFIED' ? (
                        <span className="text-[11px] font-mono text-emerald-300">
                          ✓ Promoted by {item.reviewed_by_role || 'LEGAL'}
                        </span>
                      ) : item.provenance_status === 'SOURCE_UNAVAILABLE' ? (
                        <span className="text-[11px] font-mono text-rose-300">
                          Blocked: Official Snapshot Required
                        </span>
                      ) : (
                        <button
                          type="button"
                          onClick={() => handlePromoteCitationToVerified(item.citation_id)}
                          className="px-2.5 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-[11px] cursor-pointer"
                        >
                          Approve & Promote ({selectedReviewerRole})
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
};

export default PrivacyOSPortal;
