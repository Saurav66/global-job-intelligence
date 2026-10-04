#!/usr/bin/env python3
"""
Tests for job_utils.py (normalization, URL cleaning, and fingerprinting).
"""

import unittest
from scripts.job_utils import (
    normalize_text,
    normalize_company,
    normalize_title,
    normalize_location,
    normalize_url,
    extract_ats_requisition_id,
    generate_job_fingerprint,
)


class TestJobUtils(unittest.TestCase):

    def test_normalize_text(self):
        self.assertEqual(normalize_text("  Senior   DevOps   Engineer  "), "Senior DevOps Engineer")
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "")

    def test_normalize_company(self):
        self.assertEqual(normalize_company("Northstar Systems Inc."), "northstar")
        self.assertEqual(normalize_company("ACME Corp, LLC"), "acme")
        self.assertEqual(normalize_company("CloudForge Technologies Ltd."), "cloudforge")
        self.assertEqual(normalize_company("Scale AI"), "scale ai")

    def test_normalize_title(self):
        # Cleaning noise while preserving role identity
        self.assertEqual(
            normalize_title("Senior DevOps Engineer - Remote (Worldwide)"),
            "senior devops engineer"
        )
        self.assertEqual(
            normalize_title("Sr. Platform Eng. [Hybrid]"),
            "senior platform engineer"
        )
        self.assertEqual(
            normalize_title("AI Infrastructure Engineer"),
            "ai infrastructure engineer"
        )
        # Ensure distinct titles do NOT collide
        self.assertNotEqual(
            normalize_title("Senior DevOps Engineer"),
            normalize_title("Senior Platform Engineer")
        )

    def test_normalize_location(self):
        self.assertEqual(normalize_location("Remote - Worldwide"), "remote-global")
        self.assertEqual(normalize_location("Anywhere"), "remote-global")
        self.assertEqual(normalize_location("Bengaluru, India (Remote)"), "india-remote")
        self.assertEqual(normalize_location("United States - Remote"), "us-remote")
        self.assertEqual(normalize_location("London, UK (Hybrid)"), "emea-regional")
        self.assertEqual(normalize_location(""), "unknown")

    def test_normalize_url(self):
        raw_url = "https://boards.greenhouse.io/northstar/jobs/12345?utm_source=linkedin&utm_medium=feed&ref=123#apply"
        expected = "https://boards.greenhouse.io/northstar/jobs/12345"
        self.assertEqual(normalize_url(raw_url), expected)

        # Host casing and default port normalization
        raw_port_url = "HTTPS://Jobs.AshbyHQ.com:443/company/abc-123/"
        self.assertEqual(normalize_url(raw_port_url), "https://jobs.ashbyhq.com/company/abc-123")

    def test_extract_ats_requisition_id(self):
        gh_url = "https://boards.greenhouse.io/northstar/jobs/554433"
        self.assertEqual(extract_ats_requisition_id(gh_url), "gh:northstar:554433")

        ashby_url = "https://jobs.ashbyhq.com/vectorgrid/d3b07384-d113-4607-b2e0"
        self.assertEqual(extract_ats_requisition_id(ashby_url), "ashby:vectorgrid:d3b07384-d113-4607-b2e0")

        lever_url = "https://jobs.lever.co/cloudforge/e5f6g7h8"
        self.assertEqual(extract_ats_requisition_id(lever_url), "lever:cloudforge:e5f6g7h8")

        generic_url = "https://example.com/careers/devops"
        self.assertIsNone(extract_ats_requisition_id(generic_url))

    def test_fingerprint_stability_and_collision(self):
        job1 = {
            "company": "Northstar Systems Inc.",
            "job_title": "Senior DevOps Engineer",
            "location": "Remote - Worldwide",
            "canonical_url": "https://boards.greenhouse.io/northstar/jobs/554433?utm_source=feed"
        }
        job2 = {
            "company": "Northstar Systems",
            "job_title": "Senior DevOps Engineer - Remote",
            "location": "Worldwide",
            "canonical_url": "https://boards.greenhouse.io/northstar/jobs/554433"
        }
        # ATS Requisition ID ensures identical fingerprint
        self.assertEqual(generate_job_fingerprint(job1), generate_job_fingerprint(job2))

        # Different job at same company must NOT collide
        job3 = {
            "company": "Northstar Systems Inc.",
            "job_title": "AI Infrastructure Engineer",
            "location": "Remote - Worldwide",
            "canonical_url": "https://boards.greenhouse.io/northstar/jobs/998811"
        }
        self.assertNotEqual(generate_job_fingerprint(job1), generate_job_fingerprint(job3))


if __name__ == "__main__":
    unittest.main()
