#!/usr/bin/env python3
"""
Tests for runtime_probe.py (capability probing, filesystem checks, and version inspection).
"""

import unittest
from pathlib import Path
from scripts.runtime_probe import probe_runtime, SKILL_VERSION


class TestRuntimeProbe(unittest.TestCase):

    def test_probe_structure_and_types(self):
        res = probe_runtime()
        self.assertTrue(res["python"])
        self.assertTrue(res["filesystem_read"])
        self.assertTrue(res["filesystem_write"])
        self.assertTrue(res["atomic_replace"])
        self.assertTrue(res["skill_scripts_accessible"])
        self.assertEqual(len(res["missing_scripts"]), 0)
        self.assertEqual(res["skill_version"], "0.3.1")
        self.assertIn("timestamp_utc", res)
        self.assertIn("cwd", res)


if __name__ == "__main__":
    unittest.main()
