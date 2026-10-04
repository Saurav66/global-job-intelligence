# Morning Scan Routine — Daily Global Discovery

This template configures and executes the **Daily Morning Discovery Scan** by wrapping the unified scheduled run protocol.

---

## Execution Configuration

- **`RUN_MODE`:** `MORNING`
- **Discovery Window:** Preceding **24–48 hours**
- **Deep Qualification Target:** Top **20–30 surviving opportunities**
- **Durable Dataset Artifact:** `JOB_MASTER_TABLE.jsonl`
- **Sunday Retrospective Trigger:** Active (executes [templates/weekly_intelligence.md](file:///opt/saurav/global-job-intelligence/templates/weekly_intelligence.md) on Sundays)

---

## Instructions for Manus Agent

1. Initialize execution with `RUN_MODE=MORNING`.
2. Follow the unified protocol defined in [templates/scheduled_run.md](file:///opt/saurav/global-job-intelligence/templates/scheduled_run.md).
3. Ingest candidate context, materialize `JOB_MASTER_TABLE.jsonl`, run broad multi-channel discovery, execute deterministic qualification/scoring, persist updated artifacts, and deliver the Morning Intelligence Brief.
4. If the execution day is **Sunday**, proceed immediately to execute `templates/weekly_intelligence.md`.
5. **Enforce Phase-1 Boundary:** Stop after report and manifest delivery. Do not submit applications.
