# E012 — Inverted Fair Value Gap

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Price Action / Structure. **Permanent, append-only research log.**

**Second edge run under the CEO's "full edge profile" directive (2026-07-22)**, reusing
`edge_research/_profile.py` (built for E010). Data loaded exclusively via `_common.load()`; no direct
CSV read anywhere in `e012_inverted_fvg.py`.

## V0 (frozen, registered 2026-07-20, verbatim)

> A Fair Value Gap that is fully violated ("inverted") flips role and acts as an opposite-direction
> reaction zone.

Measured outcome (as registered): reaction rate/magnitude at the inverted FVG level vs. a no-reaction
baseline.

## Method (full disclosure in `e012_inverted_fvg.py`)

- **Fair Value Gap (FVG)**, standard 3-bar imbalance: bullish FVG at bar i if low[i] > high[i-2] (zone
  = [high[i-2], low[i]]); bearish FVG if high[i] < low[i-2] (zone = [high[i], low[i-2]]).
- **Inversion**: the first later bar whose CLOSE decisively violates the zone (below its low for a
  bullish FVG, above its high for a bearish one) — V0's own "fully violated."
- **V0 test**: after inversion, does price revisit the zone, and react in the NEW (opposite) direction?
  (`_profile.py::movement_profile()`, same 7 horizons/5 ATR thresholds used for every edge this
  session.)
- **Controls**: (1) **un-inverted-FVG control** — FVGs never fully violated within the test horizon,
  tested for reaction in their ORIGINAL role (the classic "FVG gets touched and holds" story); (2)
  **random-matched-distance control** (seed=42), no real structure.
- **Data split**: `data_split_id = pre_holdout_2025-10-23T09-15-00Z_v1`,
  `holdout_cutoff = 2025-10-23T09:15:00+00:00`, `holdout_excluded = true`.

## A. V0 test — headline result: **NOT SUPPORTED** (and a striking parallel to E010's own finding)

| Timeframe | n inverted FVGs (revisited) | Continuation rate (new direction) | Reversal rate |
|---|---|---|---|
| M15 | 12,433 | **50.0%** | 49.7% |
| H1 | 2,898 | **52.9%** | 47.1% |

After an FVG inverts, price continues in the NEW (opposite) direction almost exactly as often as it
reverses — **a coin flip**, on both timeframes. Favorable/adverse ATR-threshold hit rates are symmetric
at every threshold (e.g. M15, 1.0×ATR: 81.4% vs 82.0%; 2.0×ATR: 65.6% vs 66.2%). **V0's specific
directional claim is not supported**, on either timeframe, at any of 3 gap-size filters, in any session/
volatility/trend/day-of-week slice, or in any year (sections B-D, G).

**The same pattern already found for E010 (Breaker Block Snatch) recurs here, independently**: the
**un-inverted-FVG control** (gaps never fully violated) shows a large, real, directional continuation
effect in their ORIGINAL role — 86.8% (M15) / 86.2% (H1), mean net favorable move +0.48 ATR by 1 bar,
utterly unlike the inverted group's ~50/50 null (χ² p=4.4e-80, M15; p=8.6e-19, H1). **Two independently-
operationalized structural concepts (order blocks in E010, fair value gaps here) now both show the same
qualitative pattern: violating/inverting a structural zone appears to destroy its predictive power
entirely, rather than "flipping" it into a new, opposite-direction edge as both V0s claim** — this
cross-edge consistency is flagged explicitly as a pattern worth keeping in mind for the remaining
structure-pattern edges (E015, E013, E016, E011, E014), several of which share the same "broken zone
flips polarity" framing.

## B. Timeframe profile

| Timeframe | Available? | n inverted | Revisit rate | Continuation rate | vs. random-matched (p) |
|---|---|---|---|---|---|
| M1 | **No** — confirmed unavailable, `EDGE_DISCOVERY_ROADMAP.md` §1 | — | — | — | — |
| M5 | **No** — same reason | — | — | — | — |
| **M15** | Yes | 12,804 | 97.1% | 50.0% | random=96.9%, p=0.360 (n.s.) |
| **H1** | Yes | 2,994 | 96.8% | 52.9% | random=96.8%, p=1.00 (n.s.) |
| H4 / D1 | Not tested — registry's own listed timeframes for this edge are M5/M15/H1 only; not run |

Both timeframes agree closely (continuation ≈50-53%) — the null is not an artifact of one timeframe's
resolution.

## C. Movement profile (M15, inverted group, primary config)

| Horizon (bars) | Mean net return (ATR) | Mean MFE | Mean MAE |
|---|---|---|---|
| 1 | −0.013 | 0.61 | 0.63 |
| 3 | −0.041 | 1.07 | 1.11 |
| 5 | −0.050 | 1.39 | 1.45 |
| 10 | −0.055 | 1.97 | 2.05 |
| 20 | −0.012 | 2.82 | 2.87 |
| 50 | +0.008 | 4.78 | 4.78 |

Mean net return hovers around zero at every horizon; MFE and MAE are almost perfectly symmetric
throughout — the same non-directional signature found for E010's breaker group.

## D. Context profile (M15, inverted group)

| Dimension | Range across slices (continuation rate) | Verdict |
|---|---|---|
| Session | 49.2%–52.0% | No effect |
| Volatility regime | 49.6%–50.3% | No effect |
| Trend context | 49.9%–51.1% | No effect |
| Day of week | 49.8%–50.3% | No effect |

H1's own slices are slightly noisier (47.1%-56.1%, smaller n) but show no consistent, reliable
directional pattern either. As with E010, position-in-daily-range/prior-day-range/gap-bucket slices
were not separately run this pass, given the pooled and every-other-tested-slice result is already flat
— a disclosed scope choice, not a hidden gap.

## E. Controls and falsification

- **Un-inverted-FVG control**: real, large, directional effect (section A) — proves this methodology
  can detect a genuine edge when one exists.
- **Random-matched-distance control**: revisit rate indistinguishable from inverted FVGs on both
  timeframes (M15 p=0.360, H1 p=1.00) — consistent with every other edge studied this program; the
  null is in the *reaction*, not the *revisit*.
- **Explanations ruled out as sufficient alone**: proximity, trend, volatility, session timing, and
  gap-size selection (0.0/0.1/0.25×ATR minimum filters all ~50%, section G) — none recovers a
  directional edge.

## F. Edge improvement search (V1)

No V1 candidate found. The effect is null across every gap-size filter, timeframe, session, volatility
regime, trend context, day of week, and year (section G). No combination search was run to hunt for a
favorable segment. **Declared: NO V1 CANDIDATE.**

The un-inverted-FVG continuation effect (section A) is not proposed as E012's own V1 — same reasoning
as E010: it tests a different (in effect, opposite) hypothesis and belongs to a separate future edge if
opened, not folded in here.

## G. Robustness (inverted group, M15 unless noted)

- **Gap-size sensitivity**: continuation 50.0% (no filter, n=12,804), 50.2% (≥0.1×ATR, n=9,972), 50.4%
  (≥0.25×ATR, n=6,748) — flat across a ~2× range in event count; no favorable filter exists or was
  selected.
- **Yearly stability**: 2022 (n=169, thin) 47.6%; 2023 (n=4,454) 50.3%; 2024 (n=4,524) 50.2%; 2025
  (n=3,657) 49.6% — stable at ~50% every full year. H1: 2023 53.4%, 2024 51.2%, 2025 54.4% (n=883-1,072)
  — mildly above 50% every year but never far from it and not treated as a real deviation without
  further evidence (same posture as E010's own mild 2025 H1 uptick).
- **Concentration risk**: near-uniform ~50% across thousands of events per slice — not produced by a
  handful of extreme observations.
- **Multiple-testing risk**: many slices tested, uncorrected; but since every slice independently lands
  near 50% rather than a few reaching significance by chance, this is not a concern for the negative
  conclusion specifically (uncorrected multiple testing risks false positives, not false negatives).
- **Cost/slippage impact**: not modeled — moot, no directional edge for costs to erode.

## H. Practical profile

**What it is**: a claim that a Fair Value Gap, once fully closed through, flips into an opposite-
direction reaction zone. **When it appears**: whenever an FVG later gets fully violated — very common
(12,804 events on M15 alone). **Timeframe**: clear on both M15 and H1; M1/M5 unavailable. **Session/
regime**: uniformly a coin flip everywhere tested. **Average movement**: statistically zero net
directional movement; MFE≈MAE at every horizon. **Frequency**: very common, not rare. **Controls**: the
random-matched-distance control shows revisit alone isn't special (consistent with every other edge
this program); the un-inverted-FVG control shows the methodology can detect a real effect, sharpening
the null found for inversion specifically. **Can it be used alone?** No. **Needs context?** No context
tested rescues it. **V1 candidate?** None. **Confidence level**: high confidence in the null — consistent
across timeframes, gap-size filters, sessions, regimes, trend contexts, days, and years, with the
methodology's own sensitivity demonstrated by the un-inverted control. **Key limitation**: below the
protocol's ~5-6yr horizon (clean data ~2.85yr); no formal out-of-time split beyond the yearly breakdown;
the FVG/inversion operational definitions are one disclosed, standard choice, not the only possible one.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** No — the inverted-FVG reaction is statistically indistinguishable
   from a coin flip on every tested dimension.
2. **Frequency?** Very common — 12,804 inverted-FVG events on M15 alone over ~2.85 years.
3/4. **Days it works/fails?** No day-of-week distinction found.
5. **Sessions?** No session distinction found.
6. **Volatility regimes?** No regime distinction found.
7. **Filters that improve it?** None found across gap-size, timeframe, session, volatility, trend,
   day-of-week, or year.
8. **Conditions that invalidate it?** The entire concept, as operationalized, is invalidated broadly.
9. **Out-of-sample?** Yearly breakdown (section G) is the closest available check and shows the null
   holding in every full year; no additional formal out-of-time split run (redundant given this).

## Current status

**Version: V0.** **Verdict: NONE ISSUED** — per protocol §2, below the ~5-6yr horizon. Remains in
**Stage 2 — Discovery, full profile complete**.

**V0 NOT SUPPORTED — NO V1 CANDIDATE.** Not modified to rescue it. Preserved permanently, alongside the
un-inverted-FVG comparator finding.

**Next steps if revisited**: (a) Tier-0 history extension; (b) a dedicated, separately-registered future
edge testing the un-inverted-FVG continuation effect found here (real, large, robust, but not this
edge's own V0) — noting this is now the SECOND such finding this session (after E010's unflipped-OB
effect), suggesting a possible unifying future edge: "unbroken structural zones (of any kind) predict
continuation; broken/flipped ones predict nothing"; (c) a stricter/alternative FVG detection convention
if a future revisit wants to test sensitivity to that specific choice.

**Artifacts**: `e012_inverted_fvg.py`, `e012_inverted_fvg_results.json` (full output, both timeframes,
all slices, sensitivity, and yearly stability).

## Scope clarification (added 2026-07-22, Protocol v2 — `EDGE_RESEARCH_PROTOCOL.md` §9)

**This study is structural-behavior Discovery, not direct scalping validation.** It tested whether an
FVG inversion carries a statistically distinguishable directional signal over multi-bar/multi-day
horizons (§§1-8 of the protocol) — it did NOT test whether the market recognizes the concept
immediately, or whether it (or the un-inverted-FVG comparator, CEC-001) produces a mechanically-defined,
cost-aware scalp trade reaching TP=2R before SL=1R within minutes (the new §9 question). No such test
has been run for this edge; §9's own tests are currently blocked project-wide (no M1/M5/tick data
exists — §9.6). This note does not change this edge's own V0 result, verdict, or status above, all of
which stand unedited.
