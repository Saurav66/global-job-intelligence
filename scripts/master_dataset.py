#!/usr/bin/env python3
"""
Master Dataset Manager (master_dataset.py)
Manages local JSONL dataset operations: initialization, loading, validation,
atomic upserting, deduplication, summary analytics, and expiration marking.
"""

import argparse
import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from scripts.job_utils import generate_job_fingerprint
    from scripts.validate_job import validate_job_record
    from scripts.deduplicate_jobs import check_duplicate_signal, merge_job_records
except ImportError:
    from job_utils import generate_job_fingerprint
    from validate_job import validate_job_record
    from deduplicate_jobs import check_duplicate_signal, merge_job_records

DEFAULT_DATASET_PATH = "job_master.jsonl"


def load_dataset(dataset_path: str = DEFAULT_DATASET_PATH) -> List[Dict[str, Any]]:
    """Loads all records from a JSONL file."""
    path = Path(dataset_path)
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line_str = line.strip()
            if line_str:
                try:
                    records.append(json.loads(line_str))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping corrupted JSON on line {line_num}: {e}", file=sys.stderr)
    return records


def save_dataset_atomic(records: List[Dict[str, Any]], dataset_path: str = DEFAULT_DATASET_PATH) -> None:
    """Atomically saves a list of job records to a JSONL file using a temp file."""
    target_path = Path(dataset_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in the same directory for atomic replace
    with tempfile.NamedTemporaryFile("w", dir=target_path.parent, delete=False, encoding="utf-8") as tf:
        temp_name = tf.name
        for rec in records:
            tf.write(json.dumps(rec, ensure_ascii=False) + "\n")
        tf.flush()
        os.fsync(tf.fileno())

    os.replace(temp_name, str(target_path))


def init_dataset(dataset_path: str = DEFAULT_DATASET_PATH) -> bool:
    """Initializes an empty master dataset file if it does not already exist."""
    path = Path(dataset_path)
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return True


def upsert_records(
    incoming_records: List[Dict[str, Any]],
    dataset_path: str = DEFAULT_DATASET_PATH
) -> Dict[str, Any]:
    """
    Upserts incoming records into master dataset with atomic saving.
    Merges duplicates safely and appends new unique records.
    """
    existing_records = load_dataset(dataset_path)
    records_by_id = {r.get("job_id", generate_job_fingerprint(r)): r for r in existing_records}

    inserted_count = 0
    updated_count = 0

    for incoming in incoming_records:
        inc = copy.deepcopy(incoming)
        if not inc.get("job_id"):
            inc["job_id"] = generate_job_fingerprint(inc)
        inc_id = inc["job_id"]

        # 1. Exact ID match
        if inc_id in records_by_id:
            merged = merge_job_records(records_by_id[inc_id], inc)
            records_by_id[inc_id] = merged
            updated_count += 1
            continue

        # 2. Duplicate signal match
        matched_id = None
        for ex_id, ex_rec in records_by_id.items():
            dup_meta = check_duplicate_signal(inc, ex_rec)
            if dup_meta:
                matched_id = ex_id
                merged = merge_job_records(ex_rec, inc)
                records_by_id[ex_id] = merged
                updated_count += 1
                break

        if not matched_id:
            records_by_id[inc_id] = inc
            inserted_count += 1

    final_list = list(records_by_id.values())
    save_dataset_atomic(final_list, dataset_path)

    return {
        "dataset_path": dataset_path,
        "total_records": len(final_list),
        "inserted": inserted_count,
        "updated": updated_count,
    }


def mark_expired(job_id: str, dataset_path: str = DEFAULT_DATASET_PATH) -> bool:
    """Marks a specific job_id as EXPIRED in the master dataset."""
    records = load_dataset(dataset_path)
    found = False
    for r in records:
        if r.get("job_id") == job_id:
            r["status"] = "EXPIRED"
            found = True
            break
    if found:
        save_dataset_atomic(records, dataset_path)
    return found


def summarize_dataset(dataset_path: str = DEFAULT_DATASET_PATH) -> Dict[str, Any]:
    """Generates aggregate summary counts from the master dataset."""
    records = load_dataset(dataset_path)
    summary = {
        "total_jobs": len(records),
        "by_priority": {},
        "by_status": {},
        "by_role_family": {},
        "by_remote_type": {},
        "salary_disclosed_count": 0,
        "salary_undisclosed_count": 0,
    }

    for r in records:
        p = r.get("priority", "UNKNOWN")
        summary["by_priority"][p] = summary["by_priority"].get(p, 0) + 1

        s = r.get("status", "UNKNOWN")
        summary["by_status"][s] = summary["by_status"].get(s, 0) + 1

        rf = r.get("role_family", "UNKNOWN")
        summary["by_role_family"][rf] = summary["by_role_family"].get(rf, 0) + 1

        rt = r.get("remote_type", "UNKNOWN")
        summary["by_remote_type"][rt] = summary["by_remote_type"].get(rt, 0) + 1

        if r.get("salary_disclosed"):
            summary["salary_disclosed_count"] += 1
        else:
            summary["salary_undisclosed_count"] += 1

    return summary


def main():
    parser = argparse.ArgumentParser(description="Master Dataset JSONL Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # init
    p_init = subparsers.add_parser("init", help="Initialize empty master dataset")
    p_init.add_argument("--file", default=DEFAULT_DATASET_PATH, help="Path to dataset JSONL")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate all records in dataset")
    p_val.add_argument("--file", default=DEFAULT_DATASET_PATH, help="Path to dataset JSONL")

    # summary
    p_sum = subparsers.add_parser("summary", help="Summarize dataset metrics")
    p_sum.add_argument("--file", default=DEFAULT_DATASET_PATH, help="Path to dataset JSONL")

    # upsert
    p_up = subparsers.add_parser("upsert", help="Upsert records from a JSON / JSONL file")
    p_up.add_argument("input_file", help="Path to input JSON/JSONL file with new records")
    p_up.add_argument("--file", default=DEFAULT_DATASET_PATH, help="Path to target dataset JSONL")

    # expire
    p_exp = subparsers.add_parser("expire", help="Mark a job as EXPIRED")
    p_exp.add_argument("job_id", help="Job ID to mark expired")
    p_exp.add_argument("--file", default=DEFAULT_DATASET_PATH, help="Path to target dataset JSONL")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        created = init_dataset(args.file)
        if created:
            print(f"Initialized new empty master dataset at: {args.file}")
        else:
            print(f"Master dataset already exists at: {args.file}")
        sys.exit(0)

    elif args.command == "validate":
        records = load_dataset(args.file)
        invalid_count = 0
        for idx, rec in enumerate(records, start=1):
            val, errs, _ = validate_job_record(rec)
            if not val:
                invalid_count += 1
                print(f"Record {idx} ({rec.get('job_id')}) INVALID: {errs}", file=sys.stderr)
        if invalid_count == 0:
            print(f"All {len(records)} records in {args.file} are valid.")
            sys.exit(0)
        else:
            print(f"Found {invalid_count} invalid records in {args.file}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "summary":
        summary = summarize_dataset(args.file)
        print(json.dumps(summary, indent=2))
        sys.exit(0)

    elif args.command == "upsert":
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Input file not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        incoming = []
        if input_path.suffix == ".jsonl":
            with open(input_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        incoming.append(json.loads(line))
        else:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                incoming = data if isinstance(data, list) else [data]
        res = upsert_records(incoming, args.file)
        print(json.dumps(res, indent=2))
        sys.exit(0)

    elif args.command == "expire":
        ok = mark_expired(args.job_id, args.file)
        if ok:
            print(f"Marked job '{args.job_id}' as EXPIRED in {args.file}")
            sys.exit(0)
        else:
            print(f"Job '{args.job_id}' not found in {args.file}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
