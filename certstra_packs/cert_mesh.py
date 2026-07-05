#!/usr/bin/env python3
"""CertMeshPack — reference certify pack. Parity with CertMesh.

source_project: github.com/sadpig70/CertMesh
stages: certify
Parity anchor: per-parameter drift + capability diff -> checks whose max-severity merge
reproduces CertMesh.certify verdict (certifiable / needs_review / blocked).
"""

from ._base import certifiable, needs_review, blocked


def _is_safer(direction, delta):
    if direction == "lower_is_safer":
        return delta < 0
    if direction == "upper_is_safer":
        return delta > 0
    return False  # "exact": any change is drift


def checks(packet, P=None):
    """certify-stage function (kernel STAGE_FN: certify -> checks)."""
    baseline = packet["baseline"]
    candidate = packet["candidate"]
    out = []
    for p in baseline["parameters"]:
        v = candidate["parameter_values"][p["name"]]
        delta = v - p["certified_value"]
        if abs(delta) <= p["tolerance"]:
            out.append(certifiable(p["name"]))
        elif _is_safer(p["direction"], delta):
            out.append(needs_review(p["name"], "improvement drift"))
        else:
            out.append(blocked(p["name"], "regression drift"))
    added = sorted(set(candidate.get("capabilities", [])) - set(baseline.get("capabilities", [])))
    if added:
        out.append(needs_review("capabilities", f"uncertified capabilities added: {added}"))
    return out


MANIFEST = {
    "name": "cert-mesh", "version": "1.0", "stages": ["certify"],
    "cert_schema": "schemas/packet-certmesh.schema.json",
    "source_project": "github.com/sadpig70/CertMesh",
}


def _packet(pid, values, caps, added_cap=False):
    params = [
        {"name": "max_speed", "certified_value": 2.0, "tolerance": 0.1, "direction": "lower_is_safer", "unit": "m/s"},
        {"name": "min_clearance", "certified_value": 0.5, "tolerance": 0.05, "direction": "upper_is_safer", "unit": "m"},
    ]
    cand_caps = list(caps) + (["autonomous_night_ops"] if added_cap else [])
    return {"policy_id": pid, "baseline": {"parameters": params, "capabilities": caps},
            "candidate": {"parameter_values": values, "capabilities": cand_caps}}


SAMPLES = {
    "certify": {"packet": _packet("P-CERT", {"max_speed": 2.05, "min_clearance": 0.52}, ["pick", "place"])},
    # improvement (slower/safer) -> needs_review; regression -> blocked
    "needs_review": {"packet": _packet("P-NR", {"max_speed": 1.5, "min_clearance": 0.52}, ["pick", "place"])},
    "blocked": {"packet": _packet("P-BLK", {"max_speed": 2.5, "min_clearance": 0.52}, ["pick", "place"])},
}
