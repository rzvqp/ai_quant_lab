# Replay-walk pullers — mechanism & the window-boundary property

This note exists so the **window-boundary property** below is written down, not rediscovered. It was
established by investigation on 2026-07-27 (see the Data Acquisition division report and the two fix
commits `0894191` / `228359b`). Read it before touching `pull_replay.mjs` or `replay_seek.mjs`.

## What these pullers do

TradingView serves deep intraday history for `OANDA:XAUUSD` only through **Replay mode**, not through
ordinary chart panning (`setVisibleRange`, which for M15 only ever loads the current ~300-bar window).
`pull_replay.mjs` therefore walks Replay **backward**, window by window (~300 bars each), reading every
loaded bar and de-duplicating by timestamp, until it reaches the provider's history floor. Output is a
6-column CSV (`time,open,high,low,close,volume`, epoch-UTC first column). Provider floors measured in
Phase 0: **M15 ≈ 2011-07-25**, H1 ≈ 2006-03, M5 ≈ 2021-07-22, M1 ≈ 2025-07-24 (rolling ~1 year).

## THE window-boundary property (the thing you must not forget)

**The bar at the Replay cursor — the newest / rightmost bar of each loaded window — carries a
PROVISIONAL close and volume.** It is the "current" replay bar and is not yet finalized. Every other
bar in the window (the interior bars) is final.

If you collect windows that are **adjacent** (no overlap) with first-seen de-duplication, that
provisional cursor bar becomes the *only* capture of its timestamp and is saved verbatim — **one wrong
bar roughly every 300 bars, silently, across the whole file.** On a range that overlaps an existing
reference this shows up (here: 195 of 196 overlap mismatches fell exactly on window right-edges, a
right-edge-vs-interior mismatch rate of ~57,800×). On a **virgin** range with no reference, nothing
would flag it. This is precisely why Verification 0 (a control region — real overlap where it exists,
or a half-window-offset double pull where it does not) is mandatory for every acquisition.

## How the ORIGINAL pipeline avoided it (and why we no longer use that shape)

The first lab dataset (`data/market/OANDA_XAUUSD_M15.csv`, 2022-12-16→2026-07-13; CHANGELOG line 1864)
was built in **three stages**:

1. `pull_replay_m15.mjs` — replay walk requesting **calendar-day midnight** (`slice(0,10)`) with
   stop/start per iteration. Empirically reproduced on a control slice: this produced **0 mismatches vs
   the reference** (all captured bars final) but left **boundary GAPS** — it never kept the provisional
   cursor bar; it simply failed to cover the seam between windows (~660 missing bars per 2 months).
2. `pull_gapfill.mjs` — re-read each gap region (targeting `gapDate+2days`), so the previously-missing
   boundary bars now landed **inside** a new window as **interior** (final) bars, and were added.
3. `pull_native.mjs` — cross-check of the resampled H1/H4/D1 vs native TradingView (0 mismatches). Note
   H1/H4/D1 in the original set were **resampled from M15** (`code/resample_ny.py`), not pulled.

So the corrective element was **gapfill**; the proven property is **"never keep the cursor bar — read
every bar as an interior bar."**

## How the CURRENT puller enforces it (single pass, overlapping windows)

`pull_replay.mjs` reproduces that proven property directly, without the two-stage gaps+gapfill dance:
it **overlaps** consecutive windows. Each new window is sought a few bars **inside** the
already-collected region (`nextOverlapSeekMs(frontier, overlapBars>=2, tf)` — ends at
`frontier + overlap*barSec`). The provisional rightmost bar therefore always lands on an already-final
bar, and first-seen de-dup keeps the FINAL value; every genuinely-new bar is an interior/final bar.
Result on control slices: **0 mismatches, 0 gaps** vs the existing file. The still-forming terminal bar
(market open) is dropped so the file ends on a settled bar. `replay_seek.test.mjs` carries a mechanical
simulation proving no provisional cursor bar reaches the file.

Boundary note: at the **absolute provider floor** there is no older window to overlap-cover the deepest
few bars, so the walk stops ~1 window short of the very first bar (e.g. M15 v2 starts 2011-07-26 vs the
2011-07-25 floor — 94 bars). This is principled (those bars cannot be interior-validated), not a defect.

## The two independent fixes on top of the historical puller

- `5accefd` — **seek/stall fix**: request the exact instant one second before the oldest bar, not
  calendar-day midnight, which after tradingview-mcp `c839e91` (fail-closed `replay.start`) trips a
  "Data point unavailable" toast and halts the walk as false "stale".
- `0894191` — **window-boundary fix**: the overlapping-windows mechanism above.
- `228359b` — resume-path fix: compute the frontier with an O(n) reduce, not `Math.min(...keys)`, which
  overflows the call stack on a 300k+ bar resume.
