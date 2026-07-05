#!/usr/bin/env python3
"""Verdict severity algebra + -stra family alignment.

Certstra certification verdicts (certifiable < needs_review < blocked) share the
severity shape of the -stra family. `to_attestra_verdict` maps them so a certification
can be attested. Reproduces CertMesh's verdict scheme. Pure stdlib.
"""

SEVERITY = {"certifiable": 0, "needs_review": 1, "blocked": 2}
ATTESTRA_MAP = {"certifiable": "valid", "needs_review": "thin", "blocked": "breach"}


def to_attestra_verdict(verdict):
    return ATTESTRA_MAP[verdict]


def worst_of(verdicts):
    return max(verdicts, key=lambda v: SEVERITY[v]) if verdicts else "needs_review"


def certifiable(check, reason="within certified tolerance"):
    return {"check": check, "verdict": "certifiable", "reason": reason}


def needs_review(check, reason):
    return {"check": check, "verdict": "needs_review", "reason": reason}


def blocked(check, reason):
    return {"check": check, "verdict": "blocked", "reason": reason}
