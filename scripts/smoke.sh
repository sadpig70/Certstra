#!/usr/bin/env bash
set -euo pipefail; cd "$(dirname "$0")/.."
NOW="${1:-2026-07-06}"; TMP=".smoke_tmp"; trap 'rm -rf "$TMP"' EXIT; rm -rf "$TMP"; mkdir -p "$TMP"
echo "[1/4] unittest"; python -m unittest discover -s tests -q
echo "[2/4] determinism"; python cli.py determinism >/dev/null && echo "      clean"
echo "[3/4] certify+stage pipeline (release-mesh) + ledger"
python cli.py run --pack release-mesh --ledger "$TMP/c.jsonl" --now "$NOW" >/dev/null
python cli.py verify --ledger "$TMP/c.jsonl" >/dev/null && echo "      ledger chain valid"
echo "[4/4] pack registry"
python -c "from certstra_packs.loader import load_packs;r=load_packs();assert len(r['packs'])==3 and not r['errors'];print('      3 packs, 0 errors')"
echo "SMOKE OK"
