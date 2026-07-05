#!/usr/bin/env python3
"""Certification-pack loader + registry + stage dispatcher.

Discovers packs under certstra_packs/, validates their contract, dedups by fingerprint,
and dispatches a stage through the kernel. A pack contributes formulas only; certify/
stage/ledger stay in certstra_core.
"""

import importlib
import pkgutil

from certstra_core.fingerprint import fingerprint_pack
from certstra_core.certify import certify
from certstra_core.stage_schedule import plan_stages

_RESERVED = {"loader", "_base"}
_REQUIRED_MANIFEST = ("name", "version", "stages", "cert_schema", "source_project")
STAGES = ("certify", "stage")
STAGE_FN = {"certify": "checks", "stage": "schedule"}


def discover_module_names(package="certstra_packs"):
    pkg = importlib.import_module(package)
    names = []
    for _finder, name, _ispkg in pkgutil.iter_modules(pkg.__path__):
        short = name.split(".")[-1]
        if short in _RESERVED or short.startswith("__"):
            continue
        names.append(name)
    return sorted(names)


def validate_module(mod, name):
    m = getattr(mod, "MANIFEST", None)
    if not isinstance(m, dict):
        return None, None, f"{name}: no MANIFEST dict"
    miss = [k for k in _REQUIRED_MANIFEST if not m.get(k)]
    if miss:
        return None, None, f"{name}: manifest missing {miss}"
    stages = m["stages"]
    if not isinstance(stages, list) or not stages or any(s not in STAGES for s in stages):
        return None, None, f"{name}: stages must be a non-empty subset of {STAGES}"
    fns = {}
    for stage in stages:
        fn = getattr(mod, STAGE_FN[stage], None)
        if not callable(fn):
            return None, None, f"{name}: stage '{stage}' requires callable {STAGE_FN[stage]}()"
        fns[stage] = fn
    return m, fns, ""


def load_packs(package="certstra_packs"):
    registry = {"packs": {}, "dropped": [], "errors": []}
    seen_fp = {}
    for mod_name in discover_module_names(package):
        try:
            mod = importlib.import_module(f"{package}.{mod_name}")
        except Exception as exc:  # noqa: BLE001
            registry["errors"].append(f"{mod_name}: import failed: {exc}")
            continue
        manifest, fns, err = validate_module(mod, mod_name)
        if err:
            registry["errors"].append(err)
            continue
        fp = fingerprint_pack(manifest)
        if fp in seen_fp:
            registry["dropped"].append({"name": manifest["name"],
                                        "reason": f"duplicate_fingerprint_of:{seen_fp[fp]}"})
            continue
        seen_fp[fp] = manifest["name"]
        registry["packs"][manifest["name"]] = {
            **manifest, "fingerprint": fp, "module": f"{package}.{mod_name}",
            "fns": fns, "samples": dict(getattr(mod, "SAMPLES", {})),
        }
    return registry


def get_pack(registry, name):
    if name not in registry["packs"]:
        raise KeyError(f"unknown pack: {name} (have: {sorted(registry['packs'])})")
    return registry["packs"][name]


def run_stage(pack, stage, inputs, now=""):
    if stage not in pack["fns"]:
        raise ValueError(f"pack '{pack['name']}' does not implement stage '{stage}'")
    fns = pack["fns"]
    if stage == "certify":
        return certify(fns["certify"](inputs["packet"], inputs.get("P", {})))
    if stage == "stage":
        release = inputs["release"]
        return plan_stages(release, fns["stage"](release, inputs.get("P", {})), now=now)
    raise ValueError(f"unknown stage: {stage}")
