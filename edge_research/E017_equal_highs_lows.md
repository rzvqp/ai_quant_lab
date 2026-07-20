# E017 — Equal Highs / Lows Target

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Liquidity. **This file is the permanent, append-only research log for this edge —
nothing below is ever deleted or retroactively edited; refinements are new, dated, appended versions.**

**First edge run under the post-remediation regime** (`EDGE_RESEARCH_PROTOCOL.md` §8) — data loaded
exclusively via the centralized `_common.load()` loader, no direct CSV read anywhere in
`e017_equal_highs_lows.py`.

## V0 (frozen, registered 2026-07-20, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> Clusters of equal highs/lows act as magnet levels that price is statistically likely to reach before
> reversing.

Measured outcome (as registered): rate at which price reaches the equal-highs/lows level, and reversal
rate/magnitude once reached.

## Discovery pass 1 (2026-07-21)

**Split metadata** (`e017_equal_highs_lows_results.json`): `data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`, `holdout_cutoff = 2025-10-23T09:15:00+00:00`,
`holdout_excluded = true`, `min_date_used = 2022-12-16 10:45:00 UTC`,
`max_date_used = 2025-10-23 09:00:00 UTC`, `n_bars_used = 67,321` (of 84,152; 16,831 holdout bars
excluded), `loader_version = flowA_common_v2_holdout_enforced_2026-07-21`. ~2.85 years — short of the
protocol's §2 ~5-6yr requirement; this is a Discovery-stage first pass, not a Final-Verdict-eligible
run.

**Method** (full disclosure in `e017_equal_highs_lows.py`):
- Swing (fractal) detection: k=5, same disclosed method already used for E028 (reproduced from scratch
  in this file, not imported — each edge script is self-contained). 4,072 swing highs / 4,057 swing
  lows detected.
- For every **consecutive pair of same-type swings** (p1, p2), **p2 is the target level tested in
  BOTH groups** — the only difference between groups is whether p1 sat within tolerance of p2:
  - **EQUAL group**: `|p2 − p1| ≤ tolerance × ATR14[p2]`.
  - **ISOLATED-CONTROL group**: the same pair, NOT within tolerance — an ordinary, non-doubled swing.
  Tolerance swept over **{0.10, 0.15, 0.25, 0.40} × ATR** (CEO-required clustering-tolerance
  sensitivity check); 0.15 is the primary/headline value, picked before any result was seen.
- **Second, stronger control — RANDOM-MATCHED-DISTANCE**: for a sample of purely random bar locations
  (seed=42, no swing structure at all), a synthetic target is placed at a distance (in ATR units)
  resampled with replacement from the EQUAL group's own empirical distance distribution. This tests
  whether the reach-rate found for real equal-highs/lows is simply "a target this close, given this
  much time, usually gets touched anyway" — independent of any real swing structure whatsoever.
- For every event: `reach` = whether price ever touches/exceeds the target within a horizon (96 / 480 /
  1920 M15 bars ≈ 1 / 5 / 20 trading days — horizon sensitivity, not optimized to one value).
  `time_to_reach` in bars. `reaction`, if reached: signed distance (ATR units) between target and price
  N=16 bars (~4h) later — positive = price pulled back (reversal); negative = continued through.
- Both **equal-HIGHS** and **equal-LOWS** run independently, compared for asymmetry.
- A **distance-quantile-matched** comparison (equal vs. isolated within the same distance quartile)
  directly tests whether any apparent effect is just a proximity artifact.
- Session/volatility slices at the primary tolerance/horizon.

## Headline result — V0 is NOT supported; the core "equal = stronger magnet" claim is REFUTED on
both tested dimensions, for both highs and lows, robustly across every tolerance and horizon tested

**(a) Reach rate — equal vs. isolated: no meaningful difference, at any tolerance, at any horizon:**

| Side | Tolerance | Horizon 96 (1d) | Horizon 480 (5d) | Horizon 1920 (20d) |
|---|---|---|---|---|
| High | 0.10 | equal 80.7% / isolated 80.6% | 94.1% / 92.6% | 97.5% / 97.6% |
| High | **0.15** | **80.6% / 80.6%** | **93.2% / 92.6%** | 97.5% / 97.6% |
| High | 0.25 | 80.7% / 80.6% | 93.0% / 92.6% | 98.2% / 97.5% |
| High | 0.40 | 81.9% / 80.3% | 93.2% / 92.6% | 97.9% / 97.6% |
| Low | 0.10 | 75.8% / 74.1% | 86.6% / 86.3% | 89.8% / 91.4% |
| Low | **0.15** | **76.4% / 74.0%** | **87.1% / 86.2%** | 90.5% / 91.4% |
| Low | 0.25 | 77.8% / 73.7% | 87.8% / 86.1% | 91.9% / 91.2% |
| Low | 0.40 | 76.1% / 73.8% | 87.3% / 86.1% | 92.1% / 91.1% |

At the primary tolerance/horizon (0.15, 480 bars), the equal-vs-isolated reach-rate difference is
**not statistically significant** (chi-square: high p=0.826, low p=0.765, n=279/263 equal vs
n=3792/3793 isolated) — and every other tolerance/horizon combination shows the same near-identical
pattern. **Tolerance choice does not materially change this conclusion anywhere in the tested range.**

**(b) The random-matched-distance control reaches its target MORE often and MUCH faster than either
real swing group — the opposite of what a "magnet" story would predict:**

| Side | Equal reach rate | Isolated reach rate | Random-matched reach rate | Equal vs. random p |
|---|---|---|---|---|
| High | 93.2% (median TTF 16 bars) | 92.6% (TTF 17 bars) | **98.2%** (TTF **1 bar**) | **p=0.0067** |
| Low | 87.1% (TTF 13 bars) | 86.2% (TTF 18 bars) | **92.8%** (TTF **2 bars**) | **p=0.043** |

A purely random level placed at the same ATR-normalized distance as a real equal-highs/lows cluster is
reached significantly *more* reliably, and dramatically faster (median 1-2 bars vs. 13-18 bars), than
the real swing-based levels. This directly contradicts the idea that these levels have special
"magnetic" pulling power — if anything, real local-extreme swing points (equal or not) appear mildly
*harder* to reach again than an arbitrary nearby level, plausibly because a fresh swing high/low is, by
construction, a point the market only just failed to exceed (a level with some real local resistance),
which a random level has no reason to share.

**(c) Reaction/reversal — no reversal-magnitude boost from being "equal"; if anything the opposite
sign on the high side:**

| Side | Equal mean reaction | Isolated mean reaction | Equal vs. isolated p |
|---|---|---|---|
| High | **−0.640** (CI excludes 0; continuation, not reversal) | −0.303 (CI excludes 0; also continuation) | p=0.056 (borderline; equal is MORE continuation-biased, i.e. LESS reversal, than isolated — the wrong direction for V0) |
| Low | +0.436 (CI includes 0; not significant) | +0.147 (CI excludes 0, barely; small reversal) | p=0.384 (n.s.) |

Both groups show net **continuation through** the level rather than reversal on the high side (both
means negative); the low side shows a small, only-marginally-significant reversal for isolated lows and
no significant reversal for equal lows. **In neither case does the "equal" property produce a stronger
reversal than the isolated-control** — the one borderline-significant difference found (high side,
p=0.056) points in the opposite direction from V0's own prediction.

**(d) Distance-quantile-matched comparison (controls for the proximity confound directly)**: within
every distance quartile, for both sides, equal and isolated reach rates stay within ~1-4 percentage
points of each other with no consistent direction (e.g. high q1: 93.2% vs 94.2%; q4: 89.7% vs 90.0%;
low q4: 90.9% vs 83.5% — the one quartile with a larger gap, but n=55 equal events, too thin to weigh).
**No proximity-driven artifact was found to explain the (null) result — because there is no positive
effect left to explain once distance is matched.**

**(e) Session/volatility slices**: no session (Asia/London/NY/late) or volatility tercile (low/mid/
high) shows equal-highs/lows reaching meaningfully more often than isolated ones — every slice's gap is
within a few percentage points, no consistent direction, consistent with the pooled null finding.

**(f) Asymmetry between highs and lows**: both sides tell the same qualitative story (equal ≈
isolated < random-matched on reach rate; no reversal boost from "equal"), though the high side's
reaction-direction anomaly (equal *less* reversing than isolated, borderline p=0.056) is not mirrored
on the low side (n.s. either way) — a real, disclosed asymmetry, but one that (if anything) works
against V0 on the high side and is simply absent on the low side, not a case of the hypothesis holding
on one side only.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** No supporting signal found on
   either of the two dimensions the registry itself specifies (reach rate, reversal-after-reach). The
   "equal" property does not measurably raise reach rate above an ordinary isolated swing at any
   tolerance or horizon tested, and does not raise reversal magnitude either.
2. **Frequency?** At the primary tolerance (0.15×ATR), ~279 equal-highs pairs and ~263 equal-lows pairs
   over ~2.85 years (~98/yr and ~92/yr respectively) — vs. ~3,792/3,793 isolated (non-equal) pairs of
   the same type, i.e. equal pairs are a small minority (~7%) of all consecutive same-type swing pairs.
3/4. **Days it works/fails?** Not separately sliced by day-of-week in this pass (deferred — session
   and volatility slices were prioritized as the more standard controls; day-of-week showed no signal
   in the closely related E025/E026 passes and was not expected to add new information here).
5. **Sessions?** No session (Asia/London/NY/late) shows a meaningfully elevated equal-vs-isolated
   reach-rate gap.
6. **Volatility regimes?** No volatility tercile shows a meaningfully elevated gap.
7. **Filters that improve it?** Not searched — searching for a filter/tolerance that produces a
   positive result would be exactly the "optimize until profitable" behavior the protocol forbids.
   The tolerance sweep itself (0.10–0.40×ATR) was run as a disclosed sensitivity check, not a search
   for a favorable value, and found no tolerance that changes the conclusion.
8. **Conditions that invalidate it?** The core claim is invalidated broadly: real swing highs/lows
   (equal or not) are reached *less* reliably and far more slowly than a random level at the same
   distance — the entire "swing point = liquidity magnet" framing (not just the "equal" refinement of
   it) is called into question by the random-matched-distance control, though that broader question is
   Category-adjacent to this specific edge (E017 is about the "equal" refinement specifically) and is
   flagged here as a finding relevant to future related edges (E009/E010/E012/E015/E013/E016, all
   structure-pattern edges reusing similar swing-based logic) rather than fully resolved for this edge.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; flagged as a gap, consistent
   with several of the five earlier edges.

## Current status

**Version: V0.** **Verdict: NONE ISSUED.** Per `EDGE_RESEARCH_PROTOCOL.md` §2, no Final Verdict may be
issued below the ~5-6yr horizon; the clean data (~2.85 years) is short of that requirement. This edge
remains in **Stage 2 — Discovery, first pass complete** — **not** Early-Refuted (the protocol allows
Early Refutation as a Final Verdict at Discovery, but §2 blocks ANY Final Verdict, including REFUTED,
below the full horizon; this pass's strong negative evidence is recorded as a Discovery finding, not as
a REFUTED verdict).

**No V1 candidate framing is offered.** Unlike E025/E026/E029/E032/E028, this pass's own evidence does
not suggest a plausible narrower or reversed-condition refinement of V0 worth carrying forward as an
unfrozen candidate — the "equal" distinguishing property itself was tested directly and repeatedly
found to add nothing, across every tolerance and horizon, every session, every volatility regime, and
both distance-matched and unmatched comparisons. If this edge is revisited, the first question should
be whether "equal highs/lows" as a concept is worth pursuing at all, not which narrower condition might
salvage it.

**A finding worth flagging for future, related edges**: the random-matched-distance control's own
result (real swing points reached *less* reliably than an arbitrary matched-distance level) raises a
broader open question about whether swing/fractal-detected points in general carry the "liquidity
pool"/"magnet" significance commonly attributed to them in the source literature this registry draws
from — relevant to E009, E010, E012, E015, E013, E016, E011, E014 (all structure-pattern edges reusing
swing-based logic), though not conclusively resolved here and not itself part of E017's own scope.

**Next steps if revisited**: (a) acquire the Tier-0 history extension for a genuine 5-6yr horizon;
(b) day-of-week slice; (c) formal out-of-time split; (d) if any related structure-pattern edge produces
a similarly-shaped random-matched-distance anomaly, consider a dedicated cross-edge study of that
question rather than re-deriving it independently each time.

**Artifacts**: `e017_equal_highs_lows.py` (analysis script), `e017_equal_highs_lows_results.json` (full
output incl. all tolerances, horizons, slices, and the distance-matched comparison).
