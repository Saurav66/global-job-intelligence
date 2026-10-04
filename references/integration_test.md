# Integration Test Contract Reference (First Live Manus Run)

This document defines the acceptance test contract for the first controlled live execution of the **Global Job Intelligence Skill** inside a **Manus Project**.

---

## 1. Test Objective & Scope

The purpose of the initial live integration test is **verification of system contracts and runtime execution**, NOT high-volume discovery.

### Target Constraints
- **Discovery Target:** Identify and evaluate **5 to 10 viable live job opportunities**.
- **Credit Preservation:** Limit search depth to high-signal channels (direct ATS portals and top remote boards).
- **No Phase-2 Actions:** Strictly verify zero application submissions, form autofills, or recruiter contact.

---

## 2. Acceptance Verification Matrix

| Area Tested | Verification Criteria |
| :--- | :--- |
| **Skill Ingestion** | Skill is loaded, recognized, and [SKILL.md](file:///opt/saurav/global-job-intelligence/SKILL.md) control plane triggers properly. |
| **Context Access** | Private candidate context is read from the Manus Project without exposing secrets. |
| **Context Validation** | `scripts/context_validator.py` evaluates context sufficiency (`MINIMUM`, `STANDARD`, or `ENRICHED`). |
| **Runtime Probe** | `scripts/runtime_probe.py` probes Python and filesystem capabilities. |
| **Durable Persistence** | Locates or initializes `JOB_MASTER_TABLE.jsonl` and creates working copy `job_master.jsonl`. |
| **Multi-Tier Deduplication** | Pre-filters cross-posted URLs and assigns deterministic SHA-256 fingerprints. |
| **Scoring Engine** | Evaluates $S_{\text{capability}}$, $S_{\text{opportunity}}$, $S_{\text{final}}$, and $S_{\text{resume}}$ with no fabricated salaries. |
| **Run Manifest** | Serializes execution metadata to `RUN_MANIFEST.json` with `run_mode = "INTEGRATION_TEST"`. |
| **Execution Reporting** | Delivers formatted Markdown brief conforming to the Integration Test Report schema. |

---

## 3. Acceptance Status Definitions

### A. PASS
- Skill triggers and loads references successfully.
- Private candidate context is ingested and validated.
- At least 3–5 valid structured live job records are discovered and evaluated.
- Deduplication and fingerprint generation run correctly.
- Durable dataset artifact (`JOB_MASTER_TABLE.jsonl`) is updated/created.
- Execution manifest (`RUN_MANIFEST.json`) is generated.
- Zero Phase-2 actions (no applications or forms).
- *Note:* A test may **PASS under `MANUAL_FALLBACK`** if script execution is unavailable in the environment but all reference rules and artifacts are produced accurately.

### B. PARTIAL PASS
- Discovery and qualification work, but:
  - Deterministic scripts fail unexpectedly and require manual recovery.
  - Candidate context required manual formatting adjustments.
  - Durable artifact export encountered a non-fatal warning.

### C. FAIL
- Skill fails to trigger or parse instructions.
- Candidate context cannot be read.
- System fabricates undisclosed compensation or bypasses hard blockers.
- Job history or dataset is corrupted/overwritten without recovery.
- Any Phase-2 action is attempted.
- Candidate private data is leaked.

---

## 4. Standardized Integration Test Report Format

```markdown
# Integration Test Result — Global Job Intelligence

**Skill Version:** 0.3.1  
**Run ID:** 20261004T...-INTEGRATION_TEST-...  
**Execution Mode:** DETERMINISTIC / HYBRID_FALLBACK / MANUAL_FALLBACK  
**Candidate Context Level:** MINIMUM / STANDARD / ENRICHED  

---

## 1. Runtime Capabilities
- **Python Standard Library:** Available / Unavailable
- **Filesystem Read/Write:** Verified
- **Deterministic Scripts Accessible:** Yes / No
- **Persistent Artifact Restored:** Yes / Initialized Clean
- **Execution Fallback Used:** None / HYBRID / MANUAL

## 2. Discovery Funnel
- **Raw Postings Discovered:** XX
- **Unique Qualified Opportunities Retained:** XX (Target: 5–10)
- **Duplicates Removed / Merged:** XX
- **Hard-Filter Disqualifications:** XX

## 3. Qualified Live Opportunities (Sample Table)

| Final Score | Company | Role Title | Remote Type | India Eligible | Disclosed Salary | Cap Score | Opp Score | Resume Match | Status | Canonical ATS Link |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **91.2** | ExampleCorp | Senior DevSecOps | `REMOTE_GLOBAL` | YES | $140k - $170k | 92.0 | 90.0 | 88.0 | `SHORTLIST_A_PLUS` | [ATS Link](https://...) |

## 4. Persisted Artifacts
- **Durable Dataset:** `JOB_MASTER_TABLE.jsonl` (Records: XX | SHA-256: `...`)
- **Execution Manifest:** `RUN_MANIFEST.json` (Status: `SUCCESS`)

## 5. Runtime Issues & Warnings
- **Warnings:** None
- **Errors:** None

## 6. Acceptance Status
**RESULT:** ✅ **PASS** / ⚠️ **PARTIAL PASS** / ❌ **FAIL**
```
