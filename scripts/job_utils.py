#!/usr/bin/env python3
"""
Job Utilities Module (job_utils.py)
Standardized normalization, text cleaning, URL canonicalization,
and deterministic job fingerprint generation.
"""

import hashlib
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

# Common tracking / noise query parameters to strip from job URLs
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gh_src", "lever-source", "lever-origin", "ref", "reference",
    "source", "tracking", "trk", "trkcode", "fbclid", "gclid",
    "msclkid", "mc_cid", "mc_eid", "ia_src", "from", "sid"
}

# Legal & organizational suffixes for normalized company names
COMPANY_SUFFIX_REGEX = re.compile(
    r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|technologies|tech|solutions|systems|software|co|gmbh|sa|bv|pvt|plc)\b\.?",
    re.IGNORECASE
)

# Common title prefixes, levels, and suffixes that can be cleaned conservatively for matching
TITLE_NOISE_REGEX = re.compile(
    r"(\s*[\(\[\-–—]\s*(remote|work from anywhere|hybrid|onsite|worldwide|global|anywhere|full[- ]time|contract|india|us|emea|apac)[\)\]]?\s*)+$",
    re.IGNORECASE
)


def normalize_text(value: Optional[str]) -> str:
    """Conservatively trims and collapses whitespace in a string."""
    if not value or not isinstance(value, str):
        return ""
    # Collapse multiple whitespaces and trim
    return re.sub(r"\s+", " ", value.strip())


def normalize_company(value: Optional[str]) -> str:
    """
    Normalizes company names for deterministic comparison.
    Lowercases, removes legal entity noise (Inc, LLC, Ltd), strips punctuation.
    """
    text = normalize_text(value).lower()
    if not text:
        return ""
    # Remove legal suffixes
    text = COMPANY_SUFFIX_REGEX.sub("", text)
    # Remove non-alphanumeric except spaces
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(value: Optional[str]) -> str:
    """
    Normalizes job titles for comparison without erasing genuine role differences.
    Lowercases, cleans trailing remote/workplace tags and punctuation.
    """
    text = normalize_text(value).lower()
    if not text:
        return ""
    # Strip trailing remote / workplace tags (e.g. "Senior DevOps Engineer - Remote")
    text = TITLE_NOISE_REGEX.sub("", text)
    # Standardize abbreviations
    text = re.sub(r"\bsr\.?\b", "senior", text)
    text = re.sub(r"\bjr\.?\b", "junior", text)
    text = re.sub(r"\beng\.?\b", "engineer", text)
    text = re.sub(r"\bk8s\b", "kubernetes", text)
    # Clean special punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_location(value: Optional[str]) -> str:
    """
    Categorizes and normalizes location strings into comparable geographic buckets.
    """
    text = normalize_text(value).lower()
    if not text:
        return "unknown"
    
    if any(k in text for k in ["worldwide", "anywhere", "global remote", "remote - global", "remote (global)", "remote - worldwide"]):
        return "remote-global"
    if "india" in text:
        return "india-remote" if "remote" in text else "india-onsite"
    if any(k in text for k in ["us only", "united states", "usa", "us remote", "remote - us"]):
        return "us-remote"
    if any(k in text for k in ["uk", "united kingdom", "london", "emea", "europe", "germany", "france"]):
        return "emea-remote" if "remote" in text else "emea-regional"
    if any(k in text for k in ["apac", "singapore", "australia", "japan"]):
        return "apac-remote" if "remote" in text else "apac-regional"
    if "remote" in text:
        return "remote-unspecified"
    
    # Generic alphanumeric clean
    clean = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", clean).strip()


def normalize_url(value: Optional[str]) -> str:
    """
    Normalizes URLs by lowercasing scheme/host, stripping trailing slashes,
    and removing marketing/tracking query parameters (utm_*, ref, etc.)
    while preserving functional path segments and requisition parameters.
    """
    if not value or not isinstance(value, str):
        return ""
    url_str = value.strip()
    if not url_str:
        return ""
    
    try:
        parsed = urlparse(url_str)
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        # Remove default ports
        if netloc.endswith(":443") and scheme == "https":
            netloc = netloc[:-4]
        elif netloc.endswith(":80") and scheme == "http":
            netloc = netloc[:-3]
        
        path = parsed.path.rstrip("/")
        if not path:
            path = ""
            
        # Parse query string and remove known tracking params
        query_tuples = parse_qsl(parsed.query, keep_blank_values=False)
        filtered_query = [
            (k, v) for k, v in query_tuples
            if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
        ]
        # Sort query params for deterministic ordering
        filtered_query.sort(key=lambda x: x[0])
        new_query = urlencode(filtered_query)
        
        return urlunparse((scheme, netloc, path, "", new_query, ""))
    except Exception:
        return url_str.rstrip("/")


def extract_ats_requisition_id(url: Optional[str]) -> Optional[str]:
    """
    Extracts deterministic ATS requisition identifiers from standard ATS URL patterns.
    Examples:
      - Greenhouse: boards.greenhouse.io/{company}/jobs/{job_id} -> gh:{company}:{job_id}
      - Ashby: jobs.ashbyhq.com/{company}/{job_id} -> ashby:{company}:{job_id}
      - Lever: jobs.lever.co/{company}/{uuid} -> lever:{company}:{uuid}
      - Workable: apply.workable.com/{company}/j/{id} -> workable:{company}:{id}
    """
    if not url:
        return None
    
    norm = normalize_url(url)
    
    # Greenhouse
    gh_match = re.search(r"boards\.greenhouse\.io/([^/]+)/jobs/([0-9a-zA-Z_-]+)", norm)
    if gh_match:
        return f"gh:{gh_match.group(1).lower()}:{gh_match.group(2)}"
    
    # Ashby
    ashby_match = re.search(r"jobs\.ashbyhq\.com/([^/]+)/([0-9a-zA-Z_-]+)", norm)
    if ashby_match:
        return f"ashby:{ashby_match.group(1).lower()}:{ashby_match.group(2).lower()}"
    
    # Lever
    lever_match = re.search(r"jobs\.lever\.co/([^/]+)/([0-9a-zA-Z_-]+)", norm)
    if lever_match:
        return f"lever:{lever_match.group(1).lower()}:{lever_match.group(2).lower()}"
    
    # Workable
    workable_match = re.search(r"apply\.workable\.com/([^/]+)/j/([0-9a-zA-Z_-]+)", norm)
    if workable_match:
        return f"workable:{workable_match.group(1).lower()}:{workable_match.group(2)}"
    
    return None


def generate_job_fingerprint(job: Dict[str, Any]) -> str:
    """
    Generates a deterministic SHA-256 fingerprint for a job record.
    
    Priority hierarchy:
    1. ATS Requisition ID if extractable from canonical_url or source_url.
    2. Canonical URL if trustworthy (ATS or company domain).
    3. Composite entity fingerprint: SHA256(norm(company) | norm(title) | norm(location_bucket)).
    
    Does NOT include volatile fields like timestamps, scores, notes, or salaries.
    """
    canonical_url = normalize_url(job.get("canonical_url") or "")
    source_url = normalize_url(job.get("source_url") or "")
    
    # Signal 1: ATS Requisition ID
    ats_id = extract_ats_requisition_id(canonical_url) or extract_ats_requisition_id(source_url)
    if ats_id:
        hash_digest = hashlib.sha256(f"ats:{ats_id}".encode("utf-8")).hexdigest()
        return f"sha256_{hash_digest}"
    
    # Signal 2: Trustworthy Direct Canonical URL
    if canonical_url and any(ats in canonical_url for ats in ["greenhouse.io", "ashbyhq.com", "lever.co", "workable.com", "smartrecruiters.com", "myworkdayjobs.com", "icims.com"]):
        hash_digest = hashlib.sha256(f"url:{canonical_url}".encode("utf-8")).hexdigest()
        return f"sha256_{hash_digest}"
    
    # Signal 3: Composite Entity Fingerprint
    company_norm = normalize_company(job.get("company"))
    title_norm = normalize_title(job.get("job_title"))
    loc_norm = normalize_location(job.get("location"))
    
    composite_key = f"comp:{company_norm}|{title_norm}|{loc_norm}"
    hash_digest = hashlib.sha256(composite_key.encode("utf-8")).hexdigest()
    return f"sha256_{hash_digest}"
