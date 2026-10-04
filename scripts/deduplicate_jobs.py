#!/usr/bin/env python3
"""
Deduplication Module (deduplicate_jobs.py)
Multi-tier duplicate detection (ATS ID, Canonical URL, SHA256 Fingerprint, SequenceMatcher Similarity)
and deterministic record merging.
"""

import copy
import difflib
import json
import sys
from typing import Dict, Any, List, Optional, Tuple

try:
    from scripts.job_utils import (
        normalize_company,
        normalize_title,
        normalize_location,
        normalize_url,
        extract_ats_requisition_id,
        generate_job_fingerprint
    )
except ImportError:
    from job_utils import (
        normalize_company,
        normalize_title,
        normalize_location,
        normalize_url,
        extract_ats_requisition_id,
        generate_job_fingerprint
    )

# Source tier ranking (lower number = higher authority)
SOURCE_TIER_RANK = {
    "CAREERS": 1,
    "ASHBY": 2,
    "GREENHOUSE": 2,
    "LEVER": 2,
    "WORKABLE": 2,
    "WORKDAY": 2,
    "SMARTRECRUITERS": 2,
    "ICIMS": 2,
    "HIMALAYAS": 3,
    "REMOTEOK": 3,
    "WEWORKREMOTELY": 3,
    "WELLFOUND": 3,
    "YCOMBINATOR": 3,
    "LINKEDIN": 4,
    "AGGREGATOR": 5,
    "UNKNOWN": 6,
}


def get_source_tier(source: Optional[str], url: Optional[str]) -> int:
    """Returns rank order for job source authority."""
    src_upper = (source or "").upper()
    for key, rank in SOURCE_TIER_RANK.items():
        if key in src_upper:
            return rank
    url_str = (url or "").lower()
    if any(ats in url_str for ats in ["greenhouse.io", "ashbyhq.com", "lever.co", "workable.com"]):
        return 2
    if any(nb in url_str for nb in ["himalayas.app", "remoteok.com", "weworkremotely.com", "wellfound.com"]):
        return 3
    if "linkedin.com" in url_str:
        return 4
    return 5


def compute_title_similarity(title1: str, title2: str) -> float:
    """Computes string similarity between two normalized titles using SequenceMatcher."""
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 1.0
    return difflib.SequenceMatcher(None, t1, t2).ratio()


def check_duplicate_signal(incoming: Dict[str, Any], existing: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Evaluates whether an incoming job matches an existing record.
    Returns match metadata if a duplicate signal is found.
    """
    in_ats = extract_ats_requisition_id(incoming.get("canonical_url")) or extract_ats_requisition_id(incoming.get("source_url"))
    ex_ats = extract_ats_requisition_id(existing.get("canonical_url")) or extract_ats_requisition_id(existing.get("source_url"))

    # Signal 1: ATS Requisition ID Match (EXACT)
    if in_ats and ex_ats and in_ats == ex_ats:
        return {
            "is_duplicate": True,
            "signal": "ATS_REQUISITION_ID",
            "confidence": "EXACT",
            "matched_job_id": existing.get("job_id"),
            "details": f"Matching ATS Requisition ID: {in_ats}"
        }

    # Signal 2: Canonical URL Match (VERY_STRONG)
    in_can_url = normalize_url(incoming.get("canonical_url"))
    ex_can_url = normalize_url(existing.get("canonical_url"))
    if in_can_url and ex_can_url and in_can_url == ex_can_url:
        return {
            "is_duplicate": True,
            "signal": "CANONICAL_URL",
            "confidence": "VERY_STRONG",
            "matched_job_id": existing.get("job_id"),
            "details": f"Matching Canonical URL: {in_can_url}"
        }

    # Signal 3: Deterministic SHA256 Fingerprint (STRONG)
    in_fp = incoming.get("job_id") or generate_job_fingerprint(incoming)
    ex_fp = existing.get("job_id") or generate_job_fingerprint(existing)
    if in_fp == ex_fp:
        return {
            "is_duplicate": True,
            "signal": "COMPOSITE_FINGERPRINT",
            "confidence": "STRONG",
            "matched_job_id": existing.get("job_id"),
            "details": f"Matching Fingerprint Hash: {in_fp}"
        }

    # Signal 4: Conservative Entity Similarity (POSSIBLE)
    in_comp = normalize_company(incoming.get("company"))
    ex_comp = normalize_company(existing.get("company"))
    if in_comp and ex_comp and in_comp == ex_comp:
        in_loc = normalize_location(incoming.get("location"))
        ex_loc = normalize_location(existing.get("location"))
        # Location must be compatible
        if in_loc == ex_loc or "remote" in in_loc and "remote" in ex_loc:
            sim = compute_title_similarity(incoming.get("job_title", ""), existing.get("job_title", ""))
            if sim >= 0.88:
                return {
                    "is_duplicate": True,
                    "signal": "HIGH_SIMILARITY_ENTITY",
                    "confidence": "POSSIBLE",
                    "matched_job_id": existing.get("job_id"),
                    "details": f"Company match '{in_comp}', Title similarity {sim:.2f}, Location match"
                }

    return None


def merge_job_records(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely merges incoming duplicate data into existing master record.
    Preserves historical metadata, earliest first_seen_at, latest last_seen_at,
    and authoritative source URLs.
    """
    merged = copy.deepcopy(existing)

    # 1. Timestamps
    first_seen_ex = existing.get("first_seen_at") or ""
    first_seen_in = incoming.get("first_seen_at") or ""
    if first_seen_in and (not first_seen_ex or first_seen_in < first_seen_ex):
        merged["first_seen_at"] = first_seen_in

    last_seen_ex = existing.get("last_seen_at") or ""
    last_seen_in = incoming.get("last_seen_at") or ""
    if last_seen_in and (not last_seen_ex or last_seen_in > last_seen_ex):
        merged["last_seen_at"] = last_seen_in

    # 2. Source & Canonical URL Authority
    ex_tier = get_source_tier(existing.get("source"), existing.get("canonical_url"))
    in_tier = get_source_tier(incoming.get("source"), incoming.get("canonical_url"))

    if in_tier < ex_tier:
        # Incoming is higher authority
        merged["canonical_url"] = incoming.get("canonical_url") or existing.get("canonical_url")
        merged["source"] = incoming.get("source") or existing.get("source")
        if incoming.get("source_url"):
            merged["source_url"] = incoming["source_url"]

    # 3. List fields: union without duplicates
    list_fields = [
        "required_skills", "preferred_skills", "cloud_platforms",
        "programming_languages", "container_tools", "iac_tools",
        "cicd_tools", "security_tools", "observability_tools", "ai_ml_requirements",
        "main_matches", "main_gaps"
    ]
    for field in list_fields:
        ex_list = existing.get(field) or []
        in_list = incoming.get(field) or []
        if isinstance(ex_list, list) and isinstance(in_list, list):
            # Union while preserving order
            seen = set()
            combined = []
            for item in ex_list + in_list:
                item_str = str(item).strip()
                if item_str and item_str.lower() not in seen:
                    seen.add(item_str.lower())
                    combined.append(item_str)
            merged[field] = combined

    # 4. Fill in missing factual fields without overwriting existing data with None/UNKNOWN
    scalar_fields = [
        "posted_date", "experience_min", "experience_max",
        "salary_min", "salary_max", "currency", "salary_period",
        "timezone_requirements", "recommended_resume"
    ]
    for field in scalar_fields:
        ex_val = existing.get(field)
        in_val = incoming.get(field)
        if (ex_val is None or ex_val == "UNKNOWN") and (in_val is not None and in_val != "UNKNOWN"):
            merged[field] = in_val

    # 5. Salary disclosed flag
    if incoming.get("salary_disclosed") is True:
        merged["salary_disclosed"] = True

    return merged


def deduplicate_batch(
    incoming_jobs: List[Dict[str, Any]],
    master_jobs: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Processes a batch of incoming jobs against master dataset.
    Returns:
      (unique_new_jobs, updated_master_records, duplicates_list)
    """
    master_by_id = {j.get("job_id", generate_job_fingerprint(j)): copy.deepcopy(j) for j in master_jobs}
    unique_new = []
    duplicates = []

    for inc in incoming_jobs:
        inc_copy = copy.deepcopy(inc)
        if not inc_copy.get("job_id"):
            inc_copy["job_id"] = generate_job_fingerprint(inc_copy)

        match_meta = None
        for m_id, m_job in master_by_id.items():
            match_meta = check_duplicate_signal(inc_copy, m_job)
            if match_meta:
                # Merge into existing master
                merged_record = merge_job_records(m_job, inc_copy)
                master_by_id[m_id] = merged_record
                inc_copy["status"] = "DUPLICATE"
                inc_copy["duplicate_metadata"] = match_meta
                duplicates.append(inc_copy)
                break

        if not match_meta:
            # Check within the current incoming batch as well
            batch_match = None
            for idx, u_job in enumerate(unique_new):
                batch_match = check_duplicate_signal(inc_copy, u_job)
                if batch_match:
                    unique_new[idx] = merge_job_records(u_job, inc_copy)
                    inc_copy["status"] = "DUPLICATE"
                    inc_copy["duplicate_metadata"] = batch_match
                    duplicates.append(inc_copy)
                    break
            if not batch_match:
                unique_new.append(inc_copy)

    updated_master = list(master_by_id.values())
    return unique_new, updated_master, duplicates


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print("Usage: python3 scripts/deduplicate_jobs.py incoming.jsonl [master.jsonl]")
        print("Deduplicates incoming jobs against existing master dataset.")
        sys.exit(0)

    incoming_file = sys.argv[1]
    master_file = sys.argv[2] if len(sys.argv) > 2 else None

    incoming_jobs = []
    try:
        with open(incoming_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    incoming_jobs.append(json.loads(line))
    except Exception as e:
        print(f"Error reading incoming file: {e}", file=sys.stderr)
        sys.exit(1)

    master_jobs = []
    if master_file:
        try:
            with open(master_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        master_jobs.append(json.loads(line))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error reading master file: {e}", file=sys.stderr)
            sys.exit(1)

    unique_new, updated_master, duplicates = deduplicate_batch(incoming_jobs, master_jobs)

    print(json.dumps({
        "incoming_count": len(incoming_jobs),
        "unique_new_count": len(unique_new),
        "duplicates_detected": len(duplicates),
        "total_master_count": len(updated_master)
    }, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
