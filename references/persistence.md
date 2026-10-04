# Persistence & Artifact Contract Reference

This document defines the storage architecture, artifact lifecycle, synchronization protocols, optimistic concurrency guards, and disaster recovery procedures for the Global Job Intelligence system.

---

## 1. Storage Entities & Terminology

| Entity Identifier | Role & Scope | Durability |
| :--- | :--- | :--- |
| **`JOB_MASTER_TABLE`** | Logical canonical dataset containing all validated historical job records. | **Durable System Truth** |
| **`JOB_MASTER_TABLE.jsonl`** | Serialized JSON Lines representation saved as a named Manus project artifact. | **Durable Storage Artifact** |
| **`JOB_MASTER_TABLE.csv`** | Optional tabular export for human review / spreadsheet integration. | **Export Artifact** |
| **`job_master.jsonl`** | Ephemeral working copy stored in the temporary agent runtime workspace. | **Temporary Working Copy** |
| **`RUN_MANIFEST.json`** | Metadata manifest documenting execution metrics, checksums, and status. | **Durable Audit Artifact** |

---

## 2. Execution Lifecycle Protocols

```
[ START OF RUN ]
  1. Inspect environment for existing JOB_MASTER_TABLE.jsonl artifact.
  2. If found:
     - Run: python3 scripts/artifact_sync.py import --source JOB_MASTER_TABLE.jsonl --runtime job_master.jsonl
     - Validate input checksum and record count.
  3. If not found:
     - Run: python3 scripts/master_dataset.py init --file job_master.jsonl
  4. If validation fails:
     - Trigger DATASET_RECOVERY protocol (Do not overwrite).
                     ↓
[ MID RUN: DISCOVERY, SCORING & DEDUPLICATION ]
  - New records validated and upserted into local working copy job_master.jsonl.
                     ↓
[ END OF RUN ]
  1. Validate entire local working dataset: python3 scripts/master_dataset.py validate --file job_master.jsonl
  2. Synchronize to durable artifact with concurrency check:
     python3 scripts/artifact_sync.py export --runtime job_master.jsonl --dest JOB_MASTER_TABLE.jsonl --expected-input-hash <HASH>
  3. Generate and persist RUN_MANIFEST.json.
  4. Deliver Markdown scan brief.
```

---

## 3. Optimistic Concurrency Protection

When scheduled tasks run concurrently or in separate task sessions within the same project, stale overwrites must be prevented:

```
[ Export Request ]
        │
        ▼
[ Compare Input SHA-256 vs. Destination Current SHA-256 ]
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
[ Checksum Match ]           [ Checksum Mismatch (DATASET_CONFLICT) ]
   │                                │
   ▼                                ▼
[ Atomic Export Succeeded ]   [ Conflict Resolution Protocol ]
                                1. Reload latest destination artifact.
                                2. Re-apply new run delta via merge_job_records().
                                3. Re-validate combined dataset.
                                4. Retry atomic export once.
```

If the destination checksum has changed during execution, `artifact_sync.py` flags `DATASET_CONFLICT`, preventing accidental data clobbering.

---

## 4. Dataset Recovery Protocols

The system handles 5 distinct persistence state permutations:

| Scenario | State Observed | Mandatory Recovery Action |
| :---: | :--- | :--- |
| **Case A** | Fresh project; neither local copy nor durable artifact exists. | Initialize empty working dataset (`job_master.jsonl`) with 0 records. Record initialization in manifest. |
| **Case B** | Fresh agent workspace; local `job_master.jsonl` absent, but durable `JOB_MASTER_TABLE.jsonl` exists. | Materialize `job_master.jsonl` from `JOB_MASTER_TABLE.jsonl`. Validate all records and proceed. |
| **Case C** | Local `job_master.jsonl` is corrupted / invalid, but durable `JOB_MASTER_TABLE.jsonl` is valid. | Discard invalid local working copy; restore clean copy from durable artifact. |
| **Case D** | Durable `JOB_MASTER_TABLE.jsonl` artifact fails validation. | **DO NOT OVERWRITE.** Preserve corrupted artifact as `JOB_MASTER_TABLE_CORRUPT_<TIMESTAMP>.jsonl`. Flag status as `DATASET_RECOVERY_REQUIRED`. Restore from most recent known-good historical artifact if available. |
| **Case E** | Both local and durable datasets are corrupted or missing after prior runs. | Initialize clean dataset. Explicitly alert the user in the report that historical tracking was unrecoverable. |

> **CARDINAL RULE OF PERSISTENCE:**  
> **Never silently delete, overwrite, or reset job history.** When corruption is detected, preserve raw artifacts and alert the candidate.
