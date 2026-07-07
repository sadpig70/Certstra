#!/usr/bin/env python3
"""BioClockPack — biological-clock certification as a Certstra certify pack.

source_project: github.com/sadpig70/BioClock

ROUTING / CONDENSE FINDING (HELIX machine-aware routing): BioClock was grouped with
DriftDossier + LazarettoStage as a "Bio staged-release" cluster whose supposed novel M11
"drift" machine looked like a CONDENSE (new-platform) candidate. Reading real code refutes
that: M11 drift is NOT a novel platform machine. BioClock's `certify_bio_clock` turns
evidence drift + freshness + quarantine into a certification verdict
(certified/conditional/expired/revoked/blocked) — Certstra's certify machine
(certified -> certifiable, conditional -> needs_review, expired/revoked/blocked -> blocked).
So BioClock is BUILD_ON_PLATFORM onto Certstra, not a new platform. (DriftDossier is a
per-event divergence SCORING machine -> defer; LazarettoStage is M12 staged-release, which
Certstra already has.)

Reproduces BioClock.core.track_drift + certify_bio_clock as four certify checks whose
max-severity equals the source verdict. See tests/test_bio_clock_parity.py.
"""

from ._base import certifiable, needs_review, blocked

DEFAULT_MAX_FRESHNESS_DAYS = 30


def _drift(packet):
    """Mirror track_drift: drift severity, sample gap, freshness expiry."""
    protocol = packet.get("protocol", {}) if isinstance(packet.get("protocol"), dict) else {}
    evidence = packet.get("evidence", {}) if isinstance(packet.get("evidence"), dict) else {}
    target = float(protocol.get("target_effect_size", 0) or 0)
    observed = float(evidence.get("observed_effect_size", 0) or 0)
    required = float(protocol.get("required_samples", 0) or 0)
    actual = float(evidence.get("actual_samples", 0) or 0)
    freshness = float(evidence.get("data_freshness_days", 0) or 0)
    max_fresh = float(packet.get("max_freshness_days", DEFAULT_MAX_FRESHNESS_DAYS) or DEFAULT_MAX_FRESHNESS_DAYS)
    drift_magnitude = abs(target - observed)
    severity = "none" if drift_magnitude < 0.1 else "moderate" if drift_magnitude < 0.3 else "severe"
    return severity, max(0.0, required - actual), freshness > max_fresh


def checks(packet, P=None):
    """certify-stage function (kernel STAGE_FN: certify -> checks).

    Four checks whose max-severity reproduces certify_bio_clock: quarantine-not-passed /
    freshness-expired / severe-drift -> blocked; moderate-drift / sample-gap -> needs_review.
    """
    severity, sample_gap, freshness_expired = _drift(packet)
    quarantine = packet.get("quarantine", {}) if isinstance(packet.get("quarantine"), dict) else {}
    stages = quarantine.get("stages", [])
    stages = stages if isinstance(stages, list) else []
    all_passed = bool(stages) and all(s.get("observation_passed") is True for s in stages)

    out = [certifiable("quarantine") if all_passed
           else blocked("quarantine", "quarantine stages not all observation-passed")]
    out.append(blocked("freshness", "evidence freshness expired") if freshness_expired
               else certifiable("freshness"))
    if severity == "severe":
        out.append(blocked("drift", "severe evidence drift (certification revoked)"))
    elif severity == "moderate":
        out.append(needs_review("drift", "moderate evidence drift"))
    else:
        out.append(certifiable("drift"))
    out.append(needs_review("samples", f"sample gap {sample_gap:g}") if sample_gap > 0
               else certifiable("samples"))
    return out


MANIFEST = {
    "name": "bio-clock", "version": "1.0", "stages": ["certify"],
    "cert_schema": "schemas/cert-bioclock.schema.json",
    "source_project": "github.com/sadpig70/BioClock",
}


def _packet(pid, target, observed, required, actual, freshness, stages_passed):
    return {"packet_id": pid,
            "protocol": {"endpoint": "primary", "target_effect_size": target, "required_samples": required},
            "evidence": {"observed_effect_size": observed, "actual_samples": actual, "data_freshness_days": freshness},
            "quarantine": {"organism_id": pid, "stages": [
                {"name": "isolation", "duration_days": 14, "observation_passed": stages_passed}]}}


SAMPLES = {
    # no drift, samples met, fresh, quarantine passed -> certified -> certifiable
    "certify": {"packet": _packet("BC-C", 0.5, 0.5, 100, 100, 10, True)},
    # moderate drift (|0.5-0.7|=0.2), else clean -> conditional -> needs_review
    "needs_review": {"packet": _packet("BC-NR", 0.5, 0.7, 100, 100, 10, True)},
    # quarantine stage failed -> blocked
    "blocked": {"packet": _packet("BC-BLK", 0.5, 0.5, 100, 100, 10, False)},
}
