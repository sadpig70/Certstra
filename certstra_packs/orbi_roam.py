#!/usr/bin/env python3
"""OrbiRoamPack — orbital tasking-to-action authorization as a Certstra certify pack.

source_project: github.com/sadpig70/OrbiRoam
stages: certify

ROUTING (HELIX BUILD_ON_PLATFORM, machine-aware): OrbiRoam binds orbital sensor tasking
that triggers a terrestrial autonomous action to an accountable jurisdiction, a
human-review SLA, and a cross-jurisdiction roaming agreement, gating each tasking into
authorized / review_required / blocked. That 3-level authorization verdict maps exactly
onto Certstra's certify algebra (certifiable / needs_review / blocked), so OrbiRoam lands
on Certstra (the first non-hand-built Certstra growth beyond its condensed reference packs).

Reproduces OrbiRoam.registry.decide, incl. its published JURISDICTION_TABLE and
ROAMING_AGREEMENTS reference tables. See tests/test_orbi_roam_parity.py.
"""

from ._base import certifiable, needs_review, blocked

# Indicative governance defaults (mirror OrbiRoam.models): jurisdiction -> (max
# tasking->action latency without review, requires a roaming agreement cross-jurisdiction).
JURISDICTION_TABLE = {
    "US": (60.0, True), "EU": (30.0, True), "JP_KR": (45.0, True),
    "intl_waters": (10.0, True), "commercial": (120.0, True),
}
ROAMING_AGREEMENTS = frozenset({
    frozenset({"US", "EU"}), frozenset({"US", "commercial"}), frozenset({"EU", "commercial"}),
    frozenset({"JP_KR", "commercial"}), frozenset({"US", "JP_KR"}),
})


def _has_roaming(a, b):
    return a == b or frozenset({a, b}) in ROAMING_AGREEMENTS


def decide(tasking):
    """authorized / review_required / blocked for one tasking. Mirrors registry.decide."""
    tj = tasking.get("tasking_jurisdiction")
    aj = tasking.get("action_jurisdiction")
    same = tj == aj
    roamed = (not same) and _has_roaming(tj, aj)
    if not tasking.get("triggers_autonomous_action", False):
        return "authorized", "informational tasking; no terrestrial autonomous action"
    if not tasking.get("registered", False):
        return "blocked", "unregistered tasking authority — no accountable jurisdiction or SLA"
    policy = JURISDICTION_TABLE.get(aj)
    if policy is None:
        return "blocked", f"action jurisdiction '{aj}' is not registered"
    max_latency, requires_roaming = policy
    if not same and requires_roaming and not roamed:
        return "blocked", f"no roaming agreement between {tj} and {aj}"
    if float(tasking.get("latency_seconds", 0) or 0) > max_latency:
        return "review_required", f"latency exceeds {aj} SLA {max_latency:.0f}s — human-in-loop required"
    where = "same-jurisdiction" if same else "roamed cross-jurisdiction"
    return "authorized", f"registered + {where} + within SLA"


def checks(packet, P=None):
    """certify-stage function (kernel STAGE_FN: certify -> checks)."""
    tasking = packet.get("tasking", {}) if isinstance(packet.get("tasking"), dict) else {}
    action, reason = decide(tasking)
    name = "roaming_registry"
    if action == "authorized":
        return [certifiable(name, reason)]
    if action == "review_required":
        return [needs_review(name, reason)]
    return [blocked(name, reason)]


MANIFEST = {
    "name": "orbi-roam", "version": "1.0", "stages": ["certify"],
    "cert_schema": "schemas/cert-orbiroam.schema.json",
    "source_project": "github.com/sadpig70/OrbiRoam",
}


def _tasking(tid, tj, aj, triggers=True, registered=True, latency=10.0):
    return {"tasking_id": tid, "operator": "op", "tasking_jurisdiction": tj,
            "action_jurisdiction": aj, "triggers_autonomous_action": triggers,
            "latency_seconds": latency, "registered": registered}


SAMPLES = {
    # same-jurisdiction, registered, within SLA -> authorized -> certifiable
    "certify": {"packet": {"tasking": _tasking("T-A", "US", "US", latency=30.0)}},
    # US->EU (roamed) but latency 45 > EU SLA 30 -> review_required -> needs_review
    "needs_review": {"packet": {"tasking": _tasking("T-R", "US", "EU", latency=45.0)}},
    # US->intl_waters, cross-jurisdiction with no roaming agreement -> blocked
    "blocked": {"packet": {"tasking": _tasking("T-B", "US", "intl_waters")}},
}
