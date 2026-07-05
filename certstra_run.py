#!/usr/bin/env python3
"""CertRun — run a pack's declared stages end-to-end.

certify/stage -> (provenance verify) -> certification ledger. Meta/IO layer:
file I/O + injected `now`, clock-free.
"""

from certstra_core.ledger import append_cert, verify_ledger
from certstra_core.provenance import verify_provenance
from certstra_packs.loader import run_stage


def cert_run(pack, inputs, now="", ledger_path=None, subject=None, chain=None, record=None):
    """Run every declared stage the caller supplied inputs for.

    inputs: {"certify": {packet}, "stage": {release}}
    chain + record: optional; verify the record's evidence against the chain.
    """
    pid = subject or f"{pack['name']}-run"
    out = {"pack": pack["name"], "stages": {}, "ledger_records": []}
    for stage in ("certify", "stage"):
        if stage not in pack["stages"] or stage not in inputs:
            continue
        result = run_stage(pack, stage, inputs[stage], now=now)
        out["stages"][stage] = result
        if ledger_path:
            rec = append_cert(ledger_path, result, pack["name"], stage, now=now, subject=pid)
            out["ledger_records"].append({"kind": stage, "index": rec["index"]})
    if chain is not None and record is not None:
        prov = verify_provenance(record, chain)
        out["provenance"] = prov
        if ledger_path:
            rec = append_cert(ledger_path, prov, pack["name"], "verify", now=now, subject=pid)
            out["ledger_records"].append({"kind": "verify", "index": rec["index"]})
    if ledger_path:
        out["chain"] = verify_ledger(ledger_path)
    return out


def pack_inputs_from_samples(pack):
    return {stage: pack["samples"][stage] for stage in pack["stages"]
            if stage in pack.get("samples", {})}
