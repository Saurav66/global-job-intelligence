# Search Strategy Reference

This document defines the target role families, prioritized search channels, query structuring rules, and discovery funnel architecture for the Phase-1 Global Job Intelligence system.

---

## 1. Target Role Families

The discovery engine monitors four primary role families and one specialized client-facing track.

### A. Core Platform, Cloud, and SRE Roles
- **DevSecOps Engineer** / **Senior DevSecOps Engineer**
- **DevOps Engineer** / **Senior DevOps Engineer**
- **Platform Engineer** / **Senior Platform Engineer** / **Cloud Platform Engineer**
- **Cloud Engineer** / **Senior Cloud Engineer** / **Cloud Infrastructure Engineer**
- **Infrastructure Engineer** / **Infrastructure Automation Engineer**
- **Site Reliability Engineer (SRE)** / **Senior Site Reliability Engineer** / **Reliability Engineer**
- **Production Engineer**

### B. Security & Infrastructure Specialization
- **Cloud Security Engineer**
- **DevOps Security Engineer**
- **Platform Security Engineer**
- **Infrastructure Security Engineer**
- **Kubernetes Engineer** / **Kubernetes Platform Engineer**
- **Cloud Automation Engineer**
- **CI/CD Engineer** / **Build & Release Engineer**

### C. AI Infrastructure & MLOps
- **AI Infrastructure Engineer**
- **AI Platform Engineer**
- **ML Platform Engineer**
- **MLOps Engineer**
- **LLM Infrastructure Engineer**
- **LLMOps Engineer**
- **AI Deployment Engineer**
- **AI Systems Engineer**

> **Relevance Multiplier:** Prioritize and highlight roles within this cluster that integrate:
> - Cloud platforms (AWS, GCP, Azure)
> - Kubernetes & container orchestration
> - Terraform / OpenTofu & Infrastructure as Code (IaC)
> - Retrieval-Augmented Generation (RAG) architectures
> - Vector databases (Pinecone, Weaviate, Qdrant, Milvus, pgvector)
> - LLM orchestration & inference serving (vLLM, Ollama, TensorRT-LLM)
> - Autonomous agentic systems and tool-calling infrastructure
> - MLOps pipelines and model deployment lifecycles

### D. Client & Deployment Solutions (Tracked Separately)
- **Forward Deployed Engineer** / **Forward Deployed DevOps Engineer**
- **Platform Solutions Engineer**
- **Infrastructure Solutions Engineer**
- **Technical Solutions Engineer**
- **Deployment Engineer**
- **Cloud Solutions Engineer**

*Note: Maintain this family as an identifiable distinct track so client-facing and solution-engineering roles can be filtered or reported independently.*

---

## 2. Search Source Hierarchy

To maximize signal and minimize noise, search sources are prioritized in the following order:

```
[ Tier 1: Official Company Careers ]
                ↓
[ Tier 2: Direct ATS Gateways (Greenhouse, Lever, Ashby, Workable, etc.) ]
                ↓
[ Tier 3: Specialist Reputable Job Platforms & Ecosystem Boards ]
                ↓
[ Tier 4: Professional Networks (LinkedIn) ]
                ↓
[ Tier 5: General Aggregators & Public Search ]
```

### Source Breakdown
1. **Tier 1: Direct Company Career Portals**
   - Official company websites (e.g., `company.com/careers`, `jobs.company.com`).
   - Primary canonical source of truth for open requisitions.
2. **Tier 2: Direct ATS Gateways**
   - Greenhouse (`boards.greenhouse.io/*`, `job-boards.greenhouse.io/*`)
   - Lever (`jobs.lever.co/*`)
   - Ashby (`jobs.ashbyhq.com/*`)
   - Workday (`*.myworkdayjobs.com/*`)
   - SmartRecruiters (`jobs.smartrecruiters.com/*`)
   - Workable (`apply.workable.com/*`)
   - iCIMS (`*.icims.com/*`)
3. **Tier 3: Specialist Remote & Ecosystem Job Boards**
   - Himalayas (`himalayas.app`)
   - Remote OK (`remoteok.com`)
   - We Work Remotely (`weworkremotely.com`)
   - Wellfound / AngelList (`wellfound.com`)
   - Y Combinator Startup Jobs (`workatastartup.com`)
   - Specialist DevOps / Cloud / Kubernetes / Security boards
4. **Tier 4: Professional Networks**
   - LinkedIn Jobs (filtered strictly for direct postings, remote eligibility, and recruiter direct posts).
5. **Tier 5: Aggregators & Search Engines**
   - Targeted Google Dorks / public web search across ATS domains.

---

## 3. Phased Discovery Funnel (Credit & Cost Optimization)

Manus agents must operate with resource efficiency. Avoid performing heavy extraction and LLM analysis on raw unvetted search results.

```
[ Step 1: Broad Discovery ]
  - Execute multi-source queries (ATS endpoints, job boards, queries).
  - Collect basic listing cards (Title, Company, URL, Snippet).
          ↓
[ Step 2: Lightweight Extraction & Normalization ]
  - Extract minimal metadata: Company, Raw Title, Raw Location, URL.
  - Generate canonical URL & deduplication fingerprint.
          ↓
[ Step 3: Deduplication ]
  - Compare against Master Job Dataset and current run cache.
  - Drop or update existing records without re-analyzing.
          ↓
[ Step 4: Hard Blocker & Eligibility Filtering ]
  - Check location eligibility (e.g., India-based remote eligibility).
  - Check experience level (filter out entry-level, VP/Director, >10y hard reqs).
  - Check citizenship / clearance restrictions.
          ↓
[ Step 5: Deep Analysis on Surviving Shortlist (Top 20–30 Jobs) ]
  - Fetch complete job description.
  - Extract detailed tech stack and requirements.
  - Compute Candidate Capability Score, Opportunity Score, Resume Coverage.
          ↓
[ Step 6: Dataset Update & Report Generation ]
  - Record structured records into master dataset.
  - Render concise Markdown scan reports.
```

---

## 4. Query Construction Guidelines

When formulating search queries across web search, search engines, and ATS indices, combine **Role Keywords**, **Core Technologies**, and **Location / Remote Modifiers**.

### Representative Query Patterns

- **DevSecOps / Security:**
  `("DevSecOps" OR "Cloud Security Engineer" OR "Platform Security") ("Kubernetes" OR "Terraform" OR "AWS") ("Remote" OR "Anywhere" OR "India")`
- **Platform / Infrastructure:**
  `("Platform Engineer" OR "Senior Platform Engineer" OR "Cloud Infrastructure Engineer") ("Kubernetes" OR "IaC" OR "CI/CD") ("Remote" OR "Worldwide")`
- **AI Infrastructure / MLOps:**
  `("AI Infrastructure" OR "AI Platform Engineer" OR "MLOps" OR "LLMOps") ("Kubernetes" OR "Terraform" OR "vLLM" OR "RAG") ("Remote")`
- **Direct ATS Dorks:**
  `site:boards.greenhouse.io ("Platform Engineer" OR "DevOps" OR "DevSecOps") ("Remote" OR "India" OR "Global") -intitle:intern`
  `site:jobs.ashbyhq.com ("AI Infrastructure" OR "Platform Engineer" OR "SRE") "Remote"`
  `site:jobs.lever.co ("DevOps Engineer" OR "Cloud Engineer") ("Worldwide" OR "Remote")`

---

## 5. Canonical URL Identification

When discovering a role through an aggregator or professional network:
1. Attempt to trace the link back to the direct ATS or company careers page.
2. Store the direct ATS/Careers URL as `canonical_url`.
3. Store the discovery platform link as `source_url`.
4. If the direct ATS link cannot be resolved, set `canonical_url = source_url`.
