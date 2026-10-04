# Runtime Contract Reference

This document defines execution environments, persistent vs. temporary boundaries, fallback modes, run-mode contracts, and idempotency guarantees for the Global Job Intelligence Skill.

---

## 1. Runtime Environment Partitioning

Manus executions operate in a sandboxed, ephemeral runtime workspace. The system explicitly partitions responsibilities and data lifetimes:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PERSISTENT MANUS PROJECT CONTEXT                     │
│  • Candidate Private Profile (Capabilities, Location, Preferences)     │
│  • Resume Variant Documents (*.pdf, *.docx)                            │
│  • Imported Skill Repository (Workflow Logic & Reference Rules)        │
│  • Scheduled Task History & Context                                    │
│  • Durable Dataset Artifact (JOB_MASTER_TABLE.jsonl / .csv)            │
│  • Historical Run Manifests (RUN_MANIFEST.json)                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Materialize at start of run)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   TEMPORARY RUNTIME WORKING SPACE                      │
│  • Working Master Dataset (job_master.jsonl)                           │
│  • Raw Multi-Channel Search Cards & Discovered Listings                │
│  • Temporary Score Inputs & Scoring Outputs                            │
│  • Intermediate Deduplication Queues                                   │
│  • Ephemeral Log & Debug Outputs                                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Persist atomically at end of run)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DURABLE ARTIFACT PERSISTENCE                       │
│  • Updated JOB_MASTER_TABLE.jsonl (Verified via SHA-256 Checksum)      │
│  • Execution Run Manifest (RUN_MANIFEST.json)                          │
│  • Executive Daily Brief / Weekly Market Digest Markdown Report        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Responsibility Matrix

| Entity | Core Responsibility |
| :--- | :--- |
| **Manus Agent** | Ingest candidate context, execute web discovery across ATS dorks and job boards, interpret unstructured job descriptions, extract factual requirements, evaluate qualitative scores, invoke deterministic utilities, update durable artifacts, and generate report briefs. |
| **Deterministic Scripts** | Validate schema contracts, compute SHA-256 fingerprints, execute multi-tier deduplication, perform weighted math and UNKNOWN re-normalization, derive priority/status enums, atomically upsert dataset records, and generate run manifests. |
| **Persistent Project** | Long-term store for candidate identity, resume files, scheduled task cadences, and validated durable job records (`JOB_MASTER_TABLE.jsonl`). |
| **Temporary Runtime** | Scratch workspace for scratch files (`job_master.jsonl`), intermediate query caches, and per-run logs. Must be treated as disposable. |

---

## 3. Script Execution Fallback Modes

The Skill supports three operational execution modes to ensure resilience across diverse agent runtimes:

```
[ Check Execution Environment ]
               │
      ┌────────┴────────┐
      ▼                 ▼
[ Python Stdlib   [ Scripts Not
  Executable ]      Executable ]
      │                 │
      ▼                 ▼
[ DETERMINISTIC ] [ MANUAL_FALLBACK ]
```

1. **`DETERMINISTIC` (Standard Mode):**  
   All Python utilities execute successfully.
2. **`HYBRID_FALLBACK` (Partial Execution):**  
   Certain scripts execute (e.g., scoring math), while others are handled via manual agent reasoning adhering to references.
3. **`MANUAL_FALLBACK` (Instruction-Driven Mode):**  
   Python script execution is disabled or restricted in the runtime environment. The agent executes the identical rules manually by consulting [references/](file:///opt/saurav/global-job-intelligence/references/).

> **MANUS FALLBACK RULE:**  
> If Manus can read bundled scripts but execution is restricted in the environment, **switch once immediately to `MANUAL_FALLBACK` mode** and proceed with discovery. Do NOT repeatedly retry failing script commands or waste tokens. Record the fallback in `RUN_MANIFEST.json`.

> **NON-NEGOTIABLE FALLBACK RULES:**
> - Fallback mode **MUST NEVER** skip deduplication.
> - Fallback mode **MUST NEVER** skip scoring or fabricate undisclosed salaries.
> - Fallback mode **MUST NEVER** bypass hard blockers.
> - The active mode (`DETERMINISTIC`, `HYBRID_FALLBACK`, or `MANUAL_FALLBACK`) must be explicitly recorded in `RUN_MANIFEST.json` and the executive report.

---

## 4. Morning vs. Evening Run Contracts

To optimize token and credit consumption, morning and evening discovery cycles have distinct contracts:

### A. Morning Scan (`RUN_MODE=MORNING`)
- **Scope:** Broad multi-channel discovery covering postings from the preceding **24–48 hours**.
- **Execution:** Maximum search breadth across direct ATS portals, specialized remote boards, and networks.
- **Deep Analysis Target:** Top **20–30 surviving unique opportunities**.
- **Sunday Trigger:** Automatically invokes `templates/weekly_intelligence.md` after completing the morning brief.

### B. Evening Scan (`RUN_MODE=EVENING`)
- **Scope:** Incremental scan targeting postings surfaced during European/UK business hours and early US morning activity (**preceding 10–14 hours**).
- **Execution:** Focused incremental queries; aggressive deduplication against `JOB_MASTER_TABLE.jsonl`.
- **Deep Analysis Target:** Only net-new survivors (~10–15 jobs).
- **Historical Grounding:** Uses `JOB_MASTER_TABLE.jsonl` timestamps and IDs to determine incrementality—**never relies on conversational memory alone**.

---

## 5. Idempotency & Temporal Contract

1. **Idempotency Guarantee:**  
   If a scheduled run re-discovers an identical set of jobs, it must:
   - Match existing records via ATS ID, canonical URL, or SHA-256 fingerprint.
   - Update `last_seen_at` timestamps on existing records.
   - Retain total record count without generating duplicate rows.
2. **Standardized Timestamps:**  
   - All internal timestamps use **ISO 8601 UTC** format: `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2026-10-04T08:00:00Z`).
   - If a posting lists only a date without time, preserve date precision (`YYYY-MM-DD`) and do not manufacture fictitious hours/minutes.
3. **Freshness Resolution:**  
   - When `posted_date` is explicitly stated and parseable, calculate `job_age_days = now().date - posted_date`.
   - Relative strings (e.g., *"3 hours ago"*, *"1 day ago"*) are normalized relative to current run UTC time.
   - Vague strings (e.g., *"recently"*, *"active"*) are assigned `posted_date = "UNKNOWN"`, and freshness is derived from `first_seen_at`.
