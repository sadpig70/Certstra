#!/usr/bin/env python3
"""RoboTracePack — robot incident evidence validation and reconstruction.

source_project: github.com/sadpig70/RoboTrace
stages: certify
"""

from ._base import certifiable, needs_review, blocked


def checks(packet, P=None):
    """certify: incident evidence integrity + reconstructibility."""
    inc = packet["incident"]
    out = []
    if inc.get("evidence_hash") and inc.get("chain_intact") is True:
        out.append(certifiable("evidence_integrity"))
    else:
        out.append(blocked("evidence_integrity", "incident evidence chain broken or missing"))
    out.append(certifiable("reconstruction") if inc.get("reconstructible") is True
               else needs_review("reconstruction", "incident not fully reconstructible"))
    return out


MANIFEST = {
    "name": "robo-trace", "version": "1.0", "stages": ["certify"],
    "cert_schema": "schemas/packet-robotrace.schema.json",
    "source_project": "github.com/sadpig70/RoboTrace",
}

SAMPLES = {
    "certify": {"packet": {"incident": {
        "incident_id": "INC-7", "evidence_hash": "e7", "chain_intact": True, "reconstructible": True}}},
}
