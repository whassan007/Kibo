# Regulatory Source Licensing, Attribution & Reuse Compliance (`Section 4.1`)

## 1. Licensing Governance Policy

KIBO Privacy OS ingests legislative, regulatory, supervisory, and judicial publications exclusively from official government, parliamentary, gazette, regulator, and court repositories (`262` curated sources across `113` jurisdictions). Every `RegulatorySourceEntry` in [`kibo-is/core/regulatory_intelligence/source_registry/`](file:///Users/wael/Code/iCloudCode/kibo.is/kibo-is/core/regulatory_intelligence/source_registry/__init__.py) carries explicit `licensing_and_reuse` terms and `auth_requirements`.

---

## 2. Jurisdictional Reuse Regimes

### 2.1 United States (Federal, 50 States, DC & Territories)
- **Federal Statutes, Regulations, Enforcement Actions & Federal Court Opinions (`17 U.S.C. § 105`)**:
  - Works of the United States Government (Congress.gov, GovInfo, eCFR, Federal Register, FTC, HHS OCR, CFPB, SEC, Supreme Court, and Federal Circuit Courts) are in the **public domain** under `17 U.S.C. § 105`.
- **State Statutes, Regulations & Judicial Decisions (Government Edicts Doctrine)**:
  - Under the U.S. Supreme Court's decision in *Georgia v. Public.Resource.Org, Inc.*, 590 U.S. 255 (2020), official statutory texts, legislative bills, administrative regulations, attorney general opinions, and judicial decisions authored by state lawmakers, regulators, and judges cannot be copyrighted under the Government Edicts Doctrine.
  - KIBO preserves canonical URLs and official citation attribution for all 50 states, DC, and US territories.

### 2.2 Canada (Federal, 10 Provinces & 3 Territories)
- **Federal Laws, Regulations, OPC Decisions & Federal/Supreme Court Judgments**:
  - Governed by the **Reproduction of Federal Law Order (SI/97-5)** and the **Open Government Licence – Canada**, which permit any person to reproduce federal enactments and consolidations of federal enactments, as well as decisions and reasons for decision of federally-constituted courts and administrative tribunals (including the Supreme Court of Canada, Federal Court of Appeal, and Office of the Privacy Commissioner of Canada), without charge or request for permission, provided due diligence is exercised in ensuring accuracy and the reproduction is not represented as an official version.
- **Provincial & Territorial Statutes and Commissioner Decisions**:
  - Governed by provincial King's Printer open reproduction policies (e.g., LégisQuébec / CAI Quebec open reproduction with attribution, Ontario e-Laws / IPC Ontario non-commercial & compliance reproduction with source attribution, BC Laws / King's Printer Licence, Alberta King's Printer open use).
  - For **CanLII** feeds (`canlii.org`), KIBO records `auth_requirements="api_key"` where API access is used and respects CanLII Terms of Use by linking directly to primary court/tribunal neutral citations (`SCC`, `FCA`, `ONCA`, `QCCA`) and official commissioner repositories.

### 2.3 European Union (Union-Wide & 27 Member States)
- **EUR-Lex, Publications Office Cellar, CJEU Curia, EDPB & EDPS**:
  - Governed by **Commission Decision 2011/833/EU** on the reuse of Commission documents and the EUR-Lex Legal Notice (CC BY 4.0 / open reuse for commercial and non-commercial purposes provided the source `"© European Union, https://eur-lex.europa.eu"` is acknowledged and the legal authenticity disclaimer for the Official Journal is preserved).
- **EU Member State National Gazettes & DPAs (`27 Member States + 16 German Länder`)**:
  - Official statutory texts and DPA enforcement decisions published in national official journals (*Journal Officiel / Légifrance*, *Bundesgesetzblatt / Gesetze im Internet*, *BOE*, *Gazzetta Ufficiale / Normattiva*, *RIS Austria*, *Overheid.nl*, *ISAP Poland*, etc.) are exempt from copyright or open for reuse with source attribution under national copyright exceptions for official acts (e.g., § 5 UrhG in Germany, Art. L122-5 Code de la propriété intellectuelle in France).
