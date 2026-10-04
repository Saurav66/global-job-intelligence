#!/usr/bin/env python3
"""
Run Manifest Generator (run_manifest.py)
Creates, validates, and serializes execution-state metadata manifests (RUN_MANIFEST.json)
for end-of-run auditing and historical task tracing.
"""

import argparse
import datetime
import json
import sys
import uuid
from typing import Dict, Any, List, Optional

SKILL_VERSION = "0.3.1"

VALID_RUN_MODES = {"MORNING", "EVENING", "WEEKLY", "MANUAL_TEST", "INTEGRATION_TEST"}
VALID_RUN_STATUSES = {"SUCCESS", "PARTIAL_SUCCESS", "FAILED", "DATASET_RECOVERY_REQUIRED"}
VALID_FALLBACK_MODES = {"DETERMINISTIC", "HYBRID_FALLBACK", "MANUAL_FALLBACK"}


def generate_run_id(run_mode: str = "MORNING", dt: Optional[datetime.datetime] = None) -> str:
    """Generates a standardized run ID: YYYYMMDDTHHMMSSZ-<MODE>-<SHORT_HASH>."""
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    ts = dt.strftime("%Y%m%dT%H%M%SZ")
    mode_str = run_mode.upper().strip()
    short_hash = uuid.uuid4().hex[:8]
    return f"{ts}-{mode_str}-{short_hash}"


def create_run_manifest(
    run_id: Optional[str] = None,
    run_mode: str = "MORNING",
    started_at: Optional[str] = None,
    completed_at: Optional[str] = None,
    candidate_context_level: str = "STANDARD",
    input_record_count: int = 0,
    output_record_count: int = 0,
    input_sha256: Optional[str] = None,
    output_sha256: Optional[str] = None,
    raw_found: int = 0,
    unique_new: int = 0,
    duplicates: int = 0,
    hard_rejected: int = 0,
    analyzed: int = 0,
    a_plus_count: int = 0,
    a_count: int = 0,
    b_count: int = 0,
    c_count: int = 0,
    resume_holds: int = 0,
    scripts_available: bool = True,
    deterministic_processing_used: bool = True,
    fallback_used: str = "DETERMINISTIC",
    warnings: Optional[List[str]] = None,
    errors: Optional[List[str]] = None,
    run_status: str = "SUCCESS"
) -> Dict[str, Any]:
    """Builds a standardized Run Manifest dictionary."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mode_upper = run_mode.upper() if run_mode.upper() in VALID_RUN_MODES else "MORNING"
    status_upper = run_status.upper() if run_status.upper() in VALID_RUN_STATUSES else "SUCCESS"
    fallback_upper = fallback_used.upper() if fallback_used.upper() in VALID_FALLBACK_MODES else "DETERMINISTIC"

    if not run_id:
        run_id = generate_run_id(mode_upper)

    manifest = {
        "run_id": run_id,
        "started_at": started_at or now_iso,
        "completed_at": completed_at or now_iso,
        "run_mode": mode_upper,
        "skill_version": SKILL_VERSION,
        "candidate_context_level": candidate_context_level.upper(),
        "dataset": {
            "input_record_count": int(input_record_count),
            "output_record_count": int(output_record_count),
            "input_sha256": input_sha256,
            "output_sha256": output_sha256
        },
        "discovery": {
            "raw_found": int(raw_found),
            "unique_new": int(unique_new),
            "duplicates": int(duplicates),
            "hard_rejected": int(hard_rejected),
            "analyzed": int(analyzed)
        },
        "priorities": {
            "A_plus": int(a_plus_count),
            "A": int(a_count),
            "B": int(b_count),
            "C": int(c_count)
        },
        "resume_holds": int(resume_holds),
        "execution": {
            "scripts_available": bool(scripts_available),
            "deterministic_processing_used": bool(deterministic_processing_used),
            "fallback_used": fallback_upper
        },
        "warnings": warnings or [],
        "errors": errors or [],
        "run_status": status_upper
    }
    return manifest


def save_manifest(manifest: Dict[str, Any], output_path: str = "RUN_MANIFEST.json") -> None:
    """Serializes the run manifest to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Run Manifest Utility")
    parser.add_argument("--mode", default="MORNING", choices=["MORNING", "EVENING", "WEEKLY", "MANUAL_TEST"])
    parser.add_argument("--status", default="SUCCESS", choices=["SUCCESS", "PARTIAL_SUCCESS", "FAILED", "DATASET_RECOVERY_REQUIRED"])
    parser.add_argument("--fallback", default="DETERMINISTIC", choices=["DETERMINISTIC", "HYBRID_FALLBACK", "MANUAL_FALLBACK"])
    parser.add_argument("--out", default="RUN_MANIFEST.json", help="Path to write manifest JSON")
    parser.add_argument("--raw", type=int, default=0, help="Raw jobs discovered")
    parser.add_argument("--unique", type=int, default=0, help="Unique new jobs")
    parser.add_argument("--dups", type=int, default=0, help="Duplicates detected")
    parser.add_argument("--in-records", type=int, default=0, help="Input record count")
    parser.add_argument("--out-records", type=int, default=0, help="Output record count")
    parser.add_argument("--context-level", default="STANDARD", help="Context level (MINIMUM, STANDARD, ENRICHED)")

    args = parser.parse_args()

    manifest = create_run_manifest(
        run_mode=args.mode,
        run_status=args.status,
        fallback_used=args.fallback,
        raw_found=args.raw,
        unique_new=args.unique,
        duplicates=args.dups,
        input_record_count=args.in_records,
        output_record_count=args.out_records,
        candidate_context_level=args.context_level
    )

    if args.out != "-":
        save_manifest(manifest, args.out)
        print(f"Saved run manifest to '{args.out}' (Run ID: {manifest['run_id']})")
    else:
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
