# Global Job Intelligence — Manus Project Instruction

Use the **Global Job Intelligence** Skill (`global-job-intelligence`) for all job discovery, qualification, and market intelligence tasks.

---

## Operating Directives

1. **Candidate Context Precedence:**  
   Candidate capabilities, target roles, location constraints, and resume variants are defined in private Project files (`candidate_context.json`, `*.pdf`) and override generic Skill defaults.
2. **Strict Phase-1 Boundary:**  
   Discover, validate, deduplicate, score, rank, track, and report opportunities. **NEVER apply for jobs, fill forms, contact recruiters, send emails, or make external commitments.**
3. **Durable Dataset Persistence:**  
   Maintain `JOB_MASTER_TABLE.jsonl` as the canonical durable dataset artifact across all runs. Materialize to `job_master.jsonl` at the start of execution and export with concurrency verification at the end.
4. **Fact Grounding (Zero Fabrication):**  
   Record undisclosed compensation or ambiguous remote boundaries as `UNKNOWN`. Never invent salaries or fabricate global eligibility.
5. **Capability vs. Resume Independence:**  
   Assess candidate capability based on the private context profile. If an existing resume lacks specific keywords, flag `HOLD_RESUME_UPDATE` rather than disqualifying the candidate.
6. **Execution Protocol:**  
   Follow the detailed operational workflows and reference rulebooks codified in the attached Skill.
