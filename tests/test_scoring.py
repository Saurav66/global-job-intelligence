#!/usr/bin/env python3
"""
Tests for score_job.py (scoring engine, dynamic weights, unknown handling, status derivation).
"""

import unittest
from scripts.score_job import (
    calculate_weighted_score,
    compute_final_score,
    derive_priority,
    derive_status,
    score_job_record,
    CAPABILITY_PROFILES,
    OPPORTUNITY_WEIGHTS,
)


class TestScoring(unittest.TestCase):

    def test_weighted_score_full(self):
        dims = {
            "infrastructure_devops": 90,
            "cloud": 80,
            "containers_k8s": 90,
            "iac_automation": 85,
            "experience_fit": 90,
            "cicd": 80,
            "linux_systems": 80,
            "security_devsecops": 75,
            "observability": 80,
            "scripting": 80,
            "ai_rag_alignment": 70,
        }
        res = calculate_weighted_score(dims, CAPABILITY_PROFILES["DEFAULT"])
        self.assertAlmostEqual(res["score"], 83.8, places=1)
        self.assertEqual(res["evaluated_weight"], 100.0)
        self.assertEqual(res["omitted_dimensions"], [])

    def test_unknown_weight_renormalization(self):
        # Opportunity score with undisclosed salary (compensation = None)
        opp_dims = {
            "remote_eligibility": 100,
            "compensation": None,  # Undisclosed
            "company_quality": 90,
            "job_freshness": 100,
            "career_upside": 90,
            "seniority_fit": 90,
            "employment_quality": 85,
            "timezone_practicality": 85,
        }
        res = calculate_weighted_score(opp_dims, OPPORTUNITY_WEIGHTS)
        # Evaluated weight should be 80.0 (100 - 20 for compensation)
        self.assertEqual(res["evaluated_weight"], 80.0)
        self.assertIn("compensation", res["omitted_dimensions"])
        # Score should be properly normalized out of 100
        self.assertGreater(res["score"], 80.0)

    def test_compute_final_score(self):
        # 90 * 0.60 + 85 * 0.40 = 54 + 34 = 88.0
        final = compute_final_score(90.0, 85.0)
        self.assertEqual(final, 88.0)

    def test_derive_priority(self):
        self.assertEqual(derive_priority(92.5), "A_PLUS")
        self.assertEqual(derive_priority(87.0), "A")
        self.assertEqual(derive_priority(78.0), "B")
        self.assertEqual(derive_priority(68.0), "C")
        self.assertEqual(derive_priority(62.0), "LOW")

    def test_derive_status_precedence(self):
        # 1. Hard blocker overrides high score
        self.assertEqual(
            derive_status(final_score=95.0, capability_score=95.0, resume_coverage_score=90.0, hard_blocker=True),
            "REJECTED"
        )

        # 2. Location ambiguity overrides score
        self.assertEqual(
            derive_status(final_score=92.0, capability_score=90.0, resume_coverage_score=90.0, remote_type="UNKNOWN"),
            "REVIEW_LOCATION"
        )

        # 3. High capability but low resume coverage -> HOLD_RESUME_UPDATE
        self.assertEqual(
            derive_status(final_score=89.0, capability_score=90.0, resume_coverage_score=60.0, remote_type="REMOTE_GLOBAL"),
            "HOLD_RESUME_UPDATE"
        )

        # 4. Standard score tiers
        self.assertEqual(
            derive_status(final_score=91.5, capability_score=90.0, resume_coverage_score=85.0, remote_type="REMOTE_GLOBAL"),
            "SHORTLIST_A_PLUS"
        )
        self.assertEqual(
            derive_status(final_score=86.0, capability_score=85.0, resume_coverage_score=85.0, remote_type="REMOTE_GLOBAL"),
            "SHORTLIST_A"
        )
        self.assertEqual(
            derive_status(final_score=78.0, capability_score=80.0, resume_coverage_score=80.0, remote_type="REMOTE_GLOBAL"),
            "SHORTLIST_B"
        )
        self.assertEqual(
            derive_status(final_score=68.0, capability_score=70.0, resume_coverage_score=70.0, remote_type="REMOTE_GLOBAL"),
            "SHORTLIST_C"
        )

    def test_score_job_record_ai_platform(self):
        job = {
            "company": "VectorGrid AI",
            "job_title": "AI Infrastructure Engineer",
            "role_family": "AI_INFRASTRUCTURE",
            "remote_type": "REMOTE_GLOBAL",
            "candidate_location_eligible": True,
            "capability_dimensions": {
                "ai_rag_alignment": 95,
                "infrastructure_devops": 90,
                "cloud": 90,
                "scripting": 90,
                "containers_k8s": 90,
                "experience_fit": 90,
                "iac_automation": 85,
                "cicd": 80,
            },
            "opportunity_dimensions": {
                "remote_eligibility": 100,
                "compensation": 90,
                "company_quality": 95,
                "job_freshness": 100,
                "career_upside": 95,
                "seniority_fit": 90,
                "employment_quality": 90,
                "timezone_practicality": 85,
            },
            "resume_coverage_score": 88.0,
            "hard_blocker": False,
        }
        scored = score_job_record(job)
        self.assertEqual(scored["scoring_metadata"]["capability_profile_used"], "AI_PLATFORM")
        self.assertGreaterEqual(scored["final_score"], 90.0)
        self.assertEqual(scored["priority"], "A_PLUS")
        self.assertEqual(scored["status"], "SHORTLIST_A_PLUS")


if __name__ == "__main__":
    unittest.main()
