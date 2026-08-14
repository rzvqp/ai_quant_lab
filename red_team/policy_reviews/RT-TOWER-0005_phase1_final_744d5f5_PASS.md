# RED TEAM — PHASE-1 FINAL REVALIDATION · tower worker pin closure @ `744d5f5`
### RT-TOWER-0005 · **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
**Date:** 2026-08-14 · **Auditor:** Red Team · **Task:** final Phase-1 revalidation after AI Trader's pin-closure report; sidecar `12f9241` is the authoritative source (RT-TOWER-0004 / `ccb50c5`). **No engine modified; no real data.** Verified against the sidecar, `git rev-parse`, the worker + client test suites, and independent reproduction of the handshake defenses.

# VERDICT — **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
All five checks pass. The `ve_tower` 0.3.0 artifact (already PASS on all material points, RT-TOWER-0002/0003) plus the isolated worker + identity handshake are sound; my RT-TOWER-0003 findings (fake-server accepted, unbounded cache, loopback not enforced) are **fixed and re-verified**. The pin's three `None` fields are the exact values I verified and deliver below — recording them completes the pin during the staged install. **STAGED_INSTALL is authorized automatically**: AI Trader installs `ve_tower 0.3.0` **only** in the separate tower venv and begins N3/N4 wiring. **LIVE_SHADOW stays forbidden; authority stays inactive; Alpha stays PAUSED.**

## 1 · Pin vs sidecar `12f9241`
The pin's non-`None` expected fields all equal the authoritative sidecar: `ve_tower_package_version=0.3.0`, `package_build_commit=6daf2aa`, `state_delivery_commit=0207ffa` (correctly separate), `wheel_sha256=0c2581c068f3bd7d0c5beff1358af0aa906485d69ed74bf66c8a6d8d0c0120d2`. The three PENDING fields are `None` and `verify_pin` **fails closed** on them (correct — never fabricated; awaiting my delivery).

## 2 · The three values — RECOMPUTED, not accepted on declaration
- **`vendored_source_identity` = `sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c`** — independently recomputed from the 13 git blob identities via the manifest's documented algorithm (sort `(name, git_blob_sha1)` by name → `"name sha1"` lines → join `\n` + trailing `\n` → `"sha256:"+sha256`), against blobs re-fetched with `git rev-parse` (RT-TOWER-0004, re-affirmed). Exact match.
- **`n3_contract_version` = `tower-n3-request-v2`**, **`n4_contract_version` = `tower-n4-request-v2`** — match `version.py` @ `6daf2aa` and the sidecar.

## 3 · Commit matrix — unambiguous, self-reference fixed
No two commits carry the same identity name. The prior `WORKER_BUILD_COMMIT = "88857ba…"` hardcoded constant is **deleted**; `worker_delivery_commit` is now written by the installer (`install_tower_env.ps1` → `git rev-parse HEAD`, refusing to run on any uncommitted `tower_worker/` change) and only **read** by `artifact_identity.py`. The report's matrix disambiguates the terminology: `worker_validated_core_commit=88857ba` (the handshake/cache/loopback implementation I substantively reviewed), the prior `4d01fb2` relabeled, going-forward delivery commit installer-written. The only hardcoded hashes in the worker/pin are `6daf2aa` (build) and `0207ffa` (state-delivery) — correctly separated `ve_tower` identities, not worker identities.

## 4 · Handshake does NOT rely on the documentary field
`verify_pin` now checks **all nine** `WorkerIdentity` fields. **Exact-match** (the proof it runs the right code): `wheel_sha256`, `package_build_commit`, `ve_tower_package_version`, `vendored_source_identity`, `n3/n4_contract_version`, `worker_package_version`, `protocol_version` — plus an **HMAC-SHA256 challenge-response** session proof. **Presence-only:** `worker_delivery_commit` (can't be exact-matched without re-creating the self-reference bug; the meaningful check is "not `None`", proving it is installer-manifest-backed). So the running-code proof is the **artifact hash + build commit + ve_tower version + vendored_source_identity + HMAC**, never the documentary `worker_delivery_commit`.

## 5 · Re-executed attacks — all defended (worker 32 + client 56 tests pass)
`PROTOCOL_VERSION=2.0`; the launcher exchanges an HMAC shared secret; the client verifies session identity on every response. Reason codes confirm the defenses: `HANDSHAKE_HMAC_MISMATCH`, `HANDSHAKE_IDENTITY_MISMATCH`, `HANDSHAKE_SESSION_ID_MISMATCH`, `HANDSHAKE_NOT_ESTABLISHED`, `RESPONSE_IDENTITY_MISMATCH`, `STALE_RESPONSE`, `STALE_SESSION`.
- **fake server** (no HMAC secret) → **rejected** (`HANDSHAKE_HMAC_MISMATCH`) — the RT-TOWER-0003 gap I demonstrated is closed; a responder that doesn't know the secret can't match regardless of how plausible its claimed fields look (`test_tower_launcher::test_1`).
- **wrong wheel / wrong contract / old ve_tower version** → pin mismatch (`test_tower_identity_pin`).
- **other session / response from an old session (after restart)** → `STALE_SESSION` (`test_tower_isolation`, real sequential subprocesses).
- **port occupied** → worker `bind()` fails → `TOWER_WORKER_STARTUP_FAILED`; the launcher never handshakes against the occupier.
- **cache bound + TTL + request-id reuse** → `tower_cache.py` (bounded, TTL) — `test_tower_cache` passes.
- **non-loopback bind** → rejected; **crash/restart** → fail-closed.
Worker suite **32 passed**; client tower suites **56 passed**; isolation **8 passed** (the one failure was my own partial-extraction artifact — a missing `ai_trader.structural_observer` in my sandbox, not a defect).

## EXACT VALUES → AI Trader (to record in `tower_identity_pin.py` at install)
```
EXPECTED_VENDORED_SOURCE_IDENTITY = "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"
EXPECTED_N3_CONTRACT_VERSION      = "tower-n3-request-v2"
EXPECTED_N4_CONTRACT_VERSION      = "tower-n4-request-v2"
```
(the worker side's `install_manifest` must carry the same three, sourced from sidecar `12f9241`, so `verify_pin` matches.)

## VERDICT — **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
Automatic, no further CEO approval. **AI Trader may now:** record the three values above into the pin; install **exactly** `ve_tower-0.3.0-py3-none-any.whl` (SHA-256 `0c2581c0…20d2`) **only** in the separate tower venv (verify_tower_wheel pin = this SHA); begin N3/N4 wiring through the isolated worker over the loopback IPC. **Still forbidden:** LIVE_SHADOW start, authority activation (`set_authority` stays uncalled), Alpha (PAUSED), CAND-T05 (frozen). Phase 2 (the real IPC→worker→N3→N4→Router→EV→N6→Risk→broker-BLOCKED path) is the next, separate review before any `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2`.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
