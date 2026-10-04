#!/usr/bin/env python3
"""
Candidate Context Validator (context_validator.py)
Validates private candidate context JSON against references/candidate_context.md.
Evaluates context sufficiency levels (MINIMUM, STANDARD, ENRICHED), checks enum validity,
and detects configuration errors without requiring heavyweight libraries.
"""

import json
import sys
from typing import Dict, Any, List, Tuple

VALID_CONFIDENCE_LEVELS = {"CORE", "STRONG", "WORKING", "EXPOSURE"}
VALID_REMOTE_PREFS = {"REMOTE_ONLY", "REMOTE_PREFERRED", "HYBRID_ACCEPTABLE", "ANY", "UNKNOWN"}
VALID_PERIODS = {"ANNUAL", "MONTHLY", "HOURLY", "UNKNOWN"}


def validate_candidate_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates candidate context dictionary.
    Returns:
      {
        "valid": bool,
        "sufficiency_level": "MINIMUM" | "STANDARD" | "ENRICHED" | "INSUFFICIENT",
        "errors": List[str],
        "warnings": List[str]
      }
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(context, dict):
        return {
            "valid": False,
            "sufficiency_level": "INSUFFICIENT",
            "errors": ["Candidate context must be a JSON object / dictionary."],
            "warnings": []
        }

    # 1. Candidate Info
    cand = context.get("candidate", {})
    if not isinstance(cand, dict) or not cand:
        errors.append("Missing required 'candidate' section.")
    else:
        exp_years = cand.get("experience_years")
        if exp_years is None:
            errors.append("Missing required 'candidate.experience_years'.")
        else:
            try:
                exp_num = float(exp_years)
                if exp_num < 0:
                    errors.append("'candidate.experience_years' cannot be negative.")
            except (ValueError, TypeError):
                errors.append(f"'candidate.experience_years' ({exp_years}) must be a valid number.")

    # 2. Location Info
    loc = context.get("location", {})
    if not isinstance(loc, dict) or not loc:
        errors.append("Missing required 'location' section.")
    else:
        country = loc.get("country")
        if not country or str(country).strip() == "":
            errors.append("Missing required 'location.country'.")
        if not loc.get("timezone"):
            warnings.append("Missing 'location.timezone'; timezone overlap calculations will be estimated.")

    # 3. Capabilities
    caps = context.get("capabilities", {})
    if not isinstance(caps, dict) or not caps:
        errors.append("Missing required 'capabilities' section.")
    else:
        primary_domains = caps.get("primary_domains", [])
        if not isinstance(primary_domains, list) or len(primary_domains) == 0:
            errors.append("Missing required 'capabilities.primary_domains' (must be a non-empty list).")

        # Check for duplicates in list fields
        for field, items in caps.items():
            if isinstance(items, list):
                seen = set()
                for it in items:
                    it_norm = str(it).strip().lower()
                    if it_norm in seen:
                        warnings.append(f"Duplicate entry '{it}' in capabilities.{field}.")
                    seen.add(it_norm)

    # 4. Role Preferences
    role_prefs = context.get("role_preferences", {})
    if not isinstance(role_prefs, dict) or not role_prefs:
        errors.append("Missing required 'role_preferences' section.")
    else:
        prim_roles = role_prefs.get("primary", [])
        if not isinstance(prim_roles, list) or len(prim_roles) == 0:
            errors.append("Missing required 'role_preferences.primary' (must be a non-empty list of target roles).")

    # 5. Capability Confidence Map
    conf_map = context.get("capability_confidence", {})
    if isinstance(conf_map, dict):
        for cap_name, conf_level in conf_map.items():
            conf_upper = str(conf_level).upper().strip()
            if conf_upper not in VALID_CONFIDENCE_LEVELS:
                errors.append(
                    f"Invalid confidence level '{conf_level}' for '{cap_name}'. Must be one of: {sorted(VALID_CONFIDENCE_LEVELS)}"
                )

    # 6. Resume Variants
    resumes = context.get("resume_variants", [])
    if isinstance(resumes, list):
        resume_ids = set()
        for idx, res in enumerate(resumes, start=1):
            if not isinstance(res, dict):
                errors.append(f"Resume variant #{idx} must be an object.")
                continue
            r_id = res.get("id")
            if not r_id:
                errors.append(f"Resume variant #{idx} is missing required 'id'.")
            elif r_id in resume_ids:
                errors.append(f"Duplicate resume variant id '{r_id}'.")
            else:
                resume_ids.add(r_id)

    # 7. Compensation
    comp = context.get("compensation", {})
    if isinstance(comp, dict) and comp:
        sal_min = comp.get("minimum")
        sal_target = comp.get("target")
        min_num, target_num = None, None

        if sal_min is not None:
            try:
                min_num = float(sal_min)
                if min_num < 0:
                    errors.append("'compensation.minimum' cannot be negative.")
            except (ValueError, TypeError):
                errors.append(f"'compensation.minimum' ({sal_min}) is not a valid number.")

        if sal_target is not None:
            try:
                target_num = float(sal_target)
                if target_num < 0:
                    errors.append("'compensation.target' cannot be negative.")
            except (ValueError, TypeError):
                errors.append(f"'compensation.target' ({sal_target}) is not a valid number.")

        if min_num is not None and target_num is not None:
            if min_num > target_num:
                errors.append(f"'compensation.minimum' ({min_num}) cannot exceed 'compensation.target' ({target_num}).")

        period = comp.get("period")
        if period and str(period).upper() not in VALID_PERIODS:
            errors.append(f"Invalid compensation period '{period}'. Must be one of: {sorted(VALID_PERIODS)}")

    # 8. Employment Preferences
    emp_prefs = context.get("employment_preferences", {})
    if isinstance(emp_prefs, dict) and emp_prefs:
        r_pref = emp_prefs.get("remote_preference")
        if r_pref and str(r_pref).upper() not in VALID_REMOTE_PREFS:
            errors.append(f"Invalid remote_preference '{r_pref}'. Must be one of: {sorted(VALID_REMOTE_PREFS)}")

    # 9. Sufficiency Level Calculation
    is_valid = len(errors) == 0
    if not is_valid:
        sufficiency = "INSUFFICIENT"
    else:
        # Check for STANDARD level
        has_tools = bool(caps.get("cloud") and caps.get("containers") and caps.get("iac"))
        has_remote_pref = bool(emp_prefs.get("remote_preference"))
        has_resumes = bool(len(resumes) > 0)
        is_standard = has_tools and has_remote_pref and has_resumes

        # Check for ENRICHED level
        has_comp = bool(comp.get("minimum") or comp.get("target"))
        has_confidence = bool(len(conf_map) > 0)
        has_search_prefs = bool(context.get("search_preferences"))
        is_enriched = is_standard and has_comp and has_confidence and has_search_prefs

        if is_enriched:
            sufficiency = "ENRICHED"
        elif is_standard:
            sufficiency = "STANDARD"
        else:
            sufficiency = "MINIMUM"

    return {
        "valid": is_valid,
        "sufficiency_level": sufficiency,
        "errors": errors,
        "warnings": warnings
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: python3 scripts/context_validator.py <candidate_context.json>")
        print("Validates candidate private context against references/candidate_context.md.")
        sys.exit(0)

    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON from '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)

    result = validate_candidate_context(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
