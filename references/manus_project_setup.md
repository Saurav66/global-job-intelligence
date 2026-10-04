# Manus Project Setup & Candidate Handoff Reference

This reference outlines the exact steps to configure a private **Manus Project** with the imported **Global Job Intelligence Skill**, securely supply private candidate data, and execute the initial integration test.

---

## 1. Setup Architecture Overview

```
[ Public GitHub Repository ] ──────────────────(Import Skill)──┐
  • Generic workflow logic & scripts                            │
  • Zero candidate PII                                          ▼
                                                  ┌───────────────────────────┐
                                                  │   PRIVATE MANUS PROJECT   │
[ Private Candidate Files ] ──────(Upload)───────►│  • candidate_context.json │
  • Capabilities & preferences                    │  • resume_devsecops.pdf   │
  • Resume variants (*.pdf)                       │  • Attached Skill         │
                                                  └─────────────┬─────────────┘
                                                                │ (Start Task)
                                                                ▼
                                                  ┌───────────────────────────┐
                                                  │ 1. Run Integration Test   │
                                                  │ 2. Establish Schedules    │
                                                  └───────────────────────────┘
```

---

## 2. Step-by-Step Setup Procedure

### Step 1: Import Skill into Manus
1. In your Manus Dashboard, open **Settings** $\rightarrow$ **Custom Skills** (or **Skills Hub**).
2. Click **Import Skill from GitHub** and provide your public repository URL:
   ```text
   https://github.com/<YOUR_GITHUB_USERNAME>/global-job-intelligence
   ```
3. Manus will automatically discover [SKILL.md](file:///opt/saurav/global-job-intelligence/SKILL.md) and load supporting references and templates.

### Step 2: Create a Private Manus Project
1. Create a new Project named **"Global Job Intelligence — Personal"** (or your preferred title).
2. Attach the imported **`global-job-intelligence`** Skill to this project.
3. Configure the Project Instruction using the template in [templates/manus_project_instruction.md](file:///opt/saurav/global-job-intelligence/templates/manus_project_instruction.md).

### Step 3: Add Private Candidate Profile to Project
1. Copy [templates/candidate_context.example.json](file:///opt/saurav/global-job-intelligence/templates/candidate_context.example.json) as a starting baseline.
2. Fill in your real capabilities, target domains, experience years, and compensation targets.
3. Save as `candidate_context.json` and upload it directly into the Manus Project files.
4. *Security check:* Ensure your real `candidate_context.json` is NEVER committed to your public GitHub repository.

### Step 4: Add Resume Documents to Project
1. Upload your primary resume variants (e.g., `resume_devsecops.pdf`, `resume_ai_infra.pdf`) to the Project files.
2. Ensure the file names match the `artifact_ref` values defined in your `candidate_context.json`.

### Step 5: Execute First Live Integration Test
1. Start a task inside your private Project with the prompt:
   ```text
   Execute the live acceptance integration test using templates/integration_test.md.
   ```
2. Verify that:
   - Candidate context is validated.
   - 5–10 viable live opportunities are discovered, deduplicated, and scored.
   - `JOB_MASTER_TABLE.jsonl` and `RUN_MANIFEST.json` are generated.
   - The report indicates an acceptance status of **PASS**.

### Step 6: Establish Production Schedules
1. After a successful integration test, configure your recurring task schedule in Manus:
   - **Morning Scan (08:00 Local):** Uses [templates/morning_scan.md](file:///opt/saurav/global-job-intelligence/templates/morning_scan.md).
   - **Evening Scan (18:00 Local):** Uses [templates/evening_scan.md](file:///opt/saurav/global-job-intelligence/templates/evening_scan.md).
