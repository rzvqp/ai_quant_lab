# RED TEAM — PHASE-1 FINAL REVALIDATION · delivery `d1a971a`
### RT-TOWER-0006 · **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
**Date:** 2026-08-14 · **Auditor:** Red Team · **Target:** AI Trader `READY_FOR_TOWER_PHASE1_REVALIDATION_FINAL` @ `d1a971a` (the pin is now filled from the verified sidecar; new `sidecar_verification.py`). Authoritative source: `HANDOFF_MANIFEST-0.3.0.json` @ `12f9241` / `TOWER_METADATA_PASS` @ `ccb50c5`. **No engine modified; no real data.** `ve_tower` remains UNINSTALLED in the AI Trader env; `bridge.py` remains UNCONNECTED.

# VERDICT — **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
Verified at `d1a971a` (not prior versions). All five checks pass; no reproducible decision-path violation. The pin is now **complete** (the three `None`s filled with my verified values), the new sidecar verifier **recomputes** rather than copies, the commit matrix is unambiguous, and every handshake attack is defended in the **real code**. Authorization is automatic.

## 1 · Sidecar & pin — filled, recomputed, fail-closed
The pin's `EXPECTED_*` no longer contains `None`: `EXPECTED_VENDORED_SOURCE_IDENTITY = "sha256:4c0deecbec7afc74b1fc7f61898ad10e54b63d3b7c5cad63b80ee8c647a69e1c"`, `EXPECTED_N3_CONTRACT_VERSION = "tower-n3-request-v2"`, `EXPECTED_N4_CONTRACT_VERSION = "tower-n4-request-v2"` — exactly the values I verified.
- **Independent git-anchored recompute:** aggregating the 13 blobs re-fetched via `git rev-parse <source_commit>:code/<mod>.py`, through the documented algorithm, yields `sha256:4c0dee…69e1c` == the pinned value.
- **Fail-closed per field (verified):** flipping any of `vendored_source_identity`, `n3_contract_version`, `n4_contract_version`, `wheel_sha256`, `package_build_commit` → `verify_pin` reports a mismatch on that field. `worker_delivery_commit` is presence-only (any non-null passes; `None` fails).

## 2 · Worker commit matrix — one meaning per identity, no self-reference
Linear chain, all confirmed via git (`d1a971a` descends from `88857ba`):
| commit | meaning |
|---|---|
| `88857ba` | `worker_validated_core_commit` — the handshake/cache/loopback IMPLEMENTATION I reviewed |
| `4d01fb2` | the SUPERSEDED hardcoded-`WORKER_BUILD_COMMIT` approach (now deleted) |
| `0839307` | installer manifest-writer fix |
| `744d5f5` | pin-closure report update |
| `7747c4b` | fill the pin from the verified sidecar; `worker_delivery_commit` captured here by the installer |
| `d1a971a` | record the final identity matrix |
**`artifact_identity.py` @ `d1a971a` contains no hardcoded commit hash** (grep-verified) — the self-referential constant is gone; `worker_delivery_commit` is installer-written (`git rev-parse HEAD`, refusing on any uncommitted `tower_worker/` change) and only read. **`worker_delivery_commit` stays documentary (presence-only); the handshake does NOT use it as security proof** — the real proof is the exact identities (`wheel_sha256`, `package_build_commit`, `ve_tower_package_version`, `vendored_source_identity`, contracts, `worker_package_version`, `protocol_version`) **plus the HMAC-SHA256 session proof**. Point 4 satisfied: an installer-written field is never the proof-of-correct-code (that would be circular).

## 3 · `sidecar_verification.py` — recomputes, refuses, no copied value (verified IN CODE)
Ran the real module against the real sidecar → `SIDECAR_VERIFIED_OK`. Verified by construction and by tampering:
- **Recomputes, never copies:** `vendored_source_identity` is recomputed from the 13 declared blobs and compared to the declared string; the returned `VerifiedSidecar.vendored_source_identity` is the **recomputed** value. Changing **only** the declared identity → REFUSED (recompute mismatch); changing **one blob** (identity untouched) → REFUSED (recompute mismatch) — so it cannot confirm itself.
- **Refuses incomplete/modified:** dropped blob (12≠13) → REFUSED; wrong `manifest_schema_version` → REFUSED; `n3`/`n4` request≠response → REFUSED; missing/empty required field → REFUSED.
- **`artifact_fingerprint`** is read for the record, **never compared, never gates anything, never a pin constant** — consistent with my RT-TOWER-0004 finding.
(The git-anchor of the 13 blobs is Red Team's independent verification — done above; the pinned aggregate is my git-anchored value, so the full chain is anchored outside the sidecar.)

## 4 · Attacks re-executed from the REAL code (`PROTOCOL_VERSION=2.0`)
Launcher exchanges an HMAC shared secret; the client verifies session identity on every response. Reason codes: `HANDSHAKE_HMAC_MISMATCH`, `HANDSHAKE_IDENTITY_MISMATCH`, `HANDSHAKE_SESSION_ID_MISMATCH`, `HANDSHAKE_NOT_ESTABLISHED`, `RESPONSE_IDENTITY_MISMATCH`, `STALE_RESPONSE`, `STALE_SESSION`.
- **fake server** (no secret) → `HANDSHAKE_HMAC_MISMATCH` (the RT-TOWER-0003 gap I demonstrated is closed).
- **wrong wheel hash / wrong vendored identity / wrong N3 / wrong N4** → `verify_pin` mismatch (reproduced above).
- **other session_id / response from an old session (after restart)** → `STALE_SESSION`.
- **port occupied** → worker `bind()` fails → `TOWER_WORKER_STARTUP_FAILED`; no handshake against the occupier.
- **cache bound / TTL / request-id reuse with different payload** → `tower_cache.py`.
- **bind `0.0.0.0` / non-loopback** → rejected; **crash / restart / missing field / `None`** → fail-closed.

## 5 · Tests & isolation — independently confirmed
- **Worker suite: 32 passed.** **Client tower + sidecar suites: 74 passed.** (My prior isolation "failure" was a sandbox extraction artifact — a missing `ai_trader.structural_observer` — not a defect.)
- **`bridge.py` still hardcodes `market_map_available=False, levels_available=False, confirmation_available=False`** — UNCONNECTED.
- **`set_authority` is never called** (the only match is the comment stating exactly that) — authority INACTIVE.
- **`ve_tower` remains UNINSTALLED in the AI Trader environment** (the worker's `artifact_identity` fail-closes to `None`; AI Trader's isolation report confirms; the "0.3.0 installed" I see is my own throwaway sandbox venv, not AI Trader's).
- **LIVE_SHADOW not started.**

## VERDICT — **TOWER_ARTIFACT_PASS · STAGED_INSTALL_AUTHORIZED**
Automatic, no further CEO approval. **AI Trader may now, in sequence:** (1) install exactly `ve_tower-0.3.0-py3-none-any.whl` (`0c2581c0…20d2`) **only** in the separate tower venv; (2) verify the installed distribution; (3) start the real worker; (4) wire N3/N4 through the loopback IPC; (5) remove the three hardcoded `False` values in `bridge.py`; (6) close the tests blocked on the tower; (7) deliver `READY_FOR_LIVE_SHADOW_REVIEW_CANDIDATE_V2`. **Still forbidden:** LIVE_SHADOW start, authority activation (`set_authority` stays uncalled); **Alpha PAUSED, CAND-T05 frozen.** Phase 2 (the real IPC→worker→N3→N4→Router→EV→N6→Risk→broker-BLOCKED path) is the next, separate review.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
