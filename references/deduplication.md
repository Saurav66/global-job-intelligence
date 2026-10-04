# Deduplication & Canonicalization Reference

This document defines the deterministic, fingerprinting, and semantic algorithms used to detect duplicates, resolve canonical URLs, and merge redundant job postings across disparate platforms.

> **Deterministic Implementation:** Canonical URL normalization and SHA-256 fingerprinting are implemented in [`scripts/job_utils.py`](file:///opt/saurav/global-job-intelligence/scripts/job_utils.py). Multi-tier duplicate detection and merging are implemented in [`scripts/deduplicate_jobs.py`](file:///opt/saurav/global-job-intelligence/scripts/deduplicate_jobs.py).

---

## 1. Multi-Tier Deduplication Pipeline

Deduplication occurs before costly deep analysis to preserve Manus context and execution credits.

```
Incoming Discovery Item
          ↓
[ Tier 1: Canonical URL & Requisition ID Match ] ──(Match found)──→ MERGE & UPDATE
          ↓ No match
[ Tier 2: Deterministic Entity Fingerprint ] ──────(Match found)──→ MERGE & UPDATE
          ↓ No match
[ Tier 3: Semantic Description & Similarity Match ] ─(Match found)──→ MERGE & UPDATE
          ↓ No match
[ Unique New Opportunity ] ────────────────────────────────────────→ PROCEED TO QUALIFICATION
```

---

## 2. Deduplication Tiers

### Tier 1: Exact Canonical URL & ATS Requisition ID Match
- **Canonical URL Normalization:** Strip tracking parameters (`utm_source`, `utm_medium`, `gh_src`, `lever-source`, `ref`, session tokens).
- **ATS Requisition Extraction:** Extract the unique ATS identifier from recognized platforms:
  - Greenhouse: `boards.greenhouse.io/{company}/jobs/{job_id}` $\rightarrow$ `gh:{company}:{job_id}`
  - Ashby: `jobs.ashbyhq.com/{company}/{job_id}` $\rightarrow$ `ashby:{company}:{job_id}`
  - Lever: `jobs.lever.co/{company}/{uuid}` $\rightarrow$ `lever:{company}:{uuid}`
  - Workday: `*.myworkdayjobs.com/*/job/{location}/{req_id}` $\rightarrow$ `wd:{company}:{req_id}`

### Tier 2: Deterministic Entity Fingerprint
When a job is cross-posted across third-party boards (e.g., Himalayas, Remote OK) without direct ATS URLs, compute a deterministic fingerprint:

$$\text{Fingerprint} = \text{SHA256}(\text{norm}(\text{company}) \,\|\, \text{norm}(\text{job\_title}) \,\|\, \text{norm}(\text{location\_bucket}))$$

- **Normalization Rules:**
  - `norm(company)`: Lowercase, remove legal suffixes (`Inc.`, `LLC`, `Ltd`, `Technologies`, `Corp`), strip punctuation.
  - `norm(job_title)`: Lowercase, standardize level prefixes (`Sr.` $\rightarrow$ `senior`, `Lead` $\rightarrow$ `lead`), strip punctuation.
  - `norm(location_bucket)`: Map to standard geographic buckets (`remote-global`, `remote-india`, `remote-us`, `london-hybrid`).

### Tier 3: Semantic Description Match
For listings where titles differ slightly (e.g., "Senior DevOps Engineer" vs. "Senior Cloud & DevOps Engineer") at the same company:
- Compare normalized job description headers, team descriptions, and bullet points.
- If content overlap exceeds 85% and requirements are identical, flag as duplicate.

---

## 3. Canonical Source Hierarchy

When identical postings are detected across multiple sources, preserve the highest-tier URL as `canonical_url` and retain alternative discovery links in the notes / alternate URLs list:

```
Tier 1: Official Company Careers Portal (e.g., acme.com/careers/...)
                  >
Tier 2: Direct ATS Portal (e.g., boards.greenhouse.io/acme/...)
                  >
Tier 3: Trusted Niche Platforms (e.g., Himalayas, WeWorkRemotely, YC)
                  >
Tier 4: Professional Networks (e.g., LinkedIn Direct Job Post)
                  >
Tier 5: General Aggregators (e.g., Jooble, Indeed, Jobrapido)
```

---

## 4. Distinguishing Legitimately Separate Roles from Cross-Postings

Do NOT rely solely on job titles to declare a duplicate. Companies frequently hire for multiple distinct teams under similar titles.

### Criteria for Distinct Openings:
1. **Different Requisition IDs:** If ATS IDs differ (e.g., `req_1042` vs. `req_1089`), treat as separate openings even if titles are identical.
2. **Distinct Team / Department:** A "Platform Engineer" in Data Platform vs. "Platform Engineer" in Core Infrastructure are separate roles.
3. **Distinct Location / Remote Boundaries:** A role restricted to US vs. a sister role open to EMEA/Global are separate requisitions.

### Merging Rules for Verified Duplicates:
When a new discovery matches an existing active record:
1. Update `last_seen_at` on the existing master record to current timestamp.
2. Upgrade `canonical_url` if the new discovery provides a higher-tier source (e.g., discovered on LinkedIn, now resolved to Ashby ATS).
3. If new compensation or metadata is revealed, update fields without creating a duplicate record.
4. Set status of the redundant discovery item to `DUPLICATE` in the current scan log.
