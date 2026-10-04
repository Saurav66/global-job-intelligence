#!/usr/bin/env python3
"""
Tests for deduplicate_jobs.py (duplicate signals, similarity matching, and safe merging).
"""

import unittest
from scripts.deduplicate_jobs import (
    check_duplicate_signal,
    compute_title_similarity,
    merge_job_records,
    deduplicate_batch,
    get_source_tier,
)


class TestDeduplication(unittest.TestCase):

    def test_title_similarity(self):
        # Exact match after normalization
        sim1 = compute_title_similarity(
            "Senior DevOps Engineer",
            "Senior DevOps Engineer - Remote"
        )
        self.assertEqual(sim1, 1.0)

        # High similarity
        sim2 = compute_title_similarity(
            "Senior Cloud & DevOps Engineer",
            "Senior DevOps Engineer"
        )
        self.assertGreater(sim2, 0.80)

        # Low similarity / distinct roles
        sim3 = compute_title_similarity(
            "Senior DevOps Engineer",
            "Senior Data Platform Engineer"
        )
        self.assertLess(sim3, 0.75)

    def test_ats_requisition_duplicate_signal(self):
        job_master = {
            "job_id": "sha256_northstar_gh",
            "company": "Northstar Systems Inc.",
            "job_title": "Senior DevOps Engineer",
            "source": "GREENHOUSE",
            "canonical_url": "https://boards.greenhouse.io/northstar/jobs/554433",
            "location": "Remote - Worldwide"
        }
        job_incoming = {
            "company": "Northstar Systems",
            "job_title": "Senior DevOps Engineer - Remote (Worldwide)",
            "source": "LINKEDIN",
            "source_url": "https://www.linkedin.com/jobs/view/99887766/?ref=aggregator",
            "canonical_url": "https://boards.greenhouse.io/northstar/jobs/554433?gh_src=linkedin",
            "location": "Remote - Worldwide"
        }
        signal = check_duplicate_signal(job_incoming, job_master)
        self.assertIsNotNone(signal)
        self.assertTrue(signal["is_duplicate"])
        self.assertEqual(signal["confidence"], "EXACT")
        self.assertEqual(signal["signal"], "ATS_REQUISITION_ID")

    def test_merge_job_records(self):
        existing = {
            "job_id": "sha256_record_01",
            "first_seen_at": "2026-10-01T10:00:00Z",
            "last_seen_at": "2026-10-01T10:00:00Z",
            "company": "CloudForge Labs",
            "job_title": "Senior Platform Engineer",
            "source": "AGGREGATOR",
            "source_url": "https://aggregator.example.com/job/1",
            "canonical_url": "https://aggregator.example.com/job/1",
            "salary_disclosed": False,
            "salary_min": None,
            "required_skills": ["Kubernetes", "AWS"]
        }
        incoming = {
            "first_seen_at": "2026-10-04T08:00:00Z",
            "last_seen_at": "2026-10-04T08:00:00Z",
            "company": "CloudForge Labs",
            "job_title": "Senior Platform Engineer",
            "source": "LEVER",
            "source_url": "https://jobs.lever.co/cloudforge/123",
            "canonical_url": "https://jobs.lever.co/cloudforge/123",
            "salary_disclosed": True,
            "salary_min": 145000.0,
            "salary_max": 175000.0,
            "currency": "USD",
            "required_skills": ["Kubernetes", "Terraform", "ArgoCD"]
        }

        merged = merge_job_records(existing, incoming)

        # 1. Earliest first_seen_at preserved
        self.assertEqual(merged["first_seen_at"], "2026-10-01T10:00:00Z")
        # 2. Latest last_seen_at updated
        self.assertEqual(merged["last_seen_at"], "2026-10-04T08:00:00Z")
        # 3. Authoritative canonical URL promoted (Lever > Aggregator)
        self.assertEqual(merged["canonical_url"], "https://jobs.lever.co/cloudforge/123")
        self.assertEqual(merged["source"], "LEVER")
        # 4. Salary updated from new disclosure
        self.assertTrue(merged["salary_disclosed"])
        self.assertEqual(merged["salary_min"], 145000.0)
        # 5. Skills unioned without duplicates
        self.assertEqual(sorted(merged["required_skills"]), ["AWS", "ArgoCD", "Kubernetes", "Terraform"])

    def test_deduplicate_batch(self):
        master = [
            {
                "job_id": "sha256_northstar_01",
                "first_seen_at": "2026-10-01T10:00:00Z",
                "last_seen_at": "2026-10-01T10:00:00Z",
                "company": "Northstar Systems",
                "job_title": "Senior DevSecOps Engineer",
                "canonical_url": "https://jobs.ashbyhq.com/northstar/101",
                "location": "Remote - Worldwide",
                "required_skills": ["AWS", "Kubernetes"]
            }
        ]
        incoming = [
            # Duplicate item
            {
                "company": "Northstar Systems Inc.",
                "job_title": "Senior DevSecOps Engineer - Remote",
                "canonical_url": "https://jobs.ashbyhq.com/northstar/101?utm_source=feed",
                "location": "Remote - Worldwide",
                "first_seen_at": "2026-10-04T08:00:00Z",
                "last_seen_at": "2026-10-04T08:00:00Z",
                "required_skills": ["AWS", "Terraform"]
            },
            # Net-new item
            {
                "company": "VectorGrid AI",
                "job_title": "AI Platform Engineer",
                "canonical_url": "https://boards.greenhouse.io/vectorgrid/jobs/202",
                "location": "Remote - India",
                "first_seen_at": "2026-10-04T08:00:00Z",
                "last_seen_at": "2026-10-04T08:00:00Z",
                "required_skills": ["vLLM", "Ray"]
            }
        ]

        unique_new, updated_master, duplicates = deduplicate_batch(incoming, master)

        self.assertEqual(len(unique_new), 1)
        self.assertEqual(unique_new[0]["company"], "VectorGrid AI")
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(updated_master), 1)
        # Check that master record was updated
        self.assertEqual(updated_master[0]["last_seen_at"], "2026-10-04T08:00:00Z")
        self.assertIn("Terraform", updated_master[0]["required_skills"])


if __name__ == "__main__":
    unittest.main()
