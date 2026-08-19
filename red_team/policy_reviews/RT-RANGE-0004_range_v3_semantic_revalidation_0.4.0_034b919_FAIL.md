# RED TEAM — `ve_n1_replay 0.4.0` RANGE SEMANTIC V3 DELTA REVALIDATION
### RT-RANGE-0004 · **RANGE_V3_SEMANTIC_FAIL**
**Date:** 2026-08-19 · **Auditor:** Red Team · **Target:** `ve_n1_replay 0.4.0` (RANGE SEMANTIC V3, longitudinal segment redesign). Wheel `ve_n1_replay-0.4.0-py3-none-any.whl`, SHA-256 `c79f5fcab202a72c6548a470e7702b6917685dc782c67f5f4dfe4ed0af363699` (126 766 B); build `dead38d`, delivery `034b919`. Statistician spec `bf9f780`, manifest v2.7.84 `db098ed`, fingerprint `cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233`.

**Read-only. No artifact modified, no parameter recalibrated, no intermediate result given to VE. Alpha not started; hypotheses not run; detector not modified; no AI Trader / LIVE_SHADOW deployment. No PnL / SEALED-OOS / orders. Nothing changed outside `red_team/`.**

---

# VERDICT — **RANGE_V3_SEMANTIC_FAIL**

**One material defect blocks ratification: §12 — the config schema accepts `d_min_bars` values that destroy the declared O(n)/4-hour performance guarantee, with no contractual maximum, and the delivered benchmark exercised only the favorable canonical value.** Empirically confirmed: `slope()` is O(`d_min_bars`) per bar (20× `d_min` → **20.1×** per-bar cost after filling the `closes` deque), and `RangeConfigV3(…, d_min_bars=200000, acknowledge_construction_only=True)` **constructs without error**. At `d_min_bars=200000` the per-bar cost extrapolates to ~90 ms → ~8.9 h for 355 696 bars, well over the claimed 4 h. Per mandate §12 ("*valori foarte mari sunt refuzate SAU rămân în limitele de performanță declarate*" — neither holds; "*benchmarkul nu folosește numai o configurație favorabilă dacă schema acceptă unele patologice*" — it did) and §19 ("*PASS numai dacă TOATE condițiile sunt îndeplinite*"), this is a material FAIL.

**Everything else PASSES, independently verified.** Identity, delta, install, D1–D4, the HBL-20 sweep causality, K/N consumption, all 14 states, the incremental running median, zero-lookahead/snapshot, N1 byte-parity, isolation, and the HBL honesty boundary all hold. The canonical config (`d_min_bars=96`) **does** meet the guarantee: I reproduced clean O(n) scaling (10k→20k = 2.00×, ~5.56 ms/bar → ~33 min at 355 696 bars, matching VE's 30 min 41 s). **The defect is narrow and cheaply fixed** — this is not a semantic error in the detector.

**Minimal fix (for VE — not implemented by Red Team):** add an explicit contractual maximum on `d_min_bars`, validated in `RangeConfigV3.__post_init__` (fail-closed like the K>N guard), **or** bound the OLS slope window independently of `d_min_bars`; then benchmark at the declared maximum. **New version required (e.g. 0.4.1).** Alpha stays blocked; `NEW_INDEPENDENT_BLIND_LABEL_BATCH` is NOT authorized.

---

## PASS/FAIL matrix

| § | Check | Result |
|---|-------|--------|
| 1 | Artifact identity (SHA/commits/sidecar/manifest) | **PASS** |
| 2 | Delta 0.3.1→0.4.0 surgical, N1 byte-identical | **PASS** |
| 3 | Clean-venv install + 237 tests | **PASS** |
| 4 | D1 — segment-local anchor, no leak | **PASS** |
| 5 | D2 — degenerate geometry impossible (public surface) | **PASS** |
| 6 | D3 — TOO_SHORT reachable from segment start | **PASS** |
| 7 | D4 — acceptance terminates but does not erase | **PASS** |
| 8 | Sweep causality (HBL-20) | **PASS** |
| 9 | K and N both consumed; K>N refused | **PASS** |
| 10 | All 14 states reachable via public API | **PASS** |
| 11 | Incremental running median == offline oracle | **PASS** |
| **12** | **Performance risk via config (`d_min_bars`)** | **FAIL** |
| 13 | Zero-lookahead + invariance | **PASS** |
| 14 | Snapshot / identity fail-closed | **PASS** |
| 15 | HBL interpretation honesty | **PASS** |
| 16 | Benchmark (canonical O(n)/4h) | **PASS (canonical only)** |
| 17 | Regression + prohibitions | **PASS** |
| 18 | Invariants untouched | **PASS** |

## §1 — Artifact identity · PASS
Wheel re-hashed = `c79f5fca…3699`, 126 766 B — identical to declared, `SHA256SUMS.txt`, and git-stored bytes (`git cat-file`). Build `dead38d`, delivery `034b919` in git log. Statistician `bf9f780` ("RANGE_SEMANTIC_SPEC_READY_FOR_VE"), manifest v2.7.84 `db098ed`, fingerprint `cddaab38…` — all exact. `self_declared_pass=false`; `HUMAN_LABEL_BATCH_01_CEO_ASSISTED_RESULTS` present. **Sidecar describes exactly the delivered wheel** (`wheel_sha256=c79f5fca…`, size 126766, correct filename); the `048ee2b4…` inside `predecessor_kept_unmodified` is a legitimate 0.3.1 reference (build `aa01f41`), not a mismatch.

## §2 — Delta 0.3.1→0.4.0 · PASS
Recursive wheel diff: **only two new files** (`range_semantic_v3.py`, `range_engine_v3.py`) + two additively-modified (`__init__.py`, `version.py`). **Byte-identical to 0.3.1:** `_ai` (15 modules), `_det` (5 detectors), `incremental.py`, `_bootstrap.py`, and all six predecessor range files (v1/v2/v2_1 — 0.3.1 not overwritten). N1 incremental (0.1.1) byte-identical. `ve_brain`/Router/EV/N6/broker are not in the wheel and unmodified. Change limited to RANGE V3 + contracts/exports/versions/docs.

## §3 — Independent installation · PASS
Installed 0.4.0 in a clean, empty venv (no sibling source tree); resolves from `site-packages`; version `0.4.0`. `RangeConfigV3` requires `K`/`N`/`w_atr` explicitly (no hidden default) and refuses construction without `acknowledge_construction_only=True` (`ConfigNotRatifiedError`). **237 tests, 0 failures, 0 errors, 0 skipped** (JUnit XML) from the installed wheel — matches the declared count.

## §4 — D1 segment-local anchor · PASS
Independent (public producer): a segment established near 3340 then terminated by breakout; the **successor** segment at 4340 anchors at ~4346 — **no swing leak** from the 2400/3340 predecessor. Two very different prehistories followed by an identical suffix produce **identical anchor geometry** on the fresh suffix segment (61 established bars, exact match). Distinct `segment_id`s per regime.

## §5 — D2 degenerate geometry · PASS (via public surface)
Through `observe()` (not `_Segment` construction): `atr=None` → `ATR_UNAVAILABLE`; `atr=0`, `NaN`/`Inf` inputs, and near-equal anchors **never** yield an `available & ESTABLISHED` result with `anchor_upper<=anchor_lower` or non-finite anchors, and never crash. `ZONES_DEGENERATE` **is reachable** via `observe()` on near-degenerate geometry (width ≪ 2w), and such a segment **never reaches ESTABLISHED**.

## §6 — D3 duration · PASS
`TOO_SHORT` is genuinely reachable via the public engine/producer (not just the enum). It appears **only** while `bars_in_segment < d_min` (with geometry present) and clears at/above `d_min`. A long prehistory before a fresh short segment does **not** auto-age it (`bars_in_segment` restarts from the segment's own `structural_start`).

## §7 — D4 acceptance ≠ erasure · PASS
Establish → sustained breakout: `BREAKOUT_ACCEPTANCE_UP` emitted, segment terminated, and it **survives in `history`** with `reached_established=True` and `end_reason=TERMINATED_BY_BREAKOUT`; the successor carries `predecessor_id`. Distinct meanings for `TERMINATED_BY_BREAKOUT` vs `RANGE_FAILED_PRECONDITION` confirmed.

## §8 — Sweep causality (HBL-20) · PASS
Driving the producer over the HBL-20 synthetic fixture: **exactly one** `LIQUIDITY_SWEEP_DOWN`, confirmed at **bar 56 (the re-entry)**, `confirm_ts = bar56.ts_close ≠ bar52.ts_close`. The breach bar 52 emits no confirmed sweep; bars 53–55 emit no premature sweep/breakout. Mirrored UP fixture yields `LIQUIDITY_SWEEP_UP`.

## §9 — K and N · PASS
`K>N` → `RangeSemanticContractErrorV3` (K≤N invariant enforced). **K consumed:** same breach/re-entry → clean sweep at K=5 vs `SWEEP_WINDOW_EXPIRED` at K=2. **N consumed:** on a controlled sustained breakout, `BREAKOUT_ACCEPTANCE` fires at exactly the Nth consecutive outside close (N=3→bar 3, N=5→bar 5, N=6→bar 6). Both parameters influence outputs; impossible configs refused.

## §10 — All 14 states reachable (public) · PASS
Every `SegmentEventKindV3` value was produced through the public `observe()`/engine surface — including `CHANNEL_UP`/`CHANNEL_DOWN` (via an oscillating drifting channel), `LIQUIDITY_SWEEP_UP/DOWN`, `BREAKOUT_ACCEPTANCE_UP/DOWN`, `RANGE_FAILED`, `UNAVAILABLE`, `TRANSITION`, and the range states — no enum instantiation, no private-helper call, no result-fabricating fixture.

## §11 — Running median · PASS
`_RunningMedian` (two-heap) equals `statistics.median` at **every prefix** across 10 sequences (even/odd, duplicates, extremes, sorted, reverse-sorted, constant). Two instances share no state; deterministic; snapshot/restore reconstructs by replaying `add()` (order-independent value).

## §12 — Performance risk via config · **FAIL**
`slope()` iterates the entire `closes` deque (`maxlen = d_min_bars`) each bar → **O(`d_min_bars`) per bar**. `RangeConfigV3.__post_init__` validates only `acknowledge_construction_only`, `K≤N`, and positivity — **no maximum on `d_min_bars`**; `RangeConfigV3(K=1,N=2,w_atr=0.3,acknowledge_construction_only=True,d_min_bars=200000)` constructs cleanly. Empirically, after filling the deque: `d_min=200 → 90.9 µs/bar`, `d_min=4000 → 1829 µs/bar` (**20.1×** for 20× `d_min`) — clean O(`d_min`). Extrapolated to `d_min=200000`: ~90 ms/bar → **~8.9 h for 355 696 bars**, breaching the 4 h guarantee. The Statistician spec (`bf9f780`) is silent on a `d_min_bars` bound; memory is bounded (`deque maxlen`) so this is a **compute**, not a memory-leak, failure. VE's benchmark used only the favorable `d_min=96`. This is exactly the §12 condition the mandate names as FAIL-or-require-limit; with only two terminal verdicts and §19 requiring all conditions, it is a FAIL.

## §13 — Zero-lookahead + invariance · PASS
Engine: prefix run == full-run prefix (zero lookahead); chunk-invariance under `[116]/[1,115]/[50,66]/[80,20,16]` via snapshot/restore between chunks reproduces the continuous run exactly. (The producer's bar index is its own internal counter — chunk-invariant by construction.)

## §14 — Snapshot / identity · PASS
`restore` **explicitly refuses** 0.2.0/0.3.0/0.3.1 snapshots (`RangeSnapshotErrorV3`), unknown types, `None`, and config/spec/schema/n1-identity mismatch; restore is **atomic** (a fresh isolated producer is built and validated before any state is swapped — all-or-nothing). Valid same-identity restore continues bit-identically to the never-restarted run.

## §15 — HBL honesty · PASS
The sidecar states plainly: HBL windows are **synthetic qualitative analogs** built from the CEO's published phase descriptions (real intervals deliberately unpublished), HBL-20 is numerically exact from the Statistician's own published bar verification, and the batch is `CEO_ASSISTED — NOT blind, NOT independent, NOT OOS, NOT validation. Construction-only PERMANENT`. No claim of real-window recognition, no `RANGE_V3_BLIND_PASS`, no SEALED/OOS access. Honesty boundary respected.

## §16 — Benchmark · PASS (canonical only)
At the canonical `d_min_bars=96`: clean linear scaling (10k→20k = **2.00×**, ~5.56 ms/bar) → ~33 min extrapolated at 355 696 bars, consistent with VE's reported 30 min 41 s / 193 bars-s. O(n)/4h holds **for the canonical config** — which is exactly why §12 (non-canonical `d_min`) is the gap. Run against the installed wheel; single process; process cleaned up.

## §17 — Regression + prohibitions · PASS
237/237 tests pass (installed wheel). No executable forbidden imports in `range_semantic_v3.py`/`range_engine_v3.py` (only stdlib `heapq`/`hashlib`/`math` + typing + internal `from .`); no MT5/broker/`order_send`/`set_authority`/`probability_inputs`/default-LONG/range-fabricating-fallback. N1 layer byte-identical to 0.1.1 (§2). `ve_n1_replay` **not importable** in the AI-Trader live venv (0.4.0 not in the runtime). Rollback path 0.4.0→0.3.1→0.1.1→0.4.0 declared and consistent with each wheel's presence. (mypy `--strict` not independently re-run — mypy's compiled components cannot be reassembled in this offline app-controlled venv; VE reports it clean.)

## §18 — Invariants · PASS
0.4.0 is an isolated wheel that composes N1 + adds RANGE V3; it does not write to the Alpha registry, tombstones, verdicts, F1–F6, F7, the Strategy Catalog, the broker gate, or LIVE_SHADOW. `m_inference=26`, `n_generated_total=363` and the rest are untouched by construction (read-only artifact review). LIVE_SHADOW verified read-only: task Running, live PIDs 22592/25992 on the old runtime, unchanged.

---

## What I re-verified independently vs. did not run
- **Independently driven this session:** §1 identity (re-hash, git-stored bytes, sidecar, commits), §2 wheel diff, §3 install + 237-test JUnit, §4–§11/§13/§14 adversarial via the public producer/engine, §12 empirical O(`d_min`) + uncapped-schema, §16 canonical O(n) scaling, §17 isolation/imports.
- **NOT run:** mypy (offline tooling limit); full 355 696-bar wall-clock (used O(n) checkpoints at the canonical config; VE's 30m41s reproduced by extrapolation); any Alpha run / PnL / SEALED-OOS / real orders.

## Disposition
`RANGE_V3_SEMANTIC_PASS` is **not** issued. **Alpha remains blocked; `NEW_INDEPENDENT_BLIND_LABEL_BATCH` NOT authorized.** VE fixes the §12 defect (contractual `d_min_bars` maximum, or `d_min`-independent slope window) and re-benchmarks at the maximum, delivering a new version. Everything else in RANGE V3 is independently confirmed sound, so remediation is expected to be surgical. Next owner: **`STATISTICIAN_RANGE_V2_FAILURE_RULING`** / VE for the fix (per the mandate's FAIL branch). LIVE_SHADOW continues on the existing safe runtime. Red Team modified no VE/AI-Trader code and changed nothing outside `red_team/`.
