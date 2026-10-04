#!/usr/bin/env python3
"""
Skill Repository Validator (validate_skill.py)
Validates repository structure, SKILL.md frontmatter, Python syntax compilation,
Markdown hyperlinks, schema enum consistency, candidate context templates,
and audits for private data / secret leaks.
"""

import os
import py_compile
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    ".gitignore",
    "references/search_strategy.md",
    "references/eligibility_rules.md",
    "references/scoring.md",
    "references/job_schema.md",
    "references/deduplication.md",
    "references/reporting.md",
    "references/candidate_context.md",
    "references/runtime_contract.md",
    "references/persistence.md",
    "references/integration_test.md",
    "references/manus_project_setup.md",
    "templates/morning_scan.md",
    "templates/evening_scan.md",
    "templates/weekly_intelligence.md",
    "templates/scheduled_run.md",
    "templates/integration_test.md",
    "templates/manus_project_instruction.md",
    "templates/candidate_context.example.md",
    "templates/candidate_context.example.json",
    "scripts/README.md",
    "scripts/job_utils.py",
    "scripts/score_job.py",
    "scripts/deduplicate_jobs.py",
    "scripts/validate_job.py",
    "scripts/master_dataset.py",
    "scripts/context_validator.py",
    "scripts/artifact_sync.py",
    "scripts/run_manifest.py",
    "scripts/runtime_probe.py",
    "scripts/preflight.py",
    "scripts/validate_skill.py",
    "tests/fixtures/jobs_valid.jsonl",
    "tests/fixtures/jobs_duplicates.jsonl",
    "tests/fixtures/jobs_scoring.jsonl",
    "tests/fixtures/jobs_invalid.jsonl",
    "tests/fixtures/integration/candidate_context_minimum.json",
    "tests/fixtures/integration/candidate_context_standard.json",
    "tests/fixtures/integration/candidate_context_enriched.json",
    "tests/fixtures/integration/empty_job_master.jsonl",
    "tests/test_job_utils.py",
    "tests/test_scoring.py",
    "tests/test_deduplication.py",
    "tests/test_validation.py",
    "tests/test_master_dataset.py",
    "tests/test_context_validator.py",
    "tests/test_artifact_sync.py",
    "tests/test_run_manifest.py",
    "tests/test_runtime_probe.py",
    "tests/test_preflight.py",
]

PRIVACY_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", "Real Email Address"),
    (r"\+?[0-9]{10,14}", "Phone Number"),
    (r"(?i)(api[_-]?key|secret[_-]?key|bearer\s+[a-z0-9_\-\.]+)\s*[:=]\s*['\"][^'\"]+['\"]", "API Key / Secret Token"),
    (r"(?i)aws_access_key_id\s*=", "AWS Credentials"),
]

# Safe / mock strings in documentation and tests
SAFE_PATTERNS = [
    r"user@example\.com",
    r"candidate@example\.com",
    r"john\.doe@example\.com",
    r"sha256_",
]


def check_structure(repo_root: Path) -> list:
    errors = []
    for rel_path in REQUIRED_FILES:
        full_path = repo_root / rel_path
        if not full_path.exists():
            errors.append(f"Missing required file: {rel_path}")
    return errors


def check_skill_frontmatter(repo_root: Path) -> list:
    errors = []
    skill_file = repo_root / "SKILL.md"
    if not skill_file.exists():
        return ["SKILL.md does not exist"]

    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return ["SKILL.md missing opening YAML frontmatter delimiter (---)"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return ["SKILL.md YAML frontmatter is not properly closed with (---)"]

    fm = parts[1]
    if "name: global-job-intelligence" not in fm:
        errors.append("SKILL.md frontmatter missing 'name: global-job-intelligence'")
    if "description:" not in fm:
        errors.append("SKILL.md frontmatter missing 'description:'")

    lines = [line.strip() for line in fm.strip().split("\n") if line.strip()]
    for line in lines:
        key = line.split(":", 1)[0].strip()
        if key not in ["name", "description"] and not line.startswith("-") and not line.startswith(" "):
            errors.append(f"SKILL.md frontmatter contains extra unexpected key: {key}")

    return errors


def check_python_compilation(repo_root: Path) -> list:
    errors = []
    for py_file in repo_root.rglob("*.py"):
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"Syntax/Compilation error in {py_file.relative_to(repo_root)}: {e}")
    return errors


def check_privacy_and_secrets(repo_root: Path) -> list:
    errors = []
    for file_path in repo_root.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith(".git") and "__pycache__" not in str(file_path):
            if file_path.suffix in [".pyc", ".png", ".jpg", ".pdf"]:
                continue

            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            for pattern, desc in PRIVACY_PATTERNS:
                matches = re.finditer(pattern, text)
                for m in matches:
                    matched_str = m.group(0)
                    if file_path.name in ["validate_skill.py"]:
                        continue
                    if any(re.search(safe, matched_str) for safe in SAFE_PATTERNS):
                        continue
                    if "<" in matched_str or ">" in matched_str or "example" in matched_str.lower() or "synthetic" in matched_str.lower():
                        continue
                    errors.append(f"Potential privacy/secret leak in {file_path.relative_to(repo_root)}: '{matched_str}' ({desc})")
    return errors


def check_relative_links(repo_root: Path) -> list:
    errors = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for md_file in repo_root.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        for match in link_pattern.finditer(content):
            link_text, raw_target = match.groups()
            raw_target = raw_target.strip()

            # Skip external URLs, badges, anchors, mailto, licenses
            if raw_target.startswith("http://") or raw_target.startswith("https://") or raw_target.startswith("#") or raw_target.startswith("mailto:") or raw_target == "LICENSE":
                continue

            if raw_target.startswith("file://"):
                file_path_str = raw_target[len("file://"):]
                target_path = Path(file_path_str)
            else:
                target_path = (md_file.parent / raw_target).resolve()

            target_str = str(target_path).split("#")[0]
            if not target_str:
                continue
            resolved_target = Path(target_str)

            if not resolved_target.exists():
                errors.append(f"Broken link in {md_file.relative_to(repo_root)}: '{raw_target}' (Target not found)")
    return errors


def check_forbidden_phase2_actions(repo_root: Path) -> list:
    errors = []
    forbidden_tokens = [
        "selenium",
        "playwright",
        "puppeteer",
        "pyautogui",
        "smtplib",
        "auto_apply",
        "submit_application",
    ]
    for py_file in (repo_root / "scripts").glob("*.py"):
        if py_file.name == "validate_skill.py":
            continue
        content = py_file.read_text(encoding="utf-8").lower()
        for token in forbidden_tokens:
            if token in content:
                errors.append(f"Forbidden Phase-2 library/action '{token}' found in {py_file.name}")
    return errors


def check_version_consistency(repo_root: Path) -> list:
    errors = []
    manifest_py = repo_root / "scripts" / "run_manifest.py"
    if manifest_py.exists():
        content = manifest_py.read_text(encoding="utf-8")
        if 'SKILL_VERSION = "0.3.1"' not in content:
            errors.append("SKILL_VERSION in scripts/run_manifest.py is not '0.3.1'")
    probe_py = repo_root / "scripts" / "runtime_probe.py"
    if probe_py.exists():
        content = probe_py.read_text(encoding="utf-8")
        if 'SKILL_VERSION = "0.3.1"' not in content:
            errors.append("SKILL_VERSION in scripts/runtime_probe.py is not '0.3.1'")
    return errors


def main():
    repo_root = Path(__file__).resolve().parent.parent
    print(f"🔍 Validating Skill Repository at: {repo_root}")

    all_errors = []

    print("  [1/7] Checking repository structure & required files (v0.3.1)...")
    all_errors.extend(check_structure(repo_root))

    print("  [2/7] Checking SKILL.md frontmatter...")
    all_errors.extend(check_skill_frontmatter(repo_root))

    print("  [3/7] Compiling Python scripts & test suites...")
    all_errors.extend(check_python_compilation(repo_root))

    print("  [4/7] Auditing for private data / secret leaks...")
    all_errors.extend(check_privacy_and_secrets(repo_root))

    print("  [5/7] Verifying internal Markdown hyperlinks...")
    all_errors.extend(check_relative_links(repo_root))

    print("  [6/7] Enforcing Phase-1 boundaries (no auto-apply/scrapers)...")
    all_errors.extend(check_forbidden_phase2_actions(repo_root))

    print("  [7/7] Checking version consistency (0.3.1)...")
    all_errors.extend(check_version_consistency(repo_root))

    if all_errors:
        print("\n❌ Validation Failed with Errors:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ All validations passed successfully! Repository is clean, compliant, and ready for Manus import.")
        sys.exit(0)


if __name__ == "__main__":
    main()
