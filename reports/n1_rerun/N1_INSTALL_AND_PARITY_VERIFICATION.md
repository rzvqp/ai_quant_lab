# N1 HANDOFF — Install Verification + Smoke Parity (Phase 1 of the canonical rerun)

**Division:** Alpha Discovery (Flow B) · **Date:** 2026-08-16 · **Authorization:** RT-N1-0001 `N1_HANDOFF_PASS`,
`ALPHA_CANONICAL_RERUN_AUTHORIZED` (Red Team commit `5352570`).

## Controlled install
- Service paused cleanly via temporary `PAUSED_BY_CEO`; log line `PAUSED_BY_CEO flag found — exiting cleanly`.
- **Pre-install watermarks:** m_total **357**, registry **355** records, registry_sha256 `801e18a5f4eedaf4d375a7eaa22527f98627caff618d1c33590f280ebd25b20c`, duplicate tombstones **16**.
- **SHA-256 verified BEFORE install (exact match):**
  - `ve_n1_replay-0.1.0-py3-none-any.whl` = `372b35f990153aa777cbbf16c05ba8e58b1c0a7dd800b78540bc7fc0ce0eb3f1` ✓ (authorized)
  - `ve_brain-0.1.3-py3-none-any.whl` = `edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11` ✓
- Installed into an **isolated venv** `C:\Users\MEDION GAMING\.alpha_n1_venv` (no rebuild; `--no-index` for ve_brain). ve_n1_replay pulled only `numpy>=1.24`.
- **Collision / bootstrap fail-closed (verified in-process):**
  - `ve_tower` NOT importable in the Alpha process ✓ (N1 must not pull the N3/N4 artifact)
  - the LIVE AI Trader repo is NOT imported — ve_n1_replay uses its **own hermetic vendored** `_ai/ai_trader` (the stray `ai_trader/` mirror inside the Alpha repo is never on the rerun's path; rerun runs from a neutral cwd)
- **Artifact pins read back from the installed wheel (all match the handoff):**
  `VE_N1_REPLAY_VERSION=0.1.0`, `N1_REPLAY_CONTRACT_VERSION=n1-replay-request-v1`, `AI_SOURCE_COMMIT=21ae632`,
  `DETECTOR_SUBMODULE_COMMIT=61cbd58c…`, `VE_BRAIN_VERSION=0.1.3`, `VE_BRAIN_WHEEL_SHA256=edd208ad…`,
  `ve_brain.N1_CONTRACT_VERSION=n1-additive-raw-axes-v1`, `ROUTER_VERSION=router-v1`, `RAW_AXIS_SCHEMA_VERSION=raw-axis-v1`.

## Smoke parity — **PASS** (`smoke_parity.py`, output `smoke_parity_output.json`)
Verified input sequences reconstructed byte-for-byte from the AI Trader conftest arrays (authoritative inputs);
the OFFICIAL engine produced the outputs (no invented outputs, no repo import).

| property | result |
|---|---|
| live (`observe_closed_bar`) == `replay()` | identical ✓ |
| TREND_UP (460 calm + BOS_BULL) | `applicable_regimes == {TREND_UP}`, `RawAxes(direction='up', structure='strong')` ✓ |
| TREND_DOWN (vertical mirror → BOS_BEAR) | `TREND_DOWN`, `RawAxes(direction='down', structure='strong')` ✓ |
| UNCERTAIN (calm prefix, no confirmed break) | `applicable_regimes == {UNCERTAIN}` ✓ |
| BREAKOUT/BOS | `RawAxes(structure='strong')` on the confirmed break ✓ |
| snapshot / restore | tail after restore == full replay tail ✓ |
| duplicate bar (same ts) | **idempotent** — `bars_observed` unchanged, identical fingerprint ✓ |
| out-of-order bar | `OutOfOrderBarError` (fail-closed) ✓ |

**Result pins on a live reading:** `n1_contract_version=n1-additive-raw-axes-v1`, `router_version=router-v1`,
`detector_configuration_fingerprint=effa0663b8a45bb5`.

**Conclusion:** the artifact is installed, isolated, and **correct** on the smoke set. Correctness is NOT the
blocker. See `N1_RERUN_FEASIBILITY_BLOCKER.md` for the performance blocker that prevents the full 355k-bar replay.
