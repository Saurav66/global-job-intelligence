#!/usr/bin/env python3
"""
Score Job Module (score_job.py)
Deterministic calculation engine for candidate capability, opportunity attractiveness,
final composite score, resume coverage evaluation, and priority/status derivation.
"""

import json
import sys
from typing import Dict, Any, Optional, Tuple, List

# Capability Scoring Profiles by Role Track (Weights sum to 100)
CAPABILITY_PROFILES: Dict[str, Dict[str, float]] = {
    "DEFAULT": {
        "infrastructure_devops": 20.0,
        "cloud": 15.0,
        "containers_k8s": 10.0,
        "iac_automation": 10.0,
        "experience_fit": 10.0,
        "cicd": 8.0,
        "linux_systems": 7.0,
        "security_devsecops": 5.0,
        "observability": 5.0,
        "scripting": 5.0,
        "ai_rag_alignment": 5.0,
    },
    "AI_PLATFORM": {
        "ai_rag_alignment": 25.0,
        "infrastructure_devops": 15.0,
        "cloud": 15.0,
        "scripting": 12.0,
        "containers_k8s": 10.0,
        "experience_fit": 10.0,
        "iac_automation": 8.0,
        "cicd": 5.0,
        "observability": 0.0,
        "linux_systems": 0.0,
        "security_devsecops": 0.0,
    },
    "CLOUD_SECURITY": {
        "security_devsecops": 25.0,
        "cloud": 20.0,
        "iac_automation": 15.0,
        "infrastructure_devops": 10.0,
        "containers_k8s": 10.0,
        "experience_fit": 10.0,
        "linux_systems": 5.0,
        "cicd": 5.0,
        "observability": 0.0,
        "scripting": 0.0,
        "ai_rag_alignment": 0.0,
    },
    "SRE": {
        "observability": 20.0,
        "infrastructure_devops": 15.0,
        "linux_systems": 15.0,
        "cloud": 15.0,
        "containers_k8s": 10.0,
        "experience_fit": 10.0,
        "cicd": 8.0,
        "iac_automation": 7.0,
        "scripting": 0.0,
        "security_devsecops": 0.0,
        "ai_rag_alignment": 0.0,
    }
}

# Opportunity Scoring Dimensions (Weights sum to 100)
OPPORTUNITY_WEIGHTS: Dict[str, float] = {
    "remote_eligibility": 25.0,
    "compensation": 20.0,
    "company_quality": 15.0,
    "job_freshness": 10.0,
    "career_upside": 10.0,
    "seniority_fit": 8.0,
    "employment_quality": 7.0,
    "timezone_practicality": 5.0,
}


def calculate_weighted_score(
    dimension_scores: Dict[str, Any],
    weight_map: Dict[str, float]
) -> Dict[str, Any]:
    """
    Computes weighted score with dynamic weight re-normalization for UNKNOWN/null values.
    If a dimension score is None, 'UNKNOWN', or missing, its weight is omitted and
    remaining weights are scaled proportionally to 100.
    """
    total_evaluated_weight = 0.0
    accumulated_points = 0.0
    omitted_dimensions = []

    for dim, weight in weight_map.items():
        if weight <= 0.0:
            continue
        val = dimension_scores.get(dim)
        if val is None or val == "UNKNOWN":
            omitted_dimensions.append(dim)
            continue
        try:
            num_val = float(val)
            # Clamp between 0 and 100
            clamped_val = max(0.0, min(100.0, num_val))
            accumulated_points += clamped_val * weight
            total_evaluated_weight += weight
        except (ValueError, TypeError):
            omitted_dimensions.append(dim)

    if total_evaluated_weight <= 0.0:
        return {
            "score": 0.0,
            "evaluated_weight": 0.0,
            "omitted_dimensions": omitted_dimensions,
        }

    # Normalize proportionally to 100-point scale
    normalized_score = (accumulated_points / total_evaluated_weight)
    return {
        "score": round(normalized_score, 1),
        "evaluated_weight": round(total_evaluated_weight, 1),
        "omitted_dimensions": omitted_dimensions,
    }


def compute_final_score(
    capability_score: float,
    opportunity_score: float,
    cap_weight: float = 0.60,
    opp_weight: float = 0.40
) -> float:
    """Computes composite final score (0.0 to 100.0)."""
    cap_clamped = max(0.0, min(100.0, float(capability_score)))
    opp_clamped = max(0.0, min(100.0, float(opportunity_score)))
    final = (cap_clamped * cap_weight) + (opp_clamped * opp_weight)
    return round(final, 1)


def derive_priority(final_score: float) -> str:
    """Derives priority tier string from final score."""
    if final_score >= 90.0:
        return "A_PLUS"
    elif final_score >= 85.0:
        return "A"
    elif final_score >= 75.0:
        return "B"
    elif final_score >= 65.0:
        return "C"
    else:
        return "LOW"


def derive_status(
    final_score: float,
    capability_score: float,
    resume_coverage_score: Optional[float],
    hard_blocker: bool = False,
    remote_type: str = "UNKNOWN",
    candidate_location_eligible: Any = True,
    current_status: Optional[str] = None
) -> str:
    """
    Deterministically derives job status adhering to strict precedence:
      1. EXPIRED
      2. REJECTED (hard blocker)
      3. DUPLICATE
      4. REVIEW_LOCATION (ambiguous remote boundaries)
      5. REVIEW_SALARY
      6. HOLD_RESUME_UPDATE (High capability >= 85 but resume representation < 75)
      7. Score-derived Shortlists (SHORTLIST_A_PLUS, SHORTLIST_A, SHORTLIST_B, SHORTLIST_C, REJECTED)
    """
    if current_status == "EXPIRED":
        return "EXPIRED"
    if hard_blocker:
        return "REJECTED"
    if current_status == "DUPLICATE":
        return "DUPLICATE"
    
    # Location ambiguity check
    if remote_type == "UNKNOWN" or candidate_location_eligible == "UNKNOWN" or current_status == "REVIEW_LOCATION":
        return "REVIEW_LOCATION"
    
    # Explicit salary review preservation
    if current_status == "REVIEW_SALARY":
        return "REVIEW_SALARY"
    
    # Check for Resume Representation Hold
    if resume_coverage_score is not None and resume_coverage_score != "UNKNOWN":
        try:
            rc_val = float(resume_coverage_score)
            if capability_score >= 85.0 and rc_val < 75.0:
                return "HOLD_RESUME_UPDATE"
        except (ValueError, TypeError):
            pass

    # Score-derived tiers
    if final_score >= 90.0:
        return "SHORTLIST_A_PLUS"
    elif final_score >= 85.0:
        return "SHORTLIST_A"
    elif final_score >= 75.0:
        return "SHORTLIST_B"
    elif final_score >= 65.0:
        return "SHORTLIST_C"
    else:
        return "REJECTED"


def score_job_record(job: Dict[str, Any], profile_name: str = "DEFAULT") -> Dict[str, Any]:
    """
    Evaluates a full job record dict, calculating capability, opportunity,
    final score, priority, and status.
    """
    # Select capability profile
    role_family = (job.get("role_family") or "").upper()
    if "AI" in role_family:
        profile_key = "AI_PLATFORM"
    elif "SECURITY" in role_family or "DEVSECOPS" in role_family:
        profile_key = "CLOUD_SECURITY"
    elif "SRE" in role_family:
        profile_key = "SRE"
    else:
        profile_key = profile_name if profile_name in CAPABILITY_PROFILES else "DEFAULT"
        
    cap_weights = CAPABILITY_PROFILES[profile_key]
    
    # Extract capability dimension scores
    cap_dims = job.get("capability_dimensions", {})
    # If capability_score is already directly supplied by agent:
    if not cap_dims and job.get("candidate_capability_score") is not None:
        cap_score = float(job["candidate_capability_score"])
        cap_meta = {"score": cap_score, "evaluated_weight": 100.0, "omitted_dimensions": []}
    else:
        cap_meta = calculate_weighted_score(cap_dims, cap_weights)
        cap_score = cap_meta["score"]
    
    # Extract opportunity dimension scores
    opp_dims = job.get("opportunity_dimensions", {})
    if not opp_dims and job.get("opportunity_score") is not None:
        opp_score = float(job["opportunity_score"])
        opp_meta = {"score": opp_score, "evaluated_weight": 100.0, "omitted_dimensions": []}
    else:
        opp_meta = calculate_weighted_score(opp_dims, OPPORTUNITY_WEIGHTS)
        opp_score = opp_meta["score"]
        
    final = compute_final_score(cap_score, opp_score)
    priority = derive_priority(final)
    
    status = derive_status(
        final_score=final,
        capability_score=cap_score,
        resume_coverage_score=job.get("resume_coverage_score"),
        hard_blocker=bool(job.get("hard_blocker", False)),
        remote_type=job.get("remote_type", "UNKNOWN"),
        candidate_location_eligible=job.get("candidate_location_eligible", True),
        current_status=job.get("status")
    )
    
    result = dict(job)
    result["candidate_capability_score"] = cap_score
    result["opportunity_score"] = opp_score
    result["final_score"] = final
    result["priority"] = priority
    result["status"] = status
    result["scoring_metadata"] = {
        "capability_profile_used": profile_key,
        "capability_omitted": cap_meta["omitted_dimensions"],
        "opportunity_omitted": opp_meta["omitted_dimensions"]
    }
    return result


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python3 scripts/score_job.py [job_file.json]")
        print("Calculates capability, opportunity, final score, priority, and status for job JSON.")
        sys.exit(0)

    try:
        if len(sys.argv) > 1 and sys.argv[1] != "-":
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
    except Exception as e:
        print(f"Error loading JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    scored = score_job_record(data)
    print(json.dumps(scored, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
