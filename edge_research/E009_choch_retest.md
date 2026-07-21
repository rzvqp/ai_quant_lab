# E009 — Change of Character (CHoCH) Retest

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Price Action / Structure. **This file is the permanent, append-only research log for
this edge — nothing below is ever deleted or retroactively edited; refinements are new, dated, appended
versions.**

**Note on this edge's own authorization history**: an earlier message in this session referenced
"E009 — Previous Day High / Previous Day Low," which does not exist anywhere in
`EDGE_DISCOVERY_REGISTRY_v1.md` (verified directly, reported back, and withdrawn by explicit CEO
decision before any research began). This log studies the registry's own actual, frozen E009 only.

## V0 (frozen, registered 2026-07-20, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> After a Change of Character (CHoCH) signals a possible trend shift, price frequently retests the
> CHoCH level before continuing in the new direction.

Measured outcome (as registered): retest rate, and continuation-vs-failure rate after the retest.

## Discovery pass 1 (2026-07-21)

**Split metadata** (`e009_choch_retest_results.json`): `data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`, `holdout_cutoff = 2025-10-23T09:15:00+00:00`,
`holdout_excluded = true`, `min_date_used = 2022-12-16 10:45:00 UTC`,
`max_date_used = 2025-10-23 09:00:00 UTC`, `n_bars_used = 67,321` (of 84,152; 16,831 holdout bars
excluded), `loader_version = flowA_common_v2_holdout_enforced_2026-07-21`. ~2.85 years — short of the
protocol's §2 ~5-6yr requirement; this is a Discovery-stage first pass, not a Final-Verdict-eligible
run. Loaded exclusively via `_common.load()` — no direct CSV read anywhere in `e009_choch_retest.py`.

**Method** (full disclosure in `e009_choch_retest.py`):
- Swing (fractal) detection: k=5 primary (same disclosed method as E017/E028), swept at k∈{3,5,8} for
  a sensitivity check. 6,533 swings at k=5.
- **Mechanical BOS/CHoCH classification**, standard ICT/SMC definition, over the zigzag sequence: a
  trend state ('up'/'down') is bootstrapped once 2 confirmed highs and 2 confirmed lows exist, then:
  trend='up' + new low breaks below the immediately preceding low → **CHoCH-down** (trend flips to
  'down'); trend='down' + new high breaks above the immediately preceding high → **CHoCH-up**
  (symmetric); trend='up' + new high breaks above the preceding high → **BOS-up** (ordinary
  continuation, trend unchanged); trend='down' + new low breaks below the preceding low → **BOS-down**
  (symmetric). A swing that doesn't break the relevant reference (e.g. a lower high forming inside an
  uptrend) produces no event. At k=5: **1,902 CHoCH events, 1,263 BOS events**.
- **On-topic control — BOS**: both CHoCH and BOS are real, confirmed breaks of a real swing level; the
  only difference is whether the break agrees with (BOS) or contradicts (CHoCH) the preceding trend.
  Grouping by the level type broken (a low broken downward = "low-break," tested identically whether
  CHoCH-down or BOS-down; a high broken upward = "high-break," symmetric) keeps retest/continuation
  mechanics identical across the CHoCH-vs-BOS comparison — only the `kind` label differs, directly
  testing whether CHoCH-ness itself adds anything beyond an ordinary structural break.
- **Second, stronger control — RANDOM-MATCHED-DISTANCE** (seed=42): synthetic levels at random bar
  locations, distance (ATR units) resampled from the CHoCH group's own empirical distribution — no real
  structure at all. Tests whether retest is just generic proximity/travel behavior.
- **Retest** = price ever touches/exceeds the broken level within a horizon (96/480/1920 M15 bars ≈
  1/5/20 trading days). **Continuation** = after the retest (or from the break itself if no retest),
  price makes a NEW EXTREME beyond the original break price within a further horizon — V0's own
  "continuing in the new direction" claim, tested directly.

## Headline result — V0 is NOT supported: CHoCH shows no retest-rate, continuation-rate, or
failure-rate advantage over an ordinary BOS break, at any tested granularity, horizon, session, or
volatility regime — and the retest metric itself is revealed to be a near-ceiling, largely
non-discriminating measurement at this swing scale (an important, disclosed methodological finding
in its own right)

**(a) Primary comparison (k=5, horizon=480/5 days) — CHoCH vs. BOS, both level types:**

| Group | n CHoCH | n BOS | CHoCH retest rate | BOS retest rate | p (retest) | CHoCH continuation rate | BOS continuation rate | p (continuation) |
|---|---|---|---|---|---|---|---|---|
| Low-break (bearish CHoCH / bearish BOS) | 1,902 | 1,263 | 97.3% | 97.7% | 0.516 | 89.3% | 90.7% | 0.220 |
| High-break (bullish CHoCH / bullish BOS) | 1,902 | 1,263 | 95.5% | 95.9% | 0.648 | 93.3% | 93.8% | 0.586 |

No comparison reaches significance; every point estimate sits within 1-2 percentage points of its
counterpart, with BOS numerically (non-significantly) *higher* than CHoCH on every metric in both
groups — the opposite direction from what "CHoCH is special" would predict, though not itself a
significant finding.

**(b) Retest rate is saturated (near-ceiling) at every horizon tested, including the shortest — this
limits how much the retest dimension alone can discriminate anything:**

| Group | Horizon | CHoCH retest | BOS retest | Random-matched retest |
|---|---|---|---|---|
| Low-break | 96 (1d) | 93.3% | 94.7% | — |
| Low-break | 480 (5d) | 97.3% | 97.7% | **97.1%** |
| Low-break | 1920 (20d) | 99.3% | 99.0% | — |
| High-break | 96 (1d) | 91.4% | 90.3% | — |
| High-break | 480 (5d) | 95.5% | 95.9% | **94.1%** |
| High-break | 1920 (20d) | 96.5% | 97.2% | — |

Even at the shortest horizon (1 trading day), retest rates sit at 90-95% for real breaks. **The
random-matched-distance control** (no real swing/structure, same ATR-distance profile as real CHoCH
events) reaches 97.1% (low-break) and 94.1% (high-break) — statistically indistinguishable from the
real CHoCH rate in both cases (p=0.770 low-break, p=0.068 high-break, the latter borderline but in the
direction of the REAL levels retesting *less*, not more, than random — the opposite of E017's own
finding, where random beat real more clearly; this reversal is reported, not smoothed over, and is
plausibly explained by E009's levels being much closer on average — median distance <1 ATR — than
E017's, pushing this measurement further into the ceiling zone for all three groups alike).
**Disclosed methodological limitation**: at k=3/5/8, the immediately-preceding same-type swing is
typically close enough in price that "retest" (an intrabar touch, no time limit under 20 trading days)
is close to a foregone conclusion regardless of CHoCH/BOS/random status — this pass's own retest metric
has limited room left to detect a true effect even if one existed, at this operational definition and
swing scale. This is disclosed as an open question for any future revisit (see "Next steps"), not
resolved in this pass.

**(c) Fractal-k sensitivity (3/5/8) — same null pattern at every granularity tested, no favorable k
found or searched for:**

| k | Low-break: CHoCH vs BOS retest | p | High-break: CHoCH vs BOS retest | p |
|---|---|---|---|---|
| 3 | 97.3% vs 96.5% | 0.287 | 94.9% vs 95.1% | 0.866 |
| 5 (primary) | 97.3% vs 97.7% | 0.516 | 95.5% vs 95.9% | 0.648 |
| 8 | 95.0% vs 95.8% | 0.703 | 92.6% vs 91.5% | 0.594 |

**(d) Session/volatility slices**: no session (Asia/London/NY/late) or volatility tercile shows a
meaningful CHoCH-vs-BOS gap on retest or continuation, for either level type — every slice sits within
1-4 percentage points with no consistent direction.

**(e) Compound outcome rates (retest-then-continue / retest-then-fail / no-retest at all) — the fuller
picture V0's own "retest... before continuing" claim implies, tested directly, still no CHoCH
advantage:**

| Group | CHoCH retest-then-continue | BOS retest-then-continue | CHoCH retest-then-fail | BOS retest-then-fail | CHoCH no-retest | BOS no-retest |
|---|---|---|---|---|---|---|
| Low-break | 86.6% | 88.4% | 10.7% | 9.3% | 2.7% | 2.3% |
| High-break | 88.7% | 89.7% | 6.7% | 6.2% | 4.5% | 4.1% |

CHoCH events are, if anything, marginally (non-significantly) *more* likely than BOS to retest and then
**fail** to continue (10.7% vs 9.3% low-break; 6.7% vs 6.2% high-break) — a small, disclosed hint in the
opposite direction from V0, not itself statistically decisive (see part (a) above — the underlying
continuation-rate difference this compound figure is built from was p=0.220/0.586, not significant).

**(f) Asymmetry between low-break and high-break**: qualitatively identical story on both sides — no
CHoCH advantage, similarly saturated retest rates, similarly non-significant compound-outcome gaps. The
one directional difference worth noting (part (b)) is the high-break group's borderline
real-vs-random comparison trending toward real levels retesting *less* than random, not seen as clearly
on the low-break side — thin evidence, not treated as a confirmed asymmetry.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** No supporting signal found. CHoCH does not retest, continue, or
   fail-after-retest at a rate distinguishable from an ordinary BOS break, at any tested k, horizon,
   session, or volatility regime.
2. **Frequency?** At k=5: 1,902 CHoCH events and 1,263 BOS events per level type (low-break and
   high-break each), over ~2.85 years — CHoCH is actually the MORE common event type here (60% of
   all classified breaks), not a rare special case, since this sample's price action is choppy enough
   that trend reversals (by this mechanical definition) happen often.
3/4. **Days it works/fails?** Not separately sliced by day-of-week in this pass (deferred, consistent
   with E017 — session and volatility were prioritized as the more standard controls).
5. **Sessions?** No session shows a meaningfully elevated CHoCH-vs-BOS gap on any metric.
6. **Volatility regimes?** No volatility tercile shows a meaningfully elevated gap.
7. **Filters that improve it?** Not searched — the k-sensitivity sweep was run to check robustness,
   not to hunt for a favorable value, and found none across the tested range.
8. **Conditions that invalidate it?** The core claim is invalidated broadly: CHoCH's distinguishing
   property (contradicting vs. agreeing with the preceding trend) does not measurably change retest,
   continuation, or failure behavior relative to BOS, at any setting tested.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass; flagged as a gap, consistent
   with several earlier edges.

## Current status

**Version: V0.** **Verdict: NONE ISSUED.** Per `EDGE_RESEARCH_PROTOCOL.md` §2, no Final Verdict may be
issued below the ~5-6yr horizon; the clean data (~2.85 years) is short of that requirement. This edge
remains in **Stage 2 — Discovery, first pass complete**.

**V0 NOT SUPPORTED — NO V1 CANDIDATE.** Consistent with the CEO's own accepted interpretation of E017,
this pass's own evidence does not suggest a plausible narrower or reversed-condition refinement of V0
worth carrying forward as an unfrozen candidate. CHoCH's defining property (a structural break against
rather than with the preceding trend) was tested directly against its most natural real-world control
(BOS, a same-mechanism break WITH the trend) and repeatedly found to make no measurable difference. The
hypothesis is not modified to rescue it, per standing instruction; this negative result is preserved
permanently as the Discovery finding for this pass.

**A methodological finding worth flagging for future edges (not itself part of E009's scope)**: the
retest metric, as operationalized here (touch the immediately-preceding same-type swing, any horizon up
to 20 trading days), is close to saturated (90%+) for real structural breaks AND for a random,
distance-matched, no-structure control alike. This limits this pass's own power to detect a true CHoCH
effect on the retest dimension specifically, even though the continuation and compound-outcome
dimensions (less saturated, 86-94%) told the same null story independently. Any future revisit of a
"retest"-flavored edge (this registry's other structure-pattern edges — E010, E012, E015, E013, E016,
E011, E014 — may share this concern) should consider either a much coarser swing definition or a
stricter retest criterion (e.g. a confirmed close beyond the level, not an intrabar touch) to leave more
room for a genuine effect to be detected.

**Next steps if revisited**: (a) acquire the Tier-0 history extension for a genuine 5-6yr horizon;
(b) day-of-week slice; (c) formal out-of-time split; (d) a stricter, close-based retest definition to
address the saturation concern above.

**Artifacts**: `e009_choch_retest.py` (analysis script), `e009_choch_retest_results.json` (full output
incl. all k values, horizons, slices, and the random-matched control).

## Scope clarification (added 2026-07-22, Protocol v2 — `EDGE_RESEARCH_PROTOCOL.md` §9)

**This study is structural-behavior Discovery, not direct scalping validation.** It tested whether
CHoCH retests carry a statistically distinguishable directional signal over multi-bar/multi-day
horizons (§§1-8 of the protocol) — it did NOT test whether the market recognizes the concept
immediately, or whether it produces a mechanically-defined, cost-aware scalp trade reaching TP=2R
before SL=1R within minutes (the new §9 question). No such test has been run for this edge; §9's own
tests are currently blocked project-wide (no M1/M5/tick data exists — §9.6). This note does not change
this edge's own V0 result, verdict, or status above, all of which stand unedited.
