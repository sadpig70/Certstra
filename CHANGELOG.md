# Changelog

## [0.1.0] — 2026-07-06

First release of Certstra — a deterministic certification platform (kernel + N domain
packs). Fourth of the HELIX `-stra` family (attest/clear/route/certify), and the FIRST
platform emitted (semi-automatically) by the HELIX Condense recipe from the
robotics/release cluster.

- certstra_core: verdict (certifiable<needs_review<blocked, Attestra-aligned), certify
  (severity merge = CertMesh._decide_verdict), stage_schedule (M12 staged rollout, new),
  provenance, ledger, fingerprint, determinism
- certstra_packs: cert-mesh (reference, CertMesh parity), release-mesh, robo-trace
- certstra_run.py, cli.py, tests, .pgf design + status
- CERTMESH PARITY OK (4/4 verdict cases == real CertMesh.certify); determinism clean; 12 tests
