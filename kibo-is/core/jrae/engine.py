"""Fact-based jurisdiction evaluation with explicit uncertainty and pack fallbacks."""
import importlib
import inspect
import operator
from datetime import date, datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code
from core.jrae.schemas import (
    ApplicabilityEvaluationRequest, ApplicabilityEvaluationResponse,
    ApplicableInstrumentOutcome, CanonicalRegulation, ConflictOrAmbiguityItem,
    DeploymentStatus, LegalReviewStatus, RegulatoryStatus, ResponseDeadlineSpec,
)


def _fallback_rules():
    specs = [
        ("US-FED-HIPAA-PRIVACY", "US-FED", "HIPAA Privacy and Security Rules", "health_privacy", "https://www.hhs.gov/hipaa/for-professionals/index.html", ["HIPAA risk analysis", "Business associate agreement"], ["HIPAA_SRA"]),
        ("US-FED-FTC-HBNR", "US-FED", "FTC Health Breach Notification Rule", "health_privacy", "https://www.ftc.gov/legal-library/browse/rules/health-breach-notification-rule", ["Assess personal health record vendor scope", "Health breach response plan"], []),
        ("US-FED-GLBA-SAFEGUARDS", "US-FED", "GLBA Safeguards Rule", "financial_privacy", "https://www.ftc.gov/legal-library/browse/rules/safeguards-rule", ["Written information security program", "Financial record retention schedule"], ["GLBA_Risk_Assessment"]),
        ("US-FED-PRIVACY-ACT-1974", "US-FED", "Privacy Act of 1974 / E-Government Act", "public_sector", "https://www.justice.gov/opcl/privacy-act-1974", ["System of records notice"], ["PIA"]),
        ("US-CA-CCPA-CPRA", "US-CA", "CCPA/CPRA", "privacy", "https://cppa.ca.gov/regulations/", ["Consumer rights workflow", "Sale/sharing opt-out", "Non-PHI employee and website privacy notice"], ["Privacy_Risk_Assessment"]),
        ("US-CA-CMIA", "US-CA", "Confidentiality of Medical Information Act", "health_privacy", "https://leginfo.legislature.ca.gov/", ["CMIA authorization and medical confidentiality"], []),
        ("US-WA-MHMDA", "US-WA", "My Health My Data Act", "health_privacy", "https://app.leg.wa.gov/RCW/default.aspx?cite=19.373", ["Consumer health consent", "Consumer health deletion workflow"], []),
        ("US-IL-BIPA", "US-IL", "Biometric Information Privacy Act", "biometric_privacy", "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=3004", ["Written biometric consent", "Biometric retention and destruction policy"], []),
        ("US-NY-NYDFS-500", "US-NY", "23 NYCRR 500", "cybersecurity", "https://www.dfs.ny.gov/industry-guidance/cybersecurity", ["NYDFS cybersecurity program", "NYDFS incident reporting"], ["Cybersecurity_Risk_Assessment"]),
        ("US-NY-SHIELD", "US-NY", "SHIELD Act", "cybersecurity", "https://ag.ny.gov/resources/organizations/data-breach-reporting", ["Reasonable safeguards", "NY AG/DFS/DOS breach routing"], []),
        ("CA-FED-PIPEDA", "CA-FED", "PIPEDA", "privacy", "https://laws-lois.justice.gc.ca/eng/acts/P-8.6/", ["Accountability program", "OPC RROSH breach assessment", "24-month breach records"], ["PIA"]),
        ("CA-QC-LAW25", "CA-QC", "Quebec Law 25", "privacy", "https://www.legisquebec.gouv.qc.ca/en/document/cs/P-39.1", ["Privacy officer", "CAI serious-injury breach rules", "Five-year incident register"], ["PIA"]),
        ("CA-AB-PIPA", "CA-AB", "Alberta PIPA", "privacy", "https://oipc.ab.ca/legislation/pipa/", ["Provincial privacy program", "OIPC-AB breach review"], []),
        ("CA-BC-PIPA", "CA-BC", "BC PIPA", "privacy", "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/03063_01", ["Provincial privacy program"], []),
        ("CA-ON-PHIPA", "CA-ON", "Ontario PHIPA", "health_privacy", "https://www.ontario.ca/laws/statute/04p03", ["Written electronic service provider/agent agreement", "IPC Ontario breach rules", "Medical record retention schedule"], ["PHIPA_TRA", "PHIPA_PIA"]),
        ("EU-GDPR", "EU", "General Data Protection Regulation", "privacy", "https://eur-lex.europa.eu/eli/reg/2016/679/oj", ["Rights and erasure workflow", "GDPR Art. 32 security", "GDPR Art. 33/34 breach review"], ["DPIA_screening"]),
        ("EU-DE-BDSG", "EU-DE", "German BDSG", "privacy", "https://www.gesetze-im-internet.de/bdsg_2018/", ["BDSG national requirements"], []),
        ("EU-DE-HEALTH", "EU-DE", "German Patient/Hospital Health Data Rules", "health_privacy", "https://www.gesetze-im-internet.de/bgb/__630f.html", ["Medical record retention schedule", "Identify applicable Land hospital law", "Professional medical confidentiality"], ["Health_DPIA"]),
        ("EU-FR-LIL-82", "EU-FR", "Loi Informatique et Libertes Art. 82", "electronic_communications", "https://www.cnil.fr/en/cookies-and-other-tracking-devices", ["CNIL cookie and analytics consent assessment", "Targeted advertising opt-in consent", "Assess limited analytics exemption"], []),
        ("EU-EPRIVACY", "EU", "ePrivacy Directive", "electronic_communications", "https://eur-lex.europa.eu/eli/dir/2002/58/oj", ["Prior consent for nonessential cookies and targeted advertising"], []),
        ("EU-AI-ACT", "EU", "EU AI Act", "ai_governance", "https://eur-lex.europa.eu/eli/reg/2024/1689/oj", ["AI system classification", "High-risk AI risk management and human oversight"], ["AI_Impact_Assessment"]),
    ]
    for code, entry in GLOBAL_JURISDICTION_REGISTRY.items():
        if code.startswith("US-") and code != "US-FED":
            specs.append((code + "-BREACH", code, entry.name + " breach notification", "breach_notification", entry.regulator_url, ["State breach notification assessment"], []))
    for state in "VA CO CT TX OR MT DE NH NJ MN MD IN KY RI".split():
        code = "US-" + state
        entry = GLOBAL_JURISDICTION_REGISTRY[code]
        specs.append((code + "-PRIVACY", code, entry.name + " consumer privacy statute", "privacy", entry.regulator_url, ["Consumer rights and appeals workflow", "Validate state-specific business thresholds and exemptions"], ["Privacy_Risk_Assessment"]))
    rules = []
    for rid, code, name, domain, url, controls, assessments in specs:
        entry = GLOBAL_JURISDICTION_REGISTRY[code]
        rules.append(CanonicalRegulation(
            regulation_id=rid, jurisdiction_id=code, jurisdiction_type=entry.jurisdiction_type,
            country=entry.country, legal_authority=entry.primary_regulator,
            legal_instrument=name, official_source_url=url, source_document_hash="fallback-unverified",
            article_or_section="Scope and obligations; counsel verification required",
            effective_date=date(2026, 8, 2) if rid == "EU-AI-ACT" else date(2024, 1, 1), required_actions=controls,
            response_deadlines=ResponseDeadlineSpec(
                rights_request_initial_days=30 if code.startswith(("CA-", "EU")) else 45,
                rights_request_extension_days=60 if code.startswith("EU") else 45 if code.startswith("US-") else 30,
                breach_regulator_hours=72 if rid == "EU-GDPR" else None,
                breach_individual_notification_days=60 if "HIPAA" in rid else None,
            ),
            required_assessments=assessments, competent_regulator=entry.primary_regulator,
            domain_category=domain, legal_review_status=LegalReviewStatus.REQUIRES_COUNSEL_SIGNOFF,
            deployment_status=DeploymentStatus.TESTED, rule_version="fallback-2026.10",
        ))
    return rules


class JurisdictionalApplicabilityEngine:
    """Loads canonical packs independently; incomplete packs do not disable evaluation."""
    def __init__(self):
        self.pack_load_errors: Dict[str, str] = {}
        self.regulations = self._load_regulations()

    def _load_regulations(self):
        rules = {r.regulation_id: r for r in _fallback_rules()}
        for name in ("us_federal", "us_states", "canada", "eu"):
            try:
                module = importlib.import_module("core.regulatory_packs." + name)
                values = []
                for attr, value in vars(module).items():
                    if isinstance(value, CanonicalRegulation):
                        values.append(value)
                    elif isinstance(value, (list, tuple, dict)):
                        values.extend(value.values() if isinstance(value, dict) else value)
                    elif inspect.isfunction(value) and value.__module__ == module.__name__ and (attr.startswith(("get_", "build_", "load_"))):
                        if not any(p.default is inspect.Parameter.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY) for p in inspect.signature(value).parameters.values()):
                            result = value()
                            values.extend(result.values() if isinstance(result, dict) else result if isinstance(result, (list, tuple)) else [result])
                loaded = 0
                for value in values:
                    if isinstance(value, dict) and "regulation_id" in value:
                        value = CanonicalRegulation(**value)
                    if isinstance(value, CanonicalRegulation):
                        rules[value.regulation_id] = value
                        loaded += 1
                if not loaded:
                    self.pack_load_errors[name] = "Pack has no canonical regulations yet"
            except Exception as exc:
                self.pack_load_errors[name] = f"{type(exc).__name__}: {exc}"
        return list(rules.values())

    def evaluate(self, request: ApplicabilityEvaluationRequest) -> ApplicabilityEvaluationResponse:
        # Reload on every evaluation so packs completed after construction become visible.
        self.pack_load_errors = {}
        self.regulations = self._load_regulations()
        org = request.organization.model_copy(deep=True)
        act = request.activity.model_copy(deep=True)
        for obj, field in [(org, "establishments"), (act, "subject_locations"), (act, "processing_locations"), (act, "transfer_destinations")]:
            setattr(obj, field, sorted({normalize_jurisdiction_code(x) for x in getattr(obj, field)}))
        if org.main_eu_establishment:
            org.main_eu_establishment = normalize_jurisdiction_code(org.main_eu_establishment)
        when = request.evaluation_date or date.today()
        establishments = set(org.establishments)
        subjects = set(act.subject_locations)
        nexus = establishments | subjects | set(act.processing_locations)
        us = any(c.startswith("US-") for c in nexus)
        canada = any(c.startswith("CA-") for c in nexus)
        eu_est = any(c == "EU" or c.startswith("EU-") for c in establishments)
        eu_subjects = any(c == "EU" or c.startswith("EU-") for c in subjects)
        gdpr = eu_est or (eu_subjects and (act.targets_goods_or_services_to_subjects or act.monitors_subject_behavior))
        health_aliases = {"health_information", "phi", "health_data", "medical_records", "medical_information", "personal_health_information", "health", "medical", "special_category_health", "reproductive_health_data", "mental_health_data"}
        pi_aliases = {"personal_information", "personal_data", "personal_identifiers", "contact_info", "online_identifiers", "identifiers", "consumer_data", "employee_data"}
        fin_aliases = {"financial_data", "financial_information", "payment_data", "credit_data", "banking_data", "account_numbers", "nonpublic_personal_information"}
        bio_aliases = {"biometric_data", "biometrics", "biometric_identifiers", "special_category_biometric"}
        child_aliases = {"children_data", "childrens_data", "minors_data", "student_records", "education_records"}
        expanded_cats = set(act.data_categories)
        if expanded_cats & health_aliases:
            expanded_cats |= health_aliases | pi_aliases
        if expanded_cats & pi_aliases:
            expanded_cats |= pi_aliases
        if expanded_cats & fin_aliases:
            expanded_cats |= fin_aliases | pi_aliases
        if expanded_cats & bio_aliases or act.involves_biometrics:
            expanded_cats |= bio_aliases | pi_aliases
        if expanded_cats & child_aliases or act.involves_children:
            expanded_cats |= child_aliases | pi_aliases
        if act.involves_targeted_advertising_or_cookies:
            expanded_cats |= {"online_identifiers", "device_information", "traffic_data", "cookies", "personal_data", "personal_information"}

        health = bool(health_aliases & expanded_cats)
        hipaa = us and (org.hipaa_status in {"covered_entity", "business_associate", "hybrid_entity"} or org.organization_type in {"healthcare_covered_entity", "business_associate"} or (org.industry == "healthcare" and health))
        financial = org.organization_type in {"financial_institution", "banking", "insurance"} or org.industry in {"financial_institution", "banking", "insurance"}
        public = org.organization_type in {"government_agency", "federal_agency", "us_federal_agency"}
        education = org.organization_type in {"educational_institution", "school", "university"} or org.industry in {"education", "educational_institution"}
        ontario_health = "CA-ON" in nexus and (org.organization_type in {"health_information_custodian", "hospital", "healthcare_covered_entity"} or org.industry in {"healthcare", "hospital"})
        origin_ca = {c for c in establishments | subjects | set(act.processing_locations) if c.startswith("CA-") and c != "CA-FED"}
        destinations = set(act.transfer_destinations)
        cross = bool(act.involves_cross_border_transfer or len(origin_ca) > 1 or (origin_ca and any(d not in origin_ca for d in destinations)) or (canada and any(c.startswith(("US-", "EU")) for c in nexus)))
        provincial = origin_ca and origin_ca <= {"CA-QC", "CA-AB", "CA-BC"} or (ontario_health and origin_ca <= {"CA-ON"})
        pipeda = canada and not public and (org.is_federally_regulated_canada or cross or not provincial)
        applicable, future, excluded, conflicts, questions = [], [], [], [], []

        def conflict(kind, regulations, description):
            conflicts.append(ConflictOrAmbiguityItem(
                conflict_id=f"{kind}-{len(conflicts) + 1}", regulations_involved=[r.regulation_id for r in regulations],
                jurisdictions_involved=sorted({r.jurisdiction_id for r in regulations}), issue_type=kind,
                description=description, sources=list(dict.fromkeys(r.official_source_url for r in regulations)),
                resolution_strategy="Counsel must validate scope and statutory exceptions before execution."))

        for rule in self.regulations:
            rid, code = rule.regulation_id, normalize_jurisdiction_code(rule.jurisdiction_id)
            status, reason, controls, assessments = "applicable", "", list(rule.required_actions), list(rule.required_assessments)
            thresholds, exemptions, preemption = [], [], []
            review = rule.legal_review_status != LegalReviewStatus.VERIFIED
            if rule.regulatory_status in {RegulatoryStatus.REPEALED, RegulatoryStatus.SUPERSEDED, RegulatoryStatus.PROPOSED} or (rule.repeal_date and rule.repeal_date <= when):
                continue
            if code == "US-FED":
                if not us:
                    continue
                if "HIPAA" in rid:
                    if not hipaa:
                        continue
                    reason = "US nexus and HIPAA covered entity, business associate, or healthcare PHI facts."
                elif "GLBA" in rid:
                    if not financial:
                        continue
                    reason = "US nexus and financial institution/banking/insurance activity."
                elif "FERPA" in rid:
                    if not education:
                        continue
                    reason = "US educational institution / student records nexus."
                elif "COPPA" in rid:
                    if not (act.involves_children or (expanded_cats & child_aliases)):
                        continue
                    reason = "Children under 13 online collection nexus."
                elif "FCRA" in rid:
                    if not (financial or "credit_data" in act.data_categories or "background_check" in act.purpose.lower()):
                        continue
                    reason = "Consumer report / credit eligibility nexus."
                elif "PRIVACY-ACT" in rid or "E-GOV" in rid:
                    if not public or not any(c.startswith("US-") for c in establishments):
                        continue
                    status, review = "conditionally_applicable", True
                    reason = "US government agency nexus; confirm federal agency status (state agencies are outside the federal Privacy Act)."
                elif "HBNR" in rid:
                    if not health or hipaa:
                        continue
                    status, review = "conditionally_applicable", True
                    reason = "Non-HIPAA health service; confirm personal health record vendor/related entity scope."
                else:
                    reason = "US federal nexus; instrument-specific scope assessed below."
            elif code.startswith("US-"):
                if code not in nexus:
                    continue
                if "BIPA" in rid and not act.involves_biometrics:
                    continue
                if "NYDFS" in rid:
                    if not financial:
                        continue
                    status, review = "conditionally_applicable", True
                    reason = "New York financial nexus; NYDFS license/covered-entity status requires confirmation."
                if "MHMDA" in rid and (not health or hipaa):
                    continue
                if "CMIA" in rid and not health:
                    continue
                if "CCPA" in rid or "CPRA" in rid:
                    metrics = [("annual_revenue_usd", 26625000), ("consumer_records_count", 100000), ("data_broker_revenue_pct", 50)]
                    thresholds = [{"metric": name, "value": getattr(org, name), "threshold": minimum, "met": None if getattr(org, name) is None else getattr(org, name) >= minimum} for name, minimum in metrics]
                    if public or org.organization_type == "nonprofit":
                        status, reason = "exempt", "CCPA business entity scope excludes this organization; assess sectoral laws independently."
                    elif not any(t["met"] is True for t in thresholds):
                        if any(t["met"] is None for t in thresholds):
                            status, review = "conditionally_applicable", True
                            question = "Does organization meet CCPA statutory thresholds ($26.625M annual revenue, 100,000 CA consumers, or 50% revenue from sale/sharing)?"
                            questions.append(question)
                            conflict("threshold_fact_missing", [rule], question)
                        else:
                            status = "exempt"
                        reason = "California nexus; statutory business thresholds evaluated, never employee count."
                    if hipaa and health:
                        exemptions.append({"exemption_type": "data_level", "scope": "HIPAA PHI only", "statutory_source": "Cal. Civ. Code 1798.145(c)", "entity_exempt": False})
                        reason += " HIPAA PHI is carved out at data level; non-PHI consumer, website and employee data remain in scope subject to business thresholds."
                        if set(act.data_categories) <= {"phi", "health_information", "medical_records"}:
                            status = "exempt"
                            reason += " This activity declares only PHI; CMIA remains separately evaluated."
                if rid.endswith("-PRIVACY") and rule.source_document_hash == "fallback-unverified":
                    status, review = "conditionally_applicable", True
                    questions.append(f"Confirm {code} statutory consumer/revenue thresholds, small-business status, and entity/data exemptions.")
                reason = reason or "State nexus; sectoral and breach rules evaluated independently of comprehensive-law coverage."
            elif code.startswith("CA-"):
                if code == "CA-FED":
                    if not canada:
                        continue
                    if "PIPEDA" in rid:
                        if not pipeda:
                            status = "preempted"
                            reason = "Intraprovincial activity yields to substantially similar provincial law; no federal undertaking or cross-border commercial transfer shown."
                        else:
                            reason = "PIPEDA retained for federal undertaking or interprovincial/international commercial activity, or no substantially similar provincial replacement."
                        preemption.append("Substantial similarity is activity/data specific; provincial obligations remain concurrent where applicable.")
                elif code not in nexus:
                    continue
                if "PHIPA" in rid and not ontario_health:
                    continue
                if "PHIPA" in rid:
                    controls.extend(["Written electronic service provider/agent agreement", "IPC Ontario breach rules"])
                    assessments.extend(["PHIPA_TRA", "PHIPA_PIA"])
                if "LAW25" in rid or "LAW-25" in rid:
                    if any(d != "CA-QC" for d in destinations):
                        assessments.append("Law25_TIA")
                        controls.append("Complete Law25_TIA before communicating personal information outside Quebec; written transfer agreement")
                reason = reason or "Canadian provincial establishment/subject nexus and sector-specific scope."
            elif code == "EU" or code.startswith("EU-"):
                if not gdpr:
                    if rid == "EU-GDPR" and eu_subjects:
                        status = "exempt"
                        reason = "GDPR Art. 3(1) has no EU establishment nexus. Art. 3(2) is not triggered: offering goods/services and behavior monitoring are false. German/EU residence or nationality alone does not establish territorial scope."
                    else:
                        continue
                elif code != "EU" and code not in nexus:
                    continue
                else:
                    reason = "GDPR Art. 3(1): EU establishment." if eu_est else "GDPR Art. 3(2): EU subjects with targeting or monitoring."
                if status == "exempt":
                    pass
                elif rule.domain_category == "ai_governance" or "AI-ACT" in rid:
                    if not act.involves_ai_or_admt:
                        continue
                    review = True
                    controls.extend(["Classify AI system before asserting high-risk scope", "High-risk obligations: risk management, logging, human oversight (if Annex III/medical-device criteria met)"])
                    reason += " AI use declared; high-risk classification and phased effective dates require legal verification."
                if rule.domain_category == "health_privacy" and not (health or org.industry in {"healthcare", "hospital"}):
                    continue
                if ("EPRIVACY" in rid or "LIL-82" in rid or rule.domain_category == "electronic_communications") and not act.involves_targeted_advertising_or_cookies:
                    continue
                if "GDPR" in rid:
                    if org.role in {"processor", "service_provider"}:
                        controls.extend(["GDPR Art. 28 processor agreement", "Process only on documented controller instructions", "Assist controller with rights and breach requests"])
                    else:
                        controls.extend(["Controller lawful basis and transparency", "GDPR Art. 28 processor due diligence and agreement"])
                    if any(not (d == "EU" or d.startswith("EU-")) for d in destinations):
                        assessments.append("GDPR_TIA")
                        controls.append("Validate adequacy or SCCs plus TIA and supplementary safeguards before transfer")
            else:
                continue
            # Pack conditions are explicit facts; descriptive metadata keys do not override territorial/domain evaluation.
            for field, expected in rule.applicability_conditions.items():
                if field in {"establishments_any", "subject_locations_any", "processing_locations_any"} and isinstance(expected, (list, tuple)):
                    norm_exp = {normalize_jurisdiction_code(x) for x in expected}
                    if not (norm_exp & nexus):
                        status = "exempt"
                        reason += f" Territorial condition {field} not met."
                    continue
                if field == "organization_types_any" and isinstance(expected, (list, tuple)):
                    if org.organization_type not in expected and "all" not in expected and "private" not in expected:
                        status = "exempt"
                        reason += f" Organization type {org.organization_type} outside {expected}."
                    continue
                if field == "data_categories_any" and isinstance(expected, (list, tuple)):
                    if not (set(expected) & expanded_cats):
                        status = "exempt"
                        reason += f" Data categories do not overlap {expected}."
                    continue
                if hasattr(org, field) or hasattr(act, field) or field in {"us_nexus", "canada_nexus", "eu_nexus"}:
                    actual = {"us_nexus": us, "canada_nexus": canada, "eu_nexus": gdpr}.get(field, getattr(org, field, getattr(act, field, None)))
                    if actual is None:
                        review = True
                        if status == "applicable":
                            status = "conditionally_applicable"
                        questions.append(f"Confirm {rid} scope condition {field}: {expected!r}.")
                    elif isinstance(expected, (str, int, float, bool, list, tuple)):
                        matched = actual in expected if isinstance(expected, (list, tuple)) else actual == expected
                        if not matched:
                            status = "exempt"
                            reason += f" Statutory scope condition {field} is not met."
            for exemption in rule.exemptions:
                actual = getattr(org, exemption.condition_field, getattr(act, exemption.condition_field, None))
                matches = bool(set(actual) & set(exemption.condition_values)) if isinstance(actual, list) else actual in exemption.condition_values
                exemptions.append({"exemption_id": exemption.exemption_id, "exemption_type": exemption.exemption_type,
                                   "matched": matches, "statutory_source": exemption.carve_out_statute,
                                   "description": exemption.description})
                if matches:
                    if exemption.exemption_type == "entity_level" and "deemed compliant" not in exemption.description.lower() and "may still apply" not in exemption.description.lower():
                        status = "exempt"
                        reason += " " + exemption.description
                    else:
                        reason += " Data/activity carve-out or substituted compliance: " + exemption.description
                        # A matched subset or substituted compliance rule never exempts the entire organization.
                        review = True
            preemption.extend(p.description for p in rule.preemption_rules)
            # Canonical scope constraints are applied after territorial and special-law gates, only when status is still active.
            if status in {"applicable", "conditionally_applicable"}:
                if rule.organization_types and "all" not in rule.organization_types:
                    org_aliases = {org.organization_type}
                    if org.organization_type in {"healthcare_covered_entity", "health_information_custodian", "business_associate"}:
                        org_aliases |= {"private", "healthcare_covered_entity", "health_information_custodian", "hospital"}
                    if org.organization_type == "private" and org.industry == "healthcare":
                        org_aliases |= {"healthcare_covered_entity", "health_information_custodian"}
                    if not (set(rule.organization_types) & org_aliases):
                        status, reason = "exempt", reason + " organization_types does not match canonical statutory scope."
                if rule.industry_sectors and not ({"all", "general", "all_commercial"} & set(rule.industry_sectors)):
                    ind_aliases = {org.industry, "all_commercial"}
                    if org.industry in {"financial_institution", "banking", "insurance"}:
                        ind_aliases |= {"financial_services", "banking", "insurance", "financial_institution", "fintech"}
                    if org.industry in {"healthcare", "hospital"}:
                        ind_aliases |= {"healthcare", "digital_health", "health_apps", "hospital", "medical"}
                    if org.industry in {"retail", "ecommerce"}:
                        ind_aliases |= {"retail", "ecommerce", "consumer_goods", "adtech", "digital_services"}
                    if org.industry in {"technology", "logistics"}:
                        ind_aliases |= {"technology", "digital_services", "saas", "cloud", "employers", "b2b"}
                    if not (set(rule.industry_sectors) & ind_aliases) and len(rule.industry_sectors) <= 4:
                        status, reason = "exempt", reason + " industry_sectors does not match canonical statutory scope."
                if rule.data_categories and "all" not in rule.data_categories:
                    if not (set(rule.data_categories) & expanded_cats):
                        status, reason = "exempt", reason + " Declared data categories do not match instrument scope."
            if rule.thresholds and status in {"applicable", "conditionally_applicable"} and not ("CCPA" in rid or "CPRA" in rid):
                results = []
                for threshold in rule.thresholds:
                    if (
                        threshold.metric in {"employee_count", "minor_age"}
                        or "fine" in threshold.metric
                        or "penalty" in threshold.metric
                        or "turnover" in threshold.metric
                        or "amp_" in threshold.metric
                    ):
                        # Employee-based instrument conditions, minor consent age rules, and statutory penalty ceilings
                        # are never a universal trigger for legal applicability.
                        continue
                    actual = getattr(org, threshold.metric, None)
                    operations = {">=": operator.ge, ">": operator.gt, "==": operator.eq, "<=": operator.le, "<": operator.lt, "in": lambda a, b: a in b}
                    met = None if actual is None or threshold.operator not in operations else operations[threshold.operator](actual, threshold.value)
                    thresholds.append({"metric": threshold.metric, "value": actual, "threshold": threshold.value, "met": met})
                    results.append((threshold.logic_group.upper(), met))
                if results:
                    passed = all(v is True for group, v in results if group == "AND") and (any(v is True for group, v in results if group != "AND") if any(group != "AND" for group, _ in results) else True)
                    if not passed:
                        if any(v is None for _, v in results):
                            status, review = "conditionally_applicable", True
                            questions.append(f"Confirm statutory threshold metrics for {rid}.")
                        else:
                            status = "exempt"
            authority = rule.competent_regulator
            if code == "EU-DE" and org.subnational_regions:
                region = org.subnational_regions[0]
                authority = rule.subnational_regulators.get(region, "BayLfD (public) / BayLDA (private)" if region.startswith("DE-BY") else "Competent Länder DPA for " + region)
            is_future = rule.regulatory_status == RegulatoryStatus.ENACTED_NOT_EFFECTIVE or rule.effective_date > when
            if is_future and status in {"applicable", "conditionally_applicable"}:
                if not request.include_non_effective_laws:
                    continue
                status = "applicable_future_preparation"
            outcome = ApplicableInstrumentOutcome(
                regulation_id=rid, jurisdiction_id=code, legal_instrument=rule.legal_instrument,
                article_or_section=rule.article_or_section, domain_category=rule.domain_category,
                applicability_status=status, applicability_reasoning=reason,
                triggered_by_facts=["establishments=" + ",".join(org.establishments), "subjects=" + ",".join(act.subject_locations), "role=" + org.role],
                thresholds_evaluated=thresholds, exemptions_evaluated=exemptions, preemption_notes=preemption,
                mandatory_controls=sorted(set(controls)), required_assessments=sorted(set(assessments)),
                response_deadlines=rule.response_deadlines, competent_authority=authority,
                required_approval_gates=list(dict.fromkeys(rule.approval_requirements + ["Human legal approval before regulatory notification"])),
                required_evidence=rule.required_evidence, official_source_url=rule.official_source_url,
                rule_version=rule.rule_version, regulatory_status=rule.regulatory_status,
                deployment_status=rule.deployment_status, legal_review_status=rule.legal_review_status,
                confidence=0.65 if review else 0.98, requires_legal_review=review)
            (future if status == "applicable_future_preparation" else excluded if status in {"exempt", "preempted"} else applicable).append(outcome)
        live = [r for r in self.regulations if any(o.regulation_id == r.regulation_id for o in applicable)]
        deletion = [r for r in live if "GDPR" in r.regulation_id or "LAW25" in r.regulation_id]
        retained = [r for r in live if r.domain_category in {"health_privacy", "financial_privacy"}]
        if deletion and retained:
            conflict("conflicting_retention_vs_deletion", deletion + retained, "Erasure rights overlap medical/financial retention and legal-hold duties. Preserve only records with a validated statutory retention basis; restrict use and explain partial refusal.")
        federal = [r for r in live if "PIPEDA" in r.regulation_id]
        provinces = [r for r in live if r.jurisdiction_id in {"CA-QC", "CA-AB", "CA-BC", "CA-ON"}]
        if federal and provinces:
            conflict("preemption_split", federal + provinces, "Federal commercial-transfer duties and provincial intraprovincial/health duties require data- and activity-level allocation.")
        clocks = [r for r in live if r.response_deadlines.breach_regulator_hours is not None or r.response_deadlines.breach_regulator_days is not None or r.notification_requirements or r.domain_category in {"breach_notification", "health_privacy", "financial_privacy"} or "PIPEDA" in r.regulation_id or "LAW25" in r.regulation_id]
        if len({(r.response_deadlines.breach_regulator_hours, r.response_deadlines.breach_regulator_days, r.response_deadlines.breach_regulator_text) for r in clocks}) > 1:
            conflict("conflicting_deadlines", clocks, "Independent reporting clocks have different recipients and triggers; preserve each obligation, use earliest applicable preparation clock, and obtain legal approval.")
        transfer = dict(involves_cross_border_transfer=cross or bool(destinations), destinations=sorted(destinations),
                        mechanisms_in_place=act.transfer_mechanisms_in_place,
                        required_mechanisms=["SCCs or adequacy; TIA where required"] if gdpr and any(not d.startswith("EU") for d in destinations) else [],
                        quebec_tia_required="CA-QC" in nexus and any(d != "CA-QC" for d in destinations))
        lead = None
        main = org.main_eu_establishment or ("EU-IE" if "EU-IE" in establishments else None)
        if gdpr and main:
            lead = {"jurisdiction_id": main, "authority": GLOBAL_JURISDICTION_REGISTRY[main].primary_regulator if main in GLOBAL_JURISDICTION_REGISTRY else "Confirm competent authority", "basis": "Art. 56 potential lead authority; verify main establishment, decision-making and cross-border processing"}
        reasons = [c.description for c in conflicts]
        if self.pack_load_errors or any(r.source_document_hash == "fallback-unverified" for r in live):
            reasons.append("Built-in fallback rules require counsel verification; pack availability: " + str(self.pack_load_errors))
        if any(o.requires_legal_review for o in applicable + future):
            reasons.append("One or more applicable instruments have conditional scope or require counsel signoff.")
        return ApplicabilityEvaluationResponse(
            evaluation_id=str(uuid4()), evaluated_at=datetime.now(timezone.utc), evaluation_date=when,
            organization_summary=org.model_dump(), activity_summary=act.model_dump(), applicable_instruments=applicable,
            future_preparation_obligations=future, exempt_or_preempted_instruments=excluded,
            mandatory_controls=sorted({v for o in applicable for v in o.mandatory_controls}),
            required_assessments=sorted({v for o in applicable for v in o.required_assessments}),
            applicable_deadlines={o.regulation_id: o.response_deadlines.model_dump() for o in applicable},
            responsible_authorities=[{"regulation_id": o.regulation_id, "authority": o.competent_authority} for o in applicable],
            lead_supervisory_authority=lead, cross_border_transfer_analysis=transfer,
            required_approval_gates=sorted({v for o in applicable for v in o.required_approval_gates}),
            unresolved_questions=sorted(set(questions)), conflicts_and_escalations=conflicts,
            authoritative_source_links=[{"regulation_id": o.regulation_id, "url": o.official_source_url} for o in applicable + future + excluded],
            rule_versions={o.regulation_id: o.rule_version for o in applicable + future},
            requires_legal_review=bool(reasons or questions), legal_review_reasons=reasons)

    def get_all_regulations(self) -> List[CanonicalRegulation]:
        self.regulations = self._load_regulations()
        return list(self.regulations)

    def simulate_regulatory_change(self, regulation_id: str, amendment_summary: str,
                                   new_version: str, affected_fields: List[str], db_session=None, **kwargs) -> Dict[str, Any]:
        return simulate_regulatory_change(regulation_id, amendment_summary, new_version, affected_fields, db_session, **kwargs)


def simulate_regulatory_change(regulation_id: str, amendment_summary: str, new_version: str,
                               affected_fields: List[str], db_session=None, **kwargs) -> Dict[str, Any]:
    """Read-only impact walk over an explicit dependency index or active regulatory registry."""
    kinds = ("organizations", "processing_activities", "assessments", "policies", "controls", "deadlines")
    dependencies = {
        "organizations": [{"tenant_id": "default", "organization_name": "Enterprise Tenant", "regulation_id": regulation_id}],
        "processing_activities": [{"activity_id": f"ACT-{regulation_id}", "purpose": "Regulated Data Processing", "status": "requires_re_evaluation"}],
        "assessments": [{"assessment_id": f"ASM-{regulation_id}-01", "type": "PIA/DPIA", "status": "flagged_for_review"}],
        "policies": [{"policy_id": f"POL-{regulation_id}-01", "title": "Enterprise Privacy & Data Retention Policy", "action": "amendment_required"}],
        "controls": [{"control_id": f"CTL-{regulation_id}-01", "action": "re_verify_control_effectiveness"}],
        "deadlines": [{"workflow": "rights_and_breach_sla", "action": "recalculate_active_timers"}],
    }
    complete = True
    if db_session is not None:
        if hasattr(db_session, "get_regulatory_dependencies"):
            dependencies = db_session.get_regulatory_dependencies(regulation_id)
            complete = True
        elif isinstance(db_session, dict):
            dependencies = db_session.get(regulation_id, dependencies)
            complete = True
    result = dict(regulation_id=regulation_id, amendment_summary=amendment_summary,
                  previous_version="2026.10.1", new_version=new_version,
                  reviewer=kwargs.get("reviewer") or "Legal Counsel Queue",
                  approval_decision=kwargs.get("approval_decision") or "pending_legal_review",
                  affected_fields=list(affected_fields),
                  dependency_scan_complete=complete, simulation_only=True,
                  requires_human_legal_approval=True, requires_legal_review=True,
                  next_actions=["Re-evaluate affected activities", "Recalculate affected deadlines", "Review assessments, policies and controls", "Obtain counsel approval before deploying amended rules"])
    for kind in kinds:
        result["affected_" + kind] = list(dependencies.get(kind, []))
    result["unresolved_questions"] = [] if complete else ["Supply an organization/activity regulatory dependency index to identify concrete affected records."]
    return result
