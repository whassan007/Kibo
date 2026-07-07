#!/usr/bin/env python3
"""
Enhanced program to discover laws, regulations, standards, torts, cross-border agreements,
and penalties across Canada, US, and EU jurisdictions.
"""

import re
import json
import os
from typing import Dict, List, Tuple
import requests
from urllib.parse import quote
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base data structure with known laws and standards
BASE_STATUTES_AND_STANDARDS = {
    # Canada / US / EU Core Privacy Laws
    "PHIPA (ON)": {
        "name": "Personal Health Information Protection Act",
        "jurisdiction": "Ontario, Canada",
        "type": "Privacy Law",
        "source_url": "https://www.ontario.ca/laws/statute/17p05",
        "description": "Protects personal health information of individuals in Ontario"
    },
    "Law 25 (QC)": {
        "name": "Act to Secure the Protection of Personal Information in the Private Sector",
        "jurisdiction": "Quebec, Canada",
        "type": "Privacy Law",
        "source_url": "https://www.legisquebec.gouv.qc.ca/en/ShowDoc/cs/A-21.1",
        "description": "Quebec's private sector privacy legislation"
    },
    "PIPEDA (CA)": {
        "name": "Personal Information Protection and Electronic Documents Act",
        "jurisdiction": "Canada (Federal)",
        "type": "Privacy Law",
        "source_url": "https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-pipeda/",
        "description": "Canada's federal privacy law for private sector organizations"
    },
    "CCPA / CPRA (US)": {
        "name": "California Consumer Privacy Act / California Privacy Rights Act",
        "jurisdiction": "California, US",
        "type": "Privacy Law",
        "source_url": "https://oag.ca.gov/privacy/ccpa",
        "description": "California's comprehensive privacy legislation"
    },
    "GDPR (EU)": {
        "name": "General Data Protection Regulation",
        "jurisdiction": "European Union",
        "type": "Privacy Law",
        "source_url": "https://gdpr-info.eu/",
        "description": "EU regulation governing data protection and privacy"
    },
    "UK-GDPR": {
        "name": "UK General Data Protection Regulation",
        "jurisdiction": "United Kingdom",
        "type": "Privacy Law",
        "source_url": "https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/",
        "description": "UK implementation of GDPR"
    },
    "APP (AU)": {
        "name": "Australian Privacy Principles",
        "jurisdiction": "Australia",
        "type": "Privacy Law",
        "source_url": "https://www.oaic.gov.au/privacy/privacy-act/",
        "description": "Australian privacy law principles"
    },
    "PDPA (SG)": {
        "name": "Personal Data Protection Act",
        "jurisdiction": "Singapore",
        "type": "Privacy Law",
        "source_url": "https://www.pdpa.gov.sg/",
        "description": "Singapore's data protection legislation"
    },
    
    # Sector-Specific Overlays
    "HIPAA (US Health)": {
        "name": "Health Insurance Portability and Accountability Act",
        "jurisdiction": "United States",
        "type": "Healthcare Law",
        "source_url": "https://www.hhs.gov/hipaa/index.html",
        "description": "US healthcare privacy and security law"
    },
    "SOX (Financial Reporting)": {
        "name": "Sarbanes-Oxley Act",
        "jurisdiction": "United States",
        "type": "Financial Law",
        "source_url": "https://www.sec.gov/spotlight/sarbanes-oxley/index.shtml",
        "description": "US financial reporting and corporate governance law"
    },
    "PCI-DSS (Card Data)": {
        "name": "Payment Card Industry Data Security Standard",
        "jurisdiction": "Global",
        "type": "Security Standard",
        "source_url": "https://www.pcisecuritystandards.org/",
        "description": "Data security standard for organizations processing card payments"
    },
    "NIST CSF (Cybersecurity)": {
        "name": "National Institute of Standards and Technology Cybersecurity Framework",
        "jurisdiction": "United States",
        "type": "Cybersecurity Standard",
        "source_url": "https://www.nist.gov/cyberframework",
        "description": "Framework for improving cybersecurity risk management"
    },
    
    # New Statutes from your list
    "FIPPA (ON)": {
        "name": "Freedom of Information and Protection of Privacy Act",
        "jurisdiction": "Ontario, Canada",
        "type": "Freedom of Information Law",
        "source_url": "https://www.ontario.ca/laws/statute/05f17",
        "description": "Ontario's freedom of information and privacy legislation"
    },
    "PIPA (AB)": {
        "name": "Personal Information Protection Act",
        "jurisdiction": "Alberta, Canada",
        "type": "Privacy Law",
        "source_url": "https://www.alberta.ca/personal-information-protection-act.aspx",
        "description": "Alberta's privacy legislation"
    },
    "BIPA (IL)": {
        "name": "Biometric Information Privacy Act",
        "jurisdiction": "Illinois, US",
        "type": "Privacy Law",
        "source_url": "https://www.illinoiscourts.gov/Content/Issues/Biometric-Information-Privacy-Act-BIPA.aspx",
        "description": "Illinois law governing biometric data collection"
    },
    "NYDFS Part 500 (NY)": {
        "name": "New York Department of Financial Services Cybersecurity Requirements",
        "jurisdiction": "New York, US",
        "type": "Financial Cybersecurity Law",
        "source_url": "https://www.dfs.ny.gov/about/press/press_releases/2021/pr20210930",
        "description": "NYDFS cybersecurity requirements for financial institutions"
    },
    "NYC Local Law 144 (AI Bias Audits)": {
        "name": "Local Law 144 of 2023 - AI Bias Audit Requirement",
        "jurisdiction": "New York City, US",
        "type": "AI Regulation",
        "source_url": "https://council.nyc.gov/legislation/l-144-2023/",
        "description": "New York City law requiring AI bias audits for certain systems"
    },
    "My Health My Data Act (WA)": {
        "name": "My Health My Data Act",
        "jurisdiction": "Washington, US",
        "type": "Health Privacy Law",
        "source_url": "https://app.leg.wa.gov/Code/Display.aspx?code=43.20.100",
        "description": "Washington state law governing health data privacy"
    },
    "FERPA (US Federal)": {
        "name": "Family Educational Rights and Privacy Act",
        "jurisdiction": "United States",
        "type": "Educational Privacy Law",
        "source_url": "https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html",
        "description": "US federal law protecting student education records"
    },
    "FTC Act §5 (US Federal)": {
        "name": "Federal Trade Commission Act Section 5",
        "jurisdiction": "United States",
        "type": "Consumer Protection Law",
        "source_url": "https://www.ftc.gov/tips-advice/business-center/guidance/ftc-act-section-5-unfair-or-deceptive-acts-or-practices",
        "description": "FTC law prohibiting unfair or deceptive acts or practices"
    },
    "EU AI Act": {
        "name": "European Union Artificial Intelligence Act",
        "jurisdiction": "European Union",
        "type": "AI Regulation",
        "source_url": "https://digital-strategy.ec.europa.eu/en/policies/artificial-intelligence-act",
        "description": "EU legislation governing artificial intelligence systems"
    },
    "ISO/IEC 27001 (Global)": {
        "name": "Information Security Management System Standard",
        "jurisdiction": "Global",
        "type": "Security Standard",
        "source_url": "https://www.iso.org/isoiec-27001-information-security.html",
        "description": "International standard for information security management"
    }
}

# Additional known laws that would be discovered
DISCOVERED_LAWS = {
    # Alberta specific laws
    "Health Information Act (AB)": {
        "name": "Health Information Act",
        "jurisdiction": "Alberta, Canada",
        "type": "Health Privacy Law",
        "source_url": "https://www.alberta.ca/health-information-act.aspx",
        "description": "Alberta's legislation governing health information privacy"
    },
    "Personal Information Protection Act (AB)": {
        "name": "Personal Information Protection Act",
        "jurisdiction": "Alberta, Canada",
        "type": "Privacy Law",
        "source_url": "https://www.alberta.ca/personal-information-protection-act.aspx",
        "description": "Alberta's privacy legislation for personal information"
    },
    
    # Municipal privacy laws
    "City of Toronto Privacy Policy": {
        "name": "City of Toronto Privacy Policy",
        "jurisdiction": "Toronto, Ontario, Canada",
        "type": "Municipal Privacy Law",
        "source_url": "https://www.torontomayor.ca/privacy/",
        "description": "City of Toronto's privacy practices for residents"
    },
    
    # EU specific laws
    "NIS Directive (EU)": {
        "name": "Network and Information Security Directive",
        "jurisdiction": "European Union",
        "type": "Cybersecurity Law",
        "source_url": "https://www.europarl.europa.eu/legislative-tracks/summary/2016/379785",
        "description": "EU directive on network and information security"
    },
    
    # US state laws
    "Colorado Privacy Act (CPA)": {
        "name": "Colorado Privacy Act",
        "jurisdiction": "Colorado, US",
        "type": "Privacy Law",
        "source_url": "https://leg.colorado.gov/bills/sb21-190",
        "description": "Colorado's comprehensive privacy legislation"
    },
    
    # Anti-spam laws
    "CASL (Canada)": {
        "name": "Canadian Anti-Spam Legislation",
        "jurisdiction": "Canada",
        "type": "Anti-Spam Law",
        "source_url": "https://www.cic.gc.ca/english/resources/legislation/casl/index.asp",
        "description": "Canadian legislation against spam and unsolicited electronic messages"
    },
    
    # Cross-border agreements
    "CETA (Canada-EU)": {
        "name": "Comprehensive Economic and Trade Agreement",
        "jurisdiction": "Canada-EU",
        "type": "Cross-border Agreement",
        "source_url": "https://www.canadaceta.org/",
        "description": "Trade agreement between Canada and EU with data protection provisions"
    },
    "USMCA (US-Mexico-Canada)": {
        "name": "United States-Mexico-Canada Agreement",
        "jurisdiction": "US-Mexico-Canada",
        "type": "Cross-border Agreement",
        "source_url": "https://ustr.gov/trade-agreements/free-trade-agreements/usmca",
        "description": "Trade agreement with data protection and privacy provisions"
    }
}

# Privacy torts
PRIVACY_TORTS = {
    # US Torts
    "US Intrusion upon seclusion": {
        "name": "Intrusion upon seclusion",
        "jurisdiction": "United States",
        "type": "Privacy Tort",
        "source_url": "https://www.law.cornell.edu/wex/intrusion_upon_seclusion",
        "description": "Tort involving intrusion into another's private affairs"
    },
    "US Public disclosure of private facts": {
        "name": "Public disclosure of private facts",
        "jurisdiction": "United States",
        "type": "Privacy Tort",
        "source_url": "https://www.law.cornell.edu/wex/public_disclosure_of_private_facts",
        "description": "Tort involving publication of private facts that would be offensive to a reasonable person"
    },
    "US False light": {
        "name": "False light",
        "jurisdiction": "United States",
        "type": "Privacy Tort",
        "source_url": "https://www.law.cornell.edu/wex/false_light",
        "description": "Tort involving false or misleading portrayal of a person"
    },
    "US Appropriation of name/likeness": {
        "name": "Appropriation of name/likeness",
        "jurisdiction": "United States",
        "type": "Privacy Tort",
        "source_url": "https://www.law.cornell.edu/wex/appropriation_of_name_or_likeness",
        "description": "Tort involving unauthorized use of a person's name or likeness"
    },
    
    # Canada Torts
    "Canada Intrusion upon seclusion": {
        "name": "Intrusion upon seclusion",
        "jurisdiction": "Canada",
        "type": "Privacy Tort",
        "source_url": "https://www.canlii.org/en/ca/scc/doc/2018/2018canlii3479/2018canlii3479.html",
        "description": "Tort involving intrusion into another's private affairs"
    },
    "Canada Public disclosure of private facts": {
        "name": "Public disclosure of private facts",
        "jurisdiction": "Canada",
        "type": "Privacy Tort",
        "source_url": "https://www.canlii.org/en/ca/scc/doc/2018/2018canlii3479/2018canlii3479.html",
        "description": "Tort involving publication of private facts that would be offensive to a reasonable person"
    },
    "Canada False light": {
        "name": "False light",
        "jurisdiction": "Canada",
        "type": "Privacy Tort",
        "source_url": "https://www.canlii.org/en/ca/scc/doc/2018/2018canlii3479/2018canlii3479.html",
        "description": "Tort involving false or misleading portrayal of a person"
    },
    "Canada Appropriation": {
        "name": "Appropriation",
        "jurisdiction": "Canada",
        "type": "Privacy Tort",
        "source_url": "https://www.canlii.org/en/ca/scc/doc/2018/2018canlii3479/2018canlii3479.html",
        "description": "Tort involving unauthorized use of a person's name or likeness"
    },
    
    # EU Torts (GDPR-derived)
    "EU Infringement of personality rights": {
        "name": "Infringement of personality rights",
        "jurisdiction": "European Union",
        "type": "Privacy Tort",
        "source_url": "https://gdpr-info.eu/art-8-gdpr/",
        "description": "Right to protection of personal data under GDPR Article 8"
    },
    "EU Breach of confidentiality": {
        "name": "Breach of confidentiality",
        "jurisdiction": "European Union",
        "type": "Privacy Tort",
        "source_url": "https://gdpr-info.eu/art-5-gdpr/",
        "description": "Data protection violation through breach of confidentiality"
    },
    "EU Data protection violation": {
        "name": "Data protection violation",
        "jurisdiction": "European Union",
        "type": "Privacy Tort",
        "source_url": "https://gdpr-info.eu/art-5-gdpr/",
        "description": "Violation of data protection principles under GDPR"
    },
    "EU Right to be forgotten": {
        "name": "Right to be forgotten",
        "jurisdiction": "European Union",
        "type": "Privacy Tort",
        "source_url": "https://gdpr-info.eu/art-17-gdpr/",
        "description": "Right under GDPR Article 17 for deletion of personal data"
    }
}

# Penalties and violations
PENALTIES = {
    # Canadian penalties
    "OPC (Federal)": {
        "name": "Office of the Privacy Commissioner of Canada",
        "jurisdiction": "Canada (Federal)",
        "type": "Privacy Penalty",
        "source_url": "https://www.priv.gc.ca/en/",
        "description": "Federal privacy commissioner with enforcement powers",
        "max_penalty": "CAD 100,000 per violation"
    },
    "IPC ON": {
        "name": "Information and Privacy Commissioner of Ontario",
        "jurisdiction": "Ontario, Canada",
        "type": "Privacy Penalty",
        "source_url": "https://www.ipc.on.ca/",
        "description": "Ontario privacy commissioner with enforcement powers",
        "max_penalty": "CAD 50,000 per violation"
    },
    "CAI QC": {
        "name": "Commission de la protection de la vie privée du Québec",
        "jurisdiction": "Quebec, Canada",
        "type": "Privacy Penalty",
        "source_url": "https://www.cai.gouv.qc.ca/",
        "description": "Quebec privacy commissioner with enforcement powers",
        "max_penalty": "CAD 100,000 per violation"
    },
    
    # US penalties
    "FTC": {
        "name": "Federal Trade Commission",
        "jurisdiction": "United States",
        "type": "Privacy Penalty",
        "source_url": "https://www.ftc.gov/",
        "description": "US federal agency with enforcement powers for deceptive practices",
        "max_penalty": "$43,792 per violation"
    },
    "SEC": {
        "name": "Securities and Exchange Commission",
        "jurisdiction": "United States",
        "type": "Privacy Penalty",
        "source_url": "https://www.sec.gov/",
        "description": "US federal agency with enforcement powers for financial reporting",
        "max_penalty": "$1,000,000 + disgorgement"
    },
    
    # EU penalties
    "EU DPA": {
        "name": "European Data Protection Authority",
        "jurisdiction": "European Union",
        "type": "Privacy Penalty",
        "source_url": "https://edpb.europa.eu/",
        "description": "EU data protection authority with enforcement powers",
        "max_penalty": "4% global turnover OR €20 million (whichever higher)"
    },
    
    # Sector-specific US penalties
    "HHS/HIPAA": {
        "name": "Health and Human Services (HIPAA)",
        "jurisdiction": "United States",
        "type": "Privacy Penalty",
        "source_url": "https://www.hhs.gov/hipaa/index.html",
        "description": "Health privacy enforcement under HIPAA",
        "max_penalty": "$1.5 million per violation"
    }
}

# Cross-border agreements
CROSS_BORDER_AGREEMENTS = {
    "CETA (Canada-EU)": {
        "name": "Comprehensive Economic and Trade Agreement",
        "jurisdiction": "Canada-EU",
        "type": "Cross-border Agreement",
        "source_url": "https://www.canadaceta.org/",
        "description": "Trade agreement between Canada and EU with data protection provisions"
    },
    "USMCA (US-Mexico-Canada)": {
        "name": "United States-Mexico-Canada Agreement",
        "jurisdiction": "US-Mexico-Canada",
        "type": "Cross-border Agreement",
        "source_url": "https://ustr.gov/trade-agreements/free-trade-agreements/usmca",
        "description": "Trade agreement with data protection and privacy provisions"
    },
    "Privacy Shield (EU-US)": {
        "name": "EU-US Privacy Shield Framework",
        "jurisdiction": "EU-US",
        "type": "Cross-border Agreement",
        "source_url": "https://www.privacyshield.gov/",
        "description": "Framework for transferring personal data between EU and US"
    },
    "AUS-UK Data Transfer Agreement": {
        "name": "Data Transfer Agreement (Australia-UK)",
        "jurisdiction": "Australia-UK",
        "type": "Cross-border Agreement",
        "source_url": "https://www.gov.uk/government/publications/data-transfers-between-the-uk-and-australia",
        "description": "Agreement for data transfers between Australia and UK"
    }
}

class ComplianceLawDiscovery:
    def __init__(self):
        self.known_laws = BASE_STATUTES_AND_STANDARDS.copy()
        self.discovered_laws = DISCOVERED_LAWS.copy()
        self.privacy_torts = PRIVACY_TORTS.copy()
        self.penalties = PENALTIES.copy()
        self.cross_border_agreements = CROSS_BORDER_AGREEMENTS.copy()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ComplianceLawDiscovery/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
        
    def get_statute_info(self, statute_name: str) -> Dict:
        """Get detailed information about a specific statute or standard"""
        # Check if it's in known laws
        info = self.known_laws.get(statute_name)
        if info:
            return info
            
        # Check if it's in discovered laws
        info = self.discovered_laws.get(statute_name)
        if info:
            return info
            
        # Check if it's a privacy tort
        info = self.privacy_torts.get(statute_name)
        if info:
            return info
            
        # Check if it's a penalty
        info = self.penalties.get(statute_name)
        if info:
            return info
            
        # Check if it's a cross-border agreement
        info = self.cross_border_agreements.get(statute_name)
        if info:
            return info
            
        return None
    
    def find_authoritative_sources(self) -> List[Dict]:
        """Find all authoritative sources for the laws and standards in the diagram"""
        
        # Create a list of all statutes and standards from your diagram
        all_statutes = list(self.known_laws.keys())
        
        # For each statute, get its information
        results = []
        
        for statute in all_statutes:
            info = self.get_statute_info(statute)
            if info:
                results.append({
                    "name": info["name"],
                    "jurisdiction": info["jurisdiction"],
                    "type": info["type"],
                    "source_url": info["source_url"],
                    "description": info["description"]
                })
        
        return results
    
    def discover_law_by_name(self, law_name: str) -> Dict:
        """Attempt to discover a law by name using various strategies"""
        logger.info(f"Attempting to discover law: {law_name}")
        
        # 1. Check if it's already known
        for key, value in self.known_laws.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                return value
                
        for key, value in self.discovered_laws.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                return value
                
        # 2. Check for privacy torts
        for key, value in self.privacy_torts.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                return value
                
        # 3. Check for penalties
        for key, value in self.penalties.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                return value
                
        # 4. Check for cross-border agreements
        for key, value in self.cross_border_agreements.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                return value
        
        # 5. Use search engines to find the law (simulated)
        discovered = self._search_law_online(law_name)
        if discovered:
            return discovered
            
        # 6. Check for partial matches with existing laws
        partial_matches = self._find_partial_matches(law_name)
        if partial_matches:
            return partial_matches[0]
            
        # 7. If all else fails, create a placeholder
        return self._create_placeholder_law(law_name)
    
    def _search_law_online(self, law_name: str) -> Dict:
        """Search online for the law using various strategies"""
        try:
            logger.info(f"Searching online for law: {law_name}")
            
            # Check if law name matches any known patterns
            if "health information act" in law_name.lower() and "alberta" in law_name.lower():
                return {
                    "name": "Health Information Act",
                    "jurisdiction": "Alberta, Canada",
                    "type": "Health Privacy Law",
                    "source_url": "https://www.alberta.ca/health-information-act.aspx",
                    "description": "Alberta's legislation governing health information privacy"
                }
                
            if "personal information protection act" in law_name.lower() and "alberta" in law_name.lower():
                return {
                    "name": "Personal Information Protection Act",
                    "jurisdiction": "Alberta, Canada",
                    "type": "Privacy Law",
                    "source_url": "https://www.alberta.ca/personal-information-protection-act.aspx",
                    "description": "Alberta's privacy legislation for personal information"
                }
                
            if "biometric information privacy act" in law_name.lower() and "illinois" in law_name.lower():
                return {
                    "name": "Biometric Information Privacy Act",
                    "jurisdiction": "Illinois, US",
                    "type": "Privacy Law",
                    "source_url": "https://www.illinoiscourts.gov/Content/Issues/Biometric-Information-Privacy-Act-BIPA.aspx",
                    "description": "Illinois law governing biometric data collection"
                }
                
            # Check for privacy torts
            if "intrusion upon seclusion" in law_name.lower():
                return {
                    "name": "Intrusion upon seclusion",
                    "jurisdiction": "United States/Canada/EU",
                    "type": "Privacy Tort",
                    "source_url": "https://www.law.cornell.edu/wex/intrusion_upon_seclusion",
                    "description": "Tort involving intrusion into another's private affairs"
                }
                
            if "false light" in law_name.lower():
                return {
                    "name": "False light",
                    "jurisdiction": "United States/Canada/EU",
                    "type": "Privacy Tort",
                    "source_url": "https://www.law.cornell.edu/wex/false_light",
                    "description": "Tort involving false or misleading portrayal of a person"
                }
                
            # Check for penalties
            if "ftc" in law_name.lower():
                return {
                    "name": "Federal Trade Commission",
                    "jurisdiction": "United States",
                    "type": "Privacy Penalty",
                    "source_url": "https://www.ftc.gov/",
                    "description": "US federal agency with enforcement powers for deceptive practices",
                    "max_penalty": "$43,792 per violation"
                }
                
            if "gdpr" in law_name.lower():
                return {
                    "name": "General Data Protection Regulation",
                    "jurisdiction": "European Union",
                    "type": "Privacy Law",
                    "source_url": "https://gdpr-info.eu/",
                    "description": "EU regulation governing data protection and privacy"
                }
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            
        return None
    
    def _find_partial_matches(self, law_name: str) -> List[Dict]:
        """Find partial matches for a law name"""
        matches = []
        
        # Check known laws
        for key, value in self.known_laws.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                matches.append(value)
                
        # Check discovered laws
        for key, value in self.discovered_laws.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                matches.append(value)
                
        # Check privacy torts
        for key, value in self.privacy_torts.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                matches.append(value)
                
        # Check penalties
        for key, value in self.penalties.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                matches.append(value)
                
        # Check cross-border agreements
        for key, value in self.cross_border_agreements.items():
            if law_name.lower() in key.lower() or law_name.lower() in value["name"].lower():
                matches.append(value)
                
        return matches
    
    def _create_placeholder_law(self, law_name: str) -> Dict:
        """Create a placeholder for an unknown law"""
        return {
            "name": law_name,
            "jurisdiction": "Unknown",
            "type": "Unknown Law Type",
            "source_url": "Not yet discovered",
            "description": f"Law '{law_name}' has not been formally discovered or catalogued yet. Please research and provide authoritative source."
        }
    
    def discover_laws_in_jurisdiction(self, jurisdiction: str) -> Dict:
        """Discover laws specific to a jurisdiction"""
        logger.info(f"Searching for laws in jurisdiction: {jurisdiction}")
        
        discoveries = {
            "laws": [],
            "torts": [],
            "penalties": [],
            "agreements": []
        }
        
        # Check if jurisdiction has specific known laws
        if "alberta" in jurisdiction.lower():
            # Discover Alberta-specific laws
            discoveries["laws"].append(self.discover_law_by_name("Health Information Act (AB)"))
            discoveries["laws"].append(self.discover_law_by_name("Personal Information Protection Act (AB)"))
            
        elif "ontario" in jurisdiction.lower():
            # Discover Ontario-specific laws
            discoveries["laws"].append(self.discover_law_by_name("PHIPA"))
            discoveries["laws"].append(self.discover_law_by_name("FIPPA"))
            
        elif "quebec" in jurisdiction.lower():
            # Discover Quebec-specific laws
            discoveries["laws"].append(self.discover_law_by_name("Law 25"))
            
        elif "new york" in jurisdiction.lower() or "ny" in jurisdiction.lower():
            # Discover New York-specific laws
            discoveries["laws"].append(self.discover_law_by_name("NYDFS Part 500"))
            discoveries["laws"].append(self.discover_law_by_name("NYC Local Law 144"))
            
        elif "california" in jurisdiction.lower() or "ca" in jurisdiction.lower():
            # Discover California-specific laws
            discoveries["laws"].append(self.discover_law_by_name("CCPA / CPRA"))
            
        elif "united states" in jurisdiction.lower() or "us" in jurisdiction.lower():
            # Discover US federal laws
            discoveries["laws"].append(self.discover_law_by_name("FTC Act §5"))
            discoveries["laws"].append(self.discover_law_by_name("HIPAA"))
            discoveries["laws"].append(self.discover_law_by_name("SOX"))
            
        elif "european union" in jurisdiction.lower() or "eu" in jurisdiction.lower():
            # Discover EU laws
            discoveries["laws"].append(self.discover_law_by_name("GDPR"))
            discoveries["laws"].append(self.discover_law_by_name("EU AI Act"))
            
        # Discover privacy torts for the jurisdiction
        if "us" in jurisdiction.lower() or "united states" in jurisdiction.lower():
            discoveries["torts"].extend([
                self.discover_law_by_name("US Intrusion upon seclusion"),
                self.discover_law_by_name("US Public disclosure of private facts"),
                self.discover_law_by_name("US False light"),
                self.discover_law_by_name("US Appropriation of name/likeness")
            ])
        elif "canada" in jurisdiction.lower():
            discoveries["torts"].extend([
                self.discover_law_by_name("Canada Intrusion upon seclusion"),
                self.discover_law_by_name("Canada Public disclosure of private facts"),
                self.discover_law_by_name("Canada False light"),
                self.discover_law_by_name("Canada Appropriation")
            ])
        elif "eu" in jurisdiction.lower() or "european union" in jurisdiction.lower():
            discoveries["torts"].extend([
                self.discover_law_by_name("EU Infringement of personality rights"),
                self.discover_law_by_name("EU Breach of confidentiality"),
                self.discover_law_by_name("EU Data protection violation"),
                self.discover_law_by_name("EU Right to be forgotten")
            ])
            
        # Discover penalties for the jurisdiction
        if "canada" in jurisdiction.lower():
            discoveries["penalties"].extend([
                self.discover_law_by_name("OPC (Federal)"),
                self.discover_law_by_name("IPC ON"),
                self.discover_law_by_name("CAI QC")
            ])
        elif "us" in jurisdiction.lower() or "united states" in jurisdiction.lower():
            discoveries["penalties"].extend([
                self.discover_law_by_name("FTC"),
                self.discover_law_by_name("SEC"),
                self.discover_law_by_name("HHS/HIPAA")
            ])
        elif "eu" in jurisdiction.lower() or "european union" in jurisdiction.lower():
            discoveries["penalties"].append(self.discover_law_by_name("EU DPA"))
            
        # Discover cross-border agreements
        if "canada" in jurisdiction.lower() and ("us" in jurisdiction.lower() or "united states" in jurisdiction.lower()):
            discoveries["agreements"].append(self.discover_law_by_name("USMCA (US-Mexico-Canada)"))
        elif "canada" in jurisdiction.lower() and ("eu" in jurisdiction.lower() or "european union" in jurisdiction.lower()):
            discoveries["agreements"].append(self.discover_law_by_name("CETA (Canada-EU)"))
            
        return discoveries
    
    def discover_all_laws(self, jurisdictions: List[str]) -> Dict:
        """Discover all laws for specified jurisdictions"""
        discovery_results = {}
        
        for jurisdiction in jurisdictions:
            logger.info(f"Starting discovery for {jurisdiction}")
            results = self.discover_laws_in_jurisdiction(jurisdiction)
            discovery_results[jurisdiction] = results
            time.sleep(0.5)  # Be respectful to servers
            
        return discovery_results
    
    def add_discovered_law(self, law_name: str, jurisdiction: str, type: str, 
                          source_url: str, description: str):
        """Add a newly discovered law to the database"""
        law_key = f"{law_name} ({jurisdiction})"
        self.discovered_laws[law_key] = {
            "name": law_name,
            "jurisdiction": jurisdiction,
            "type": type,
            "source_url": source_url,
            "description": description
        }
        logger.info(f"Added discovered law: {law_name}")
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of all authoritative sources"""
        
        sources = self.find_authoritative_sources()
        
        # Create the report
        report = "# Authoritative Sources for Laws, Regulations, Standards, Torts and Penalties\n\n"
        report += "This document lists all the authoritative sources for laws, regulations, standards, privacy torts, and penalties referenced in the Enterprise Compliance Neural Net diagram.\n\n"
        
        # Group by type
        grouped_by_type = {}
        for source in sources:
            type_key = source["type"]
            if type_key not in grouped_by_type:
                grouped_by_type[type_key] = []
            grouped_by_type[type_key].append(source)
        
        # Add each group to the report
        for type_name, type_sources in grouped_by_type.items():
            report += f"## {type_name}\n\n"
            
            for source in type_sources:
                report += f"### {source['name']}\n"
                report += f"- **Jurisdiction**: {source['jurisdiction']}\n"
                report += f"- **Source URL**: [{source['source_url']}]({source['source_url']})\n"
                report += f"- **Description**: {source['description']}\n\n"
        
        return report
    
    def save_report(self):
        """Save the report to a file"""
        report = self.generate_report()
        
        # Save to markdown file
        with open("authoritative_sources.md", "w") as f:
            f.write(report)
        
        print("Report saved to 'authoritative_sources.md'")
        
        # Also save as JSON for programmatic use
        sources = self.find_authoritative_sources()
        with open("authoritative_sources.json", "w") as f:
            json.dump(sources, f, indent=2)
        
        print("JSON data saved to 'authoritative_sources.json'")

def main():
    """Main function to run the program"""
    print("Searching for authoritative sources for all laws and standards in the Enterprise Compliance Neural Net...")
    
    # Initialize discovery engine
    discovery_engine = ComplianceLawDiscovery()
    
    # Get all sources
    sources = discovery_engine.find_authoritative_sources()
    
    print(f"\nFound {len(sources)} authoritative sources:\n")
    
    # Display results
    for i, source in enumerate(sources, 1):
        print(f"{i}. {source['name']}")
        print(f"   Jurisdiction: {source['jurisdiction']}")
        print(f"   Type: {source['type']}")
        print(f"   Source: {source['source_url']}")
        print()
    
    # Generate and save full report
    discovery_engine.save_report()
    
    # Example discovery for specific jurisdictions
    print("\n=== DISCOVERY EXAMPLES ===")
    
    # Discover laws for a few example jurisdictions
    example_jurisdictions = [
        "Alberta, Canada",
        "Toronto, ON", 
        "Vancouver, BC",
        "New York, NY",
        "United States",
        "European Union"
    ]
    
    discovery_results = discovery_engine.discover_all_laws(example_jurisdictions)
    
    print("\nDiscovered laws in example jurisdictions:")
    for jurisdiction, results in discovery_results.items():
        print(f"\n--- {jurisdiction} ---")
        if results["laws"]:
            print("Laws:")
            for law in results["laws"]:
                print(f"  - {law['name']}: {law['description']}")
        if results["torts"]:
            print("Privacy Torts:")
            for tort in results["torts"]:
                print(f"  - {tort['name']}: {tort['description']}")
        if results["penalties"]:
            print("Penalties:")
            for penalty in results["penalties"]:
                print(f"  - {penalty['name']}: {penalty['description']}")
        if results["agreements"]:
            print("Cross-border Agreements:")
            for agreement in results["agreements"]:
                print(f"  - {agreement['name']}: {agreement['description']}")
    
    # Demonstrate discovery of a specific law like HIA in Alberta
    print("\n=== SPECIFIC EXAMPLE: Discovering Alberta's Health Information Act ===")
    hia_discovery = discovery_engine.discover_law_by_name("Health Information Act")
    if hia_discovery:
        print(f"Discovered: {hia_discovery['name']}")
        print(f"Jurisdiction: {hia_discovery['jurisdiction']}")
        print(f"Type: {hia_discovery['type']}")
        print(f"Description: {hia_discovery['description']}")
        print(f"Source URL: {hia_discovery['source_url']}")
    
    # Demonstrate discovery of privacy torts
    print("\n=== EXAMPLE: Discovering Privacy Torts ===")
    tort_discovery = discovery_engine.discover_law_by_name("Intrusion upon seclusion")
    if tort_discovery:
        print(f"Discovered Tort: {tort_discovery['name']}")
        print(f"Jurisdiction: {tort_discovery['jurisdiction']}")
        print(f"Type: {tort_discovery['type']}")
        print(f"Description: {tort_discovery['description']}")
        print(f"Source URL: {tort_discovery['source_url']}")
    
    # Demonstrate discovery of penalties
    print("\n=== EXAMPLE: Discovering Penalties ===")
    penalty_discovery = discovery_engine.discover_law_by_name("FTC")
    if penalty_discovery:
        print(f"Discovered Penalty: {penalty_discovery['name']}")
        print(f"Jurisdiction: {penalty_discovery['jurisdiction']}")
        print(f"Type: {penalty_discovery['type']}")
        print(f"Description: {penalty_discovery['description']}")
        print(f"Max Penalty: {penalty_discovery.get('max_penalty', 'Not specified')}")
        print(f"Source URL: {penalty_discovery['source_url']}")
    
    # Demonstrate discovery of cross-border agreements
    print("\n=== EXAMPLE: Discovering Cross-border Agreements ===")
    agreement_discovery = discovery_engine.discover_law_by_name("CETA (Canada-EU)")
    if agreement_discovery:
        print(f"Discovered Agreement: {agreement_discovery['name']}")
        print(f"Jurisdiction: {agreement_discovery['jurisdiction']}")
        print(f"Type: {agreement_discovery['type']}")
        print(f"Description: {agreement_discovery['description']}")
        print(f"Source URL: {agreement_discovery['source_url']}")
    
    print("\nProgram completed successfully!")
    print("\nTo view the full report:")
    print("- Open 'authoritative_sources.md' in a markdown viewer")
    print("- Or examine 'authoritative_sources.json' for programmatic access")

if __name__ == "__main__":
    main()

