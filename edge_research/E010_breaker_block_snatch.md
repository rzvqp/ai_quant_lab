# E010 — Breaker Block Snatch

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md`.
**Category**: Price Action / Structure. **Permanent, append-only research log.**

**First edge run under the CEO's "full edge profile" directive (2026-07-22, overnight authorization)**:
beyond a binary V0 test, this log covers a timeframe profile, a movement profile (7 horizons × 5 ATR
thresholds), a context profile, controls/falsification, a V1 search, and robustness checks, per that
authorization's sections A-H. Data loaded exclusively via `_common.load()`; no direct CSV read anywhere
in `e010_breaker_block_snatch.py`.

## V0 (frozen, registered 2026-07-20, verbatim)

> A failed order block that flips polarity ("breaker") is often revisited and respected as
> support/resistance in the opposite direction.

Measured outcome (as registered): rate at which the breaker level produces a reaction, and reaction
magnitude.

## Method (full disclosure in `e010_breaker_block_snatch.py` / `_profile.py`)

- **Order block (OB)**: a displacement bar with range > 1.5×ATR14(prior bar) and a strong directional
  body (≥50% of its own range); the last opposite-colored bar within the preceding 10 bars is the OB
  zone. 1.5×/50%/10-bar are plain, disclosed defaults, swept for sensitivity (1.2×/1.5×/2.0×), not
  searched for a favorable result.
- **Breaker flip**: the first later bar whose CLOSE decisively violates the OB zone (below its low for
  a bullish OB, above its high for a bearish OB) — this is V0's own "failed order block."
- **V0 test**: after the flip, does price revisit the zone, and does it react in the NEW (flipped)
  direction? (`_profile.py::movement_profile()`, 7 horizons {1,3,5,10,20,50} bars, 5 ATR thresholds
  {0.25,0.5,1.0,1.5,2.0}, outcome classified continuation/reversal/stall at the 1.0×ATR reference.)
- **Controls**: (1) **unflipped-OB control** — OBs never later violated within the test horizon, tested
  for reaction in their ORIGINAL (unbroken) polarity — the natural "is flipping itself special"
  baseline; (2) **random-matched-distance control** (seed=42) — synthetic zones at random locations,
  distance-matched to the breaker group's own empirical distribution, no real structure at all.
- **Data split**: `data_split_id = pre_holdout_2025-10-23T09-15-00Z_v1`,
  `holdout_cutoff = 2025-10-23T09:15:00+00:00`, `holdout_excluded = true`.

## A. V0 test — headline result: **NOT SUPPORTED**

| Timeframe | n breakers (revisited) | Continuation rate (new direction) | Reversal rate | Stall rate |
|---|---|---|---|---|
| M15 | 5,604 | **49.9%** | 49.9% | 0.2% |
| H1 | 1,478 | **51.4%** | 48.6% | 0.0% |

After a breaker flip, price continues in the NEW (flipped) direction almost exactly as often as it
reverses back — **a coin flip, on both tested timeframes**. The favorable/adverse ATR-threshold hit
rates tell the identical story at every threshold (e.g. M15, 1.0×ATR: favorable 80.2% vs adverse 81.0%;
2.0×ATR: 64.7% vs 64.3% — always within ~1 point of each other). **V0's specific directional claim is
not supported by this pass's evidence, on either timeframe, at any displacement threshold, in any
session/volatility/trend/day-of-week slice, or in any year of the sample** (see sections B-D, G).

**A striking, unplanned finding from the natural control**: the **unflipped-OB control** (ordinary
order blocks that were never violated) shows a **large, real, directional continuation effect in their
ORIGINAL polarity** — 88.0% (M15) / 86.2% (H1) continuation rate, with a mean net favorable move of
**+1.03 ATR by just 1 bar after the revisit** (M15) — utterly unlike the breaker group's ~50/50 null.
The gap between breaker (49.9%) and unflipped (88.0%) continuation rates is enormous and overwhelming
(χ²-test p=5.9e-119, M15; p=3.6e-30, H1). **This suggests that violating an order block does not
"flip its polarity to a new, opposite-direction magnet" as V0 claims — it appears to simply destroy the
level's predictive power entirely**, while an ordinary, never-violated order block carries a real,
strong, directional edge of its own (a different hypothesis than E010's own V0, flagged below as a
candidate for a future, separately-registered edge, not folded into E010's own V1).

## B. Timeframe profile

| Timeframe | Available? | n breakers | Revisit rate | Continuation rate | vs. random-matched revisit rate (p) |
|---|---|---|---|---|---|
| M1 | **No** — not present anywhere in this project's data (`EDGE_DISCOVERY_ROADMAP.md` §1's own established gap finding, re-confirmed here, not re-derived) | — | — | — | — |
| M5 | **No** — same reason | — | — | — | — |
| **M15** | Yes | 5,833 | 96.1% | 49.9% | random=95.5%, p=0.128 (n.s.) |
| **H1** | Yes | 1,550 | 95.3% | 51.4% | random=95.3%, p=1.00 (n.s.) |
| H4 / D1 | Not tested — the registry's own listed timeframes for this edge are M5/M15/H1 only; H4/D1 would produce very few events over a 2.85yr window and were not run this pass | — | — | — | — |

Both tested timeframes agree closely (continuation ≈50-51%, revisit ≈95-96%) — **the null result is
not an artifact of one timeframe's own resolution**; M15's finer granularity does not surface a
directional edge that H1's coarser view misses, or vice versa. Per the CEO's own instruction, the
timeframe with the "biggest" number is not treated as automatically best — here neither timeframe shows
a real effect at all, so there is no favorable timeframe to (mis)report.

## C. Movement profile (M15, breaker group, primary config)

| Horizon (bars) | Mean net return (ATR, signed toward predicted direction) | Mean MFE | Mean MAE |
|---|---|---|---|
| 1 | +0.005 | 0.64 | 0.65 |
| 3 | +0.027 | 1.13 | 1.11 |
| 5 | −0.005 | 1.45 | 1.44 |
| 10 | +0.012 | 2.00 | 2.00 |
| 20 | −0.010 | 2.79 | 2.77 |
| 50 | +0.150 | 4.63 | 4.46 |

Mean net return hovers around zero at every horizon (the largest, at 50 bars, +0.15 ATR, is small
relative to the ~4.5 ATR of MFE/MAE churn already accumulated by then) — **MFE and MAE are almost
perfectly symmetric at every horizon**, the clearest possible signature of a non-directional, noise-like
process. ATR-threshold hit rates (favorable vs. adverse) are likewise symmetric at every threshold
tested (0.25/0.5/1.0/1.5/2.0×ATR) — see the table in section A. Median time-to-favorable-threshold rises
from same-bar (0.25×ATR) to 8 bars (2.0×ATR), unremarkable and matched almost exactly by the adverse
side's own timing (not separately tabulated here — see the JSON `by_threshold` block for exact figures).

## D. Context profile (M15, breaker group)

| Dimension | Range across slices (continuation rate) | Verdict |
|---|---|---|
| Session (Asia/London/NY/late) | 48.6%–50.7% | No session shows a real effect |
| Volatility regime (low/mid/high) | 49.2%–52.4% | No regime shows a real effect |
| Trend context (bull/bear/range, 20-bar EMA-slope) | 48.8%–51.8% | No trend context shows a real effect |
| Day of week | 48.5%–51.6% | No day shows a real effect |

Every single slice sits within ~1-3 percentage points of 50% — **no context dimension recovers a
directional edge the pooled result hides**. Per the CEO's own instruction not to introduce arbitrary
segments without justification: position-in-daily-range, prior-day-range bucket, and gap-from-close
bucket were **not** separately sliced this pass — with the pooled effect already indistinguishable from
noise on every tested dimension, and no theoretical reason to expect one of the untested dimensions to
reverse that, further slicing was judged unlikely to be informative and was deprioritized in favor of
completing the robustness checks (section G) within this session's time budget. This is a disclosed
scope choice, not a hidden gap.

## E. Controls and falsification

- **Unflipped-OB control**: real, large, directional effect (see section A) — the natural comparator
  shows this methodology CAN detect a genuine directional edge when one exists; its absence for the
  breaker group is therefore not an artifact of insensitive measurement.
- **Random-matched-distance control**: revisit rate statistically indistinguishable from breakers on
  both timeframes (M15 p=0.128, H1 p=1.00) — consistent with the same "close levels get revisited
  regardless of structure" pattern already found in E017/E009, and not itself the source of the
  direction-null (which comes from the *reaction*, not the *revisit*, dimension).
- **Explanations tested and ruled out as sufficient on their own**: proximity (random control shows
  revisit alone isn't special; the null is in reaction direction, not revisit rate), trend (bull/bear/
  range slices all ~50%), volatility (all terciles ~50%), session timing (all sessions ~50%),
  displacement-selection sensitivity (1.2×/1.5×/2.0× all ~50%, section G). **A positive raw revisit
  rate (95-96%) was not treated as evidence of a real edge** — exactly the check the CEO's own
  authorization required — because the reaction dimension it would need to pair with is absent.

## F. Edge improvement search (V1)

No V1 candidate was found for E010's own V0 (breaker-flip directional reaction) — the effect is null
across every tested displacement threshold, timeframe, session, volatility regime, trend context, day
of week, and year (section G); there is no objective, predefined subset in which it recovers to a
real, non-coin-flip rate. Per the CEO's own rules, no combination search was run to hunt for a
favorable segment (which would violate rule F.1/F.2), and no V0 modification was made retroactively
(rule F.3). **Declared: NO V1 CANDIDATE.**

The unflipped-OB continuation effect (section A) is NOT proposed as E010's own V1 — it tests a
different, in some sense opposite, hypothesis (unbroken order blocks, not broken/flipped ones) and
belongs to a separate, future, explicitly-registered edge if the CEO chooses to open one — folding it
in here would violate the "no V0 modification" rule by quietly substituting a different claim.

## G. Robustness (breaker group, M15 unless noted)

- **Displacement-threshold sensitivity**: continuation rate 50.1% (1.2×ATR, n=9,684), 49.9% (1.5×ATR,
  n=5,833), 50.5% (2.0×ATR, n=2,594) — flat across a nearly 4× range in event count. No favorable
  threshold exists; none was selected.
- **Yearly subperiod stability**: 2022 (n=77, thin) 41.6%; 2023 (n=2,108) 48.6%; 2024 (n=2,021) 50.8%;
  2025 (n=1,627) 50.9%. Aside from the very thin 2022 partial year, every full year sits at ~49-51% —
  **stable across the sample, not concentrated in one period**. H1's own yearly breakdown (2023 49.6%,
  2024 50.2%, 2025 55.4%, n=429) shows a mild uptick in 2025 but remains close to 50% and is based on a
  smaller H1 sample; not treated as a real deviation without further evidence.
- **Cost/slippage impact**: not modeled — consistent with Discovery-stage scope (statistical reaction
  only, per protocol §0.2), and moot here regardless, since there is no directional edge for costs to
  erode.
- **Concentration risk**: outcome rates are near-uniformly ~50% across thousands of events in every
  slice — this null is not produced by a handful of extreme observations.
- **Multiple-testing risk**: many slices were tested (sessions, volatility, trend, day-of-week, years,
  3 displacement thresholds, 2 timeframes) with no correction applied; however, since EVERY slice
  independently lands near 50% rather than a few reaching significance by chance, multiple-testing
  inflation is not a concern for this pass's own (negative) conclusion — false positives, not false
  negatives, are what uncorrected multiple testing would normally risk producing.

## H. Practical profile

**What it is**: a claim that an order block violated by price ("broken," then closed through) flips
into an opposite-direction reaction zone. **When it appears**: whenever a displacement candle's own
originating order block later gets closed through — frequent (5,833 events on M15 alone over 2.85
years). **Timeframe**: tested clearly on M15 and H1; M1/M5 unavailable in this project. **Session/
regime**: no session or regime makes it stronger or weaker — it is uniformly a coin flip everywhere
tested. **Average movement produced**: statistically zero net directional movement; MFE ≈ MAE at every
horizon out to 50 bars. **Adverse risk**: symmetric with the (absent) favorable side — there is no
asymmetric edge to size a trade against. **Frequency**: common, not rare. **Controls**: the
random-matched-distance control shows the *revisit* itself isn't special (generic proximity behavior,
consistent with other edges studied this program); the unflipped-OB control shows this methodology
*can* detect a real directional effect when one exists, which sharpens rather than weakens the null
found for breakers specifically. **Can it be used alone?** No — no signal to use. **Needs context?**
No context tested rescues it. **V1 candidate?** None. **Confidence level**: high confidence in the null,
given the consistency across timeframes, thresholds, sessions, regimes, trend contexts, days, and years,
and given the same methodology's own demonstrated sensitivity (via the unflipped-OB control). **Key
limitation**: below the protocol's ~5-6yr horizon (clean data ~2.85yr); no out-of-time formal split run
(the yearly breakdown in section G is the closest proxy); the OB-detection operational definition
(1.5×ATR/50%-body/10-bar-lookback) is one disclosed, reasonable choice among several a stricter ICT
practitioner might use differently.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all?** No — the breaker-flip reaction is statistically indistinguishable
   from a coin flip on every tested dimension.
2. **Frequency?** Common — 5,833 breaker events on M15 alone over ~2.85 years (~2 per trading day).
3/4. **Days it works/fails?** No day-of-week distinction found (48.5-51.6% range, all ~coin-flip).
5. **Sessions?** No session distinction found.
6. **Volatility regimes?** No regime distinction found.
7. **Filters that improve it?** None found across displacement threshold, timeframe, session,
   volatility, trend, day-of-week, or year — searched broadly (as robustness checks, not as a hunt for
   a favorable result) and none recovered a real effect.
8. **Conditions that invalidate it?** The entire concept, as operationalized, is invalidated broadly —
   not a specific sub-condition.
9. **Out-of-sample?** The yearly breakdown (section G) is the closest available check in this pass and
   shows the null holding in every full year; a formal, dedicated out-of-time split was not additionally
   run (redundant given the year-by-year stability already shown).

## Current status

**Version: V0.** **Verdict: NONE ISSUED** — per protocol §2, below the ~5-6yr horizon (clean data
~2.85yr). Remains in **Stage 2 — Discovery, full profile complete**.

**V0 NOT SUPPORTED — NO V1 CANDIDATE.** The hypothesis is not modified to rescue it. This negative
result, and the unflipped-OB comparator finding, are preserved permanently.

**Next steps if revisited**: (a) Tier-0 history extension for a genuine 5-6yr horizon; (b) a dedicated,
separately-registered future edge testing the unflipped-OB continuation effect found here as a
byproduct (a real, large, robust effect, but not this edge's own V0); (c) a stricter/alternative OB
detection convention, if a future revisit wants to test sensitivity to that specific operational choice.

**Artifacts**: `e010_breaker_block_snatch.py`, `e010_breaker_block_snatch_results.json` (full output,
both timeframes, all slices, sensitivity, and yearly stability), `_profile.py` (new shared profiling
library, reused by all edges studied under this directive going forward).

## Scope clarification (added 2026-07-22, Protocol v2 — `EDGE_RESEARCH_PROTOCOL.md` §9)

**This study is structural-behavior Discovery, not direct scalping validation.** It tested whether a
breaker-block flip carries a statistically distinguishable directional signal over multi-bar/multi-day
horizons (§§1-8 of the protocol) — it did NOT test whether the market recognizes the concept
immediately, or whether it (or the unflipped-OB comparator, CEC-001) produces a mechanically-defined,
cost-aware scalp trade reaching TP=2R before SL=1R within minutes (the new §9 question). No such test
has been run for this edge; §9's own tests are currently blocked project-wide (no M1/M5/tick data
exists — §9.6). This note does not change this edge's own V0 result, verdict, or status above, all of
which stand unedited.
