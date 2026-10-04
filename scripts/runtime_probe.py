#!/usr/bin/env python3
"""
Runtime Probe Utility (runtime_probe.py)
Safely probes Python execution capabilities, filesystem read/write access,
atomic replacement support, and skill script accessibility without leaking host secrets.
"""

import datetime
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

SKILL_VERSION = "0.3.1"

REQUIRED_SCRIPTS = [
    "job_utils.py",
    "validate_job.py",
    "deduplicate_jobs.py",
    "score_job.py",
    "master_dataset.py",
    "context_validator.py",
    "artifact_sync.py",
    "run_manifest.py",
]


def probe_runtime(scripts_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Probes runtime execution capabilities."""
    if scripts_dir is None:
        scripts_dir = Path(__file__).resolve().parent

    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # 1. Test filesystem write & atomic replace in a temp file
    fs_write_ok = False
    atomic_replace_ok = False
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            tf.write("probe_test")
            temp_name = tf.name

        with tempfile.NamedTemporaryFile("w", delete=False) as tf2:
            tf2.write("probe_target")
            target_name = tf2.name

        fs_write_ok = os.path.exists(temp_name)
        os.replace(temp_name, target_name)
        atomic_replace_ok = True

        if os.path.exists(target_name):
            os.remove(target_name)
    except Exception:
        fs_write_ok = False
        atomic_replace_ok = False

    # 2. Test filesystem read
    fs_read_ok = False
    try:
        readme_path = scripts_dir / "README.md"
        if readme_path.exists():
            _ = readme_path.read_text(encoding="utf-8")
            fs_read_ok = True
    except Exception:
        fs_read_ok = False

    # 3. Check skill scripts accessibility
    all_scripts_accessible = True
    missing_scripts = []
    for s_name in REQUIRED_SCRIPTS:
        s_path = scripts_dir / s_name
        if not s_path.exists() or not s_path.is_file():
            all_scripts_accessible = False
            missing_scripts.append(s_name)

    result = {
        "python": True,
        "filesystem_read": fs_read_ok,
        "filesystem_write": fs_write_ok,
        "atomic_replace": atomic_replace_ok,
        "skill_scripts_accessible": all_scripts_accessible,
        "missing_scripts": missing_scripts,
        "cwd": str(Path.cwd()),
        "timestamp_utc": now_iso,
        "skill_version": SKILL_VERSION
    }
    return result


def main():
    res = probe_runtime()
    print(json.dumps(res, indent=2))
    # Exit 0 if basic capabilities are present
    sys.exit(0 if (res["python"] and res["filesystem_write"] and res["skill_scripts_accessible"]) else 1)


if __name__ == "__main__":
    main()
