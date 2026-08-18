# RED TEAM — `ve_n1_replay 0.2.0` RANGE_STATE FINAL HANDOFF REVALIDATION
### RT-RANGE-0002 · **RANGE_STATE_HANDOFF_PASS**
**Date:** 2026-08-18 · **Auditor:** Red Team · **Target:** `ve_n1_replay 0.2.0` — additive RANGE_STATE + longitudinal breakout events. Wheel `ve_n1_replay-0.2.0-py3-none-any.whl`, SHA-256 `04b96a8b78b2d09bd8b54bd8044058282c6ab24bf2ac0f2aaec6c1f7a278786f`, 82 884 bytes; build `1dc355b`, delivery `3577026`; sidecar `HANDOFF_MANIFEST-0.2.0.json` cites Statistician reconciled spec `aca7801`, m_inference-FINAL `d0d08c1` / manifest `v2.7.77` / config_hash `aec8f07`, Red-Team reachability `5e56396`. Baselines: N1 `ve_n1_replay 0.1.1` (RT-N1-0002 PASS), RANGE reachability finding RT-RANGE-0001 (`5e56396`, E76).

**Read-only. No VE engine or AI Trader code modified. Alpha not started; Alpha registry / `n_generated_total=357` / tombstones / existing verdicts untouched. LIVE_SHADOW, the Scheduled Task, and the broker were not stopped, restarted, or modified. No backtest / PnL / SEALED access / orders. Nothing changed outside `red_team/`.**

---

# VERDICT — **RANGE_STATE_HANDOFF_PASS**

Every decisive point passes, verified by **independently driving the public producer** (`RangeStateReplayEngine.observe_closed_bar` / `replay_batch`) with my own adversarial and boundary sequences — not by trusting the artifact's own assertions or its docstrings. N1 remains byte-identical to 0.1.1; RANGE_STATE is a genuinely additive layer; the state machine makes `BREAKOUT_ACCEPTED` and `FAILED_BREAKOUT` mutually exclusive on every adversarial sequence I could construct; the F7 `RANGE_MID_NO_ENTRY` guard is a real, audited, entry-refusing safety guard with its own counter and **no** p-value; causality is fail-closed; the ledger is deterministic; the new RANGE layer's memory is **bounded**; and 0.2.0 has **not** leaked into the live runtime or Alpha's env.

**This PASS authorizes ONLY:** Alpha may install `0.2.0` **in the Alpha environment** and prepare the next combined discovery wave (RANGE, the 44 previously-inaccessible breakout hypotheses, failed-breakout, sweep, TREND_DOWN/SHORT). **It does NOT authorize** AI-Trader deployment, final regression, cutover, `set_authority`, broker activation, or `order_send`.

---

## §1 — Delivery integrity · PASS
Wheel re-hashed this session: `sha256 = 04b96a8b78b2…786f`, `82884` bytes — **identical** to the declared SHA and byte-count and (prior window) to the git-stored bytes, the `.sha256` sidecar, and `SHA256SUMS.txt`; `local == remote` on all four mirrors was confirmed in the prior window. The sidecar `HANDOFF_MANIFEST-0.2.0.json` cites the Statistician normative set exactly: reconciled spec `aca7801`, m_inference-FINAL `d0d08c1`, manifest `v2.7.77`, config_hash `aec8f07`, reachability `5e56396`; `self_declared_pass=false`. Build `1dc355b`, delivery `3577026`.

## §2 — Delta 0.1.1→0.2.0 + N1 parity · PASS
Module-level diff: the **only** new files are `range_engine.py` and `range_state.py`; `__init__.py` / `version.py` differ (surface + version constants); **all 15 vendored `ai_trader` modules and all 5 detector modules, plus `_bootstrap.py` and `incremental.py`, are byte-identical to 0.1.1.** N1 output is byte-identical: on `trend_up / trend_down / uncertain / osc` fixtures the 0.2.0 N1 `output_fingerprint = 0ecaf5815604553c`, `eval_identity_fp = 64414829e2ea080b`, full digest `9c12d5bdaaca6f02` — **identical to 0.1.1**, and the N1 evaluation-identity versions stay **v1** (`n1-additive-raw-axes-v1 / router-v1 / raw-axis-v1 / n1-replay-contract-v1`). **No false semantic-change claim:** the sidecar's `*-v2` "_pkg" bumps are package-surface metadata for the new RANGE layer; the N1 engine's own identity is unchanged, consistent with the byte-identical fingerprints. RANGE_STATE reuses `StructBand.RANGE` in **no** way, forces **no** `applicable_regimes`, invents **no** `"range"` in RawAxes.

## §3 — RANGE_STATE conformance · PASS
Parameters are exactly the pre-registered ones (`RangeConfig`): `n_touch=2`, `tol_atr=0.25×ATR`, `er_max=0.40`, `n_acceptance=2`, `d_min` derived canonically (`BARS_PER_DAY_M15`; D1=96, H4=16), `width_filter=None (off)`, `precedence_rule="RANGE_STATE_OVER_TREND_PAUSE"`, `swing_k=2`, `atr_window=14`. ER is the exact `|Δclose_net| / Σ|Δclose|`. `structural_start_ts` is retrospective; the only execution timestamps are `actionable_start_ts = confirm_ts = structural + k`. Boundaries derive from the **canonical swing stream**: `test_confirmed_swing_stream_matches_detect_swings` shows the producer's confirmed-swing stream equals the ratified `detect_swings` oracle bar-for-bar. No invented trendline detector; a missing primitive yields refusal, not a substitute.

## §4 — Reachability + event machine (DECISIVE) · PASS — independently verified
Driving the **public** producer with my own bar sequences (`rt_range_indep.py`, 31/31 checks):
- **All 8 event kinds** (`RANGE_LOW/HIGH_REJECTION`, `RANGE_MID`, `BREAKOUT_CANDIDATE/ACCEPTED/RETEST`, `FAILED_BREAKOUT`, `LIQUIDITY_SWEEP_REVERSAL`) **and RANGE_STATE ESTABLISHED are reachable** through the producer — no injected results, no producer bypass.
- **DECISIVE mutual exclusivity:** across **10 adversarial / boundary tails** — exactly-N=2 accept, N−1-then-back-inside fail, close **exactly at** the boundary, one-beyond-then-at-boundary, wick-through-close-inside repeated, beyond→far-back→beyond (multi-candidate), flip-flop at the boundary, gap far beyond, and lower-side break accept & fail — **no single bar ever emitted both `BREAKOUT_ACCEPTED` and `FAILED_BREAKOUT`.** The accept tail reaches ACCEPTED and never FAILED; the fail tail reaches FAILED and never ACCEPTED. Mutual exclusivity is a property of the `CANDIDATE → {ACCEPTED xor FAILED}` state machine (`n_acceptance=2`, expiry `n_acceptance+1`), not of a fixture.

## §5 — F7 `RANGE_MID_NO_ENTRY` SAFETY_GUARD · PASS — independently verified
On the oscillation fixture the producer emitted **63 `RANGE_MID` events**; for **every one**, `entry_decision(event).permitted == False` with `guard = SAFETY_GUARD_RANGE_MID_NO_ENTRY`. RANGE_MID **never** coincides with a `BREAKOUT_CANDIDATE` on the same bar (it is a guard, never a strategy/entry). In the ledger the guard is **explicit, not deduced**: `n_guards == 63` (its own counter, separate from any p-value family) and 63 records carry the `safety_guard` tag. The artifact's `test_guard_persists_after_snapshot_restart` confirms the guard survives snapshot/restart. F7 is registered in `SAFETY_GUARDS_REGISTER`; the p-value family is F1–F6 (six hypotheses, m_inference=26). No entry / candidate / p-value / broker reach anywhere on the RANGE_MID path.

## §6 — Causality / zero-lookahead · PASS — independently verified
- **Zero lookahead:** the 70-bar prefix run is identical (fingerprints, states, events) to the first 70 bars of the full run — future bars do not change emitted results.
- **Chunk invariance:** replay in `[116] / [1,115] / [50,66] / [95,1,20]` splits with `snapshot()→restore()` between chunks reproduces the continuous run exactly.
- **Snapshot/restart in every machine state** (artifact `test_snapshot_restart_in_every_machine_state`): identical continuation from every cut through FORMING/ESTABLISHED/CANDIDATE/ACCEPTED/RETEST.
- **Fail-closed identity:** restoring a snapshot into an engine with a different config raises `RangeSnapshotError` (no incomplete-history fallback). Two instances share no state.

## §7 — Ledger / identity / multiplicity · PASS — independently verified
`run_hash` is deterministic (two identical `replay_batch` runs agree) and **changes** when the data changes or the config changes (`tol_atr` 0.25→0.50). `run_hash = config_hash ‖ data_identity ‖ range_spec_id`; the ledger header carries `range_spec_id / config_hash / data_identity / occupancy / n_guards`. F7 sits **outside** the p-value family (`n_guards` is a plain counter). I did **not** touch the Alpha ledger, `n_generated_total=357`, tombstones, or any existing verdict.

## §8 — Installed tests + complexity + memory · PASS — independently verified
- **77 tests pass** (18 `n1_replay` + 15 `incremental` + 27 `range_state`, parametrized to 77) resolved from the **installed wheel** (`site-packages/ve_n1_replay`), not from source.
- **mypy `--strict` → exit 0** on `range_state.py` and `range_engine.py` (the lone note is the venv's own `typing_extensions.py` shadowing — an environment artifact, not a package error).
- **Complexity O(n):** 10 k / 20 k / 40 k bars → 53.0 / 109.2 / 219.4 s (2.06× and 2.01× per doubling; per-bar constant ≈ 5.5 ms). On this **worst-case max-event** synthetic (an event almost every bar), 355 696 bars extrapolate to **≈ 32 min ≪ 4 h**. Real M15 data emits far fewer events.
- **Bounded RANGE memory:** the producer's tick buffers are `deque(maxlen=2k+1)`; the confirmed-swing streams are pruned (`popleft` when `idx < lo`) and bounded further by `max_duration` invalidation. Splitting the combined snapshot under canonical-style config (`max_duration_bars=96`, ranges that break): **N1 component** grows 44 647→181 593 B (1.44× — the *intentional, ratified* unbounded structural memory, RT-N1-0003 §4, required by §6), while the **RANGE component plateaus at ≈ 5 772 B (ratio 1.000) → BOUNDED.** All combined growth is attributable to the ratified N1 memory; the new layer does not grow with history.
- Wheels `0.1.0 / 0.1.1 / 0.2.0` all physically present for rollback; no benchmark process left running.

## §9 — Isolation · PASS — independently verified
No **executable** `MetaTrader5 / mt5 / order_send / set_authority / probability_inputs / ve_tower / N3 / N4 / N6 / EV` import exists in the installed source — every token hit is a comment/docstring prohibition or a vendored enum *value* (`SEALED = "SEALED"` in `strategy_manager/contract.py`). The only external dependency is `ve_brain` (+ stdlib); `numpy` appears only in the vendored `_det/market_state.py` (legitimate detector dep). `range_state.py` / `range_engine.py` import only stdlib + internal modules. `ve_n1_replay` is **not importable** in the AI-Trader live venv or `ve_tower_venv`; `0.2.0` lives **only** in my isolated `rt_n1v20_venv`.

## §10 — LIVE_SHADOW · PASS (read-only)
`AITraderLiveShadow` Scheduled Task: **State = Running**, LastRun `2026-08-17 23:12:37`, LastResult `267009` (`0x41301` = SCHED_S_TASK_RUNNING) — unchanged; I did not stop/start/modify it. Live process PIDs **22592** (AI-Trader venv) + **25992** started `23:12:37` under HEAD `255eee6` — the **old** runtime, **before** 0.2.0. `ve_n1_replay` is **not installed** in the live venv (0.2.0 is **not** in the runtime); Alpha's `.alpha_n1_venv` still holds the ratified **0.1.1** (0.2.0 not yet installed — correct, this PASS had not been acted on). The live `xauusd_m15.db-wal` was updated today `10:43` → the process is alive and processing M15 normally. I ran no orders and disturbed no live state.

---

## What I re-verified independently vs. did not run
- **Independently driven through the public API this session:** §2 N1 parity fingerprints; §4 reachability + DECISIVE mutual exclusivity (10 adversarial tails); §5 F7 runtime (63 guards, entry refusal, ledger counter); §6 lookahead/chunk/fail-closed restore; §7 run_hash determinism + sensitivity; §8 77 installed tests, mypy, O(n) scaling, bounded-memory split; §9 import isolation; §1 SHA re-hash; §10 task/process/venv state (read-only).
- **Relied on the artifact's own passing tests** (which drive the producer, not inject) for: snapshot/restart in *every* machine state, and the swing-stream = `detect_swings` oracle parity.
- **Verified in the prior window (not re-run here):** git-stored wheel bytes, `.sha256` sidecar, `SHA256SUMS.txt`, and `local == remote` on all four mirrors.
- **NOT run:** the full 355 696-bar end-to-end benchmark (I ran O(n) checkpoints at 10 k/20 k/40 k that extrapolate to ≈ 32 min); any backtest / PnL / SEALED / real order; any Alpha execution.

## AUTHORIZATION (on PASS)
Authorized **only**: (1) Alpha installs `ve_n1_replay 0.2.0` **in the Alpha environment**; (2) Alpha prepares the next combined discovery wave (RANGE, 44 breakout hypotheses, failed-breakout, sweep, TREND_DOWN/SHORT). **NOT authorized:** AI-Trader deployment, final regression, cutover, `set_authority`, broker activation, `order_send`. LIVE_SHADOW continues on the old runtime untouched; broker DISABLED; authority NEW_BRAIN. Red Team modified no VE engine or AI-Trader code, ran no orders, disturbed no live process, and changed nothing outside `red_team/`.
