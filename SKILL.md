---
name: global-job-intelligence
description: Discovers, qualifies, deduplicates, scores, ranks, and reports global and remote job opportunities for experienced DevSecOps, DevOps, Cloud, Platform, SRE, AI Infrastructure, MLOps, and adjacent engineering candidates. Designed for job discovery and market intelligence only; does not perform job applications.
---

# Global Job Intelligence Skill (Phase 1 — v0.3.1)

This Skill acts as the execution control plane for an automated, multi-source global job discovery and qualification system.

---

## Unified Runtime Workflow Protocol

When executing a discovery task (via scheduled task, integration test, or ad-hoc prompt), follow this sequential lifecycle:

```
[ Step 1: Ingest & Validate Candidate Context ]
                      ↓
[ Step 2: Probe Runtime & Materialize Durable Dataset Artifact (JOB_MASTER_TABLE.jsonl) ]
                      ↓
[ Step 3: Broad, Incremental, or Sample Multi-Channel Discovery ]
                      ↓
[ Step 4: Extraction, Normalization & Validation ]
                      ↓
[ Step 5: Multi-Tier Deduplication (Deterministic) ]
                      ↓
[ Step 6: Geographic & Hard-Blocker Checks ]
                      ↓
[ Step 7: Multi-Dimensional Scoring & Status Derivation ]
                      ↓
[ Step 8: Resume Coverage & Representation Gap Analysis ]
                      ↓
[ Step 9: Local Master Dataset Upsert (Atomic JSONL) ]
                      ↓
[ Step 10: Synchronize to Durable Artifact with Concurrency Guard ]
                      ↓
[ Step 11: Write Run Manifest (RUN_MANIFEST.json) ]
                      ↓
[ Step 12: Deliver Executive Markdown Intelligence Brief ]
                      ↓
[ Step 13: Strict Phase-1 Boundary Enforcement (STOP) ]
```

---

## Operational Steps & Resource References

### 1. Ingest & Validate Candidate Context
- Ingest private candidate profile from the active Manus Project.
- Validate context structure: `python3 scripts/context_validator.py candidate_context.json`.
- Consult [references/candidate_context.md](file:///opt/saurav/global-job-intelligence/references/candidate_context.md) for sufficiency levels (`MINIMUM`, `STANDARD`, `ENRICHED`).
- Never commit private candidate details to the repository.

### 2. Probe Runtime & Materialize Durable Dataset
- Probe execution capabilities: `python3 scripts/runtime_probe.py`.
- Import latest validated artifact: `python3 scripts/artifact_sync.py import --source JOB_MASTER_TABLE.jsonl --runtime job_master.jsonl`.
- Consult [references/persistence.md](file:///opt/saurav/global-job-intelligence/references/persistence.md) for recovery protocols (Cases A–E).

### 3. Multi-Channel Discovery
- **Integration Test:** Execute controlled live sample (5–10 viable jobs) using [templates/integration_test.md](file:///opt/saurav/global-job-intelligence/templates/integration_test.md).
- **Morning Scan:** Execute broad discovery across direct ATS gateways (Greenhouse, Lever, Ashby, Workday), remote boards (Himalayas, RemoteOK, WWR, Wellfound), and networks for postings from the last 24–48h using [templates/morning_scan.md](file:///opt/saurav/global-job-intelligence/templates/morning_scan.md).
- **Evening Scan:** Execute incremental queries for UK/EU and early US postings from the last 10–14h using [templates/evening_scan.md](file:///opt/saurav/global-job-intelligence/templates/evening_scan.md).
- Consult [references/search_strategy.md](file:///opt/saurav/global-job-intelligence/references/search_strategy.md) for role taxonomy and ATS dorks.

### 4. Normalization, Validation & Deduplication
- Clean titles/locations and strip tracking parameters (`utm_*`, `gh_src`) via [`scripts/job_utils.py`](file:///opt/saurav/global-job-intelligence/scripts/job_utils.py).
- Generate deterministic SHA-256 fingerprints.
- Validate structured records using [`scripts/validate_job.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_job.py) and [references/job_schema.md](file:///opt/saurav/global-job-intelligence/references/job_schema.md).
- Run batch deduplication against working copy `job_master.jsonl` using [`scripts/deduplicate_jobs.py`](file:///opt/saurav/global-job-intelligence/scripts/deduplicate_jobs.py) and [references/deduplication.md](file:///opt/saurav/global-job-intelligence/references/deduplication.md).

### 5. Eligibility & Hard-Filter Evaluation
- Evaluate remote type (`REMOTE_GLOBAL`, `REMOTE_INDIA`, etc.) according to [references/eligibility_rules.md](file:///opt/saurav/global-job-intelligence/references/eligibility_rules.md).
- Reject incompatible location restrictions, foreign security clearances, or executive levels. Never reject solely for missing resume keywords.

### 6. Deep Qualification, Scoring & Status Derivation
- Fetch complete job specifications for surviving candidates.
- Evaluate scores via [`scripts/score_job.py`](file:///opt/saurav/global-job-intelligence/scripts/score_job.py) and [references/scoring.md](file:///opt/saurav/global-job-intelligence/references/scoring.md):
  - $S_{\text{capability}}$ (role-aware profile).
  - $S_{\text{opportunity}}$ (dynamic weight re-normalization for undisclosed compensation).
  - $S_{\text{final}} = S_{\text{capability}} \times 0.60 + S_{\text{opportunity}} \times 0.40$.
  - Derive priority (`A_PLUS`, `A`, `B`, `C`, `LOW`) and status (`SHORTLIST_A_PLUS`, `HOLD_RESUME_UPDATE`, `REVIEW_LOCATION`, etc.).

### 7. Resume Coverage Assessment
- Assess resume representation independently from technical competency.
- Flag high capability with low resume representation as `HOLD_RESUME_UPDATE`.

### 8. Local Dataset Upsert & Durable Artifact Synchronization
- Upsert validated records into `job_master.jsonl` via `scripts/master_dataset.py upsert`.
- Export working dataset to durable artifact `JOB_MASTER_TABLE.jsonl` with concurrency check via `scripts/artifact_sync.py export`.

### 9. Write Execution Manifest & Deliver Report
- Generate audit manifest `RUN_MANIFEST.json` via [`scripts/run_manifest.py`](file:///opt/saurav/global-job-intelligence/scripts/run_manifest.py).
- Render Markdown brief according to [references/reporting.md](file:///opt/saurav/global-job-intelligence/references/reporting.md) (or [references/integration_test.md](file:///opt/saurav/global-job-intelligence/references/integration_test.md) for live test).
- If Sunday morning, execute [templates/weekly_intelligence.md](file:///opt/saurav/global-job-intelligence/templates/weekly_intelligence.md).

### 10. Phase Boundary Enforcement
- **STOP.** Do not submit applications, fill out forms, or contact recruiters.

---

## Execution Fallback Notice
> **Graceful Fallback:** If script execution is unavailable or restricted in the runtime, switch once immediately to `MANUAL_FALLBACK` following [references/runtime_contract.md](file:///opt/saurav/global-job-intelligence/references/runtime_contract.md). Never skip deduplication, scoring, or hard blockers.
