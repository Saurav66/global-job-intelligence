#!/usr/bin/env python3
"""
Job Record Validator (validate_job.py)
Validates normalized job records against references/job_schema.md.
Zero-dependency, returns structured actionable errors and warnings.
"""

import json
import re
import sys
from typing import Dict, Any, List, Tuple

# Schema Allowed Enums
VALID_REMOTE_TYPES = {
    "REMOTE_GLOBAL",
    "REMOTE_INDIA",
    "REMOTE_APAC_INDIA_ALLOWED",
    "REMOTE_INTERNATIONAL_INDIA_ALLOWED",
    "REMOTE_COUNTRY_RESTRICTED",
    "HYBRID",
    "ONSITE",
    "UNKNOWN",
}

VALID_ROLE_FAMILIES = {
    "CORE_DEVOPS_PLATFORM",
    "SECURITY_INFRASTRUCTURE",
    "AI_INFRASTRUCTURE",
    "CLIENT_DEPLOYMENT",
    "UNKNOWN",
}

VALID_STATUSES = {
    "NEW",
    "SHORTLIST_A_PLUS",
    "SHORTLIST_A",
    "SHORTLIST_B",
    "SHORTLIST_C",
    "HOLD_RESUME_UPDATE",
    "REVIEW_LOCATION",
    "REVIEW_SALARY",
    "DUPLICATE",
    "REJECTED",
    "EXPIRED",
}

VALID_PRIORITIES = {"A_PLUS", "A", "B", "C", "LOW", "REJECT"}

REQUIRED_FIELDS = [
    "job_id",
    "first_seen_at",
    "last_seen_at",
    "company",
    "job_title",
    "role_family",
    "source",
    "source_url",
    "canonical_url",
    "location",
    "remote_type",
    "candidate_location_eligible",
]

LIST_FIELDS = [
    "required_skills",
    "preferred_skills",
    "cloud_platforms",
    "programming_languages",
    "container_tools",
    "iac_tools",
    "cicd_tools",
    "security_tools",
    "observability_tools",
    "ai_ml_requirements",
    "main_matches",
    "main_gaps",
]


def validate_job_record(job: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Validates a single job dictionary against the Phase-1 schema.
    Returns: (is_valid, list_of_errors, list_of_warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(job, dict):
        return False, ["Job record must be a JSON object / dictionary"], []

    # 1. Required Fields
    for field in REQUIRED_FIELDS:
        val = job.get(field)
        if val is None or val == "":
            errors.append(f"Missing or empty required field: '{field}'")

    # 2. Enums
    remote_type = job.get("remote_type")
    if remote_type and remote_type not in VALID_REMOTE_TYPES:
        errors.append(
            f"Invalid remote_type '{remote_type}'. Must be one of: {sorted(VALID_REMOTE_TYPES)}"
        )

    role_family = job.get("role_family")
    if role_family and role_family not in VALID_ROLE_FAMILIES:
        errors.append(
            f"Invalid role_family '{role_family}'. Must be one of: {sorted(VALID_ROLE_FAMILIES)}"
        )

    status = job.get("status")
    if status:
        if status == "APPLIED":
            errors.append("Status 'APPLIED' is strictly forbidden in Phase 1 (Discovery & Qualification Only)")
        elif status not in VALID_STATUSES:
            errors.append(f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}")

    priority = job.get("priority")
    if priority and priority not in VALID_PRIORITIES:
        errors.append(
            f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}"
        )

    # 3. Score Validations (0.0 to 100.0)
    score_fields = [
        "candidate_capability_score",
        "opportunity_score",
        "final_score",
        "resume_coverage_score",
    ]
    for sf in score_fields:
        s_val = job.get(sf)
        if s_val is not None and s_val != "UNKNOWN":
            try:
                num = float(s_val)
                if num < 0.0 or num > 100.0:
                    errors.append(f"Score '{sf}' ({num}) must be between 0.0 and 100.0")
            except (ValueError, TypeError):
                errors.append(f"Score '{sf}' ({s_val}) is not a valid number")

    # 4. Experience Range Consistency
    exp_min = job.get("experience_min")
    exp_max = job.get("experience_max")
    exp_min_num, exp_max_num = None, None

    if exp_min is not None and exp_min != "UNKNOWN":
        try:
            exp_min_num = float(exp_min)
            if exp_min_num < 0:
                errors.append(f"experience_min ({exp_min_num}) cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"experience_min ({exp_min}) is not a valid number")

    if exp_max is not None and exp_max != "UNKNOWN":
        try:
            exp_max_num = float(exp_max)
            if exp_max_num < 0:
                errors.append(f"experience_max ({exp_max_num}) cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"experience_max ({exp_max}) is not a valid number")

    if exp_min_num is not None and exp_max_num is not None:
        if exp_min_num > exp_max_num:
            errors.append(
                f"experience_min ({exp_min_num}) cannot exceed experience_max ({exp_max_num})"
            )

    # 5. Salary Range Consistency
    sal_min = job.get("salary_min")
    sal_max = job.get("salary_max")
    sal_min_num, sal_max_num = None, None

    if sal_min is not None and sal_min != "UNKNOWN":
        try:
            sal_min_num = float(sal_min)
            if sal_min_num < 0:
                errors.append(f"salary_min ({sal_min_num}) cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"salary_min ({sal_min}) is not a valid number")

    if sal_max is not None and sal_max != "UNKNOWN":
        try:
            sal_max_num = float(sal_max)
            if sal_max_num < 0:
                errors.append(f"salary_max ({sal_max_num}) cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"salary_max ({sal_max}) is not a valid number")

    if sal_min_num is not None and sal_max_num is not None:
        if sal_min_num > sal_max_num:
            errors.append(
                f"salary_min ({sal_min_num}) cannot exceed salary_max ({sal_max_num})"
            )

    sal_disclosed = job.get("salary_disclosed")
    if sal_disclosed is not None and not isinstance(sal_disclosed, bool):
        errors.append("salary_disclosed must be a boolean (true/false)")

    # 6. List Fields Type Check
    for lf in LIST_FIELDS:
        if lf in job:
            val = job[lf]
            if val is not None and not isinstance(val, list):
                errors.append(f"Field '{lf}' must be a list of strings, got {type(val).__name__}")

    # 7. URLs Check
    for url_field in ["canonical_url", "source_url"]:
        u_val = job.get(url_field)
        if u_val and not (u_val.startswith("http://") or u_val.startswith("https://")):
            warnings.append(f"{url_field} '{u_val}' does not start with http/https")

    # 8. Hard blocker check
    hb = job.get("hard_blocker")
    if hb is not None and not isinstance(hb, bool):
        errors.append("hard_blocker must be a boolean (true/false)")
    if hb is True and status and status != "REJECTED":
        errors.append(f"Record with hard_blocker=true must have status='REJECTED', found '{status}'")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: python3 scripts/validate_job.py <job.json | jobs.jsonl>")
        print("Validates job records against Phase-1 schema definitions.")
        sys.exit(0)

    target_file = sys.argv[1]
    records = []
    try:
        if target_file.endswith(".jsonl"):
            with open(target_file, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, start=1):
                    if line.strip():
                        records.append((line_idx, json.loads(line)))
        else:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = list(enumerate(data, start=1))
                else:
                    records = [(1, data)]
    except Exception as e:
        print(f"Error reading file {target_file}: {e}", file=sys.stderr)
        sys.exit(1)

    all_valid = True
    total_errors = 0
    results = []

    for idx, job in records:
        valid, errs, warns = validate_job_record(job)
        if not valid:
            all_valid = False
            total_errors += len(errs)
        results.append({
            "record_index": idx,
            "job_id": job.get("job_id", "UNKNOWN"),
            "valid": valid,
            "errors": errs,
            "warnings": warns
        })

    print(json.dumps({
        "all_valid": all_valid,
        "total_records": len(records),
        "total_errors": total_errors,
        "details": results if not all_valid else "All records valid"
    }, indent=2))

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
