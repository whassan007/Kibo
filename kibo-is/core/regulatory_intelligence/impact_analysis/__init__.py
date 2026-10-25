"""
KIBO Privacy OS — Multi-Jurisdictional Regulatory Impact Analyzer (Worker G21)
Implements RD-09 & Section 9:
- Given an `OrganizationProfile` (or multi-jurisdiction enterprise tenant operating in
  California (`US-CA`), Ontario (`CA-ON`), Quebec (`CA-QC`), France (`EU-FR`), and
  Germany (`EU-DE`)) and a newly discovered/amended regulation or decision, computes an
  `ImpactAssessmentReport` (from `core.regulatory_intelligence`) plus detailed
  per-jurisdiction blast radius:
  * Affected organizations / establishments
  * Affected processing activities (RoPA records)
  * Affected data categories & data subjects
  * Triggered assessments:
    - CPPA ADMT/Risk Assessment in `US-CA`
    - Quebec Law 25 EFVP/PIA in `CA-QC`
    - Ontario PHIPA s. 12 lockbox/breach review in `CA-ON`
    - CNIL Art. 82 cookie/tracker consent audit in `EU-FR`
    - German BDSG § 26 / § 38 DPO & employee monitoring DPIA in `EU-DE`
  * Affected contracts / DPAs / SCCs
  * Affected retention schedules, notices, and DSAR workflows
  * Affected controls and evidence artifacts
  * Recommended remediation tasks with priority (`P0`, `P1`, `P2`) and statutory deadlines
  * Required human approvals (`CPO`, `DPO`, `LEGAL`)
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code
from core.jrae.schemas import OrganizationProfileInput, ProcessingActivityInput
from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DecisionAnnotation,
    DecisionVerdictAnnotation,
    ImpactAssessmentReport,
    JurisdictionBlastRadius,
    LegalPassageAnnotation,
    ProvisionDiffRecord,
    RemediationTaskSpec,
    StatutoryAnnotation,
    compute_sha256_hex,
)
from core.regulatory_intelligence.applicability import (
    Obligation,
    OrganizationProfile,
    RegulatoryApplicabilityBridge,
)


FIVE_CANONICAL_TENANT_JURISDICTIONS: Tuple[str, ...] = (
    "US-CA",
    "CA-ON",
    "CA-QC",
    "EU-FR",
    "EU-DE",
)


# Canonical multi-jurisdiction blueprint per jurisdiction for RD-09 & Section 9
_JURISDICTION_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "US-CA": {
        "jurisdiction_name": "United States — California (US-CA)",
        "competent_authority": "California Privacy Protection Agency (CPPA / CalPrivacy) & California Attorney General",
        "organization_unit": {
            "organization_id": "ORG-TENANT-US-CA",
            "organization_name": "KIBO Enterprise North America Inc. (California Establishment)",
            "jurisdiction_id": "US-CA",
            "role": "business / controller",
            "sector": "technology, e-commerce & digital health",
        },
        "processing_activities": [
            {
                "activity_id": "ROPA-US-CA-001",
                "name": "AI/ADMT Consumer Personalization, Behavioral Profiling & Model Training",
                "purpose": "Automated decision-making technology (ADMT), consumer scoring, and targeted cross-context advertising",
                "lawful_basis_or_authority": "Cal. Civ. Code §§ 1798.100, 1798.120, 1798.185(a)(15)-(16); 11 CCR §§ 7150-7221",
                "status": "requires_re_evaluation",
            },
            {
                "activity_id": "ROPA-US-CA-002",
                "name": "Third-Party Service Provider & Contractor Data Sharing Pipeline",
                "purpose": "Cloud analytics and service provider / contractor disclosures under Cal. Civ. Code § 1798.100(d)",
                "lawful_basis_or_authority": "Cal. Civ. Code § 1798.100(d)",
                "status": "requires_contract_addendum_check",
            },
        ],
        "data_categories": [
            "personal_information",
            "sensitive_personal_information",
            "ai_training_and_profiling_data",
            "online_identifiers",
            "precise_geolocation",
        ],
        "data_subjects": [
            "california_consumers",
            "website_visitors",
            "job_applicants_and_employees_ca",
        ],
        "triggered_assessments": [
            "CPPA ADMT & Privacy Risk Assessment (11 CCR §§ 7150-7221 / Cal. Civ. Code § 1798.185(a)(15)(B))",
            "CPPA Annual Independent Cybersecurity Audit (Cal. Civ. Code § 1798.185(a)(15)(A))",
        ],
        "contracts_dpas_sccs": [
            {
                "contract_id": "DPA-US-CA-1798-100D",
                "contract_type": "CCPA/CPRA Service Provider & Contractor Addendum",
                "statutory_basis": "Cal. Civ. Code § 1798.100(d) & 11 CCR § 7051",
                "action_required": "Update mandatory purpose limitation, sale/sharing prohibition, and audit clauses",
            },
        ],
        "retention_schedules": [
            {
                "schedule_id": "RET-US-CA-CONSUMER-01",
                "category": "California Consumer Personal & Sensitive Personal Information",
                "statutory_basis": "Cal. Civ. Code § 1798.100(a)(3) & (c)",
                "max_retention": "Disclosed purpose duration only; purge ADMT telemetry after 12 months",
                "action_required": "Enforce automated retention ceiling and Notice at Collection alignment",
            },
        ],
        "notices": [
            {
                "notice_id": "NOT-US-CA-COLLECTION-ADMT",
                "notice_type": "CCPA Notice at Collection & Pre-Use ADMT Notice",
                "statutory_basis": "Cal. Civ. Code § 1798.100(a) & 11 CCR § 7200",
                "action_required": "Publish Pre-Use ADMT Notice with plain-language logic disclosure and opt-out link",
            },
        ],
        "dsar_workflows": [
            {
                "workflow_id": "DSAR-US-CA-OPTOUT-ADMT",
                "workflow_name": "California Right to Opt-Out of Sale/Sharing & ADMT + Right to Delete/Access",
                "statutory_deadline": "15 business days for Opt-Out / ADMT; 45 calendar days for Access/Delete (10 business days acknowledgement)",
                "action_required": "Recalculate SLA timers and enable ADMT human appeal routing",
            },
        ],
        "controls": [
            "CTRL-CPPA-ADMT-PRE-USE-NOTICE-AND-OPTOUT",
            "CTRL-CPPA-ANNUAL-CYBERSECURITY-AUDIT",
            "CTRL-CPRA-1798-100D-SERVICE-PROVIDER-CONTRACTOR-DPA",
            "CTRL-GPC-GLOBAL-PRIVACY-CONTROL-SIGNAL-HONORING",
        ],
        "evidence_artifacts": [
            "EVID-US-CA-CPPA-RISK-ASSESSMENT-ATTESTATION",
            "EVID-US-CA-ADMT-LOGIC-EVALUATION-LOG",
            "EVID-US-CA-1798-100D-EXECUTED-CONTRACTOR-DPAS",
        ],
        "remediation_tasks": [
            {
                "priority": "P0",
                "title": "Execute CPPA ADMT & High-Risk Privacy Risk Assessment",
                "description": "Complete and file abridged CPPA Risk Assessment attestation before running ADMT or AI training on California consumer data.",
                "statutory_deadline": "Prior to initiating ADMT processing / within 30 calendar days of amendment effective date",
                "owner_role": "CPO",
                "citation_reference": "Cal. Civ. Code § 1798.185(a)(15)-(16); 11 CCR §§ 7150-7221",
            },
            {
                "priority": "P1",
                "title": "Remediate Cal. Civ. Code § 1798.100(d) Service Provider & Contractor DPAs",
                "description": "Amend all California vendor, service provider, and contractor agreements to include mandatory CPRA § 1798.100(d) clauses.",
                "statutory_deadline": "Within 45 calendar days",
                "owner_role": "LEGAL",
                "citation_reference": "Cal. Civ. Code § 1798.100(d)",
            },
        ],
    },
    "CA-ON": {
        "jurisdiction_name": "Canada — Ontario (CA-ON)",
        "competent_authority": "Information and Privacy Commissioner of Ontario (IPC Ontario)",
        "organization_unit": {
            "organization_id": "ORG-TENANT-CA-ON",
            "organization_name": "KIBO Ontario Health Information Custodian & Clinical Services Ltd.",
            "jurisdiction_id": "CA-ON",
            "role": "health_information_custodian / electronic_service_provider",
            "sector": "healthcare & hospital clinical systems",
        },
        "processing_activities": [
            {
                "activity_id": "ROPA-CA-ON-001",
                "name": "Electronic Health Record (EHR) Custody, Patient Lockbox & Clinical Access Auditing",
                "purpose": "Custody and clinical use of personal health information (PHI) with patient consent directives (lockbox)",
                "lawful_basis_or_authority": "Ontario PHIPA, S.O. 2004, c. 3, Sched. A, ss. 12, 17, 20(2), 54",
                "status": "requires_re_evaluation",
            },
        ],
        "data_categories": [
            "phi",
            "health_information",
            "medical_records",
            "personal_information",
        ],
        "data_subjects": [
            "ontario_patients",
            "healthcare_recipients",
            "clinical_practitioners",
        ],
        "triggered_assessments": [
            "Ontario PHIPA s. 12 Lockbox & Breach Review (IPC Ontario PHIPA Decisions 175 & 110)",
            "Ontario PHIPA Threat Risk Assessment (TRA) & Privacy Impact Assessment (PIA) (O. Reg. 329/04 s. 6)",
        ],
        "contracts_dpas_sccs": [
            {
                "contract_id": "DPA-CA-ON-PHIPA-ESP",
                "contract_type": "Ontario PHIPA Electronic Service Provider (ESP) & Health Information Network Provider (HINP) Agreement",
                "statutory_basis": "Ontario PHIPA s. 10(4) & O. Reg. 329/04 s. 6",
                "action_required": "Verify agent/ESP restrictions, audit log delivery, and unauthorized access notification clauses",
            },
        ],
        "retention_schedules": [
            {
                "schedule_id": "RET-CA-ON-PHI-01",
                "category": "Ontario Clinical & Electronic Health Records (PHI)",
                "statutory_basis": "Ontario PHIPA s. 13 & Public Hospitals Act Reg. 965",
                "max_retention": "Minimum 10 years from last clinical visit (or 10 years past age 18 for minors); retain access audit logs",
                "action_required": "Verify immutable EHR access audit trail and secure destruction standards",
            },
        ],
        "notices": [
            {
                "notice_id": "NOT-CA-ON-PHIPA-STATEMENT",
                "notice_type": "PHIPA Written Statement of Information Practices & Lockbox Notice",
                "statutory_basis": "Ontario PHIPA s. 16 & s. 12(2)",
                "action_required": "Update public statement on patient lockbox consent directives and IPC breach notification rights",
            },
        ],
        "dsar_workflows": [
            {
                "workflow_id": "DSAR-CA-ON-PHIPA-ACCESS-LOCKBOX",
                "workflow_name": "Ontario PHIPA s. 54 PHI Access / Correction & s. 12(2) Breach Notification Workflow",
                "statutory_deadline": "30 calendar days for PHI Access/Correction (PHIPA s. 54); first reasonable opportunity for s. 12(2) breach notice + March 1 annual IPC report",
                "action_required": "Enforce patient lockbox masking and s. 12(2) unauthorized access notification triggers",
            },
        ],
        "controls": [
            "CTRL-PHIPA-S12-LOCKBOX-CONSENT-DIRECTIVE-ENFORCEMENT",
            "CTRL-PHIPA-EHR-RBAC-AND-SNOOPING-DETECTION-AUDIT",
            "CTRL-PHIPA-S12-FIRST-REASONABLE-OPPORTUNITY-BREACH-NOTICE",
        ],
        "evidence_artifacts": [
            "EVID-CA-ON-PHIPA-TRA-PIA-REPORT",
            "EVID-CA-ON-EHR-ACCESS-AUDIT-LOG",
            "EVID-CA-ON-ESP-HINP-AGREEMENT-REGISTRY",
        ],
        "remediation_tasks": [
            {
                "priority": "P0",
                "title": "Conduct Ontario PHIPA s. 12 Lockbox & Snooping Breach Control Review",
                "description": "Audit EHR role-based access controls, automated snooping alerts, and patient lockbox consent directive workflows per IPC Ontario PHIPA Decisions 175 & 110.",
                "statutory_deadline": "At first reasonable opportunity / within 15 calendar days",
                "owner_role": "DPO",
                "citation_reference": "Ontario PHIPA, S.O. 2004, c. 3, Sched. A, s. 12(1)-(2); IPC PHIPA Decisions 175 & 110",
            },
        ],
    },
    "CA-QC": {
        "jurisdiction_name": "Canada — Québec (CA-QC)",
        "competent_authority": "Commission d'accès à l'information du Québec (CAI)",
        "organization_unit": {
            "organization_id": "ORG-TENANT-CA-QC",
            "organization_name": "KIBO Québec Technologies Inc. (Montréal Establishment)",
            "jurisdiction_id": "CA-QC",
            "role": "enterprise / responsable du traitement (controller)",
            "sector": "technology, cloud services & retail",
        },
        "processing_activities": [
            {
                "activity_id": "ROPA-CA-QC-001",
                "name": "Cross-Border Personal Information Communication Outside Québec & Automated Decision-Making",
                "purpose": "Cloud hosting and analytics processing outside Québec (art. 17) and automated profiling/portability (art. 12.1, art. 27)",
                "lawful_basis_or_authority": "Québec Loi 25 (L.Q. 2021, c. 25) / LPRPSP art. 3.1, 3.5, 12.1, 17, 27",
                "status": "requires_efvp_pia",
            },
        ],
        "data_categories": [
            "renseignement_personnel",
            "personal_information",
            "sensitive_personal_information",
            "biometric_data",
        ],
        "data_subjects": [
            "quebec_residents",
            "consumers_qc",
            "employees_qc",
        ],
        "triggered_assessments": [
            "Quebec Law 25 EFVP/PIA (Évaluation des facteurs relatifs à la vie privée — LPRPSP art. 3.3 & art. 17 Cross-Border TIA)",
        ],
        "contracts_dpas_sccs": [
            {
                "contract_id": "DPA-CA-QC-LAW25-ART17",
                "contract_type": "Québec Law 25 Art. 17 & Art. 18.3 Written Cross-Border & Processor Transfer Agreement",
                "statutory_basis": "LPRPSP (Loi 25) art. 17 & art. 18.3",
                "action_required": "Execute written contract binding out-of-province recipient to ÉFVP mitigation measures and confidentiality incident reporting",
            },
        ],
        "retention_schedules": [
            {
                "schedule_id": "RET-CA-QC-LAW25-01",
                "category": "Québec Renseignements Personnels & 5-Year Confidentiality Incident Register",
                "statutory_basis": "LPRPSP art. 23 (destruction/anonymization) & Règlement sur les incidents de confidentialité (5-year register)",
                "max_retention": "Destroy or anonymize immediately upon fulfillment of purpose; retain incident register for 5 years (60 months)",
                "action_required": "Validate Law 25 art. 23 anonymization procedure and 60-month incident register",
            },
        ],
        "notices": [
            {
                "notice_id": "NOT-CA-QC-LAW25-BILINGUAL",
                "notice_type": "Loi 25 Bilingual Privacy Policy, Privacy Officer Title/Contact & Art. 12.1 Automated Decision Notice",
                "statutory_basis": "LPRPSP art. 3.1, art. 8, art. 8.1, art. 12.1",
                "action_required": "Publish Responsable de la protection des renseignements personnels contact, out-of-Québec transfer notice, and profiling opt-in disclosure",
            },
        ],
        "dsar_workflows": [
            {
                "workflow_id": "DSAR-CA-QC-LAW25-30D",
                "workflow_name": "Québec Law 25 Access, Rectification, De-indexation & Structured Data Portability (art. 27, 32)",
                "statutory_deadline": "30 calendar days from receipt (no unilateral extension; 30-day CAI review window upon refusal); prompt CAI breach notice on risk of serious injury",
                "action_required": "Enable machine-readable data portability export (Loi 25 art. 27) and 30-day strict SLA",
            },
        ],
        "controls": [
            "CTRL-LAW25-CROSS-BORDER-TRANSFER-GATE",
            "CTRL-WRITTEN-DATA-PROTECTION-CONTRACT-ART17",
            "CTRL-LAW25-PRIVACY-BY-DEFAULT-HIGHEST-CONFIDENTIALITY",
            "CTRL-LAW25-FIVE-YEAR-INCIDENT-REGISTER",
        ],
        "evidence_artifacts": [
            "EVID-CA-QC-LAW25-EFVP-PIA-SIGNED-REPORT",
            "EVID-CA-QC-ART17-WRITTEN-TRANSFER-AGREEMENTS",
            "EVID-CA-QC-CONFIDENTIALITY-INCIDENT-REGISTER-60M",
        ],
        "remediation_tasks": [
            {
                "priority": "P0",
                "title": "Complete Mandatory Québec Law 25 ÉFVP / PIA Before Cross-Border Transfer",
                "description": "Execute Évaluation des facteurs relatifs à la vie privée (ÉFVP) under Loi 25 art. 17 for all personal information communicated outside Québec and sign art. 17 written agreements.",
                "statutory_deadline": "Prior to communicating personal information outside Québec / within 15 calendar days",
                "owner_role": "CPO",
                "citation_reference": "Québec Loi 25 (L.Q. 2021, c. 25), LPRPSP art. 3.3, art. 17, art. 18.3",
            },
        ],
    },
    "EU-FR": {
        "jurisdiction_name": "European Union — France (EU-FR)",
        "competent_authority": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
        "organization_unit": {
            "organization_id": "ORG-TENANT-EU-FR",
            "organization_name": "KIBO France SAS (Paris Establishment)",
            "jurisdiction_id": "EU-FR",
            "role": "controller / responsable de traitement",
            "sector": "technology, e-commerce & digital media",
        },
        "processing_activities": [
            {
                "activity_id": "ROPA-EU-FR-001",
                "name": "Web/Mobile Analytics, Advertising Trackers (Cookies) & Cross-Border EU Telemetry",
                "purpose": "Storage and reading of non-essential trackers/cookies on user terminal equipment and GDPR cross-border transfers",
                "lawful_basis_or_authority": "Loi Informatique et Libertés (LIL) Art. 82; Directive 2002/58/EC Art. 5(3); GDPR Art. 6(1)(a), Art. 35, Art. 46",
                "status": "requires_cnil_cookie_audit",
            },
        ],
        "data_categories": [
            "cookies",
            "online_identifiers",
            "personal_data",
            "sensitive_personal_information",
        ],
        "data_subjects": [
            "french_subscribers_and_users",
            "eu_data_subjects_fr",
            "employees_fr",
        ],
        "triggered_assessments": [
            "CNIL Art. 82 Cookie & Tracker Consent Audit (Loi Informatique et Libertés Art. 82 & CNIL Délibération SAN-2021-023 / SAN-2022-023)",
            "GDPR Art. 35 Data Protection Impact Assessment (AIPD / DPIA — CNIL High-Risk List)",
        ],
        "contracts_dpas_sccs": [
            {
                "contract_id": "DPA-EU-FR-GDPR-ART28-SCC",
                "contract_type": "GDPR Art. 28 Data Processing Agreement & EU 2021/914 Standard Contractual Clauses (SCCs)",
                "statutory_basis": "GDPR Art. 28 & Art. 46(2)(c); CJEU Schrems II (C-311/18)",
                "action_required": "Verify joint-controller/processor cookie consent propagation and Chapter V supplementary transfer safeguards",
            },
        ],
        "retention_schedules": [
            {
                "schedule_id": "RET-EU-FR-CNIL-COOKIES",
                "category": "French Terminal Tracker Consent Logs & Exempt Audience Measurement Data",
                "statutory_basis": "Loi Informatique et Libertés Art. 82 & CNIL Guidelines (Délibération 2020-091)",
                "max_retention": "6 months recommended for cookie consent choice storage; 13 months max tracker lifespan; 25 months max analytics retention",
                "action_required": "Align CMP cookie expiration and analytics retention with CNIL Art. 82 thresholds",
            },
        ],
        "notices": [
            {
                "notice_id": "NOT-EU-FR-CNIL-CMP-BANNER",
                "notice_type": "CNIL Art. 82 First-Layer Cookie Banner ('Tout refuser' Symmetry) & GDPR Art. 13/14 Transparency Notice",
                "statutory_basis": "Loi Informatique et Libertés Art. 82 & GDPR Art. 13",
                "action_required": "Enforce 'Tout refuser' (Refuse All) button on the first layer with identical visual prominence and single-click symmetry as 'Tout accepter'",
            },
        ],
        "dsar_workflows": [
            {
                "workflow_id": "DSAR-EU-FR-GDPR-CONSENT-WITHDRAWAL",
                "workflow_name": "French GDPR Art. 12-22 Data Subject Rights & Instant Art. 82 Cookie Consent Withdrawal",
                "statutory_deadline": "1 calendar month under GDPR Art. 12(3) (up to 3 months for complex requests); immediate effect for Art. 82 tracker withdrawal; 72 hours for CNIL Art. 33 breach notification",
                "action_required": "Verify instant consent withdrawal icon and 1-month GDPR DSAR clock",
            },
        ],
        "controls": [
            "CTRL-CNIL-ART82-REFUSE-ALL-FIRST-LAYER-SYMMETRY",
            "CTRL-PRIOR-OPT-IN-COOKIE-CONSENT-BANNER",
            "CTRL-GDPR-ART35-PRE-PROCESSING-DPIA-GATE",
            "CTRL-GDPR-CHAPTER-V-SCC-TIA-ENFORCEMENT",
        ],
        "evidence_artifacts": [
            "EVID-EU-FR-CNIL-ART82-CMP-CONSENT-AUDIT-TRAIL",
            "EVID-EU-FR-CNIL-AIPD-DPIA-REPORT",
            "EVID-EU-FR-ART28-PROCESSOR-AND-SCC-REGISTRY",
        ],
        "remediation_tasks": [
            {
                "priority": "P0",
                "title": "Execute CNIL Art. 82 Cookie/Tracker Consent Symmetry Audit",
                "description": "Verify zero non-essential cookies fire prior to consent and enforce first-layer 'Tout refuser' symmetry per Loi Informatique et Libertés Art. 82 and CNIL enforcement holdings.",
                "statutory_deadline": "Immediate / within 14 calendar days",
                "owner_role": "DPO",
                "citation_reference": "Loi Informatique et Libertés Art. 82; Directive 2002/58/EC Art. 5(3); CNIL SAN-2021-023",
            },
        ],
    },
    "EU-DE": {
        "jurisdiction_name": "European Union — Germany (EU-DE)",
        "competent_authority": "Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI) & Competent Länder Authorities (BayLDA / LfDI)",
        "organization_unit": {
            "organization_id": "ORG-TENANT-EU-DE",
            "organization_name": "KIBO Deutschland GmbH (Munich DE-BY & Berlin DE-BE Establishments)",
            "jurisdiction_id": "EU-DE",
            "role": "verantwortlicher (controller) / auftragsverarbeiter (processor)",
            "sector": "technology, industrial cloud & enterprise workforce",
        },
        "processing_activities": [
            {
                "activity_id": "ROPA-EU-DE-001",
                "name": "Employee HR Processing, Workplace Telemetry & Automated Scoring / Profiling",
                "purpose": "Employment relationship data processing (§ 26 BDSG), automated processing by >=20 persons (§ 38 BDSG), and AI/profiling scoring (GDPR Art. 22 & Art. 35)",
                "lawful_basis_or_authority": "BDSG § 26 & § 38; GDPR (DSGVO) Art. 6(1), Art. 22, Art. 35, Art. 37-39; CJEU C-634/21 (SCHUFA)",
                "status": "requires_bdsg_dpia_and_dpo_review",
            },
        ],
        "data_categories": [
            "personenbezogene_daten",
            "employee_data",
            "personal_data",
            "ai_training_and_profiling_data",
        ],
        "data_subjects": [
            "german_employees_beschaeftigte",
            "german_consumers_and_users",
            "job_applicants_de",
        ],
        "triggered_assessments": [
            "German BDSG § 26 / § 38 DPO & Employee Monitoring DPIA (Datenschutz-Folgenabschätzung nach Art. 35 DSGVO & § 26 / § 38 BDSG)",
            "GDPR Art. 22 Automated Individual Decision-Making & Scoring Legal Basis Assessment (CJEU C-634/21 SCHUFA)",
        ],
        "contracts_dpas_sccs": [
            {
                "contract_id": "DPA-EU-DE-ART28-BV",
                "contract_type": "German Art. 28 DSGVO Auftragsverarbeitungsvertrag (AVV) & Works Council Betriebsvereinbarung (§ 26 Abs. 4 BDSG)",
                "statutory_basis": "GDPR Art. 28 & BDSG § 26 Abs. 4; CJEU C-34/21 (Hauptpersonalrat)",
                "action_required": "Review AVV subprocessor controls and verify that collective agreements (Betriebsvereinbarungen) meet GDPR Art. 88(2) necessity standards",
            },
        ],
        "retention_schedules": [
            {
                "schedule_id": "RET-EU-DE-BDSG-HGB",
                "category": "German Employee Records (§ 26 BDSG) & Commercial Tax Retention (§ 257 HGB / § 147 AO)",
                "statutory_basis": "BDSG § 26, GDPR Art. 17(3)(b), § 257 HGB, § 147 AO",
                "max_retention": "6 months for rejected job applicants; 6–10 years for statutory commercial/tax records with processing restriction under GDPR Art. 18",
                "action_required": "Enforce two-stage blocking (Sperrung) and deletion schedule reconciling GDPR Art. 17 erasure with HGB/AO retention",
            },
        ],
        "notices": [
            {
                "notice_id": "NOT-EU-DE-DATENSCHUTZ-DPO",
                "notice_type": "German Datenschutzerklärung (Art. 13/14 DSGVO), § 38 BDSG DPO Contact & Employee Monitoring Notice",
                "statutory_basis": "GDPR Art. 13/14, Art. 37(7) & BDSG § 26, § 38",
                "action_required": "Publish designated Datenschutzbeauftragter contact details and notify competent Landesdatenschutzbehörde (BayLDA / BlnBDI)",
            },
        ],
        "dsar_workflows": [
            {
                "workflow_id": "DSAR-EU-DE-ART15-22-SCHUFA",
                "workflow_name": "German GDPR Art. 15 Auskunft, Art. 17 Löschung & Art. 22 Automated Scoring Contest Workflow",
                "statutory_deadline": "1 calendar month under GDPR Art. 12(3); 72 hours for Art. 33 breach notification to competent Land DPA",
                "action_required": "Provide meaningful logic explanation for automated probability scores per CJEU C-634/21 (SCHUFA) and enforce Art. 22 human intervention",
            },
        ],
        "controls": [
            "CTRL-BDSG38-DPO-DESIGNATION-AND-REGISTRATION",
            "CTRL-BDSG26-EMPLOYEE-DATA-NECESSITY-AND-WORKS-COUNCIL-GATE",
            "CTRL-GDPR-ART35-PRE-PROCESSING-DPIA-GATE",
            "CTRL-GDPR-ART22-HUMAN-INTERVENTION-SCORING-SAFEGUARD",
        ],
        "evidence_artifacts": [
            "EVID-EU-DE-BDSG38-DPO-APPOINTMENT-AND-BAYLDA-FILING",
            "EVID-EU-DE-ART35-DSFA-EMPLOYEE-AND-AI-DPIA",
            "EVID-EU-DE-ART28-AVV-AND-BETRIEBSVEREINBARUNG-AUDIT",
        ],
        "remediation_tasks": [
            {
                "priority": "P0",
                "title": "Verify § 38 BDSG DPO Designation & Conduct § 26 BDSG / Art. 35 DSGVO Employee & AI DPIA",
                "description": "Confirm Datenschutzbeauftragter registration with competent Land DPA (≥20 automated processing staff or Art. 35 DPIA trigger) and complete DSFA for employee monitoring and automated scoring.",
                "statutory_deadline": "Prior to commencing processing / within 14 calendar days",
                "owner_role": "DPO",
                "citation_reference": "§ 26 BDSG; § 38 Abs. 1 BDSG; Art. 22, 35, 37 DSGVO; CJEU C-634/21 & C-34/21",
            },
        ],
    },
}


class RegulatoryImpactAnalyzer:
    """
    RD-09 & Section 9 — Multi-Jurisdictional Regulatory Impact & Blast Radius Analyzer.

    Computes an `ImpactAssessmentReport` with detailed per-jurisdiction blast radius across
    an enterprise tenant's operating jurisdictions (including the 5 canonical jurisdictions:
    `US-CA`, `CA-ON`, `CA-QC`, `EU-FR`, and `EU-DE`).
    """

    def __init__(
        self,
        applicability_bridge: Optional[RegulatoryApplicabilityBridge] = None,
    ) -> None:
        self.bridge = applicability_bridge or RegulatoryApplicabilityBridge()

    @staticmethod
    def build_default_multi_jurisdiction_organization() -> OrganizationProfileInput:
        """
        Returns the default multi-jurisdiction enterprise tenant profile operating in
        California (`US-CA`), Ontario (`CA-ON`), Quebec (`CA-QC`), France (`EU-FR`),
        and Germany (`EU-DE`).
        """
        return OrganizationProfileInput(
            name="KIBO Global Multi-Jurisdiction Enterprise Tenant",
            industry="technology",
            organization_type="private",
            employee_count=450,
            annual_revenue_usd=185_000_000.0,
            consumer_records_count=650_000,
            data_broker_revenue_pct=0.0,
            is_federally_regulated_canada=False,
            hipaa_status="business_associate",
            role="controller",
            establishments=list(FIVE_CANONICAL_TENANT_JURISDICTIONS),
            main_eu_establishment="EU-FR",
            subnational_regions=["DE-BY", "DE-BE"],
        )

    def analyze_impact(
        self,
        organization_or_item: Union[
            OrganizationProfileInput,
            Dict[str, Any],
            StatutoryAnnotation,
            DecisionAnnotation,
            ProvisionDiffRecord,
            CanonicalLegalDocument,
            Obligation,
            List[Any],
            None,
        ] = None,
        regulatory_change: Union[
            StatutoryAnnotation,
            DecisionAnnotation,
            ProvisionDiffRecord,
            CanonicalLegalDocument,
            Obligation,
            Dict[str, Any],
            List[Any],
            OrganizationProfileInput,
            None,
        ] = None,
        *,
        organization: Optional[Union[OrganizationProfileInput, Dict[str, Any]]] = None,
        tenant_id: str = "enterprise-multi-jurisdiction-tenant",
        include_all_tenant_jurisdictions: bool = True,
    ) -> ImpactAssessmentReport:
        """
        Computes a comprehensive `ImpactAssessmentReport` (RD-09 & Section 9) for a tenant
        operating across multiple jurisdictions (defaulting to or including `US-CA`, `CA-ON`,
        `CA-QC`, `EU-FR`, and `EU-DE`).

        Flexible argument handling:
        - `analyze_impact(organization_profile, regulatory_change)`
        - `analyze_impact(regulatory_change, organization=organization_profile)`
        - `analyze_impact()` (uses default 5-jurisdiction enterprise profile and canonical multi-jurisdiction change set)
        """
        org_profile, change_items = self._resolve_arguments(
            organization_or_item=organization_or_item,
            regulatory_change=regulatory_change,
            organization_kw=organization,
        )

        # Determine tenant jurisdictions to evaluate
        declared_est = [normalize_jurisdiction_code(j) for j in (org_profile.establishments or []) if j]
        if not declared_est:
            declared_est = list(FIVE_CANONICAL_TENANT_JURISDICTIONS)
        elif include_all_tenant_jurisdictions:
            for code in FIVE_CANONICAL_TENANT_JURISDICTIONS:
                if code not in declared_est:
                    declared_est.append(code)

        # Extract trigger metadata from the supplied regulatory change(s)
        trigger_id, trigger_type, trigger_title, trigger_citation, change_jurs = self._summarize_trigger(change_items)

        # Ensure any specific jurisdiction from the trigger is also represented
        evaluated_jurisdictions: List[str] = list(declared_est)
        for cj in change_jurs:
            norm_cj = normalize_jurisdiction_code(cj)
            if norm_cj and norm_cj not in evaluated_jurisdictions and norm_cj in _JURISDICTION_BLUEPRINTS:
                evaluated_jurisdictions.append(norm_cj)

        per_jur_blast: Dict[str, JurisdictionBlastRadius] = {}
        all_orgs: List[Dict[str, Any]] = []
        all_est: List[str] = []
        all_activities: List[Dict[str, Any]] = []
        all_data_cats: List[str] = []
        all_subjects: List[str] = []
        all_assessments: List[str] = []
        all_contracts: List[Dict[str, Any]] = []
        all_retentions: List[Dict[str, Any]] = []
        all_notices: List[Dict[str, Any]] = []
        all_dsars: List[Dict[str, Any]] = []
        all_controls: List[str] = []
        all_evidence: List[str] = []
        all_tasks: List[RemediationTaskSpec] = []

        for jur_code in evaluated_jurisdictions:
            blast = self._compute_jurisdiction_blast_radius(
                jur_code=jur_code,
                org_profile=org_profile,
                change_items=change_items,
                trigger_citation=trigger_citation,
            )
            per_jur_blast[jur_code] = blast

            all_orgs.extend(blast.affected_organizations)
            for e in blast.affected_establishments:
                if e not in all_est:
                    all_est.append(e)
            all_activities.extend(blast.affected_processing_activities)
            for dc in blast.affected_data_categories:
                if dc not in all_data_cats:
                    all_data_cats.append(dc)
            for ds in blast.affected_data_subjects:
                if ds not in all_subjects:
                    all_subjects.append(ds)
            for asm in blast.triggered_assessments:
                if asm not in all_assessments:
                    all_assessments.append(asm)
            all_contracts.extend(blast.affected_contracts_dpas_sccs)
            all_retentions.extend(blast.affected_retention_schedules)
            all_notices.extend(blast.affected_notices)
            all_dsars.extend(blast.affected_dsar_workflows)
            for ctl in blast.affected_controls:
                if ctl not in all_controls:
                    all_controls.append(ctl)
            for ev in blast.affected_evidence_artifacts:
                if ev not in all_evidence:
                    all_evidence.append(ev)
            all_tasks.extend(blast.remediation_tasks)

        # Sort remediation tasks deterministically by priority (P0 -> P1 -> P2)
        priority_rank = {"P0": 0, "P1": 1, "P2": 2}
        all_tasks.sort(key=lambda t: (priority_rank.get(t.priority, 9), t.jurisdiction_id, t.task_id))

        report_seed = f"{tenant_id}:{org_profile.name}:{trigger_id}:{','.join(evaluated_jurisdictions)}"
        report_id = f"IMPACT-{compute_sha256_hex(report_seed)[:14].upper()}"

        summary_text = (
            f"Multi-jurisdictional regulatory impact assessment for '{org_profile.name}' across "
            f"{len(evaluated_jurisdictions)} jurisdictions ({', '.join(evaluated_jurisdictions)}). "
            f"Identified {len(all_orgs)} affected organization units, {len(all_activities)} RoPA processing activities, "
            f"{len(all_assessments)} mandatory assessments, {len(all_contracts)} affected DPAs/SCCs/contracts, "
            f"{len(all_controls)} technical/organizational controls, and {len(all_tasks)} prioritized remediation tasks "
            f"(P0/P1/P2) requiring CPO, DPO, and LEGAL sign-off."
        )

        return ImpactAssessmentReport(
            report_id=report_id,
            tenant_id=tenant_id,
            organization_name=org_profile.name or "Enterprise Organization",
            trigger_record_id=trigger_id,
            trigger_record_type=trigger_type,
            trigger_title=trigger_title,
            trigger_citation=trigger_citation,
            generated_at=datetime.now(timezone.utc),
            evaluated_jurisdictions=evaluated_jurisdictions,
            affected_jurisdictions=list(per_jur_blast.keys()),
            per_jurisdiction_blast_radius=per_jur_blast,
            affected_organizations=all_orgs,
            affected_establishments=all_est,
            affected_processing_activities=all_activities,
            affected_data_categories=all_data_cats,
            affected_data_subjects=all_subjects,
            triggered_assessments=all_assessments,
            affected_contracts=all_contracts,
            affected_retention_schedules=all_retentions,
            affected_notices=all_notices,
            affected_dsar_workflows=all_dsars,
            affected_controls=all_controls,
            affected_evidence_artifacts=all_evidence,
            recommended_remediation_tasks=all_tasks,
            required_human_approvals=["CPO", "DPO", "LEGAL"],
            requires_legal_review=True,
            summary=summary_text,
        )

    # Alias methods for ergonomic invocation across tests and routers
    compute_impact = analyze_impact
    compute_blast_radius = analyze_impact
    evaluate_blast_radius = analyze_impact

    def _resolve_arguments(
        self,
        organization_or_item: Any,
        regulatory_change: Any,
        organization_kw: Any,
    ) -> Tuple[OrganizationProfileInput, List[Any]]:
        org_profile: Optional[OrganizationProfileInput] = None
        changes: List[Any] = []

        def _is_org(val: Any) -> bool:
            if isinstance(val, OrganizationProfileInput):
                return True
            if isinstance(val, dict) and (
                "establishments" in val
                or "annual_revenue_usd" in val
                or "organization_type" in val
                or "employee_count" in val
            ):
                return True
            return False

        if organization_kw is not None:
            org_profile = (
                organization_kw
                if isinstance(organization_kw, OrganizationProfileInput)
                else OrganizationProfileInput(**organization_kw)
            )

        if _is_org(organization_or_item):
            org_profile = (
                organization_or_item
                if isinstance(organization_or_item, OrganizationProfileInput)
                else OrganizationProfileInput(**organization_or_item)
            )
            if regulatory_change is not None:
                changes = list(regulatory_change) if isinstance(regulatory_change, (list, tuple)) else [regulatory_change]
        else:
            if organization_or_item is not None:
                changes = (
                    list(organization_or_item)
                    if isinstance(organization_or_item, (list, tuple))
                    else [organization_or_item]
                )
            if _is_org(regulatory_change) and org_profile is None:
                org_profile = (
                    regulatory_change
                    if isinstance(regulatory_change, OrganizationProfileInput)
                    else OrganizationProfileInput(**regulatory_change)
                )
            elif regulatory_change is not None and not _is_org(regulatory_change):
                if isinstance(regulatory_change, (list, tuple)):
                    changes.extend(regulatory_change)
                else:
                    changes.append(regulatory_change)

        if org_profile is None:
            org_profile = self.build_default_multi_jurisdiction_organization()

        return org_profile, changes

    def _summarize_trigger(self, change_items: List[Any]) -> Tuple[str, str, str, str, List[str]]:
        if not change_items:
            return (
                "MULTI-JURISDICTION-REGULATORY-UPDATE-2026",
                "multi_jurisdiction_regulatory_bundle",
                "2026 Multi-Jurisdictional Regulatory & Enforcement Update (US-CA, CA-ON, CA-QC, EU-FR, EU-DE)",
                "Cal. Civ. Code § 1798.185(a)(15)-(16); Ontario PHIPA s. 12; Québec Loi 25 art. 17; France LIL Art. 82; German BDSG §§ 26, 38",
                list(FIVE_CANONICAL_TENANT_JURISDICTIONS),
            )

        first = change_items[0]
        jurs: List[str] = []
        for item in change_items:
            j = getattr(item, "jurisdiction_id", None) or (item.get("jurisdiction_id") if isinstance(item, dict) else None)
            if j and j not in jurs:
                jurs.append(str(j))

        if isinstance(first, LegalPassageAnnotation):
            return (
                first.annotation_id,
                "statutory_annotation",
                first.normalized_legal_concept,
                first.source_section,
                jurs,
            )
        if isinstance(first, DecisionVerdictAnnotation):
            return (
                first.decision_id,
                "decision_annotation",
                first.case_name,
                first.neutral_citation_or_id,
                jurs,
            )
        if isinstance(first, ProvisionDiffRecord):
            return (
                first.diff_id,
                "provision_diff",
                f"Amendment to {first.provision_ref} ({first.previous_version} -> {first.current_version})",
                first.provision_ref,
                jurs,
            )
        if isinstance(first, CanonicalLegalDocument):
            return (
                first.document_id,
                "canonical_document",
                first.canonical_title,
                first.official_citation or first.document_id,
                jurs,
            )
        if isinstance(first, Obligation):
            return (
                first.obligation_id,
                first.source_record_type,
                first.title,
                first.official_citation,
                jurs,
            )
        if isinstance(first, dict):
            return (
                str(first.get("id") or first.get("diff_id") or first.get("annotation_id") or first.get("decision_id") or "REG-CHANGE-001"),
                str(first.get("type") or "regulatory_change"),
                str(first.get("title") or first.get("case_name") or first.get("provision_ref") or "Regulatory Update"),
                str(first.get("official_citation") or first.get("provision_ref") or "Statutory Citation"),
                jurs,
            )
        return ("REG-CHANGE-001", "regulatory_change", str(first), "Statutory Citation", jurs)

    def _compute_jurisdiction_blast_radius(
        self,
        jur_code: str,
        org_profile: OrganizationProfileInput,
        change_items: List[Any],
        trigger_citation: str,
    ) -> JurisdictionBlastRadius:
        blueprint = _JURISDICTION_BLUEPRINTS.get(jur_code)
        if blueprint is None:
            entry = GLOBAL_JURISDICTION_REGISTRY.get(jur_code)
            jur_name = entry.name if entry else jur_code
            authority = entry.primary_regulator if entry else "Competent Regulatory Authority"
            blueprint = {
                "jurisdiction_name": jur_name,
                "competent_authority": authority,
                "organization_unit": {
                    "organization_id": f"ORG-TENANT-{jur_code}",
                    "organization_name": f"{org_profile.name} ({jur_code} Establishment)",
                    "jurisdiction_id": jur_code,
                    "role": org_profile.role,
                    "sector": org_profile.industry,
                },
                "processing_activities": [
                    {
                        "activity_id": f"ROPA-{jur_code}-001",
                        "name": f"{jur_code} Regulated Personal Data Processing",
                        "purpose": "Commercial and operational data processing",
                        "lawful_basis_or_authority": trigger_citation,
                        "status": "requires_re_evaluation",
                    }
                ],
                "data_categories": ["personal_data", "sensitive_personal_information"],
                "data_subjects": [f"{jur_code.lower()}_residents"],
                "triggered_assessments": [f"{jur_code} Privacy & Regulatory Impact Assessment"],
                "contracts_dpas_sccs": [
                    {
                        "contract_id": f"DPA-{jur_code}-001",
                        "contract_type": f"{jur_code} Data Processing Agreement",
                        "statutory_basis": trigger_citation,
                        "action_required": "Review processor and cross-border clauses",
                    }
                ],
                "retention_schedules": [
                    {
                        "schedule_id": f"RET-{jur_code}-01",
                        "category": f"{jur_code} Personal Data",
                        "statutory_basis": trigger_citation,
                        "max_retention": "Purpose-limited retention",
                        "action_required": "Review retention schedule",
                    }
                ],
                "notices": [
                    {
                        "notice_id": f"NOT-{jur_code}-01",
                        "notice_type": f"{jur_code} Privacy Notice",
                        "statutory_basis": trigger_citation,
                        "action_required": "Update transparency disclosures",
                    }
                ],
                "dsar_workflows": [
                    {
                        "workflow_id": f"DSAR-{jur_code}-01",
                        "workflow_name": f"{jur_code} Data Subject Rights Workflow",
                        "statutory_deadline": "30 calendar days",
                        "action_required": "Validate DSAR SLA timer",
                    }
                ],
                "controls": [f"CTRL-{jur_code}-COMPLIANCE-VERIFICATION"],
                "evidence_artifacts": [f"EVID-{jur_code}-COMPLIANCE-ATTESTATION"],
                "remediation_tasks": [
                    {
                        "priority": "P1",
                        "title": f"Review {jur_code} Regulatory Compliance Controls",
                        "description": f"Assess impact of {trigger_citation} on {jur_code} operations.",
                        "statutory_deadline": "Within 30 calendar days",
                        "owner_role": "DPO",
                        "citation_reference": trigger_citation,
                    }
                ],
            }

        # Enrich with any specific controls/assessments from matching change_items
        extra_assessments: List[str] = []
        extra_controls: List[str] = []
        extra_tasks: List[RemediationTaskSpec] = []

        for idx, item in enumerate(change_items):
            item_jur = normalize_jurisdiction_code(
                getattr(item, "jurisdiction_id", None)
                or (item.get("jurisdiction_id") if isinstance(item, dict) else "")
                or ""
            )
            if item_jur == jur_code or (item_jur == "EU" and jur_code.startswith("EU-")):
                if isinstance(item, (LegalPassageAnnotation, DecisionVerdictAnnotation, ProvisionDiffRecord, Obligation)):
                    ob = self.bridge.to_obligation(item)
                    for a in ob.required_assessments:
                        if a not in extra_assessments:
                            extra_assessments.append(a)
                    for c in ob.required_controls:
                        if c not in extra_controls:
                            extra_controls.append(c)
                    extra_tasks.append(
                        RemediationTaskSpec(
                            task_id=f"TASK-{jur_code}-CHANGE-{idx + 1:02d}",
                            jurisdiction_id=jur_code,
                            priority="P0" if isinstance(item, DecisionVerdictAnnotation) or getattr(item, "is_substantive", True) else "P2",
                            title=f"Implement {ob.official_citation} Obligation ({ob.title})",
                            description=ob.legal_requirement,
                            statutory_deadline=ob.statutory_deadline_text or "Prior to effective date / within 30 calendar days",
                            owner_role="LEGAL" if "contract" in ob.legal_requirement.lower() else "DPO",
                            affected_artifacts=list(ob.required_controls),
                            citation_reference=ob.official_citation,
                            requires_human_approval=True,
                        )
                    )

        assessments = list(blueprint["triggered_assessments"])
        for a in extra_assessments:
            if a not in assessments:
                assessments.append(a)

        controls = list(blueprint["controls"])
        for c in extra_controls:
            if c not in controls:
                controls.append(c)

        tasks: List[RemediationTaskSpec] = []
        for t_idx, raw_t in enumerate(blueprint["remediation_tasks"]):
            tasks.append(
                RemediationTaskSpec(
                    task_id=f"TASK-{jur_code}-{t_idx + 1:02d}",
                    jurisdiction_id=jur_code,
                    priority=raw_t["priority"],
                    title=raw_t["title"],
                    description=raw_t["description"],
                    statutory_deadline=raw_t["statutory_deadline"],
                    owner_role=raw_t["owner_role"],
                    affected_artifacts=list(controls[:2]),
                    citation_reference=raw_t["citation_reference"],
                    requires_human_approval=True,
                )
            )
        tasks.extend(extra_tasks)

        # Ensure P0, P1, and P2 tasks exist or are well-formed
        if not any(t.priority == "P1" for t in tasks):
            tasks.append(
                RemediationTaskSpec(
                    task_id=f"TASK-{jur_code}-CONTRACT-NOTICE-P1",
                    jurisdiction_id=jur_code,
                    priority="P1",
                    title=f"Update {jur_code} Contracts/DPAs, Privacy Notices & DSAR SLAs",
                    description=f"Synchronize {jur_code} processor agreements, transparency notices, and DSAR timers with current statutory requirements.",
                    statutory_deadline="Within 30 calendar days",
                    owner_role="LEGAL",
                    affected_artifacts=[c["contract_id"] for c in blueprint["contracts_dpas_sccs"]],
                    citation_reference=blueprint["contracts_dpas_sccs"][0]["statutory_basis"],
                    requires_human_approval=True,
                )
            )
        if not any(t.priority == "P2" for t in tasks):
            tasks.append(
                RemediationTaskSpec(
                    task_id=f"TASK-{jur_code}-RETENTION-EVIDENCE-P2",
                    jurisdiction_id=jur_code,
                    priority="P2",
                    title=f"Refresh {jur_code} Retention Schedule & Audit Evidence Artifacts",
                    description=f"Archive updated {jur_code} RoPA records, retention schedules, and compliance evidence artifacts.",
                    statutory_deadline="Within 60 calendar days",
                    owner_role="CPO",
                    affected_artifacts=list(blueprint["evidence_artifacts"]),
                    citation_reference=blueprint["retention_schedules"][0]["statutory_basis"],
                    requires_human_approval=True,
                )
            )

        establishments = [jur_code]
        if jur_code == "EU-DE" and org_profile.subnational_regions:
            for reg in org_profile.subnational_regions:
                if reg.startswith("DE-") and reg not in establishments:
                    establishments.append(reg)

        return JurisdictionBlastRadius(
            jurisdiction_id=jur_code,
            jurisdiction_name=blueprint["jurisdiction_name"],
            applicable=True,
            competent_authority=blueprint["competent_authority"],
            triggered_by_facts=[
                f"establishment={jur_code}",
                f"role={org_profile.role}",
                f"industry={org_profile.industry}",
            ],
            affected_organizations=[dict(blueprint["organization_unit"])],
            affected_establishments=establishments,
            affected_processing_activities=[dict(pa) for pa in blueprint["processing_activities"]],
            affected_data_categories=list(blueprint["data_categories"]),
            affected_data_subjects=list(blueprint["data_subjects"]),
            triggered_assessments=assessments,
            affected_contracts_dpas_sccs=[dict(c) for c in blueprint["contracts_dpas_sccs"]],
            affected_retention_schedules=[dict(r) for r in blueprint["retention_schedules"]],
            affected_notices=[dict(n) for n in blueprint["notices"]],
            affected_dsar_workflows=[dict(w) for w in blueprint["dsar_workflows"]],
            affected_controls=controls,
            affected_evidence_artifacts=list(blueprint["evidence_artifacts"]),
            remediation_tasks=tasks,
            required_human_approvals=["CPO", "DPO", "LEGAL"],
        )


__all__ = [
    "FIVE_CANONICAL_TENANT_JURISDICTIONS",
    "ImpactAssessmentReport",
    "JurisdictionBlastRadius",
    "RemediationTaskSpec",
    "RegulatoryImpactAnalyzer",
]
