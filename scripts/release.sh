#!/usr/bin/env bash
# Release strand gates 1-5 (automatic). Publish (6) is user-gated: run gh manually.
set -euo pipefail; cd "$(dirname "$0")/.."
python -m unittest discover -s tests -q
python cli.py determinism >/dev/null
bash scripts/smoke.sh >/dev/null
test -f CHANGELOG.md && test -f pyproject.toml
echo "RELEASE-READY (gates 1-5 pass)"
