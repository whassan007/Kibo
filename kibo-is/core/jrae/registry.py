"""
KIBO Privacy OS — Global Jurisdiction Registry
Covers:
- United States: Federal (US-FED), all 50 States (US-AL .. US-WY), Washington DC (US-DC), and key territories (US-PR, US-GU, US-VI)
- Canada: Federal (CA-FED), all 10 Provinces (CA-AB .. CA-SK), and all 3 Territories (CA-NT, CA-NU, CA-YT)
- European Union: EU-Wide (EU) and all 27 Member States (EU-AT .. EU-SE), with subnational authorities (e.g. Germany Länder)
- Expansion Jurisdictions (marked non-EU): UK (GB), EEA non-EU (NO, IS, LI), Switzerland (CH)
"""

from typing import Dict, List, Optional
from core.jrae.schemas import JurisdictionEntry, JurisdictionType

# ---------------------------------------------------------------------------
# 1. UNITED STATES: FEDERAL + 50 STATES + DC + TERRITORIES
# ---------------------------------------------------------------------------

US_STATES_METADATA = [
    ("US-AL", "Alabama", False, "Office of the Alabama Attorney General", "https://www.alabamaag.gov"),
    ("US-AK", "Alaska", False, "Alaska Department of Law (Attorney General)", "https://law.alaska.gov"),
    ("US-AZ", "Arizona", False, "Arizona Attorney General's Office", "https://www.azag.gov"),
    ("US-AR", "Arkansas", False, "Arkansas Attorney General", "https://arkansasag.gov"),
    ("US-CA", "California", True, "California Privacy Protection Agency (CalPrivacy) & California Attorney General", "https://cppa.ca.gov"),
    ("US-CO", "Colorado", True, "Colorado Attorney General", "https://coag.gov"),
    ("US-CT", "Connecticut", True, "Connecticut Office of the Attorney General", "https://portal.ct.gov/AG"),
    ("US-DE", "Delaware", True, "Delaware Department of Justice (Consumer Protection Unit)", "https://attorneygeneral.delaware.gov"),
    ("US-DC", "District of Columbia", False, "Office of the Attorney General for the District of Columbia", "https://oag.dc.gov"),
    ("US-FL", "Florida", True, "Florida Department of Legal Affairs (Attorney General)", "https://www.myfloridalegal.com"),
    ("US-GA", "Georgia", False, "Office of the Attorney General of Georgia", "https://law.georgia.gov"),
    ("US-HI", "Hawaii", False, "Department of the Attorney General, State of Hawaii", "https://ag.hawaii.gov"),
    ("US-ID", "Idaho", False, "Office of the Attorney General of Idaho", "https://www.ag.idaho.gov"),
    ("US-IL", "Illinois", False, "Illinois Attorney General", "https://illinoisattorneygeneral.gov"),
    ("US-IN", "Indiana", True, "Indiana Office of the Attorney General", "https://www.in.gov/attorneygeneral"),
    ("US-IA", "Iowa", True, "Office of the Attorney General of Iowa", "https://www.iowaattorneygeneral.gov"),
    ("US-KS", "Kansas", False, "Kansas Attorney General", "https://ag.ks.gov"),
    ("US-KY", "Kentucky", True, "Kentucky Office of the Attorney General", "https://www.ag.ky.gov"),
    ("US-LA", "Louisiana", False, "Louisiana Department of Justice (Attorney General)", "https://www.ag.state.la.us"),
    ("US-ME", "Maine", False, "Office of the Maine Attorney General", "https://www.maine.gov/ag"),
    ("US-MD", "Maryland", True, "Maryland Office of the Attorney General", "https://www.marylandattorneygeneral.gov"),
    ("US-MA", "Massachusetts", False, "Massachusetts Office of the Attorney General", "https://www.mass.gov/orgs/office-of-attorney-general-andrea-joy-campbell"),
    ("US-MI", "Michigan", False, "Michigan Department of Attorney General", "https://www.michigan.gov/ag"),
    ("US-MN", "Minnesota", True, "Office of the Minnesota Attorney General", "https://www.ag.state.mn.us"),
    ("US-MS", "Mississippi", False, "Office of the Attorney General, State of Mississippi", "https://www.ago.state.ms.us"),
    ("US-MO", "Missouri", False, "Missouri Attorney General's Office", "https://ago.mo.gov"),
    ("US-MT", "Montana", True, "Montana Department of Justice (Office of Consumer Protection)", "https://dojmt.gov"),
    ("US-NE", "Nebraska", True, "Nebraska Attorney General's Office", "https://ago.nebraska.gov"),
    ("US-NV", "Nevada", False, "Nevada Office of the Attorney General", "https://ag.nv.gov"),
    ("US-NH", "New Hampshire", True, "New Hampshire Department of Justice (Attorney General)", "https://www.doj.nh.gov"),
    ("US-NJ", "New Jersey", True, "New Jersey Office of the Attorney General (Division of Consumer Affairs)", "https://www.njoag.gov"),
    ("US-NM", "New Mexico", False, "New Mexico Department of Justice", "https://nmdoj.gov"),
    ("US-NY", "New York", False, "New York State Office of the Attorney General & NYDFS", "https://ag.ny.gov"),
    ("US-NC", "North Carolina", False, "North Carolina Department of Justice", "https://ncdoj.gov"),
    ("US-ND", "North Dakota", False, "North Dakota Office of Attorney General", "https://attorneygeneral.nd.gov"),
    ("US-OH", "Ohio", False, "Ohio Attorney General", "https://www.ohioattorneygeneral.gov"),
    ("US-OK", "Oklahoma", False, "Oklahoma Office of the Attorney General", "https://oklahoma.gov/oag.html"),
    ("US-OR", "Oregon", True, "Oregon Department of Justice (Attorney General)", "https://www.doj.state.or.us"),
    ("US-PA", "Pennsylvania", False, "Pennsylvania Office of Attorney General", "https://www.attorneygeneral.gov"),
    ("US-RI", "Rhode Island", True, "Rhode Island Office of the Attorney General", "https://riag.ri.gov"),
    ("US-SC", "South Carolina", False, "South Carolina Department of Consumer Affairs & Attorney General", "https://www.scag.gov"),
    ("US-SD", "South Dakota", False, "South Dakota Office of Attorney General", "https://atg.sd.gov"),
    ("US-TN", "Tennessee", True, "Tennessee Office of the Attorney General and Reporter", "https://www.tn.gov/attorneygeneral"),
    ("US-TX", "Texas", True, "Texas Office of the Attorney General", "https://www.texasattorneygeneral.gov"),
    ("US-UT", "Utah", True, "Utah Office of the Attorney General & Division of Consumer Protection", "https://attorneygeneral.utah.gov"),
    ("US-VT", "Vermont", False, "Vermont Office of the Attorney General", "https://ago.vermont.gov"),
    ("US-VA", "Virginia", True, "Office of the Attorney General of Virginia", "https://www.oag.state.va.us"),
    ("US-WA", "Washington", False, "Washington State Office of the Attorney General", "https://www.atg.wa.gov"),
    ("US-WV", "West Virginia", False, "West Virginia Office of the Attorney General", "https://ago.wv.gov"),
    ("US-WI", "Wisconsin", False, "Wisconsin Department of Justice", "https://www.doj.state.wi.us"),
    ("US-WY", "Wyoming", False, "Wyoming Office of the Attorney General", "https://ag.wyo.gov"),
]

US_TERRITORIES_METADATA = [
    ("US-PR", "Puerto Rico", False, "Puerto Rico Department of Consumer Affairs (DACO) & Dept. of Justice", "https://www.daco.pr.gov"),
    ("US-GU", "Guam", False, "Office of the Attorney General of Guam", "https://oagguam.org"),
    ("US-VI", "U.S. Virgin Islands", False, "U.S. Virgin Islands Department of Justice", "https://usvidoj.com"),
]

# ---------------------------------------------------------------------------
# 2. CANADA: FEDERAL + 10 PROVINCES + 3 TERRITORIES
# ---------------------------------------------------------------------------

CANADA_PROVINCES_TERRITORIES = [
    ("CA-AB", "Alberta", JurisdictionType.PROVINCE, True, "Office of the Information and Privacy Commissioner of Alberta (OIPC-AB)", "https://oipc.ab.ca"),
    ("CA-BC", "British Columbia", JurisdictionType.PROVINCE, True, "Office of the Information and Privacy Commissioner for British Columbia (OIPC-BC)", "https://www.oipc.bc.ca"),
    ("CA-MB", "Manitoba", JurisdictionType.PROVINCE, False, "Manitoba Ombudsman", "https://www.ombudsman.mb.ca"),
    ("CA-NB", "New Brunswick", JurisdictionType.PROVINCE, False, "Office of the Ombud for New Brunswick", "https://www.ombudnb.ca"),
    ("CA-NL", "Newfoundland and Labrador", JurisdictionType.PROVINCE, False, "Office of the Information and Privacy Commissioner of Newfoundland and Labrador", "https://www.oipc.nl.ca"),
    ("CA-NS", "Nova Scotia", JurisdictionType.PROVINCE, False, "Information and Privacy Commissioner for Nova Scotia", "https://oipc.novascotia.ca"),
    ("CA-ON", "Ontario", JurisdictionType.PROVINCE, False, "Information and Privacy Commissioner of Ontario (IPC)", "https://www.ipc.on.ca"),
    ("CA-PE", "Prince Edward Island", JurisdictionType.PROVINCE, False, "Information and Privacy Commissioner of Prince Edward Island", "https://www.assembly.pe.ca/oipc"),
    ("CA-QC", "Quebec", JurisdictionType.PROVINCE, True, "Commission d'accès à l'information du Québec (CAI)", "https://www.cai.gouv.qc.ca"),
    ("CA-SK", "Saskatchewan", JurisdictionType.PROVINCE, False, "Office of the Saskatchewan Information and Privacy Commissioner", "https://oipc.sk.ca"),
    ("CA-NT", "Northwest Territories", JurisdictionType.TERRITORY, False, "Information and Privacy Commissioner of the Northwest Territories", "https://atipp-nt.ca"),
    ("CA-NU", "Nunavut", JurisdictionType.TERRITORY, False, "Information and Privacy Commissioner of Nunavut", "https://atipp-nu.ca"),
    ("CA-YT", "Yukon", JurisdictionType.TERRITORY, False, "Yukon Information and Privacy Commissioner (Ombudsman)", "https://yukonombudsman.ca"),
]

# ---------------------------------------------------------------------------
# 3. EUROPEAN UNION: EU-WIDE + 27 MEMBER STATES (+ German Länder authorities)
# ---------------------------------------------------------------------------

GERMAN_LANDER_AUTHORITIES = [
    {"code": "DE-BW", "region": "Baden-Württemberg", "authority": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg (LfDI BW)"},
    {"code": "DE-BY-PRIV", "region": "Bavaria (Private Sector)", "authority": "Bayerisches Landesamt für Datenschutzaufsicht (BayLDA)"},
    {"code": "DE-BY-PUB", "region": "Bavaria (Public Sector)", "authority": "Der Bayerische Landesbeauftragte für den Datenschutz (BayLfD)"},
    {"code": "DE-BE", "region": "Berlin", "authority": "Berliner Beauftragte für Datenschutz und Informationsfreiheit (BlnBDI)"},
    {"code": "DE-BB", "region": "Brandenburg", "authority": "Die Landesbeauftragte für den Datenschutz und für das Recht auf Akteneinsicht Brandenburg (LDA BB)"},
    {"code": "DE-HB", "region": "Bremen", "authority": "Die Landesbeauftragte für Datenschutz und Informationsfreiheit der Freien Hansestadt Bremen"},
    {"code": "DE-HH", "region": "Hamburg", "authority": "Der Hamburgische Beauftragte für Datenschutz und Informationsfreiheit (HmbBfDI)"},
    {"code": "DE-HE", "region": "Hesse", "authority": "Der Hessische Beauftragte für Datenschutz und Informationsfreiheit (HBDI)"},
    {"code": "DE-MV", "region": "Mecklenburg-Western Pomerania", "authority": "Der Landesbeauftragte für Datenschutz und Informationsfreiheit Mecklenburg-Vorpommern"},
    {"code": "DE-NI", "region": "Lower Saxony", "authority": "Die Landesbeauftragte für den Datenschutz Niedersachsen (LfD NI)"},
    {"code": "DE-NW", "region": "North Rhine-Westphalia", "authority": "Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen (LDI NRW)"},
    {"code": "DE-RP", "region": "Rhineland-Palatinate", "authority": "Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Rheinland-Pfalz"},
    {"code": "DE-SL", "region": "Saarland", "authority": "Unabhängiges Datenschutzzentrum Saarland"},
    {"code": "DE-SN", "region": "Saxony", "authority": "Sächsischer Datenschutz- und Transparenzbeauftragter"},
    {"code": "DE-ST", "region": "Saxony-Anhalt", "authority": "Landesbeauftragter für den Datenschutz Sachsen-Anhalt"},
    {"code": "DE-SH", "region": "Schleswig-Holstein", "authority": "Unabhängiges Landeszentrum für Datenschutz Schleswig-Holstein (ULD)"},
    {"code": "DE-TH", "region": "Thuringia", "authority": "Thüringer Landesbeauftragter für den Datenschutz und die Informationsfreiheit (TLfDI)"},
]

EU_MEMBER_STATES = [
    ("EU-AT", "Austria", "AT", "Österreichische Datenschutzbehörde (DSB)", "https://www.dsb.gv.at", []),
    ("EU-BE", "Belgium", "BE", "Autorité de protection des données / Gegevensbeschermingsautoriteit (APD/GBA)", "https://www.dataprotectionauthority.be", []),
    ("EU-BG", "Bulgaria", "BG", "Commission for Personal Data Protection (CPDP)", "https://www.cpdp.bg", []),
    ("EU-HR", "Croatia", "HR", "Croatian Personal Data Protection Agency (AZOP)", "https://azop.hr", []),
    ("EU-CY", "Cyprus", "CY", "Office of the Commissioner for Personal Data Protection", "https://www.dataprotection.gov.cy", []),
    ("EU-CZ", "Czechia", "CZ", "Office for Personal Data Protection (ÚOOÚ)", "https://www.uoou.cz", []),
    ("EU-DK", "Denmark", "DK", "Datatilsynet (Danish Data Protection Agency)", "https://www.datatilsynet.dk", []),
    ("EU-EE", "Estonia", "EE", "Estonian Data Protection Inspectorate (AKI)", "https://www.aki.ee", []),
    ("EU-FI", "Finland", "FI", "Office of the Data Protection Ombudsman (Tietosuojavaltuutetun toimisto)", "https://tietosuoja.fi", []),
    ("EU-FR", "France", "FR", "Commission Nationale de l'Informatique et des Libertés (CNIL)", "https://www.cnil.fr", []),
    ("EU-DE", "Germany", "DE", "Der Bundesbeauftragte für den Datenschutz und die Informationsfreiheit (BfDI) & 17 Länder Authorities", "https://www.bfdi.bund.de", GERMAN_LANDER_AUTHORITIES),
    ("EU-GR", "Greece", "GR", "Hellenic Data Protection Authority (HDPA)", "https://www.dpa.gr", []),
    ("EU-HU", "Hungary", "HU", "National Authority for Data Protection and Freedom of Information (NAIH)", "https://www.naih.hu", []),
    ("EU-IE", "Ireland", "IE", "Data Protection Commission (DPC)", "https://www.dataprotection.ie", []),
    ("EU-IT", "Italy", "IT", "Garante per la protezione dei dati personali (Garante)", "https://www.garanteprivacy.it", []),
    ("EU-LV", "Latvia", "LV", "Data State Inspectorate (DVI)", "https://www.dvi.gov.lv", []),
    ("EU-LT", "Lithuania", "LT", "State Data Protection Inspectorate (VDAI)", "https://vdai.lrv.lt", []),
    ("EU-LU", "Luxembourg", "LU", "Commission Nationale pour la Protection des Données (CNPD)", "https://cnpd.public.lu", []),
    ("EU-MT", "Malta", "MT", "Office of the Information and Data Protection Commissioner (IDPC)", "https://idpc.org.mt", []),
    ("EU-NL", "Netherlands", "NL", "Autoriteit Persoonsgegevens (AP)", "https://autoriteitpersoonsgegevens.nl", []),
    ("EU-PL", "Poland", "PL", "Personal Data Protection Office (UODO)", "https://uodo.gov.pl", []),
    ("EU-PT", "Portugal", "PT", "Comissão Nacional de Proteção de Dados (CNPD)", "https://www.cnpd.pt", []),
    ("EU-RO", "Romania", "RO", "National Supervisory Authority for Personal Data Processing (ANSPDCP)", "https://www.dataprotection.ro", []),
    ("EU-SK", "Slovakia", "SK", "Office for Personal Data Protection of the Slovak Republic (ÚOOÚ SR)", "https://dataprotection.gov.sk", []),
    ("EU-SI", "Slovenia", "SI", "Information Commissioner of the Republic of Slovenia (IP RS)", "https://www.ip-rs.si", []),
    ("EU-ES", "Spain", "ES", "Agencia Española de Protección de Datos (AEPD)", "https://www.aepd.es", [
        {"code": "ES-CT", "region": "Catalonia (Public Sector)", "authority": "Autoritat Catalana de Protecció de Dades (APDCAT)"},
        {"code": "ES-PV", "region": "Basque Country (Public Sector)", "authority": "Datuak Babesteko Euskal Bulegoa (AVPD)"},
        {"code": "ES-AN", "region": "Andalusia (Public Sector)", "authority": "Consejo de Transparencia y Protección de Datos de Andalucía"},
    ]),
    ("EU-SE", "Sweden", "SE", "Integritetsskyddsmyndigheten (IMY)", "https://www.imy.se", []),
]


def build_jurisdiction_registry() -> Dict[str, JurisdictionEntry]:
    registry: Dict[str, JurisdictionEntry] = {}

    # 1. US Federal
    registry["US-FED"] = JurisdictionEntry(
        jurisdiction_id="US-FED",
        name="United States (Federal)",
        jurisdiction_type=JurisdictionType.FEDERAL,
        country="US",
        primary_regulator="Federal Trade Commission (FTC), HHS Office for Civil Rights (OCR), CFPB, SEC, OCC, Dept. of Education",
        regulator_url="https://www.ftc.gov",
        has_comprehensive_privacy_law=False,
    )

    # 2. US 50 States + DC
    for code, name, has_comp, reg, url in US_STATES_METADATA:
        registry[code] = JurisdictionEntry(
            jurisdiction_id=code,
            name=f"United States — {name}",
            jurisdiction_type=JurisdictionType.STATE,
            country="US",
            state_or_province=name,
            parent_jurisdiction_id="US-FED",
            primary_regulator=reg,
            regulator_url=url,
            has_comprehensive_privacy_law=has_comp,
        )

    # 3. US Territories
    for code, name, has_comp, reg, url in US_TERRITORIES_METADATA:
        registry[code] = JurisdictionEntry(
            jurisdiction_id=code,
            name=f"United States Territory — {name}",
            jurisdiction_type=JurisdictionType.TERRITORY,
            country="US",
            state_or_province=name,
            parent_jurisdiction_id="US-FED",
            primary_regulator=reg,
            regulator_url=url,
            has_comprehensive_privacy_law=has_comp,
        )

    # 4. Canada Federal
    registry["CA-FED"] = JurisdictionEntry(
        jurisdiction_id="CA-FED",
        name="Canada (Federal)",
        jurisdiction_type=JurisdictionType.FEDERAL,
        country="CA",
        primary_regulator="Office of the Privacy Commissioner of Canada (OPC) & CRTC / OSFI",
        regulator_url="https://www.priv.gc.ca",
        has_comprehensive_privacy_law=True,
    )

    # 5. Canada 10 Provinces + 3 Territories
    for code, name, jtype, has_priv_comp, reg, url in CANADA_PROVINCES_TERRITORIES:
        registry[code] = JurisdictionEntry(
            jurisdiction_id=code,
            name=f"Canada — {name}",
            jurisdiction_type=jtype,
            country="CA",
            state_or_province=name,
            parent_jurisdiction_id="CA-FED",
            primary_regulator=reg,
            regulator_url=url,
            has_comprehensive_privacy_law=has_priv_comp,
        )

    # 6. European Union (Supranational)
    registry["EU"] = JurisdictionEntry(
        jurisdiction_id="EU",
        name="European Union (EU-Wide)",
        jurisdiction_type=JurisdictionType.SUPRANATIONAL,
        country="EU",
        primary_regulator="European Data Protection Board (EDPB), European Data Protection Supervisor (EDPS) & European AI Office",
        regulator_url="https://www.edpb.europa.eu",
        has_comprehensive_privacy_law=True,
    )

    # 7. All 27 EU Member States
    for code, name, iso2, reg, url, sub_auths in EU_MEMBER_STATES:
        registry[code] = JurisdictionEntry(
            jurisdiction_id=code,
            name=f"European Union — {name}",
            jurisdiction_type=JurisdictionType.MEMBER_STATE,
            country=iso2,
            member_state=name,
            parent_jurisdiction_id="EU",
            primary_regulator=reg,
            regulator_url=url,
            subnational_authorities=sub_auths,
            has_comprehensive_privacy_law=True,
        )

    # 8. Optional Non-EU Expansion Jurisdictions (explicitly separated per Section 6.3)
    for code, name, iso2, reg, url in [
        ("GB", "United Kingdom (Non-EU Expansion)", "GB", "Information Commissioner's Office (ICO)", "https://ico.org.uk"),
        ("NO", "Norway (EEA Non-EU Expansion)", "NO", "Datatilsynet (Norwegian Data Protection Authority)", "https://www.datatilsynet.no"),
        ("IS", "Iceland (EEA Non-EU Expansion)", "IS", "Persónuvernd", "https://www.personuvernd.is"),
        ("LI", "Liechtenstein (EEA Non-EU Expansion)", "LI", "Datenschutzstelle (DSS)", "https://www.datenschutzstelle.li"),
        ("CH", "Switzerland (Non-EU Adequacy Expansion)", "CH", "Federal Data Protection and Information Commissioner (FDPIC)", "https://www.edoeb.admin.ch"),
    ]:
        registry[code] = JurisdictionEntry(
            jurisdiction_id=code,
            name=name,
            jurisdiction_type=JurisdictionType.FEDERAL,
            country=iso2,
            primary_regulator=reg,
            regulator_url=url,
            has_comprehensive_privacy_law=True,
            catalogued=True,
            implemented=False,
            tested=False,
            legally_reviewed=False,
            production_enabled=False,
        )

    return registry


GLOBAL_JURISDICTION_REGISTRY: Dict[str, JurisdictionEntry] = build_jurisdiction_registry()

# Canonical aliases so inputs like "IE", "DE", "FR", "Ontario", "Quebec", "California" resolve cleanly
JURISDICTION_ALIASES: Dict[str, str] = {
    "US": "US-FED",
    "USA": "US-FED",
    "US_FEDERAL": "US-FED",
    "CA": "CA-FED",
    "CANADA": "CA-FED",
    "CA_FEDERAL": "CA-FED",
    "EU_UNION": "EU",
    "ONTARIO": "CA-ON",
    "QUEBEC": "CA-QC",
    "ALBERTA": "CA-AB",
    "BRITISH_COLUMBIA": "CA-BC",
    "CALIFORNIA": "US-CA",
    "COLORADO": "US-CO",
    "VIRGINIA": "US-VA",
    "CONNECTICUT": "US-CT",
    "TEXAS": "US-TX",
    "WASHINGTON": "US-WA",
    "NEW_YORK": "US-NY",
    "ILLINOIS": "US-IL",
}
for code, name, iso2, _, _, _ in EU_MEMBER_STATES:
    JURISDICTION_ALIASES[iso2] = code
    JURISDICTION_ALIASES[name.upper().replace(" ", "_")] = code


def normalize_jurisdiction_code(raw: str) -> str:
    if not raw:
        return ""
    cleaned = raw.strip().upper().replace(" ", "_")
    if cleaned in GLOBAL_JURISDICTION_REGISTRY:
        return cleaned
    if cleaned in JURISDICTION_ALIASES:
        return JURISDICTION_ALIASES[cleaned]
    cleaned_hyphen = cleaned.replace("_", "-")
    if cleaned_hyphen in GLOBAL_JURISDICTION_REGISTRY:
        return cleaned_hyphen
    return raw.strip()
