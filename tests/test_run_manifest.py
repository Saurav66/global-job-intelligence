#!/usr/bin/env python3
"""
Tests for run_manifest.py (manifest generation, run ID format, and execution metadata).
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.run_manifest import (
    generate_run_id,
    create_run_manifest,
    save_manifest,
    SKILL_VERSION,
)


class TestRunManifest(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.test_dir, "RUN_MANIFEST.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_id_generation(self):
        run_id_m = generate_run_id("MORNING")
        self.assertIn("-MORNING-", run_id_m)
        self.assertTrue(run_id_m.startswith("20"))

        run_id_e = generate_run_id("EVENING")
        self.assertIn("-EVENING-", run_id_e)

        # Uniqueness
        self.assertNotEqual(generate_run_id("MORNING"), generate_run_id("MORNING"))

    def test_create_and_save_manifest(self):
        manifest = create_run_manifest(
            run_mode="MORNING",
            run_status="SUCCESS",
            fallback_used="DETERMINISTIC",
            candidate_context_level="STANDARD",
            input_record_count=10,
            output_record_count=15,
            input_sha256="abc123hash",
            output_sha256="def456hash",
            raw_found=40,
            unique_new=5,
            duplicates=10,
            hard_rejected=25,
            analyzed=5,
            a_plus_count=2,
            a_count=3,
            b_count=0,
            c_count=0,
            resume_holds=1,
            warnings=["Test warning"]
        )

        self.assertEqual(manifest["skill_version"], SKILL_VERSION)
        self.assertEqual(manifest["run_mode"], "MORNING")
        self.assertEqual(manifest["run_status"], "SUCCESS")
        self.assertEqual(manifest["execution"]["fallback_used"], "DETERMINISTIC")
        self.assertEqual(manifest["dataset"]["input_record_count"], 10)
        self.assertEqual(manifest["dataset"]["output_record_count"], 15)
        self.assertEqual(manifest["priorities"]["A_plus"], 2)
        self.assertEqual(manifest["resume_holds"], 1)

        # Save to disk
        save_manifest(manifest, self.manifest_path)
        self.assertTrue(os.path.exists(self.manifest_path))

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            self.assertEqual(loaded["run_id"], manifest["run_id"])
            self.assertEqual(loaded["skill_version"], "0.3.1")

    def test_integration_test_run_mode(self):
        manifest = create_run_manifest(run_mode="INTEGRATION_TEST", run_status="SUCCESS")
        self.assertEqual(manifest["run_mode"], "INTEGRATION_TEST")
        self.assertEqual(manifest["skill_version"], "0.3.1")


if __name__ == "__main__":
    unittest.main()
