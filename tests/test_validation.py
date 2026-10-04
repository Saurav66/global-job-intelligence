#!/usr/bin/env python3
"""
Tests for validate_job.py (schema validation, enum checks, range consistency).
"""

import json
import unittest
from pathlib import Path
from scripts.validate_job import validate_job_record


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def test_valid_fixtures(self):
        valid_file = self.fixtures_dir / "jobs_valid.jsonl"
        with open(valid_file, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                if line.strip():
                    job = json.loads(line)
                    is_valid, errors, _ = validate_job_record(job)
                    self.assertTrue(is_valid, f"Line {line_idx} failed validation: {errors}")

    def test_invalid_fixtures(self):
        invalid_file = self.fixtures_dir / "jobs_invalid.jsonl"
        with open(invalid_file, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                if line.strip():
                    job = json.loads(line)
                    is_valid, errors, _ = validate_job_record(job)
                    self.assertFalse(is_valid, f"Line {line_idx} was expected to fail validation")
                    self.assertGreater(len(errors), 0)

    def test_forbidden_applied_status(self):
        job = {
            "job_id": "sha256_applied_check",
            "first_seen_at": "2026-10-04T08:00:00Z",
            "last_seen_at": "2026-10-04T08:00:00Z",
            "company": "TestCorp",
            "job_title": "Senior DevOps Engineer",
            "role_family": "CORE_DEVOPS_PLATFORM",
            "source": "ASHBY",
            "source_url": "https://jobs.ashbyhq.com/test/1",
            "canonical_url": "https://jobs.ashbyhq.com/test/1",
            "location": "Remote",
            "remote_type": "REMOTE_GLOBAL",
            "candidate_location_eligible": True,
            "status": "APPLIED"  # FORBIDDEN IN PHASE 1
        }
        is_valid, errors, _ = validate_job_record(job)
        self.assertFalse(is_valid)
        self.assertTrue(any("APPLIED" in e for e in errors))

    def test_salary_and_experience_ranges(self):
        job = {
            "job_id": "sha256_range_check",
            "first_seen_at": "2026-10-04T08:00:00Z",
            "last_seen_at": "2026-10-04T08:00:00Z",
            "company": "TestCorp",
            "job_title": "Senior DevOps Engineer",
            "role_family": "CORE_DEVOPS_PLATFORM",
            "source": "ASHBY",
            "source_url": "https://jobs.ashbyhq.com/test/1",
            "canonical_url": "https://jobs.ashbyhq.com/test/1",
            "location": "Remote",
            "remote_type": "REMOTE_GLOBAL",
            "candidate_location_eligible": True,
            "salary_min": 180000.0,
            "salary_max": 140000.0,  # min > max
            "experience_min": 8.0,
            "experience_max": 4.0,   # min > max
        }
        is_valid, errors, _ = validate_job_record(job)
        self.assertFalse(is_valid)
        self.assertTrue(any("salary_min" in e for e in errors))
        self.assertTrue(any("experience_min" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
