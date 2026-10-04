# Example Candidate Context Template (Private Context)

> **⚠️ PRIVACY NOTICE:**  
> This file is a generic demonstration template containing **fictional placeholders**.  
> **DO NOT** commit real candidate contact details, actual resumes, or personal compensation information to the public repository.  
> Your actual candidate profile should be saved inside your **private Manus Project / Session prompt**.

---

```json
{
  "candidate": {
    "identifier": "<CANDIDATE_ID_PLACEHOLDER>",
    "experience_years": 4.5
  },
  "location": {
    "country": "<BASE_COUNTRY_PLACEHOLDER>",
    "city": "<BASE_CITY_PLACEHOLDER>",
    "timezone": "Asia/Kolkata"
  },
  "employment_preferences": {
    "remote_preference": "REMOTE_ONLY",
    "employment_types": ["FULL_TIME", "CONTRACT"],
    "timezone_tolerance": "GLOBAL_ANY"
  },
  "compensation": {
    "minimum": 120000.0,
    "target": 150000.0,
    "currency": "USD",
    "period": "ANNUAL"
  },
  "capabilities": {
    "primary_domains": ["DevSecOps", "Platform Engineering", "Cloud Infrastructure"],
    "secondary_domains": ["AI Infrastructure", "Site Reliability Engineering (SRE)"],
    "cloud": ["AWS", "GCP"],
    "containers": ["Kubernetes", "Docker", "Helm", "Kustomize"],
    "iac": ["Terraform", "OpenTofu"],
    "cicd": ["GitHub Actions", "ArgoCD", "GitLab CI"],
    "programming": ["Python", "Go", "Bash"],
    "observability": ["Prometheus", "Grafana", "Datadog", "OpenTelemetry"],
    "security": ["Trivy", "Snyk", "AWS IAM", "Vault", "SAST/DAST"],
    "ai_ml": ["vLLM", "Ray", "Qdrant", "Pinecone", "RAG", "Ollama"],
    "databases": ["PostgreSQL", "Redis", "Kafka"],
    "networking": ["VPC", "DNS", "Service Mesh", "Istio"],
    "product_experience": ["Cloud-Native SaaS", "Distributed Systems"]
  },
  "capability_confidence": {
    "AWS": "CORE",
    "Kubernetes": "CORE",
    "Terraform": "CORE",
    "CI/CD Security": "CORE",
    "Python": "STRONG",
    "ArgoCD": "STRONG",
    "Go": "WORKING",
    "vLLM": "WORKING",
    "Ray": "WORKING",
    "Qdrant": "WORKING"
  },
  "resume_variants": [
    {
      "id": "devsecops_platform_senior",
      "label": "Senior DevSecOps & Cloud Platform Track",
      "focus": "Automated security scanning in CI/CD, Kubernetes infrastructure, and Terraform automation.",
      "artifact_ref": "resume_devsecops.pdf"
    },
    {
      "id": "ai_infra_platform",
      "label": "AI Platform & LLM Infrastructure Track",
      "focus": "GPU cluster orchestration, vLLM/Ray deployment, and vector database management.",
      "artifact_ref": "resume_ai_infra.pdf"
    }
  ],
  "role_preferences": {
    "primary": [
      "Senior DevSecOps Engineer",
      "Senior Platform Engineer",
      "Senior DevOps Engineer",
      "Cloud Platform Engineer"
    ],
    "secondary": [
      "AI Platform Engineer",
      "AI Infrastructure Engineer",
      "Senior Site Reliability Engineer (SRE)"
    ],
    "experimental": [
      "Forward Deployed Engineer",
      "Platform Solutions Engineer"
    ],
    "excluded": [
      "Frontend Engineer",
      "Engineering Manager",
      "Technical Recruiter"
    ]
  },
  "work_authorization": {
    "countries": ["<BASE_COUNTRY_PLACEHOLDER>"],
    "sponsorship_required": true
  },
  "search_preferences": {
    "target_geographies": ["REMOTE_GLOBAL", "REMOTE_INDIA", "REMOTE_APAC_INDIA_ALLOWED", "REMOTE_INTERNATIONAL_INDIA_ALLOWED"],
    "excluded_geographies": ["US_ONSITE", "UK_ONSITE", "EU_ONSITE", "US_ONLY_CITIZENSHIP"],
    "target_role_families": ["CORE_DEVOPS_PLATFORM", "SECURITY_INFRASTRUCTURE", "AI_INFRASTRUCTURE", "CLIENT_DEPLOYMENT"],
    "excluded_role_families": ["EXECUTIVE_MANAGEMENT", "PURE_FRONTEND"]
  }
}
```
