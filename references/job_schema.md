# Job Data Schema Reference

This reference defines the normalized data schema for job records in the Phase-1 Global Job Intelligence system.

The schema is designed to be storage-agnostic and maps cleanly to **JSON Lines (JSONL)**, **CSV**, **SQLite / PostgreSQL**, and **Google Sheets / Airtable**.

> **Deterministic Implementation:** Schema enforcement is implemented in [`scripts/validate_job.py`](file:///opt/saurav/global-job-intelligence/scripts/validate_job.py) and dataset management in [`scripts/master_dataset.py`](file:///opt/saurav/global-job-intelligence/scripts/master_dataset.py).

---

## 1. Field Definitions

| Field Name | Type | Description / Allowed Values | Nullable / Default |
| :--- | :--- | :--- | :--- |
| `job_id` | String | Unique deterministic hash (e.g., `SHA256(canonical_url)` or company-title-ats slug). | **Required** |
| `first_seen_at` | ISO8601 String | Timestamp when first discovered (`YYYY-MM-DDTHH:MM:SSZ`). | **Required** |
| `last_seen_at` | ISO8601 String | Timestamp when last confirmed active (`YYYY-MM-DDTHH:MM:SSZ`). | **Required** |
| `company` | String | Normalized hiring company name (e.g., "Datadog", "Scale AI"). | **Required** |
| `job_title` | String | Official job title as posted (e.g., "Senior DevSecOps Engineer"). | **Required** |
| `role_family` | String | Primary role family: `CORE_DEVOPS_PLATFORM`, `SECURITY_INFRASTRUCTURE`, `AI_INFRASTRUCTURE`, `CLIENT_DEPLOYMENT`. | **Required** |
| `secondary_role_family` | String | Optional secondary alignment (e.g., `AI_INFRASTRUCTURE`). | Nullable |
| `seniority` | String | Normalized level: `MID`, `SENIOR`, `STAFF`, `LEAD`, `PRINCIPAL`, `UNKNOWN`. | `UNKNOWN` |
| `source` | String | Discovery origin (e.g., `GREENHOUSE`, `LEVER`, `ASHBY`, `HIMALAYAS`, `LINKEDIN`). | **Required** |
| `source_url` | String | Original URL where the listing was discovered. | **Required** |
| `canonical_url` | String | Direct ATS / careers page URL for the requisition. | **Required** |
| `posted_date` | String | Original posting date if available (`YYYY-MM-DD`) or `UNKNOWN`. | `UNKNOWN` |
| `job_age_days` | Integer | Calculated days elapsed since posting, or `null`. | Nullable |
| `location` | String | Raw location string from listing (e.g., "Remote - Global", "Bengaluru, India"). | **Required** |
| `remote_type` | String | Enum: `REMOTE_GLOBAL`, `REMOTE_INDIA`, `REMOTE_APAC_INDIA_ALLOWED`, `REMOTE_INTERNATIONAL_INDIA_ALLOWED`, `REMOTE_COUNTRY_RESTRICTED`, `HYBRID`, `ONSITE`, `UNKNOWN`. | **Required** |
| `candidate_location_eligible`| Boolean / String | `true`, `false`, or `"UNKNOWN"`. | **Required** |
| `country_restrictions` | Array / String | List of restricted countries or `"NONE"`. | `[]` |
| `timezone_requirements` | String | Overlap requirement (e.g., "EST 4hr overlap", "APAC", "None"). | `UNKNOWN` |
| `employment_type` | String | `FULL_TIME`, `CONTRACT`, `PART_TIME`, `UNKNOWN`. | `FULL_TIME` |
| `experience_min` | Float / Int | Minimum years of experience specified in posting. | Nullable |
| `experience_max` | Float / Int | Maximum years of experience specified in posting. | Nullable |
| `salary_min` | Float | Minimum base compensation advertised. | Nullable |
| `salary_max` | Float | Maximum base compensation advertised. | Nullable |
| `currency` | String | ISO 4217 Currency Code (e.g., `USD`, `INR`, `EUR`, `GBP`) or `UNKNOWN`. | `UNKNOWN` |
| `salary_period` | String | `ANNUAL`, `MONTHLY`, `HOURLY`, `UNKNOWN`. | `UNKNOWN` |
| `salary_disclosed` | Boolean | `true` if compensation was explicitly listed; `false` otherwise. | `false` |
| `required_skills` | Array of String | Key mandatory tools and technical competencies. | `[]` |
| `preferred_skills` | Array of String | Secondary / nice-to-have competencies. | `[]` |
| `cloud_platforms` | Array of String | Extracted cloud targets (e.g., `["AWS", "GCP", "Azure"]`). | `[]` |
| `programming_languages`| Array of String | Extracted languages (e.g., `["Python", "Go", "Bash"]`). | `[]` |
| `container_tools` | Array of String | Extracted container stack (e.g., `["Kubernetes", "Docker", "Helm"]`). | `[]` |
| `iac_tools` | Array of String | Extracted IaC stack (e.g., `["Terraform", "OpenTofu", "Pulumi"]`). | `[]` |
| `cicd_tools` | Array of String | Extracted CI/CD stack (e.g., `["GitHub Actions", "ArgoCD"]`). | `[]` |
| `security_tools` | Array of String | Extracted security stack (e.g., `["Trivy", "Snyk", "Vault"]`). | `[]` |
| `observability_tools` | Array of String | Extracted telemetry stack (e.g., `["Prometheus", "Datadog", "OTel"]`). | `[]` |
| `ai_ml_requirements` | Array of String | Extracted AI/ML stack (e.g., `["vLLM", "Qdrant", "RAG", "Ray"]`). | `[]` |
| `candidate_capability_score`| Float | Calculated score (0.0 – 100.0). | Nullable |
| `opportunity_score` | Float | Calculated score (0.0 – 100.0). | Nullable |
| `final_score` | Float | Composite score ($S_{\text{capability}} \times 0.6 + S_{\text{opportunity}} \times 0.4$). | Nullable |
| `resume_coverage_score`| Float | Score assessing current resume presentation match (0.0 – 100.0). | Nullable |
| `recommended_resume` | String | Identifier for best-fit resume track (e.g., `"DevSecOps_Platform"`, `"AI_Infra"`). | Nullable |
| `priority` | String | Priority tier: `A_PLUS`, `A`, `B`, `C`, `LOW`, `REJECT`. | `LOW` |
| `status` | String | Valid Phase-1 status (see Status Life-Cycle below). | `NEW` |
| `hard_blocker` | Boolean | `true` if an immediate disqualification trigger was tripped. | `false` |
| `rejection_reason` | String | Explanation of rejection (e.g., `"US_CITIZENSHIP_ONLY"`, `"ONSITE_UK"`). | Nullable |
| `main_matches` | Array of String | Core strengths / capabilities matching the job description. | `[]` |
| `main_gaps` | Array of String | Missing technologies or resume presentation gaps. | `[]` |
| `short_reason` | String | One-sentence summary explaining the scoring and status. | Nullable |
| `notes` | String | Additional context, recruiter notes, or specific company signals. | Nullable |

---

## 2. Valid Phase-1 Status Lifecycle

Every record must maintain a valid state from the following enumerated set:

- `NEW`: Discovered during broad scan, pending deep qualification.
- `SHORTLIST_A_PLUS`: Top-tier opportunity (Final Score 90–100, verified remote eligibility).
- `SHORTLIST_A`: Strong opportunity (Final Score 85–89).
- `SHORTLIST_B`: Viable opportunity (Final Score 75–84).
- `SHORTLIST_C`: Moderate opportunity (Final Score 65–74).
- `HOLD_RESUME_UPDATE`: Qualified candidate ($S_{\text{capability}} \ge 85$), but existing resume representation is deficient ($S_{\text{resume}} < 75$).
- `REVIEW_LOCATION`: Location eligibility is ambiguous or unverified (`remote_type = UNKNOWN`).
- `REVIEW_SALARY`: High-quality company/role requiring compensation clarification.
- `DUPLICATE`: Redundant posting already represented by an existing canonical record.
- `REJECTED`: Disqualified by hard blockers or low match score ($S_{\text{final}} < 65$).
- `EXPIRED`: Position confirmed closed, unlisted, or expired.

> **CRITICAL PHASE-1 BOUNDARY:**
> - `APPLIED` is **NOT** a valid Phase-1 status.
> - The Phase-1 system strictly discovers and qualifies opportunities. It does not submit applications.

---

## 3. Storage Formats

### A. JSON Record Example
```json
{
  "job_id": "sha256_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "first_seen_at": "2026-10-04T08:00:00Z",
  "last_seen_at": "2026-10-04T08:00:00Z",
  "company": "CloudNative Labs",
  "job_title": "Senior DevSecOps Engineer",
  "role_family": "SECURITY_INFRASTRUCTURE",
  "secondary_role_family": "CORE_DEVOPS_PLATFORM",
  "seniority": "SENIOR",
  "source": "ASHBY",
  "source_url": "https://jobs.ashbyhq.com/cloudnative-labs/12345",
  "canonical_url": "https://jobs.ashbyhq.com/cloudnative-labs/12345",
  "posted_date": "2026-10-03",
  "job_age_days": 1,
  "location": "Remote - Worldwide",
  "remote_type": "REMOTE_GLOBAL",
  "candidate_location_eligible": true,
  "country_restrictions": [],
  "timezone_requirements": "UTC-5 to UTC+5 overlap",
  "employment_type": "FULL_TIME",
  "experience_min": 4.0,
  "experience_max": 7.0,
  "salary_min": 140000.0,
  "salary_max": 175000.0,
  "currency": "USD",
  "salary_period": "ANNUAL",
  "salary_disclosed": true,
  "required_skills": ["Kubernetes", "Terraform", "AWS", "CI/CD Security", "Python"],
  "preferred_skills": ["ArgoCD", "Trivy", "Go"],
  "cloud_platforms": ["AWS"],
  "programming_languages": ["Python", "Go", "Bash"],
  "container_tools": ["Kubernetes", "Docker", "Helm"],
  "iac_tools": ["Terraform"],
  "cicd_tools": ["GitHub Actions", "ArgoCD"],
  "security_tools": ["Trivy", "Snyk", "AWS IAM"],
  "observability_tools": ["Prometheus", "Grafana"],
  "ai_ml_requirements": [],
  "candidate_capability_score": 92.0,
  "opportunity_score": 90.0,
  "final_score": 91.2,
  "resume_coverage_score": 88.0,
  "recommended_resume": "DevSecOps_Platform_Senior",
  "priority": "A_PLUS",
  "status": "SHORTLIST_A_PLUS",
  "hard_blocker": false,
  "rejection_reason": null,
  "main_matches": ["Strong AWS & K8s DevSecOps alignment", "Terraform & CI/CD pipeline automation"],
  "main_gaps": ["Go listed as nice-to-have"],
  "short_reason": "Excellent global remote match with transparent US-tier compensation.",
  "notes": "Direct Ashby listing. Verified global contractor hiring."
}
```

### B. CSV Mapping
When exporting to CSV, nested arrays (e.g., `required_skills`, `cloud_platforms`) are serialized as semicolon-delimited strings (e.g., `"Kubernetes;Terraform;AWS"`).
