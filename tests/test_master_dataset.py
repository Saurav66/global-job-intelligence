#!/usr/bin/env python3
"""
Tests for master_dataset.py (JSONL dataset operations, atomic persistence, summary counts).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.master_dataset import (
    init_dataset,
    load_dataset,
    save_dataset_atomic,
    upsert_records,
    summarize_dataset,
    mark_expired,
)


class TestMasterDataset(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dataset_path = os.path.join(self.test_dir, "test_job_master.jsonl")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init_and_load_dataset(self):
        # Initializing new dataset
        created = init_dataset(self.dataset_path)
        self.assertTrue(created)
        self.assertTrue(os.path.exists(self.dataset_path))

        # Re-init should return False (already exists)
        self.assertFalse(init_dataset(self.dataset_path))

        # Empty load
        records = load_dataset(self.dataset_path)
        self.assertEqual(len(records), 0)

    def test_atomic_save_and_load(self):
        sample_jobs = [
            {
                "job_id": "job_01",
                "company": "Northstar Systems",
                "job_title": "Senior DevOps Engineer",
                "priority": "A_PLUS",
                "status": "SHORTLIST_A_PLUS",
                "salary_disclosed": True
            },
            {
                "job_id": "job_02",
                "company": "VectorGrid AI",
                "job_title": "AI Platform Engineer",
                "priority": "A",
                "status": "SHORTLIST_A",
                "salary_disclosed": False
            }
        ]
        save_dataset_atomic(sample_jobs, self.dataset_path)

        loaded = load_dataset(self.dataset_path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["job_id"], "job_01")
        self.assertEqual(loaded[1]["job_id"], "job_02")

    def test_upsert_and_merge(self):
        init_dataset(self.dataset_path)

        job1 = {
            "job_id": "job_101",
            "company": "CloudForge Labs",
            "job_title": "Platform Engineer",
            "source": "AGGREGATOR",
            "canonical_url": "https://example.com/job/101",
            "required_skills": ["AWS", "Kubernetes"],
            "first_seen_at": "2026-10-01T00:00:00Z",
            "last_seen_at": "2026-10-01T00:00:00Z"
        }
        res1 = upsert_records([job1], self.dataset_path)
        self.assertEqual(res1["inserted"], 1)
        self.assertEqual(res1["updated"], 0)

        # Incoming update for job1 with additional skill and higher tier source
        job1_update = {
            "job_id": "job_101",
            "company": "CloudForge Labs",
            "job_title": "Platform Engineer",
            "source": "LEVER",
            "canonical_url": "https://jobs.lever.co/cloudforge/101",
            "required_skills": ["AWS", "Terraform"],
            "first_seen_at": "2026-10-04T00:00:00Z",
            "last_seen_at": "2026-10-04T00:00:00Z"
        }
        job2_new = {
            "job_id": "job_102",
            "company": "PulseStream",
            "job_title": "SRE",
            "source": "ASHBY",
            "canonical_url": "https://jobs.ashbyhq.com/pulsestream/102",
            "first_seen_at": "2026-10-04T00:00:00Z",
            "last_seen_at": "2026-10-04T00:00:00Z"
        }

        res2 = upsert_records([job1_update, job2_new], self.dataset_path)
        self.assertEqual(res2["inserted"], 1)
        self.assertEqual(res2["updated"], 1)
        self.assertEqual(res2["total_records"], 2)

        loaded = load_dataset(self.dataset_path)
        merged_job1 = [r for r in loaded if r["job_id"] == "job_101"][0]
        self.assertEqual(merged_job1["first_seen_at"], "2026-10-01T00:00:00Z")
        self.assertEqual(merged_job1["last_seen_at"], "2026-10-04T00:00:00Z")
        self.assertEqual(merged_job1["canonical_url"], "https://jobs.lever.co/cloudforge/101")
        self.assertIn("Terraform", merged_job1["required_skills"])
        self.assertIn("Kubernetes", merged_job1["required_skills"])

    def test_mark_expired_and_summary(self):
        sample_jobs = [
            {
                "job_id": "job_01",
                "priority": "A_PLUS",
                "status": "SHORTLIST_A_PLUS",
                "role_family": "SECURITY_INFRASTRUCTURE",
                "remote_type": "REMOTE_GLOBAL",
                "salary_disclosed": True
            },
            {
                "job_id": "job_02",
                "priority": "A",
                "status": "SHORTLIST_A",
                "role_family": "AI_INFRASTRUCTURE",
                "remote_type": "REMOTE_INDIA",
                "salary_disclosed": False
            }
        ]
        save_dataset_atomic(sample_jobs, self.dataset_path)

        # Mark job_02 expired
        ok = mark_expired("job_02", self.dataset_path)
        self.assertTrue(ok)

        summary = summarize_dataset(self.dataset_path)
        self.assertEqual(summary["total_jobs"], 2)
        self.assertEqual(summary["by_status"]["SHORTLIST_A_PLUS"], 1)
        self.assertEqual(summary["by_status"]["EXPIRED"], 1)
        self.assertEqual(summary["salary_disclosed_count"], 1)
        self.assertEqual(summary["salary_undisclosed_count"], 1)


if __name__ == "__main__":
    unittest.main()
