#!/usr/bin/env python3
"""
Tests for context_validator.py (candidate context schema and sufficiency level checks).
"""

import unittest
from scripts.context_validator import validate_candidate_context


class TestContextValidator(unittest.TestCase):

    def test_minimum_valid_context(self):
        ctx = {
            "candidate": {"experience_years": 4.5},
            "location": {"country": "India"},
            "capabilities": {
                "primary_domains": ["DevOps", "Platform Engineering"]
            },
            "role_preferences": {
                "primary": ["Senior DevOps Engineer"]
            }
        }
        res = validate_candidate_context(ctx)
        self.assertTrue(res["valid"])
        self.assertEqual(res["sufficiency_level"], "MINIMUM")
        self.assertEqual(len(res["errors"]), 0)

    def test_standard_valid_context(self):
        ctx = {
            "candidate": {"experience_years": 4.5},
            "location": {"country": "India", "timezone": "Asia/Kolkata"},
            "employment_preferences": {
                "remote_preference": "REMOTE_ONLY"
            },
            "capabilities": {
                "primary_domains": ["DevSecOps"],
                "cloud": ["AWS"],
                "containers": ["Kubernetes"],
                "iac": ["Terraform"]
            },
            "resume_variants": [
                {"id": "devsecops_senior", "label": "Senior DevSecOps"}
            ],
            "role_preferences": {
                "primary": ["Senior DevSecOps Engineer"]
            }
        }
        res = validate_candidate_context(ctx)
        self.assertTrue(res["valid"])
        self.assertEqual(res["sufficiency_level"], "STANDARD")

    def test_enriched_valid_context(self):
        ctx = {
            "candidate": {"experience_years": 5.0},
            "location": {"country": "India", "timezone": "Asia/Kolkata"},
            "employment_preferences": {
                "remote_preference": "REMOTE_ONLY"
            },
            "compensation": {
                "minimum": 130000.0,
                "target": 160000.0,
                "currency": "USD"
            },
            "capabilities": {
                "primary_domains": ["AI Infrastructure"],
                "cloud": ["AWS", "GCP"],
                "containers": ["Kubernetes"],
                "iac": ["Terraform"]
            },
            "capability_confidence": {
                "AWS": "CORE",
                "Kubernetes": "CORE",
                "Python": "STRONG"
            },
            "resume_variants": [
                {"id": "ai_infra", "label": "AI Infra"}
            ],
            "role_preferences": {
                "primary": ["AI Platform Engineer"]
            },
            "search_preferences": {
                "target_geographies": ["REMOTE_GLOBAL"]
            }
        }
        res = validate_candidate_context(ctx)
        self.assertTrue(res["valid"])
        self.assertEqual(res["sufficiency_level"], "ENRICHED")

    def test_missing_required_fields(self):
        ctx = {
            "candidate": {},  # missing experience_years
            "location": {},   # missing country
            "capabilities": {},
            "role_preferences": {}
        }
        res = validate_candidate_context(ctx)
        self.assertFalse(res["valid"])
        self.assertEqual(res["sufficiency_level"], "INSUFFICIENT")
        self.assertGreater(len(res["errors"]), 0)

    def test_invalid_confidence_level(self):
        ctx = {
            "candidate": {"experience_years": 4.5},
            "location": {"country": "India"},
            "capabilities": {"primary_domains": ["DevOps"]},
            "capability_confidence": {
                "AWS": "SUPER_EXPERT"  # Invalid enum
            },
            "role_preferences": {"primary": ["Senior DevOps Engineer"]}
        }
        res = validate_candidate_context(ctx)
        self.assertFalse(res["valid"])
        self.assertTrue(any("SUPER_EXPERT" in e for e in res["errors"]))

    def test_duplicate_resume_ids(self):
        ctx = {
            "candidate": {"experience_years": 4.5},
            "location": {"country": "India"},
            "capabilities": {"primary_domains": ["DevOps"]},
            "resume_variants": [
                {"id": "resume_track_a", "label": "Track A"},
                {"id": "resume_track_a", "label": "Track A Duplicate"}
            ],
            "role_preferences": {"primary": ["Senior DevOps Engineer"]}
        }
        res = validate_candidate_context(ctx)
        self.assertFalse(res["valid"])
        self.assertTrue(any("Duplicate resume variant id" in e for e in res["errors"]))

    def test_invalid_compensation_range(self):
        ctx = {
            "candidate": {"experience_years": 4.5},
            "location": {"country": "India"},
            "compensation": {
                "minimum": 180000.0,
                "target": 140000.0  # min > target
            },
            "capabilities": {"primary_domains": ["DevOps"]},
            "role_preferences": {"primary": ["Senior DevOps Engineer"]}
        }
        res = validate_candidate_context(ctx)
        self.assertFalse(res["valid"])
        self.assertTrue(any("minimum" in e and "target" in e for e in res["errors"]))


if __name__ == "__main__":
    unittest.main()
