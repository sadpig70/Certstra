#!/usr/bin/env python3
"""Certstra kernel + packs tests — certify merge, staged rollout, CertMesh parity, determinism."""

import os
import tempfile
import unittest

from certstra_core import (
    certify, certifiable, needs_review, blocked, plan_stages, verify_provenance,
    to_attestra_verdict, append_cert, verify_ledger, build_record,
)
from certstra_core.determinism import check_tree
from certstra_packs.loader import load_packs, run_stage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED = {"cert-mesh", "release-mesh", "robo-trace",
            "orbi-roam",   # BUILD_ON_PLATFORM: OrbiRoam tasking authorization -> Certstra certify pack
            "bio-clock"}   # BUILD_ON_PLATFORM: BioClock drift+quarantine certification (not a CONDENSE)


class TestCertify(unittest.TestCase):
    def test_severity_merge(self):
        self.assertEqual(certify([certifiable("a"), blocked("b", "x")])["verdict"], "blocked")
        self.assertEqual(certify([certifiable("a"), needs_review("b", "x")])["verdict"], "needs_review")
        self.assertEqual(certify([certifiable("a"), certifiable("b")])["verdict"], "certifiable")

    def test_attestra_alignment(self):
        self.assertEqual(to_attestra_verdict("certifiable"), "valid")
        self.assertEqual(to_attestra_verdict("needs_review"), "thin")
        self.assertEqual(to_attestra_verdict("blocked"), "breach")


class TestStageSchedule(unittest.TestCase):
    def test_full_rollout(self):
        sched = [{"name": "canary", "cohort_pct": 30, "observed_incidents": 0, "incident_threshold": 1},
                 {"name": "broad", "cohort_pct": 70, "observed_incidents": 0, "incident_threshold": 2}]
        r = plan_stages("OS-1", sched, now="T")
        self.assertTrue(r["rollout_complete"])
        self.assertFalse(r["halted"])

    def test_halt_on_incident(self):
        sched = [{"name": "canary", "cohort_pct": 5, "observed_incidents": 3, "incident_threshold": 1},
                 {"name": "broad", "cohort_pct": 95, "observed_incidents": 0, "incident_threshold": 2}]
        r = plan_stages("OS-2", sched, now="T")
        self.assertTrue(r["halted"])
        self.assertEqual(len(r["stages"]), 1)   # halted at canary, broad never planned


class TestProvenance(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(verify_provenance({"evidence_hash": "e7"},
                                          [{"evidence_hash": "e7", "confirmed": True}])["provenance_valid"])
        self.assertFalse(verify_provenance({"evidence_hash": "e7"},
                                           [{"evidence_hash": "e7", "confirmed": False}])["provenance_valid"])


class TestLedger(unittest.TestCase):
    def test_chain_time_independent_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.jsonl")
            append_cert(p, {"verdict": "certifiable", "certified_at": "X"}, "cert-mesh", "certify", now="T1")
            append_cert(p, {"verdict": "blocked", "certified_at": "X"}, "cert-mesh", "certify", now="T2")
            self.assertTrue(verify_ledger(p)["valid"])
        a = build_record("", {"v": 1}, "m", "certify", now="AAA")
        b = build_record("", {"v": 1}, "m", "certify", now="ZZZ")
        self.assertEqual(a["record_hash"], b["record_hash"])


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = load_packs()

    def test_all_packs(self):
        self.assertEqual(set(self.reg["packs"]), EXPECTED)
        self.assertEqual(self.reg["errors"], [])
        self.assertEqual(self.reg["dropped"], [])

    def test_every_stage_runs(self):
        for name, pack in self.reg["packs"].items():
            for stage in pack["stages"]:
                self.assertIn(stage, pack["samples"], f"{name} missing {stage} sample")
                self.assertIsInstance(run_stage(pack, stage, pack["samples"][stage], now="T"), dict)


class TestCertMeshParity(unittest.TestCase):
    """cert-mesh sample verdicts reproduce CertMesh's certifiable/needs_review/blocked scheme."""
    def setUp(self):
        self.m = load_packs()["packs"]["cert-mesh"]

    def test_certifiable(self):
        self.assertEqual(run_stage(self.m, "certify", self.m["samples"]["certify"])["verdict"], "certifiable")

    def test_needs_review_on_improvement(self):
        self.assertEqual(run_stage(self.m, "certify", self.m["samples"]["needs_review"])["verdict"], "needs_review")

    def test_blocked_on_regression(self):
        self.assertEqual(run_stage(self.m, "certify", self.m["samples"]["blocked"])["verdict"], "blocked")


class TestDeterminism(unittest.TestCase):
    def test_clean(self):
        rep = check_tree(ROOT)
        self.assertTrue(rep["clean"], f"violations: {rep['violations']}")
        self.assertGreater(rep["files_scanned"], 6)


if __name__ == "__main__":
    unittest.main()
