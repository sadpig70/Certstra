#!/usr/bin/env python3
"""Certify — merge per-check certification verdicts to the highest severity.

Generalizes CertMesh._decide_verdict: any regression -> blocked; else any
improvement / uncertified-added -> needs_review; else certifiable. A pack emits
one CheckResult per parameter/capability with the right verdict; the max-severity
merge reproduces CertMesh exactly. Pure stdlib.
"""

from .verdict import SEVERITY


def certify(checks):
    """Merge check verdicts (blocked > needs_review > certifiable)."""
    if not checks:
        return {"verdict": "needs_review", "reason": "no_checks", "worst": None, "checks": []}
    worst = max(checks, key=lambda c: SEVERITY[c["verdict"]])
    return {"verdict": worst["verdict"], "reason": worst["reason"],
            "worst": worst["check"], "checks": checks}
