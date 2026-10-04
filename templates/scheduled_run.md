# Unified Scheduled Run Contract — Global Job Intelligence

This template defines the unified execution protocol for scheduled tasks in Manus, supporting both **MORNING** broad discovery and **EVENING** incremental delta cycles.

---

## Run Configuration Parameters

Before initiating the run, determine or specify the operational mode:
- `RUN_MODE`: `MORNING` (default for daily morning runs) or `EVENING` (for daily afternoon/evening delta runs).
- `DURABLE_DATASET_ARTIFACT`: `JOB_MASTER_TABLE.jsonl`
- `WORKING_COPY`: `job_master.jsonl`
- `MANIFEST_FILE`: `RUN_MANIFEST.json`

---

## Unified Execution Protocol

```
[ Step 1: Ingest & Validate Candidate Context ]
                      ↓
[ Step 2: Materialize / Restore Durable Artifact ]
                      ↓
[ Step 3: Multi-Channel Discovery (Morning vs. Evening Scope) ]
                      ↓
[ Step 4: Normalization, Validation & Pre-Deduplication ]
                      ↓
[ Step 5: Geographic & Hard-Blocker Filtering ]
                      ↓
[ Step 6: Deep Multi-Dimensional Scoring (Top Survivors) ]
                      ↓
[ Step 7: Local Working Dataset Upsert (Atomic JSONL) ]
                      ↓
[ Step 8: Durable Artifact Export with Concurrency Guard ]
                      ↓
[ Step 9: Run Manifest Generation (RUN_MANIFEST.json) ]
                      ↓
[ Step 10: Executive Markdown Brief Delivery ]
                      ↓
[ Step 11: Sunday Weekly Digest Trigger (Morning Only) ]
                      ↓
[ Step 12: Strict Phase-1 Boundary Enforcement (STOP) ]
```

---

## Detailed Step-by-Step Instructions

### Step 1: Candidate Context Ingestion & Validation
1. Read the private candidate profile from the Manus Project context.
2. Validate the configuration:
   ```bash
   python3 scripts/context_validator.py candidate_context.json
   ```
3. Record the context sufficiency level (`MINIMUM`, `STANDARD`, or `ENRICHED`).

### Step 2: Materialize / Restore Working Master Dataset
1. Attempt to import the durable dataset artifact:
   ```bash
   python3 scripts/artifact_sync.py import --source JOB_MASTER_TABLE.jsonl --runtime job_master.jsonl
   ```
2. **Handle Persistence Recovery Cases:**
   - **Artifact Found & Valid:** Working copy `job_master.jsonl` is ready. Note input SHA-256 hash.
   - **Artifact Missing (Case A/B):** Initialize clean dataset (`python3 scripts/master_dataset.py init --file job_master.jsonl`).
   - **Artifact Validation Failed (Case D):** Enter `DATASET_RECOVERY_REQUIRED`. Do not overwrite corrupted artifact.

### Step 3: Multi-Channel Web & ATS Discovery
- **If `RUN_MODE=MORNING`:**
  - Execute broad queries across Greenhouse, Lever, Ashby, Workday, Himalayas, RemoteOK, WWR, Wellfound, and LinkedIn.
  - Target postings indexed within the preceding **24–48 hours**.
- **If `RUN_MODE=EVENING`:**
  - Execute incremental queries focused on Europe/UK and early US business day activity (**preceding 10–14 hours**).
  - Cross-reference with `job_master.jsonl` timestamps to avoid repeating morning discoveries.

### Step 4: Normalization, Validation & Deduplication
1. Clean titles, locations, and strip URL tracking parameters via `scripts/job_utils.py`.
2. Generate deterministic SHA-256 fingerprints.
3. Validate candidate records using `scripts/validate_job.py`.
4. Run batch deduplication against `job_master.jsonl`:
   ```bash
   python3 scripts/deduplicate_jobs.py incoming_scan.jsonl job_master.jsonl
   ```

### Step 5: Eligibility & Hard Blocker Checks
1. Evaluate remote type (`REMOTE_GLOBAL`, `REMOTE_INDIA`, etc.) according to [references/eligibility_rules.md](file:///opt/saurav/global-job-intelligence/references/eligibility_rules.md).
2. Hard-reject incompatible residency, inaccessible security clearances, or under/over-level titles.

### Step 6: Deep Technical Scoring & Resume Coverage
1. For top surviving opportunities (~20–30 for morning; ~10–15 for evening), fetch full JDs.
2. Calculate scores using `scripts/score_job.py`:
   - $S_{\text{capability}}$ (role-aware profile)
   - $S_{\text{opportunity}}$ (dynamic weight re-normalization for undisclosed compensation)
   - $S_{\text{final}} = S_{\text{capability}} \times 0.60 + S_{\text{opportunity}} \times 0.40$
   - $S_{\text{resume}}$ (detect `HOLD_RESUME_UPDATE` states)

### Step 7: Atomic Working Dataset Upsert
1. Merge new qualified records into the local working dataset:
   ```bash
   python3 scripts/master_dataset.py upsert qualified_jobs.jsonl --file job_master.jsonl
   ```

### Step 8: Durable Artifact Export & Concurrency Check
1. Validate and export updated dataset to the durable project artifact:
   ```bash
   python3 scripts/artifact_sync.py export --runtime job_master.jsonl --dest JOB_MASTER_TABLE.jsonl --expected-hash <INPUT_HASH>
   ```
2. If `DATASET_CONFLICT` is returned, reload latest `JOB_MASTER_TABLE.jsonl`, re-apply upserts, and retry export.

### Step 9: Generate Run Manifest
1. Create execution manifest documenting run metrics, checksums, and execution status:
   ```bash
   python3 scripts/run_manifest.py --mode MORNING --status SUCCESS --in-records <COUNT> --out-records <COUNT> --out RUN_MANIFEST.json
   ```

### Step 10: Deliver Executive Intelligence Brief
1. Render Markdown brief according to [references/reporting.md](file:///opt/saurav/global-job-intelligence/references/reporting.md).
2. Highlight Tier A+ / A opportunities and notable resume representation gaps.

### Step 11: Sunday Weekly Trigger (Morning Only)
- If execution day is **Sunday** and `RUN_MODE=MORNING`, proceed immediately to compile [templates/weekly_intelligence.md](file:///opt/saurav/global-job-intelligence/templates/weekly_intelligence.md).

### Step 12: Strict Phase-1 Boundary
- **STOP.** Do not apply, submit forms, upload resumes, or contact recruiters.

---

## Execution Fallback Modes
- **DETERMINISTIC:** All scripts execute normally.
- **HYBRID_FALLBACK:** Script execution partially available; manual fallback applies matching rules for missing operations.
- **MANUAL_FALLBACK:** Python unavailable; agent executes the matching rules defined in [references/](file:///opt/saurav/global-job-intelligence/references/) manually. Fallback mode MUST be documented in the report and manifest.
