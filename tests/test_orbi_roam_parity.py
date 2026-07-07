#!/usr/bin/env python3
"""Parity anchor: certstra_packs.orbi_roam vs the real OrbiRoam registry.

OrbiRoam is an independent repo (github.com/sadpig70/OrbiRoam); it is not vendored in
Certstra. When its source is importable in a dev checkout, this test asserts the pack's
certify verdict reproduces registry.decide's action (authorized/review_required/blocked)
across every branch. In CI (source absent) it skips.

Point ORBIROAM_SRC at the project's ``src`` dir to run it, e.g.
    ORBIROAM_SRC=D:/IdeaFirst/orbiroam/src python -m unittest tests.test_orbi_roam_parity
"""

import os
import sys
import unittest

from certstra_packs.loader import load_packs, run_stage


def _load_orbiroam():
    candidates = [os.environ.get("ORBIROAM_SRC")]
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates += [
        os.path.join(here, "..", "orbiroam", "src"),
        os.path.join(here, "..", "OrbiRoam", "src"),
        "D:/IdeaFirst/orbiroam/src",
    ]
    for cand in candidates:
        if cand and os.path.isdir(cand) and cand not in sys.path:
            sys.path.insert(0, cand)
    try:
        from orbiroam import registry as registry_mod  # noqa: WPS433
        from orbiroam import models as models_mod  # noqa: WPS433
        return registry_mod, models_mod
    except Exception:  # noqa: BLE001 — source simply not present here
        return None, None


_REGISTRY, _MODELS = _load_orbiroam()

_ACTION_TO_VERDICT = {"authorized": "certifiable", "review_required": "needs_review", "blocked": "blocked"}

# (tasking_jur, action_jur, triggers, registered, latency) covering every branch.
_CASES = [
    ("US", "US", True, True, 30.0),          # same-jur within SLA -> authorized
    ("US", "EU", True, True, 20.0),          # roamed within EU SLA 30 -> authorized
    ("US", "EU", True, True, 45.0),          # roamed but over EU SLA -> review_required
    ("US", "US", False, True, 999.0),        # no autonomous action -> authorized
    ("US", "US", True, False, 30.0),         # unregistered authority -> blocked
    ("US", "atlantis", True, True, 5.0),     # action jurisdiction not registered -> blocked
    ("US", "intl_waters", True, True, 5.0),  # cross-jur, no roaming agreement -> blocked
    ("JP_KR", "commercial", True, True, 100.0),  # roamed, within commercial SLA 120 -> authorized
]


def _packet(tj, aj, triggers, registered, latency):
    return {"tasking": {"tasking_id": "T", "operator": "op", "tasking_jurisdiction": tj,
                        "action_jurisdiction": aj, "triggers_autonomous_action": triggers,
                        "latency_seconds": latency, "registered": registered}}


@unittest.skipUnless(_REGISTRY is not None, "OrbiRoam source not importable (independent repo)")
class TestOrbiRoamParity(unittest.TestCase):
    def setUp(self):
        self.pack = load_packs()["packs"]["orbi-roam"]

    def test_action_matches_source(self):
        for tj, aj, triggers, registered, latency in _CASES:
            with self.subTest(tj=tj, aj=aj, latency=latency):
                tasking = _MODELS.CanonicalTasking(
                    tasking_id="T", operator="op", sensor_id="s", tasking_jurisdiction=tj,
                    action_jurisdiction=aj, triggers_autonomous_action=triggers,
                    latency_seconds=latency, registered=registered, timestamp="", source="t")
                action = _REGISTRY.decide(tasking).action
                expected = _ACTION_TO_VERDICT[action]

                result = run_stage(self.pack, "certify",
                                   {"packet": _packet(tj, aj, triggers, registered, latency)})
                self.assertEqual(
                    result["verdict"], expected,
                    f"action={action} -> expected {expected}, got {result['verdict']}")


if __name__ == "__main__":
    unittest.main()
