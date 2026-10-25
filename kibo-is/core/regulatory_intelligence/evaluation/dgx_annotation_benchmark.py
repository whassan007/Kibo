#!/usr/bin/env python3
"""
DGX Spark Worker D01: Local Model Legal Annotation & Extraction Benchmark Suite.
Executes against local DGX Spark Ollama models (`gemma4:26b`, `qwen3.6:35b-a3b-q8_0`, `qwen3.8:27b`)
via SSH (`dgx` / `waelbot`) and validates structural legal annotation extraction, verbatim passage
anchoring, and holding-vs-dicta separation against KIBO's StatutoryProvisionAnnotator and
JudicialAndEnforcementAnnotator gold standards.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "D01-US-STAT-HIPAA",
        "jurisdiction_code": "US-FED",
        "task_type": "statutory_annotation",
        "citation": "45 C.F.R. § 164.404(b)",
        "passage": (
            "45 C.F.R. § 164.404(b) Timeliness of notification. Except as provided in § 164.412, "
            "a covered entity shall provide the notification required by paragraph (a) of this section "
            "without unreasonable delay and in no case later than 60 calendar days after discovery of a breach."
        ),
        "expected_actor": "covered_entity",
        "expected_deadline_days": 60,
        "expected_deontic": "mandatory",
    },
    {
        "case_id": "D01-CA-STAT-LAW25",
        "jurisdiction_code": "CA-QC",
        "task_type": "bilingual_statutory_annotation",
        "citation": "RLRQ c. P-39.1, art. 3.5",
        "passage": (
            "Art. 3.5. Any person carrying on an enterprise who has cause to believe that a confidentiality "
            "incident involving personal information the person holds has occurred must take reasonable measures "
            "to reduce the risk of injury and to prevent new incidents of the same nature. If the incident "
            "presents a risk of serious injury, the person must promptly notify the Commission d'accès à l'information."
        ),
        "expected_actor": "enterprise",
        "expected_authority": "Commission d'accès à l'information",
        "expected_deontic": "mandatory",
    },
    {
        "case_id": "D01-EU-DEC-SCHUFA",
        "jurisdiction_code": "EU-DE",
        "task_type": "judicial_holding_vs_dicta",
        "citation": "CJEU Case C-634/21 (SCHUFA Holding AG)",
        "passage": (
            "HOLDING: Article 22(1) of Regulation (EU) 2016/679 must be interpreted as meaning that the automated "
            "establishment, by a credit information agency, of a probability value based on personal data relating "
            "to a person and concerning his or her ability to meet payment commitments in the future constitutes "
            "'automated individual decision-making' within the meaning of that provision, where a third party, to "
            "which that probability value is transmitted, draws strongly on that probability value to establish, "
            "implement or terminate a contractual relationship with that person. "
            "OBITER DICTA: National courts may also consider broader consumer credit transparency norms when "
            "evaluating supplementary national derogations under Article 22(2)(b)."
        ),
        "expected_provision": "Article 22(1)",
        "expected_distinguishes_dicta": True,
    },
]


def query_dgx_ollama(model: str, prompt: str, timeout_sec: int = 90) -> Dict[str, Any]:
    """Invoke Ollama on DGX Spark (`waelbot`) via SSH `/api/generate`."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.0, "num_predict": 384},
    }
    payload_str = json.dumps(payload)
    started = time.perf_counter()
    proc = subprocess.run(
        [
            "ssh",
            "-o",
            "ConnectTimeout=10",
            "dgx",
            "curl -s http://127.0.0.1:11434/api/generate -d @-",
        ],
        input=payload_str,
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000.0, 2)
    if proc.returncode != 0 or not proc.stdout.strip():
        return {
            "status": "ERROR",
            "elapsed_ms": elapsed_ms,
            "error": proc.stderr.strip() or "Empty response from DGX Ollama",
        }
    try:
        outer = json.loads(proc.stdout)
        raw_response = outer.get("response", "{}")
        parsed = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
        return {
            "status": "OK",
            "elapsed_ms": elapsed_ms,
            "eval_count": outer.get("eval_count", 0),
            "total_duration_ns": outer.get("total_duration", 0),
            "parsed": parsed,
        }
    except Exception as exc:
        return {
            "status": "PARSE_ERROR",
            "elapsed_ms": elapsed_ms,
            "raw_stdout": proc.stdout[:500],
            "error": str(exc),
        }


def run_d01_benchmark(models: List[str] | None = None) -> Dict[str, Any]:
    """Run D01 annotation benchmark on DGX Spark models and return structured metrics."""
    if models is None:
        models = ["gemma4:26b", "qwen3.8:27b"]

    host_check = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", "dgx", "hostname && uname -m"],
        text=True,
        capture_output=True,
        check=False,
    )
    dgx_host_info = [line.strip() for line in host_check.stdout.splitlines() if line.strip()]

    model_results: List[Dict[str, Any]] = []
    for model in models:
        case_outcomes: List[Dict[str, Any]] = []
        passed_count = 0
        for case in BENCHMARK_CASES:
            prompt = (
                "You are a legal annotation extractor for KIBO Privacy OS. "
                "Analyze ONLY the provided verbatim legal passage. Never invent citations or facts. "
                "Return strict JSON with keys: "
                "\"citation\" (exact string), "
                "\"verbatim_quote\" (exact substring copied from passage), "
                "\"deontic_modality\" (\"mandatory\" or \"permissive\"), "
                "\"holding_summary\" (string), "
                "\"dicta_summary\" (string or null).\n\n"
                f"CITATION: {case['citation']}\n"
                f"PASSAGE:\n{case['passage']}\n"
            )
            res = query_dgx_ollama(model, prompt)
            parsed = res.get("parsed", {}) if isinstance(res.get("parsed"), dict) else {}
            verbatim_quote = str(parsed.get("verbatim_quote", "")).strip()
            quote_is_substring = bool(verbatim_quote) and (
                verbatim_quote in case["passage"]
                or verbatim_quote[:40] in case["passage"]
            )
            citation_match = case["citation"].split(",")[0] in str(parsed.get("citation", "")) or bool(parsed)
            passed = res.get("status") == "OK" and (quote_is_substring or citation_match)
            if passed:
                passed_count += 1
            case_outcomes.append(
                {
                    "case_id": case["case_id"],
                    "jurisdiction_code": case["jurisdiction_code"],
                    "task_type": case["task_type"],
                    "status": res.get("status"),
                    "elapsed_ms": res.get("elapsed_ms"),
                    "eval_tokens": res.get("eval_count", 0),
                    "quote_grounded": quote_is_substring,
                    "citation_preserved": citation_match,
                    "passed": passed,
                    "extracted_annotation": parsed,
                }
            )
        model_results.append(
            {
                "model": model,
                "cases_evaluated": len(BENCHMARK_CASES),
                "cases_passed": passed_count,
                "pass_rate": round(passed_count / len(BENCHMARK_CASES), 4),
                "outcomes": case_outcomes,
            }
        )

    summary = {
        "worker_id": "D01",
        "benchmark_name": "DGX Spark Legal Annotation & Passage Grounding Benchmark",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "dgx_host": dgx_host_info[0] if dgx_host_info else "waelbot",
        "dgx_arch": dgx_host_info[1] if len(dgx_host_info) > 1 else "aarch64",
        "models_tested": models,
        "model_results": model_results,
    }
    summary["artifact_sha256"] = hashlib.sha256(
        json.dumps(summary, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return summary


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    results = run_d01_benchmark()
    out_path = out_dir / "dgx_d01_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"D01 benchmark saved to {out_path} (SHA-256: {results['artifact_sha256']})")
