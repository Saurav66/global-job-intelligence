#!/usr/bin/env python3
"""
Pre-Flight Orchestrator (preflight.py)
Runs pre-flight verification before live execution: checks skill version, script accessibility,
runtime probe, candidate context JSON (if provided), and master dataset integrity (if provided).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from scripts.runtime_probe import probe_runtime, SKILL_VERSION
    from scripts.context_validator import validate_candidate_context
    from scripts.artifact_sync import count_and_validate_records
except ImportError:
    from runtime_probe import probe_runtime, SKILL_VERSION
    from context_validator import validate_candidate_context
    from artifact_sync import count_and_validate_records


def run_preflight(
    candidate_path: Optional[str] = None,
    dataset_path: Optional[str] = None,
    repo_root: Optional[Path] = None
) -> Dict[str, Any]:
    """Orchestrates comprehensive pre-flight readiness checks."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent

    errors = []
    warnings = []

    # 1. Runtime Probe
    probe = probe_runtime(repo_root / "scripts")
    if not probe["filesystem_write"] or not probe["atomic_replace"]:
        errors.append("Filesystem write/atomic replace test failed.")
    if not probe["skill_scripts_accessible"]:
        errors.append(f"Missing required scripts: {probe['missing_scripts']}")

    # 2. Candidate Context Validation (if supplied)
    context_status = "NOT_SUPPLIED"
    context_level = "UNKNOWN"
    if candidate_path:
        cp = Path(candidate_path)
        if not cp.exists():
            errors.append(f"Candidate context file '{candidate_path}' does not exist.")
            context_status = "FILE_NOT_FOUND"
        else:
            try:
                with open(cp, "r", encoding="utf-8") as f:
                    c_data = json.load(f)
                c_val = validate_candidate_context(c_data)
                context_level = c_val.get("sufficiency_level", "UNKNOWN")
                if not c_val["valid"]:
                    errors.extend([f"Candidate Context: {e}" for e in c_val["errors"]])
                    context_status = "INVALID"
                else:
                    context_status = f"VALID ({context_level})"
                warnings.extend([f"Candidate Context: {w}" for w in c_val.get("warnings", [])])
            except Exception as e:
                errors.append(f"Failed to parse candidate context JSON: {e}")
                context_status = "PARSE_ERROR"

    # 3. Master Dataset Validation (if supplied)
    dataset_status = "NOT_SUPPLIED"
    record_count = 0
    if dataset_path:
        dp = Path(dataset_path)
        if not dp.exists():
            warnings.append(f"Dataset file '{dataset_path}' does not exist (will be initialized clean).")
            dataset_status = "NOT_FOUND_CLEAN_INIT"
        else:
            d_valid, d_count, d_errors = count_and_validate_records(str(dp))
            record_count = d_count
            if not d_valid:
                errors.extend([f"Dataset Record: {e}" for e in d_errors[:5]])
                if len(d_errors) > 5:
                    errors.append(f"... and {len(d_errors) - 5} more dataset validation errors.")
                dataset_status = f"INVALID ({len(d_errors)} errors)"
            else:
                dataset_status = f"VALID ({record_count} records)"

    ready = len(errors) == 0
    return {
        "ready": ready,
        "skill_version": SKILL_VERSION,
        "runtime_probe": probe,
        "candidate_context": {
            "status": context_status,
            "sufficiency_level": context_level,
            "path": candidate_path
        },
        "dataset": {
            "status": dataset_status,
            "record_count": record_count,
            "path": dataset_path
        },
        "errors": errors,
        "warnings": warnings
    }


def main():
    parser = argparse.ArgumentParser(description="Skill Pre-Flight Readiness Checker")
    parser.add_argument("--candidate", help="Path to candidate context JSON")
    parser.add_argument("--dataset", help="Path to master dataset JSONL")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    res = run_preflight(candidate_path=args.candidate, dataset_path=args.dataset)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        status_icon = "✅ READY" if res["ready"] else "❌ NOT READY"
        print(f"=== Global Job Intelligence Pre-Flight: {status_icon} ===")
        print(f"Skill Version:       {res['skill_version']}")
        print(f"Script Access:       {'OK' if res['runtime_probe']['skill_scripts_accessible'] else 'FAIL'}")
        print(f"Candidate Context:   {res['candidate_context']['status']}")
        print(f"Dataset Status:      {res['dataset']['status']}")

        if res["warnings"]:
            print("\n⚠️ Warnings:")
            for w in res["warnings"]:
                print(f"  - {w}")

        if res["errors"]:
            print("\n❌ Errors:")
            for e in res["errors"]:
                print(f"  - {e}")

    sys.exit(0 if res["ready"] else 1)


if __name__ == "__main__":
    main()
