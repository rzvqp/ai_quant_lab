# RED TEAM — `ve_n1_replay 0.4.1` RANGE V3 PERFORMANCE DELTA REVALIDATION
### RT-RANGE-0005 · **RANGE_V3_PERFORMANCE_DELTA_PASS**
**Date:** 2026-08-19 · **Auditor:** Red Team · **Target:** `ve_n1_replay 0.4.1` (fix for the §12 defect in RT-RANGE-0004 `87cad2c`/E79). Wheel `ve_n1_replay-0.4.1-py3-none-any.whl`, SHA-256 `39673910666e13708b1d4cb7266d1730bb1c9ceea4e0b021a1bf3cfa1f8281f4` (141 157 B); build `f9af357`, delivery `7dc2ff9`.

**Read-only. No artifact modified, no parameter recalibrated. Alpha not started; detector not modified; no AI Trader / LIVE_SHADOW deployment. No PnL / SEALED-OOS / orders. Nothing changed outside `red_team/`.**

---

# VERDICT — **RANGE_V3_PERFORMANCE_DELTA_PASS**

**The RT-RANGE-0004 §12 defect is closed, and the 0.4.0 RANGE semantics are unchanged.** VE chose **Variant A** — an incremental O(1) OLS slope via sufficient statistics — with **no `d_min_bars` cap** (correctly declining to invent an unratified maximum), plus a CEO-requested `d_min_bars` input-validation hardening. Independently verified through the public surface:

- **The fix works (§7):** the range-producer per-bar cost is **flat** — 15.42 / 15.45 / **15.26 µs** at `d_min_bars` = 96 / 4000 / **200000** (the exact value that triggered the FAIL). No growth with `d_min`; the ~9 h projection is gone. Canonical O(n) holds (10k→20k = 2.06×, ~33 min at 355 696 bars, under 4 h, consistent with VE's 30 m 18 s).
- **The math is exact (§4):** the incremental slope matches a full-recompute offline oracle at **every prefix** across all enumerated sequences and window sizes (incl. a 20 000-bar eviction run at `d_min=4000`); max abs diff **3.9 × 10⁻¹⁰** (only on pathological 10⁹-magnitude inputs), and **bit-exact (0.0)** on the real `observe()` path — too small to ever flip `IS_CHANNEL`.
- **The semantics are unchanged (§9):** 0.4.0 vs 0.4.1 produce **0 mismatches** over a mixed 116-bar trace and a **bit-identical HBL-20 trace** (sweep still confirms at bar 56, not breach bar 52).
- **The hardening is contractual (§6):** every invalid `d_min_bars` (−100, −1, 0, 1.0, 5.5, `True`, `False`, `"96"`, `None`, 96.0) is rejected via `RangeSemanticContractErrorV3` (not `IndexError`); `bool` is rejected despite subclassing `int`; valid values (1/96/4000/200000) accepted; an invalid config can never construct a `RangeConfigV31` instance.

The change is surgical: N1 (0.1.1) and 0.4.0's `range_semantic_v3.py`/`range_engine_v3.py` are byte-identical; the new `RangeSemanticProducerV31` differs from `RangeSemanticProducerV3` by **only the documented single call-site** (`seg.push_close(close)` vs `seg.closes.append(close)`) plus comments.

**PASS closes RT-RANGE-0004** and authorizes **only** `NEW_INDEPENDENT_BLIND_LABEL_BATCH`. It does **not** authorize the Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, the broker, or trades.

---

## PASS/FAIL matrix

| § | Check | Result |
|---|-------|--------|
| 1 | Git / artefact identity | **PASS** |
| 2 | Surgical diff 0.4.0→0.4.1 | **PASS** |
| 3 | Isolated install + 320 tests + `CONSTRUCTION_ONLY` | **PASS** |
| 4 | Incremental OLS == offline oracle | **PASS** |
| 5 | `IS_CHANNEL` threshold parity | **PASS** |
| 6 | `d_min_bars` contractual hardening | **PASS** |
| 7 | Adversarial perf `d_min=200000` (O(1)) | **PASS** |
| 8 | Canonical benchmark (O(n), <4h) | **PASS** |
| 9 | Semantic parity 0.4.0 ↔ 0.4.1 | **PASS** |
| 10 | Snapshot 0.4.1 (schema + fail-closed) | **PASS** |
| 11 | Minimal semantic regression | **PASS** |
| 12 | Rollback + isolation | **PASS** |
| 13 | Prohibitions + invariants | **PASS** |

## §1 — Identity · PASS
Wheel re-hashed = `39673910…81f4`, 141 157 B — identical to declared, `SHA256SUMS.txt`, and git-stored bytes. Build `f9af357`, delivery `7dc2ff9`; `self_declared_pass=false`; sidecar `wheel_sha256`/filename/size match exactly (the `c79f5fca…` inside is a legitimate 0.4.0 predecessor reference). The wheel embeds the prior verdict provenance: `RANGE_V3_1_RED_TEAM_COMMIT=87cad2c`, `…_VERDICT=RANGE_V3_SEMANTIC_FAIL`, `…_ENTRY=E79`, `…_DEFECT_SECTION=§12`, `RANGE_V3_1_FIX_VARIANT=A`.

## §2 — Surgical diff · PASS
Recursive wheel diff 0.4.0→0.4.1: **two new files** (`range_semantic_v3_1.py`, `range_engine_v3_1.py`) + two additively-modified (`__init__.py`, `version.py`). **Byte-identical to 0.4.0:** N1 `_ai`(15)/`_det`(5)/`incremental.py`/`_bootstrap.py`, **and 0.4.0's own `range_semantic_v3.py`/`range_engine_v3.py`** (kept untouched), plus every predecessor range file. Normalized source diff of the producer (renames + call-site neutralized, comments/docstrings stripped): the **only** code change is `seg.closes.append(close)` → `seg.push_close(close)`. `ve_brain`/Router/EV/N6/broker are not in the wheel and unmodified.

## §3 — Isolated install + tests · PASS
Installed 0.4.1 in a clean, empty venv; resolves from `site-packages`; version `0.4.1`. **320 tests, 0 failures, 0 errors, 0 skipped** (JUnit XML) — matches the declared count. `RangeConfigV31` remains `UNRATIFIED/CONSTRUCTION_ONLY` (requires explicit K/N/w_atr + `acknowledge_construction_only=True`).

## §4 — Incremental OLS parity · PASS
`_IncrementalSlope` keeps `Sx=n(n−1)/2` and `Sxx=n(n−1)(2n−1)/6` closed-form (exact) and maintains only `Sy`/`Sxy` incrementally; the eviction shift is algebraically correct (`Sxy_new = Sxy_old − Sy_old + y_evicted + (n−1)·y_new`, verified by derivation). Compared to a full-recompute oracle at **every prefix** for windows 1/2/3/10/96/4000 across constant/ramp-up/ramp-down/oscillation/duplicate/small/large/alternating-extreme/random sequences, plus a 20 000-bar eviction run at `d_min=4000`: **max abs diff 3.9 × 10⁻¹⁰, max rel diff 1.4 × 10⁻⁷**, appearing only on 10⁹-magnitude adversarial inputs. **Flip risk on `IS_CHANNEL`: none** — on the real `observe()` path the slope is bit-identical (§5/§9), and a ~4 × 10⁻¹⁰ slope error times `d_min≤200000` is ~8 × 10⁻⁵ of drift, far below any threshold.

## §5 — `IS_CHANNEL` threshold parity · PASS
Driving the actual producers on the mixed sequence, the per-bar slope difference between 0.4.0 and 0.4.1 is **exactly 0.0**, so the channel-vs-range classification and reason codes are identical (subsumed by §9's 0 mismatches, which includes every `IS_CHANNEL`/`CHANNEL_UP/DOWN` decision on the trace).

## §6 — `d_min_bars` hardening · PASS
`RangeConfigV31.__post_init__` calls `super().__post_init__()` (0.4.0's K/N/w_atr/K≤N checks, unchanged), then rejects `d_min_bars` that is a `bool`, is not an `int`, or is `<1` — via `RangeSemanticContractErrorV3` (the existing exception, no new type). Verified through the public API: all of `{-100,-1,0,1.0,5.5,True,False,"96",None,96.0}` → `RangeSemanticContractErrorV3`; `{1,96,4000,200000}` accepted; `bool` rejected despite the int subtype; a rejected construction produces no instance and does not mutate a separate valid instance. The crash path (`IndexError` from `push_close`) is structurally unreachable.

## §7 — Adversarial performance · PASS
Range-producer per-bar cost is **flat with `d_min_bars`**: 15.42 µs (`d_min=96`), 15.45 µs (`d_min=4000`), **15.26 µs (`d_min=200000`)** — O(1), no proportional growth, bounded `closes` deque retained only for O(1) eviction peek, zero exceptions, valid output, process cleaned up. The RT-RANGE-0004 ~9 h projection at `d_min=200000` is closed (the range layer no longer dominates; full-engine cost stays N1-bound).

## §8 — Canonical benchmark · PASS
0.4.1 at `d_min_bars=96`: 10k→20k bars = **2.06×** (linear), ~5.6 ms/bar → **~33 min** at 355 696 bars, under 4 h and consistent with VE's reported 30 m 18 s. Single process; no concurrent old benchmark; ≤ 0.4.0's own canonical time (0.4.1's range layer is now O(1) vs 0.4.0's O(96)).

## §9 — Semantic parity 0.4.0 ↔ 0.4.1 · PASS
On identical inputs (matched configs), the full per-bar trace — availability, lifecycle, segment/predecessor IDs, anchors, mid, touches, `confirm_ts`, pending/confirmed events, reason codes, slope — is **identical: 0 mismatches over 116 bars**. **HBL-20 reproduced bit-for-bit**: breach low bar 52, single `LIQUIDITY_SWEEP_DOWN` confirmed at bar 56 (`confirm_ts` = bar 56 ≠ bar 52), markup bar 63 — trace identical to 0.4.0. On VE's "0/320 mismatches": 320 is the **test count**, not a comparison count; VE's parity harness compares per-bar states across its corpus, and my independent comparison (116 + 71 bars) corroborates zero semantic divergence. Version identity (`range_spec_id`/`config_hash`) intentionally differs by contract (new producer version), as designed.

## §10 — Snapshot 0.4.1 · PASS
The snapshot schema is extended with the slope sufficient statistics (`_slope_sum_y`/`_slope_sum_xy`). `restore` **explicitly refuses** snapshots from 0.2.0/0.3.0/0.3.1 **and 0.4.0** (`RangeSnapshotV3_040`, the immediate predecessor — no correspondent for the new fields), plus unknown types, `None`, corrupt/truncated payloads, and schema/N1-identity/spec/config mismatch — all via `RangeSnapshotErrorV31`, **atomically** (a fresh isolated producer is validated before any swap; a failed restore leaves the engine unchanged, verified). Chunk-invariance across `[116]/[1,115]/[50,66]/[80,20,16]` reproduces the continuous run; snapshot/restore works at `d_min=200000`.

## §11 — Minimal semantic regression · PASS
On 0.4.1 directly: D1 segment-local anchor (no leak), D2 `ZONES_DEGENERATE` reachable and never established, D3 `TOO_SHORT` reachable, D4 breakout terminates but the segment survives in history with `reached_established`, K>N refused, all 14 states reachable via the public surface, sweep confirmed only at re-entry, zero-lookahead prefix parity — all hold (consistent with the §9 full parity to the 0.4.0 baseline that passed these in RT-RANGE-0004).

## §12 — Rollback + isolation · PASS
Functional rollback `0.4.1 → 0.4.0 → 0.3.1 → 0.1.1 → 0.4.1`: each version installs, resolves from `site-packages` (no source/cache contamination), reports the correct `__version__`, and exposes its signature API (`RangeConfigV31`/`RangeConfigV3`/`RangeConfigV2Pinned`/`N1IncrementalReplayEngine`); the chain returns cleanly to 0.4.1. (VE additionally reports each version's own suite 320/237/162/43; I verified the install/version/API chain independently.)

## §13 — Prohibitions + invariants · PASS
No executable forbidden imports in `range_semantic_v3_1.py`/`range_engine_v3_1.py` (only stdlib `heapq`/`hashlib`/`math` + typing + internal `from .`); no MT5/broker/`order_send`/`set_authority`/`probability_inputs`/default-LONG/range-fabricating-fallback. `ve_n1_replay` is **not importable** in the AI-Trader live venv (0.4.1 not in the runtime). LIVE_SHADOW verified read-only (task Running, unchanged). `n_generated_total=363`, `m_inference=26`, tombstones, Alpha registry, verdicts, F1–F6, F7, Strategy Catalog, broker gate untouched by construction (isolated wheel).

---

## What I re-verified independently vs. did not run
- **Independently this session:** §1 identity (re-hash/git-bytes/SHA256SUMS/embedded refs), §2 wheel + normalized-source diff, §3 install + 320-test JUnit, §4 incremental-vs-oracle across all enumerated cases + 20k-bar eviction, §5 slope parity, §6 hardening table, §7 O(1) at d_min up to 200000, §8 canonical O(n) scaling, §9 parity + HBL-20, §10 snapshot attacks, §11 regressions, §12 rollback chain, §13 imports/isolation.
- **NOT run:** mypy (offline tooling limit; VE reports clean); full 355 696-bar wall-clock (used O(n) checkpoints; VE's 30m18s reproduced by extrapolation); each historical suite end-to-end (verified install/version/API chain; VE ran 320/237/162/43); any Alpha / PnL / SEALED-OOS / order.

## Disposition
`RANGE_V3_PERFORMANCE_DELTA_PASS` **closes RT-RANGE-0004** and authorizes **only** `NEW_INDEPENDENT_BLIND_LABEL_BATCH`. NOT authorized: Strategy Catalog, Alpha, AI-Trader integration, LIVE_SHADOW cutover, broker, trades. LIVE_SHADOW continues on the existing safe runtime. Red Team modified no VE/AI-Trader code and changed nothing outside `red_team/`.
