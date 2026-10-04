# Integration Test Routine — First Live Manus Verification

This template executes a controlled, small-scale live integration test to verify Skill discovery, script execution, candidate context ingestion, scoring, and durable artifact persistence in a new Manus Project.

---

## Execution Parameters

- **`RUN_MODE`:** `INTEGRATION_TEST`
- **Target Volume:** **5 to 10 viable live opportunities** (Do NOT chase hundreds of jobs)
- **Durable Dataset Artifact:** `JOB_MASTER_TABLE.jsonl`
- **Manifest File:** `RUN_MANIFEST.json`

---

## Step-by-Step Test Protocol

### Step 1: Confirm Skill Ingestion & Runtime Capabilities
1. Probe available execution capabilities:
   ```bash
   python3 scripts/runtime_probe.py
   ```
2. Determine execution mode:
   - **`DETERMINISTIC`:** Python scripts execute normally.
   - **`MANUAL_FALLBACK`:** If script execution is unavailable or restricted in the runtime environment, **switch once immediately to manual fallback mode** (do not retry failing commands repeatedly).

### Step 2: Load & Validate Private Candidate Context
1. Ingest `candidate_context.json` from the active Manus Project.
2. Validate context schema:
   ```bash
   python3 scripts/context_validator.py candidate_context.json
   ```
3. Record candidate context sufficiency level (`MINIMUM`, `STANDARD`, or `ENRICHED`).

### Step 3: Materialize / Initialize Durable Master Dataset
1. Attempt to import the durable dataset artifact:
   ```bash
   python3 scripts/artifact_sync.py import --source JOB_MASTER_TABLE.jsonl --runtime job_master.jsonl
   ```
2. If absent, initialize a clean dataset:
   ```bash
   python3 scripts/master_dataset.py init --file job_master.jsonl
   ```

### Step 4: Controlled Live Multi-Channel Discovery
1. Search a focused sample of live postings across:
   - Direct ATS gateways (Greenhouse, Lever, Ashby, Workday)
   - Specialized remote boards (Himalayas, RemoteOK, We Work Remotely, Wellfound)
2. **Target Role Taxonomy:** DevSecOps, Platform Engineering, Cloud Engineering, SRE, and AI Infrastructure.
3. **Target Remote Boundaries:** `REMOTE_GLOBAL`, `REMOTE_INDIA`, or international remote open to India candidates.
4. Stop broad searching once **5 to 10 viable, unblocked opportunities** have been identified.

### Step 5: Normalization, Validation & Deduplication
1. Strip tracking parameters and clean titles via [`scripts/job_utils.py`](file:///opt/saurav/global-job-intelligence/scripts/job_utils.py).
2. Generate deterministic SHA-256 fingerprints.
3. Validate candidate records using [`scripts/validate_job.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_job.py).
4. Run batch deduplication against `job_master.jsonl` using [`scripts/deduplicate_jobs.py`](file:///opt/saurav/global-job-intelligence/scripts/deduplicate_jobs.py).

### Step 6: Multi-Dimensional Scoring
1. Fetch full specifications for the retained test opportunities.
2. Calculate scores using [`scripts/score_job.py`](file:///opt/saurav/global-job-intelligence/scripts/score_job.py):
   - $S_{\text{capability}}$ (role-aware profile)
   - $S_{\text{opportunity}}$ (zero-salary-fabrication handling)
   - $S_{\text{final}} = S_{\text{capability}} \times 0.60 + S_{\text{opportunity}} \times 0.40$
   - $S_{\text{resume}}$ and status derivation

### Step 7: Dataset Upsert & Durable Artifact Export
1. Merge qualified records into working copy `job_master.jsonl`:
   ```bash
   python3 scripts/master_dataset.py upsert test_jobs.jsonl --file job_master.jsonl
   ```
2. Export to durable project artifact:
   ```bash
   python3 scripts/artifact_sync.py export --runtime job_master.jsonl --dest JOB_MASTER_TABLE.jsonl
   ```

### Step 8: Generate Run Manifest & Integration Test Report
1. Generate audit manifest:
   ```bash
   python3 scripts/run_manifest.py --mode INTEGRATION_TEST --status SUCCESS --in-records 0 --out-records <COUNT> --raw <COUNT> --unique <COUNT> --out RUN_MANIFEST.json
   ```
2. Render the Integration Test Report conforming to [references/integration_test.md](file:///opt/saurav/global-job-intelligence/references/integration_test.md).
3. Conclude execution (Strict Phase-1 boundary).
