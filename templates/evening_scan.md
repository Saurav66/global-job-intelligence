# Evening Scan Routine — Incremental Global Discovery

This template configures and executes the **Daily Evening Incremental Scan** by wrapping the unified scheduled run protocol.

---

## Execution Configuration

- **`RUN_MODE`:** `EVENING`
- **Discovery Window:** Preceding **10–14 hours** (Europe/UK business day and early US morning activity)
- **Deep Qualification Target:** Top **10–15 net-new surviving opportunities**
- **Durable Dataset Artifact:** `JOB_MASTER_TABLE.jsonl`
- **Deduplication Baseline:** Grounded against historical `JOB_MASTER_TABLE.jsonl` timestamps

---

## Instructions for Manus Agent

1. Initialize execution with `RUN_MODE=EVENING`.
2. Follow the unified protocol defined in [templates/scheduled_run.md](file:///opt/saurav/global-job-intelligence/templates/scheduled_run.md).
3. Ingest candidate context, materialize `JOB_MASTER_TABLE.jsonl`, run targeted incremental discovery, execute deterministic qualification/scoring, persist updated artifacts, and deliver the Evening Delta Brief.
4. **Enforce Phase-1 Boundary:** Stop after report and manifest delivery. Do not submit applications.
