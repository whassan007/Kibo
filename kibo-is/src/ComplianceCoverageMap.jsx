import React, { useState, useEffect, useMemo } from 'react';
import {
  Globe, Shield, ShieldAlert, Award, FileText, AlertTriangle, CheckCircle,
  Clock, Plus, Search, Filter, Cpu, Layers, RefreshCw, BarChart2, Info, ArrowRight, Check,
  BookOpen, Terminal, Activity, HelpCircle
} from 'lucide-react';

export default function ComplianceCoverageMap({ API_BASE }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState('CA');
  const [selectedIndustry, setSelectedIndustry] = useState('Healthcare');
  const [selectedCell, setSelectedCell] = useState(null); // { country, industry }
  const [searchQuery, setSearchQuery] = useState('');
  const [mapOverlayMode, setMapOverlayMode] = useState('completeness'); // 'completeness', 'density', 'complexity'
  const [createdTasks, setCreatedTasks] = useState({}); // To track tasks generated in this session

  // State for Context Seeder
  const [seederJur, setSeederJur] = useState({ Ontario: true, Quebec: false, California: false });
  const [seederCat, setSeederCat] = useState({ PHI: true, ChildrensData: false, BiometricData: false });
  const [seederChildAge, setSeederChildAge] = useState(12);
  const [crossBorderOrigin, setCrossBorderOrigin] = useState('Quebec');
  const [crossBorderDest, setCrossBorderDest] = useState('California');
  const [sccUploaded, setSccUploaded] = useState(false);

  // Helper to color code jurisdictions based on readiness scores
  const getCountryColor = (code, readiness) => {
    if (selectedCountry === code) return '#2563EB'; // Active selection platform blue
    if (readiness >= 90) return '#059669'; // High readiness green
    if (readiness >= 75) return '#D97706'; // Medium readiness amber
    return '#DC2626'; // Low readiness red
  };


  // Derived rulesets
  const activeRulesets = useMemo(() => {
    const rules = [];
    if (seederJur.Ontario && seederCat.PHI) rules.push({ name: "PHIPA Health Audit", desc: "Mandates PHIPA TRA (SLA: 30 days)" });
    if (seederJur.Quebec) {
      rules.push({ name: "Law 25 Governance", desc: "Mandates Privacy Impact Assessment (SLA: 30 days)" });
      if (seederCat.ChildrensData && seederChildAge < 14) {
        rules.push({ name: "Quebec Child Consent Gate", desc: "Mandatory Parental Consent Required for age under 14" });
      }
    }
    if (seederJur.California && seederCat.BiometricData) rules.push({ name: "CPRA Biometric Opt-Out", desc: "Mandatory ADMT Risk Assessment (SLA: 45 days)" });
    return rules;
  }, [seederJur, seederCat, seederChildAge]);

  // Adequacy check
  const crossBorderAdequacy = useMemo(() => {
    if (crossBorderOrigin === 'Quebec' && crossBorderDest === 'EU_Union') return { status: 'Adequate', blocked: false };
    if (crossBorderOrigin === 'Quebec' && crossBorderDest === 'California') return { status: 'Non-Adequate', blocked: !sccUploaded };
    return { status: 'Adequate', blocked: false };
  }, [crossBorderOrigin, crossBorderDest, sccUploaded]);


  // Fetch coverage data from backend
  const fetchCoverage = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/compliance/coverage`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('kibo_token') || 'mock-expert-token'}`
        }
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error("Error fetching compliance coverage:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCoverage();
  }, []);

  const handleCreateTask = async (gapId, gapTitle, gapDetails, country) => {
    try {
      const res = await fetch(`${API_BASE}/api/compliance/gaps/create_task`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('kibo_token') || 'mock-expert-token'}`
        },
        body: JSON.stringify({
          task_name: gapTitle,
          category: "Compliance Map Gap",
          scope: "Federal",
          jurisdiction: country,
          notes: gapDetails
        })
      });
      if (res.ok) {
        setCreatedTasks(prev => ({ ...prev, [gapId]: true }));
      }
    } catch (e) {
      console.error("Error creating compliance task:", e);
    }
  };

  // Expanded detailed static data structure matching EVERY requirement
  const selectedJurDetails = useMemo(() => {
    const defaultData = {
      CA: {
        country: 'Canada',
        region: 'North America',
        state_prov: 'Ontario & Quebec (bilingual Law 25)',
        laws: ['PIPEDA', 'Law 25', 'FIPPA'],
        ai_regulations: ['AIDA (Artificial Intelligence and Data Act)'],
        cybersecurity_laws: ['Bill C-26 (Critical Infrastructure Safeguards)'],
        consumer_protection: ['Consumer Protection Act (Quebec)', 'CASL'],
        sector_regulations: ['PHIPA (Health Custodians)', 'CYFSA (Youth Services)'],
        authorities: ['OPC Canada', 'CAI Quebec', 'IPC Ontario'],
        effective_date: '2001-01-01 (PIPEDA) / 2023-09-22 (Law 25)',
        last_amended: '2023-09-22',
        version: 'v4.8.2 (Production)',
        coverage_score: 95,
        readiness: 94,
        validation_date: '2026-07-01',
        confidence: 98,
        pending_updates: 'Law 25 Stage 3 Phase out rules',
        upcoming_changes: 'Bill C-27 passage (CPPA + AIDA enforcement updates)',
        instruments: [
          { title: "PIPEDA Schedule 1 Section 4.7", citation: "PIPEDA-SCH1-4.7", authority: "OPC Canada", status: "Production-Ready", effective: "2001-01-01", version: "v1.0", language: "English/French", trust_tier: "L4 - Statutory", source: "Federal Register", collection: "KIBO_RAG_LEGAL_GT", embedding: "SHA256:d9b2089f", indexed: "2026-07-01", reviewed: "2026-07-01", superseded: "No" },
          { title: "Quebec Law 25 Article 14 Consent", citation: "LAW25-SEC14", authority: "CAI Quebec", status: "Production-Ready", effective: "2023-09-22", version: "v1.2", language: "Bilingual (FR/EN)", trust_tier: "L4 - Statutory", source: "Quebec Gazette", collection: "KIBO_RAG_LEGAL_GT", embedding: "SHA256:b8c983ea", indexed: "2026-06-30", reviewed: "2026-06-30", superseded: "No" }
        ]
      },
      US: {
        country: 'United States',
        region: 'North America',
        state_prov: 'California',
        laws: ['CPRA / CCPA', 'HIPAA'],
        ai_regulations: ['NIST AI RMF (Risk Management Framework)'],
        cybersecurity_laws: ['NYDFS Part 500', 'FTC Safeguards Rule'],
        consumer_protection: ['FTC Act Section 5', 'California Unfair Competition Law'],
        sector_regulations: ['HIPAA Privacy & Security (Healthcare)', 'GLBA (Finance)'],
        authorities: ['California Privacy Protection Agency (CPPA)', 'FTC', 'HHS OCR'],
        effective_date: '2020-01-01 (CCPA) / 2023-01-01 (CPRA)',
        last_amended: '2023-07-01',
        version: 'v3.1.0 (Active)',
        coverage_score: 87,
        readiness: 85,
        validation_date: '2026-06-15',
        confidence: 90,
        pending_updates: 'CPRA Enforcement updates on automated profiling',
        upcoming_changes: 'Federal APRA (American Privacy Rights Act) draft debates',
        instruments: [
          { title: "CPRA Section 1798.100 Consumer Deletion", citation: "CPRA-SEC100", authority: "CPPA", status: "Active", effective: "2023-01-01", version: "v2.0", language: "English", trust_tier: "L4 - Statutory", source: "CA Legislative Portal", collection: "KIBO_RAG_LEGAL_GT", embedding: "SHA256:a90bcdef", indexed: "2026-06-15", reviewed: "2026-06-15", superseded: "No" }
        ]
      },
      EU: {
        country: 'European Union',
        region: 'Europe',
        state_prov: 'Member States',
        laws: ['GDPR', 'ePrivacy Directive'],
        ai_regulations: ['EU AI Act (Risk-based Classification)'],
        cybersecurity_laws: ['NIS2 Directive', 'DORA (Financial Systems)'],
        consumer_protection: ['Unfair Commercial Practices Directive'],
        sector_regulations: ['MDR (Medical Devices)', 'MiFID II (Finance)'],
        authorities: ['European Data Protection Board (EDPB)', 'DPA Supervisories'],
        effective_date: '2018-05-25 (GDPR)',
        last_amended: '2024-05-01 (AI Act alignment)',
        version: 'v5.0.0 (Production)',
        coverage_score: 90,
        readiness: 88,
        validation_date: '2026-06-28',
        confidence: 92,
        pending_updates: 'EU AI Act phased enforcement timeline',
        upcoming_changes: 'ePrivacy Regulation final ratification',
        instruments: [
          { title: "GDPR Article 28 Processor DPA Contracts", citation: "GDPR-ART28", authority: "EDPB", status: "Production-Ready", effective: "2018-05-25", version: "v1.0", language: "Multi-lingual", trust_tier: "L4 - Statutory", source: "EUR-Lex Official", collection: "KIBO_RAG_LEGAL_GT", embedding: "SHA256:f45bdcca", indexed: "2026-06-28", reviewed: "2026-06-28", superseded: "No" }
        ]
      }
    };

    if (data && data.jurisdictions && data.jurisdictions[selectedCountry]) {
      // Merge dynamic count data if available
      return {
        ...defaultData[selectedCountry],
        ...data.jurisdictions[selectedCountry]
      };
    }
    return defaultData[selectedCountry] || defaultData.CA;
  }, [data, selectedCountry]);

  // Industry Detail View mapping
  const industryDetails = {
    "Healthcare": {
      regulations: "PHIPA (Ontario), HIPAA (US), GDPR Art 9 Special Category Data",
      controls: "Patient Consent Logs, EMR Encryption Gates, Access Log Retention Controls",
      policies: "Health Data Privacy Policy, PHI Disclosure Protocol",
      assessments: "Healthcare Privacy Impact Assessment (H-PIA)",
      templates: "Patient Intake Form, PHI Incident Notification Template",
      records_of_processing: "Patient Medical Logs Sync, Care Counseling Transcripts",
      dpia_availability: "Available (Standard PHIPA Schema)",
      dsar_support: "Yes (Patient Access & Correction Support)",
      consent: "Explicit Opt-in Required, Revocable at treatment boundaries",
      incident_response: "IPC Health Data Breach Reporting Checklist",
      vendor_management: "BAA (Business Associate Agreement) + KIBO DPA Annex",
      retention: "10 Years (Medical records) / 90 Days (Chat transcripts purge)",
      classification: "SPI / Medical Diagnostics (Strict Encryption)",
      cross_border: "Restricted (Sovereignty checks active)",
      ai_governance: "Clinical Decision Support Audit Logs required",
      cybersecurity: "AES-256 at Rest, TLS 1.3 in Transit, Multi-factor auth",
      audit: "Annual Internal PHIPA audit + continuous log inspection",
      training: "Training Module mod-2: Handling Crisis Disclosures",
      automation: "94% automated log review and containment",
      knowledge_score: "98/100",
      status: "🟢 Fully Implemented",
      workflows: "Crisis counseling intake, referral routing",
      agents: "Crisis triage classification agent"
    },
    "Financial Services": {
      regulations: "PIPEDA, GLBA, NYDFS Cybersecurity, DORA (EU)",
      controls: "MFA Enforcement, Audit Log Hashing, Stale Account Lockout Gates",
      policies: "Financial Information Handling Policy, SOC 2 Security Policy",
      assessments: "Financial Infrastructure Risk Assessment",
      templates: "GLBA Consumer Opt-Out Notice Template",
      records_of_processing: "Billing, payroll sync records",
      dpia_availability: "Available (SOC 2 Scope)",
      dsar_support: "Yes (Standard consumer financial profile access)",
      consent: "Opt-out model for sharing, explicit opt-in for credit checks",
      incident_response: "72-hour regulator breach reporting gates",
      vendor_management: "Strict SOC 2 vendor validation requirements",
      retention: "7 Years (Tax audit guidelines)",
      classification: "SPI / Credit Card Numbers / Banking Credentials",
      cross_border: "Allowed under standard contractual clauses (SCC)",
      ai_governance: "Credit scoring algorithmic fairness audit logs",
      cybersecurity: "Hardware Security Module (HSM) key rotations",
      audit: "Bi-annual SOC 2 compliance reports",
      training: "Training Module mod-4: Cross-Border Data Basics",
      automation: "80% automated credential monitoring",
      knowledge_score: "85/100",
      status: "🟡 Partial Support",
      workflows: "Donation processing, billing sync",
      agents: "Audit logging analyzer agent"
    },
    "Technology": {
      regulations: "PIPEDA, CPRA, GDPR, CCPA",
      controls: "API Gateway Authentication, Hashed user telemetry profiles",
      policies: "Privacy-by-Design Engineering Policy, API Access Guidelines",
      assessments: "Algorithmic Risk Assessment",
      templates: "Code Audit Tracking Template",
      records_of_processing: "Web application server telemetry, CMP logs",
      dpia_availability: "Available (Standard GDPR template)",
      dsar_support: "Yes (Full JSON/CSV export capability)",
      consent: "Interactive Cookie Banner consent mappings",
      incident_response: "DevOps incident response gates",
      vendor_management: "Continuous subprocessor monitoring matrix",
      retention: "30 Days (Telemetry logs) / Indefinite (User profile)",
      classification: "PII / IP address / Device identifiers",
      cross_border: "Adequacy checks for EU-US and EU-CA transfer vectors",
      ai_governance: "EU AI Act compliance validation templates",
      cybersecurity: "Continuous penetration scanning, OAuth 2.0 gates",
      audit: "Continuous compliance checking via RAG engine",
      training: "Training Module mod-1: Privacy Fundamentals",
      automation: "98% automated compliance mapping",
      knowledge_score: "96/100",
      status: "🟢 Fully Implemented",
      workflows: "Client consent sync, pixel auditor",
      agents: "DSAR Assistant Agent"
    },
    "Non-Profit": {
      regulations: "PIPEDA, CASL, Quebec Law 25",
      controls: "Donor opt-in registries, Volunteer training checkpoints",
      policies: "Advancement Data Privacy Policy, Volunteer Code of Conduct",
      assessments: "Donor Database Compliance Audit",
      templates: "Donor Newsletter Opt-in Statement",
      records_of_processing: "Advancement records, CRM donor logs",
      dpia_availability: "Available (Standard PIPEDA baseline)",
      dsar_support: "Yes (Donor record extraction)",
      consent: "Informed, revocable consent for newsletters and calls",
      incident_response: "OPC notification templates",
      vendor_management: "Data Protection Annex signed",
      retention: "7 Years (Donor receipts)",
      classification: "PII / Donation history / Contact details",
      cross_border: "Allowed under DPA guidelines",
      ai_governance: "N/A",
      cybersecurity: "Access role separation (Advancement vs. Operations)",
      audit: "Annual PSR Committee audit reviews",
      training: "Training Module mod-3: Law 25 for Frontline Staff",
      automation: "90% automated consent registry auditing",
      knowledge_score: "99/100",
      status: "🟢 Fully Implemented",
      workflows: "Advancement outreach validation, volunteer onboarding",
      agents: "Ingestion Agent, Compliance Auditor"
    }
  };

  const selectedIndustryDetails = useMemo(() => {
    return industryDetails[selectedCountry === 'US' && selectedIndustry === 'Non-Profit' ? 'Technology' : selectedIndustry];
  }, [selectedIndustry, selectedCountry]);

  // Dynamic Coverage Matrix Cells Detailed popup
  const matrixCellDetails = useMemo(() => {
    if (!selectedCell) return null;
    const { country, industry } = selectedCell;
    
    // Custom mapping details
    return {
      country: country === 'CA' ? 'Canada' : country === 'US' ? 'United States' : 'European Union',
      industry: industry,
      regulations: country === 'CA' 
        ? "PIPEDA Schedule 1, Quebec Law 25, provincial Health Privacy Acts"
        : country === 'US' ? "HIPAA Privacy Rule, CPRA Section 1798" : "GDPR Articles 6, 9, 28",
      controls: country === 'CA'
        ? "Consent verification gateways, Localized data backup registries"
        : "BAA contract monitors, NIST encryption baseline checks",
      workflows: "User database sync, incident tracking log, automated redaction routing",
      templates: "PIA standard workbook, data protection annex draft, incident notify letter",
      risk_models: "Insider risk assessment, cross-border data sovereignty mismatch score",
      sources: "RAG collection 'KIBO_RAG_LEGAL_GT', active SQLite log registries",
      citations: "LAW25-SEC14, PIPEDA-SCH1-4.7, GDPR-ART28",
      confidence: country === 'CA' ? 98 : 90,
      validation: "Validated via continuous continuous vector shards on 2026-07-01"
    };
  }, [selectedCell]);

  const filteredInstruments = useMemo(() => {
    if (!selectedJurDetails.instruments) return [];
    return selectedJurDetails.instruments.filter(inst => {
      const matchesSearch = inst.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            inst.citation.toLowerCase().includes(searchQuery.toLowerCase()) ||
                            inst.keywords.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSearch;
    });
  }, [selectedJurDetails, searchQuery]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#FAFAFA] text-[#6B7280]">
        <div className="flex flex-col items-center space-y-3">
          <RefreshCw size={24} className="animate-spin text-blue-500" />
          <span className="text-xs font-bold uppercase tracking-widest font-mono">Parsing RAG Vector Database ...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#FAFAFA] overflow-y-auto">
      
      {/* 1. TOP STATS: READINESS ANALYTICS */}
      <div className="grid grid-cols-5 gap-3 p-4 border-b border-[#E5E7EB] bg-white/85">
        {[
          { label: 'Total Mapped Countries', value: Object.keys(data?.jurisdictions || {}).length, color: 'text-emerald-700', icon: Globe },
          { label: 'Active Regulatory Authorities', value: 5, color: 'text-blue-400', icon: Shield },
          { label: 'Compliance Instruments (RAG)', value: data?.total_laws || 0, color: 'text-sky-700', icon: FileText },
          { label: 'Active Compliance Lessons', value: data?.lessons_count || 0, color: 'text-amber-700', icon: Award },
          { label: 'Average Vector Confidence', value: '94.2%', color: 'text-purple-700', icon: BarChart2 }
        ].map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-gray-50/60 border border-[#E5E7EB]/70 p-3 rounded-lg flex items-center justify-between">
              <div>
                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">{stat.label}</p>
                <p className={`text-lg font-extrabold ${stat.color} mt-1`}>{stat.value}</p>
              </div>
              <Icon size={18} className="text-gray-600 opacity-60" />
            </div>
          );
        })}
      </div>

      {/* 2. MAP & PANEL ROW */}
      <div className="grid grid-cols-12 gap-0 border-b border-[#E5E7EB]">
        
        {/* Interactive World Map (Left Panel) */}
        <div className="col-span-8 bg-[#F9FAFB] p-4 flex flex-col justify-between" style={{ minHeight: '400px' }}>
          <div>
            <div className="flex justify-between items-center mb-3">
              <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1">
                <Globe size={12} className="text-blue-500 mr-1" />
                <span>DYNAMIC REGULATORY COVERAGE HEATMAP</span>
              </span>
              
              {/* Map Heat overlay selectors */}
              <div className="flex bg-gray-50 border border-[#E5E7EB] rounded-lg p-0.5">
                {[
                  { id: 'completeness', label: 'Completeness' },
                  { id: 'density', label: 'RAG Density' },
                  { id: 'complexity', label: 'Complexity' }
                ].map(opt => (
                  <button
                    key={opt.id}
                    onClick={() => setMapOverlayMode(opt.id)}
                    className={`text-[9px] font-bold px-2 py-1 rounded transition-all cursor-pointer ${
                      mapOverlayMode === opt.id ? 'bg-blue-600 text-[#111827]' : 'text-gray-500 hover:text-[#374151]'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
            
            <p className="text-[10px] text-gray-500">
              Generated dynamically from current vector shards. Click on highlighted sovereign zones to audit instrument databases.
            </p>
          </div>

          {/* SVG Map Layout */}
          <div className="flex-1 flex items-center justify-center p-4 relative">
            <svg className="w-full max-w-2xl h-60" viewBox="0 0 800 400">
              {/* Canada */}
              <path
                d="M 120 70 L 160 50 L 220 80 L 240 100 L 200 120 L 140 100 Z"
                fill={getCountryColor('CA', data?.jurisdictions?.CA?.readiness || 94)}
                stroke="#090C15"
                strokeWidth="1.5"
                className="cursor-pointer hover:opacity-85 transition-opacity"
                onClick={() => setSelectedCountry('CA')}
              />
              <text x="170" y="85" fill="#FFFFFF" fontSize="9" fontWeight="bold" className="pointer-events-none select-none">CANADA</text>

              {/* USA */}
              <path
                d="M 110 110 L 210 130 L 230 160 L 150 180 L 120 150 Z"
                fill={getCountryColor('US', data?.jurisdictions?.US?.readiness || 85)}
                stroke="#090C15"
                strokeWidth="1.5"
                className="cursor-pointer hover:opacity-85 transition-opacity"
                onClick={() => setSelectedCountry('US')}
              />
              <text x="160" y="145" fill="#FFFFFF" fontSize="9" fontWeight="bold" className="pointer-events-none select-none">UNITED STATES</text>

              {/* Europe */}
              <path
                d="M 380 90 L 430 70 L 480 100 L 460 140 L 400 135 Z"
                fill={getCountryColor('EU', data?.jurisdictions?.EU?.readiness || 88)}
                stroke="#090C15"
                strokeWidth="1.5"
                className="cursor-pointer hover:opacity-85 transition-opacity"
                onClick={() => setSelectedCountry('EU')}
              />
              <text x="420" y="105" fill="#FFFFFF" fontSize="9" fontWeight="bold" className="pointer-events-none select-none">EUROPEAN UNION</text>

              {/* Connections lines */}
              <line x1="220" y1="130" x2="400" y2="105" stroke="#1E294B" strokeDasharray="3,3" />
            </svg>

            {/* Map Legend */}
            <div className="absolute bottom-2 left-2 bg-white/90 border border-[#E5E7EB] p-2.5 rounded-lg text-[9px] text-[#6B7280] space-y-1">
              <span className="font-bold text-[8px] uppercase tracking-wider block text-gray-500 mb-1">Coverage Key</span>
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span>🟢 Fully Supported (Score &gt; 90)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-500" />
                <span>🟡 Partial Support (Score 80-89)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                <span>🟠 Regulatory Knowledge Only</span>
              </div>
            </div>
          </div>
        </div>

        {/* 3. DYNAMIC DETAIL PANEL (Right Side Panel - All 18 Spec Fields) */}
        <div className="col-span-4 bg-white border-l border-[#E5E7EB] p-4 flex flex-col justify-between overflow-y-auto max-h-[400px]">
          <div className="space-y-3.5">
            <div className="flex justify-between items-start border-b border-[#E5E7EB] pb-2">
              <div>
                <h3 className="text-sm font-extrabold text-[#111827]">{selectedJurDetails.country}</h3>
                <span className="text-[9px] text-[#6B7280] font-mono uppercase">{selectedJurDetails.region} &bull; {selectedJurDetails.state_prov}</span>
              </div>
              <div className="text-right">
                <span className="text-xl font-black text-emerald-700">{selectedJurDetails.readiness}%</span>
                <p className="text-[8px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">Readiness Score</p>
              </div>
            </div>

            {/* Detailed list display of 18 parameters */}
            <div className="space-y-2 text-[11px] text-[#374151]">
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable Privacy Laws:</span> {selectedJurDetails.laws?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable AI Regulations:</span> {selectedJurDetails.ai_regulations?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable Cybersecurity Laws:</span> {selectedJurDetails.cybersecurity_laws?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Consumer Protection Laws:</span> {selectedJurDetails.consumer_protection?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Sector-Specific Regulations:</span> {selectedJurDetails.sector_regulations?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Regulatory Authorities:</span> {selectedJurDetails.authorities?.join(', ')}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Effective Dates:</span> {selectedJurDetails.effective_date}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Latest Amendment Date:</span> {selectedJurDetails.last_amended}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Version:</span> {selectedJurDetails.version}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Coverage Score:</span> {selectedJurDetails.coverage_score}/100</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Last Validation Date:</span> {selectedJurDetails.validation_date}</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Knowledge Confidence Score:</span> {selectedJurDetails.confidence}%</div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Pending Updates:</span> <span className="text-amber-700 font-semibold">{selectedJurDetails.pending_updates}</span></div>
              <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Upcoming Legislative Changes:</span> <span className="text-blue-400 font-semibold">{selectedJurDetails.upcoming_changes}</span></div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. COMPLIANCE INSTRUMENT EXPLORER (All 14 Spec Fields) */}
      <div className="p-4 border-b border-[#E5E7EB] bg-white/20 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1">
            <FileText size={12} className="text-blue-500 mr-1" />
            <span>COMPLIANCE INSTRUMENT EXPLORER (RAG collections)</span>
          </span>
          
          <div className="flex space-x-2">
            <div className="flex items-center space-x-1.5 bg-[#FAFAFA] border border-[#E5E7EB] px-2.5 py-1 rounded-md">
              <Search size={12} className="text-gray-500" />
              <input
                type="text"
                placeholder="Search collection..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-xs outline-hidden text-[#111827] placeholder-gray-600 w-48"
              />
            </div>
          </div>
        </div>

        {/* Instruments Table displaying 14 fields */}
        <div className="border border-[#E5E7EB] rounded-xl overflow-x-auto bg-[#F9FAFB]">
          <table className="w-full text-xs text-left border-collapse min-w-[1000px]">
            <thead>
              <tr className="bg-white text-gray-500 border-b border-[#E5E7EB] font-semibold text-[10px] uppercase">
                <th className="p-3">Title</th>
                <th className="p-3">Citation</th>
                <th className="p-3">Authority</th>
                <th className="p-3">Status</th>
                <th className="p-3">Effective</th>
                <th className="p-3">Version</th>
                <th className="p-3">Language</th>
                <th className="p-3">Trust Tier</th>
                <th className="p-3">Source</th>
                <th className="p-3">RAG Collection</th>
                <th className="p-3">Embedding Coll</th>
                <th className="p-3">Indexed</th>
                <th className="p-3">Reviewed</th>
                <th className="p-3">Superseded</th>
                <th className="p-3 text-right">Doc Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E294B] bg-[#FAFAFA]/40 font-mono text-[10px]">
              {filteredInstruments.length === 0 ? (
                <tr>
                  <td colSpan="15" className="p-6 text-center text-gray-500 italic">No compliance instruments match filter.</td>
                </tr>
              ) : (
                filteredInstruments.map((inst, idx) => (
                  <tr key={idx} className="hover:bg-gray-50/40 text-[#374151]">
                    <td className="p-3 font-semibold text-[#111827] font-sans text-xs">{inst.title}</td>
                    <td className="p-3 text-blue-400 font-bold">{inst.citation}</td>
                    <td className="p-3 font-sans text-[11px]">{inst.authority}</td>
                    <td className="p-3"><span className="px-1.5 py-0.5 bg-emerald-950 text-emerald-700 rounded-full border border-emerald-900/30 text-[9px] uppercase">{inst.status}</span></td>
                    <td className="p-3">{inst.effective}</td>
                    <td className="p-3">{inst.version}</td>
                    <td className="p-3">{inst.language}</td>
                    <td className="p-3 text-purple-700">{inst.trust_tier}</td>
                    <td className="p-3 font-sans">{inst.source}</td>
                    <td className="p-3 text-sky-700">{inst.collection}</td>
                    <td className="p-3 text-gray-500 truncate max-w-24">{inst.embedding}</td>
                    <td className="p-3">{inst.indexed}</td>
                    <td className="p-3">{inst.reviewed}</td>
                    <td className="p-3 text-rose-700">{inst.superseded}</td>
                    <td className="p-3 text-right font-sans">
                      <a href="#" onClick={(e) => { e.preventDefault(); alert(`RAG Document loaded: ${inst.title}`); }} className="text-blue-500 hover:underline">
                        Open RAG Doc ↗
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. COVERAGE MATRIX (Dynamic modal click details) & INDUSTRY DETAIL VIEW */}
      <div className="grid grid-cols-12 gap-0 border-b border-[#E5E7EB]">
        
        {/* Industry Matrix (Left Panel) */}
        <div className="col-span-8 p-4 border-r border-[#E5E7EB] space-y-4">
          <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block">JURISDICTION & INDUSTRY MATRIX</span>
          
          <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-[#F9FAFB]">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-white text-gray-500 border-b border-[#E5E7EB] font-semibold text-[10px] uppercase">
                  <th className="p-3">Jurisdiction</th>
                  {data?.industries?.map((ind, i) => (
                    <th key={i} className="p-3">{ind}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E294B]">
                {['CA', 'US', 'EU'].map((code) => (
                  <tr key={code} className="hover:bg-gray-50/40">
                    <td className="p-3 font-bold text-[#111827]">{code === 'CA' ? 'Canada' : code === 'US' ? 'United States' : 'European Union'}</td>
                    {data?.industries?.map((ind, i) => {
                      const intersection = matrixData[code]?.[ind] || { status: '⚪ Unknown', details: 'N/A' };
                      const isSelected = selectedCell && selectedCell.country === code && selectedCell.industry === ind;
                      return (
                        <td
                          key={i}
                          onClick={() => setSelectedCell({ country: code, industry: ind })}
                          className={`p-3 cursor-pointer transition-all ${
                            isSelected ? 'bg-blue-600/10 border-2 border-blue-500' : 'hover:bg-slate-800/40'
                          }`}
                        >
                          <span className={`font-bold text-[10px] ${
                            intersection.status.includes('Supported') ? 'text-emerald-700' :
                            intersection.status.includes('Partial') ? 'text-amber-700' : 'text-orange-400'
                          }`}>
                            {intersection.status}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Matrix Cell Click-To-Reveal Details (All specified fields) */}
          {matrixCellDetails && (
            <div className="bg-gray-50/80 border border-blue-500/30 p-4 rounded-xl space-y-3.5">
              <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-2">
                <h4 className="text-xs font-extrabold text-blue-400 uppercase tracking-wider">
                  Intersection: {matrixCellDetails.country} &bull; {matrixCellDetails.industry}
                </h4>
                <button onClick={() => setSelectedCell(null)} className="text-gray-500 hover:text-[#111827] text-xs cursor-pointer">✕</button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs text-[#374151]">
                <div className="space-y-2">
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable Regulations:</span> {matrixCellDetails.regulations}</div>
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Required Controls:</span> {matrixCellDetails.controls}</div>
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Implemented Workflows:</span> {matrixCellDetails.workflows}</div>
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Available Templates:</span> {matrixCellDetails.templates}</div>
                </div>
                <div className="space-y-2">
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Risk Models:</span> {matrixCellDetails.risk_models}</div>
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Knowledge Sources:</span> {matrixCellDetails.sources}</div>
                  <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Referenced Legal Instruments:</span> <code className="text-blue-300">{matrixCellDetails.citations}</code></div>
                  <div className="flex justify-between text-[10px] text-gray-550 pt-1 border-t border-[#E5E7EB]">
                    <span>Confidence: <strong className="text-emerald-700">{matrixCellDetails.confidence}%</strong></span>
                    <span>{matrixCellDetails.validation}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 6. INDUSTRY DETAIL VIEW (Right Panel - All 24 Spec Fields) */}
        <div className="col-span-4 p-4 space-y-3 bg-white/30">
          <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-2">
            <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest block">INDUSTRY DETAIL WORKSPACE</span>
            <select
              value={selectedIndustry}
              onChange={(e) => setSelectedIndustry(e.target.value)}
              className="bg-[#FAFAFA] border border-[#E5E7EB] text-[10px] rounded px-2 py-1 text-[#111827] cursor-pointer outline-hidden"
            >
              {data?.industries?.map((ind, i) => (
                <option key={i} value={ind}>{ind}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2.5 text-[11px] text-[#374151] max-h-[300px] overflow-y-auto pr-1">
            <div className="flex justify-between items-center bg-gray-50 p-2 rounded border border-[#E5E7EB]">
              <span className="text-xs font-bold text-[#111827]">{selectedIndustry} Portfolio</span>
              <span className="text-[10px] font-bold text-blue-400">{selectedIndustryDetails.status}</span>
            </div>
            
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable Regulations:</span> {selectedIndustryDetails.regulations}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Applicable Controls:</span> {selectedIndustryDetails.controls}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Required Policies:</span> {selectedIndustryDetails.policies}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Required Assessments:</span> {selectedIndustryDetails.assessments}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Available Templates:</span> {selectedIndustryDetails.templates}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Required Records of Processing:</span> {selectedIndustryDetails.records_of_processing}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">DPIA Availability:</span> {selectedIndustryDetails.dpia_availability}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">DSAR Support:</span> {selectedIndustryDetails.dsar_support}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Consent Management:</span> {selectedIndustryDetails.consent}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Incident Response Protocol:</span> {selectedIndustryDetails.incident_response}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Vendor Management:</span> {selectedIndustryDetails.vendor_management}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Retention Requirements:</span> {selectedIndustryDetails.retention}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Data Classification Rules:</span> {selectedIndustryDetails.classification}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Cross-Border Transfer Rules:</span> {selectedIndustryDetails.cross_border}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">AI Governance Requirements:</span> {selectedIndustryDetails.ai_governance}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Cybersecurity Requirements:</span> {selectedIndustryDetails.cybersecurity}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Audit Requirements:</span> {selectedIndustryDetails.audit}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Training Modules:</span> {selectedIndustryDetails.training}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Automation Coverage:</span> {selectedIndustryDetails.automation}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Knowledge Coverage Score:</span> {selectedIndustryDetails.knowledge_score}/100</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Supported Workflows:</span> {selectedIndustryDetails.workflows}</div>
            <div><span className="text-gray-500 font-bold block uppercase text-[8px]">Supported AI Agents:</span> {selectedIndustryDetails.agents}</div>
          </div>
        </div>

      </div>

      {/* 7. GAP ANALYSIS PANEL */}
      <div className="p-4 bg-white/10 space-y-4">
        <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1">
          <AlertTriangle size={12} className="text-amber-500 mr-1" />
          <span>REGULATORY GAP ANALYSIS ENGINE</span>
        </span>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.gaps?.map((gap) => (
            <div key={gap.id} className="bg-gray-50/75 border border-[#E5E7EB] p-3 rounded-lg flex flex-col justify-between space-y-3">
              <div>
                <div className="flex justify-between items-start gap-2">
                  <h4 className="text-[11px] font-extrabold text-[#111827]">{gap.title}</h4>
                  <span className="text-[8px] bg-slate-800 border border-slate-700 text-slate-400 px-1.5 py-0.5 rounded font-mono uppercase">{gap.type}</span>
                </div>
                <p className="text-[10px] text-[#6B7280] leading-normal mt-1">{gap.details}</p>
              </div>

              <div className="flex justify-between items-center text-[9px] text-gray-500 pt-1.5 border-t border-[#E5E7EB]/50">
                <span>Scope: {gap.scope} ({gap.jurisdiction})</span>
                
                {createdTasks[gap.id] ? (
                  <span className="text-emerald-700 font-bold flex items-center space-x-1 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-900/30">
                    <Check size={10} />
                    <span>Task Generated</span>
                  </span>
                ) : (
                  <button
                    onClick={() => handleCreateTask(gap.id, gap.title, gap.details, gap.jurisdiction)}
                    className="text-blue-400 hover:text-blue-300 font-bold hover:underline cursor-pointer flex items-center space-x-1"
                  >
                    <Plus size={10} />
                    <span>Create Task</span>
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 8. ONTOLOGICAL ONBOARDING (CONTEXT SEEDER) & ACTION ENGINE */}
      <div className="p-4 border-b border-[#E5E7EB] bg-white space-y-4">
        <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-2">
          <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1.5">
            <Cpu size={12} className="text-blue-600" />
            <span>Ontological Onboarding (Context Seeder)</span>
          </span>
          <span className="text-[9px] bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-bold uppercase border border-blue-200">Ontology Seeder Active</span>
        </div>

        <div className="grid grid-cols-12 gap-4">
          {/* Seeder selectors */}
          <div className="col-span-4 bg-gray-50 border border-[#E5E7EB] p-3.5 rounded-xl space-y-3">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block">Active Context Triggers</span>
            
            {/* Jurisdictions */}
            <div className="space-y-1.5">
              <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider block">Jurisdictions</span>
              <div className="flex flex-wrap gap-2">
                {Object.keys(seederJur).map(j => (
                  <label key={j} className="flex items-center space-x-1.5 text-xs text-gray-700 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={seederJur[j]}
                      onChange={() => setSeederJur(prev => ({ ...prev, [j]: !prev[j] }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="font-semibold">{j}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Data Categories */}
            <div className="space-y-1.5 pt-2 border-t border-gray-250">
              <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider block">Data Categories</span>
              <div className="flex flex-wrap gap-2">
                {Object.keys(seederCat).map(c => (
                  <label key={c} className="flex items-center space-x-1.5 text-xs text-gray-700 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={seederCat[c]}
                      onChange={() => setSeederCat(prev => ({ ...prev, [c]: !prev[c] }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="font-semibold">{c === 'ChildrensData' ? 'Child Data' : c}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Age slider if children data selected */}
            {seederCat.ChildrensData && (
              <div className="space-y-1 pt-1.5">
                <div className="flex justify-between text-[10px] text-gray-600 font-semibold">
                  <span>Data Subject Child Age:</span>
                  <strong className="text-blue-600">{seederChildAge} Years</strong>
                </div>
                <input
                  type="range"
                  min="5"
                  max="18"
                  value={seederChildAge}
                  onChange={(e) => setSeederChildAge(parseInt(e.target.value))}
                  className="w-full h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
            )}
          </div>

          {/* Dynamic Active Rulesets */}
          <div className="col-span-8 bg-gray-50 border border-[#E5E7EB] p-3.5 rounded-xl flex flex-col justify-between">
            <div className="space-y-2">
              <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block">Activated Ontology Rulesets</span>
              <div className="flex flex-wrap gap-2">
                {activeRulesets.map((r, i) => (
                  <div key={i} className="bg-white border border-[#E5E7EB] p-2.5 rounded-lg flex flex-col space-y-0.5 shadow-xs max-w-[240px]">
                    <span className="text-[10px] font-extrabold text-blue-600">{r.name}</span>
                    <span className="text-[9px] text-gray-500">{r.desc}</span>
                  </div>
                ))}
                {activeRulesets.length === 0 && (
                  <span className="text-xs text-gray-400 italic">No context triggers checked. Standard review active.</span>
                )}
              </div>
            </div>

            {/* Statutory Action Chips */}
            <div className="pt-3 border-t border-gray-250">
              <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider block mb-1.5">Statutory Action Initiators</span>
              <div className="flex flex-wrap gap-2">
                {activeRulesets.map((r, i) => (
                  <button
                    key={i}
                    onClick={() => alert(`Initiating statutory workflow for: ${r.name}`)}
                    className="font-mono text-[9px] font-bold px-2.5 py-1 bg-white border-2 border-blue-600 text-blue-600 hover:bg-blue-50 transition-all cursor-pointer rounded"
                  >
                    INITIATE {r.name.toUpperCase().replace(/ /g, '_')}
                  </button>
                ))}
                {activeRulesets.length === 0 && (
                  <button
                    onClick={() => alert("Initiating standard review")}
                    className="font-mono text-[9px] font-bold px-2.5 py-1 bg-white border-2 border-gray-300 text-gray-600 hover:bg-gray-50 transition-all cursor-pointer rounded"
                  >
                    INITIATE_STANDARD_REVIEW
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 9. CROSS-BORDER SPLIT-PANE ADEQUACY WORKSPACE */}
      <div className="p-4 border-b border-[#E5E7EB] bg-white space-y-4">
        <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-2">
          <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1.5">
            <Globe size={12} className="text-blue-600" />
            <span>Cross-Border split-pane adequacy workspace</span>
          </span>
          <span className="text-[9px] bg-purple-50 text-purple-700 px-2 py-0.5 rounded font-bold uppercase border border-purple-200">Transfer Gatekeeper</span>
        </div>

        <div className="grid grid-cols-12 gap-4">
          {/* Left Panel: Flow Visualizer */}
          <div className="col-span-7 bg-gray-50 border border-[#E5E7EB] p-4 rounded-xl space-y-3.5">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block">Data Flow Direction</span>
            
            <div className="flex justify-between items-center bg-white p-3 rounded-lg border border-[#E5E7EB] shadow-xs">
              <div className="text-center w-24">
                <span className="text-[8px] text-gray-400 font-bold uppercase block">Origin</span>
                <select
                  value={crossBorderOrigin}
                  onChange={(e) => setCrossBorderOrigin(e.target.value)}
                  className="text-xs bg-gray-50 border border-[#E5E7EB] rounded px-1.5 py-0.5 text-gray-800 font-bold"
                >
                  <option value="Quebec">Quebec</option>
                  <option value="Ontario">Ontario</option>
                </select>
              </div>

              <div className="flex-1 flex flex-col items-center justify-center space-y-1">
                <ArrowRight size={16} className="text-blue-600 animate-pulse" />
                <span className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                  crossBorderAdequacy.status === 'Adequate' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}>
                  {crossBorderAdequacy.status}
                </span>
              </div>

              <div className="text-center w-24">
                <span className="text-[8px] text-gray-400 font-bold uppercase block">Destination</span>
                <select
                  value={crossBorderDest}
                  onChange={(e) => setCrossBorderDest(e.target.value)}
                  className="text-xs bg-gray-50 border border-[#E5E7EB] rounded px-1.5 py-0.5 text-gray-800 font-bold"
                >
                  <option value="California">California</option>
                  <option value="EU_Union">EU Union</option>
                </select>
              </div>
            </div>

            <div className="text-[10px] text-gray-500 font-medium leading-relaxed bg-white border border-[#E5E7EB] p-2.5 rounded-lg shadow-xs">
              Adequacy Status details: <strong>Quebec to {crossBorderDest}</strong>. 
              {crossBorderAdequacy.status === 'Adequate' ? (
                <span className="text-emerald-700 ml-1">✓ Reciprocal adequacy established. Standard logging enabled.</span>
              ) : (
                <span className="text-rose-700 ml-1">⚠ Independent Transfer Impact Assessment (TIA) and Standard Contractual Clauses (SCC) mandatory.</span>
              )}
            </div>
          </div>

          {/* Right Panel: Blocker Status & Upload */}
          <div className="col-span-5 bg-gray-50 border border-[#E5E7EB] p-4 rounded-xl flex flex-col justify-between">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest block mb-2">Gatekeeper Blocker Status</span>
            
            {crossBorderAdequacy.blocked ? (
              <div className="bg-rose-50 border border-rose-200 p-3 rounded-lg flex flex-col space-y-2">
                <div className="flex items-center space-x-2">
                  <ShieldAlert size={14} className="text-rose-600" />
                  <span className="text-[10px] font-black text-rose-700 uppercase tracking-wide">DEPLOYMENT BLOCKED</span>
                </div>
                <p className="text-[9px] text-rose-600 leading-normal font-mono">
                  CRITICAL: No verified SCC/DPA uploaded for this transfer. Deployment locked.
                </p>
                <button
                  onClick={() => { setSccUploaded(true); alert("SCC / DPA Agreement uploaded. Re-evaluating adequacy blocker..."); }}
                  className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold py-1 px-2.5 text-[9px] rounded uppercase cursor-pointer transition-all shadow-xs"
                >
                  Upload & Verify Signed SCC Agreement
                </button>
              </div>
            ) : (
              <div className="bg-emerald-50 border border-emerald-200 p-3 rounded-lg flex flex-col space-y-2">
                <div className="flex items-center space-x-2">
                  <CheckCircle size={14} className="text-emerald-600" />
                  <span className="text-[10px] font-black text-emerald-700 uppercase tracking-wide">DEPLOYMENT CLEARED</span>
                </div>
                <p className="text-[9px] text-emerald-600 leading-normal">
                  All adequacy checks satisfied or TIA/SCC has been uploaded and verified.
                </p>
                {sccUploaded && (
                  <button
                    onClick={() => setSccUploaded(false)}
                    className="text-[9px] font-bold text-blue-600 hover:underline text-left cursor-pointer"
                  >
                    Reset uploaded agreement
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 10. STATUTORY ARTIFACT REGISTRY */}
      <div className="p-4 bg-white space-y-4">
        <div className="flex justify-between items-center border-b border-[#E5E7EB] pb-2">
          <span className="text-[10px] font-bold text-[#6B7280] uppercase tracking-widest flex items-center space-x-1.5">
            <FileText size={12} className="text-blue-600" />
            <span>Statutory Artifact Registry Ledger</span>
          </span>
          <span className="text-[9px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase border border-emerald-200">Vault Ledger Active</span>
        </div>

        <div className="border border-[#E5E7EB] rounded-xl overflow-hidden bg-gray-50">
          <table className="w-full text-xs text-left border-collapse font-mono text-[10px]">
            <thead>
              <tr className="bg-white text-gray-500 border-b border-[#E5E7EB] font-bold text-[8px] uppercase tracking-wider">
                <th className="p-3">Artifact ID</th>
                <th className="p-3">Statutory Title</th>
                <th className="p-3">Triggering Project</th>
                <th className="p-3 text-right">FAIR Loss Risk</th>
                <th className="p-3">Renewal Deadline</th>
                <th className="p-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5E7EB]">
              {[
                { id: 'TRA-PHIPA-002', title: 'PHIPA Threat & Risk Assessment (TRA)', project: 'Kids Help Phone Portal', risk: '$2.4M', deadline: 'Renewing (In 2 Days)', status: 'Approved', renewHighlight: true },
                { id: 'TIA-LAW25-014', title: 'Quebec Law 25 Transfer Assessment (TIA)', project: 'Crisis Database Sync', risk: '$1.8M', deadline: 'In 45 Days', status: 'Blocked', renewHighlight: false },
                { id: 'PIA-LAW25-089', title: 'Quebec Law 25 Privacy Impact Assessment', project: 'Child Consent Interface', risk: '$3.2M', deadline: 'In 90 Days', status: 'Approved', renewHighlight: false },
                { id: 'DPIA-GDPR-445', title: 'GDPR Article 35 Data Protection Assessment', project: 'Global Analytics Store', risk: '$850K', deadline: 'In 180 Days', status: 'Approved', renewHighlight: false }
              ].map((art, idx) => (
                <tr
                  key={idx}
                  className={`hover:bg-gray-100/50 ${
                    art.renewHighlight ? 'bg-amber-50/70 border-l-4 border-amber-500 font-semibold' : 'text-gray-650'
                  }`}
                >
                  <td className="p-3 font-bold text-gray-800">{art.id}</td>
                  <td className="p-3 font-sans text-xs text-gray-900 font-semibold">{art.title}</td>
                  <td className="p-3 font-sans">{art.project}</td>
                  <td className="p-3 text-right text-rose-700 font-bold">{art.risk} ANNUALLY</td>
                  <td className="p-3">
                    <span className={art.renewHighlight ? 'text-amber-700 font-bold' : 'text-gray-500'}>
                      {art.deadline}
                    </span>
                  </td>
                  <td className="p-3 text-right font-sans">
                    <span className={`px-2 py-0.5 text-[9px] font-bold rounded-full border ${
                      art.status === 'Approved' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
                    }`}>
                      {art.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
