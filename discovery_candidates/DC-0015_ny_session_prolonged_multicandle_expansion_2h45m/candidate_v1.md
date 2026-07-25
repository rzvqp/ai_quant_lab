# Discovery Candidate DC-0015: A Sustained NY-Session Directional Expansion Persists Across Eleven Consecutive M15 Candles (~2h45m), the Longest Single-Direction Run Observed in This Replay

## Metadata

- **candidate_id**: DC-0015
- **title**: A Sustained NY-Session Directional Expansion Persists Across Eleven Consecutive M15 Candles (~2h45m), the Longest Single-Direction Run Observed in This Replay
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-08-29 13:00-16:00 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0013 (large sustained NY-session expansion, 4 candles, ~43pt, ended in consolidation), DC-0014 (V-reversal + sustained expansion at 00:00-01:00 UTC, 4-5 candles, ~35pt, ended in reversal), DC-0008 (sustained multi-minute construction, the underlying mechanism family)
- **content_hash**: sha256:f6526ab36f30391622309f27519583a735abd9f60589e52362e3d6797af15d8e

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-08-29, starting at the 13:00-13:15 UTC M15 candle (O3416.51), price advanced in a broadly
sustained direction across eleven consecutive M15 candles, reaching a peak of 3447.79 at
approximately 15:45 UTC before a small pullback appeared in the 15:45-16:00 candle (high 3447.735,
low 3445.015). Across the full run (13:00-15:45 UTC, roughly 2 hours 45 minutes), price moved
approximately 31.3 points (3416.51 -> 3447.79) without a candle that gave back more than a small
fraction of the preceding advance.

Volume throughout the eleven candles stayed elevated and did not show the sharp single-candle
spikes characteristic of DC-0008/DC-0011's single-minute-concentration family: 11305, 9495, 9989,
10370, 16948, 19061, 16295, 13021, 10799, 12729, 6626, 11242. Dropping to M5 on the two
highest-volume candles (16948 and 19061 vol) showed volume distributed fairly evenly across the
three M5 sub-candles each time (e.g. 6823/6057/6181 for one), with no single dominant M5 candle —
matching the "sustained, distributed" construction already documented in DC-0008/DC-0013/DC-0014
rather than a concentrated sweep.

## 2. Why It Attracted Attention

The v2 pre-investigation filter would ordinarily screen out NY-session volume in the 5,000-20,000
range as already-documented (multiple prior NY sessions have shown comparable per-candle volume).
What passed the filter here was not any single candle's magnitude, but the persistence: eleven
consecutive M15 candles advancing in the same direction with no meaningful pullback is longer than
any other sustained-expansion instance observed in this replay, including DC-0013 (four candles)
and DC-0014 (four to five candles before reversing). The total point move (~31pt) sits between
DC-0013's (~43pt) and DC-0014's (~35pt), but achieved over roughly three times the duration.

## 3. Why It May Repeat

The underlying construction (sustained, distributed multi-minute volume, no single-candle
concentration) is the same mechanism already catalogued in DC-0008/DC-0013/DC-0014. What is
new here is specifically the duration dimension: whether NY-session sustained expansions can
persist this long, and whether the volume-declining-then-small-pullback pattern seen at the end
(19061 -> 13021 -> 10799 -> 12729 -> 6626 -> 11242, ending in a modest pullback) is a recognizable
"exhaustion" signature worth comparing against future instances. A single instance cannot establish
whether 2h45m is an unusual outlier duration or a plausible upper bound for this construction type.

## 4. Why It Deserves Further Investigation

Alpha now has three documented instances of "large sustained multi-candle expansion" (DC-0013,
DC-0014, DC-0015) at three different clock times/sessions (NY midday, the 00:00-01:00 UTC
transition, and this prolonged NY-afternoon run), with three different durations (4, ~5, and 11
candles) and three different resolutions (consolidation, reversal, modest pullback). Comparing
duration against eventual resolution across these three instances -- and against any future
instances -- is a natural next step for understanding whether this construction family has any
duration-dependent behavior.

## 5. Confidence

**Low.** One instance of this specific duration. The construction mechanism itself (sustained,
distributed volume) has multiple precedents, but the ~2h45m persistence and the specific
volume-decline-then-pullback ending pattern rest on n=1 and should not be treated as a repeatable
signature.

## Additional Notes (optional)

No external calendar catalyst is visible from price/volume data alone; this candidate makes no
claim about cause. The 12:30 UTC window (18th instance in this replay, occurring shortly before
this expansion began) ran ordinary (volume ~6,211, roughly 1x the immediately preceding bars) and
is not treated as related to this expansion's onset.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:f6526ab36f30391622309f27519583a735abd9f60589e52362e3d6797af15d8e**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
