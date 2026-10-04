# Global Job Intelligence (Phase 1)

[![Skill Version](https://img.shields.io/badge/version-0.3.1-blue.svg)](file:///opt/saurav/global-job-intelligence/CHANGELOG.md)
[![Platform](https://img.shields.io/badge/platform-Manus%20Agent-purple.svg)](https://manus.im)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An automated, multi-source global job discovery, qualification, deduplication, scoring, and market intelligence system designed for experienced **DevSecOps, Platform, Cloud, SRE, and AI Infrastructure** engineers.

---

## ⚠️ Important Scope & Phase-1 Boundaries

This repository represents **Phase 1 ONLY**.

### What Phase 1 DOES:
- Discovers global and remote opportunities across direct ATS portals, specialized job platforms, and professional networks.
- Validates geographic eligibility (worldwide remote, India-remote, regional).
- Normalizes job metadata and deduplicates cross-posted listings across channels using deterministic algorithms.
- Evaluates candidate technical capabilities and opportunity attractiveness using a multi-dimensional, role-aware scoring model.
- Analyzes candidate resume presentation gaps separately from actual technical competency.
- Maintains durable dataset persistence via project artifacts (`JOB_MASTER_TABLE.jsonl`) with optimistic concurrency guards and atomic working copy updates.
- Generates morning, evening, and weekly market intelligence briefs with machine-readable audit manifests (`RUN_MANIFEST.json`).
- Supports live integration testing (`RUN_MODE=INTEGRATION_TEST`) for controlled acceptance verification.

### What Phase 1 MUST NOT DO:
- ❌ **Apply for jobs** or submit web application forms.
- ❌ **Contact recruiters**, hiring managers, or send automated emails.
- ❌ **Upload private resumes** or cover letters to external platforms.
- ❌ **Create external accounts** on job boards.
- ❌ **Make external commitments** on behalf of the candidate.

---

## 🔒 Privacy & Public Repository Security

> **CRITICAL PRIVACY NOTICE:**  
> This repository is designed to be **publicly hostable on GitHub**. It contains only generic workflow logic, scoring algorithms, reference schemas, and deterministic scripts.

### 🚫 DO NOT STORE IN THIS REPOSITORY:
- Candidate contact information (email, phone, home address).
- Private resumes, cover letters, or portfolio drafts.
- Current compensation details or private financial targets.
- API keys, credentials, cookies, session tokens, or secrets.
- Confidential employer or client data.
- Historical runtime job datasets (`JOB_MASTER_TABLE.jsonl` / `job_master.jsonl`).

### How Candidate Private Context is Supplied
Candidate-specific parameters reside strictly inside the **private Manus Project / Session context**, not in git. See [references/candidate_context.md](file:///opt/saurav/global-job-intelligence/references/candidate_context.md), [templates/candidate_context.example.json](file:///opt/saurav/global-job-intelligence/templates/candidate_context.example.json), and [references/manus_project_setup.md](file:///opt/saurav/global-job-intelligence/references/manus_project_setup.md).

---

## 🏗️ Runtime Architecture

```
Public GitHub Skill Repository (Workflow Logic & Reference Rulebooks)
                                 │
                                 ▼ (Import as Skill)
┌────────────────────────────────────────────────────────────────────────┐
│                   PERSISTENT MANUS PROJECT CONTEXT                     │
│  ├── Private Candidate Context (candidate_context.json)                │
│  ├── Resume Variant Documents (*.pdf, *.docx)                          │
│  ├── Imported Skill (global-job-intelligence)                          │
│  ├── Scheduled Task Session (Morning / Evening Cadence)                │
│  └── Durable Storage Artifacts:                                        │
│        • JOB_MASTER_TABLE.jsonl (Canonical Historical Dataset)        │
│        • RUN_MANIFEST.json (Audit Trail & Checksums)                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Materialize at run start
                                    ▼ (via artifact_sync.py import)
┌────────────────────────────────────────────────────────────────────────┐
│                   TEMPORARY RUNTIME WORKING SPACE                      │
│  ├── Working Dataset Copy: job_master.jsonl                            │
│  ├── Intermediate Discovery Cards & Parsed Tech Stacks                 │
│  ├── Deterministic Python Utilities (job_utils, score_job, etc.)       │
│  └── Ephemeral Execution Logs                                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Atomic export at run end
                                    ▼ (with Optimistic Concurrency Guard)
┌────────────────────────────────────────────────────────────────────────┐
│                     DURABLE ARTIFACT PERSISTENCE                       │
│  • Updated JOB_MASTER_TABLE.jsonl                                      │
│  • RUN_MANIFEST.json                                                   │
│  • Executive Daily Brief / Weekly Market Digest Markdown Report        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
global-job-intelligence/
│
├── SKILL.md                          # Main Manus Skill definition & control plane
├── README.md                         # Repository documentation and architecture guide
├── CHANGELOG.md                      # Semantic versioning history
├── .gitignore                        # Privacy and runtime artifact protections
│
├── references/                       # Domain knowledge and operational rulebooks
│   ├── search_strategy.md            # Target role taxonomy, search channels, and query patterns
│   ├── eligibility_rules.md          # Remote classification, experience thresholds, hard blockers
│   ├── scoring.md                    # 4-tier scoring formulas, weights, and priority tiers
│   ├── job_schema.md                 # Canonical data schema and Phase-1 status lifecycle
│   ├── deduplication.md              # URL canonicalization, ATS slug matching, fingerprinting
│   ├── reporting.md                  # Daily scan briefs, summary metrics, and resume gap formats
│   ├── candidate_context.md          # Private candidate schema and sufficiency levels
│   ├── runtime_contract.md           # Execution environments, fallback modes, run contracts
│   ├── persistence.md                # Durable artifacts, recovery protocols, concurrency guards
│   ├── integration_test.md           # Acceptance criteria for first live integration run
│   └── manus_project_setup.md        # Private Manus project configuration and handoff guide
│
├── templates/                        # Executable prompt templates for Manus agent runs
│   ├── scheduled_run.md              # Unified execution protocol for scheduled tasks
│   ├── integration_test.md           # First live acceptance test prompt routine
│   ├── morning_scan.md               # Thin wrapper for 24h broad discovery routine
│   ├── evening_scan.md               # Thin wrapper for incremental EU/US scan routine
│   ├── weekly_intelligence.md        # 7-day retrospective analytics and market demand digest
│   ├── manus_project_instruction.md  # Reusable Manus Project instruction directive
│   ├── candidate_context.example.json# Validated JSON template for private candidate context
│   └── candidate_context.example.md  # Markdown template for private candidate context
│
├── scripts/                          # Deterministic Python utilities (Zero External Dependencies)
│   ├── README.md                     # Script invocation map and CLI documentation
│   ├── preflight.py                  # Pre-flight environment and configuration checker
│   ├── runtime_probe.py              # Environment capability and filesystem probe
│   ├── context_validator.py          # Candidate context schema and sufficiency validator
│   ├── artifact_sync.py              # Atomic artifact import/export and concurrency guard
│   ├── run_manifest.py               # Execution manifest generator (RUN_MANIFEST.json)
│   ├── job_utils.py                  # Normalization, tracking URL cleanup, SHA-256 fingerprinting
│   ├── validate_job.py               # Pure Python schema and enum validator
│   ├── deduplicate_jobs.py           # Multi-tier duplicate detection and safe record merging
│   ├── score_job.py                  # Weighted scoring math, UNKNOWN re-normalization, status derivation
│   ├── master_dataset.py             # Atomic JSONL dataset operations (init, upsert, summary, expire)
│   └── validate_skill.py             # Comprehensive repository, privacy, and link validator
│
└── tests/                            # Automated test suite and synthetic fixtures
    ├── fixtures/                     # Pure synthetic job records (no real PII)
    │   ├── jobs_valid.jsonl
    │   ├── jobs_duplicates.jsonl
    │   ├── jobs_scoring.jsonl
    │   ├── jobs_invalid.jsonl
    │   └── integration/              # Context fixtures for integration tests
    │       ├── candidate_context_minimum.json
    │       ├── candidate_context_standard.json
    │       ├── candidate_context_enriched.json
    │       └── empty_job_master.jsonl
    ├── test_preflight.py             # Tests for preflight readiness checker
    ├── test_runtime_probe.py         # Tests for runtime execution probe
    ├── test_context_validator.py     # Tests for candidate context schema and sufficiency
    ├── test_artifact_sync.py         # Tests for artifact materialization and concurrency conflicts
    ├── test_run_manifest.py          # Tests for manifest generation and audit serialization
    ├── test_job_utils.py             # Tests for normalization, URL parsing, and fingerprinting
    ├── test_validation.py            # Tests for schema validation and forbidden Phase-1 states
    ├── test_deduplication.py         # Tests for ATS ID matching, similarity, and merging
    ├── test_scoring.py               # Tests for role weights, UNKNOWN handling, and status precedence
    └── test_master_dataset.py        # Tests for atomic persistence and dataset operations
```

---

## 🚀 Live Integration Testing Sequence

Follow this sequence to execute your first controlled live test with Manus:

1. **Run Local Pre-Flight Check:**
   ```bash
   python3 scripts/preflight.py
   ```
2. **Import Skill into Manus:** Connect your public repository in **Custom Skills**.
3. **Configure Private Project:** Follow [references/manus_project_setup.md](file:///opt/saurav/global-job-intelligence/references/manus_project_setup.md) to attach the Skill and upload `candidate_context.json`.
4. **Trigger Live Test:** Run prompt using [templates/integration_test.md](file:///opt/saurav/global-job-intelligence/templates/integration_test.md).
5. **Verify Acceptance:** Confirm acceptance criteria in [references/integration_test.md](file:///opt/saurav/global-job-intelligence/references/integration_test.md) indicate **`PASS`**.

---

## 🛠️ Automated Testing & Quality Gates

Run the complete test suite (45 unit tests, pure Python standard library):

```bash
python3 -m unittest discover tests
```

Run repository safety, link, and compilation audit:

```bash
python3 scripts/validate_skill.py
```

---

## 📄 License & Contributing

This project is licensed under the MIT License. Contributions via pull requests are welcome. Please ensure all modifications pass `python3 -m unittest discover tests` and `python3 scripts/validate_skill.py`.
