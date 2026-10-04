# Scoring Model Specification

This reference defines the multi-dimensional scoring framework used to qualify, rank, and prioritize job opportunities in Phase 1.

Every evaluated job receives four distinct numerical scores (0–100):
1. **Candidate Capability Score** ($S_{\text{capability}}$)
2. **Opportunity Score** ($S_{\text{opportunity}}$)
3. **Final Score** ($S_{\text{final}}$)
4. **Resume Coverage Score** ($S_{\text{resume}}$)

> **Deterministic Implementation:** The calculations, dynamic weight re-normalization, and priority/status derivation rules in this document are codified in [`scripts/score_job.py`](file:///opt/saurav/global-job-intelligence/scripts/score_job.py).

---

## 1. Candidate Capability Score (100 Points Baseline)

The Candidate Capability Score measures how effectively the candidate's actual technical proficiencies and engineering background match the demands of the role.

### Baseline Category Breakdown

| Capability Category | Baseline Weight | Key Evaluation Focus |
| :--- | :---: | :--- |
| **Infrastructure & DevOps Core** | **20** | Architecture, reliability, distributed systems, system design |
| **Cloud Alignment** | **15** | AWS, GCP, Azure, multi-cloud networking, cloud primitives |
| **Kubernetes & Containers** | **10** | K8s architecture, Helm, Kustomize, container internals |
| **IaC & Automation** | **10** | Terraform, OpenTofu, Terragrunt, Pulumi, Ansible |
| **Experience Fit** | **10** | Seniority alignment (3–7y ideal, 7–8y stretch, 5+/6+ viable) |
| **CI/CD & Release Engineering** | **8** | GitHub Actions, GitLab CI, ArgoCD, Flux, pipelines |
| **Linux & Systems Internals** | **7** | POSIX, networking, kernel tunables, troubleshooting |
| **Security & DevSecOps** | **5** | IAM, SAST/DAST, vulnerability scanning, compliance |
| **Observability & Monitoring** | **5** | Prometheus, Grafana, OpenTelemetry, Datadog, ELK |
| **Programming & Scripting** | **5** | Python, Bash, Go, TypeScript/Node.js, APIs |
| **AI / RAG / Agentic Alignment** | **5** | Vector DBs, vLLM, Ollama, LangChain/LlamaIndex, MLOps |
| **Total Baseline** | **100** | |

### Dynamic Role-Aware Weight Redistribution
Do not mechanically penalize a job for categories that are irrelevant to its specialization. The scoring engine redistributes weights based on the primary `role_family`:

- **AI Platform / MLOps Track:**
  - AI / RAG / Agentic Alignment increases to **20–25 points**.
  - Programming (Python/Go) increases to **10–12 points**.
  - Security / Observability / Linux weights are re-scaled proportionally.
- **Cloud Security / DevSecOps Track:**
  - Security & DevSecOps increases to **25–30 points**.
  - Cloud Alignment and IaC increase to **15–20 points**.
  - AI / Agentic weights decrease to minimal or optional bonus.
- **Site Reliability Engineering (SRE) Track:**
  - Observability, Linux Internals, and Reliability Engineering increase to **25–30 points**.
  - CI/CD and Cloud infrastructure remain core (~30 points).

---

## 2. Opportunity Score (100 Points Baseline)

The Opportunity Score measures the attractiveness, viability, compensation potential, and organizational quality of the job posting.

| Opportunity Dimension | Baseline Weight | Evaluation Criteria |
| :--- | :---: | :--- |
| **Remote & Location Viability** | **25** | Unrestricted global remote (25), India-remote/EOR (25), APAC-friendly (20), restricted remote with exceptions (10), unclear (5). |
| **Compensation Quality** | **20** | Top-of-market for candidate location, clear transparency, equity upside. *(See Handling Undisclosed Compensation below)* |
| **Company Quality & Brand** | **15** | Tier-1 tech, high-growth venture-backed startup (YC, Sequoia, etc.), established profitable enterprise, tech-forward culture. |
| **Job Freshness** | **10** | Posted < 24h (10), 1–3 days (8), 4–7 days (5), > 7 days (2). |
| **Career Upside & Tech Stack** | **10** | Modern cloud-native stack, cutting-edge AI/K8s infra, high technical autonomy, learning trajectory. |
| **Seniority Level Match** | **8** | Senior / Staff IC fit (8), Mid-level (7), stretch Lead (6). |
| **Employment Quality** | **7** | Direct full-time employee (FTE), clear contractor terms, transparent benefits, equipment stipend. |
| **Timezone & Practicality** | **5** | Overlap feasibility with candidate's time zone (IST $\pm$ 4–6 hours manageable). |
| **Total** | **100** | |

### Handling Undisclosed Compensation (Zero-Fabrication Rule)
When a listing does not disclose a salary or hourly rate:
- **DO NOT assign a score of 0.**
- **DO NOT fabricate an estimated salary** without a formal benchmark model.
- Set `salary_disclosed = false` and assign `salary_min = null`, `salary_max = null`, `currency = UNKNOWN`.
- **Redistribution Method:** Re-normalize the remaining 80 points of the Opportunity Score to a 100-point scale:
  $$\text{Opportunity Score}_{\text{normalized}} = \frac{\text{Points Earned (excluding salary)}}{80} \times 100$$
- If the company is a known top-tier employer or well-funded entity, flag status as `REVIEW_SALARY` if candidate follow-up is desired.

---

## 3. Final Composite Score & Priority Tiers

The Final Score combines candidate capability and opportunity attractiveness using a 60/40 weighted formula:

$$S_{\text{final}} = \left(S_{\text{capability}} \times 0.60\right) + \left(S_{\text{opportunity}} \times 0.40\right)$$

### Priority Classifications

| Tier | Final Score Range | Action / Workflow Status |
| :---: | :---: | :--- |
| **A+** | **90 – 100** | Top-tier match. High capability, excellent compensation/remote fit. Priority shortlist (`SHORTLIST_A_PLUS`). |
| **A** | **85 – 89** | Strong match. Highly viable opportunity (`SHORTLIST_A`). |
| **B** | **75 – 84** | Good match. Solid backup or specialized domain match (`SHORTLIST_B`). |
| **C** | **65 – 74** | Moderate match. Viable if volume is low (`SHORTLIST_C`). |
| **Below C** | **< 65** | Low priority or reject (`REJECTED` / discarded). |

> **Note:** Hard blockers (incompatible location, security clearance, executive level) override any calculated score and force `status = REJECTED`.

---

## 4. Resume Coverage Score ($S_{\text{resume}}$)

The Resume Coverage Score measures how well the candidate's **existing resume document** represents the required qualifications of the job.

- **Independent Evaluation:** This score is computed separately from the Candidate Capability Score.
- **Formula Concept:**
  $$S_{\text{resume}} = \frac{\text{Directly Documented Evidence in Resume}}{\text{Total Job Requirements}} \times 100$$

### Interpretation & Status Handling:
- If $S_{\text{capability}} \ge 85$ and $S_{\text{resume}} \ge 80$: The candidate is qualified and the existing resume is ready. Assigned to `SHORTLIST_A_PLUS` or `SHORTLIST_A`.
- If $S_{\text{capability}} \ge 85$ and $S_{\text{resume}} < 75$: The candidate possesses the capability, but the existing resume has keyword/narrative representation gaps.
  - Set `status = HOLD_RESUME_UPDATE`.
  - Document the missing representations in `main_gaps` and the report's **Resume Representation Gaps** section.
  - **NEVER** conclude that the candidate lacks the skill simply because it is absent from a specific resume version.
