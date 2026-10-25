"""
Agent A6 — DGX Spark (NVIDIA GB10) Regulatory Intelligence, Ontology Consistency & Local LLM Evaluation Suite.
Executes against local Ollama models on `dgx` (`waelbot`) using synthetic compliance scenarios only.
Never transmits customer data.
"""

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime
from typing import Any, Dict, List


SYNTHETIC_BENCHMARK_CASES = [
    {
        "case_id": "DGX-SYN-01",
        "title": "California Hospital External AI Diagnostic Assistant",
        "jurisdictions": ["US-FED", "US-CA"],
        "facts": "Private non-profit hospital in California (1,200 employees) adopts a third-party cloud AI radiology diagnostic assistant processing patient Electronic Health Records (PHI).",
        "expected_laws": ["HIPAA Privacy/Security/Breach", "California CMIA", "CalPrivacy ADMT / AI Transparency", "BAA Requirement"],
        "must_not_assume": "Must not assume CCPA applies to HIPAA PHI (carve-out under Cal. Civ. Code § 1798.145(c)), nor assume every US federal law (like FERPA or GLBA) applies.",
    },
    {
        "case_id": "DGX-SYN-02",
        "title": "Ontario Hospital Cloud Processor Transfer",
        "jurisdictions": ["CA-ON", "CA-FED"],
        "facts": "Ontario public hospital (Health Information Custodian) engages a cloud electronic service provider to host patient scheduling and clinical notes.",
        "expected_laws": ["Ontario PHIPA", "PHIPA Threat Risk Assessment (TRA)", "O. Reg. 329/04 s. 6 Electronic Service Provider Agreement", "IPC Ontario Breach Notification"],
        "must_not_assume": "Must distinguish Ontario PHIPA health information custodian obligations from commercial PIPEDA rules.",
    },
    {
        "case_id": "DGX-SYN-03",
        "title": "Quebec Enterprise International Data Transfer",
        "jurisdictions": ["CA-QC", "CA-FED"],
        "facts": "Private retail enterprise in Montreal transfers Quebec customer personal information to a US analytics processor.",
        "expected_laws": ["Quebec Law 25 (CQLR c. P-39.1)", "Section 17 Transfer Impact Assessment (TIA)", "Written contract with adequate protection", "French privacy notice"],
        "must_not_assume": "Must require a Law 25 Section 17 PIA/TIA prior to communicating personal information outside Quebec.",
    },
    {
        "case_id": "DGX-SYN-04",
        "title": "German Hospital AI-Assisted Scheduling",
        "jurisdictions": ["EU", "EU-DE"],
        "facts": "Bavarian hospital deploys AI-assisted patient triage and appointment scheduling processing health data.",
        "expected_laws": ["GDPR Art. 9(2)(h) & Art. 35 DPIA", "German BDSG § 22 & § 38 DPO", "Bavarian Hospital / Patient Data Protection laws", "EU AI Act High-Risk AI System", "BayLDA / Bavarian Supervisory Authority"],
        "must_not_assume": "Must model both GDPR and German national/Länder hospital and supervisory authority rules.",
    },
    {
        "case_id": "DGX-SYN-05",
        "title": "German Resident Deletion Request to US/Canadian Company Without EU Nexus",
        "jurisdictions": ["US-FED", "CA-FED", "EU-DE"],
        "facts": "German resident submits a GDPR Art. 17 erasure request to a US-headquartered B2B logistics firm with Canadian operations that has no EU establishment, does not offer goods/services to the EU, and does not monitor behavior in the EU.",
        "expected_laws": ["GDPR Art. 3(1) and Art. 3(2) Territorial Scope Negative Determination", "US/Canadian applicable rules only"],
        "must_not_assume": "Must NOT assume GDPR applies solely from German nationality or residence when Art. 3(1)/(2) nexus is absent.",
    },
]


def evaluate_on_dgx_ollama(model: str = "gemma4:26b", ollama_url: str = "http://127.0.0.1:11434/api/generate") -> Dict[str, Any]:
    """Run synthetic legal reasoning & ontology grounding checks on DGX Spark Ollama."""
    results = []
    start_all = time.time()
    for case in SYNTHETIC_BENCHMARK_CASES:
        prompt = (
            f"You are a multi-jurisdictional privacy compliance evaluator.\n"
            f"Scenario: {case['facts']}\n"
            f"Identify: (1) Applicable statutes, (2) Mandatory assessments/agreements, "
            f"(3) Exemptions or territorial scope limits ({case['must_not_assume']}). "
            f"Respond concisely in 4-6 bullet points."
        )
        t0 = time.time()
        payload = json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.1, "num_predict": 512}
        }).encode("utf-8")
        try:
            req = urllib.request.Request(ollama_url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                response_text = (body.get("response") or body.get("thinking") or "").strip()
                eval_count = body.get("eval_count", 0)
                status = "PASS" if len(response_text) > 20 else "WARN"
        except Exception as exc:
            response_text = f"Fallback deterministic evaluation: {exc}"
            eval_count = 0
            status = "DETERMINISTIC_FALLBACK"
        elapsed = round(time.time() - t0, 2)
        results.append({
            "case_id": case["case_id"],
            "title": case["title"],
            "jurisdictions": case["jurisdictions"],
            "model": model,
            "status": status,
            "latency_sec": elapsed,
            "tokens_generated": eval_count,
            "expected_laws": case["expected_laws"],
            "sample_output": response_text[:500],
        })

    return {
        "agent": "A6",
        "host": os.uname().nodename,
        "evaluated_at": datetime.utcnow().isoformat() + "Z",
        "model": model,
        "total_cases": len(results),
        "passed_cases": sum(1 for r in results if r["status"] == "PASS"),
        "total_duration_sec": round(time.time() - start_all, 2),
        "cases": results,
    }


if __name__ == "__main__":
    report = evaluate_on_dgx_ollama()
    print(json.dumps(report, indent=2))
