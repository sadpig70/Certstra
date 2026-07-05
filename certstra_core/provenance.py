#!/usr/bin/env python3
"""Provenance — verify a certification/incident record against a confirmed evidence chain.

Generalizes RoboTrace incident evidence + OrbiRoam hash-chained authorization: the
record's evidence must appear, confirmed, in the chain. Pure stdlib.
"""


def verify_provenance(record, chain):
    """Return {provenance_valid, chain_length, evidence_hash}."""
    evidence = record.get("evidence_hash")
    link = next((l for l in chain
                 if l.get("evidence_hash") == evidence and l.get("confirmed")), None)
    return {
        "provenance_valid": evidence is not None and link is not None,
        "chain_length": len(chain),
        "evidence_hash": evidence,
    }
