"""Certstra kernel — single-source deterministic certification substrate.

stdlib only. Time is injected (`now`); hashes exclude wall-time metadata. Fourth of
the -stra family (attest / clear / route / certify) — shared severity algebra.
Emitted by the HELIX Condense recipe from the robotics/release cluster.
"""

from .verdict import (
    SEVERITY, ATTESTRA_MAP, to_attestra_verdict, worst_of,
    certifiable, needs_review, blocked,
)
from .certify import certify
from .stage_schedule import plan_stages
from .provenance import verify_provenance
from .ledger import canonical_json, sha256, append_cert, build_record, verify_ledger
from .fingerprint import normalize, fingerprint, fingerprint_pack

__all__ = [
    "SEVERITY", "ATTESTRA_MAP", "to_attestra_verdict", "worst_of",
    "certifiable", "needs_review", "blocked",
    "certify", "plan_stages", "verify_provenance",
    "canonical_json", "sha256", "append_cert", "build_record", "verify_ledger",
    "normalize", "fingerprint", "fingerprint_pack",
]
