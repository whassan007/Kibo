import { VITE_API_BASE } from './api';

// ============================================================================
// KIBO PRIVACY OS — ENTERPRISE PORTAL & MULTI-JURISDICTIONAL CLIENT SERVICE
// ============================================================================

export type JurisdictionType =
  | 'supranational'
  | 'federal'
  | 'state'
  | 'province'
  | 'territory'
  | 'member_state'
  | 'subnational'
  | 'sectoral';

export type RegulatoryStatus =
  | 'proposed'
  | 'enacted_not_effective'
  | 'effective'
  | 'amended'
  | 'repealed'
  | 'superseded'
  | 'under_legal_review';

export type DeploymentStatus =
  | 'discovered'
  | 'parsed'
  | 'tested'
  | 'legally_reviewed'
  | 'approved'
  | 'production_enabled';

export type LegalReviewStatus =
  | 'pending'
  | 'verified'
  | 'requires_counsel_signoff'
  | 'rejected';

export interface TenantIdentityContext {
  tenantId: string;
  userId: string;
  bearerToken: string;
}

export interface SubnationalAuthority {
  code: string;
  region: string;
  authority: string;
}

export interface JurisdictionEntry {
  jurisdiction_id: string;
  name: string;
  jurisdiction_type: JurisdictionType;
  country: string;
  state_or_province?: string | null;
  member_state?: string | null;
  parent_jurisdiction_id?: string | null;
  primary_regulator: string;
  regulator_url: string;
  subnational_authorities: SubnationalAuthority[];
  has_comprehensive_privacy_law: boolean;
  catalogued: boolean;
  implemented: boolean;
  tested: boolean;
  legally_reviewed: boolean;
  production_enabled: boolean;
}

export interface OrganizationProfileInput {
  name?: string;
  industry: string;
  organization_type: string;
  employee_count?: number;
  annual_revenue_usd?: number;
  consumer_records_count?: number;
  data_broker_revenue_pct?: number;
  is_federally_regulated_canada: boolean;
  hipaa_status?: string | null;
  role: string;
  establishments: string[];
  main_eu_establishment?: string | null;
  subnational_regions?: string[];
}

export interface ProcessingActivityInput {
  purpose: string;
  data_categories: string[];
  data_subject_categories: string[];
  subject_locations: string[];
  processing_locations: string[];
  transfer_destinations?: string[];
  third_party_processors: boolean;
  involves_ai_or_admt: boolean;
  involves_biometrics?: boolean;
  involves_children?: boolean;
  involves_targeted_advertising_or_cookies?: boolean;
  involves_cross_border_transfer?: boolean;
  targets_goods_or_services_to_subjects?: boolean;
  monitors_subject_behavior?: boolean;
  transfer_mechanisms_in_place?: string[];
}

export interface ApplicabilityEvaluationRequest {
  organization: OrganizationProfileInput;
  activity: ProcessingActivityInput;
  evaluation_date?: string;
  include_non_effective_laws?: boolean;
}

export interface ThresholdEvaluationItem {
  metric: string;
  operator: string;
  threshold_value: number | string;
  organization_value?: number | string | null;
  met: boolean;
  logic_group: string;
  description: string;
}

export interface ExemptionEvaluationItem {
  exemption_id: string;
  exemption_type: string;
  carve_out_statute?: string | null;
  applies: boolean;
  scope: string;
  description: string;
}

export interface ResponseDeadlineSpec {
  rights_request_initial_days?: number | null;
  rights_request_day_type: string;
  rights_request_extension_days?: number | null;
  rights_request_appeal_days?: number | null;
  identity_verification_required: boolean;
  breach_regulator_hours?: number | null;
  breach_regulator_days?: number | null;
  breach_regulator_text: string;
  breach_attorney_general_threshold_individuals?: number | null;
  breach_individual_notification_days?: number | null;
  breach_individual_text: string;
  cure_period_days?: number | null;
  record_retention_years?: number | null;
}

export interface ApplicableInstrumentOutcome {
  regulation_id: string;
  jurisdiction_id: string;
  legal_instrument: string;
  article_or_section: string;
  domain_category: string;
  applicability_status:
    | 'applicable'
    | 'applicable_future_preparation'
    | 'conditionally_applicable'
    | 'exempt'
    | 'preempted';
  applicability_reasoning: string;
  triggered_by_facts: string[];
  thresholds_evaluated: ThresholdEvaluationItem[];
  exemptions_evaluated: ExemptionEvaluationItem[];
  preemption_notes: string[];
  mandatory_controls: string[];
  required_assessments: string[];
  response_deadlines: ResponseDeadlineSpec;
  competent_authority: string;
  required_approval_gates: string[];
  required_evidence: string[];
  official_source_url: string;
  rule_version: string;
  regulatory_status: RegulatoryStatus;
  deployment_status: DeploymentStatus;
  legal_review_status: LegalReviewStatus;
  confidence: number;
  requires_legal_review: boolean;
}

export interface ConflictOrAmbiguityItem {
  conflict_id: string;
  regulations_involved: string[];
  jurisdictions_involved: string[];
  issue_type: string;
  description: string;
  sources: string[];
  resolution_strategy: string;
  requires_legal_review: boolean;
}

export interface ApplicabilityEvaluationResponse {
  evaluation_id: string;
  evaluated_at: string;
  evaluation_date: string;
  organization_summary: Record<string, unknown>;
  activity_summary: Record<string, unknown>;
  applicable_instruments: ApplicableInstrumentOutcome[];
  future_preparation_obligations: ApplicableInstrumentOutcome[];
  exempt_or_preempted_instruments: ApplicableInstrumentOutcome[];
  mandatory_controls: string[];
  required_assessments: string[];
  applicable_deadlines: Record<string, unknown>;
  responsible_authorities: Array<{ jurisdiction_id: string; authority: string; url?: string }>;
  lead_supervisory_authority?: {
    jurisdiction_id: string;
    authority: string;
    basis: string;
  } | null;
  cross_border_transfer_analysis: {
    cross_border_transfer_detected: boolean;
    required_mechanisms: string[];
    notes: string[];
  };
  required_approval_gates: string[];
  unresolved_questions: string[];
  conflicts_and_escalations: ConflictOrAmbiguityItem[];
  authoritative_source_links: Array<{ regulation_id: string; title: string; url: string }>;
  rule_versions: Record<string, string>;
  requires_legal_review: boolean;
  legal_review_reasons: string[];
}

// ============================================================================
// MULTI-JURISDICTION BREACH WAR ROOM SCHEMAS
// ============================================================================

export interface BreachIncidentInput {
  title: string;
  discovery_timestamp: string;
  jurisdictions: string[];
  affected_counts_by_jurisdiction: Record<string, number>;
  data_categories: string[];
  involves_phi: boolean;
  involves_financial: boolean;
  is_critical_infrastructure: boolean;
  risk_of_harm_level: 'low' | 'moderate' | 'high' | 'rrosh';
  encryption_or_safe_harbor_intact: boolean;
  description: string;
}

export interface BreachRegimeObligation {
  jurisdiction_id: string;
  regulation_id: string;
  regime_label: string;
  threshold_standard: string;
  threshold_met: boolean;
  regulator_authority: string;
  regulator_deadline_text: string;
  regulator_deadline_hours?: number | null;
  individual_notification_text: string;
  individual_deadline_days?: number | null;
  ag_or_media_trigger?: string | null;
  record_retention_requirement: string;
  requires_human_legal_approval: boolean;
  approval_status: 'pending_counsel_gate' | 'counsel_approved' | 'hold_privilege';
}

export interface BreachWarRoomResponse {
  incident_id: string;
  created_at: string;
  discovery_timestamp: string;
  strictest_regulator_deadline_hours: number | null;
  strictest_individual_deadline_days: number | null;
  qualitative_deadlines_require_immediate_review: boolean;
  unified_timeline: Array<{
    step_order: number;
    window: string;
    milestone: string;
    regimes_covered: string[];
    gate_type: 'automated_containment' | 'forensic_privilege' | 'human_legal_approval';
  }>;
  regime_evaluations: BreachRegimeObligation[];
  deduplicated_containment_tasks: Array<{
    task_id: string;
    category: string;
    task_title: string;
    satisfied_regimes: string[];
    owner_role: string;
    status: 'pending' | 'in_progress' | 'completed';
    requires_human_legal_approval: boolean;
  }>;
  requires_human_legal_approval: boolean;
}

// ============================================================================
// ASSESSMENTS, DSAR NEXUS & ROPA SCHEMAS
// ============================================================================

export interface AssessmentRecommendationRequest {
  activity_name: string;
  jurisdictions: string[];
  involves_high_risk_processing: boolean;
  involves_ai_or_admt: boolean;
  involves_cross_border_transfer: boolean;
  involves_phi_or_hin: boolean;
  relies_on_legitimate_interests: boolean;
  is_public_sector: boolean;
}

export interface RecommendedAssessmentTemplate {
  assessment_code: 'PIA' | 'DPIA' | 'PHIPA_TRA' | 'LAW25_TIA' | 'GDPR_LIA' | 'EU_AI_FRIA_ADMT';
  title: string;
  statutory_basis: string;
  jurisdiction_scope: string[];
  mandatory: boolean;
  trigger_reason: string;
  required_sections: string[];
  required_signoffs: string[];
}

export interface AssessmentRecommendationResponse {
  recommendation_id: string;
  assessments: RecommendedAssessmentTemplate[];
  requires_legal_review: boolean;
}

export interface DsarEvaluateRequest {
  subject_name_or_id: string;
  subject_residency: string;
  controller_establishments: string[];
  request_type:
    | 'access'
    | 'deletion_erasure'
    | 'correction_rectification'
    | 'portability'
    | 'opt_out_sale_sharing_targeted_ads'
    | 'limit_sensitive_pi'
    | 'admt_human_review_explanation'
    | 'withdraw_consent';
  received_at: string;
  is_complex_or_extended: boolean;
  holds_litigation_or_aml_ledger: boolean;
}

export interface DsarNexusEvaluationResponse {
  request_id: string;
  subject_residency: string;
  applicable_regimes: string[];
  strictest_initial_deadline: string;
  strictest_initial_days: number;
  day_type: string;
  acknowledgement_deadline?: string | null;
  extension_available_days: number;
  appeal_window_days?: number | null;
  verification_standard: string;
  exemptions_and_retention_conflicts: Array<{
    code: string;
    statute: string;
    scope: 'partial_redaction' | 'hold_deletion' | 'full_exemption';
    explanation: string;
  }>;
  requires_human_legal_approval: boolean;
}

export interface RopaRecord {
  record_id: string;
  processing_activity: string;
  role: 'Controller' | 'Processor' | 'Joint Controller';
  purposes: string[];
  legal_bases_gdpr: string[];
  data_subject_categories: string[];
  data_categories: string[];
  jurisdictions: string[];
  recipients_and_subprocessors: string[];
  cross_border_transfer_mechanism: string;
  retention_schedule: string;
  tom_security_controls: string[];
  linked_assessments: string[];
  last_verified: string;
}

// ============================================================================
// CORPORATE AI HUBS & GOVERNED ASSISTANT SCHEMAS
// ============================================================================

export interface AssistantQueryRequest {
  query: string;
  channel: 'm365_copilot' | 'claude_mcp' | 'gemini_enterprise' | 'portal_console';
  jurisdiction_context: string[];
}

export interface GovernedAssistantResponse {
  query_id: string;
  channel: string;
  evaluated_at: string;
  statutory_requirements: Array<{
    citation: string;
    jurisdiction: string;
    summary: string;
    official_url: string;
  }>;
  regulator_guidance: Array<{
    authority: string;
    document: string;
    summary: string;
  }>;
  company_policies: Array<{
    policy_id: string;
    title: string;
    requirement: string;
  }>;
  contractual_commitments: Array<{
    instrument: string;
    clause: string;
    obligation: string;
  }>;
  ai_recommendation: {
    synthesized_guidance: string;
    recommended_next_steps: string[];
    confidence: number;
    requires_legal_counsel_signoff: boolean;
    guardrail_disclaimer: string;
  };
}

export type OperationalDataStatus =
  | 'live'
  | 'updating'
  | 'stale'
  | 'offline'
  | 'demo'
  | 'error'
  | 'unverified';

export type WorkspaceRole =
  | 'CPO'
  | 'DPO'
  | 'ANALYST'
  | 'LEGAL'
  | 'SECURITY'
  | 'MANAGER'
  | 'EMPLOYEE'
  | 'AUDITOR'
  | 'ADMIN';

export interface AuthorizedOrganizationEntry {
  tenant_id: string;
  name: string;
  industry: string;
  jurisdictions: string[];
  is_empty_workspace: boolean;
  role: WorkspaceRole;
}

export interface VerifiedSessionInfo {
  user_id: string;
  display_name: string;
  email: string;
  role: WorkspaceRole;
  active_tenant_id: string;
  session_verified: boolean;
  auth_method: string;
  authorized_organizations: AuthorizedOrganizationEntry[];
  permissions: string[];
}

export interface AssessmentDraftRecord {
  draft_id: string;
  tenant_id: string;
  title: string;
  activity_name: string;
  jurisdictions: string[];
  current_step: number;
  answers: Record<string, string>;
  evidence_links: string[];
  status: 'draft' | 'submitted_for_review' | 'approved' | 'changes_requested';
  updated_at: string;
  reviewer_notes?: string;
}

export interface CorporateAiHubIntegrationStatus {
  hub_id: 'm365_copilot' | 'claude_mcp' | 'gemini_enterprise';
  name: string;
  protocol: string;
  manifest_path: string;
  status: 'connected' | 'degraded' | 'offline_demo' | 'offline';
  auth_mode: string;
  exposed_tools: string[];
  zero_egress_enforced: boolean;
  audit_trail_active: boolean;
  last_heartbeat: string;
  operational_state?: OperationalDataStatus;
}

// ============================================================================
// DEFAULT TENANT & IDENTITY HEADERS (SERVER-VERIFIED SESSION MODEL — UX-08)
// ============================================================================

const DEFAULT_AUTHORIZED_ORGANIZATIONS: AuthorizedOrganizationEntry[] = [
  {
    tenant_id: 'tnt-enterprise-global-001',
    name: 'Aegis Global Health & Financial Corp.',
    industry: 'Healthcare & Regulated Financial Services',
    jurisdictions: ['US-FED', 'US-CA', 'US-NY', 'CA-FED', 'CA-QC', 'CA-ON', 'EU-GDPR', 'EU-DE', 'EU-FR'],
    is_empty_workspace: false,
    role: 'CPO',
  },
  {
    tenant_id: 'tnt-eu-bank-sovereign-002',
    name: 'EuroSovereign Banque SA (Frankfurt / Paris)',
    industry: 'Banking & Capital Markets',
    jurisdictions: ['EU-GDPR', 'EU-DE', 'EU-FR', 'CA-QC', 'US-NY'],
    is_empty_workspace: false,
    role: 'DPO',
  },
  {
    tenant_id: 'tnt-new-onboarding-empty',
    name: 'NovaMed Regional Clinic (New Workspace)',
    industry: 'Healthcare Provider',
    jurisdictions: [],
    is_empty_workspace: true,
    role: 'CPO',
  },
];

let currentTenantContext: TenantIdentityContext = {
  tenantId: 'tnt-enterprise-global-001',
  userId: 'usr-cpo-counsel-01',
  bearerToken: 'kibo_ent_jwt_v1_verified_session',
};

let demoModeEnabled = false;
let lastOperationalStatus: OperationalDataStatus = 'updating';
const responseCache = new Map<string, { data: unknown; cachedAt: string }>();

export function setDemoModeEnabled(enabled: boolean): void {
  demoModeEnabled = enabled;
  if (enabled) {
    lastOperationalStatus = 'demo';
  }
}

export function isDemoModeEnabled(): boolean {
  return demoModeEnabled;
}

export function getLastOperationalStatus(): OperationalDataStatus {
  return demoModeEnabled ? 'demo' : lastOperationalStatus;
}

export function getAuthorizedOrganizations(): AuthorizedOrganizationEntry[] {
  return DEFAULT_AUTHORIZED_ORGANIZATIONS;
}

export function setPrivacyOsTenantContext(ctx: Partial<TenantIdentityContext>): void {
  // Enforce authorized organization membership check on client side as well as server side (UX-08)
  if (ctx.tenantId) {
    const allowed = DEFAULT_AUTHORIZED_ORGANIZATIONS.some((o) => o.tenant_id === ctx.tenantId);
    if (!allowed) {
      throw new Error(`Unauthorized tenant switch blocked: ${ctx.tenantId}`);
    }
  }
  currentTenantContext = { ...currentTenantContext, ...ctx };
}

export function getPrivacyOsTenantContext(): TenantIdentityContext {
  return currentTenantContext;
}

function buildHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'X-Tenant-ID': currentTenantContext.tenantId,
    'X-User-ID': currentTenantContext.userId,
    Authorization: `Bearer ${currentTenantContext.bearerToken}`,
    ...(extra || {}),
  };
}

async function apiRequestWithFallback<T>(
  path: string,
  options: RequestInit,
  fallbackFactory: () => T
): Promise<{ data: T; live: boolean; status: OperationalDataStatus; cachedAt?: string }> {
  const cacheKey = `${currentTenantContext.tenantId}:${options.method || 'GET'}:${path}`;
  if (demoModeEnabled) {
    lastOperationalStatus = 'demo';
    return { data: fallbackFactory(), live: false, status: 'demo' };
  }

  const baseUrl = VITE_API_BASE.replace(/\/api\/?$/, '');
  const url = path.startsWith('http') ? path : `${baseUrl}${path}`;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 3500);
    const response = await fetch(url, {
      ...options,
      headers: buildHeaders(options.headers as Record<string, string>),
      signal: controller.signal,
    });
    clearTimeout(timer);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const json = (await response.json()) as T;
    const now = new Date().toISOString();
    responseCache.set(cacheKey, { data: json, cachedAt: now });
    lastOperationalStatus = 'live';
    return { data: json, live: true, status: 'live', cachedAt: now };
  } catch {
    const cached = responseCache.get(cacheKey);
    if (cached) {
      lastOperationalStatus = 'stale';
      return {
        data: cached.data as T,
        live: false,
        status: 'stale',
        cachedAt: cached.cachedAt,
      };
    }
    lastOperationalStatus = 'offline';
    return { data: fallbackFactory(), live: false, status: 'offline' };
  }
}

// ============================================================================
// COMPLETE GLOBAL COVERAGE MATRIX DATA (US 50+DC+Fed, CA 13+Fed, EU 27+Union)
// ============================================================================

const US_STATES_LIST: Array<[string, string, boolean, string, string]> = [
  ['US-FED', 'United States (Federal — FTC / HHS OCR / GLBA / COPPA)', false, 'FTC, HHS OCR, CFPB, SEC', 'https://www.ftc.gov'],
  ['US-AL', 'Alabama', false, 'Office of the Alabama Attorney General', 'https://www.alabamaag.gov'],
  ['US-AK', 'Alaska', false, 'Alaska Department of Law (Attorney General)', 'https://law.alaska.gov'],
  ['US-AZ', 'Arizona', false, 'Arizona Attorney General Office', 'https://www.azag.gov'],
  ['US-AR', 'Arkansas', false, 'Arkansas Attorney General', 'https://arkansasag.gov'],
  ['US-CA', 'California (CCPA/CPRA/CMIA/CalECPA)', true, 'California Privacy Protection Agency (CalPrivacy) & CA AG', 'https://cppa.ca.gov'],
  ['US-CO', 'Colorado (CPA + AI Act)', true, 'Colorado Attorney General', 'https://coag.gov'],
  ['US-CT', 'Connecticut (CTDPA)', true, 'Connecticut Office of the Attorney General', 'https://portal.ct.gov/AG'],
  ['US-DE', 'Delaware (DPDPA)', true, 'Delaware Department of Justice', 'https://attorneygeneral.delaware.gov'],
  ['US-DC', 'District of Columbia', false, 'Office of the Attorney General for DC', 'https://oag.dc.gov'],
  ['US-FL', 'Florida (FDBR)', true, 'Florida Department of Legal Affairs', 'https://www.myfloridalegal.com'],
  ['US-GA', 'Georgia', false, 'Office of the Attorney General of Georgia', 'https://law.georgia.gov'],
  ['US-HI', 'Hawaii', false, 'Department of the Attorney General, Hawaii', 'https://ag.hawaii.gov'],
  ['US-ID', 'Idaho', false, 'Office of the Attorney General of Idaho', 'https://www.ag.idaho.gov'],
  ['US-IL', 'Illinois (BIPA / PIPA)', false, 'Illinois Attorney General', 'https://illinoisattorneygeneral.gov'],
  ['US-IN', 'Indiana (ICDPA)', true, 'Indiana Office of the Attorney General', 'https://www.in.gov/attorneygeneral'],
  ['US-IA', 'Iowa (ICDPA)', true, 'Office of the Attorney General of Iowa', 'https://www.iowaattorneygeneral.gov'],
  ['US-KS', 'Kansas', false, 'Kansas Attorney General', 'https://ag.ks.gov'],
  ['US-KY', 'Kentucky (KCDPA)', true, 'Kentucky Office of the Attorney General', 'https://www.ag.ky.gov'],
  ['US-LA', 'Louisiana', false, 'Louisiana Department of Justice', 'https://www.ag.state.la.us'],
  ['US-ME', 'Maine (ISP Privacy)', false, 'Office of the Maine Attorney General', 'https://www.maine.gov/ag'],
  ['US-MD', 'Maryland (MODPA)', true, 'Maryland Office of the Attorney General', 'https://www.marylandattorneygeneral.gov'],
  ['US-MA', 'Massachusetts (201 CMR 17.00)', false, 'Massachusetts Office of the Attorney General', 'https://www.mass.gov'],
  ['US-MI', 'Michigan', false, 'Michigan Department of Attorney General', 'https://www.michigan.gov/ag'],
  ['US-MN', 'Minnesota (MCDPA)', true, 'Office of the Minnesota Attorney General', 'https://www.ag.state.mn.us'],
  ['US-MS', 'Mississippi', false, 'Office of the Attorney General, Mississippi', 'https://www.ago.state.ms.us'],
  ['US-MO', 'Missouri', false, 'Missouri Attorney General Office', 'https://ago.mo.gov'],
  ['US-MT', 'Montana (MCDPA)', true, 'Montana Department of Justice', 'https://dojmt.gov'],
  ['US-NE', 'Nebraska (NDPA)', true, 'Nebraska Attorney General Office', 'https://ago.nebraska.gov'],
  ['US-NV', 'Nevada (NRS 603A + SB 370 Health)', false, 'Nevada Office of the Attorney General', 'https://ag.nv.gov'],
  ['US-NH', 'New Hampshire (NHPA)', true, 'New Hampshire Department of Justice', 'https://www.doj.nh.gov'],
  ['US-NJ', 'New Jersey (NJDPA)', true, 'New Jersey Office of the Attorney General', 'https://www.njoag.gov'],
  ['US-NM', 'New Mexico', false, 'New Mexico Department of Justice', 'https://nmdoj.gov'],
  ['US-NY', 'New York (SHIELD Act / NYDFS Part 500)', false, 'NY State Attorney General & NYDFS', 'https://ag.ny.gov'],
  ['US-NC', 'North Carolina', false, 'North Carolina Department of Justice', 'https://ncdoj.gov'],
  ['US-ND', 'North Dakota', false, 'North Dakota Office of Attorney General', 'https://attorneygeneral.nd.gov'],
  ['US-OH', 'Ohio', false, 'Ohio Attorney General', 'https://www.ohioattorneygeneral.gov'],
  ['US-OK', 'Oklahoma', false, 'Oklahoma Office of the Attorney General', 'https://oklahoma.gov/oag.html'],
  ['US-OR', 'Oregon (OCPA)', true, 'Oregon Department of Justice', 'https://www.doj.state.or.us'],
  ['US-PA', 'Pennsylvania', false, 'Pennsylvania Office of Attorney General', 'https://www.attorneygeneral.gov'],
  ['US-RI', 'Rhode Island (RIDTPPA)', true, 'Rhode Island Office of the Attorney General', 'https://riag.ri.gov'],
  ['US-SC', 'South Carolina', false, 'South Carolina Department of Consumer Affairs & AG', 'https://www.scag.gov'],
  ['US-SD', 'South Dakota', false, 'South Dakota Office of Attorney General', 'https://atg.sd.gov'],
  ['US-TN', 'Tennessee (TIPA)', true, 'Tennessee Office of the Attorney General', 'https://www.tn.gov/attorneygeneral'],
  ['US-TX', 'Texas (TDPSA / CUBI / HB 300)', true, 'Texas Office of the Attorney General', 'https://www.texasattorneygeneral.gov'],
  ['US-UT', 'Utah (UCPA)', true, 'Utah Office of the Attorney General', 'https://attorneygeneral.utah.gov'],
  ['US-VT', 'Vermont (Data Broker Regulation)', false, 'Vermont Office of the Attorney General', 'https://ago.vermont.gov'],
  ['US-VA', 'Virginia (VCDPA)', true, 'Office of the Attorney General of Virginia', 'https://www.oag.state.va.us'],
  ['US-WA', 'Washington (My Health My Data Act)', false, 'Washington State Office of the Attorney General', 'https://www.atg.wa.gov'],
  ['US-WV', 'West Virginia', false, 'West Virginia Office of the Attorney General', 'https://ago.wv.gov'],
  ['US-WI', 'Wisconsin', false, 'Wisconsin Department of Justice', 'https://www.doj.state.wi.us'],
  ['US-WY', 'Wyoming', false, 'Wyoming Office of the Attorney General', 'https://ag.wyo.gov'],
];

const CA_JURISDICTIONS_LIST: Array<[string, string, JurisdictionType, boolean, string, string]> = [
  ['CA-FED', 'Canada (Federal — PIPEDA / Privacy Act / CASL / OSFI B-13)', 'federal', true, 'Office of the Privacy Commissioner of Canada (OPC) & CRTC', 'https://www.priv.gc.ca'],
  ['CA-AB', 'Alberta (PIPA / HIA / FOIP)', 'province', true, 'Office of the Information and Privacy Commissioner of Alberta (OIPC-AB)', 'https://oipc.ab.ca'],
  ['CA-BC', 'British Columbia (PIPA / FIPPA)', 'province', true, 'Office of the Information and Privacy Commissioner for BC (OIPC-BC)', 'https://www.oipc.bc.ca'],
  ['CA-MB', 'Manitoba (FIPPA / PHIA)', 'province', false, 'Manitoba Ombudsman', 'https://www.ombudsman.mb.ca'],
  ['CA-NB', 'New Brunswick (RTIPPA / PHIPAA)', 'province', false, 'Office of the Ombud for New Brunswick', 'https://www.ombudnb.ca'],
  ['CA-NL', 'Newfoundland and Labrador (ATIPPA 2015 / PHIA)', 'province', false, 'OIPC Newfoundland and Labrador', 'https://www.oipc.nl.ca'],
  ['CA-NS', 'Nova Scotia (FOIPOP / PIIDPA / PHIA)', 'province', false, 'Information and Privacy Commissioner for Nova Scotia', 'https://oipc.novascotia.ca'],
  ['CA-ON', 'Ontario (PHIPA / FIPPA / MFIPPA / CYFSA)', 'province', false, 'Information and Privacy Commissioner of Ontario (IPC)', 'https://www.ipc.on.ca'],
  ['CA-PE', 'Prince Edward Island (FOIPP / HIPA)', 'province', false, 'Information and Privacy Commissioner of PEI', 'https://www.assembly.pe.ca/oipc'],
  ['CA-QC', 'Quebec (Law 25 / Private Sector Act / Act Respecting Access)', 'province', true, "Commission d'accès à l'information du Québec (CAI)", 'https://www.cai.gouv.qc.ca'],
  ['CA-SK', 'Saskatchewan (FOIP / LAFOIP / HIPA)', 'province', false, 'Saskatchewan Information and Privacy Commissioner (OIPC-SK)', 'https://oipc.sk.ca'],
  ['CA-NT', 'Northwest Territories (ATIPP / HIA)', 'territory', false, 'IPC of the Northwest Territories', 'https://atipp-nt.ca'],
  ['CA-NU', 'Nunavut (ATIPP)', 'territory', false, 'Information and Privacy Commissioner of Nunavut', 'https://atipp-nu.ca'],
  ['CA-YT', 'Yukon (ATIPP / HIPA)', 'territory', false, 'Yukon Information and Privacy Commissioner', 'https://yukonombudsman.ca'],
];

const EU_JURISDICTIONS_LIST: Array<[string, string, string, string, string]> = [
  ['EU', 'European Union (GDPR / EU AI Act / ePrivacy / NIS2 / DORA / DSA / Data Act)', 'EU', 'European Data Protection Board (EDPB), EDPS & European AI Office', 'https://www.edpb.europa.eu'],
  ['EU-AT', 'Austria (DSG)', 'AT', 'Österreichische Datenschutzbehörde (DSB)', 'https://www.dsb.gv.at'],
  ['EU-BE', 'Belgium (Loi du 30 juillet 2018)', 'BE', 'Autorité de protection des données / GBA (APD/GBA)', 'https://www.dataprotectionauthority.be'],
  ['EU-BG', 'Bulgaria (ZZLD)', 'BG', 'Commission for Personal Data Protection (CPDP)', 'https://www.cpdp.bg'],
  ['EU-HR', 'Croatia (ZZOP)', 'HR', 'Croatian Personal Data Protection Agency (AZOP)', 'https://azop.hr'],
  ['EU-CY', 'Cyprus (Law 125(I)/2018)', 'CY', 'Office of the Commissioner for Personal Data Protection', 'https://www.dataprotection.gov.cy'],
  ['EU-CZ', 'Czechia (Act No. 110/2019 Coll.)', 'CZ', 'Office for Personal Data Protection (ÚOOÚ)', 'https://www.uoou.cz'],
  ['EU-DK', 'Denmark (Databeskyttelsesloven)', 'DK', 'Datatilsynet', 'https://www.datatilsynet.dk'],
  ['EU-EE', 'Estonia (IKS)', 'EE', 'Estonian Data Protection Inspectorate (AKI)', 'https://www.aki.ee'],
  ['EU-FI', 'Finland (Tietosuojalaki 1050/2018)', 'FI', 'Office of the Data Protection Ombudsman', 'https://tietosuoja.fi'],
  ['EU-FR', 'France (Loi Informatique et Libertés)', 'FR', "Commission Nationale de l'Informatique et des Libertés (CNIL)", 'https://www.cnil.fr'],
  ['EU-DE', 'Germany (BDSG / TDDDG / 16 Länder Laws)', 'DE', 'BfDI & 17 Länder Supervisory Authorities (BayLDA, LDI NRW, HmbBfDI...)', 'https://www.bfdi.bund.de'],
  ['EU-GR', 'Greece (Law 4624/2019)', 'GR', 'Hellenic Data Protection Authority (HDPA)', 'https://www.dpa.gr'],
  ['EU-HU', 'Hungary (Info Act CXII/2011)', 'HU', 'NAIH', 'https://www.naih.hu'],
  ['EU-IE', 'Ireland (Data Protection Act 2018)', 'IE', 'Data Protection Commission (DPC)', 'https://www.dataprotection.ie'],
  ['EU-IT', 'Italy (Codice Privacy D.Lgs. 196/2003 & 101/2018)', 'IT', 'Garante per la protezione dei dati personali', 'https://www.garanteprivacy.it'],
  ['EU-LV', 'Latvia (FPDAL)', 'LV', 'Data State Inspectorate (DVI)', 'https://www.dvi.gov.lv'],
  ['EU-LT', 'Lithuania (ADTAĮ)', 'LT', 'State Data Protection Inspectorate (VDAI)', 'https://vdai.lrv.lt'],
  ['EU-LU', 'Luxembourg (Law of 1 August 2018)', 'LU', 'Commission Nationale pour la Protection des Données (CNPD)', 'https://cnpd.public.lu'],
  ['EU-MT', 'Malta (Data Protection Act Cap. 586)', 'MT', 'Office of the Information and Data Protection Commissioner (IDPC)', 'https://idpc.org.mt'],
  ['EU-NL', 'Netherlands (UAVG)', 'NL', 'Autoriteit Persoonsgegevens (AP)', 'https://autoriteitpersoonsgegevens.nl'],
  ['EU-PL', 'Poland (UODO Act of 10 May 2018)', 'PL', 'Personal Data Protection Office (UODO)', 'https://uodo.gov.pl'],
  ['EU-PT', 'Portugal (Lei n.º 58/2019)', 'PT', 'Comissão Nacional de Proteção de Dados (CNPD)', 'https://www.cnpd.pt'],
  ['EU-RO', 'Romania (Law 190/2018)', 'RO', 'ANSPDCP', 'https://www.dataprotection.ro'],
  ['EU-SK', 'Slovakia (Act No. 18/2018 Coll.)', 'SK', 'ÚOOÚ SR', 'https://dataprotection.gov.sk'],
  ['EU-SI', 'Slovenia (ZVOP-2)', 'SI', 'Information Commissioner of the Republic of Slovenia (IP RS)', 'https://www.ip-rs.si'],
  ['EU-ES', 'Spain (LOPDGDD 3/2018)', 'ES', 'Agencia Española de Protección de Datos (AEPD)', 'https://www.aepd.es'],
  ['EU-SE', 'Sweden (Dataskyddslagen 2018:218)', 'SE', 'Integritetsskyddsmyndigheten (IMY)', 'https://www.imy.se'],
];

export function buildFallbackJurisdictions(): JurisdictionEntry[] {
  const entries: JurisdictionEntry[] = [];

  for (const [id, name, hasComp, reg, url] of US_STATES_LIST) {
    entries.push({
      jurisdiction_id: id,
      name,
      jurisdiction_type: id === 'US-FED' ? 'federal' : 'state',
      country: 'US',
      state_or_province: id === 'US-FED' ? null : name,
      parent_jurisdiction_id: id === 'US-FED' ? null : 'US-FED',
      primary_regulator: reg,
      regulator_url: url,
      subnational_authorities: [],
      has_comprehensive_privacy_law: hasComp,
      catalogued: true,
      implemented: true,
      tested: true,
      legally_reviewed: true,
      production_enabled: true,
    });
  }

  for (const [id, name, jtype, hasComp, reg, url] of CA_JURISDICTIONS_LIST) {
    entries.push({
      jurisdiction_id: id,
      name,
      jurisdiction_type: jtype,
      country: 'CA',
      state_or_province: id === 'CA-FED' ? null : name,
      parent_jurisdiction_id: id === 'CA-FED' ? null : 'CA-FED',
      primary_regulator: reg,
      regulator_url: url,
      subnational_authorities: [],
      has_comprehensive_privacy_law: hasComp,
      catalogued: true,
      implemented: true,
      tested: true,
      legally_reviewed: true,
      production_enabled: true,
    });
  }

  for (const [id, name, iso, reg, url] of EU_JURISDICTIONS_LIST) {
    entries.push({
      jurisdiction_id: id,
      name,
      jurisdiction_type: id === 'EU' ? 'supranational' : 'member_state',
      country: iso,
      member_state: id === 'EU' ? null : name,
      parent_jurisdiction_id: id === 'EU' ? null : 'EU',
      primary_regulator: reg,
      regulator_url: url,
      subnational_authorities:
        id === 'EU-DE'
          ? [
              { code: 'DE-BY-PRIV', region: 'Bavaria (Private Sector)', authority: 'Bayerisches Landesamt für Datenschutzaufsicht (BayLDA)' },
              { code: 'DE-NW', region: 'North Rhine-Westphalia', authority: 'LDI NRW' },
              { code: 'DE-HH', region: 'Hamburg', authority: 'HmbBfDI' },
              { code: 'DE-BE', region: 'Berlin', authority: 'BlnBDI' },
              { code: 'DE-HE', region: 'Hesse', authority: 'HBDI' },
            ]
          : [],
      has_comprehensive_privacy_law: true,
      catalogued: true,
      implemented: true,
      tested: true,
      legally_reviewed: true,
      production_enabled: true,
    });
  }

  return entries;
}

// ============================================================================
// DETERMINISTIC CLIENT-SIDE FALLBACK EVALUATOR FOR JRAE
// ============================================================================

function buildFallbackEvaluation(req: ApplicabilityEvaluationRequest): ApplicabilityEvaluationResponse {
  const org = req.organization;
  const act = req.activity;
  const allJurs = new Set<string>([
    ...org.establishments,
    ...act.subject_locations,
    ...act.processing_locations,
  ]);

  const instruments: ApplicableInstrumentOutcome[] = [];
  const exemptOrPreempted: ApplicableInstrumentOutcome[] = [];
  const conflicts: ConflictOrAmbiguityItem[] = [];
  const authorities: Array<{ jurisdiction_id: string; authority: string; url?: string }> = [];

  const revUsd = org.annual_revenue_usd ?? 45000000;
  const recordsCount = org.consumer_records_count ?? 185000;
  const brokerPct = org.data_broker_revenue_pct ?? 10;

  // 1. California CCPA/CPRA
  if (allJurs.has('US-CA') || act.subject_locations.includes('US-CA')) {
    const revMet = revUsd >= 26625000;
    const recMet = recordsCount >= 100000;
    const brkMet = brokerPct >= 50;
    const ccpaMet = revMet || recMet || brkMet;

    const phiTriggered = act.data_categories.includes('phi') || org.hipaa_status === 'covered_entity';

    if (ccpaMet) {
      instruments.push({
        regulation_id: 'US-CA-CCPA-CPRA',
        jurisdiction_id: 'US-CA',
        legal_instrument: 'California Consumer Privacy Act (as amended by CPRA) & CalPrivacy ADMT Regulations',
        article_or_section: 'Cal. Civ. Code § 1798.100 et seq.; 11 CCR § 7000 et seq.',
        domain_category: 'privacy',
        applicability_status: 'applicable',
        applicability_reasoning:
          'Organization conducts business in California or targets California residents and satisfies at least one statutory threshold under Cal. Civ. Code § 1798.140(d)(1).',
        triggered_by_facts: [
          `Annual gross revenue ($${revUsd.toLocaleString()}) evaluated against $26,625,000 CPI-adjusted threshold`,
          `California consumer/household records (${recordsCount.toLocaleString()}) >= 100,000 threshold`,
          act.involves_ai_or_admt ? 'Automated Decision-Making Technology (ADMT) pre-use notice & opt-out triggered' : 'Standard consumer data processing',
        ],
        thresholds_evaluated: [
          {
            metric: 'annual_revenue_usd',
            operator: '>=',
            threshold_value: 26625000,
            organization_value: revUsd,
            met: revMet,
            logic_group: 'OR',
            description: 'Gross annual revenue exceeds $26,625,000 (CalPrivacy CPI-adjusted threshold)',
          },
          {
            metric: 'consumer_records_count',
            operator: '>=',
            threshold_value: 100000,
            organization_value: recordsCount,
            met: recMet,
            logic_group: 'OR',
            description: 'Annually buys, sells, or shares personal information of >= 100,000 California consumers or households',
          },
          {
            metric: 'data_broker_revenue_pct',
            operator: '>=',
            threshold_value: 50,
            organization_value: brokerPct,
            met: brkMet,
            logic_group: 'OR',
            description: 'Derives >= 50% of annual revenue from selling or sharing consumers personal information',
          },
        ],
        exemptions_evaluated: [
          {
            exemption_id: 'CCPA-EX-HIPAA-CMIA',
            exemption_type: 'data_level',
            carve_out_statute: 'Cal. Civ. Code § 1798.145(c)(1) (HIPAA PHI & CMIA Medical Information)',
            applies: Boolean(phiTriggered),
            scope: phiTriggered
              ? 'Data-level partial exemption: PHI governed by HIPAA/CMIA is carved out, but non-PHI website, marketing, and HR records remain subject to CCPA/CPRA.'
              : 'Not triggered for non-clinical datasets.',
            description: 'Data-level carve-out for Protected Health Information under HIPAA and medical information under CMIA.',
          },
          {
            exemption_id: 'CCPA-EX-GLBA',
            exemption_type: 'data_level',
            carve_out_statute: 'Cal. Civ. Code § 1798.145(e) (GLBA NPI)',
            applies: act.data_categories.includes('financial'),
            scope: 'Data-level exemption for nonpublic personal information subject to GLBA; entity-level exemption does NOT apply in California.',
            description: 'GLBA data-level exemption (retains private right of action under § 1798.150 for data breaches).',
          },
        ],
        preemption_notes: [
          'HIPAA preempts weaker state laws but yields to more stringent privacy rules under 45 CFR § 160.203(b) (California CMIA & CCPA non-PHI split applies).',
        ],
        mandatory_controls: [
          'Notice at Collection & Privacy Policy with 12-month category disclosures',
          'Universal Opt-Out Mechanism (UOOM / Global Privacy Control) signal recognition',
          'Do Not Sell or Share My Personal Information & Limit Sensitive PI links',
          ...(act.involves_ai_or_admt ? ['CalPrivacy ADMT Pre-Use Notice, Access to Logic & Human Review Opt-Out'] : []),
        ],
        required_assessments: [
          'CalPrivacy Risk Assessment for High-Risk Processing',
          ...(act.involves_ai_or_admt ? ['CalPrivacy ADMT Impact Assessment'] : []),
        ],
        response_deadlines: {
          rights_request_initial_days: 45,
          rights_request_day_type: 'calendar_days (+ 10 business days acknowledgement; 15 business days for opt-out)',
          rights_request_extension_days: 45,
          rights_request_appeal_days: null,
          identity_verification_required: true,
          breach_regulator_hours: null,
          breach_regulator_days: null,
          breach_regulator_text: 'Without unreasonable delay; CA Attorney General sample notice required if >= 500 CA residents affected',
          breach_attorney_general_threshold_individuals: 500,
          breach_individual_notification_days: null,
          breach_individual_text: 'Most expedient time possible and without unreasonable delay',
          cure_period_days: null,
          record_retention_years: 2,
        },
        competent_authority: 'California Privacy Protection Agency (CalPrivacy) & California Attorney General',
        required_approval_gates: ['DPO / Privacy Counsel Sign-off on ADMT & Risk Assessment', 'Legal Review of Data-Level Carve-Out Split'],
        required_evidence: ['24-Month DSAR Metrics Log', 'Vendor Service Provider Addendum (Cal. Civ. Code § 1798.100(d))'],
        official_source_url: 'https://cppa.ca.gov/regulations/',
        rule_version: '2026.10.1',
        regulatory_status: 'effective',
        deployment_status: 'production_enabled',
        legal_review_status: 'verified',
        confidence: 0.99,
        requires_legal_review: Boolean(phiTriggered || act.involves_ai_or_admt),
      });
      authorities.push({
        jurisdiction_id: 'US-CA',
        authority: 'California Privacy Protection Agency (CalPrivacy) & California Attorney General',
        url: 'https://cppa.ca.gov',
      });
    }
  }

  // 2. US Federal HIPAA / HITECH (if PHI or HIPAA status)
  if (
    act.data_categories.includes('phi') ||
    org.hipaa_status === 'covered_entity' ||
    org.hipaa_status === 'business_associate'
  ) {
    instruments.push({
      regulation_id: 'US-FED-HIPAA-PRIVACY-SECURITY-BREACH',
      jurisdiction_id: 'US-FED',
      legal_instrument: 'HIPAA Privacy, Security, and Breach Notification Rules (45 CFR Parts 160 & 164)',
      article_or_section: '45 CFR §§ 164.302–318, 164.400–414, 164.500–534',
      domain_category: 'health_privacy',
      applicability_status: 'applicable',
      applicability_reasoning:
        'Organization acts as a HIPAA Covered Entity or Business Associate processing Protected Health Information (PHI).',
      triggered_by_facts: [
        `HIPAA status: ${org.hipaa_status || 'covered_entity / PHI processor'}`,
        'Data categories include Protected Health Information (PHI)',
      ],
      thresholds_evaluated: [
        {
          metric: 'hipaa_covered_or_ba_status',
          operator: 'in',
          threshold_value: 'covered_entity | business_associate',
          organization_value: org.hipaa_status || 'covered_entity',
          met: true,
          logic_group: 'AND',
          description: 'Applies to all HIPAA Covered Entities and Business Associates regardless of revenue size',
        },
      ],
      exemptions_evaluated: [],
      preemption_notes: [
        '45 CFR § 160.203(b): HIPAA preempts contrary state law EXCEPT where state law relates to privacy of individually identifiable health information and is MORE STRINGENT (e.g., California CMIA, Texas HB 300, Ontario PHIPA cross-border).',
      ],
      mandatory_controls: [
        'Business Associate Agreements (BAAs) under 45 CFR § 164.504(e)',
        'Administrative, Physical, and Technical Safeguards (45 CFR § 164.308–312)',
        'Minimum Necessary Standard & Notice of Privacy Practices (NPP)',
      ],
      required_assessments: ['HIPAA Security Risk Analysis (45 CFR § 164.308(a)(1)(ii)(A))'],
      response_deadlines: {
        rights_request_initial_days: 30,
        rights_request_day_type: 'calendar_days',
        rights_request_extension_days: 30,
        rights_request_appeal_days: null,
        identity_verification_required: true,
        breach_regulator_hours: 1440,
        breach_regulator_days: 60,
        breach_regulator_text: 'Without unreasonable delay and no later than 60 calendar days from discovery to HHS OCR (if >= 500 affected; otherwise annual log)',
        breach_attorney_general_threshold_individuals: 500,
        breach_individual_notification_days: 60,
        breach_individual_text: 'Without unreasonable delay and in no case later than 60 calendar days after discovery',
        cure_period_days: null,
        record_retention_years: 6,
      },
      competent_authority: 'U.S. Department of Health and Human Services — Office for Civil Rights (HHS OCR)',
      required_approval_gates: ['Privacy Officer & Security Officer Sign-off on BAA & Risk Analysis'],
      required_evidence: ['6-Year HIPAA Documentation Retention Archive', 'Signed Business Associate Inventory'],
      official_source_url: 'https://www.hhs.gov/hipaa/index.html',
      rule_version: '2026.10.1',
      regulatory_status: 'effective',
      deployment_status: 'production_enabled',
      legal_review_status: 'verified',
      confidence: 0.99,
      requires_legal_review: true,
    });

    conflicts.push({
      conflict_id: 'CONF-HIPAA-STATE-PREEMPTION-SPLIT',
      regulations_involved: ['US-FED-HIPAA-PRIVACY-SECURITY-BREACH', 'US-CA-CCPA-CPRA', 'CA-ON-PHIPA'],
      jurisdictions_involved: ['US-FED', 'US-CA', 'CA-ON'],
      issue_type: 'preemption_split',
      description:
        'Entity-level vs. data-level carve-out split: HIPAA governs clinical PHI, whereas CCPA/CPRA continues to govern non-PHI consumer telemetry, HR data, and marketing pixels on non-authenticated pages.',
      sources: ['45 CFR § 160.203(b)', 'Cal. Civ. Code § 1798.145(c)(1)'],
      resolution_strategy:
        'Partition data inventory by dataset classification: apply HIPAA/CMIA controls to clinical PHI repositories and CCPA/CPRA consumer rights & opt-out controls to non-PHI web/CRM datasets.',
      requires_legal_review: true,
    });
  }

  // 3. Canada — Quebec Law 25
  if (allJurs.has('CA-QC')) {
    instruments.push({
      regulation_id: 'CA-QC-LAW25',
      jurisdiction_id: 'CA-QC',
      legal_instrument: 'Quebec Act Respecting the Protection of Personal Information in the Private Sector (as modernized by Law 25 / Bill 64)',
      article_or_section: 'CQLR c. P-39.1, ss. 3.1, 3.3, 3.5, 12.1, 17, 32',
      domain_category: 'privacy',
      applicability_status: 'applicable',
      applicability_reasoning:
        'Quebec Law 25 is deemed substantially similar to PIPEDA for intra-provincial processing in Quebec and applies extraterritorially where Quebec residents personal information is collected or transferred outside Quebec.',
      triggered_by_facts: [
        'Quebec establishment or data subjects located in Quebec (CA-QC)',
        'Cross-border communication of personal information outside Quebec requires a mandatory Transfer Impact Assessment (s. 17)',
      ],
      thresholds_evaluated: [
        {
          metric: 'quebec_personal_information_nexus',
          operator: '==',
          threshold_value: 'true',
          organization_value: 'true',
          met: true,
          logic_group: 'AND',
          description: 'Applies to any enterprise carrying on an enterprise in Quebec or processing personal information of Quebec residents (no revenue floor)',
        },
      ],
      exemptions_evaluated: [],
      preemption_notes: [
        'Substantially similar provincial private-sector law displaces PIPEDA for intra-provincial commercial activities in Quebec; PIPEDA continues to apply to interprovincial/international transfers and federal works/undertakings.',
      ],
      mandatory_controls: [
        'Designation of Person in Charge of Personal Information (Privacy Officer) published on website (s. 3.1)',
        'Highest-Privacy-by-Default Configuration for Technological Products/Services (s. 9.1)',
        'Confidentiality Incident Register maintained for 5 years & CAI notification on risk of serious injury (s. 3.5)',
        'Automated Decision Disclosure & Right to Submit Observations to Human Reviewer (s. 12.1)',
      ],
      required_assessments: [
        'Quebec Law 25 Privacy Impact Assessment (EFVP / PIA) for IS acquisition/overhaul (s. 3.3)',
        'Quebec Law 25 Cross-Border Transfer Impact Assessment (TIA) before communicating PI outside Quebec (s. 17)',
      ],
      response_deadlines: {
        rights_request_initial_days: 30,
        rights_request_day_type: 'calendar_days (strict; no unilateral administrative extension — refusal/CAI review clock runs 30 days)',
        rights_request_extension_days: 0,
        rights_request_appeal_days: 30,
        identity_verification_required: true,
        breach_regulator_hours: null,
        breach_regulator_days: null,
        breach_regulator_text: 'Promptly (avec diligence) to Commission d’accès à l’information (CAI) when incident presents a risk of serious injury',
        breach_attorney_general_threshold_individuals: null,
        breach_individual_notification_days: null,
        breach_individual_text: 'Promptly to any person whose personal information is concerned if risk of serious injury',
        cure_period_days: null,
        record_retention_years: 5,
      },
      competent_authority: "Commission d'accès à l'information du Québec (CAI)",
      required_approval_gates: ['Privacy Officer Sign-off on Law 25 s. 17 Transfer Impact Assessment', 'Written Cross-Border Data Protection Agreement'],
      required_evidence: ['Law 25 s. 17 TIA Report', '5-Year Confidentiality Incident Register'],
      official_source_url: 'https://www.cai.gouv.qc.ca',
      rule_version: '2026.10.1',
      regulatory_status: 'effective',
      deployment_status: 'production_enabled',
      legal_review_status: 'verified',
      confidence: 0.99,
      requires_legal_review: true,
    });
    authorities.push({
      jurisdiction_id: 'CA-QC',
      authority: "Commission d'accès à l'information du Québec (CAI)",
      url: 'https://www.cai.gouv.qc.ca',
    });
  }

  // 4. Canada — Ontario PHIPA & Federal PIPEDA
  if (allJurs.has('CA-ON') || allJurs.has('CA-FED')) {
    if (allJurs.has('CA-ON') && (act.data_categories.includes('phi') || org.organization_type === 'health_information_custodian')) {
      instruments.push({
        regulation_id: 'CA-ON-PHIPA',
        jurisdiction_id: 'CA-ON',
        legal_instrument: 'Ontario Personal Health Information Protection Act, 2004 (PHIPA)',
        article_or_section: 'S.O. 2004, c. 3, Sched. A, ss. 10, 12, 52–55',
        domain_category: 'health_privacy',
        applicability_status: 'applicable',
        applicability_reasoning:
          'Applies to Health Information Custodians (HICs) and their Electronic Service Providers / Agents handling Personal Health Information (PHI) in Ontario.',
        triggered_by_facts: ['Ontario nexus (CA-ON)', 'Health Information Custodian / PHI processing'],
        thresholds_evaluated: [],
        exemptions_evaluated: [],
        preemption_notes: [
          'PHIPA is declared substantially similar to PIPEDA for health information custodians in Ontario.',
        ],
        mandatory_controls: [
          'Information Practices Statement & Lock-Box Consent Management',
          'Electronic Audit Log of all PHI accesses (s. 10(3))',
          'Notification to IPC Ontario at first reasonable opportunity under prescribed breach scenarios (s. 12(2))',
        ],
        required_assessments: ['Ontario PHIPA Threat & Risk Assessment (TRA) & Privacy Impact Assessment (PIA)'],
        response_deadlines: {
          rights_request_initial_days: 30,
          rights_request_day_type: 'calendar_days',
          rights_request_extension_days: 30,
          rights_request_appeal_days: null,
          identity_verification_required: true,
          breach_regulator_hours: null,
          breach_regulator_days: null,
          breach_regulator_text: 'At the first reasonable opportunity to IPC Ontario + Annual Statistical Report by March 1',
          breach_attorney_general_threshold_individuals: null,
          breach_individual_notification_days: null,
          breach_individual_text: 'At the first reasonable opportunity to the individual',
          cure_period_days: null,
          record_retention_years: 2,
        },
        competent_authority: 'Information and Privacy Commissioner of Ontario (IPC)',
        required_approval_gates: ['HIC Privacy Contact Approval for Electronic Service Provider Agreement'],
        required_evidence: ['PHIPA TRA & PIA Artifact', 'Annual March 1 IPC Breach Statistics Log'],
        official_source_url: 'https://www.ipc.on.ca',
        rule_version: '2026.10.1',
        regulatory_status: 'effective',
        deployment_status: 'production_enabled',
        legal_review_status: 'verified',
        confidence: 0.99,
        requires_legal_review: true,
      });
      authorities.push({
        jurisdiction_id: 'CA-ON',
        authority: 'Information and Privacy Commissioner of Ontario (IPC)',
        url: 'https://www.ipc.on.ca',
      });
    }

    instruments.push({
      regulation_id: 'CA-FED-PIPEDA',
      jurisdiction_id: 'CA-FED',
      legal_instrument: 'Personal Information Protection and Electronic Documents Act (PIPEDA)',
      article_or_section: 'S.C. 2000, c. 5, s. 8, s. 10.1–10.3, Schedule 1',
      domain_category: 'privacy',
      applicability_status: 'applicable',
      applicability_reasoning:
        'Applies to commercial activities in provinces without substantially similar general private-sector legislation (e.g., Ontario commercial non-PHI), to all interprovincial/international personal information transfers, and to federal works, undertakings, or businesses.',
      triggered_by_facts: [
        'Canadian commercial processing & cross-border/interprovincial data flows',
        org.is_federally_regulated_canada ? 'Federally regulated work, undertaking, or business (FWUB) — employee data also covered' : 'Commercial activity nexus',
      ],
      thresholds_evaluated: [],
      exemptions_evaluated: [],
      preemption_notes: [
        'Yields to Quebec Law 25, Alberta PIPA, and BC PIPA exclusively for intra-provincial commercial processing; retains jurisdiction over cross-border transfers.',
      ],
      mandatory_controls: [
        'Meaningful Consent (OPC Guidelines) & Accountability Program (Schedule 1 Principle 4.1)',
        'Mandatory Breach of Security Safeguards Record Retention for 24 months (PIPEDA Breach Regulations s. 6)',
        'Comparable Level of Protection via Contract for Cross-Border Transfers (Principle 4.1.3)',
      ],
      required_assessments: ['PIPEDA Cross-Border Accountability & Sensitivity Assessment'],
      response_deadlines: {
        rights_request_initial_days: 30,
        rights_request_day_type: 'calendar_days',
        rights_request_extension_days: 30,
        rights_request_appeal_days: null,
        identity_verification_required: true,
        breach_regulator_hours: null,
        breach_regulator_days: null,
        breach_regulator_text: 'As soon as feasible after determining Real Risk of Significant Harm (RROSH) to OPC',
        breach_attorney_general_threshold_individuals: null,
        breach_individual_notification_days: null,
        breach_individual_text: 'As soon as feasible after determining Real Risk of Significant Harm (RROSH)',
        cure_period_days: null,
        record_retention_years: 2,
      },
      competent_authority: 'Office of the Privacy Commissioner of Canada (OPC)',
      required_approval_gates: ['RROSH Determination Sign-off by Privacy Officer'],
      required_evidence: ['24-Month Breach of Security Safeguards Ledger (including non-reportable incidents)'],
      official_source_url: 'https://www.priv.gc.ca',
      rule_version: '2026.10.1',
      regulatory_status: 'effective',
      deployment_status: 'production_enabled',
      legal_review_status: 'verified',
      confidence: 0.99,
      requires_legal_review: false,
    });
    authorities.push({
      jurisdiction_id: 'CA-FED',
      authority: 'Office of the Privacy Commissioner of Canada (OPC)',
      url: 'https://www.priv.gc.ca',
    });
  }

  // 5. European Union GDPR + Member State Derogations (e.g., EU-IE, EU-DE, EU-FR) + EU AI Act
  const hasEuNexus = Array.from(allJurs).some((j) => j === 'EU' || j.startsWith('EU-'));
  if (hasEuNexus) {
    instruments.push({
      regulation_id: 'EU-GDPR-2016-679',
      jurisdiction_id: 'EU',
      legal_instrument: 'General Data Protection Regulation (Regulation (EU) 2016/679)',
      article_or_section: 'Arts. 3(1)–3(2), 6, 9, 12–22, 28, 30, 32–36, 44–49, 56',
      domain_category: 'privacy',
      applicability_status: 'applicable',
      applicability_reasoning:
        'Triggered under GDPR Art. 3(1) (EU establishment processing) and/or Art. 3(2) (offering goods/services to or monitoring behavior of data subjects in the European Union).',
      triggered_by_facts: [
        `EU Establishments / Subject Locations: ${Array.from(allJurs).filter((j) => j === 'EU' || j.startsWith('EU-')).join(', ')}`,
        'Cross-border processing across EU Member States triggers Art. 56 One-Stop-Shop Lead Supervisory Authority evaluation',
      ],
      thresholds_evaluated: [
        {
          metric: 'gdpr_art3_territorial_scope',
          operator: '==',
          threshold_value: 'true',
          organization_value: 'true',
          met: true,
          logic_group: 'AND',
          description: 'GDPR Art. 3(1) Establishment or Art. 3(2) Targeting / Monitoring in the Union',
        },
      ],
      exemptions_evaluated: [],
      preemption_notes: [
        'Directly applicable across all 27 EU Member States; Member State opening clauses govern employee data (Art. 88 / Germany BDSG § 26), digital consent age (Art. 8: 13–16 yrs), and health/genetic data (Art. 9(4)).',
      ],
      mandatory_controls: [
        'Article 30 Record of Processing Activities (RoPA)',
        'Article 28 Data Processing Agreements (DPAs) with all Subprocessors',
        'Chapter V Cross-Border Transfer Safeguards (EU SCCs + Supplementary Measures / EU-US DPF)',
        '72-Hour Supervisory Authority Breach Notification Pipeline (Art. 33)',
      ],
      required_assessments: [
        'GDPR Article 35 Data Protection Impact Assessment (DPIA)',
        'Schrems II / EDPB Transfer Impact Assessment (TIA)',
        'Legitimate Interests Assessment (LIA) if relying on Art. 6(1)(f)',
      ],
      response_deadlines: {
        rights_request_initial_days: 30,
        rights_request_day_type: '1 calendar month (extendable by 2 further calendar months under Art. 12(3))',
        rights_request_extension_days: 60,
        rights_request_appeal_days: null,
        identity_verification_required: true,
        breach_regulator_hours: 72,
        breach_regulator_days: 3,
        breach_regulator_text: 'Without undue delay and, where feasible, not later than 72 hours after having become aware of it (Art. 33(1))',
        breach_attorney_general_threshold_individuals: null,
        breach_individual_notification_days: null,
        breach_individual_text: 'Without undue delay when personal data breach is likely to result in a high risk (Art. 34(1))',
        cure_period_days: null,
        record_retention_years: 5,
      },
      competent_authority: org.main_eu_establishment === 'EU-IE'
        ? 'Data Protection Commission (DPC Ireland — Lead Supervisory Authority under Art. 56)'
        : 'European Data Protection Board (EDPB) & Competent National DPAs (DPC Ireland, BfDI/BayLDA Germany, CNIL France)',
      required_approval_gates: ['EU DPO Sign-off on Art. 35 DPIA', 'Legal Counsel Sign-off on Chapter V SCCs + TIA'],
      required_evidence: ['Article 30 RoPA Export', 'Signed EU Standard Contractual Clauses (Module 2/3)'],
      official_source_url: 'https://eur-lex.europa.eu/eli/reg/2016/679/oj',
      rule_version: '2026.10.1',
      regulatory_status: 'effective',
      deployment_status: 'production_enabled',
      legal_review_status: 'verified',
      confidence: 0.99,
      requires_legal_review: true,
    });

    if (allJurs.has('EU-DE')) {
      instruments.push({
        regulation_id: 'EU-DE-BDSG-TDDDG',
        jurisdiction_id: 'EU-DE',
        legal_instrument: 'German Federal Data Protection Act (BDSG) & Telecommunications Digital Services Data Protection Act (TDDDG)',
        article_or_section: 'BDSG §§ 26, 38; TDDDG § 25',
        domain_category: 'privacy',
        applicability_status: 'applicable',
        applicability_reasoning:
          'German national derogations under GDPR opening clauses: mandatory DPO appointment threshold (§ 38 BDSG >= 20 employees processing automated personal data) and employment data rules (§ 26 BDSG).',
        triggered_by_facts: [
          'German establishment or data subjects in Germany (EU-DE)',
          'Subnational Länder supervisory authority routing (e.g. BayLDA Bavaria / LDI NRW)',
        ],
        thresholds_evaluated: [
          {
            metric: 'german_automated_processing_employees',
            operator: '>=',
            threshold_value: 20,
            organization_value: org.employee_count ?? 450,
            met: (org.employee_count ?? 450) >= 20,
            logic_group: 'OR',
            description: 'Mandatory DPO designation under § 38(1) BDSG where >= 20 persons are constantly employed in automated processing',
          },
        ],
        exemptions_evaluated: [],
        preemption_notes: [
          'Operates under GDPR Art. 37(4) and Art. 88 opening clauses; CJEU C-34/21 case law restricts broad reliance on national employment provisions lacking specific collective safeguards.',
        ],
        mandatory_controls: [
          'Formal DPO Designation filed with competent German Land Authority (§ 38 BDSG)',
          'Strict TDDDG § 25 Terminal Equipment Consent before non-essential storage/access',
        ],
        required_assessments: ['German Works Council (Betriebsrat) Co-Determination & DPIA Review'],
        response_deadlines: {
          rights_request_initial_days: 30,
          rights_request_day_type: '1 calendar month (GDPR Art. 12(3))',
          rights_request_extension_days: 60,
          rights_request_appeal_days: null,
          identity_verification_required: true,
          breach_regulator_hours: 72,
          breach_regulator_days: 3,
          breach_regulator_text: 'Within 72 hours to competent Land DPA (e.g. BayLDA) — Note § 42(4) BDSG evidentiary privilege on self-incrimination',
          breach_attorney_general_threshold_individuals: null,
          breach_individual_notification_days: null,
          breach_individual_text: 'Without undue delay (GDPR Art. 34)',
          cure_period_days: null,
          record_retention_years: 3,
        },
        competent_authority: 'BfDI & Competent State Authority (BayLDA Bavaria / LDI NRW / BlnBDI Berlin)',
        required_approval_gates: ['German DPO (Datenschutzbeauftragter) Review'],
        required_evidence: ['§ 38 BDSG DPO Appointment Letter', 'TDDDG § 25 Consent Telemetry'],
        official_source_url: 'https://www.gesetze-im-internet.de/bdsg_2018/',
        rule_version: '2026.10.1',
        regulatory_status: 'effective',
        deployment_status: 'production_enabled',
        legal_review_status: 'verified',
        confidence: 0.98,
        requires_legal_review: false,
      });
    }

    if (act.involves_ai_or_admt) {
      instruments.push({
        regulation_id: 'EU-AI-ACT-2024-1689',
        jurisdiction_id: 'EU',
        legal_instrument: 'EU Artificial Intelligence Act (Regulation (EU) 2024/1689)',
        article_or_section: 'Arts. 5, 6, 9–15, 26, 27 (Fundamental Rights Impact Assessment), 50',
        domain_category: 'ai_governance',
        applicability_status: 'applicable',
        applicability_reasoning:
          'Activity involves AI or Automated Decision-Making Technology (ADMT) with output used in the European Union.',
        triggered_by_facts: ['involves_ai_or_admt = true', 'EU subject or establishment nexus'],
        thresholds_evaluated: [],
        exemptions_evaluated: [],
        preemption_notes: [
          'Applies concurrently with GDPR Art. 22 automated decision-making safeguards.',
        ],
        mandatory_controls: [
          'Human-in-the-Loop Oversight & Transparency Disclosures (Art. 14 & Art. 50)',
          'AI Literacy & Technical Risk Management System (Art. 4 & Art. 9)',
        ],
        required_assessments: [
          'EU AI Act Article 27 Fundamental Rights Impact Assessment (FRIA)',
          'GDPR Article 35 DPIA (Combined AI/Data Protection Assessment)',
        ],
        response_deadlines: {
          rights_request_initial_days: 30,
          rights_request_day_type: 'calendar_days',
          rights_request_extension_days: null,
          rights_request_appeal_days: null,
          identity_verification_required: true,
          breach_regulator_hours: 48,
          breach_regulator_days: 2,
          breach_regulator_text: 'Serious AI incident reporting under Art. 73 (2 to 15 days depending on severity/widespread infringement)',
          breach_attorney_general_threshold_individuals: null,
          breach_individual_notification_days: null,
          breach_individual_text: 'Right to explanation of individual decision-making (Art. 86)',
          cure_period_days: null,
          record_retention_years: 10,
        },
        competent_authority: 'European AI Office & National Market Surveillance Authorities',
        required_approval_gates: ['AI Governance Committee & Legal Counsel Sign-off on Art. 27 FRIA'],
        required_evidence: ['Article 27 FRIA Dossier', 'Model Logging & Human Oversight Audit Trail'],
        official_source_url: 'https://eur-lex.europa.eu/eli/reg/2024/1689/oj',
        rule_version: '2026.10.1',
        regulatory_status: 'effective',
        deployment_status: 'production_enabled',
        legal_review_status: 'verified',
        confidence: 0.98,
        requires_legal_review: true,
      });
    }
  }

  // Example Exempt / Preempted Instrument for Transparency
  exemptOrPreempted.push({
    regulation_id: 'US-UT-UCPA-EXEMPT-CHECK',
    jurisdiction_id: 'US-UT',
    legal_instrument: 'Utah Consumer Privacy Act (UCPA)',
    article_or_section: 'Utah Code § 13-61-102(2)(g)',
    domain_category: 'privacy',
    applicability_status: 'exempt',
    applicability_reasoning:
      'UCPA provides a broad entity-level and data-level exemption for HIPAA covered entities, business associates, and GLBA financial institutions, plus requires both $25M revenue AND consumer volume thresholds.',
    triggered_by_facts: ['Entity/Data Exemption Evaluated'],
    thresholds_evaluated: [],
    exemptions_evaluated: [
      {
        exemption_id: 'UCPA-HIPAA-ENTITY-CARVEOUT',
        exemption_type: 'entity_level',
        carve_out_statute: 'Utah Code § 13-61-102(2)(g)-(h)',
        applies: true,
        scope: 'Entity-level & PHI exemption under Utah Code § 13-61-102(2)',
        description: 'Contrast with California CCPA which only grants a data-level PHI carve-out.',
      },
    ],
    preemption_notes: [],
    mandatory_controls: [],
    required_assessments: [],
    response_deadlines: {
      rights_request_initial_days: 45,
      rights_request_day_type: 'calendar_days',
      rights_request_extension_days: 45,
      rights_request_appeal_days: null,
      identity_verification_required: true,
      breach_regulator_hours: null,
      breach_regulator_days: null,
      breach_regulator_text: 'Without unreasonable delay',
      breach_attorney_general_threshold_individuals: 500,
      breach_individual_notification_days: null,
      breach_individual_text: 'Without unreasonable delay',
      cure_period_days: 30,
      record_retention_years: 2,
    },
    competent_authority: 'Utah Office of the Attorney General',
    required_approval_gates: [],
    required_evidence: [],
    official_source_url: 'https://le.utah.gov/xcode/Title13/Chapter61/13-61.html',
    rule_version: '2026.10.1',
    regulatory_status: 'effective',
    deployment_status: 'production_enabled',
    legal_review_status: 'verified',
    confidence: 0.99,
    requires_legal_review: false,
  });

  const mandatoryControls = Array.from(new Set(instruments.flatMap((i) => i.mandatory_controls)));
  const requiredAssessments = Array.from(new Set(instruments.flatMap((i) => i.required_assessments)));
  const approvalGates = Array.from(new Set(instruments.flatMap((i) => i.required_approval_gates)));

  return {
    evaluation_id: `JRAE-EVAL-${Date.now().toString().slice(-6)}`,
    evaluated_at: new Date().toISOString(),
    evaluation_date: req.evaluation_date || new Date().toISOString().slice(0, 10),
    organization_summary: {
      industry: org.industry,
      organization_type: org.organization_type,
      employee_count: org.employee_count,
      annual_revenue_usd: revUsd,
      establishments: org.establishments,
    },
    activity_summary: {
      purpose: act.purpose,
      data_categories: act.data_categories,
      subject_locations: act.subject_locations,
      processing_locations: act.processing_locations,
      involves_ai_or_admt: act.involves_ai_or_admt,
    },
    applicable_instruments: instruments,
    future_preparation_obligations: [],
    exempt_or_preempted_instruments: exemptOrPreempted,
    mandatory_controls: mandatoryControls,
    required_assessments: requiredAssessments,
    applicable_deadlines: {
      strictest_dsar_days: 30,
      strictest_dsar_regime: 'GDPR Art. 12(3) (1 calendar month) / Quebec Law 25 (30 calendar days, no unilateral extension) / Ontario PHIPA (30 days)',
      strictest_breach_regulator_hours: 72,
      strictest_breach_regime: 'GDPR Art. 33 (72 hours) + Quebec Law 25 (Promptly) + PIPEDA (As soon as feasible)',
    },
    responsible_authorities: authorities,
    lead_supervisory_authority: hasEuNexus
      ? {
          jurisdiction_id: org.main_eu_establishment || 'EU-IE',
          authority:
            org.main_eu_establishment === 'EU-DE'
              ? 'BfDI / BayLDA (Germany)'
              : 'Data Protection Commission (DPC Ireland)',
          basis: 'GDPR Article 56 One-Stop-Shop Central Administration / Main Establishment',
        }
      : null,
    cross_border_transfer_analysis: {
      cross_border_transfer_detected: true,
      required_mechanisms: [
        'EU GDPR Chapter V: 2021 Standard Contractual Clauses (SCCs) + Transfer Impact Assessment (TIA) or EU-US DPF verification',
        'Quebec Law 25 s. 17: Mandatory Cross-Border Transfer Impact Assessment (EFVP) + Written Agreement before communicating PI outside Quebec',
        'Canada PIPEDA Principle 4.1.3: Contractual comparable level of protection + transparency notice of foreign access risks',
      ],
      notes: [
        'Never conflate EU adequacy with Quebec Law 25 s. 17: Quebec requires an assessment of legal principles applicable in the receiving jurisdiction regardless of federal PIPEDA status.',
      ],
    },
    required_approval_gates: approvalGates,
    unresolved_questions: [
      'Confirm whether non-authenticated web telemetry pixels on clinical appointment pages are completely segregated from HIPAA PHI repositories.',
    ],
    conflicts_and_escalations: conflicts,
    authoritative_source_links: instruments.map((i) => ({
      regulation_id: i.regulation_id,
      title: i.legal_instrument,
      url: i.official_source_url,
    })),
    rule_versions: Object.fromEntries(instruments.map((i) => [i.regulation_id, i.rule_version])),
    requires_legal_review: true,
    legal_review_reasons: [
      'Cross-jurisdictional HIPAA vs. CCPA/CPRA data-level carve-out boundary requires Privacy Counsel sign-off.',
      'Quebec Law 25 s. 17 cross-border Transfer Impact Assessment requires formal written agreement and Privacy Officer validation.',
      ...(act.involves_ai_or_admt
        ? ['Automated Decision-Making (ADMT / EU AI Act Art. 27 FRIA) requires mandatory Human-in-the-Loop governance gate.']
        : []),
    ],
  };
}

// ============================================================================
// MULTI-JURISDICTION BREACH WAR ROOM FALLBACK GENERATOR
// ============================================================================

export function buildFallbackBreachWarRoom(input: BreachIncidentInput): BreachWarRoomResponse {
  const regimes: BreachRegimeObligation[] = [];

  if (input.jurisdictions.includes('EU-FR') || input.jurisdictions.includes('EU-DE') || input.jurisdictions.includes('EU')) {
    if (input.jurisdictions.includes('EU-FR')) {
      regimes.push({
        jurisdiction_id: 'EU-FR',
        regulation_id: 'EU-GDPR-FR-CNIL',
        regime_label: 'EU GDPR Art. 33/34 + French Loi Informatique et Libertés',
        threshold_standard: 'Risk to rights and freedoms (Regulator) / High risk (Individuals)',
        threshold_met: !input.encryption_or_safe_harbor_intact,
        regulator_authority: "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        regulator_deadline_text: 'Without undue delay and not later than 72 hours after awareness',
        regulator_deadline_hours: 72,
        individual_notification_text: 'Without undue delay (High risk — Art. 34)',
        individual_deadline_days: null,
        ag_or_media_trigger: 'CNIL Teleservice Notification Portal',
        record_retention_requirement: 'GDPR Art. 33(5) Internal Breach Register (Permanent / 5+ yrs)',
        requires_human_legal_approval: true,
        approval_status: 'pending_counsel_gate',
      });
    }
    if (input.jurisdictions.includes('EU-DE')) {
      regimes.push({
        jurisdiction_id: 'EU-DE',
        regulation_id: 'EU-GDPR-DE-BDSG',
        regime_label: 'EU GDPR Art. 33/34 + Germany BDSG § 42(4)',
        threshold_standard: 'Risk to rights and freedoms (Regulator) / High risk + § 42(4) BDSG evidentiary privilege notice',
        threshold_met: !input.encryption_or_safe_harbor_intact,
        regulator_authority: 'BfDI / BayLDA (Bavaria) & Competent Land Supervisory Authority',
        regulator_deadline_text: 'Without undue delay and not later than 72 hours after awareness',
        regulator_deadline_hours: 72,
        individual_notification_text: 'Without undue delay (High risk — Art. 34)',
        individual_deadline_days: null,
        ag_or_media_trigger: 'Invoke § 42(4) BDSG privilege reservation in German DPA filing',
        record_retention_requirement: 'GDPR Art. 33(5) Internal Breach Register',
        requires_human_legal_approval: true,
        approval_status: 'pending_counsel_gate',
      });
    }
  }

  if (input.jurisdictions.includes('CA-QC')) {
    regimes.push({
      jurisdiction_id: 'CA-QC',
      regulation_id: 'CA-QC-LAW25-S3.5',
      regime_label: 'Quebec Law 25 (Private Sector Act s. 3.5–3.8)',
      threshold_standard: 'Risk of serious injury (Risque qu’un préjudice sérieux soit causé)',
      threshold_met: input.risk_of_harm_level === 'high' || input.risk_of_harm_level === 'rrosh',
      regulator_authority: "Commission d'accès à l'information du Québec (CAI)",
      regulator_deadline_text: 'Promptly (Avec diligence)',
      regulator_deadline_hours: null,
      individual_notification_text: 'Promptly to affected individuals in Quebec',
      individual_deadline_days: null,
      ag_or_media_trigger: 'Mandatory entry in 5-Year Confidentiality Incident Register regardless of reporting threshold',
      record_retention_requirement: '60 months (5 years) minimum statutory incident register (Regulation respecting confidentiality incidents)',
      requires_human_legal_approval: true,
      approval_status: 'pending_counsel_gate',
    });
  }

  if (input.jurisdictions.includes('CA-ON')) {
    regimes.push({
      jurisdiction_id: 'CA-ON',
      regulation_id: 'CA-ON-PHIPA-PIPEDA',
      regime_label: input.involves_phi
        ? 'Ontario PHIPA s. 12(2) + Federal PIPEDA Division 1.1'
        : 'Canada Federal PIPEDA Division 1.1 (Applies in Ontario for commercial non-PHI)',
      threshold_standard: input.involves_phi
        ? 'PHIPA prescribed reporting triggers (O. Reg. 329/04 s. 6.3) + PIPEDA RROSH'
        : 'Real Risk of Significant Harm (RROSH — PIPEDA s. 10.1)',
      threshold_met: true,
      regulator_authority: input.involves_phi
        ? 'Information and Privacy Commissioner of Ontario (IPC) & OPC Canada'
        : 'Office of the Privacy Commissioner of Canada (OPC)',
      regulator_deadline_text: input.involves_phi
        ? 'At the first reasonable opportunity (PHIPA) / As soon as feasible (PIPEDA)'
        : 'As soon as feasible after determining RROSH',
      regulator_deadline_hours: null,
      individual_notification_text: input.involves_phi
        ? 'At the first reasonable opportunity'
        : 'As soon as feasible',
      individual_deadline_days: null,
      ag_or_media_trigger: input.involves_phi ? 'Mandatory Annual PHIPA Breach Statistics Report due March 1' : null,
      record_retention_requirement: '24 months minimum for ALL breaches of security safeguards under PIPEDA s. 10.3(1)',
      requires_human_legal_approval: true,
      approval_status: 'pending_counsel_gate',
    });
  }

  if (input.jurisdictions.includes('US-CA')) {
    const caCount = input.affected_counts_by_jurisdiction['US-CA'] ?? 1250;
    regimes.push({
      jurisdiction_id: 'US-CA',
      regulation_id: 'US-CA-CIV-1798.82-HIPAA',
      regime_label: input.involves_phi
        ? 'California Civil Code § 1798.82 + CMIA + Federal HIPAA Breach Rule (45 CFR § 164.404)'
        : 'California Civil Code § 1798.82 & CCPA § 1798.150',
      threshold_standard: 'Unencrypted personal information acquired by unauthorized person',
      threshold_met: !input.encryption_or_safe_harbor_intact,
      regulator_authority: input.involves_phi
        ? 'California Attorney General + HHS Office for Civil Rights (OCR) + CDPH'
        : 'California Attorney General',
      regulator_deadline_text:
        caCount >= 500
          ? 'Without unreasonable delay (CA AG electronic sample notice required because >= 500 CA residents affected; HIPAA OCR outer limit 60 calendar days)'
          : 'Without unreasonable delay',
      regulator_deadline_hours: input.involves_phi ? 1440 : null,
      individual_notification_text: 'Most expedient time possible and without unreasonable delay (HIPAA outer limit: 60 days)',
      individual_deadline_days: input.involves_phi ? 60 : null,
      ag_or_media_trigger:
        caCount >= 500
          ? `Triggered (${caCount.toLocaleString()} CA residents >= 500 threshold): Submit electronic sample notice to CA AG & prominent media if HIPAA >500`
          : 'Below 500 CA resident AG sample notice threshold',
      record_retention_requirement: 'HIPAA 6 years (45 CFR § 164.530(j)) / CCPA 24 months',
      requires_human_legal_approval: true,
      approval_status: 'pending_counsel_gate',
    });
  }

  return {
    incident_id: `INC-WAR-${Date.now().toString().slice(-5)}`,
    created_at: new Date().toISOString(),
    discovery_timestamp: input.discovery_timestamp,
    strictest_regulator_deadline_hours: 72,
    strictest_individual_deadline_days: input.involves_phi ? 60 : null,
    qualitative_deadlines_require_immediate_review: true,
    unified_timeline: [
      {
        step_order: 1,
        window: 'T + 0h to 4h',
        milestone: 'Privilege Protocol, Forensic Preservation & Encryption Safe-Harbor Verification',
        regimes_covered: ['EU-GDPR', 'CA-QC-LAW25', 'CA-FED-PIPEDA', 'CA-ON-PHIPA', 'US-CA-1798.82'],
        gate_type: 'forensic_privilege',
      },
      {
        step_order: 2,
        window: 'T + 4h to 24h',
        milestone: 'Parallel Harm Threshold Triage (GDPR Risk vs. PIPEDA RROSH vs. Law 25 Serious Injury vs. PHIPA s. 12)',
        regimes_covered: ['EU-FR', 'EU-DE', 'CA-QC', 'CA-ON', 'US-CA'],
        gate_type: 'human_legal_approval',
      },
      {
        step_order: 3,
        window: 'T + 72 Hours (Hard Clock)',
        milestone: 'EU GDPR Art. 33 Supervisory Authority Notification (CNIL France & BfDI/BayLDA Germany with § 42(4) BDSG reservation)',
        regimes_covered: ['EU-FR', 'EU-DE'],
        gate_type: 'human_legal_approval',
      },
      {
        step_order: 4,
        window: 'Promptly / First Reasonable Opportunity',
        milestone: 'Quebec CAI Notification (Law 25 s. 3.5), Ontario IPC Notification (PHIPA s. 12), and OPC RROSH Filing',
        regimes_covered: ['CA-QC', 'CA-ON', 'CA-FED'],
        gate_type: 'human_legal_approval',
      },
      {
        step_order: 5,
        window: 'Without Unreasonable Delay (<= 60 Days Max for HIPAA)',
        milestone: 'California Consumer Notice + CA Attorney General Electronic Sample Filing (>= 500 CA residents) + HHS OCR Filing',
        regimes_covered: ['US-CA', 'US-FED-HIPAA'],
        gate_type: 'human_legal_approval',
      },
    ],
    regime_evaluations: regimes,
    deduplicated_containment_tasks: [
      {
        task_id: 'TASK-01',
        category: 'Containment & Forensics',
        task_title: 'Isolate compromised OAuth/API tokens, snapshot volatile memory, and verify AES-256 key custody to evaluate encryption safe harbor',
        satisfied_regimes: ['EU-GDPR Art. 32/34(3)(a)', 'US-CA Civ. Code § 1798.82', 'HIPAA 45 CFR § 164.402', 'CA-QC Law 25 s. 3.5'],
        owner_role: 'CISO / Incident Commander',
        status: 'completed',
        requires_human_legal_approval: false,
      },
      {
        task_id: 'TASK-02',
        category: 'Statutory Register & Evidence',
        task_title: 'Log immutable entry into unified PIPEDA (24-month), Quebec Law 25 (60-month), and GDPR Art. 33(5) Confidentiality Incident Ledger',
        satisfied_regimes: ['CA-FED-PIPEDA s. 10.3', 'CA-QC-LAW25 s. 3.8', 'EU-GDPR Art. 33(5)', 'CA-ON-PHIPA'],
        owner_role: 'Privacy Operations Lead',
        status: 'in_progress',
        requires_human_legal_approval: false,
      },
      {
        task_id: 'TASK-03',
        category: 'Regulator Dispatch Gate',
        task_title: 'General Counsel & DPO Sign-Off on Regulator Notification Packets (CNIL, BayLDA, CAI Quebec, IPC Ontario, OPC, CA AG)',
        satisfied_regimes: ['EU-FR', 'EU-DE', 'CA-QC', 'CA-ON', 'US-CA'],
        owner_role: 'Chief Privacy Officer & External Legal Counsel',
        status: 'pending',
        requires_human_legal_approval: true,
      },
    ],
    requires_human_legal_approval: true,
  };
}

// ============================================================================
// ASSESSMENTS, DSAR NEXUS, ROPA & GOVERNED ASSISTANT FALLBACKS
// ============================================================================

export function buildFallbackAssessments(req: AssessmentRecommendationRequest): AssessmentRecommendationResponse {
  const templates: RecommendedAssessmentTemplate[] = [
    {
      assessment_code: 'PIA',
      title: 'Enterprise Multi-Jurisdictional Privacy Impact Assessment (PIA)',
      statutory_basis: 'OPC PIPEDA Expectations / Treasury Board Directive / State CPA Risk Assessment Rules (CA, CO, VA, CT, TX)',
      jurisdiction_scope: req.jurisdictions,
      mandatory: true,
      trigger_reason: 'Baseline privacy engineering & proportionality assessment for new or modified personal data processing.',
      required_sections: [
        'Data Flow & System Architecture Topology',
        'Necessity, Proportionality & Data Minimization Analysis',
        'Notice, Consent & Opt-Out Mechanism Verification',
        'Vendor Subprocessor & Retention Controls',
      ],
      required_signoffs: ['Product Owner', 'Privacy Architect'],
    },
  ];

  if (req.involves_high_risk_processing || req.jurisdictions.some((j) => j.startsWith('EU'))) {
    templates.push({
      assessment_code: 'DPIA',
      title: 'GDPR Article 35 Data Protection Impact Assessment (DPIA)',
      statutory_basis: 'GDPR Art. 35 & EDPB WP248 rev.01 High-Risk Criteria',
      jurisdiction_scope: ['EU', 'EU-DE', 'EU-FR', 'EU-IE'],
      mandatory: true,
      trigger_reason: 'Systematic evaluation, sensitive data at scale, or automated decision-making likely to result in high risk.',
      required_sections: [
        'Systematic Description of Processing & Purposes (Art. 35(7)(a))',
        'Necessity and Proportionality Assessment (Art. 35(7)(b))',
        'Assessment of Risks to Rights and Freedoms of Data Subjects (Art. 35(7)(c))',
        'Technical & Organizational Measures + Formal DPO Advice (Art. 35(2) & 35(7)(d))',
      ],
      required_signoffs: ['EU Data Protection Officer (DPO)', 'Information Security Officer'],
    });
  }

  if (req.involves_phi_or_hin || req.jurisdictions.includes('CA-ON')) {
    templates.push({
      assessment_code: 'PHIPA_TRA',
      title: 'Ontario PHIPA Threat & Risk Assessment (TRA) & Health PIA',
      statutory_basis: 'Ontario PHIPA s. 10, s. 12 & O. Reg. 329/04 (Electronic Service Providers / Health Information Network Providers)',
      jurisdiction_scope: ['CA-ON'],
      mandatory: true,
      trigger_reason: 'Processing Personal Health Information (PHI) as a Health Information Custodian (HIC) or Agent in Ontario.',
      required_sections: [
        'HIC / Agent Role & S. 10 Information Practices Verification',
        'Electronic Audit Logging & Lock-Box Consent Architecture',
        'Threat & Vulnerability Matrix (Infoway HTRA Alignment)',
        'Breach Notification Readiness (IPC First Reasonable Opportunity)',
      ],
      required_signoffs: ['HIC Privacy Contact', 'Chief Information Security Officer'],
    });
  }

  if (req.involves_cross_border_transfer || req.jurisdictions.includes('CA-QC')) {
    templates.push({
      assessment_code: 'LAW25_TIA',
      title: 'Quebec Law 25 Section 17 Cross-Border Transfer Impact Assessment (EFVP) & EU Clause V TIA',
      statutory_basis: 'Quebec Private Sector Act s. 17 (Law 25) & GDPR Chapter V (Schrems II / EDPB Recommendations 01/2020)',
      jurisdiction_scope: ['CA-QC', 'EU', 'CA-FED'],
      mandatory: true,
      trigger_reason: 'Personal information is communicated outside Quebec or transferred from the EEA to a third country.',
      required_sections: [
        'Sensitivity of Personal Information & Purpose of Communication (Law 25 s. 17(1)-(2))',
        'Protection Measures (Contractual & Encryption-in-Transit/Rest) (Law 25 s. 17(3))',
        'Legal Principles & Government Surveillance Analysis in Destination Jurisdiction (Law 25 s. 17(4) / Schrems II)',
        'Written Agreement Execution Gate (Mandatory prior to transfer)',
      ],
      required_signoffs: ['Person in Charge of Personal Information (Quebec Law 25 s. 3.1)', 'Legal Counsel'],
    });
  }

  if (req.relies_on_legitimate_interests) {
    templates.push({
      assessment_code: 'GDPR_LIA',
      title: 'GDPR Article 6(1)(f) Three-Part Legitimate Interests Assessment (LIA)',
      statutory_basis: 'GDPR Art. 6(1)(f) & EDPB Guidelines 1/2024 on Legitimate Interest',
      jurisdiction_scope: ['EU'],
      mandatory: true,
      trigger_reason: 'Reliance on controller or third-party legitimate interests as lawful basis under GDPR Art. 6(1)(f).',
      required_sections: [
        'Part 1 — Purpose Test: Identification of Legitimate Interest',
        'Part 2 — Necessity Test: Less Intrusive Alternatives Evaluation',
        'Part 3 — Balancing Test: Reasonable Expectations & Fundamental Rights Override Check',
        'Art. 21 Unconditional Right to Object Implementation',
      ],
      required_signoffs: ['EU Data Protection Officer (DPO)'],
    });
  }

  if (req.involves_ai_or_admt) {
    templates.push({
      assessment_code: 'EU_AI_FRIA_ADMT',
      title: 'EU AI Act Art. 27 Fundamental Rights Impact Assessment (FRIA) & CalPrivacy ADMT Assessment',
      statutory_basis: 'Regulation (EU) 2024/1689 Art. 27, GDPR Art. 22, Quebec Law 25 s. 12.1 & CalPrivacy ADMT Regulations',
      jurisdiction_scope: ['EU', 'US-CA', 'US-CO', 'CA-QC'],
      mandatory: true,
      trigger_reason: 'Deployment of AI or Automated Decision-Making Technology producing legal or similarly significant effects.',
      required_sections: [
        'Algorithmic Logic, Training Data Provenance & Bias Evaluation',
        'Affected Categories of Natural Persons & Fundamental Rights Impact (EU AI Act Art. 27(1))',
        'Pre-Use Notice, Explanation of Principal Parameters (Law 25 s. 12.1) & Opt-Out Pathway (CalPrivacy)',
        'Human-in-the-Loop Intervention & Override Protocol',
      ],
      required_signoffs: ['AI Governance Chair', 'Chief Privacy Officer', 'General Counsel'],
    });
  }

  return {
    recommendation_id: `ASMT-REC-${Date.now().toString().slice(-5)}`,
    assessments: templates,
    requires_legal_review: true,
  };
}

export function buildFallbackDsarEvaluation(req: DsarEvaluateRequest): DsarNexusEvaluationResponse {
  const resCode = req.subject_residency.toUpperCase();
  const regimes: string[] = [];
  let initialDays = 45;
  let dayType = 'calendar_days';
  let ackDeadline: string | null = null;
  let extDays = 45;
  let appealDays: number | null = 60;

  if (resCode.startsWith('EU') || req.controller_establishments.some((e) => e.startsWith('EU'))) {
    regimes.push('EU GDPR Arts. 12–22');
    initialDays = 30;
    dayType = '1 calendar month (GDPR Art. 12(3))';
    extDays = 60;
  }
  if (resCode === 'CA-QC') {
    regimes.push('Quebec Law 25 ss. 27–41');
    initialDays = 30;
    dayType = '30 calendar days (Strict — no unilateral extension; written refusal + 30-day CAI review notice)';
    extDays = 0;
    appealDays = 30;
  } else if (resCode.startsWith('CA-')) {
    regimes.push('Canada PIPEDA s. 8 / Ontario PHIPA s. 54');
    initialDays = 30;
    dayType = '30 calendar days';
    extDays = 30;
  }
  if (resCode === 'US-CA' || req.controller_establishments.includes('US-CA')) {
    regimes.push('California CCPA/CPRA Cal. Civ. Code § 1798.130');
    const recDate = new Date(req.received_at || Date.now());
    const ackDate = new Date(recDate.getTime() + 14 * 86400000);
    ackDeadline = ackDate.toISOString().slice(0, 10);
    if (req.request_type === 'opt_out_sale_sharing_targeted_ads' || req.request_type === 'limit_sensitive_pi') {
      initialDays = 15;
      dayType = '15 business days (11 CCR § 7026(f))';
      extDays = 0;
    }
  }

  if (regimes.length === 0) {
    regimes.push('US State Consumer Privacy Baseline (45 Calendar Days)');
  }

  const baseDate = new Date(req.received_at || Date.now());
  const dueDate = new Date(baseDate.getTime() + initialDays * 86400000).toISOString().slice(0, 10);

  return {
    request_id: `DSAR-NEXUS-${Date.now().toString().slice(-5)}`,
    subject_residency: req.subject_residency,
    applicable_regimes: regimes,
    strictest_initial_deadline: dueDate,
    strictest_initial_days: initialDays,
    day_type: dayType,
    acknowledgement_deadline: ackDeadline,
    extension_available_days: extDays,
    appeal_window_days: appealDays,
    verification_standard:
      req.request_type === 'opt_out_sale_sharing_targeted_ads'
        ? 'No identity verification permitted for Opt-Out of Sale/Sharing (11 CCR § 7060(b) — prevent dark patterns)'
        : 'Reasonable multi-factor verification proportionate to data sensitivity (2–3 data points + signed declaration for sensitive/deletion)',
    exemptions_and_retention_conflicts: [
      ...(req.holds_litigation_or_aml_ledger
        ? [
            {
              code: 'EX-RETENTION-CONFLICT-AML-TAX',
              statute: 'GDPR Art. 17(3)(b) / Cal. Civ. Code § 1798.105(d)(8) / Quebec Law 25',
              scope: 'hold_deletion' as const,
              explanation:
                'Deletion/erasure request conflicts with statutory tax, anti-money laundering (FINTRAC/FinCEN), or active litigation hold. Place non-exempt marketing/telemetry records into immediate erasure while isolating statutory ledger records under restricted processing lock.',
            },
          ]
        : []),
      {
        code: 'EX-THIRD-PARTY-RIGHTS-TRADE-SECRET',
        statute: 'GDPR Art. 15(4) / PIPEDA s. 9(1) / CCPA § 1798.145',
        scope: 'partial_redaction' as const,
        explanation:
          'Redact personal data of other identifiable individuals, attorney-client privileged communications, and confidential security credentials before releasing access package.',
      },
    ],
    requires_human_legal_approval: true,
  };
}

export const FALLBACK_ROPA_RECORDS: RopaRecord[] = [
  {
    record_id: 'ROPA-001',
    processing_activity: 'Global Customer Identity, Billing & Telemetry Platform',
    role: 'Controller',
    purposes: ['Contract Performance', 'Security & Fraud Prevention', 'Regulatory Tax Compliance'],
    legal_bases_gdpr: ['Art. 6(1)(b) Contract', 'Art. 6(1)(c) Legal Obligation', 'Art. 6(1)(f) Legitimate Interest'],
    data_subject_categories: ['Enterprise Customers', 'End-User Subscribers'],
    data_categories: ['Identifiers', 'Billing & Payment Metadata', 'Authentication Telemetry'],
    jurisdictions: ['US-CA', 'US-NY', 'CA-ON', 'CA-QC', 'EU-IE', 'EU-DE', 'EU-FR'],
    recipients_and_subprocessors: ['AWS (eu-central-1 / ca-central-1)', 'Stripe Payment Services'],
    cross_border_transfer_mechanism: 'EU 2021 SCCs (Module 2) + EU-US DPF + Quebec Law 25 s. 17 TIA',
    retention_schedule: 'Active subscription + 7 years statutory tax/audit ledger; telemetry purged after 90 days',
    tom_security_controls: ['AES-256-GCM Customer-Managed Keys', 'Zero-Trust mTLS', 'Immutable Audit Log'],
    linked_assessments: ['DPIA-2026-04', 'LAW25-TIA-2026-02', 'GDPR-LIA-2026-01'],
    last_verified: '2026-10-20',
  },
  {
    record_id: 'ROPA-002',
    processing_activity: 'Clinical Telehealth & Diagnostic AI Triage Assistant',
    role: 'Processor',
    purposes: ['Healthcare Delivery Support', 'Clinical Documentation Assistance'],
    legal_bases_gdpr: ['Art. 6(1)(b) Contract', 'Art. 9(2)(h) Health or Social Care'],
    data_subject_categories: ['Patients', 'Clinicians'],
    data_categories: ['Protected Health Information (PHI)', 'Clinical Notes', 'AI Triage Scores'],
    jurisdictions: ['US-FED', 'US-CA', 'CA-ON', 'CA-QC', 'EU-DE'],
    recipients_and_subprocessors: ['Sovereign Health Cloud Enclave (Encrypted HSM)'],
    cross_border_transfer_mechanism: 'Regional Data Residency Enforced (In-Province CA-ON / CA-QC & EU-DE Only)',
    retention_schedule: 'Governed by Covered Entity / HIC BAA instructions (Minimum 6–10 years clinical statutory floor)',
    tom_security_controls: ['HIPAA 45 CFR § 164.312 Controls', 'PHIPA s. 10(3) Access Audit Trail', 'Human-in-the-Loop AI Gate'],
    linked_assessments: ['PHIPA-TRA-2026-01', 'EU-AI-FRIA-2026-01', 'HIPAA-SRA-2026'],
    last_verified: '2026-10-24',
  },
];

export function buildFallbackAssistantResponse(req: AssistantQueryRequest): GovernedAssistantResponse {
  return {
    query_id: `GOV-AST-${Date.now().toString().slice(-5)}`,
    channel: req.channel,
    evaluated_at: new Date().toISOString(),
    statutory_requirements: [
      {
        citation: 'Quebec Private Sector Act s. 17 (as amended by Law 25) & s. 3.5',
        jurisdiction: 'CA-QC',
        summary:
          'Before communicating personal information outside Quebec, an enterprise must conduct a Privacy Impact Assessment (EFVP/TIA) evaluating sensitivity, purpose, protection measures, and legal principles applicable in the receiving jurisdiction, and enter into a written agreement.',
        official_url: 'https://www.legisquebec.gouv.qc.ca/en/showdoc/cs/P-39.1',
      },
      {
        citation: 'GDPR Art. 33(1), Art. 35 & Art. 46 (Regulation (EU) 2016/679)',
        jurisdiction: 'EU',
        summary:
          'Requires 72-hour supervisory authority breach notification, prior Data Protection Impact Assessment (DPIA) for high-risk processing, and Chapter V transfer safeguards (SCCs + TIA or adequacy decision).',
        official_url: 'https://eur-lex.europa.eu/eli/reg/2016/679/oj',
      },
      {
        citation: 'Cal. Civ. Code § 1798.100, § 1798.140(d), § 1798.145(c) & 45 CFR § 160.203(b)',
        jurisdiction: 'US-CA / US-FED',
        summary:
          'CCPA/CPRA applies to for-profit businesses meeting revenue ($26.625M), 100k consumer records, or 50% data broker thresholds. HIPAA PHI enjoys a data-level carve-out under § 1798.145(c), leaving non-PHI consumer/web data fully governed by CCPA.',
        official_url: 'https://cppa.ca.gov',
      },
    ],
    regulator_guidance: [
      {
        authority: "Commission d'accès à l'information du Québec (CAI)",
        document: 'Guide relative to Privacy Impact Assessments (EFVP) & Cross-Border Transfers',
        summary:
          'Emphasizes documented equivalence analysis of foreign government access laws and technical encryption controls where keys remain under controller custody.',
      },
      {
        authority: 'European Data Protection Board (EDPB) & OPC Canada',
        document: 'EDPB Recommendations 01/2020 on Supplementary Measures & OPC Cross-Border Guidelines',
        summary:
          'Mandates contractual, technical, and organizational supplementary safeguards and transparent notice to data subjects when data may be accessed by foreign authorities.',
      },
    ],
    company_policies: [
      {
        policy_id: 'POL-PRIV-004',
        title: 'Enterprise Cross-Border Data Residency & Sovereign Encryption Standard',
        requirement:
          'All production databases containing EU, Quebec, or Ontario PHI must use regional KMS keys with zero unapproved third-country egress.',
      },
      {
        policy_id: 'POL-AI-009',
        title: 'Human-in-the-Loop Governance Gate for Legal & Regulatory Decisions',
        requirement:
          'AI assistants and automated agents may draft assessments and triage obligations, but final regulatory filings, DSAR denials, and breach notices require explicit Privacy Counsel sign-off.',
      },
    ],
    contractual_commitments: [
      {
        instrument: 'Enterprise Customer Master Data Processing Addendum (DPA v2026.2)',
        clause: 'Section 6.2 (Subprocessor & Incident SLA) & Annex III (SCCs)',
        obligation:
          'Contractual commitment to notify Enterprise Controllers within 24–36 hours of confirmed security incident (stricter than statutory 72-hour GDPR ceiling).',
      },
    ],
    ai_recommendation: {
      synthesized_guidance: `For query "${req.query}", apply the strictest overlapping control baseline across ${req.jurisdiction_context.join(', ') || 'US, Canada, and EU'}: (1) Separate binding statutory requirements from contractual SLAs (your customer DPA 24-hour notice clock runs ahead of the 72-hour GDPR statutory clock); (2) Execute both the EU Chapter V TIA and Quebec Law 25 s. 17 assessment prior to any cross-border transfer; and (3) Route the generated artifact to Privacy Counsel for mandatory human sign-off.`,
      recommended_next_steps: [
        'Run JRAE Applicability Evaluation to lock rule version hashes into the immutable audit trail.',
        'Generate combined GDPR Art. 35 DPIA + Quebec Law 25 s. 17 TIA dossier.',
        'Route package to General Counsel / DPO Approval Queue before production cutover.',
      ],
      confidence: 0.98,
      requires_legal_counsel_signoff: true,
      guardrail_disclaimer:
        'GOVERNED AI BOUNDARY: Statutory citations, regulator guidance, internal policies, contractual SLAs, and AI synthesis are strictly segregated. This output does not constitute autonomous legal sign-off.',
    },
  };
}

export const FALLBACK_INTEGRATION_STATUS: CorporateAiHubIntegrationStatus[] = [
  {
    hub_id: 'm365_copilot',
    name: 'Microsoft 365 Copilot — Declarative Agent & Graph Connector',
    protocol: 'M365 Declarative Agent Schema v1.2 + OpenAPI Action Plugin',
    manifest_path: 'kibo-is/integrations/m365_copilot/declarativeAgent.json',
    status: 'connected',
    auth_mode: 'Entra ID OAuth 2.0 OBO + X-Tenant-ID Enforcement',
    exposed_tools: [
      'evaluateJurisdictionalApplicability',
      'calculateBreachAndDsarDeadlines',
      'recommendPrivacyAssessments',
      'queryGovernedPrivacyAssistant',
    ],
    zero_egress_enforced: true,
    audit_trail_active: true,
    last_heartbeat: new Date().toISOString(),
  },
  {
    hub_id: 'claude_mcp',
    name: 'Anthropic Claude Enterprise — Model Context Protocol (MCP) Server',
    protocol: 'JSON-RPC 2.0 MCP Server (Tools, Resources & Governed Prompts)',
    manifest_path: 'kibo-is/integrations/claude_mcp/server.py',
    status: 'connected',
    auth_mode: 'Mutual TLS + Scoped Enterprise Service Token',
    exposed_tools: [
      'kibo_evaluate_applicability',
      'kibo_breach_war_room_triage',
      'kibo_dsar_nexus_calculator',
      'kibo_ropa_registry_lookup',
    ],
    zero_egress_enforced: true,
    audit_trail_active: true,
    last_heartbeat: new Date().toISOString(),
  },
  {
    hub_id: 'gemini_enterprise',
    name: 'Google Gemini Enterprise / Vertex AI Agent Builder Extension',
    protocol: 'Vertex AI OpenAPI 3.0 Extension + Grounded Regulatory Corpus',
    manifest_path: 'kibo-is/integrations/gemini_enterprise/vertex_extension_openapi.yaml',
    status: 'connected',
    auth_mode: 'Google Cloud Workforce Identity Federation + VPC-SC',
    exposed_tools: [
      'evaluateMultiJurisdictionalCompliance',
      'assessCrossBorderTransferLaw25AndGdpr',
      'triageMultiRegimeIncident',
      'verifyCitationProvenance',
    ],
    zero_egress_enforced: true,
    audit_trail_active: true,
    last_heartbeat: new Date().toISOString(),
  },
];

const ASSESSMENT_DRAFT_STORAGE_KEY = 'kibo_privacy_os_assessment_drafts_v2';

export function loadAssessmentDrafts(tenantId?: string): AssessmentDraftRecord[] {
  const targetTenant = tenantId || currentTenantContext.tenantId;
  if (typeof window === 'undefined' || !window.localStorage) {
    return [];
  }
  try {
    const raw = window.localStorage.getItem(ASSESSMENT_DRAFT_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as AssessmentDraftRecord[];
    return Array.isArray(parsed) ? parsed.filter((d) => d.tenant_id === targetTenant) : [];
  } catch {
    return [];
  }
}

export function saveAssessmentDraft(
  draft: Omit<AssessmentDraftRecord, 'updated_at' | 'tenant_id'> & { tenant_id?: string }
): AssessmentDraftRecord {
  const targetTenant = draft.tenant_id || currentTenantContext.tenantId;
  const record: AssessmentDraftRecord = {
    ...draft,
    tenant_id: targetTenant,
    updated_at: new Date().toISOString(),
  };
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      const raw = window.localStorage.getItem(ASSESSMENT_DRAFT_STORAGE_KEY);
      const all: AssessmentDraftRecord[] = raw ? JSON.parse(raw) : [];
      const idx = all.findIndex((d) => d.draft_id === record.draft_id && d.tenant_id === targetTenant);
      if (idx >= 0) {
        all[idx] = record;
      } else {
        all.unshift(record);
      }
      window.localStorage.setItem(ASSESSMENT_DRAFT_STORAGE_KEY, JSON.stringify(all));
    } catch {
      // ignore storage quota errors
    }
  }
  return record;
}

// ============================================================================
// EXPORTED PRIVACY OS SERVICE CLIENT
// ============================================================================

export const PrivacyOsService = {
  getVerifiedSession: async (role?: WorkspaceRole): Promise<{ session: VerifiedSessionInfo; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<VerifiedSessionInfo>(
      '/api/v1/auth/session',
      {
        method: 'GET',
        headers: role ? { 'X-User-Role': role } : undefined,
      },
      () => ({
        user_id: currentTenantContext.userId,
        display_name: 'Dr. Elena Vance, CIPP/E, CIPP/US, CIPM',
        email: 'elena.vance@kibo.is',
        role: role || 'CPO',
        active_tenant_id: currentTenantContext.tenantId,
        session_verified: false,
        auth_method: demoModeEnabled ? 'demo_session' : 'offline_cached_session',
        authorized_organizations: DEFAULT_AUTHORIZED_ORGANIZATIONS,
        permissions: ['read:all', 'approve:assessments', 'manage:incidents'],
      })
    );
    return { session: result.data, live: result.live, status: result.status };
  },

  getJurisdictions: async (
    country?: string
  ): Promise<{ jurisdictions: JurisdictionEntry[]; live: boolean; status: OperationalDataStatus; cachedAt?: string }> => {
    const query = country ? `?country=${encodeURIComponent(country)}` : '';
    const result = await apiRequestWithFallback<{ total: number; jurisdictions: JurisdictionEntry[] }>(
      `/api/v1/compliance/jurisdictions${query}`,
      { method: 'GET' },
      () => {
        const all = buildFallbackJurisdictions();
        const filtered = country ? all.filter((j) => j.country === country || j.jurisdiction_id.startsWith(country)) : all;
        return { total: filtered.length, jurisdictions: filtered };
      }
    );
    return {
      jurisdictions: result.data.jurisdictions,
      live: result.live,
      status: result.status,
      cachedAt: result.cachedAt,
    };
  },

  evaluateApplicability: async (
    payload: ApplicabilityEvaluationRequest
  ): Promise<{ evaluation: ApplicabilityEvaluationResponse; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<ApplicabilityEvaluationResponse>(
      '/api/v1/compliance/applicability/evaluate',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => buildFallbackEvaluation(payload)
    );
    return { evaluation: result.data, live: result.live, status: result.status };
  },

  evaluateIncidentWarRoom: async (
    payload: BreachIncidentInput
  ): Promise<{ warRoom: BreachWarRoomResponse; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<BreachWarRoomResponse>(
      '/api/v1/office/incidents',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => buildFallbackBreachWarRoom(payload)
    );
    return { warRoom: result.data, live: result.live, status: result.status };
  },

  recommendAssessments: async (
    payload: AssessmentRecommendationRequest
  ): Promise<{ recommendation: AssessmentRecommendationResponse; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<AssessmentRecommendationResponse>(
      '/api/v1/office/assessments/recommend',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => buildFallbackAssessments(payload)
    );
    return { recommendation: result.data, live: result.live, status: result.status };
  },

  evaluateDsarRequest: async (
    payload: DsarEvaluateRequest
  ): Promise<{ dsar: DsarNexusEvaluationResponse; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<DsarNexusEvaluationResponse>(
      '/api/v1/office/rights/evaluate-request',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => buildFallbackDsarEvaluation(payload)
    );
    return { dsar: result.data, live: result.live, status: result.status };
  },

  getRopaRecords: async (): Promise<{ records: RopaRecord[]; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<{ records: RopaRecord[] }>(
      '/api/v1/office/ropa/records',
      { method: 'GET' },
      () => ({ records: FALLBACK_ROPA_RECORDS })
    );
    return { records: result.data.records || FALLBACK_ROPA_RECORDS, live: result.live, status: result.status };
  },

  queryGovernedAssistant: async (
    payload: AssistantQueryRequest
  ): Promise<{ response: GovernedAssistantResponse; live: boolean; status: OperationalDataStatus }> => {
    const result = await apiRequestWithFallback<GovernedAssistantResponse>(
      '/api/v1/office/assistant/query',
      {
        method: 'POST',
        body: JSON.stringify(payload),
      },
      () => buildFallbackAssistantResponse(payload)
    );
    return { response: result.data, live: result.live, status: result.status };
  },

  getIntegrationsStatus: async (): Promise<{
    integrations: CorporateAiHubIntegrationStatus[];
    live: boolean;
    status: OperationalDataStatus;
  }> => {
    const result = await apiRequestWithFallback<{ integrations: CorporateAiHubIntegrationStatus[] }>(
      '/api/v1/integrations/status',
      { method: 'GET' },
      () => ({
        // UX-07: Never claim integrations are 'connected' when backend is unreachable
        integrations: FALLBACK_INTEGRATION_STATUS.map((item) => ({
          ...item,
          status: demoModeEnabled ? 'offline_demo' : 'offline',
          operational_state: demoModeEnabled ? 'demo' : 'offline',
        })),
      })
    );
    const list = (result.data.integrations || FALLBACK_INTEGRATION_STATUS).map((item) => ({
      ...item,
      status: result.live ? item.status : demoModeEnabled ? 'offline_demo' : 'offline',
      operational_state: result.status,
    }));
    return { integrations: list, live: result.live, status: result.status };
  },
};
