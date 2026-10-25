"""
KIBO Privacy OS — Statutory, Regulatory, and Legislative Bill Provision Annotation (Worker G17)
Implements Section 6.2 & RD-05/RD-08:
- Deterministic, source-grounded passage-level legal annotation (`LegalPassageAnnotation`)
- Multi-jurisdiction support across US Federal (HIPAA, FTC, GLBA, COPPA), US State (CCPA/CPRA, etc.),
  Canada Federal & Provincial (PIPEDA, Quebec Law 25 in EN/FR), and EU / Member States (GDPR, German BDSG, French CNIL, etc.)
- Uses `MultilingualLegalParser().extract_provisions(doc.normalized_text, language=doc.language)` to extract
  provisions with guaranteed character-offset slicing (`doc.normalized_text[ann.text_start_offset:ann.text_end_offset] == ann.exact_source_excerpt`)
- Never relies on LLM confidence alone as evidence of legal correctness; sets `interpretation_status="source_grounded_deterministic"`
  when grounded in explicit statutory rules or `"requires_legal_review"` when ambiguous or based on unverified translations.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from core.regulatory_intelligence import (
    CanonicalLegalDocument,
    DocumentClassType,
    LegalPassageAnnotation,
    compute_sha256_hex,
)
from core.regulatory_intelligence.parsers.multilingual_parser import MultilingualLegalParser


# Default authoritative regulator lookup by canonical jurisdiction_id
DEFAULT_REGULATORY_AUTHORITY_BY_JURISDICTION: Dict[str, str] = {
    "US-FED": "U.S. Department of Health and Human Services (HHS OCR) / Federal Trade Commission (FTC)",
    "US-CA": "California Privacy Protection Agency (CPPA) & California Attorney General",
    "US-VA": "Virginia Office of the Attorney General",
    "US-CO": "Colorado Office of the Attorney General",
    "US-CT": "Connecticut Office of the Attorney General",
    "US-TX": "Texas Office of the Attorney General",
    "US-NY": "New York State Office of the Attorney General / NYDFS",
    "CA-FED": "Office of the Privacy Commissioner of Canada (OPC / Commissariat à la protection de la vie privée du Canada)",
    "CA-QC": "Commission d'accès à l'information du Québec (CAI)",
    "CA-ON": "Information and Privacy Commissioner of Ontario (IPC)",
    "CA-BC": "Office of the Information and Privacy Commissioner for British Columbia (OIPC BC)",
    "CA-AB": "Office of the Information and Privacy Commissioner of Alberta (OIPC AB)",
    "EU": "European Data Protection Board (EDPB) & National Supervisory Authorities",
    "EU-DE": "Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI) & Landesdatenschutzbehörden",
    "EU-FR": "Commission Nationale de l'Informatique et des Libertés (CNIL)",
    "EU-IE": "Data Protection Commission (DPC Ireland)",
    "EU-ES": "Agencia Española de Protección de Datos (AEPD)",
    "EU-IT": "Garante per la protezione dei dati personali",
    "EU-NL": "Autoriteit Persoonsgegevens (AP)",
    "UK": "Information Commissioner's Office (ICO)",
}


class StatutoryProvisionAnnotator:
    """
    Deterministic, source-grounded annotator that converts a `CanonicalLegalDocument`
    (statute, regulation, legislative bill, or official directive/guidance) into a list
    of `LegalPassageAnnotation` records with verified character offsets.

    Guarantees:
    1. `doc.normalized_text[ann.text_start_offset:ann.text_end_offset] == ann.exact_source_excerpt`
       holds for every produced `LegalPassageAnnotation`.
    2. Never uses LLM confidence alone as evidence of legal correctness.
    3. Explicitly flags ambiguous provisions, unverified machine translations, or non-enacted
       legislative bills with `interpretation_status="requires_legal_review"` and
       `verification_status="REQUIRES_LEGAL_REVIEW"`.
    """

    EXTRACTION_MODEL_ID = "kibo-deterministic-legal-annotator-v2.1"

    def __init__(self, parser: Optional[MultilingualLegalParser] = None) -> None:
        self.parser = parser or MultilingualLegalParser()

    def annotate_document(self, doc: CanonicalLegalDocument) -> List[LegalPassageAnnotation]:
        """
        Extracts statutory/regulatory provisions from `doc.normalized_text` and produces
        source-grounded `LegalPassageAnnotation` records.
        """
        if not doc.normalized_text or not doc.normalized_text.strip():
            return []

        provisions = self.parser.extract_provisions(
            doc.normalized_text,
            language=doc.language,
        )

        annotations: List[LegalPassageAnnotation] = []
        for idx, prov in enumerate(provisions):
            start_offset: int = int(prov["text_start_offset"])
            end_offset: int = int(prov["text_end_offset"])
            excerpt: str = str(prov["exact_source_excerpt"])

            # Strict invariant enforcement: exact slice match against doc.normalized_text
            if doc.normalized_text[start_offset:end_offset] != excerpt:
                raise ValueError(
                    f"Offset invariant failed for document {doc.document_id} at [{start_offset}:{end_offset}]"
                )

            source_section: str = str(prov["source_section"])
            article: Optional[str] = prov.get("article")
            subsection: Optional[str] = prov.get("subsection")
            paragraph: Optional[str] = prov.get("paragraph")
            source_language: str = str(prov.get("source_language") or doc.language or "en")

            # Deterministic legal analysis of the provision text and document metadata
            analysis = self._analyze_provision_deterministically(
                excerpt=excerpt,
                source_section=source_section,
                language=source_language,
                doc=doc,
            )

            annotation_digest = compute_sha256_hex(
                f"{doc.document_id}:{doc.document_version}:{source_section}:{start_offset}:{end_offset}"
            )[:16].upper()
            annotation_id = f"ANN-{doc.jurisdiction_id}-{idx + 1:03d}-{annotation_digest}"

            ann = LegalPassageAnnotation(
                annotation_id=annotation_id,
                document_id=doc.document_id,
                document_version=doc.document_version,
                annotation_type=analysis["annotation_type"],
                jurisdiction_id=doc.jurisdiction_id,
                source_section=source_section,
                article=article,
                subsection=subsection,
                paragraph=paragraph,
                page_number=None,
                text_start_offset=start_offset,
                text_end_offset=end_offset,
                exact_source_excerpt=excerpt,
                source_language=source_language,
                normalized_legal_concept=analysis["normalized_legal_concept"],
                plain_language_explanation=analysis["plain_language_explanation"],
                legal_requirement=analysis["legal_requirement"],
                applicability_conditions=analysis["applicability_conditions"],
                exemptions=analysis["exemptions"],
                thresholds=analysis["thresholds"],
                effective_date=doc.effective_date,
                statutory_deadline=analysis["statutory_deadline"],
                affected_organization_types=analysis["affected_organization_types"],
                affected_industries=analysis["affected_industries"],
                affected_data_categories=analysis["affected_data_categories"],
                affected_processing_activities=analysis["affected_processing_activities"],
                regulatory_authority=analysis["regulatory_authority"],
                required_controls=analysis["required_controls"],
                required_assessments=analysis["required_assessments"],
                related_regulations=analysis["related_regulations"],
                related_decisions=[],
                interpretation_status=analysis["interpretation_status"],
                evidence_strength=analysis["evidence_strength"],
                extraction_model=self.EXTRACTION_MODEL_ID,
                extraction_timestamp=datetime.utcnow(),
                verification_status=analysis["verification_status"],
            )

            # Final verification of the exact character-slice invariant
            assert doc.normalized_text[ann.text_start_offset : ann.text_end_offset] == ann.exact_source_excerpt
            annotations.append(ann)

        return annotations

    def _analyze_provision_deterministically(
        self,
        excerpt: str,
        source_section: str,
        language: str,
        doc: CanonicalLegalDocument,
    ) -> Dict[str, Any]:
        text_lower = excerpt.lower()
        sec_lower = source_section.lower()
        jur = (doc.jurisdiction_id or "").upper()
        lang = (language or doc.language or "en").lower().split("-")[0]

        # 1. Determine concept domain and rule profile
        concept_profile = self._match_concept_profile(
            excerpt=excerpt,
            text_lower=text_lower,
            sec_lower=sec_lower,
            jur=jur,
            lang=lang,
            doc=doc,
        )

        # 2. Extract deterministic thresholds (employee counts, consumer counts, dollar revenue, day counts)
        thresholds = self._extract_thresholds(excerpt, text_lower, lang, concept_profile["base_thresholds"])

        # 3. Extract statutory deadline if present in text or profile
        statutory_deadline = self._extract_statutory_deadline(
            excerpt, text_lower, lang, concept_profile.get("default_deadline")
        )

        # 4. Extract exemptions from text or profile
        exemptions = self._extract_exemptions(excerpt, text_lower, lang, concept_profile["exemptions"])

        # 5. Extract applicability conditions
        applicability_conditions = self._extract_applicability_conditions(
            excerpt, text_lower, lang, jur, concept_profile["applicability_conditions"]
        )

        # 6. Determine annotation_type deterministically
        annotation_type = self._determine_annotation_type(
            text_lower=text_lower,
            lang=lang,
            has_thresholds=bool(thresholds),
            has_deadline=statutory_deadline is not None,
            has_exemptions=bool(exemptions),
            default_type=concept_profile["annotation_type"],
        )

        # 7. Determine regulatory authority
        regulatory_authority = self._resolve_regulatory_authority(doc, jur, text_lower)

        # 8. Determine interpretation_status & verification_status strictly without LLM confidence
        is_unverified_translation = doc.translation_status == "unverified_machine_translation"
        is_pending_bill = doc.document_type == DocumentClassType.LEGISLATIVE_BILL
        is_ambiguous = bool(concept_profile.get("is_ambiguous", False)) or self._has_unresolved_ambiguity(
            excerpt, text_lower, lang
        )

        if is_unverified_translation or is_pending_bill or is_ambiguous:
            interpretation_status = "requires_legal_review"
            verification_status = "REQUIRES_LEGAL_REVIEW"
        else:
            interpretation_status = "source_grounded_deterministic"
            verification_status = "VERIFIED"

        evidence_strength = (
            "pending_legislative_text"
            if is_pending_bill
            else (
                "unverified_translation_text"
                if is_unverified_translation
                else "authoritative_primary_text"
            )
        )

        return {
            "annotation_type": annotation_type,
            "normalized_legal_concept": concept_profile["normalized_legal_concept"],
            "plain_language_explanation": concept_profile["plain_language_explanation"],
            "legal_requirement": concept_profile["legal_requirement"],
            "applicability_conditions": applicability_conditions,
            "exemptions": exemptions,
            "thresholds": thresholds,
            "statutory_deadline": statutory_deadline,
            "affected_organization_types": concept_profile["affected_organization_types"],
            "affected_industries": concept_profile["affected_industries"],
            "affected_data_categories": concept_profile["affected_data_categories"],
            "affected_processing_activities": concept_profile["affected_processing_activities"],
            "regulatory_authority": regulatory_authority,
            "required_controls": concept_profile["required_controls"],
            "required_assessments": concept_profile["required_assessments"],
            "related_regulations": concept_profile["related_regulations"],
            "interpretation_status": interpretation_status,
            "verification_status": verification_status,
            "evidence_strength": evidence_strength,
        }

    def _match_concept_profile(
        self,
        excerpt: str,
        text_lower: str,
        sec_lower: str,
        jur: str,
        lang: str,
        doc: CanonicalLegalDocument,
    ) -> Dict[str, Any]:
        """
        Matches the statutory provision against deterministic multi-jurisdictional legal concept rules.
        Covers US Federal (HIPAA, GLBA, COPPA, FTC), California (CCPA/CPRA), Canada/Quebec (PIPEDA, Law 25),
        Germany/EU (BDSG, GDPR/DSGVO), and general statutory clauses.
        """
        # Profile 1: HIPAA Breach Notification to Individuals (45 CFR § 164.404) & Breach Notification
        if (
            "164.404" in sec_lower
            or "164.404" in text_lower
            or ("unsecured protected health information" in text_lower and ("breach" in text_lower or "notify" in text_lower))
            or ("notification to individuals" in text_lower and "protected health information" in text_lower)
        ):
            return {
                "annotation_type": "statutory_obligation",
                "normalized_legal_concept": "breach_notification_to_individuals_hipaa",
                "plain_language_explanation": (
                    "A HIPAA covered entity must notify each affected individual without unreasonable delay "
                    "and in no case later than 60 calendar days after discovering a breach of unsecured "
                    "protected health information (PHI)."
                ),
                "legal_requirement": (
                    "Provide written notification of a breach of unsecured protected health information to "
                    "each affected individual without unreasonable delay and within 60 calendar days after "
                    "discovery of the breach (45 CFR § 164.404)."
                ),
                "applicability_conditions": [
                    "Entity is a HIPAA covered entity or business associate handling protected health information",
                    "Discovery of a breach of unsecured protected health information (PHI)",
                ],
                "exemptions": [
                    "Law enforcement delay pursuant to 45 CFR § 164.412",
                    "Encrypted or destroyed PHI rendered unusable, unreadable, or indecipherable under HHS guidance",
                ],
                "base_thresholds": {"max_notification_delay_calendar_days": 60},
                "default_deadline": "Without unreasonable delay and in no case later than 60 calendar days after discovery of a breach",
                "affected_organization_types": [
                    "covered_entity",
                    "business_associate",
                    "healthcare_provider",
                    "health_plan",
                    "healthcare_clearinghouse",
                ],
                "affected_industries": ["healthcare", "health_insurance", "healthtech", "life_sciences"],
                "affected_data_categories": [
                    "protected_health_information_phi",
                    "unsecured_phi",
                    "medical_records",
                    "health_identifiers",
                ],
                "affected_processing_activities": [
                    "incident_detection",
                    "breach_assessment",
                    "individual_breach_notification",
                    "phi_storage_and_transmission",
                ],
                "required_controls": [
                    "CTRL-INCIDENT-BREACH-NOTIFICATION-60D",
                    "CTRL-PHI-ENCRYPTION-AT-REST-AND-TRANSIT",
                    "CTRL-BREACH-DISCOVERY-TRACKING-LOG",
                ],
                "required_assessments": [
                    "ASSESS-HIPAA-FOUR-FACTOR-BREACH-RISK-ASSESSMENT",
                ],
                "related_regulations": ["45 CFR § 164.400", "45 CFR § 164.402", "45 CFR § 164.406", "45 CFR § 164.408", "HITECH Act § 13402"],
                "is_ambiguous": False,
            }

        # Profile 2: California CCPA / CPRA § 1798.100 (General Duties of Businesses / Notice at Collection / Purpose Limitation / Retention)
        if (
            "1798.100" in sec_lower
            or "1798.100" in text_lower
            or (
                ("at or before the point of collection" in text_lower or "categories of personal information" in text_lower)
                and ("business" in text_lower and "consumer" in text_lower)
            )
        ):
            return {
                "annotation_type": "statutory_obligation",
                "normalized_legal_concept": "notice_at_collection_and_purpose_limitation_ccpa",
                "plain_language_explanation": (
                    "Under Cal. Civ. Code § 1798.100, a business collecting consumer personal information must "
                    "inform consumers at or before the point of collection of the categories of personal and "
                    "sensitive personal information to be collected, the purposes for which they are used, "
                    "whether the information is sold or shared, and the retention period or criteria, and must "
                    "not collect or retain personal information beyond what is reasonably necessary and proportionate."
                ),
                "legal_requirement": (
                    "Provide a compliant Notice at Collection at or before the point of collection disclosing "
                    "categories, purposes, sale/sharing status, and retention periods, and enforce purpose "
                    "limitation, data minimization, and retention limits (Cal. Civ. Code § 1798.100)."
                ),
                "applicability_conditions": [
                    "For-profit business doing business in the State of California meeting CCPA/CPRA statutory thresholds (Cal. Civ. Code § 1798.140(d))",
                    "Collection of personal information or sensitive personal information from California consumers",
                ],
                "exemptions": [
                    "Medical information governed by CMIA or PHI governed by HIPAA (Cal. Civ. Code § 1798.145(c))",
                    "Deidentified or aggregate consumer information (Cal. Civ. Code § 1798.145)",
                ],
                "base_thresholds": {},
                "default_deadline": "At or before the point of collection",
                "affected_organization_types": ["business", "data_controller", "service_provider", "third_party"],
                "affected_industries": ["technology", "retail", "e_commerce", "advertising_technology", "consumer_services", "financial_services"],
                "affected_data_categories": [
                    "personal_information",
                    "sensitive_personal_information",
                    "consumer_identifiers",
                    "online_behavioral_data",
                ],
                "affected_processing_activities": [
                    "data_collection",
                    "notice_at_collection_delivery",
                    "data_retention_and_deletion",
                    "data_selling_or_sharing",
                    "purpose_limitation_enforcement",
                ],
                "required_controls": [
                    "CTRL-CCPA-NOTICE-AT-COLLECTION",
                    "CTRL-DATA-RETENTION-SCHEDULE-ENFORCEMENT",
                    "CTRL-PURPOSE-LIMITATION-AND-MINIMIZATION-GATE",
                ],
                "required_assessments": [
                    "ASSESS-CPRA-DATA-MINIMIZATION-PROPORTIONALITY-REVIEW",
                    "ASSESS-DATA-RETENTION-SCHEDULE-AUDIT",
                ],
                "related_regulations": ["Cal. Civ. Code § 1798.105", "Cal. Civ. Code § 1798.110", "Cal. Civ. Code § 1798.120", "11 CCR § 7012"],
                "is_ambiguous": False,
            }

        # Profile 3: Quebec Law 25 Art. 17 / Cross-Border Communication Outside Quebec (French & English)
        if (
            (
                ("à l'extérieur du québec" in text_lower or "extérieur du québec" in text_lower or "outside québec" in text_lower or "outside quebec" in text_lower)
                and ("évaluation des facteurs relatifs à la vie privée" in text_lower or "renseignement personnel" in text_lower or "privacy impact assessment" in text_lower or "communiquer" in text_lower)
            )
            or (jur in ("CA-QC", "CA-FED") and ("article 17" in sec_lower or "art. 17" in sec_lower) and ("québec" in text_lower or "quebec" in text_lower or "évaluation" in text_lower))
        ):
            return {
                "annotation_type": "statutory_obligation",
                "normalized_legal_concept": "cross_border_data_transfer_pia_quebec_law25",
                "plain_language_explanation": (
                    "Before communicating personal information outside Québec (including entrusting a third party "
                    "outside Québec with collecting, using, communicating, or keeping it), an enterprise must "
                    "conduct a Privacy Impact Assessment (Évaluation des facteurs relatifs à la vie privée — ÉFVP) "
                    "evaluating data sensitivity, purposes, protection measures (including contractual clauses), "
                    "and the legal framework of the destination jurisdiction, and may transfer the data only if "
                    "adequate protection is ensured and governed by a written agreement (Loi 25, art. 17)."
                ),
                "legal_requirement": (
                    "Conduct a mandatory Privacy Impact Assessment (Évaluation des facteurs relatifs à la vie privée) "
                    "prior to any communication of personal information outside Québec, verify adequate protection "
                    "against recognized privacy principles, and execute a written data protection agreement "
                    "mitigating identified risks (Québec Loi 25, art. 17 / LPRPSP art. 17)."
                ),
                "applicability_conditions": [
                    "Person or enterprise carrying on an enterprise in Québec (LPRPSP / Loi 25)",
                    "Communication or transfer of personal information outside the province of Québec, or entrusting a third party outside Québec with storage or processing",
                ],
                "exemptions": [
                    "Disclosure prevented if the Privacy Impact Assessment fails to demonstrate that the information will receive adequate protection",
                ],
                "base_thresholds": {},
                "default_deadline": "Avant de communiquer à l'extérieur du Québec (Prior to communicating personal information outside Québec)",
                "affected_organization_types": ["private_sector_enterprise", "data_controller", "cloud_service_processor"],
                "affected_industries": ["all_private_sector_industries_in_quebec", "technology", "cloud_computing", "financial_services", "retail", "healthcare"],
                "affected_data_categories": [
                    "renseignement_personnel",
                    "personal_information",
                    "sensitive_personal_information",
                ],
                "affected_processing_activities": [
                    "cross_border_data_transfer",
                    "third_party_vendor_entrustment",
                    "cloud_hosting_outside_quebec",
                    "privacy_impact_assessment_efvp",
                ],
                "required_controls": [
                    "CTRL-LAW25-CROSS-BORDER-TRANSFER-GATE",
                    "CTRL-WRITTEN-DATA-PROTECTION-CONTRACT-ART17",
                    "CTRL-DATA-LOCALIZATION-AND-TRANSFER-INVENTORY",
                ],
                "required_assessments": [
                    "ASSESS-QUEBEC-LAW25-EFVP-TRANSFER-IMPACT-ASSESSMENT",
                    "ASSESS-DESTINATION-JURISDICTION-LEGAL-ADEQUACY-REVIEW",
                ],
                "related_regulations": ["Loi 25 (L.Q. 2021, c. 25)", "LPRPSP art. 3.3", "LPRPSP art. 17", "LPRPSP art. 18.3", "PIPEDA Schedule 1 Principle 4.1.3"],
                "is_ambiguous": False,
            }

        # Profile 4: German BDSG § 38 (Datenschutzbeauftragter nichtöffentlicher Stellen / Data Protection Officer Designation)
        if (
            ("38" in sec_lower and ("bdsg" in sec_lower or "bdsg" in text_lower or "datenschutzbeauftragte" in text_lower or jur == "EU-DE"))
            or ("datenschutzbeauftragte" in text_lower and ("zwanzig" in text_lower or "20" in text_lower or "artikels 37" in text_lower or "artikel 37" in text_lower or "artikel 35" in text_lower))
            or (jur == "EU-DE" and "38" in (doc.official_citation or "") and ("datenschutzbeauftragte" in text_lower or "absatz" in sec_lower or "satz" in sec_lower))
        ):
            return {
                "annotation_type": "threshold",
                "normalized_legal_concept": "data_protection_officer_designation_threshold_bdsg_38",
                "plain_language_explanation": (
                    "Under § 38 BDSG (supplementing Article 37(1)(b) and (c) GDPR), non-public bodies (private-sector "
                    "controllers and processors) in Germany must designate a Data Protection Officer (Datenschutzbeauftragter) "
                    "if they constantly employ as a rule at least 20 persons dealing with the automated processing of "
                    "personal data, or if they undertake processing subject to a Data Protection Impact Assessment "
                    "(Art. 35 GDPR) or commercially process personal data for transfer or market/opinion research "
                    "irrespective of the number of employees."
                ),
                "legal_requirement": (
                    "Designate a statutory Data Protection Officer (Datenschutzbeauftragter) when at least 20 persons "
                    "are constantly engaged in automated processing of personal data (§ 38 Abs. 1 Satz 1 BDSG), or "
                    "regardless of employee headcount when processing requires a DPIA under Art. 35 GDPR or involves "
                    "commercial data transfer or market/opinion research (§ 38 Abs. 1 Satz 2 BDSG)."
                ),
                "applicability_conditions": [
                    "Non-public controller or processor (Verantwortlicher oder Auftragsverarbeiter nichtöffentlicher Stellen) subject to German BDSG",
                    "At least 20 persons constantly engaged in automated processing of personal data, OR processing subject to Art. 35 GDPR DPIA / commercial transfer / market research",
                ],
                "exemptions": [
                    "Non-public bodies with fewer than 20 persons engaged in automated processing that do not trigger Art. 37(1) GDPR or § 38 Abs. 1 Satz 2 BDSG high-risk/commercial processing",
                ],
                "base_thresholds": {
                    "min_persons_automated_processing": 20,
                    "employee_threshold_override_for_dpia_or_market_research": 1,
                },
                "default_deadline": "Unverzüglich bei Erreichen des Schwellenwerts bzw. vor Aufnahme der Verarbeitung (Upon reaching threshold or prior to commencing DPIA-relevant processing)",
                "affected_organization_types": [
                    "nichtoeffentliche_stelle",
                    "verantwortlicher_controller",
                    "auftragsverarbeiter_processor",
                ],
                "affected_industries": [
                    "all_private_sector_industries_in_germany",
                    "market_and_opinion_research",
                    "data_brokers_and_credit_agencies",
                    "technology",
                    "manufacturing",
                    "financial_services",
                ],
                "affected_data_categories": [
                    "personenbezogene_daten",
                    "personal_data",
                    "high_risk_processing_data",
                ],
                "affected_processing_activities": [
                    "automatisierte_verarbeitung_automated_processing",
                    "high_risk_processing_subject_to_dpia",
                    "geschäftsmäßige_übermittlung_commercial_data_transfer",
                    "markt_und_meinungsforschung_market_research",
                ],
                "required_controls": [
                    "CTRL-BDSG38-DPO-DESIGNATION-AND-REGISTRATION",
                    "CTRL-AUTOMATED-PROCESSING-HEADCOUNT-MONITOR",
                    "CTRL-DPO-CONTACT-PUBLICATION-AND-AUTHORITY-NOTICE",
                ],
                "required_assessments": [
                    "ASSESS-GDPR-ART35-DSFA-DPIA",
                    "ASSESS-BDSG38-DPO-OBLIGATION-THRESHOLD-AUDIT",
                ],
                "related_regulations": [
                    "§ 38 BDSG",
                    "Art. 35 DSGVO (GDPR)",
                    "Art. 37 DSGVO (GDPR)",
                    "Art. 38 DSGVO (GDPR)",
                    "Art. 39 DSGVO (GDPR)",
                ],
                "is_ambiguous": False,
            }

        # Profile 5: Canadian PIPEDA Principle 4.1.3 / Cross-border Processing / Accountability or Breach (Division 1.1 s. 10.1)
        if "pipeda" in text_lower or "p-21" in text_lower or (jur == "CA-FED" and ("breach of security safeguards" in text_lower or "real risk of significant harm" in text_lower or "comparable level of protection" in text_lower)):
            if "breach of security safeguards" in text_lower or "real risk of significant harm" in text_lower or "atteinte aux mesures de sécurité" in text_lower:
                return {
                    "annotation_type": "statutory_obligation",
                    "normalized_legal_concept": "breach_of_security_safeguards_reporting_pipeda",
                    "plain_language_explanation": (
                        "Under PIPEDA Division 1.1 (s. 10.1), an organization must report to the Privacy Commissioner "
                        "of Canada and notify affected individuals as soon as feasible after determining that a breach "
                        "of security safeguards involving personal information under its control creates a real risk "
                        "of significant harm (RROSH), and must maintain a record of every breach for 24 months."
                    ),
                    "legal_requirement": (
                        "Report breaches creating a real risk of significant harm (RROSH) to the OPC and notify "
                        "affected individuals as soon as feasible, and retain records of all security breaches for "
                        "at least 24 months (PIPEDA s. 10.1–10.3)."
                    ),
                    "applicability_conditions": [
                        "Organization subject to PIPEDA collecting, using, or disclosing personal information in the course of commercial activities",
                        "Breach of security safeguards involving personal information under the organization's control",
                    ],
                    "exemptions": [],
                    "base_thresholds": {"breach_record_retention_months": 24},
                    "default_deadline": "As soon as feasible after the organization determines that the breach has occurred",
                    "affected_organization_types": ["commercial_organization", "federal_work_undertaking_or_business"],
                    "affected_industries": ["all_canadian_commercial_sectors", "banking", "telecommunications", "transportation", "technology"],
                    "affected_data_categories": ["personal_information", "sensitive_personal_information"],
                    "affected_processing_activities": ["security_incident_response", "rrosh_assessment", "regulator_and_individual_breach_notification"],
                    "required_controls": ["CTRL-PIPEDA-BREACH-REGISTER-24M", "CTRL-PIPEDA-RROSH-NOTIFICATION-WORKFLOW"],
                    "required_assessments": ["ASSESS-PIPEDA-REAL-RISK-OF-SIGNIFICANT-HARM-RROSH"],
                    "related_regulations": ["PIPEDA s. 10.1", "PIPEDA s. 10.2", "PIPEDA s. 10.3", "Breach of Security Safeguards Regulations (SOR/2018-64)"],
                    "is_ambiguous": False,
                }
            return {
                "annotation_type": "statutory_obligation",
                "normalized_legal_concept": "accountability_and_third_party_transfer_safeguards_pipeda",
                "plain_language_explanation": (
                    "Under PIPEDA Schedule 1 Principle 4.1.3, an organization is accountable for personal information "
                    "in its possession or custody, including information that has been transferred to a third party "
                    "for processing, and must use contractual or other means to provide a comparable level of "
                    "protection while the information is being processed by a third party."
                ),
                "legal_requirement": (
                    "Maintain accountability for personal information transferred to third-party processors and "
                    "enforce contractual or technical safeguards providing a comparable level of protection "
                    "(PIPEDA Schedule 1, Principle 4.1.3)."
                ),
                "applicability_conditions": [
                    "Organization subject to PIPEDA in the course of commercial activity",
                    "Transfer of personal information to a domestic or cross-border third-party processor",
                ],
                "exemptions": [],
                "base_thresholds": {},
                "default_deadline": "Prior to transferring personal information to a third-party processor",
                "affected_organization_types": ["commercial_organization", "data_controller", "third_party_processor"],
                "affected_industries": ["all_canadian_commercial_sectors", "cloud_computing", "technology", "financial_services"],
                "affected_data_categories": ["personal_information"],
                "affected_processing_activities": ["third_party_data_processing", "cross_border_data_transfer", "vendor_contract_management"],
                "required_controls": ["CTRL-PIPEDA-COMPARABLE-PROTECTION-DPA", "CTRL-VENDOR-PRIVACY-SECURITY-AUDIT"],
                "required_assessments": ["ASSESS-THIRD-PARTY-PROCESSOR-SAFEGUARDS-REVIEW"],
                "related_regulations": ["PIPEDA (S.C. 2000, c. 5)", "PIPEDA Schedule 1 Principle 4.1.3", "PIPEDA Principle 4.7"],
                "is_ambiguous": False,
            }

        # Profile 6: Right to Delete / Erasure (CCPA § 1798.105, GDPR Art. 17, etc.)
        if (
            "1798.105" in sec_lower
            or "right to request that a business delete" in text_lower
            or "delete any personal information about the consumer" in text_lower
            or "right to erasure" in text_lower
            or "recht auf löschung" in text_lower
            or "droit à l'effacement" in text_lower
        ):
            return {
                "annotation_type": "statutory_obligation",
                "normalized_legal_concept": "consumer_right_to_deletion_and_erasure",
                "plain_language_explanation": (
                    "Organizations must honor verified consumer/data subject requests to delete personal information "
                    "collected from or about them, and must notify service providers, contractors, and third parties "
                    "to delete the personal information unless a statutory exemption applies."
                ),
                "legal_requirement": (
                    "Delete consumer personal information upon verified request and propagate deletion instructions "
                    "to service providers, contractors, and third parties within the statutory response timeframe."
                ),
                "applicability_conditions": [
                    "Receipt of a verifiable consumer or data subject deletion/erasure request",
                ],
                "exemptions": [
                    "Retention necessary to complete transaction, detect security incidents, debug, exercise free speech, or comply with a legal obligation",
                ],
                "base_thresholds": {"response_deadline_days": 45 if jur.startswith("US-") else 30},
                "default_deadline": "Within 45 calendar days of receiving a verifiable consumer request" if jur.startswith("US-") else "Without undue delay and within 30 days",
                "affected_organization_types": ["business", "data_controller", "service_provider", "processor"],
                "affected_industries": ["technology", "retail", "e_commerce", "financial_services", "healthcare"],
                "affected_data_categories": ["personal_information", "personal_data"],
                "affected_processing_activities": ["dsar_deletion_fulfillment", "downstream_processor_deletion_propagation", "data_retention_and_purging"],
                "required_controls": ["CTRL-DSAR-VERIFIED-DELETION-WORKFLOW", "CTRL-DOWNSTREAM-VENDOR-DELETION-PROPAGATION"],
                "required_assessments": ["ASSESS-DELETION-EXEMPTION-LEGAL-HOLD-CHECK"],
                "related_regulations": ["Cal. Civ. Code § 1798.105", "GDPR Art. 17"],
                "is_ambiguous": False,
            }

        # Profile 7: Generic deterministic fallback grounded in explicit obligation/prohibition/definition markers
        has_obligation = any(
            kw in text_lower
            for kw in (
                "shall",
                "must",
                "required to",
                "doit",
                "doivent",
                "est tenu",
                "sont tenus",
                "hat ",
                "haben ",
                "verpflichtet",
                "benennen",
                "muss",
                "müssen",
            )
        )
        has_prohibition = any(
            kw in text_lower
            for kw in (
                "shall not",
                "must not",
                "may not",
                "prohibited",
                "ne peut",
                "ne peuvent",
                "interdit",
                "darf nicht",
                "dürfen nicht",
                "unzulässig",
            )
        )
        has_definition = any(
            kw in text_lower
            for kw in (
                "means",
                "is defined as",
                "for the purposes of this",
                "on entend par",
                "désigne",
                "im sinne dieses",
                "bezeichnet",
            )
        )

        if has_prohibition and not has_obligation:
            default_type = "prohibition"
            concept = f"statutory_prohibition_{jur.lower().replace('-', '_')}"
        elif has_definition and not has_obligation:
            default_type = "definition"
            concept = f"statutory_definition_{jur.lower().replace('-', '_')}"
        else:
            default_type = "statutory_obligation"
            concept = f"statutory_obligation_{jur.lower().replace('-', '_')}"

        first_sentence = excerpt.split(".")[0].strip() if "." in excerpt else excerpt[:240].strip()
        return {
            "annotation_type": default_type,
            "normalized_legal_concept": concept,
            "plain_language_explanation": f"Provision {sec_lower} in {doc.canonical_title} ({jur}): {first_sentence}.",
            "legal_requirement": f"Comply with statutory provision {sec_lower} of {doc.canonical_title}: {first_sentence}.",
            "applicability_conditions": [f"Subject to jurisdiction {jur} and scope of {doc.canonical_title}"],
            "exemptions": [],
            "base_thresholds": {},
            "default_deadline": None,
            "affected_organization_types": ["regulated_entity", "data_controller", "data_processor"],
            "affected_industries": ["cross_sector"],
            "affected_data_categories": ["personal_data"],
            "affected_processing_activities": ["personal_data_processing"],
            "required_controls": ["CTRL-STATUTORY-COMPLIANCE-VERIFICATION"],
            "required_assessments": ["ASSESS-REGULATORY-APPLICABILITY-REVIEW"],
            "related_regulations": [doc.official_citation] if doc.official_citation else [sec_lower],
            "is_ambiguous": not (has_obligation or has_prohibition or has_definition),
        }

    def _extract_thresholds(
        self,
        excerpt: str,
        text_lower: str,
        lang: str,
        base_thresholds: Dict[str, Any],
    ) -> Dict[str, Any]:
        thresholds: Dict[str, Any] = dict(base_thresholds)

        # 1. German/English/French employee/person headcount thresholds (e.g., "zwanzig Personen" or "20 persons/employees")
        if re.search(r"\b(?:zwanzig|20)\s+personen\b", text_lower):
            thresholds["min_persons_automated_processing"] = 20
        emp_match = re.search(
            r"\b(?:at least|more than|fewer than|mindestens|au moins)\s+(\d[\d,\.]*)\s+(?:employees|persons|beschäftigte|personen|employés|personnes)\b",
            text_lower,
        )
        if emp_match:
            val_str = emp_match.group(1).replace(",", "").replace(".", "")
            if val_str.isdigit():
                thresholds["person_or_employee_headcount_threshold"] = int(val_str)

        # 2. Calendar/business day deadlines as numeric threshold
        day_match = re.search(
            r"\b(\d{1,3})\s+(?:calendar\s+days|business\s+days|days|jours|tage|tagen|kalendertage)\b",
            text_lower,
        )
        if day_match:
            days_val = int(day_match.group(1))
            thresholds.setdefault("statutory_timeframe_days", days_val)

        # 3. Consumer/household count threshold (e.g. "100,000 or more consumers or households")
        cons_match = re.search(
            r"\b(\d{1,3}(?:,\d{3})+)\s+(?:or\s+more\s+)?(?:consumers|households|individuals|data\s+subjects)\b",
            text_lower,
        )
        if cons_match:
            thresholds["min_consumers_or_households"] = int(cons_match.group(1).replace(",", ""))

        # 4. Revenue dollar threshold (e.g. "$25,000,000" or "twenty-five million dollars ($25,000,000)")
        rev_match = re.search(r"\$\s*(\d{1,3}(?:,\d{3})+)", excerpt)
        if rev_match:
            thresholds["gross_annual_revenue_usd"] = int(rev_match.group(1).replace(",", ""))

        return thresholds

    def _extract_statutory_deadline(
        self,
        excerpt: str,
        text_lower: str,
        lang: str,
        default_deadline: Optional[str],
    ) -> Optional[str]:
        # Explicit statutory deadline patterns across EN / FR / DE
        en_patterns = [
            re.compile(
                r"(without\s+unreasonable\s+delay\s+and\s+in\s+no\s+case\s+later\s+than\s+\d+\s+calendar\s+days\s+after\s+discovery\s+of\s+a\s+breach)",
                re.IGNORECASE,
            ),
            re.compile(
                r"(no\s+later\s+than\s+\d+\s+(?:calendar\s+|business\s+)?days\s+after\s+[a-z\s]+)",
                re.IGNORECASE,
            ),
            re.compile(
                r"(within\s+\d+\s+(?:calendar\s+|business\s+|working\s+)?(?:days|hours|months)\s+(?:of|after)\s+[a-z\s]+)",
                re.IGNORECASE,
            ),
            re.compile(r"(at\s+or\s+before\s+the\s+point\s+of\s+collection)", re.IGNORECASE),
            re.compile(r"(without\s+undue\s+delay(?:\s+and\s+in\s+any\s+event\s+within\s+\d+\s+(?:days|hours|months))?)", re.IGNORECASE),
        ]
        fr_patterns = [
            re.compile(r"(avant\s+de\s+communiquer\s+à\s+l'extérieur\s+du\s+québec\s+un\s+renseignement\s+personnel)", re.IGNORECASE),
            re.compile(r"(dans\s+les\s+\d+\s+jours\s+[a-zéèêàâîôûç\s]+)", re.IGNORECASE),
            re.compile(r"(avec\s+diligence|dans\s+les\s+meilleurs\s+délais)", re.IGNORECASE),
        ]
        de_patterns = [
            re.compile(r"(unverzüglich(?:\s+und\s+möglichst\s+binnen\s+\d+\s+(?:stunden|tagen))?)", re.IGNORECASE),
            re.compile(r"(innerhalb\s+von\s+\d+\s+(?:tagen|stunden|monaten))", re.IGNORECASE),
        ]

        for pat in en_patterns + fr_patterns + de_patterns:
            m = pat.search(excerpt)
            if m:
                return m.group(1).strip()

        return default_deadline

    def _extract_exemptions(
        self,
        excerpt: str,
        text_lower: str,
        lang: str,
        base_exemptions: List[str],
    ) -> List[str]:
        exemptions = list(base_exemptions)
        exemption_clauses = [
            (r"\b(except\s+as\s+provided\s+in\s+[^\.,;]+)", "en"),
            (r"\b(unless\s+[^\.,;]{10,120})", "en"),
            (r"\b(sauf\s+[^\.,;]{10,120})", "fr"),
            (r"\b(à\s+moins\s+que\s+[^\.,;]{10,120})", "fr"),
            (r"\b(soweit\s+nicht\s+[^\.,;]{10,120})", "de"),
            (r"\b(ausgenommen\s+[^\.,;]{10,120})", "de"),
        ]
        for pattern_str, _ in exemption_clauses:
            for match in re.finditer(pattern_str, excerpt, flags=re.IGNORECASE):
                clause = match.group(1).strip()
                if clause and clause not in exemptions:
                    exemptions.append(clause)
        return exemptions

    def _extract_applicability_conditions(
        self,
        excerpt: str,
        text_lower: str,
        lang: str,
        jur: str,
        base_conditions: List[str],
    ) -> List[str]:
        conditions = list(base_conditions)
        cond_patterns = [
            r"\b(soweit\s+sie\s+in\s+der\s+regel\s+mindestens\s+[^\.,;]+)",
            r"\b(nehmen\s+der\s+verantwortliche\s+oder\s+der\s+auftragsverarbeiter\s+[^\.,;]+)",
            r"\b(avant\s+de\s+communiquer\s+à\s+l'extérieur\s+du\s+québec\s+[^\.,;]+)",
            r"\b(following\s+ the\s+discovery\s+of\s+a\s+breach\s+of\s+[^\.,;]+)",
            r"\b(following\s+the\s+discovery\s+of\s+a\s+breach\s+of\s+[^\.,;]+)",
            r"\b(a\s+business\s+that\s+controls\s+the\s+collection\s+of\s+[^\.,;]+)",
        ]
        for pat_str in cond_patterns:
            m = re.search(pat_str, excerpt, flags=re.IGNORECASE)
            if m:
                clause = m.group(1).strip()
                if clause and not any(clause.lower() in c.lower() for c in conditions):
                    conditions.append(clause)
        return conditions

    def _determine_annotation_type(
        self,
        text_lower: str,
        lang: str,
        has_thresholds: bool,
        has_deadline: bool,
        has_exemptions: bool,
        default_type: str,
    ) -> str:
        # Allowed values in Section 6.2:
        # statutory_obligation, prohibition, exemption, threshold, deadline, definition, judicial_holding, judicial_dicta, remedy_order
        if default_type in (
            "statutory_obligation",
            "prohibition",
            "exemption",
            "threshold",
            "deadline",
            "definition",
        ):
            return default_type
        if has_thresholds:
            return "threshold"
        if has_deadline:
            return "deadline"
        if has_exemptions:
            return "exemption"
        return "statutory_obligation"

    def _resolve_regulatory_authority(
        self,
        doc: CanonicalLegalDocument,
        jur: str,
        text_lower: str,
    ) -> str:
        if doc.issuing_authority and doc.issuing_authority.strip():
            # If the document specifies a legislature, pair it with the enforcing privacy/data protection regulator
            if doc.issuing_authority_type in ("data_protection_authority", "sector_regulator", "attorney_general"):
                return doc.issuing_authority.strip()
            default_reg = DEFAULT_REGULATORY_AUTHORITY_BY_JURISDICTION.get(jur)
            if default_reg and default_reg.lower() not in doc.issuing_authority.lower():
                return f"{default_reg} (Enacted/Issued by {doc.issuing_authority.strip()})"
            return doc.issuing_authority.strip()

        return DEFAULT_REGULATORY_AUTHORITY_BY_JURISDICTION.get(
            jur, f"Competent Data Protection / Privacy Authority ({jur})"
        )

    @staticmethod
    def _has_unresolved_ambiguity(excerpt: str, text_lower: str, lang: str) -> bool:
        """
        Flags provisions that contain explicit editorial placeholders, bracketed draft text,
        or truncated/incomplete references requiring human counsel review.
        """
        if len(excerpt.strip()) < 20:
            return True
        ambiguity_markers = (
            "[reserved]",
            "[tbd]",
            "[insert",
            "unverified translation",
            "traduction non vérifiée",
            "unbestätigte übersetzung",
        )
        return any(marker in text_lower for marker in ambiguity_markers)
