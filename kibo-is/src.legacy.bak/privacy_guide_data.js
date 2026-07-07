// Privacy Laws: Canada, US, and EU — Complete Research Guide
// Last Updated: June 2026

export const PRIVACY_GUIDE_META = {
  title: "Privacy Laws: Canada, US, and EU — Complete Research Guide",
  lastUpdated: "June 2026",
  scope: "Federal and state privacy legislation across three jurisdictions",
  status: "Complete Research Compilation",
  verification: "Cross-referenced official government sources and regulatory bodies",
};

export const PRIVACY_GUIDE_DATA = {
  ...PRIVACY_GUIDE_META,
  sections: [

    // ─────────────────────────────────────────────────────────────────────────
    // CANADA
    // ─────────────────────────────────────────────────────────────────────────
    {
      id: "canada_federal",
      title: "Canada — Federal Legislation",
      flag: "🇨🇦",
      items: [
        {
          name: "1. Personal Information Protection and Electronic Documents Act (PIPEDA)",
          effective: "2004 (fully in force)",
          scope: "Federal private sector; applies across provincial/international borders",
          details: "Governs collection, use, and disclosure of personal information in commercial activities.",
          links: [
            { text: "OPC PIPEDA Overview", url: "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/" },
            { text: "CASL Compliance Help", url: "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/r_o_p/canadas-anti-spam-legislation/casl-compliance-help-for-businesses/" },
            { text: "PIPEDA Principles Guide", url: "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/" },
          ],
        },
        {
          name: "2. Canada's Anti-Spam Legislation (CASL) — Fighting Internet and Wireless Spam Act",
          effective: "January 1, 2014",
          scope: "Commercial electronic messages (email, SMS, social media DMs) sent to, from, or accessed in Canada",
          details: "Penalties: Up to CAD $1M per violation (individuals); up to CAD $10M (organizations).",
          links: [
            { text: "OPC CASL Overview", url: "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/r_o_p/canadas-anti-spam-legislation/" },
            { text: "FightSpam.gc.ca Portal", url: "https://www.fightspam.gc.ca" },
            { text: "CRTC Enforcement", url: "https://www.crtc.gc.ca" },
          ],
        },
        {
          name: "3. Quebec's Law 25 (Bill 64) — An Act to modernize legislative provisions as regards the protection of personal information",
          effective: "Most provisions in effect; data portability right September 2024",
          scope: "Provincial; applies to Quebec residents' personal data",
          details: "Highest penalties in Canada: Up to CAD $25M or 4% of worldwide revenue.",
          links: [
            { text: "CAI Quebec", url: "https://www.cai.gouv.qc.ca" },
            { text: "Law 25 Overview (English)", url: "https://www.cai.gouv.qc.ca/en/" },
          ],
        },
        {
          name: "4. Bill C-27 (Pending) — Digital Charter Implementation Act",
          effective: "Proposed; expected adoption within 1–2 years",
          scope: "Would introduce CPPA (replaces PIPEDA commercial provisions), Personal Information and Data Protection Tribunal Act, and Artificial Intelligence and Data Act",
          details: "Proposed Penalties: Up to CAD $25M or 5% of global gross revenue.",
          links: [
            { text: "Parliament of Canada (Bill C-27)", url: "https://www.parl.ca/DocumentViewer/en/44-1/bill/C-27/first-reading" },
            { text: "Department of Justice — Digital Charter", url: "https://www.justice.gc.ca/eng/csj-sjc/principles-principes.html" },
          ],
        },
      ],
    },
    {
      id: "canada_provincial",
      title: "Canada — Provincial Legislation",
      flag: "🇨🇦",
      items: [
        {
          name: "British Columbia — Personal Information Protection Act (PIPA)",
          effective: "2004",
          scope: "Private-sector organizations operating in BC",
          details: "Enforced by the Office of the Information and Privacy Commissioner of BC.",
          links: [{ text: "OIPC British Columbia", url: "https://www.oipc.bc.ca/" }],
        },
        {
          name: "Alberta — Personal Information Protection Act (PIPA)",
          effective: "2004",
          scope: "Private-sector organizations operating in Alberta",
          details: "Enforced by the Office of the Information and Privacy Commissioner of Alberta.",
          links: [{ text: "OIPC Alberta", url: "https://www.oipc.ab.ca/" }],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────
    // UNITED STATES — FEDERAL
    // ─────────────────────────────────────────────────────────────────────────
    {
      id: "us_federal",
      title: "United States — Federal Legislation",
      flag: "🇺🇸",
      items: [
        {
          name: "1. CAN-SPAM Act — Controlling the Assault of Non-Solicited Pornography and Marketing Act",
          effective: "January 1, 2004",
          scope: "Commercial electronic mail sent to US recipients",
          details: "Model: Opt-out (permissive). Penalties: Up to USD $43,792 per violation (adjusted annually).",
          links: [
            { text: "FTC CAN-SPAM Compliance Guide", url: "https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business" },
            { text: "FTC CAN-SPAM Overview", url: "https://www.ftc.gov/news-events/topics/protecting-consumer-privacy-security" },
            { text: "Federal Trade Commission", url: "https://www.ftc.gov" },
          ],
        },
        {
          name: "2. Children's Online Privacy Protection Act (COPPA)",
          effective: "April 21, 2000",
          scope: "Online services/websites collecting data from children under 13",
          details: "Requires parental consent, transparent privacy policies, and prohibits targeted advertising.",
          links: [
            { text: "FTC COPPA Overview", url: "https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-process/childrens-online-privacy-protection-rule-coppa" },
            { text: "COPPA Compliance", url: "https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy" },
          ],
        },
        {
          name: "3. Health Insurance Portability and Accountability Act (HIPAA)",
          effective: "April 14, 2003 (compliance deadline)",
          scope: "Protected Health Information (PHI) held by covered entities and business associates",
          details: "Enforced by HHS Office for Civil Rights.",
          links: [
            { text: "HHS HIPAA Home Page", url: "https://www.hhs.gov/hipaa/index.html" },
            { text: "HIPAA Regulations (eCFR)", url: "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C" },
            { text: "HHS OCR Enforcement", url: "https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/index.html" },
          ],
        },
        {
          name: "4. Fair Credit Reporting Act (FCRA)",
          effective: "1970; updated via Gramm-Leach-Bliley Act amendments",
          scope: "Consumer reports, credit reports, background checks",
          details: "Enforced by FTC and Consumer Financial Protection Bureau (CFPB).",
          links: [
            { text: "FTC FCRA Overview", url: "https://www.ftc.gov/business-guidance/privacy-security/fair-credit-reporting-act" },
            { text: "Text of FCRA (eCFR)", url: "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-F/part-600" },
          ],
        },
        {
          name: "5. Gramm-Leach-Bliley Act (GLBA) — Financial Privacy Rule & Safeguards Rule",
          effective: "1999; updated 2023",
          scope: "Financial institutions (banks, insurance companies, securities brokers)",
          details: "Requires privacy notices and information security standards.",
          links: [
            { text: "FTC GLBA Overview", url: "https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act" },
            { text: "GLBA Regulations (eCFR)", url: "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-H" },
          ],
        },
        {
          name: "6. Health Breach Notification Rule",
          effective: "May 2022",
          scope: "Breach notification for personal health information",
          details: "Covers vendors of personal health records and related entities.",
          links: [
            { text: "HHS Health Breach Notification Rule", url: "https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html" },
          ],
        },
        {
          name: "7. Take It Down Act (TIDA) — Intimate Images",
          effective: "May 19, 2026",
          scope: "Removal of non-consensual intimate images/videos from online platforms",
          details: "Platforms must remove content within 48 hours of a valid request. Enforced by FTC.",
          links: [
            { text: "FTC Take It Down Act Enforcement", url: "https://www.ftc.gov/news-events/news/2024/05/ftc-takes-action-under-new-authority-remove-nonconsensual-intimate-images" },
          ],
        },
        {
          name: "8. FTC Act Section 5 — Unfair and Deceptive Trade Practices",
          effective: "1914 (privacy application since 1990s)",
          scope: "General privacy violations and unfair/deceptive data practices",
          details: "FTC can bring enforcement actions against privacy violations.",
          links: [
            { text: "FTC Privacy & Security Enforcement", url: "https://www.ftc.gov/news-events/topics/protecting-consumer-privacy-security/privacy-security-enforcement" },
          ],
        },
        {
          name: "9. American Privacy Rights Act (APRA) — PENDING",
          effective: "Draft published April 21, 2024 — not yet enacted",
          scope: "Proposed unified federal privacy law covering all US states",
          details: "Would consolidate CCPA, VCDPA, CPA into a uniform national standard. Penalties up to USD $25M.",
          links: [
            { text: "House Committee on Energy and Commerce", url: "https://energycommerce.house.gov/" },
            { text: "Congress.gov APRA tracking", url: "https://www.congress.gov/" },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────
    // UNITED STATES — STATE LAWS
    // ─────────────────────────────────────────────────────────────────────────
    {
      id: "us_states",
      title: "United States — State-Level Comprehensive Privacy Laws",
      flag: "🇺🇸",
      items: [
        {
          name: "1. California Consumer Privacy Act (CCPA) & California Privacy Rights Act (CPRA)",
          effective: "CCPA: January 1, 2020 | CPRA: January 1, 2023 (enforcement Jan 1, 2024)",
          scope: "California residents' consumer data",
          details: "Enforced by CPPA & AG. Penalties: $2,500/violation; $7,500/intentional violation. Private right of action for data breaches.",
          links: [
            { text: "California AG CCPA Page", url: "https://oag.ca.gov/privacy/ccpa" },
            { text: "CCPA Full Text", url: "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201720180AB375" },
            { text: "California Privacy Protection Agency (CPPA)", url: "https://cppa.ca.gov" },
            { text: "CPRA Full Text", url: "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202020210AB701" },
            { text: "CPPA Enforcement", url: "https://cppa.ca.gov/enforcement/" },
          ],
        },
        {
          name: "2. Virginia Consumer Data Protection Act (VCDPA)",
          effective: "January 1, 2023",
          scope: "For-profit entities processing personal data of 100,000+ Virginia residents",
          details: "Up to USD $7,500 per civil violation; 30-day cure period.",
          links: [
            { text: "Virginia GA Bill Text", url: "https://lis.virginia.gov/cgi-bin/legp604.exe?211+sum+HB2307" },
            { text: "Virginia AG Privacy Page", url: "https://www.oag.state.va.us/consumer-protection/data-privacy" },
          ],
        },
        {
          name: "3. Colorado Privacy Act (CPA)",
          effective: "July 1, 2023",
          scope: "For-profit entities processing data of 100,000+ Colorado residents OR selling data of 25,000+ residents",
          details: "Enforced by Colorado Attorney General.",
          links: [
            { text: "Colorado AG Privacy Page", url: "https://coag.gov/" },
            { text: "CPA Text (SB21-169)", url: "https://leg.colorado.gov/bills/sb21-169" },
          ],
        },
        {
          name: "4. Connecticut Data Privacy Act (CTDPA)",
          effective: "July 1, 2023",
          scope: "Entities collecting Connecticut residents' data meeting threshold requirements",
          details: "Enforced by Connecticut Attorney General.",
          links: [
            { text: "Connecticut General Assembly", url: "https://www.cga.ct.gov/" },
            { text: "CTDPA Text (SB-6)", url: "https://www.cga.ct.gov/asp/cgabillstatus/cgabillstatus.asp?selBillType=Public%20Act&bill_yr=2022&bill_num=6" },
            { text: "Connecticut Attorney General", url: "https://portal.ct.gov/AG" },
          ],
        },
        {
          name: "5. Utah Consumer Privacy Act (UCPA)",
          effective: "December 31, 2023",
          scope: "More favorable to businesses; higher thresholds than CCPA/VCDPA/CPA",
          details: "Enforced by Utah Attorney General.",
          links: [
            { text: "UCPA Full Text", url: "https://le.utah.gov/xcode/Title13/Chapter61/13-61.html" },
            { text: "Utah Attorney General", url: "https://attorneygeneral.utah.gov/" },
          ],
        },
        {
          name: "6. Texas Data Privacy and Security Act (TDPSA)",
          effective: "January 1, 2024",
          scope: "Texas residents' personal data",
          details: "Enforced by Texas Attorney General.",
          links: [
            { text: "TDPSA Text", url: "https://statutes.capitol.texas.gov/Docs/BC/htm/BC.521.htm" },
            { text: "Texas Attorney General", url: "https://www.texasattorneygeneral.gov/" },
          ],
        },
        {
          name: "7. Oregon Consumer Privacy Act (OCPA)",
          effective: "July 1, 2024",
          scope: "Oregon residents' personal data",
          details: "Enforced by Oregon DOJ.",
          links: [
            { text: "Oregon Legislature", url: "https://www.oregonlegislature.gov/" },
            { text: "Oregon DOJ", url: "https://www.oregon.gov/doj/" },
          ],
        },
        {
          name: "8. Additional State Laws In Effect (2024–2026)",
          effective: "Various effective dates 2024–2026",
          scope: "Montana (Oct 2024), Tennessee (Jul 2025), Iowa (Jul 2025), Delaware (Jan 2025), Indiana (Jan 2026), Kentucky (Jan 2026), New Hampshire (Jan 2026)",
          details: "20+ states now have comprehensive privacy laws as of 2026. No federal umbrella law yet enacted.",
          links: [
            { text: "Montana MCA Title 30", url: "https://leg.mt.gov/bills/mca/title_0300/chapter_0370/part_0010/" },
            { text: "Tennessee (HB1414)", url: "https://legiscan.com/TN/bill/HB1414/2023" },
            { text: "Iowa Legislature", url: "https://legis.iowa.gov/" },
            { text: "Delaware Code", url: "https://delcode.delaware.gov/" },
            { text: "Kentucky Legislature", url: "https://legislature.ky.gov/" },
            { text: "New Hampshire Gen Court", url: "https://www.gencourt.state.nh.us/" },
          ],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────
    // EU & EEA
    // ─────────────────────────────────────────────────────────────────────────
    {
      id: "eu_core",
      title: "European Union & EEA — Core Legislation",
      flag: "🇪🇺",
      items: [
        {
          name: "1. General Data Protection Regulation (GDPR) — Regulation (EU) 2016/679",
          effective: "May 25, 2018",
          scope: "Any organization processing personal data of EU/EEA residents",
          details: "Opt-in consent model. Penalties: Up to EUR 20M or 4% of global annual revenue (whichever higher).",
          links: [
            { text: "GDPR Full Text & Commentary", url: "https://gdpr-info.eu/" },
            { text: "EUR-Lex Official GDPR Text", url: "https://eur-lex.europa.eu/eli/reg/2016/679/oj" },
            { text: "European Data Protection Board (EDPB)", url: "https://edpb.ec.europa.eu/" },
            { text: "European Data Protection Supervisor (EDPS)", url: "https://edps.europa.eu/" },
            { text: "GDPR Portal (EU Commission)", url: "https://ec.europa.eu/info/law/law-topic/data-protection_en" },
          ],
        },
        {
          name: "2. ePrivacy Directive — Directive 2002/58/EC (amended 2009/136/EC)",
          effective: "2002 (amended 2009)",
          scope: "Electronic communications services, cookies, direct marketing",
          details: '"Cookie Law" — requires explicit consent for non-essential cookies. ePrivacy Regulation proposal withdrawn February 2025; Directive remains in force.',
          links: [
            { text: "ePrivacy Directive Full Text", url: "https://eur-lex.europa.eu/eli/dir/2002/58/oj" },
            { text: "Amendment (2009/136/EC)", url: "https://eur-lex.europa.eu/eli/dir/2009/136/oj" },
            { text: "EDPS ePrivacy Page", url: "https://www.edps.europa.eu/data-protection/our-work/subjects/eprivacy-directive_en" },
          ],
        },
        {
          name: "3. Law Enforcement Directive (LED) — Directive (EU) 2016/680",
          effective: "May 25, 2018",
          scope: "Processing of personal data for law enforcement purposes",
          details: "Provides GDPR-equivalent protections for law enforcement data processing.",
          links: [
            { text: "LED Full Text", url: "https://eur-lex.europa.eu/eli/dir/2016/680/oj" },
            { text: "EDPB Guidance on LED", url: "https://edpb.ec.europa.eu/our-work-tools/our-documents_en?type=guidelines" },
          ],
        },
        {
          name: "4. Data Protection Regulation for EU Institutions — EUDPR (EU) 2018/1807",
          effective: "2019",
          scope: "Processing by EU institutions and bodies",
          details: "Applies the GDPR framework to EU institutions themselves.",
          links: [
            { text: "EUDPR Full Text", url: "https://eur-lex.europa.eu/eli/reg/2018/1807/oj" },
          ],
        },
        {
          name: "5. Digital Services Act (DSA)",
          effective: "August 25, 2024",
          scope: "Online platforms and digital services; includes privacy implications",
          details: "Large platforms must provide ad transparency, algorithmic accountability, and data access for researchers.",
          links: [
            { text: "DSA Full Text", url: "https://eur-lex.europa.eu/eli/reg/2022/1914/oj" },
            { text: "EU Commission DSA Page", url: "https://digital-strategy.ec.europa.eu/en/policies/digital-services-act" },
          ],
        },
        {
          name: "6. Digital Markets Act (DMA)",
          effective: "November 1, 2022",
          scope: "Large digital gatekeepers; includes fair data practices",
          details: "Prohibits combining personal data across services without explicit consent.",
          links: [
            { text: "DMA Full Text", url: "https://eur-lex.europa.eu/eli/reg/2022/1925/oj" },
          ],
        },
        {
          name: "7. Artificial Intelligence Act",
          effective: "Phased 2024–2026",
          scope: "AI systems; includes data minimization and privacy requirements",
          details: "High-risk AI systems face mandatory conformity assessments and data governance requirements.",
          links: [
            { text: "AI Act Full Text", url: "https://eur-lex.europa.eu/eli/reg/2024/1689/oj" },
            { text: "EU Commission AI Page", url: "https://digital-strategy.ec.europa.eu/en/policies/ai-act" },
          ],
        },
      ],
    },
    {
      id: "eu_uk",
      title: "UK Privacy Law (Post-Brexit)",
      flag: "🇬🇧",
      items: [
        {
          name: "1. UK GDPR — Data Protection Act 2018 (as amended)",
          effective: "January 1, 2021 (post-Brexit transition)",
          scope: "Organizations in UK or processing UK residents' data",
          details: "UK retained GDPR as domestic law. EU Commission granted UK adequacy decision.",
          links: [
            { text: "Information Commissioner's Office (ICO)", url: "https://ico.org.uk/" },
            { text: "ICO Privacy Guide", url: "https://ico.org.uk/for-organisations/advice-and-guidance/" },
            { text: "UK Data Protection Act 2018", url: "https://www.legislation.gov.uk/ukpga/2018/12/contents" },
          ],
        },
        {
          name: "2. Privacy and Electronic Communications Regulations (PECR)",
          effective: "2003",
          scope: "Electronic communications, cookies, email marketing in the UK",
          details: "UK equivalent of the ePrivacy Directive.",
          links: [
            { text: "ICO PECR Guidance", url: "https://ico.org.uk/for-organisations/guide-to-pecr/" },
            { text: "PECR Text", url: "https://www.legislation.gov.uk/statutory-instruments/2003/2426/contents" },
          ],
        },
      ],
    },
    {
      id: "eu_eea",
      title: "Switzerland & Non-EU EEA Countries",
      flag: "🌍",
      items: [
        {
          name: "Switzerland — Federal Data Protection Act (FDPA)",
          effective: "Harmonizing with GDPR/ePrivacy standards (fully revised FDPA: 2023)",
          scope: "Swiss private-sector and federal body data processing",
          details: "Substantially aligned with GDPR; Switzerland holds EU adequacy status.",
          links: [
            { text: "Swiss Federal DPA (FDPIC)", url: "https://www.edoeb.admin.ch/" },
            { text: "FDPA Text", url: "https://www.admin.ch/opc/en/classified-compilation/19920153/index.html" },
          ],
        },
        {
          name: "Iceland — Data Protection Act",
          effective: "2018 (GDPR-equivalent via EEA Agreement)",
          scope: "All personal data processing in Iceland",
          details: "Enforced by the Icelandic Data Protection Authority.",
          links: [{ text: "Icelandic DPA (Persónuvernd)", url: "https://www.dpa.is/" }],
        },
        {
          name: "Norway — Personal Data Act",
          effective: "2018 (GDPR incorporated via EEA Agreement)",
          scope: "All personal data processing in Norway",
          details: "Enforced by Datatilsynet (Norwegian Data Protection Authority).",
          links: [{ text: "Norwegian DPA (Datatilsynet)", url: "https://www.datatilsynet.no/" }],
        },
        {
          name: "Liechtenstein — Data Protection Act",
          effective: "2018 (GDPR-equivalent via EEA Agreement)",
          scope: "All personal data processing in Liechtenstein",
          details: "Enforced by the Liechtenstein Data Protection Office (DSP).",
          links: [{ text: "Liechtenstein DPA (DSP)", url: "https://www.dsp.li/" }],
        },
      ],
    },

    // ─────────────────────────────────────────────────────────────────────────
    // ENFORCEMENT BODIES
    // ─────────────────────────────────────────────────────────────────────────
    {
      id: "enforcement",
      title: "Enforcement & Regulatory Bodies",
      flag: "⚖️",
      items: [
        {
          name: "Canada — Federal & Provincial Regulators",
          effective: "Ongoing",
          scope: "Federal and provincial privacy enforcement",
          details: "OPC (Federal), CRTC (CASL), CAI (Quebec), OIPC BC, OIPC Alberta.",
          links: [
            { text: "OPC — Office of the Privacy Commissioner of Canada", url: "https://www.priv.gc.ca" },
            { text: "CRTC — CASL Enforcement", url: "https://www.crtc.gc.ca" },
            { text: "CAI Quebec", url: "https://www.cai.gouv.qc.ca" },
            { text: "OIPC British Columbia", url: "https://www.oipc.bc.ca" },
            { text: "OIPC Alberta", url: "https://www.oipc.ab.ca" },
          ],
        },
        {
          name: "United States — Federal Regulators",
          effective: "Ongoing",
          scope: "Federal privacy, financial data, and health data enforcement",
          details: "FTC (general), CFPB (financial), HHS OCR (HIPAA), CPPA (California), state AGs.",
          links: [
            { text: "Federal Trade Commission (FTC)", url: "https://www.ftc.gov" },
            { text: "FTC Privacy & Security Portal", url: "https://www.ftc.gov/business-guidance/privacy-security" },
            { text: "Consumer Financial Protection Bureau (CFPB)", url: "https://www.consumerfinance.gov/" },
            { text: "HHS Office for Civil Rights (HIPAA)", url: "https://www.hhs.gov/hipaa" },
            { text: "California Privacy Protection Agency (CPPA)", url: "https://cppa.ca.gov" },
            { text: "California Attorney General", url: "https://oag.ca.gov" },
            { text: "Virginia Attorney General", url: "https://www.oag.state.va.us" },
            { text: "Colorado Attorney General", url: "https://coag.gov" },
            { text: "Connecticut Attorney General", url: "https://portal.ct.gov/AG" },
            { text: "Utah Attorney General", url: "https://attorneygeneral.utah.gov" },
          ],
        },
        {
          name: "European Union — Regulatory Bodies",
          effective: "Ongoing",
          scope: "EU-wide and member-state DPAs",
          details: "EDPB (EU-wide coordination), EDPS (EU institutions), National DPAs (CNIL, BfDI, ICO, DPC, AP, etc.).",
          links: [
            { text: "European Data Protection Board (EDPB)", url: "https://edpb.ec.europa.eu" },
            { text: "EDPB Guidelines & Recommendations", url: "https://edpb.ec.europa.eu/our-work-tools/our-documents_en" },
            { text: "European Data Protection Supervisor (EDPS)", url: "https://edps.europa.eu" },
            { text: "Germany (BfDI)", url: "https://www.bfdi.bund.de/" },
            { text: "France (CNIL)", url: "https://www.cnil.fr/" },
            { text: "Spain (AEPD)", url: "https://www.aepd.es/" },
            { text: "Italy (Garante)", url: "https://www.garanteprivacy.it/" },
            { text: "Netherlands (AP)", url: "https://www.autoriteitpersoonsgegevens.nl/" },
            { text: "Ireland (DPC)", url: "https://www.dataprotection.ie/" },
            { text: "Belgium (APD)", url: "https://www.autoriteprotectiondonnees.be/" },
            { text: "Sweden (IMY)", url: "https://www.imy.se/" },
            { text: "Denmark (DPA)", url: "https://www.datatilsynet.dk/" },
            { text: "UK ICO", url: "https://ico.org.uk/" },
          ],
        },
      ],
    },
  ],

  // ───────────────────────────────────────────────────────────────────────────
  // KEY DIFFERENCES COMPARISON TABLE
  // ───────────────────────────────────────────────────────────────────────────
  comparison: [
    { feature: "Model", canada: "Opt-in (explicit consent)", us: "Opt-out (CAN-SPAM); Opt-in (CCPA)", eu: "Opt-in (explicit consent required)" },
    { feature: "Scope", canada: "Commercial activities; electronic messages", us: "Commercial email; consumer data", eu: "Any personal data processing" },
    { feature: "Penalties", canada: "CAD $1M–$10M (CASL); CAD $25M (Law 25)", us: "USD $43K–$7.5K per violation", eu: "EUR 20M or 4% revenue (whichever higher)" },
    { feature: "Private Right of Action", canada: "No (CASL suspended 2017)", us: "Yes (California data breaches)", eu: "Limited (member state dependent)" },
    { feature: "Consent Logs", canada: "Required (PIPEDA)", us: "Not required (CAN-SPAM)", eu: "Required (GDPR Art. 7)" },
    { feature: "DPA Requirement", canada: "Limited", us: "Required (high-risk processing)", eu: "Required" },
    { feature: "Data Minimization", canada: "Required (PIPEDA)", us: "Not explicit (CCPA)", eu: "Required (GDPR Art. 5)" },
  ],

  // ───────────────────────────────────────────────────────────────────────────
  // ADDITIONAL RESOURCES
  // ───────────────────────────────────────────────────────────────────────────
  additionalResources: [
    { text: "International Association of Privacy Professionals (IAPP)", url: "https://iapp.org/" },
    { text: "Privacy World Blog", url: "https://www.privacyworld.blog/" },
    { text: "OneTrust Privacy Resource Library", url: "https://www.onetrust.com/resources/" },
    { text: "Osano Privacy Library", url: "https://www.osano.com/articles/" },
    { text: "EU Data Protection Portal", url: "https://ec.europa.eu/info/law/law-topic/data-protection_en" },
    { text: "EU Digital Strategy Portal", url: "https://digital-strategy.ec.europa.eu/" },
  ],

  // ───────────────────────────────────────────────────────────────────────────
  // 2026 RESEARCHER NOTES
  // ───────────────────────────────────────────────────────────────────────────
  researcherNotes: [
    { title: "Canada", note: "Bill C-27 remains pending; Quebec Law 25 fully operational as of September 2024." },
    { title: "United States", note: "20+ states now have comprehensive privacy laws; APRA proposal under consideration at federal level." },
    { title: "EU", note: "ePrivacy Regulation proposal withdrawn (February 2025); ePrivacy Directive remains in force." },
    { title: "Digital Services", note: "DSA enforcement ongoing; DMA fully in effect; AI Act in phased implementation 2024–2026." },
    { title: "Multi-Jurisdiction", note: "Organizations operating across all three regions must comply with GDPR (strictest standard), which typically covers other jurisdictions." },
    { title: "Sector-Specific", note: "Healthcare (HIPAA), finance (GLBA), and children (COPPA) have additional federal requirements in the US." },
    { title: "Data Transfers", note: "International data flows require adequacy decisions or Standard Contractual Clauses (SCCs)." },
  ],
};
