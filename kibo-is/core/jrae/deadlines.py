"""Deterministic planning clocks; qualitative duties never become invented timers.

Business-day clocks exclude weekends only. Local holidays and legally permitted
pauses require counsel validation. Outputs are plans, never dispatch authority.
"""
from calendar import monthrange
from datetime import datetime, timedelta
from typing import Any, Dict, List

from core.jrae.registry import GLOBAL_JURISDICTION_REGISTRY, normalize_jurisdiction_code


def _months(value: datetime, months: int) -> datetime:
    index = value.year * 12 + value.month - 1 + months
    year, month = divmod(index, 12)
    return value.replace(year=year, month=month + 1,
                         day=min(value.day, monthrange(year, month + 1)[1]))


def _business(value: datetime, days: int) -> datetime:
    while days:
        value += timedelta(days=1)
        if value.weekday() < 5:
            days -= 1
    return value


def _code(value: str) -> str:
    normalized = normalize_jurisdiction_code(value)
    if normalized in GLOBAL_JURISDICTION_REGISTRY:
        return normalized
    # A statute identifier may be supplied when a province has several clocks.
    for code in sorted(GLOBAL_JURISDICTION_REGISTRY, key=len, reverse=True):
        if value.upper().startswith(code + "-"):
            return code
    return normalized


def calculate_dsar_deadline(jurisdiction_id: str, request_type: str,
                            received_at: datetime,
                            is_complex_or_extended: bool = False) -> Dict[str, Any]:
    code = _code(jurisdiction_id)
    kind = request_type.lower().replace("-", "_")
    statute = jurisdiction_id.upper()
    days, extension, business, source = 0, 0, False, ""
    appeal = None
    acknowledgement = None
    notes = []
    if code == "EU" or code.startswith("EU-"):
        initial = _months(received_at, 1)
        final = _months(received_at, 3) if is_complex_or_extended else initial
        days, extension, source = 30, 60, "GDPR Art. 12(3)"
        notes.append("Calendar months control, not fixed 30/60-day approximations.")
    else:
        states = "CA VA CO CT TX OR MT DE NH NJ MN MD IN KY RI WA".split()
        if code in {"US-" + s for s in states}:
            days, extension, source = 45, 45, "State consumer privacy rights statute"
            appeal = {"US-VA": 60, "US-CO": 45, "US-CT": 60, "US-TX": 60}.get(code)
            if code == "US-CA":
                source = "CCPA/CPRA; Cal. Civ. Code 1798.130; 11 CCR 7021, 7026"
                acknowledgement = _business(received_at, 10)
                if kind in {"opt_out", "optout", "do_not_sell", "sale_sharing_opt_out"}:
                    days, extension, business = 15, 0, True
            if code == "US-TX" and ("HB300" in statute or "HB-300" in statute or kind in {"electronic_health_records", "ehr", "health_records"}):
                days, extension, business, source = 15, 0, True, "Texas Health & Safety Code 181.102"
            if code == "US-WA":
                source = "Washington My Health My Data Act"
        elif code.startswith("CA-"):
            days, extension, source = 30, 30, "PIPEDA s. 8(3)-(4)"
            if code == "CA-QC":
                extension, source, appeal = 0, "Quebec private-sector Act ss. 32, 43", 30
                notes.append("Written refusal with reasons and CAI review rights; CAI review clock runs from refusal, not receipt.")
            elif code == "CA-ON":
                source = "Ontario PHIPA ss. 54-55"
                if "FIPPA" in statute or kind in {"fippa", "mfippa"}:
                    extension, source = 0, "Ontario FIPPA/MFIPPA (extensions require separate statutory grounds)"
            elif code == "CA-AB":
                days, extension, source = 45, 0, "Alberta PIPA s. 28"
            elif code == "CA-BC":
                days, extension, business, source = 30, 0, True, "BC PIPA s. 29"
            elif code == "CA-NL":
                days, extension, business, source = 20, 0, True, "NL ATIPPA"
            elif code == "CA-MB":
                extension, source = 0, "Manitoba PHIA"
                if kind in {"inpatient", "inpatient_access", "hospital_inpatient"}:
                    days = 3
                    notes.append("72-hour inpatient access clock.")
        else:
            raise ValueError("No supported DSAR rule for " + jurisdiction_id)
        add = _business if business else lambda value, count: value + timedelta(days=count)
        initial = add(received_at, days)
        final = add(received_at, days + (extension if is_complex_or_extended else 0))
    return {
        "jurisdiction_id": code, "request_type": request_type, "received_at": received_at,
        "initial_deadline": initial, "response_deadline": final, "deadline": final,
        "initial_days": days, "extension_days": extension,
        "day_type": "calendar_months" if code.startswith("EU") else "business_days" if business else "calendar_days",
        "acknowledgement_deadline": acknowledgement,
        "extension_notification_deadline": initial if extension else None,
        "extension_applied": bool(is_complex_or_extended and extension),
        "appeal_days": appeal, "appeal_deadline": None,
        "appeal_clock_anchor": "refusal/appeal receipt; establish separately" if appeal else None,
        "statutory_source": source, "notes": notes,
        "business_day_calendar": "weekdays_only; holidays require validation" if business or acknowledgement else None,
        "requires_human_legal_approval": True,
    }


def calculate_breach_deadlines(jurisdictions: List[str], discovery_time: datetime,
                               affected_counts_by_jurisdiction: Dict[str, int],
                               involves_phi: bool = False, involves_financial: bool = False,
                               is_critical_infrastructure: bool = False,
                               risk_of_harm_level: str = "high") -> Dict[str, Any]:
    codes = sorted({_code(j) for j in jurisdictions})
    counts: Dict[str, int] = {}
    for key, value in affected_counts_by_jurisdiction.items():
        if value < 0:
            raise ValueError("Affected counts must be nonnegative")
        counts[_code(key)] = max(counts.get(_code(key), 0), value)
    notices: List[Dict[str, Any]] = []
    retention = []
    high = risk_of_harm_level.lower() in {"high", "serious", "significant", "rrosh", "critical"}

    def add(code, regime, recipient, authority, hours=None, text="", condition=None, due=None):
        notices.append(dict(jurisdiction_id=code, regulation_id=regime,
                            recipient_type=recipient, authority=authority,
                            deadline=due if due is not None else discovery_time + timedelta(hours=hours) if hours is not None else None,
                            deadline_hours=hours, deadline_days=hours / 24 if hours is not None else None,
                            timing_requirement=text, applicability_condition=condition,
                            clock_anchor="discovery_time (validate statutory awareness/determination trigger)",
                            requires_human_legal_approval=True))

    for code in codes:
        n = counts.get(code, 0)
        if code == "EU" or code.startswith("EU-"):
            authority = GLOBAL_JURISDICTION_REGISTRY[code].primary_regulator if code != "EU" else "Competent EU DPA"
            if risk_of_harm_level.lower() not in {"none", "unlikely", "no_risk"}:
                add(code, "EU-GDPR", "regulator", authority, 72, "Without undue delay; within 72 hours", "Unless unlikely to result in risk")
            if high:
                add(code, "EU-GDPR", "individual", "Affected individuals", text="Without undue delay", condition="High risk; Art. 34 exceptions require review")
            if is_critical_infrastructure:
                add(code, "EU-NIS2", "regulator", "Competent CSIRT/NIS authority", 24, "Early warning", "In-scope entity; significant incident")
                add(code, "EU-NIS2", "regulator", "Competent CSIRT/NIS authority", 72, "Incident notification", "In-scope entity; significant incident")
            if involves_financial:
                add(code, "EU-DORA", "regulator", "Competent financial authority", 24,
                    "Initial: within 4 hours of major classification, no later than 24 hours after awareness",
                    "DORA financial entity; major ICT incident; classification time must be supplied")
                add(code, "EU-DORA", "regulator", "Competent financial authority", text="Intermediate report within 72 hours of initial notification")
        elif code.startswith("CA-"):
            if code == "CA-FED":
                if high:
                    for recipient, authority in [("regulator", "OPC"), ("individual", "Affected individuals")]:
                        add(code, "CA-FED-PIPEDA", recipient, authority, text="As soon as feasible", condition="Real risk of significant harm")
                retention.append(dict(regulation_id="CA-FED-PIPEDA", months=24, description="Retain all breach records, including nonreportable incidents"))
                if involves_financial:
                    add(code, "CA-FED-OSFI-B13", "regulator", "OSFI", 24, "Within 24 hours or sooner", "Federally regulated financial institution; reportable incident")
            elif code == "CA-QC":
                if high:
                    for recipient, authority in [("regulator", "CAI"), ("individual", "Affected individuals")]:
                        add(code, "CA-QC-LAW25", recipient, authority, text="Promptly", condition="Risk of serious injury")
                retention.append(dict(regulation_id="CA-QC-LAW25", months=60, description="Confidentiality incident register"))
            elif code == "CA-ON" and involves_phi:
                for recipient, authority in [("regulator", "IPC Ontario"), ("individual", "Affected individuals")]:
                    add(code, "CA-ON-PHIPA", recipient, authority, text="At first reasonable opportunity", condition="IPC reporting prescribed circumstances must be assessed")
                annual = discovery_time.replace(year=discovery_time.year + 1, month=3, day=1)
                add(code, "CA-ON-PHIPA", "annual_report", "IPC Ontario", due=annual, text="Annual statistical report by March 1")
            elif code == "CA-AB" and high:
                add(code, "CA-AB-PIPA", "regulator", "OIPC-AB", text="Without unreasonable delay", condition="Real risk of significant harm")
        elif code.startswith("US-") and code != "US-FED":
            days, threshold = {"US-FL": (30, 500), "US-CO": (30, 500), "US-WA": (30, 500), "US-TX": (60, 250)}.get(code, (None, None))
            add(code, code + "-BREACH", "individual", "Affected individuals", days * 24 if days else None, "Without unreasonable delay" if days is None else "Without unreasonable delay; outer limit applies")
            if code == "US-CA" and n >= 500:
                add(code, "US-CA-BREACH", "attorney_general", "California AG", text="Without unreasonable delay; validate current statutory timing and >500 threshold", condition="Planning threshold >=500; statutory threshold/version requires legal review")
            elif threshold and n >= threshold:
                # Texas AG clock is independent and shorter than individual notice.
                ag_days = 30 if code == "US-TX" else days
                add(code, code + "-BREACH", "attorney_general", code + " AG", ag_days * 24)
            if code == "US-NY":
                for authority in ["NY Attorney General", "NY Department of State", "NYDFS"]:
                    add(code, "US-NY-SHIELD", "regulator", authority, text="Without unreasonable delay")
                if involves_financial:
                    add(code, "US-NY-NYDFS-500", "regulator", "NYDFS Superintendent", 72, condition="NYDFS covered entity; reportable cybersecurity incident")
    if any(c.startswith("US-") for c in codes):
        state_counts = [n for c, n in counts.items() if c.startswith("US-") and c != "US-FED"]
        total = counts.get("US-FED", sum(state_counts))
        if involves_phi:
            add("US-FED", "US-FED-HIPAA", "individual", "Affected individuals", 60 * 24, "Without unreasonable delay", "HIPAA covered entity/business associate; unsecured PHI")
            if total >= 500:
                add("US-FED", "US-FED-HIPAA", "regulator", "HHS OCR", 60 * 24)
            else:
                year_end = discovery_time.replace(month=12, day=31, hour=0, minute=0, second=0, microsecond=0)
                add("US-FED", "US-FED-HIPAA", "regulator", "HHS OCR", due=year_end + timedelta(days=60), text="Annual log within 60 days of calendar year end")
            for code, n in counts.items():
                if code.startswith("US-") and code != "US-FED" and n >= 500:
                    add(code, "US-FED-HIPAA", "media", "Prominent media in state/jurisdiction", 60 * 24, condition="Validate statutory more-than-500 resident media trigger")
        if involves_financial:
            if total >= 500:
                add("US-FED", "US-FED-GLBA-FTC", "regulator", "FTC", 30 * 24, condition="FTC Safeguards Rule covered institution; qualifying notification event")
            add("US-FED", "US-FED-BANK-INCIDENT", "regulator", "OCC/FDIC/FRB primary regulator", 36, condition="Banking organization; qualifying notification incident; determination trigger")
    tasks: Dict[Any, Dict[str, Any]] = {}
    for notice in notices:
        # Retain distinct recipients, clocks and report stages; merge identical actions only.
        key = (notice["jurisdiction_id"], notice["recipient_type"], notice["authority"], notice["deadline"], notice["timing_requirement"])
        if key not in tasks:
            tasks[key] = dict(notice, regulation_ids=[notice["regulation_id"]], action="Prepare for human legal approval; do not auto-dispatch")
        elif notice["regulation_id"] not in tasks[key]["regulation_ids"]:
            tasks[key]["regulation_ids"].append(notice["regulation_id"])
    regulator = [n["deadline_hours"] for n in notices if n["recipient_type"] in {"regulator", "attorney_general"} and n["deadline_hours"] is not None]
    individuals = [n["deadline_days"] for n in notices if n["recipient_type"] == "individual" and n["deadline_days"] is not None]
    workflow = list(tasks.values())
    if any(n["recipient_type"] == "individual" for n in notices):
        workflow.append({
            "action": "Coordinate a single legally approved individual notice per affected person across applicable regimes; retain all independent statutory constraints",
            "recipient_type": "individual_coordination", "regulation_ids": sorted({n["regulation_id"] for n in notices if n["recipient_type"] == "individual"}),
            "requires_human_legal_approval": True,
        })
    return dict(discovery_time=discovery_time, jurisdictions=codes,
                per_jurisdiction={c: [n for n in notices if n["jurisdiction_id"] == c] for c in sorted(set(codes) | {n["jurisdiction_id"] for n in notices})},
                notifications=notices, retention_requirements=retention,
                strictest_regulator_deadline_hours=min(regulator) if regulator else None,
                strictest_individual_deadline_days=min(individuals) if individuals else None,
                qualitative_deadlines_require_immediate_review=any(n["deadline"] is None for n in notices),
                deduplicated_workflow_tasks=workflow, requires_human_legal_approval=True)
