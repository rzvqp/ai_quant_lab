# RED TEAM — CODE ATTACK · `zone_observer` (Level-3 entry, live)
### RT-CODE-A-0012 · Target: `ai_trader/zone_observer/` @ branch `ai-trader-implementation` (`ai_quant_lab-research-main`)
**Date:** 2026-08-05 · **Auditor:** Red Team · Records live: session levels (A), demand zones, IFVG, BPR, PWH/PWL, liquidity voids. Statistician confirmed **pure observation** (no score/weight/threshold). Checklist only: lookahead, leakage, circularity, ambiguity, overfitting, hidden params, reproducibility. **No data run on the market · nothing modified · no remedy.** Vendorization claims byte-verified via `git`; cost scaling measured on synthetic bars.

## VERDICT — **PASS_WITH_LIMITATIONS.**
Correctly built as a pure-observation Level-3 entry: vendorization **byte-verified with zero drift**, **no overlap** with `structural_observer`, **Primitive B absent**, **PWH/PWL formation-only**, and lookahead/leakage/circularity/overfitting/hidden-params/reproducibility all clean. The only limitation is **cost**: per-cycle is ~linear and the cold-replay total is quadratic O(N²), and the "<200 ms at 14,000 bars" projection is **optimistic** (extrapolated from an 18-bar baseline too small to show the scaling).

---

## T1 — VENDORIZATION — **byte-verified CORRECT, zero drift.**
The detectors are a **submodule** pinned at `61cbd58c`; `session_levels` is a separately-vendored single file. Every claim independently verified with `git rev-parse`/`git hash-object`:
- **Four detectors IDENTICAL across pin↔`bf02dd2`** (so importing from the pinned submodule = the `bf02dd2` version): `order_flow 23b0470`, `imbalance_mechanics aa1c6d3`, `order_block_void 2b0f3f3`, `institutional_levels 23182f4` — same blob at both commits. ✅
- **`market_structure` / `liquidity_mechanics` genuinely DIFFER** (pin `52bb1eb`/`805b8cd` vs bf `d734ac9`/`45a5219`) — confirming the stated reason for **not** moving the pin (it would change `structural_observer`'s live `detect_breaks` output). ✅
- **Vendored `session_levels` blob = `95dc487b` = `bf02dd2:code/session_levels.py`** exactly; the submodule is clean at the pin (no local drift). ✅
- **The cross-version dependency is safe:** `session_levels` (bf02dd2) imports `Block` (from the *differing* `market_structure`), `session_of` (`market_state`), `_runs` (`institutional_levels`) at the pin — and **all three symbols are byte-identical across pin↔bf02dd2** (`market_state` whole-file identical; the `Block` dataclass and `session_of` unchanged by the `detect_breaks` cascade diff). **zone_observer never touches the differing code** — it uses `market_structure` only for `Block`, which is identical. **No drift reaches any observed value.** ✅

## T2 — OVERLAP with `structural_observer` — **none; nothing double-recorded.**
Recorded event sets are **disjoint** (verified by reading both):
- `structural_observer` records: SWING, STRUCTURE_BREAK, FVG_FORMED, FVG_REACTION, REGIME, ORDER_BLOCK_{FORMED,BREAKER,MITIGATION,REJECTION} — and imports `detect_order_blocks/mitigations/rejections`, **not** `detect_demand_zones`.
- `zone_observer` records: SESSION_LEVEL_{FORMED,TOUCH}, DEMAND_ZONE_FORMED, INVERSE_FVG_FORMED, BPR_COUNT, WEEKLY_LEVEL_FORMED, LIQUIDITY_VOID.
- `detect_demand_zones` is the **one** `order_flow` function `structural_observer` doesn't record → uniquely zone's. `detect_fvgs` is computed in **both**, but zone records it **nowhere** (input to IFVG/BPR only); `structural_observer` alone records FVG_FORMED/REACTION. So the only shared thing is a **duplicate computation** (a cost, Z-U2), **not a duplicate observation.** ✅

## T3 — PRIMITIVE B — **absent from every path.**
`vendor_bridge` imports **only** Primitive A (`compute_prior_session_levels` + the touch/mid detectors); `compute_persistent_session_levels` (B, forbidden without the k=1.0×ATR filter) is **imported and called nowhere.** Grep confirms "persistent" appears only in (a) the docstring *forbidding* B and (b) an unrelated `persistent_state.store` SQLite import. ✅

## T4 — PWH/PWL — **formation only; no invented touch detector.**
`vendor_bridge` imports `compute_prior_week_levels` + `derive_week_index` (formation); `observer.py` records **`WEEKLY_LEVEL_FORMED` only.** No `detect_level_touches` import, no `WEEKLY_LEVEL_TOUCH` kind. `types.py` + the docstring state that the ratified `detect_level_touches` excludes WEEKLY_HIGH/LOW ("doar fereastra zilnica") and **no weekly-touch detector is invented.** ✅

## T5 — COMPUTE COST — **per-cycle ~linear, total quadratic; the projection is optimistic. (Z-U1)**
Every detector is recomputed from scratch on the whole accumulated array each bar. **Measured** (replicating `observe()`'s detector calls on growing synthetic arrays, N=100…3000):
- **Per-cycle scaling exponent k ≈ 1.13** → **≈ linear** per cycle (each `observe()` rescans everything). **Total to accumulate N bars = O(N^~2.1) — QUADRATIC.**
- **Extrapolated per-cycle at N=14,000 ≈ 376 ms** — **~2× the AI Trader "<200 ms" projection.** Their figure is a **linear extrapolation from an 18-bar baseline**, which is far too small to see the scaling (at 18 bars the detectors do near-zero work — few levels/pools/FVGs — so per-cycle is dominated by fixed overhead). My 100–3000-bar fit projects roughly double.
- **When it becomes a problem — the honest answer:**
  - **Live steady-state: never.** One H4 bar per 4 hours; a sub-second cycle (163–376 ms) is trivial relative to the 4-hour cadence. The projection being 2× off is immaterial live.
  - **Cold replay / restart re-accumulation: yes.** The observer keeps bar history **in-memory (disclosed: does not survive a restart)** and re-accumulates from whatever the loop re-feeds. A restart that re-feeds thousands of bars pays the **quadratic** total — my measurement extrapolates **~41 minutes to cold-replay 14,000 bars** (≈ 6 years of H4). So the cost is a **backfill / restart-recovery** concern, not a live one, and the recompute-from-scratch + in-memory-history + no-restart-persistence design compounds precisely there.

## CHECKLIST
- **Lookahead — PASS.** One **closed** bar fed at a time (the `LiveBarFeed` caller guarantees never a forming bar); `as_of = bar.ts_close`; detectors are the ratified causal ones (event at idx ≤ current), re-run on `[0, len]`. No future bar is accessible.
- **Leakage — PASS.** Pure per-observer accumulation; each detector on its own array; no cross-contamination.
- **Circularity — PASS/N-A.** Pure observation — no score, no weight, no threshold, no feedback (Statistician-confirmed and code-confirmed). It journals facts.
- **Ambiguity — minor (Z-U2).** `detect_fvgs` is computed in both observers (a redundant *computation*, disclosed); it is recorded in neither place twice.
- **Overfitting — PASS.** No fitted parameters; `BPR` tolerances `(0.0, 0.10, 0.25)` are declared observation granularities, not tuned; K_ATR unused (Primitive A needs no filter).
- **Hidden params — PASS.** `_BPR_TOLERANCES` declared; detector constants are the ratified ones.
- **Reproducibility — PASS.** Deterministic pure functions + key-based dedup → same result each run; the persisted journal keeps recorded observations across restarts, and the in-memory re-accumulation is deterministic (only a cost, T5).

## SEVERITY
- 🟡 **Z-U1 · Cost:** per-cycle ~linear, total O(N²); the "<200 ms @14,000" projection is optimistic (18-bar baseline; measured ~2× higher, ~41 min cold-replay). Non-issue live; a restart/backfill cost, compounded by in-memory history that doesn't survive a restart.
- 🟡 **Z-U2 · Duplicate computation:** `detect_fvgs` recomputed in both observers (cost, not a duplicate observation; disclosed).

## WHAT SURVIVES (verified)
Vendorization byte-verified with zero drift (four detectors identical across commits, session_levels blob-verified, cross-version `Block/session_of/_runs` identical, differing code never used); no recorded-event overlap with `structural_observer`; Primitive B absent from every path; PWH/PWL formation-only with no invented touch detector; lookahead-free (closed bars, causal detectors); no leakage/circularity/overfitting/hidden-params; reproducible. **Correctly built as a pure-observation Level-3 entry.**

## HANDOFF → CEO / Statistician
1. **Z-U1:** treat the "<200 ms @14,000" as an **optimistic live figure** (fine — live is never the bottleneck) but budget the **quadratic cold-replay / restart** cost (~tens of minutes at multi-thousand-bar backfills); if fast restart-recovery is ever needed, the recompute-from-scratch + in-memory design is the cost driver.
2. **Z-U2:** the double `detect_fvgs` computation is a minor, disclosed redundancy — acceptable for two independent processes.
3. Everything correctness-relevant (vendorization, no-overlap, no-Primitive-B, formation-only PWH/PWL, causality) is **verified clean** — the entry is safe as pure observation.

Red Team designed no remedy, ran no data on the market, modified nothing outside `red_team/`.
