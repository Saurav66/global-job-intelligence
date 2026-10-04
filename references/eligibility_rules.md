# Eligibility & Hard-Blocker Rules Reference

This document outlines the evaluation logic for geographic remote eligibility, candidate experience thresholds, hard disqualification criteria, and the critical distinction between candidate capability and resume representation.

---

## 1. Candidate Context & Baseline Profile

Candidate-specific parameters (exact location, citizenship, target preferences, and specific skill inventories) are supplied via the private Manus Project context.

The default system profile is configured for:
- **Base Location:** India
- **Target Work Modality:** Global Remote / International Remote / India Remote
- **Professional Experience Baseline:** Approximately **4.5+ years** of relevant software engineering, cloud, infrastructure, and DevOps experience.

---

## 2. Remote Modality Classification

Job listings frequently use ambiguous phrasing (e.g., "Remote", "Work from Anywhere", "Remote - US/EMEA"). Every opportunity must be assigned exactly one normalized `remote_type`:

| Classification | Definition | Default Eligibility for India-based Candidate |
| :--- | :--- | :--- |
| `REMOTE_GLOBAL` | Explicitly hiring worldwide / anywhere without country limitations. | **ELIGIBLE** |
| `REMOTE_INDIA` | Remote within India or company has an established India entity hiring remotely. | **ELIGIBLE** |
| `REMOTE_APAC_INDIA_ALLOWED` | Remote within APAC / EMEA where India is explicitly or implicitly included. | **ELIGIBLE** |
| `REMOTE_INTERNATIONAL_INDIA_ALLOWED` | US/EU/UK company hiring global contractors or Employer of Record (EOR) in India. | **ELIGIBLE** |
| `REMOTE_COUNTRY_RESTRICTED` | Remote, but strictly restricted to specific foreign countries (e.g., "US Only", "Must reside in Germany"). | **BLOCKED (Hard Reject)** |
| `HYBRID` | Requires physical presence in an office for 1–4 days per week/month in an incompatible city. | **BLOCKED (Hard Reject)** |
| `ONSITE` | 100% in-person requirement in an incompatible foreign/domestic city. | **BLOCKED (Hard Reject)** |
| `UNKNOWN` | Listing states "Remote" with no geographic boundaries or contradictory statements. | **FLAG FOR REVIEW (`REVIEW_LOCATION`)** |

> **CRITICAL RULE ON REMOTE ELIGIBILITY:**
> - The term "Remote" does **NOT** automatically imply worldwide eligibility.
> - If remote boundaries cannot be verified from the listing, assign `remote_type = UNKNOWN` and `status = REVIEW_LOCATION`.
> - **NEVER fabricate eligibility.** When evidence is absent, record `UNKNOWN`.

---

## 3. Experience Fit & Seniority Thresholds

The system evaluates experience requirements against the candidate's baseline (~4.5+ years):

### Target & Acceptable Ranges
- **Ideal Target:** Roles specifying **3 to 7 years** of experience.
- **Acceptable Stretch:** Roles specifying **7 to 8 years** when the candidate's core infrastructure, Kubernetes, and cloud alignment is exceptionally strong.
- **Explicit Inclusions:**
  - Roles requesting **"5+ years"** MUST NOT be filtered out.
  - Roles requesting **"6+ years"** MUST remain viable candidates for evaluation.
  - Mid-level, Senior, and Lead Individual Contributor (IC) roles without hard executive duties are fully eligible.

### Hard Disqualification Thresholds
- **Under-level / Entry-level:** Internships, graduate trainee programs, associate/junior roles with < 2 years target experience.
- **Over-level / Executive:** Vice President (VP), Director, Head of Department, Executive management roles.
- **Extreme Seniority:** Requisitions demanding a strict minimum of **10+ years** of experience (unless an exceptional tech stack match justifies manual review).

---

## 4. Hard Blockers (Immediate Rejection Criteria)

If any of the following conditions are met, the job record is immediately assigned `status = REJECTED` and the specific `rejection_reason` is recorded:

1. **Incompatible Geographic / Residency Requirement:**
   - Explicit requirement for physical residence or work authorization in restricted countries (e.g., "Must be authorized to work in the US without sponsorship", "UK resident only", "EU citizenship required").
2. **Mandatory Inaccessible Security Clearances:**
   - Active US DoD Secret/Top Secret, TS/SCI, UK SC/DV clearance, or foreign government-mandated security clearances that a remote international candidate cannot obtain.
3. **Incompatible In-Person Work Requirement:**
   - Mandatory on-site or hybrid attendance at a foreign office location.
4. **Target Role Mismatch:**
   - Roles unrelated to software, DevOps, infrastructure, cloud, security, or AI platform domains (e.g., pure frontend UX, sales, non-technical PM, hardware support).
5. **Requisition Closed / Expired:**
   - Position no longer accepting applications or returns an HTTP 404/410.

---

## 5. Candidate Capability vs. Resume Coverage (Non-Rejection Rules)

A core tenet of this system is that **a candidate's actual capabilities and the textual contents of their current resume are distinct entities.**

### Rules for Preserving Viable Opportunities:
1. **Never Reject for Missing Resume Keywords:**
   - Do NOT reject an otherwise strong opportunity simply because the candidate's current resume PDF/doc does not explicitly mention a specific tool, framework, or keyword.
2. **Never Reject for Go (Golang) / Secondary Languages:**
   - Do NOT reject a strong infrastructure/DevOps role solely because Go is listed as required/preferred. A candidate with strong systems and scripting background can qualify.
3. **Never Reject for AI/LLM Mentions:**
   - Do NOT filter out platform roles that mention AI/LLM infrastructure or MLOps integrations. Treat these as high-upside opportunities.
4. **Never Reject Solely Due to Low Resume Coverage:**
   - If Candidate Capability Score is high (e.g., 85+) but Resume Coverage Score is low (e.g., 55), the job MUST NOT be rejected. Assign `status = HOLD_RESUME_UPDATE`.
