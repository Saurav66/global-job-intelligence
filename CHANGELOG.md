# Changelog

All notable changes to the **Global Job Intelligence** Skill repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.1] - 2026-10-04

### Added — Live Integration Test Readiness & Operational Hardening

#### Added
- **Integration Test Contract (`references/integration_test.md`):** Formalized specification for the first live Manus integration test with controlled discovery volume (5–10 jobs), acceptance verification matrix (`PASS`, `PARTIAL PASS`, `FAIL`), and standardized reporting layout.
- **Manus Project Setup Guide (`references/manus_project_setup.md`):** Complete step-by-step instructions for importing the GitHub Skill, attaching it to a private Manus Project, uploading private candidate context & resumes, and running the live test.
- **Integration Test Routine (`templates/integration_test.md`):** Executable prompt routine configured for `RUN_MODE=INTEGRATION_TEST` with automatic one-time switch to `MANUAL_FALLBACK` if script execution is restricted.
- **Manus Project Instruction Directive (`templates/manus_project_instruction.md`):** Reusable, token-efficient Project instruction establishing Phase-1 boundaries, persistence rules, and zero-fabrication directives.
- **Validated Candidate Context JSON Template (`templates/candidate_context.example.json`):** Pure JSON context template conforming to `context_validator.py` with generic placeholders.
- **Runtime Probe Utility (`scripts/runtime_probe.py`):** Standard-library execution capability detector testing Python, filesystem read/write, atomic file replacements, and script accessibility without leaking secrets or environment variables.
- **Pre-Flight Checker (`scripts/preflight.py`):** Pre-execution verification tool orchestrating runtime probing, candidate context validation, and dataset integrity checks with human-readable and `--json` outputs.
- **Integration Test Fixtures (`tests/fixtures/integration/`):** Synthetic test datasets for minimum, standard, and enriched context configurations, plus empty dataset templates.
- **Expanded Test Suite (`tests/`):** Added tests for runtime probing (`test_runtime_probe.py`) and preflight orchestration (`test_preflight.py`), bringing the automated test suite to 45 passing unit tests.

#### Changed
- **Run Manifest Engine (`scripts/run_manifest.py`):** Bumped `SKILL_VERSION` to `0.3.1` and added `INTEGRATION_TEST` to supported run modes.
- **Validator Upgrade (`scripts/validate_skill.py`):** Upgraded to verify all v0.3.1 files, ensure template placeholder safety, and enforce `0.3.1` version consistency.
- **Runtime Contract (`references/runtime_contract.md`):** Added explicit directive instructing the agent to switch once immediately to `MANUAL_FALLBACK` if script execution is restricted, avoiding repeated retry loops.

---

## [0.3.0] - 2026-10-04

### Added — Runtime Contracts, Artifact Persistence & Execution Manifests

#### Added
- Candidate context specification, persistence lifecycle, dataset recovery cases, artifact synchronization, and run manifest generation.

---

## [0.2.0] - 2026-10-04

### Added — Deterministic Phase-1 Processing & Automated Testing

#### Added
- Deterministic normalization, schema validation, deduplication, scoring math, and atomic JSONL dataset manager.

---

## [0.1.0] - 2026-10-04

### Initial Release — Phase-1 Job Intelligence Architecture

#### Added
- Initial Phase-1 job intelligence repository architecture, search strategy, scoring rules, schema, and templates.
