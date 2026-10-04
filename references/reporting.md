# Reporting Format Reference

This reference defines the standardized reporting formats for daily scans (morning/evening) and weekly intelligence summaries.

---

## 1. Daily Discovery Report Format

Every scan produces a structured, actionable Markdown intelligence brief. Reports must prioritize high-scoring opportunities and maintain clear separation between candidate capability and resume presentation.

### Structure of the Daily Scan Report

```markdown
# Global Job Intelligence — Daily Scan Brief
**Execution Timestamp:** YYYY-MM-DD HH:MM UTC  
**Scan Type:** Morning Scan / Evening Scan  
**Target Profile:** <CANDIDATE_TITLE> (<BASE_LOCATION> Remote)  
**Execution Mode:** DETERMINISTIC / HYBRID_FALLBACK / MANUAL_FALLBACK  
**Run ID:** 20261004T080000Z-MORNING-XXXXXXXX (See `RUN_MANIFEST.json`)

---

## 1. Executive Summary & Funnel Metrics

| Metric | Count | Notes |
| :--- | :---: | :--- |
| **Raw Listings Discovered** | XX | Multi-channel queries executed |
| **Duplicates Removed / Updated** | XX | Matched to existing master records |
| **Hard-Filter Disqualifications** | XX | Location restricted, clearance, level mismatch |
| **Unique Opportunities Analyzed** | XX | Deep technical and eligibility evaluation |
| **Tier A+ Shortlist (Score 90–100)** | XX | Priority immediate review |
| **Tier A Shortlist (Score 85–89)** | XX | High-confidence opportunities |
| **Tier B Shortlist (Score 75–84)** | XX | Viable backup / specialized matches |
| **Tier C Shortlist (Score 65–74)** | XX | Moderate viability |
| **Hold for Resume Update** | XX | Qualified candidate, resume narrative gap |

---

## 2. Priority Shortlisted Opportunities (A+ & A Tiers)

| Score | Company | Role | Role Family | Remote Eligibility | Location | Advertised Salary | Recommended Resume | Status | Official Link |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **92** | CloudNative Labs | Senior DevSecOps Engineer | Security / Infra | `REMOTE_GLOBAL` | Worldwide | $140k - $175k USD | `DevSecOps_Senior` | `SHORTLIST_A_PLUS` | [View ATS](https://...) |
| **88** | Synthetix AI | AI Infrastructure Engineer | AI Infrastructure | `REMOTE_GLOBAL` | Remote (Any) | $160k - $190k USD | `AI_Infra_Platform` | `SHORTLIST_A` | [View ATS](https://...) |

### Deep Dive: Priority Highlights

#### 1. [Company Name] — [Job Title] (Score: XX/100)
- **Official URL:** [Direct Canonical Link]
- **Compensation:** Disclosed / Undisclosed
- **Remote Modality:** `REMOTE_GLOBAL` (Verified worldwide remote)
- **Key Technical Matches:** Kubernetes, Terraform AWS IaC, automated CI/CD security pipelines.
- **Identified Gaps / Stretch:** Go experience preferred for custom operator development.
- **Recommended Action:** Review job details. Ensure candidate's Kubernetes security projects are front-and-center.

---

## 3. Notable Resume Representation Gaps

> **Evaluation Rule:** A gap here indicates a skill the candidate has demonstrated in practice, but which is missing or weak in the target resume document.

| Role / Target Family | High-Value Required Skill | Current Resume State | Suggested Resume Narrative Addition |
| :--- | :--- | :--- | :--- |
| AI Platform Roles | vLLM / Model Serving Deployment | Lacks explicit keyword | Highlight GPU cluster orchestration and inference container scaling. |
| Security Roles | Automated SAST/DAST in CI/CD | Present as bullet | Emphasize pipeline policy-as-code (Trivy / OPA) in summary. |

---

## 4. Disqualification Breakdown & Statistics

| Rejection Category | Count | Primary Reason Observed |
| :--- | :---: | :--- |
| **Location / Residency Restricted** | XX | Explicit US-only / UK-only / EU residency required |
| **Mandatory Security Clearance** | XX | US DoD Secret / TS-SCI mandatory |
| **Seniority Mismatch** | XX | Entry-level / Executive VP / strict 10+ year requirements |
| **Unrelated Domain** | XX | Non-technical, pure frontend, or sales roles |
| **Expired / Closed** | XX | Requisition closed or link inactive |

---

## 5. Storage & State Update

- **Master Dataset Status:** Updated `jobs.json` / master database with XX new unique records.
- **Phase Boundary Notice:** No automated applications were submitted. Phase 1 operates strictly as a discovery and qualification intelligence system.
```

---

## 2. Table Column Standards

When outputting the primary opportunities table, adhere to the following column standards:

1. **Score:** Final composite score ($S_{\text{final}}$).
2. **Company:** Clean, normalized organization name.
3. **Role:** Full official job title.
4. **Role Family:** Normalized track (`Core DevOps`, `Security / Infra`, `AI Infra`, `Solutions`).
5. **Remote Eligibility:** Normalized classification code (`REMOTE_GLOBAL`, `REMOTE_INDIA`, `REMOTE_APAC_INDIA_ALLOWED`, etc.).
6. **Location:** Geographic scope as posted.
7. **Salary:** Disclosed currency and range, or `UNDISCLOSED`.
8. **Main Matches:** Top matching strengths (e.g., K8s, Terraform, AWS).
9. **Main Gap:** Primary missing technology or stretch requirement.
10. **Recommended Resume:** Best matching resume profile.
11. **Status:** Normalized status enum (`SHORTLIST_A_PLUS`, `HOLD_RESUME_UPDATE`, etc.).
12. **Official URL:** Markdown link pointing to direct canonical ATS / career page.
