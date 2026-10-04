# Scripts Directory — Deterministic Processing & Runtime Contracts

This directory contains zero-dependency Python utilities supporting the **Global Job Intelligence** Skill.

---

## 1. Compact Script Invocation Map

| Operation | Script | CLI Invocation Example |
| :--- | :--- | :--- |
| **Runtime Capability Probe** | [`runtime_probe.py`](file:///opt/saurav/global-job-intelligence/scripts/runtime_probe.py) | `python3 scripts/runtime_probe.py` |
| **Pre-Flight Readiness Check** | [`preflight.py`](file:///opt/saurav/global-job-intelligence/scripts/preflight.py) | `python3 scripts/preflight.py --candidate candidate_context.json --dataset job_master.jsonl --json` |
| **Context Validation** | [`context_validator.py`](file:///opt/saurav/global-job-intelligence/scripts/context_validator.py) | `python3 scripts/context_validator.py candidate_context.json` |
| **Job Schema Validation** | [`validate_job.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_job.py) | `python3 scripts/validate_job.py job.json` |
| **Deduplication & Merge** | [`deduplicate_jobs.py`](file:///opt/saurav/global-job-intelligence/scripts/deduplicate_jobs.py) | `python3 scripts/deduplicate_jobs.py incoming.jsonl job_master.jsonl` |
| **Scoring & Status Derivation**| [`score_job.py`](file:///opt/saurav/global-job-intelligence/scripts/score_job.py) | `python3 scripts/score_job.py job.json` |
| **Dataset Initialization** | [`master_dataset.py`](file:///opt/saurav/global-job-intelligence/scripts/master_dataset.py) | `python3 scripts/master_dataset.py init --file job_master.jsonl` |
| **Dataset Upsert** | [`master_dataset.py`](file:///opt/saurav/global-job-intelligence/scripts/master_dataset.py) | `python3 scripts/master_dataset.py upsert new_scan.jsonl --file job_master.jsonl` |
| **Dataset Summary** | [`master_dataset.py`](file:///opt/saurav/global-job-intelligence/scripts/master_dataset.py) | `python3 scripts/master_dataset.py summary --file job_master.jsonl` |
| **Artifact Import** | [`artifact_sync.py`](file:///opt/saurav/global-job-intelligence/scripts/artifact_sync.py) | `python3 scripts/artifact_sync.py import --source JOB_MASTER_TABLE.jsonl --runtime job_master.jsonl` |
| **Artifact Export (Guarded)** | [`artifact_sync.py`](file:///opt/saurav/global-job-intelligence/scripts/artifact_sync.py) | `python3 scripts/artifact_sync.py export --runtime job_master.jsonl --dest JOB_MASTER_TABLE.jsonl --expected-hash <HASH>` |
| **Run Manifest Generation** | [`run_manifest.py`](file:///opt/saurav/global-job-intelligence/scripts/run_manifest.py) | `python3 scripts/run_manifest.py --mode MORNING --status SUCCESS --in-records 10 --out-records 15 --out RUN_MANIFEST.json` |
| **Skill Safety Audit** | [`validate_skill.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_skill.py) | `python3 scripts/validate_skill.py` |

---

## 2. Agent vs. Script Responsibility Matrix

| Operational Phase | Manus Agent Responsibility | Deterministic Script Responsibility |
| :--- | :--- | :--- |
| **Context Ingestion** | Reads private candidate profile from Manus Project. | [`context_validator.py`](file:///opt/saurav/global-job-intelligence/scripts/context_validator.py): Checks schema, enums, compensation consistency, and calculates sufficiency level (`MINIMUM`, `STANDARD`, `ENRICHED`). |
| **Pre-Flight Check** | Evaluates readiness before discovery. | [`preflight.py`](file:///opt/saurav/global-job-intelligence/scripts/preflight.py) & [`runtime_probe.py`](file:///opt/saurav/global-job-intelligence/scripts/runtime_probe.py): Tests Python environment, filesystem access, and script availability. |
| **Artifact Lifecycle** | Locates durable `JOB_MASTER_TABLE.jsonl` artifact. | [`artifact_sync.py`](file:///opt/saurav/global-job-intelligence/scripts/artifact_sync.py): Validates, calculates SHA-256 checksums, imports/exports atomically, and guards against optimistic concurrency conflicts. |
| **Discovery** | Crafts queries across ATS gateways and boards. | *None (Agent reasoning)* |
| **Extraction** | Extracts structured facts from unstructured JDs. | *None (Agent reasoning)* |
| **Normalization** | Provides raw strings. | [`job_utils.py`](file:///opt/saurav/global-job-intelligence/scripts/job_utils.py): Normalizes text, location buckets, company names, and strips tracking parameters from URLs. |
| **Fingerprinting** | Provides normalized record. | [`job_utils.py`](file:///opt/saurav/global-job-intelligence/scripts/job_utils.py): Generates deterministic SHA-256 fingerprint hash. |
| **Validation** | Formats candidate job JSON. | [`validate_job.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_job.py): Enforces schema, numerical bounds, enum integrity, and Phase-1 boundaries. |
| **Deduplication** | Evaluates edge-case cross-postings. | [`deduplicate_jobs.py`](file:///opt/saurav/global-job-intelligence/scripts/deduplicate_jobs.py): Detects duplicates across 4 signal tiers and safely merges records without data loss. |
| **Scoring** | Assigns qualitative dimension scores (0–100). | [`score_job.py`](file:///opt/saurav/global-job-intelligence/scripts/score_job.py): Role-aware weight calculations, UNKNOWN compensation re-normalization, composite scoring, and status derivation. |
| **Local Persistence** | Instructs working dataset updates. | [`master_dataset.py`](file:///opt/saurav/global-job-intelligence/scripts/master_dataset.py): Atomic JSONL updates, summary analytics, and expiration marking. |
| **Audit & Tracing** | Synthesizes final report narrative. | [`run_manifest.py`](file:///opt/saurav/global-job-intelligence/scripts/run_manifest.py): Generates standardized `RUN_MANIFEST.json` documenting run metrics and status. |

---

## 3. Running Automated Tests

Run the complete test suite (45 unit tests, pure Python standard library):

```bash
python3 -m unittest discover tests
```
