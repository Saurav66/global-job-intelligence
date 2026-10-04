# Weekly Intelligence Template — 7-Day Market Analytics

This template defines the prompt and execution instructions for the weekly intelligence digest compiled from the accumulated master job records.

---

## Task Objective
Analyze the accumulated job discovery records from the preceding 7 days, generate statistical market insights on tech stack demand, salary distributions, and remote geography, identify systemic resume representation gaps, and compile a ranked digest of the best still-active opportunities.

> **Grounding Rule:** Do NOT invent or hallucinate market statistics. All metrics, percentages, and salary figures MUST be computed strictly from the active dataset.

---

## Execution Protocol

### Step 1: Dataset Ingestion & Filtering
1. Query the master dataset for all records where `first_seen_at >= now() - 7 days`.
2. Filter for active, non-expired, and non-rejected records to evaluate market demand.

### Step 2: Statistical Aggregation
Compute the following metrics across the 7-day dataset:
1. **Pipeline Funnel & Volume:**
   - Total raw discoveries vs. unique eligible jobs.
   - Tier distribution: $N(\text{A+}), N(\text{A}), N(\text{B}), N(\text{C}), N(\text{Hold Update})$.
2. **Role Family Distribution:**
   - Core DevOps/Platform vs. Security/Infra vs. AI Infrastructure vs. Solutions.
3. **Infrastructure & Cloud Market Demand:**
   - Cloud Platform share: AWS vs. GCP vs. Azure (percentage of listings requiring each).
   - Core Tool demand: Kubernetes, Terraform/OpenTofu, Docker, Helm, ArgoCD/Flux.
   - Programming Languages: Python vs. Go vs. Bash/Shell vs. TypeScript.
4. **AI Infrastructure & Emerging Tech Demand:**
   - Prevalence of LLMOps / MLOps requirements.
   - Demand for RAG pipelines, Vector Databases (Pinecone, Qdrant, Weaviate, pgvector), vLLM/Ollama, and Agentic frameworks.
5. **Geographic & Compensation Distribution:**
   - Breakdown of `REMOTE_GLOBAL` vs. `REMOTE_INDIA` vs. `REMOTE_APAC`.
   - Median and range of disclosed base salaries across A/A+ tier roles.

---

## 3. Weekly Intelligence Report Structure

```markdown
# Global Job Intelligence — Weekly Market Digest
**Period Covered:** YYYY-MM-DD to YYYY-MM-DD  
**Total Records Analyzed:** XXX  
**Active Qualified Opportunities:** XXX

---

## 1. 7-Day Pipeline Overview

| Metric | Count | % of Qualified Volume |
| :--- | :---: | :---: |
| **Total Opportunities Discovered** | XXX | 100% |
| **Eligible Surviving Jobs** | XXX | XX% |
| **Tier A+ (Score 90–100)** | XX | XX% |
| **Tier A (Score 85–89)** | XX | XX% |
| **Tier B (Score 75–84)** | XX | XX% |
| **Tier C (Score 65–74)** | XX | XX% |
| **Hold for Resume Update** | XX | XX% |

---

## 2. Technology & Tooling Demand Trends

### Cloud & Container Infrastructure
- **AWS:** XX% of listings | **GCP:** XX% | **Azure:** XX%
- **Kubernetes:** XX% of qualified roles
- **Terraform / OpenTofu:** XX%
- **ArgoCD / GitOps:** XX%

### Systems & Programming
- **Python:** XX% | **Go (Golang):** XX% | **Bash:** XX%

### AI Infrastructure & MLOps Signals
- **RAG / Vector Databases:** Mentioned in XX% of AI Platform / DevOps roles.
- **Model Serving (vLLM, TensorRT, Triton):** Mentioned in XX% of AI Infra roles.
- **Agentic Frameworks / Orchestration:** XX listings.

---

## 3. Top Hiring Companies This Week
1. **[Company Name]** — X open roles (AI Platform, DevSecOps)
2. **[Company Name]** — X open roles (SRE, Platform)

---

## 4. Candidate Capability vs. Resume Representation Analysis

### Systemic Resume Gaps (High Market Demand, Low Resume Representation)
- Identify technologies frequently required by Tier A/A+ roles that are omitted from the active candidate resume artifact.
- Formulate concrete bullet-point adjustments to increase $S_{\text{resume}}$ for upcoming cycles.

---

## 5. Top 5 Still-Active Opportunities of the Week

| Score | Company | Role Title | Advertised Compensation | Canonical URL |
| :---: | :--- | :--- | :--- | :---: |
| **94** | ... | Senior DevSecOps Engineer | $150k - $180k USD | [Link](https://...) |
| **91** | ... | AI Platform Engineer | $160k - $190k USD | [Link](https://...) |
```

---

## Phase Boundary Reminder
> **CRITICAL:** Do NOT attempt to apply, fill out forms, contact recruiters, or auto-submit applications. Conclude execution after report delivery and dataset persistence.
