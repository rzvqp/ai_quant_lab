# RED TEAM — TOWER HANDOFF (re-validation) · `ve_tower-0.2.0` (build `bdbeeb6`)
### RT-TOWER-0002 · FAIL points re-verified + the real-environment collision (point 5)
**Date:** 2026-08-14 · **Auditor:** Red Team · **Task:** re-verify `ve_tower 0.2.0` (all `TOWER_HANDOFF_FAIL` points closed) and decide the integration form. **No engine modified; no real data.** Verified on the wheel installed into a clean venv on the **AI Trader stack** (Python 3.14.6, numpy 2.5.1, pandas 3.0.3), external git-blob verification, and the reproduced production collision.

# VERDICT — **TOWER_HANDOFF_CONDITIONAL**
**Every prior FAIL point is genuinely closed** — the decision logic, data-identity, and byte-identity are correct, and all 14 attacks pass. **But two real integration findings block a clean PASS:** (1) the bare-name collision is **confirmed in the production config** — `ve_tower` **cannot run in the same venv** as the 5 live processes (it fail-closes on `run_n3`), so the same-venv integration form is unsafe/non-functional; (2) the bootstrap's mid-order cleanup is **incomplete** — on a collision it leaves the already-loaded vendored module (`level_output`) in `sys.modules`, contradicting its "zero partially-loaded modules" guarantee (benign today, latent risk). **The fail-closed guard itself HOLDS** — it does not silently shadow the host. PASS is conditioned on the safe integration form + the cleanup fix.

## THE FAIL POINTS — genuinely CLOSED
- **Point 13 (data substitution) — FIXED, 14 attacks pass (installed wheel):** N3 strict **M15** / N4 strict **M5** (`M5`/`BANANA`/`M15` → `invalid_timeframe`); `event_fingerprint` shared N3↔N4 (timeframe excluded — the correct design preserved); **`node_input_fingerprint` per node binds to `data_identity.bars_content_hash`** → **same `(id,symbol,as_of)` + different M15 bars → same event_fingerprint but DIFFERENT node fingerprint** (substitution now detectable); identical input → identical hash; one OHLC/ATR/timestamp change → different hash; N4↔N3 link enforced (`n3_link_mismatch`); `NaN/Inf` → `non_finite_value`; missing source → `source_identity_missing`; future/open bar → `bars_not_closed_or_ordered`.
- **Point 2/4 (byte-identity) — FIXED, externally verified:** all 13 recorded `VENDORED_BLOB_SHA1` **equal `git rev-parse <commit>:code/<mod>.py`**, and each **wheel** `_tower/*.py` git-blob-hashes to the same value — **byte-identical to the ratified heads** (the 0.1.0 EOL issue is fixed via `.gitattributes -text` + re-extract-from-blob). The check is now **external** (git), not self-referential. `zone_map@5888978`, `zone_confirmation@7f2694f` confirmed.
- **Canonical hash — sound:** timestamps as decimal strings, dicts key-sorted, floats as IEEE-754 hex (`struct.pack(">d")`, no `repr()`), type tags (int≠float≠bool), NaN/Inf refused. Deterministic.
- **Contracts / no-lookahead / unavailability / independence:** contract-version + `assert_n*_compatible` + `INCOMPATIBLE_CONTRACT`; strict-ascending, all `≤ as_of`; explicit reason codes never fabricated; no `market_intelligence`/`ai_trader` import.
- **Point 1:** SHA-256 `3ea791bad054f9356bb82a35b59646a0ffa619132e39af601b975179cc2e91a8` + 76,258 bytes exact; content == `bdbeeb6`.

## POINT 5 (decisive) — the production collision, reproduced
Reproduced the real config: the 9 host bare names (`market_state`, `market_structure`, `order_flow`, `institutional_levels`, `imbalance_mechanics`, `interactions`, `pdh_pdl_demo_engine`, `session_levels`, `order_block_void`) pre-loaded in `sys.modules`, then `import ve_tower` + trigger N3:
- **`import ve_tower` does NOT load the vendored modules** (lazy) — merely importing is safe. ✅
- **Fail-closed HOLDS:** `ensure_tower_loaded()` → `TowerLoadCollisionError` on `market_state` (#2 in load order); **all 9 host modules remain intact** — **no silent shadowing.** ✅ *(This is the good outcome the CEO asked about — the guard does not shadow tacitly.)*
- **But `ve_tower` cannot function there:** it fail-closes on the very first `run_n3`, so N3/N4 can never produce a map in the shared process. **The same-venv form is non-functional.**
- **Contamination residue (cleanup bug):** `level_output` (#1, loaded before the `market_state` #2 collision) is **left in `sys.modules`** after the fail-closed error — the mid-order cleanup only pops a module whose **exec** fails, not modules loaded **before** a collision. **Benign today** (`c40d338` == HEAD `level_output` — identical blob, so a later host `import level_output` gets identical code), but it **violates the stated "zero partially-loaded modules"** guarantee and becomes a real substitution if the host's copy ever drifts from the vendored ratified one.
- **Runtime versions:** the 14 attacks all ran on **numpy 2.5.1 / pandas 3.0.3 / Python 3.14.6** (the AI Trader stack, not VE's 2.5.2/3.0.5) — `requires-python ≥3.12` is satisfied by 3.14; numpy/pandas within range. ✅ Version compat is fine; the collision is the only environment issue.
- **Concurrency (point 4):** `ensure_tower_loaded` is a double-checked `threading.Lock` — concurrent import is safe.

## POINT 6 — the three integration forms (my comparison, as the CEO requested)
| form | verdict | why |
|---|---|---|
| **1 — separate venv + versioned IPC** | ✅ **SAFE (required)** | ve_tower's 13 bare names live only in its own process; the 5 live processes' bare names never collide. Different Python/dep profile is isolated. N3/N4 responses cross via versioned IPC. |
| **2 — same venv (pure-python co-install)** | ❌ **UNSAFE — prohibited** | **confirmed collision:** `market_state`/`market_structure`/`order_flow` (+4 more of the 13 vendored) are already-imported bare in the live processes → ve_tower fail-closes on `run_n3` (non-functional) **and** leaves the `level_output` residue. |
| **3 — hybrid, isolated to `new_brain_bridge`** | ⚠ **safe ONLY as a separate process** | if `new_brain_bridge` runs **in-process** with the live processes, the same collision applies (unsafe). Safe only if it is a **separate OS process** — i.e., form 1. |
**Recommendation: form 1 (separate venv + versioned IPC).** Form 2 must not be used.

## VERDICT — **TOWER_HANDOFF_CONDITIONAL** · Mandate B not yet reactivated
The artifact's decision logic, data-identity, byte-identity, canonical hash, and fail-closed guard are all correct — every prior FAIL is closed and the 14 attacks pass on the real stack. **PASS is conditioned on:**
1. **Integration = a separate venv/process (form 1).** The same-venv form (2) is **prohibited** — the bare-name collision is confirmed and makes ve_tower non-functional + contaminating in the shared process.
2. **Fix the mid-order cleanup:** on a collision (or any failure) in `ensure_tower_loaded`, roll back **all** vendored modules loaded in that call (currently leaks `level_output`), and restate the "zero partially-loaded modules" guarantee to match.

Meet those and re-submit the integration plan; I re-verify the collision path under form 1 and the cleanup. **Only then does Mandate B reactivate for installation.** (Documentary, non-blocking now: point 15 — AI Trader's 22/25 vs `04/05/09/20b` register, and the 6 skipped + 4 warnings — to be reconciled before `PASS_FOR_LIVE_SHADOW`.) Alpha remains PAUSED; CAND-T05 frozen.

## HANDOFF → CEO / VE / AI Trader
1. **Adopt integration form 1** (separate venv + versioned IPC); prohibit same-venv co-install.
2. **VE:** full rollback on mid-order bootstrap failure (not just exec-failure of one module).
3. On confirmation, I re-verify and the tower passes for installation under form 1.

Red Team modified no engine, ran no data on the market, changed nothing outside `red_team/`.
