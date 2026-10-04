#!/usr/bin/env python3
"""
Tests for preflight.py (pre-flight readiness checks, candidate and dataset verification).
"""

import unittest
from pathlib import Path
from scripts.preflight import run_preflight


class TestPreflight(unittest.TestCase):

    def setUp(self):
        self.fixtures_dir = Path(__file__).parent / "fixtures" / "integration"
        self.root_fixtures_dir = Path(__file__).parent / "fixtures"

    def test_preflight_default(self):
        res = run_preflight()
        self.assertTrue(res["ready"])
        self.assertEqual(res["skill_version"], "0.3.1")
        self.assertEqual(len(res["errors"]), 0)

    def test_preflight_with_valid_candidate_and_dataset(self):
        cand_path = str(self.fixtures_dir / "candidate_context_standard.json")
        ds_path = str(self.fixtures_dir / "empty_job_master.jsonl")

        res = run_preflight(candidate_path=cand_path, dataset_path=ds_path)
        self.assertTrue(res["ready"])
        self.assertIn("VALID", res["candidate_context"]["status"])
        self.assertEqual(res["candidate_context"]["sufficiency_level"], "STANDARD")
        self.assertIn("VALID", res["dataset"]["status"])

    def test_preflight_with_invalid_candidate(self):
        non_existent = str(self.fixtures_dir / "non_existent.json")
        res = run_preflight(candidate_path=non_existent)
        self.assertFalse(res["ready"])
        self.assertEqual(res["candidate_context"]["status"], "FILE_NOT_FOUND")
        self.assertGreater(len(res["errors"]), 0)

    def test_preflight_with_invalid_dataset(self):
        invalid_ds = str(self.root_fixtures_dir / "jobs_invalid.jsonl")
        res = run_preflight(dataset_path=invalid_ds)
        self.assertFalse(res["ready"])
        self.assertIn("INVALID", res["dataset"]["status"])
        self.assertGreater(len(res["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
