# RED TEAM — N1 INCREMENTAL REPLAY · revalidation of ve_n1_replay 0.1.1
### RT-N1-0002 · **N1_INCREMENTAL_PASS**
**Date:** 2026-08-18 · **Auditor:** Red Team · **Target:** `ve_n1_replay 0.1.1`, wheel `ve_n1_replay-0.1.1-py3-none-any.whl` SHA-256 `2cff7e7b…d29ab` (68,937 bytes), build `07da208`, delivery/state `e118c33`, sidecar `HANDOFF_MANIFEST-0.1.1.json`. Supersedes 0.1.0 (RT-N1-0001 PASS). **LIVE_SHADOW untouched (read-only); broker DISABLED; Alpha did not run the 355 hypotheses.** No VE engine modified; SYNTHETIC data; nothing changed outside `red_team/`.

# VERDICT — **N1_INCREMENTAL_PASS**
0.1.1 replaces the O(n²) per-bar recompute with an incremental O(n)/bounded-amortized engine that is **byte-identical per-bar to 0.1.0** and — decisively — **preserves the unbounded structural state (swings/breaks) across snapshot + restart**, so a break older than 5,000 bars is retained (`structure=strong`/`direction=up`), not lost to `UNCERTAIN`. This resolves the `N1_HYDRATION_CONDITIONAL` blocker (RT-N1-0001 §C / RT-TIME-0001 §C). Independent 355,696-bar benchmark: **18.8 min, linear**.

---

## §1 — Artefact identity · PASS
Wheel SHA-256 `2cff7e7b…d29ab` and **68,937 bytes** exact; **git-stored bytes == working wheel**; build `07da208` ("incremental O(n²)→O(n), byte-identical to 0.1.0"), delivery/state `e118c33`. Sidecar: package `0.1.1`, `supersedes 0.1.0`, `self_declared_pass: false` (VE leaves the verdict to Red Team), ve_brain 0.1.3 wheel SHA `edd208ad…` (unchanged), contracts/router/detector_config_fingerprint unchanged, **`vendored_source_identity` unchanged `sha256:1d4f6c48…`**, plus an `incremental` block declaring `history_horizon=460`, ledger/snapshot schema versions, and the horizon derivation ("structure/direction maintained by incremental swing/break state, NOT truncated").

## §2 — Byte-integrity of the closure + installed-wheel tests · PASS
Module diff 0.1.0→0.1.1: **NEW `incremental.py`**; DIFFER `__init__.py`/`version.py`; **all 15 vendored AI modules + 5 detectors + `_bootstrap.py` byte-identical to 0.1.0** (market_structure still `52bb1eba`, not ve_tower's `d734ac9a`) — the vendored closure and `vendored_source_identity` are unchanged. Installed into an **empty venv** (copied whitelisted numpy + pinned `ve_brain 0.1.3` + the 0.1.1 wheel); `ve_n1_replay.__file__` resolves to **site-packages**, and the artefact's tests were run against the **installed wheel from a neutral directory (not local source)**: **43 passed** (18 original + the incremental suite).

## §3 — Parity with 0.1.0 · PASS
On a 1,038-bar history whose confirming break is **560 bars old (beyond the 460 bounded window)**, the incremental engine (`N1IncrementalReplayEngine`) and the original oracle (`N1ReplayEngine`, byte-identical to 0.1.0) produce **byte-identical results for every bar** — `RawAxes` (`is_compressed`/`is_displacement`/`direction`/`structure`), `applicable_regimes`, Router `eligibility_decisions`/`reason_codes`, `availability_status`, `input_data_identity`, and all fingerprints (`n1_output_fingerprint`, `router_output_fingerprint`, `output_fingerprint`): **0 mismatches**. (Design corroboration: the incremental engine inherits `_build_result`/identity/snapshot and only swaps `_axes_builder`; bounded axes use a rolling 460-bar deque with the ratified functions unmodified, and structure/direction replay the exact `detect_swings`/`label_structure`/`detect_breaks` logic O(1) amortised.)

## §4 — Adversarial: >5,000-bar break survives snapshot + restart · PASS (decisive)
On a history with a real break followed by **5,300 calm bars** (break age = 5,300 > 5,000): the incremental engine's final reading is **`structure=strong`, `direction=up`, `applicable_regimes={TREND_UP, COMPRESSION}` — NOT `UNCERTAIN`**. Snapshotting after break+300 bars, restoring into a fresh engine, and continuing the remaining ~5,000 bars yields a continuation **identical** to the never-restarted run, and the restored engine's final structure still carries the >5,000-bar-old break. This is exactly the failure mode the 0.1.0 bounded-snapshot blocker exhibited (bounded restore → `UNCERTAIN`); 0.1.1 does not lose it.

## §5 — Snapshot preserves unbounded structural state · PASS
`IncrementalRawAxesBuilder.snapshot_state()` persists the full structural state — `last_high`/`last_low`, the swing stacks `{HH, LL, HL, LH}`, the `consumed` set, the `pending` swing, and `latest_break_kind` — **not** merely the last 460 bars. Confirmed empirically: after a >5,000-bar gap the restored engine reproduces the continuous run's structure exactly (§4). The bounded 460-bar buffer is used only for the genuinely bounded axes (compression ≤460, displacement ≤15, ATR14=14).

## §6 — Zero lookahead · chunk invariance · determinism · isolation · PASS
Zero lookahead (the first N results are identical whether or not later bars exist); **chunk invariance** (replaying in arbitrary chunks with a snapshot→restore between each chunk equals the monolithic replay); restart determinism (two independent runs identical); two engine instances share no state.

## §7 — Ledger / identity invalidation · PASS
The evaluation identity fingerprint changes on any change to `implementation_commit`, `symbol`, or `timeframe`; a snapshot taken under one identity is **refused** (`IncompatibleSnapshotError`) when restored into an engine with a different identity — so a change of data-context/contract/Router/detector/version invalidates the ledger rather than silently comparing across different configurations.

## §8 — Independent benchmark (355,696 bars) · PASS
Ran the incremental engine over **355,696** bars from the installed wheel: **1,128.8 s = 18.8 min** (well under the 4-hour target). Per-bar cost was flat across the run — 3.115 / 3.157 / 3.158 / 3.160 / 3.170 / 3.171 / 3.174 ms/bar at 50k/100k/150k/200k/250k/300k/355,696 — a **+1.9% drift over a 7× data increase = O(n)** (an O(n²) engine would have risen to ~22 ms/bar). The ~2-min difference from VE's ~16.9 min is background CPU (the live shadow + tower worker + a light Alpha discovery service were running); still far under 4h. (Per the mandate I checked for a lingering "Parity + timing >5000-bar" task before benchmarking — none existed; the only other Python load was the ~3%-CPU Alpha discovery service, left untouched.)

## §9 — No forbidden surfaces · PASS
No actual `import MetaTrader5` / `ve_tower` / broker / execution statements anywhere in the wheel; no `order_send`, `set_authority`, or `probability_inputs` in code. The single `SEALED` token is a `HoldoutStatus` **enum label** (`provenance.holdout_status`) in the vendored, byte-identical `strategy_manager/contract.py`, not access to sealed data. The engine imports only its vendored closure + `ve_brain` + numpy/stdlib.

## §10 — LIVE_SHADOW untouched · PASS (read-only)
Read-only checks only: the live process was not touched; `decision_authority=1.0` → **NEW_BRAIN**; shadow journal all `LIVE_SHADOW_NO_TRADE`, `order_send_calls=0`, **none reached the broker gate**; broker DISABLED. Alpha did not run the 355 hypotheses (only its light background discovery service is up).

---

## AUTHORIZATION
**N1_INCREMENTAL_PASS.** The incremental N1 engine is byte-identical to 0.1.0, preserves unbounded structural state across snapshot/restart (resolving the `N1_HYDRATION_CONDITIONAL` blocker), and scales O(n) (355,696 bars in 18.8 min). This closes the "`ve_n1_replay` incremental PASS + canonical N1 hydration" condition; Alpha may use `ve_n1_replay 0.1.1` **only in the Alpha environment** (with pinned `ve_brain 0.1.3`) for the canonical N1 rerun of the 355 hypotheses. This does **not** authorize the broker, does **not** authorize the LIVE_SHADOW cutover (that remains gated on final integration + full regression + cutover review per RT-TIME-0001), and does **not** start Alpha. **LIVE_SHADOW continues untouched; broker DISABLED; CAND-T05 frozen.** Red Team modified no VE engine, ran no real orders, disturbed no live process, and changed nothing outside `red_team/`.
