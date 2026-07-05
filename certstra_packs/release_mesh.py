#!/usr/bin/env python3
"""ReleaseMeshPack — robot OS update as a vehicle-style release (type approval + staged rollout).

source_project: github.com/sadpig70/ReleaseMesh
stages: certify, stage
"""

from ._base import certifiable, needs_review, blocked


def checks(packet, P=None):
    """certify: signed + type-approved update."""
    r = packet["release"]
    out = []
    out.append(certifiable("signature") if r.get("signed") is True
               else blocked("signature", "update is not signed"))
    out.append(certifiable("type_approval") if r.get("type_approved") is True
               else needs_review("type_approval", "type approval pending"))
    return out


def schedule(release, P=None):
    """stage: the release carries its staged rollout plan (cohorts + observation windows)."""
    return release.get("stages", [])


MANIFEST = {
    "name": "release-mesh", "version": "1.0", "stages": ["certify", "stage"],
    "cert_schema": "schemas/packet-releasemesh.schema.json",
    "source_project": "github.com/sadpig70/ReleaseMesh",
}

SAMPLES = {
    "certify": {"packet": {"release": {"id": "OS-4.2", "signed": True, "type_approved": True}}},
    "stage": {"release": {"id": "OS-4.2", "stages": [
        {"name": "canary", "cohort_pct": 5, "observation_window": "48h",
         "observed_incidents": 0, "incident_threshold": 1},
        {"name": "early", "cohort_pct": 25, "observation_window": "72h",
         "observed_incidents": 1, "incident_threshold": 2},
        {"name": "broad", "cohort_pct": 70, "observation_window": "168h",
         "observed_incidents": 0, "incident_threshold": 3},
    ]}},
}
