#!/usr/bin/env python3
"""
Tests for artifact_sync.py (artifact import, export, checksum verification, and concurrency protection).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.artifact_sync import (
    calculate_checksum,
    import_artifact,
    export_artifact,
    count_and_validate_records,
)


class TestArtifactSync(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.durable_path = os.path.join(self.test_dir, "JOB_MASTER_TABLE.jsonl")
        self.runtime_path = os.path.join(self.test_dir, "job_master.jsonl")

        self.sample_valid_job = {
            "job_id": "sha256_sync_test_01",
            "first_seen_at": "2026-10-04T08:00:00Z",
            "last_seen_at": "2026-10-04T08:00:00Z",
            "company": "Northstar Systems",
            "job_title": "Senior DevOps Engineer",
            "role_family": "CORE_DEVOPS_PLATFORM",
            "source": "ASHBY",
            "source_url": "https://jobs.ashbyhq.com/northstar/1",
            "canonical_url": "https://jobs.ashbyhq.com/northstar/1",
            "location": "Remote - Worldwide",
            "remote_type": "REMOTE_GLOBAL",
            "candidate_location_eligible": True,
            "status": "SHORTLIST_A_PLUS",
            "priority": "A_PLUS"
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_checksum_calculation(self):
        with open(self.durable_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_valid_job) + "\n")

        cs = calculate_checksum(self.durable_path)
        self.assertIsNotNone(cs)
        self.assertEqual(len(cs), 64)

        # Non-existent file
        self.assertIsNone(calculate_checksum(os.path.join(self.test_dir, "nonexistent.jsonl")))

    def test_import_artifact_success(self):
        with open(self.durable_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_valid_job) + "\n")

        res = import_artifact(self.durable_path, self.runtime_path)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["record_count"], 1)
        self.assertTrue(os.path.exists(self.runtime_path))
        self.assertEqual(res["sha256"], calculate_checksum(self.runtime_path))

    def test_import_artifact_validation_failure(self):
        invalid_job = {"job_id": "broken_01"}  # Missing required fields
        with open(self.durable_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(invalid_job) + "\n")

        res = import_artifact(self.durable_path, self.runtime_path)
        self.assertEqual(res["status"], "VALIDATION_FAILED")
        self.assertFalse(res["validated"])
        self.assertFalse(os.path.exists(self.runtime_path))  # Destination must NOT be created/overwritten

    def test_export_artifact_success(self):
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_valid_job) + "\n")

        res = export_artifact(self.runtime_path, self.durable_path)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["record_count"], 1)
        self.assertTrue(os.path.exists(self.durable_path))
        self.assertEqual(res["sha256"], calculate_checksum(self.durable_path))

    def test_export_artifact_concurrency_conflict(self):
        # 1. Initialize durable artifact with initial version
        with open(self.durable_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_valid_job) + "\n")

        initial_hash = calculate_checksum(self.durable_path)

        # 2. Simulate another task modifying the durable artifact in the background
        modified_job = dict(self.sample_valid_job)
        modified_job["last_seen_at"] = "2026-10-04T12:00:00Z"
        with open(self.durable_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(modified_job) + "\n")

        # 3. Create local runtime version
        with open(self.runtime_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.sample_valid_job) + "\n")

        # 4. Attempt export passing the original initial_hash
        res = export_artifact(
            runtime_path=self.runtime_path,
            destination_path=self.durable_path,
            expected_input_hash=initial_hash
        )

        self.assertEqual(res["status"], "DATASET_CONFLICT")
        self.assertFalse(res["validated"])
        # The background modification must NOT have been overwritten
        with open(self.durable_path, "r", encoding="utf-8") as f:
            content = json.loads(f.read().strip())
            self.assertEqual(content["last_seen_at"], "2026-10-04T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
