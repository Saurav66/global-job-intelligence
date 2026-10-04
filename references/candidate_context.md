# Candidate Context Contract Reference

This document defines the structured contract for private candidate data supplied by the active **Manus Project**.

> **PUBLIC REPOSITORY PRIVACY RULE:**  
> The public Skill repository contains **NO** candidate-specific personal information.  
> Candidate profile details reside exclusively in the **private Manus Project / Task context**.

---

## 1. Candidate Context Schema Overview

The candidate context can be provided as a structured JSON document or clean Markdown document that parses into the following canonical schema:

```yaml
candidate:
  identifier: String          # Anonymous ID or handle (e.g., "candidate_01")
  experience_years: Float     # Total professional years of experience (e.g., 4.5)

location:
  country: String             # ISO country name or 2-letter code (e.g., "India")
  city: String                # Optional city name (e.g., "Bengaluru")
  timezone: String            # IANA timezone (e.g., "Asia/Kolkata", "UTC+05:30")

employment_preferences:
  remote_preference: String   # REMOTE_ONLY, REMOTE_PREFERRED, HYBRID_ACCEPTABLE
  employment_types: Array     # [FULL_TIME, CONTRACT]
  timezone_tolerance: String  # Overlap tolerance (e.g., "IST_PLUS_MINUS_4H", "GLOBAL_ANY")

compensation:
  minimum: Float              # Optional minimum acceptable annual base compensation
  target: Float               # Optional target annual base compensation
  currency: String            # ISO 4217 Currency Code (e.g., "USD", "INR")
  period: String              # ANNUAL, MONTHLY, HOURLY

capabilities:
  primary_domains: Array      # e.g., ["DevSecOps", "Platform Engineering", "Cloud Infrastructure"]
  secondary_domains: Array    # e.g., ["AI Infrastructure", "SRE"]
  cloud: Array                # e.g., ["AWS", "GCP"]
  containers: Array           # e.g., ["Kubernetes", "Docker", "Helm"]
  iac: Array                  # e.g., ["Terraform", "OpenTofu", "Terragrunt"]
  cicd: Array                 # e.g., ["GitHub Actions", "ArgoCD", "GitLab CI"]
  programming: Array          # e.g., ["Python", "Go", "Bash"]
  observability: Array        # e.g., ["Prometheus", "Grafana", "Datadog", "OpenTelemetry"]
  security: Array             # e.g., ["Trivy", "Snyk", "Vault", "IAM"]
  ai_ml: Array                # e.g., ["vLLM", "Ray", "Qdrant", "RAG", "Ollama"]
  databases: Array            # e.g., ["PostgreSQL", "Redis", "Kafka"]
  networking: Array           # e.g., ["VPC", "DNS", "Service Mesh", "Istio"]
  product_experience: Array   # e.g., ["SaaS B2B", "Enterprise Infrastructure"]

capability_confidence:
  # Map of capability to confidence level: CORE, STRONG, WORKING, EXPOSURE
  AWS: "CORE"
  Kubernetes: "CORE"
  Terraform: "CORE"
  Python: "STRONG"
  Go: "WORKING"
  vLLM: "WORKING"

resume_variants:
  - id: String                # e.g., "devsecops_senior"
    label: String             # e.g., "Senior DevSecOps & Platform Track"
    focus: String             # Key highlights of this resume version
    artifact_ref: String      # Optional filename inside private Manus project (e.g., "resume_devsecops.pdf")

role_preferences:
  primary: Array              # Target roles (e.g., ["Senior DevSecOps Engineer", "Senior Platform Engineer"])
  secondary: Array            # Acceptable adjacent roles (e.g., ["AI Platform Engineer", "SRE"])
  experimental: Array         # Stretch roles (e.g., ["Forward Deployed Engineer"])
  excluded: Array             # Explicitly disqualified titles (e.g., ["Frontend Engineer", "Engineering Manager"])

work_authorization:
  countries: Array            # Countries candidate holds citizenship or right to work (e.g., ["India"])
  sponsorship_required: Bool  # Whether foreign visa sponsorship is required for overseas entities

search_preferences:
  target_geographies: Array   # e.g., ["GLOBAL", "INDIA", "US_REMOTE_GLOBAL_CONTRACT", "EMEA_APAC"]
  excluded_geographies: Array # e.g., ["US_ONSITE", "UK_ONSITE"]
  target_role_families: Array # e.g., ["CORE_DEVOPS_PLATFORM", "SECURITY_INFRASTRUCTURE", "AI_INFRASTRUCTURE"]
  excluded_role_families: Array # e.g., ["EXECUTIVE_MANAGEMENT", "PURE_FRONTEND"]
```

---

## 2. Context Sufficiency Levels

The system gracefully adapts its scoring accuracy based on the depth of candidate context provided:

| Level | Required Fields | System Behavior |
| :--- | :--- | :--- |
| **MINIMUM** | • `location.country`<br>• `candidate.experience_years`<br>• `capabilities.primary_domains`<br>• `role_preferences.primary` | **Functional.** Executes broad discovery and basic capability scoring. Missing dimensions (salary, tool confidence) are handled via dynamic weight re-normalization. |
| **STANDARD** | *All MINIMUM fields plus:*<br>• Detailed tool arrays (`cloud`, `containers`, `iac`, `cicd`, `programming`)<br>• `employment_preferences.remote_preference`<br>• `resume_variants` | **Recommended.** Enables precise role-aware capability scoring, ATS deduplication, and resume representation hold analysis. |
| **ENRICHED** | *All STANDARD fields plus:*<br>• `compensation` targets & currency<br>• `capability_confidence` mapping<br>• `work_authorization`<br>• `search_preferences` and exclusions | **Maximum Precision.** Enables exact compensation filtering, timezone suitability checks, and tailored resume variant selection. |

---

## 3. Capability Confidence Scale

When detailed capability confidence is supplied:
- `CORE`: Daily production expertise; deep architectural mastery ($\ge 90\%$ score credit).
- `STRONG`: Significant hands-on production experience ($\approx 80–89\%$ score credit).
- `WORKING`: Practical working knowledge, side-projects, or lab experience ($\approx 65–79\%$ score credit).
- `EXPOSURE`: Conceptual familiarity or basic tutorial experience ($\approx 40–60\%$ score credit).

---

## 4. Candidate Capability vs. Resume Artifact Truth

1. **Candidate Profile Context is the Primary Source of Truth:**  
   The candidate's actual capabilities are defined by this private context document.
2. **Resumes are Presentation Artifacts:**  
   If a skill is listed in `capabilities` but omitted from the active resume variant, the system calculates a high Candidate Capability Score ($S_{\text{capability}}$) and flags the missing item as a **Resume Representation Gap** ($S_{\text{resume}} < 75 \rightarrow \text{status = HOLD\_RESUME\_UPDATE}$).
3. **Never Infer Skill Absence from Resume Omissions:**  
   The agent must never conclude a candidate lacks a proficiency solely because it is absent from a specific PDF/Word document.
