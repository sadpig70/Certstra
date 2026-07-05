# Certstra Design @v:0.1 (Condense-emitted)

> **HELIX Condense 레시피(U2)가 robotics/release 군집에서 emit한 4번째 `-stra` 플랫폼.**
> 인증(certify) 커널 + 도메인 팩. 레시피 근거: `_workspace/condense/U2-condense-recipe.md`.
> Emit provenance: cluster=Robotics/Release(M2·M4·M12), reference=CertMesh, source roots=D:/IdeaFirst.

## 0. 명제

로봇 정책·릴리스·사고 증거를 결정론 인증하는 플랫폼. `certify → stage → verify` + hash-chain 원장.
verdict severity(certifiable<needs_review<blocked)는 Attestra(valid/thin/breach)와 정렬 → 인증을 증언 가능.

## 1. Condense MachineExtract 결과 (reused vs new)

| machine | 모듈 | 출처 |
|---|---|---|
| M1 ledger · M14 fingerprint · determinism | ledger/fingerprint/determinism | **재사용** (Routestra 커널 이식) |
| M2 verdict severity | verdict + certify | **재사용 패턴** (Attestra/Routestra 병합 로직) |
| M4 provenance | provenance | **재사용 패턴** (SkyGrid/Attestra) |
| **M12 staged rollout** | **stage_schedule** | **신규** (이 군집 고유) |

## 2. Gantree

```
Certstra // 결정론 인증 플랫폼 (Condense-emitted) (done) @v:0.1
    CertstraCore // 커널 (done) #core
        Verdict // certifiable<needs_review<blocked + Attestra 정렬 (done)
        Certify // check severity 병합 (CertMesh._decide_verdict 재현) (done)
        StageSchedule // 단계적 rollout + go/halt (M12 신규) (done)
        Provenance // 사고증거 chain 검증 (done)
        Ledger // hash-chain 인증 원장 (재사용) (done)
        Fingerprint // 팩 dedup (재사용) (done)
        Determinism // 경계 검증 (재사용) (done)
    PackContract // 팩 계약 (certify/stage) (done) #contract
        Loader // 발견·검증·dedup·run_stage (done)
    Packs // cert-mesh(ref)·release-mesh·robo-trace (done) #packs
    CertRun // certify→stage→verify→ledger 파이프라인 (done) #pipeline
    CLI // pack/run/stage/verify/determinism (done) #cli
    Tests // 커널+팩+parity+determinism (done) #test
```

## 3. PPR — certify (CertMesh parity 핵심)

```python
def certify(checks: list) -> dict:
    """check verdict를 최고 severity로 병합. cert-mesh 팩이 CertMesh 로직대로 check 생성:
       regression -> blocked, improvement/uncertified-added -> needs_review, else certifiable.
       max-severity 병합이 CertMesh._decide_verdict를 정확히 재현."""
    worst = max(checks, key=lambda c: SEVERITY[c["verdict"]])
    return {"verdict": worst["verdict"], "worst": worst["check"], "checks": checks}
    # ★ 검증: cert-mesh 4케이스 verdict == 실제 CertMesh.certify (D:/IdeaFirst/certmesh) → PARITY OK
```

## 4. 완료 기준 (U3 게이트)

```text
G1 zero-kernel-change : cert-mesh 이후 release-mesh·robo-trace 추가에 커널 무수정 (3팩 0 errors)
G2 reference-parity   : cert-mesh == 실제 CertMesh.certify (4/4 케이스) → PARITY OK
G3 determinism-clean  : clean, 14 files
G4 tests-green        : 12 unittests OK
G5 structure-conform  : canonical -stra 구조 (core/packs/run/cli/tests/pgf/README/pyproject)
```
