#!/usr/bin/env python3
"""
Artifact Synchronization & Concurrency Guard (artifact_sync.py)
Handles safe materialization, validation, atomic copying, SHA-256 checksumming,
and optimistic concurrency conflict detection between durable artifacts and runtime copies.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

try:
    from scripts.validate_job import validate_job_record
except ImportError:
    from validate_job import validate_job_record


def calculate_checksum(file_path: str) -> Optional[str]:
    """Computes the SHA-256 checksum of a file, or returns None if file does not exist."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return None
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def count_and_validate_records(file_path: str) -> Tuple[bool, int, list]:
    """Validates all JSONL records in a file and returns (is_valid, count, errors)."""
    path = Path(file_path)
    if not path.exists():
        return True, 0, []

    count = 0
    errors = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            count += 1
            try:
                record = json.loads(line_str)
                is_valid, errs, _ = validate_job_record(record)
                if not is_valid:
                    errors.append(f"Line {idx} (ID: {record.get('job_id', 'UNKNOWN')}): {'; '.join(errs)}")
            except json.JSONDecodeError as e:
                errors.append(f"Line {idx}: JSON parse error: {e}")

    return len(errors) == 0, count, errors


def atomic_copy(source_path: str, destination_path: str) -> None:
    """Atomically copies source to destination using a temporary file in the target directory."""
    src = Path(source_path).resolve()
    dst = Path(destination_path).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("wb", dir=dst.parent, delete=False) as tf:
        temp_name = tf.name
        with open(src, "rb") as sf:
            shutil.copyfileobj(sf, tf)
        tf.flush()
        os.fsync(tf.fileno())

    os.replace(temp_name, str(dst))


def import_artifact(source_path: str, runtime_path: str, validate: bool = True) -> Dict[str, Any]:
    """
    Imports and validates durable artifact into the local runtime working file.
    Will NOT overwrite runtime destination if source validation fails.
    """
    src = Path(source_path)
    if not src.exists():
        return {
            "status": "SOURCE_NOT_FOUND",
            "source": str(source_path),
            "destination": str(runtime_path),
            "record_count": 0,
            "sha256": None,
            "validated": False,
            "message": f"Durable source artifact '{source_path}' does not exist."
        }

    if validate:
        is_valid, count, errors = count_and_validate_records(str(source_path))
        if not is_valid:
            return {
                "status": "VALIDATION_FAILED",
                "source": str(source_path),
                "destination": str(runtime_path),
                "record_count": count,
                "sha256": calculate_checksum(str(source_path)),
                "validated": False,
                "errors": errors,
                "message": f"Source artifact '{source_path}' failed schema validation."
            }
    else:
        is_valid, count, errors = True, 0, []

    atomic_copy(str(source_path), str(runtime_path))
    checksum = calculate_checksum(str(runtime_path))

    return {
        "status": "SUCCESS",
        "source": str(source_path),
        "destination": str(runtime_path),
        "record_count": count,
        "sha256": checksum,
        "validated": True,
        "message": f"Successfully imported {count} records into runtime working file."
    }


def export_artifact(
    runtime_path: str,
    destination_path: str,
    expected_input_hash: Optional[str] = None,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Exports local runtime working dataset to durable artifact with optimistic concurrency protection.
    """
    rt = Path(runtime_path)
    if not rt.exists():
        return {
            "status": "RUNTIME_FILE_NOT_FOUND",
            "source": str(runtime_path),
            "destination": str(destination_path),
            "record_count": 0,
            "sha256": None,
            "validated": False,
            "message": f"Runtime working file '{runtime_path}' does not exist."
        }

    # 1. Optimistic Concurrency Guard
    dst = Path(destination_path)
    if expected_input_hash is not None and dst.exists():
        current_dst_hash = calculate_checksum(str(destination_path))
        if current_dst_hash != expected_input_hash:
            return {
                "status": "DATASET_CONFLICT",
                "source": str(runtime_path),
                "destination": str(destination_path),
                "expected_hash": expected_input_hash,
                "current_destination_hash": current_dst_hash,
                "validated": False,
                "message": (
                    f"Concurrency conflict: Destination '{destination_path}' was modified "
                    f"by another run during this execution window (stale write prevented)."
                )
            }

    # 2. Validation
    if validate:
        is_valid, count, errors = count_and_validate_records(str(runtime_path))
        if not is_valid:
            return {
                "status": "VALIDATION_FAILED",
                "source": str(runtime_path),
                "destination": str(destination_path),
                "record_count": count,
                "sha256": calculate_checksum(str(runtime_path)),
                "validated": False,
                "errors": errors,
                "message": f"Runtime working dataset '{runtime_path}' failed schema validation."
            }
    else:
        is_valid, count, errors = True, 0, []

    # 3. Atomic Export
    atomic_copy(str(runtime_path), str(destination_path))
    final_checksum = calculate_checksum(str(destination_path))

    return {
        "status": "SUCCESS",
        "source": str(runtime_path),
        "destination": str(destination_path),
        "record_count": count,
        "sha256": final_checksum,
        "validated": True,
        "message": f"Successfully exported {count} records to durable artifact '{destination_path}'."
    }


def main():
    parser = argparse.ArgumentParser(description="Artifact Sync and Concurrency Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # import
    p_imp = subparsers.add_parser("import", help="Import durable artifact to local runtime")
    p_imp.add_argument("--source", required=True, help="Durable source path (e.g., JOB_MASTER_TABLE.jsonl)")
    p_imp.add_argument("--runtime", required=True, help="Runtime destination path (e.g., job_master.jsonl)")
    p_imp.add_argument("--no-validate", action="store_true", help="Skip schema validation")

    # export
    p_exp = subparsers.add_parser("export", help="Export local runtime to durable artifact")
    p_exp.add_argument("--runtime", required=True, help="Runtime source path (e.g., job_master.jsonl)")
    p_exp.add_argument("--dest", required=True, help="Durable destination path (e.g., JOB_MASTER_TABLE.jsonl)")
    p_exp.add_argument("--expected-hash", help="Expected source hash before execution (for concurrency check)")
    p_exp.add_argument("--no-validate", action="store_true", help="Skip schema validation")

    # checksum
    p_chk = subparsers.add_parser("checksum", help="Calculate SHA-256 checksum of a file")
    p_chk.add_argument("file", help="Path to file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "checksum":
        cs = calculate_checksum(args.file)
        if cs is None:
            print(f"File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps({"file": args.file, "sha256": cs}, indent=2))
        sys.exit(0)

    elif args.command == "import":
        res = import_artifact(args.source, args.runtime, validate=not args.no_validate)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["status"] == "SUCCESS" else 1)

    elif args.command == "export":
        res = export_artifact(
            runtime_path=args.runtime,
            destination_path=args.dest,
            expected_input_hash=args.expected_hash,
            validate=not args.no_validate
        )
        print(json.dumps(res, indent=2))
        sys.exit(0 if res["status"] == "SUCCESS" else 1)


if __name__ == "__main__":
    main()
