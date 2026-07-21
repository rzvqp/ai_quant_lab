# E008 — Friday Profit Taking Shift

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Protocol**: `EDGE_RESEARCH_PROTOCOL.md` §§1-8
only — §9 (Immediate Scalping Response / Protocol v2) explicitly NOT performed, per the CEO's own
priority-shift instruction. **Category**: Session Timing. **This file is the permanent, append-only
research log for this edge — nothing below is ever deleted or retroactively edited; refinements are
new, dated, appended versions.**

**Third edge run under the reordered Tier-1 sequence** (`NEXT_SESSION_FLOW_A.md`, 2026-07-21 priority
audit). Only E008 authorized this session. Data loaded exclusively via `_common.load()`
(holdout-enforced); no direct CSV read anywhere in `e008_friday_profit_taking.py`.

## V0 (frozen, verbatim from `EDGE_DISCOVERY_REGISTRY_v1.md`)

> Friday afternoon shows a distinct behavior pattern caused by position-closing flows ahead of the
> weekend.

Measured outcome (as registered): change in directional persistence/volatility on Friday afternoon vs.
the rest of the week. Observable variables: time-of-day within Friday, week's prevailing trend
direction, volatility regime, week-of-month.

## Definitions predeclared BEFORE any outcome was inspected

1. **"Afternoon" window**: bars tagged `session` in {'ny','late'} (UTC hour ≥ 13) on a given calendar
   date — the NY-through-close period, the natural "position-closing before the weekend" window. Exists
   for every weekday, giving a direct, matched (same time-of-day) comparison.
2. **Directional persistence metric**: an efficiency ratio (Kaufman-style, disclosed) —
   `net_move / path_length`, where `net_move` is the absolute close-to-close move across the whole
   window and `path_length` is the sum of absolute bar-to-bar moves within it. 0 = pure chop, 1 =
   perfectly one-directional.
3. **Volatility metric**: `path_length / ATR14-at-window-start` — total intra-window movement,
   ATR-normalized.
4. **Week's prevailing trend direction**: sign of close(second-to-last trading day of the week) minus
   open(Monday), same week — a context feature, not part of the primary detector.
5. **Week-of-month context**: whether the date falls in the last trading week of its calendar month.
6. **Time-of-day within Friday**: Friday's own window is split into 'ny' and 'late' sub-sessions
   (bar-count check only in this pass).
7. **Primary comparison**: Friday's afternoon efficiency-ratio and volatility distributions vs. pooled
   Monday-Thursday, via Mann-Whitney U (first edge in this program needing a continuous-distribution
   test rather than a binary rate). A full day-of-week ladder (each weekday vs. the other four) is
   also reported.
8. **Falsification/placebo control**: a permutation-based placebo — randomly relabel ~1/5 of trading
   days (seed=42, matching Friday's own share) as "pseudo-Friday," compare against the rest with the
   identical test, to establish the chance noise floor for a 1-vs-4 group comparison at this sample size.
9. **Reversal-of-week's-trend test**: for every day, does its own afternoon move oppose the sign of the
   trend established by the days before it in the same week? Compared for Friday vs. pooled other days.

## Results — primary (Friday vs. pooled Monday-Thursday)

| Timeframe | Friday efficiency (mean/median) | Mon-Thu efficiency | p | Friday vol (mean/median) | Mon-Thu vol | p |
|---|---|---|---|---|---|---|
| M15 | 0.210 / 0.170 | 0.194 / 0.162 | 0.204 | 19.04 / 16.78 | 19.25 / 17.57 | 0.282 |
| H1 | 0.497 / 0.444 | 0.445 / 0.389 | 0.131 | 4.38 / 3.86 | 4.34 / 3.93 | 0.777 |

**No significant difference on either metric, on either timeframe.** V0's primary claim is not
supported at face value.

## Falsification — placebo/permutation control

Random ~1/5-of-days ("pseudo-Friday," seed=42) vs. the rest, identical test:

| Timeframe | p (efficiency) | p (volatility) |
|---|---|---|
| M15 | 0.200 | 0.679 |
| H1 | 0.787 | 0.131 |

Friday's own p-value (0.204 M15 efficiency) is statistically indistinguishable from what a **random,
meaningless subset of days** produces by chance (0.200) at this sample size — Friday shows no more of
a "difference from the rest" than an arbitrary 1-in-5 grouping would.

## Reversal-of-week's-trend test

| Timeframe | Friday opposition rate | Other-days rate | p |
|---|---|---|---|
| M15 | 51.0% (n=145) | 49.1% (n=446) | 0.758 |
| H1 | 52.1% (n=142) | 48.7% (n=435) | 0.547 |

Both rates sit at essentially a coin flip (~50%), with no significant Friday-specific tendency to
reverse the week's prevailing trend — the specific "profit-taking reversal" mechanism V0 implies is
not supported either.

## Day-of-week ladder — the real, replicated finding (not what V0 predicted)

| Day | M15 p (vol vs. rest) | H1 p (vol vs. rest) | Mean vol (M15 / H1) |
|---|---|---|---|
| **Monday** | **0.00031** | **1.55e-5** | 16.86 / 3.63 (**lowest**) |
| Tuesday | 0.459 | 0.987 | 19.35 / 4.24 |
| **Wednesday** | **2.05e-5** | **5.37e-7** | 21.42 / 5.28 (**highest**) |
| Thursday | 0.742 | 0.687 | 19.36 / 4.22 |
| Friday | 0.282 | 0.777 | 19.04 / 4.38 |

A real, robust, replicated (both M15 and H1) day-of-week volatility pattern exists — Monday afternoon
is consistently the quietest, Wednesday afternoon consistently the most volatile — but Friday sits in
the unremarkable middle of the pack on both timeframes, indistinguishable from Tuesday/Thursday. This
pattern is unrelated to V0's own proposed mechanism (weekend position-closing) and does not involve
Friday at all.

## Headline result — V0 NOT SUPPORTED

Friday afternoon shows no significant difference from the rest of the week in directional persistence
or volatility, on either tested timeframe, and this null is corroborated by a placebo control showing
Friday's apparent difference is no larger than pure chance. The reversal-of-week's-trend test (the most
direct test of the stated "profit-taking" mechanism) is likewise null. **No V1 is proposed for E008.**

**Note on the Monday/Wednesday finding**: a real, replicated day-of-week volatility pattern was found,
but it does not involve Friday and is unrelated to E008's own proposed mechanism — proposing it as an
"E008 V1" would misattribute an unrelated pattern to this edge's own hypothesis space. Consistent with
the CEC-001 precedent (`CROSS_EDGE_RESEARCH_CANDIDATES.md`), this is noted here as a disclosed,
out-of-scope observation only. It is **not** studied further, not promoted into a new edge or
mechanism, and awaits separate CEO authorization if further investigation is ever wanted.

## Answers to the 9 mandatory Discovery questions

1. **Does the edge exist at all (signal distinguishable from noise)?** No — Friday afternoon shows no
   signal distinguishable from a random day grouping, on either directional persistence or volatility,
   on either timeframe.
2. **Frequency?** 145 Friday afternoon events (M15) / 143 (H1) over ~2.85 years (~1/week, as expected).
3/4. **Days it works/fails?** The real day-of-week volatility pattern found (Monday lowest, Wednesday
   highest) does not implicate Friday at all.
5. **Sessions?** Time-of-day-within-Friday (ny vs. late sub-session) was recorded (bar counts only,
   e.g. M15: ~32 ny bars / ~4 late bars per Friday) but not further profiled given the primary test was
   already null.
6. **Volatility regimes?** Not a driver of any Friday-specific effect — no Friday-specific effect was
   found to condition on.
7. **Filters that improve it?** Not searched — would be exactly the "optimize until profitable"
   behavior the protocol forbids, and there is no positive base result to refine in the first place.
8. **Conditions that invalidate it?** The core mechanism (weekend position-closing driving distinct
   Friday-afternoon behavior) is invalidated by both the primary test and the placebo control.
9. **Out-of-sample?** Not tested via an explicit time-split in this pass, consistent with several
   earlier edges.

## Current status

**Discovery stage complete. V0 NOT SUPPORTED. No V1 proposed.** An unrelated, real, replicated
day-of-week volatility pattern (Monday quiet / Wednesday volatile) was found and disclosed as an
out-of-scope observation, not pursued further under this edge. This is a **structural-behavior
Discovery** result only (Protocol v2 §9's own labeling requirement) — no scalping validation
performed, no claim about tradability.

## Scope clarification (`EDGE_RESEARCH_PROTOCOL.md` §9)

This Discovery pass answers §§1-8 only. No Immediate Scalping Response (§9) check was performed —
per the CEO's explicit priority-shift instruction, §9 work is deferred project-wide, not attempted here.
