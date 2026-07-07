#!/usr/bin/env python3
"""Parity anchor: certstra_packs.bio_clock vs the real BioClock core.

BioClock is an independent repo (github.com/sadpig70/BioClock); it is not vendored in
Certstra. When its source is importable in a dev checkout, this test asserts the pack's
certify verdict reproduces certify_bio_clock's certification (mapped: certified ->
certifiable, conditional -> needs_review, expired/revoked/blocked -> blocked) across every
branch. In CI (source absent) it skips.

Point BIOCLOCK_SRC at the project's ``src`` dir to run it, e.g.
    BIOCLOCK_SRC=D:/HELIX/BioClock/src python -m unittest tests.test_bio_clock_parity
"""

import os
import sys
import unittest

from certstra_packs.loader import load_packs, run_stage


def _load_bioclock():
    candidates = [os.environ.get("BIOCLOCK_SRC")]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates += [
        os.path.join(here, "..", "BioClock", "src"),
        "D:/HELIX/BioClock/src",
    ]
    for cand in candidates:
        if cand and os.path.isdir(cand) and cand not in sys.path:
            sys.path.insert(0, cand)
    try:
        from BioClock import core  # noqa: WPS433
        return core
    except Exception:  # noqa: BLE001 — source simply not present here
        return None


_CORE = _load_bioclock()

# certify_bio_clock certification -> Certstra verdict.
_CERT_TO_VERDICT = {"certified": "certifiable", "conditional": "needs_review",
                    "expired": "blocked", "revoked": "blocked", "blocked": "blocked"}


def _packet(target, observed, required, actual, freshness, stages_passed):
    return {"packet_id": "P",
            "protocol": {"endpoint": "primary", "target_effect_size": target, "required_samples": required},
            "evidence": {"observed_effect_size": observed, "actual_samples": actual, "data_freshness_days": freshness},
            "quarantine": {"organism_id": "o", "stages": [
                {"name": "isolation", "duration_days": 14, "observation_passed": stages_passed}]}}

# (target, observed, required, actual, freshness, stages_passed): certified; conditional
# (moderate drift); conditional (sample gap); revoked (severe drift); expired (stale);
# blocked (quarantine fail).
_CASES = [
    (0.5, 0.5, 100, 100, 10, True),
    (0.5, 0.7, 100, 100, 10, True),
    (0.5, 0.5, 100, 80, 10, True),
    (0.5, 0.95, 100, 100, 10, True),
    (0.5, 0.5, 100, 100, 40, True),
    (0.5, 0.5, 100, 100, 10, False),
]


@unittest.skipUnless(_CORE is not None, "BioClock source not importable (independent repo)")
class TestBioClockParity(unittest.TestCase):
    def setUp(self):
        self.pack = load_packs()["packs"]["bio-clock"]

    def test_certification_matches_source(self):
        for target, observed, required, actual, freshness, passed in _CASES:
            with self.subTest(observed=observed, actual=actual, freshness=freshness, passed=passed):
                report = _CORE.track_drift(
                    {"endpoint": "primary", "target_effect_size": target, "required_samples": required},
                    {"observed_effect_size": observed, "actual_samples": actual, "data_freshness_days": freshness})
                cert = _CORE.certify_bio_clock(
                    report, {"organism_id": "o", "stages": [
                        {"name": "isolation", "duration_days": 14, "observation_passed": passed}]})
                expected = _CERT_TO_VERDICT[cert["certification"]]

                pkt = _packet(target, observed, required, actual, freshness, passed)
                result = run_stage(self.pack, "certify", {"packet": pkt})
                self.assertEqual(
                    result["verdict"], expected,
                    f"cert={cert['certification']} -> expected {expected}, got {result['verdict']}")


if __name__ == "__main__":
    unittest.main()
