# Discovery Candidate DC-0016: A Sustained Early-Asia/Pre-London Directional Expansion Reaches the Largest Point Move of This Family, Then Reverses at a Marginal New High

## Metadata

- **candidate_id**: DC-0016
- **title**: A Sustained Early-Asia/Pre-London Directional Expansion Reaches the Largest Point Move of This Family, Then Reverses at a Marginal New High
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-23
- **date_frozen**: 2026-07-23
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: 2025-09-01 01:00-03:00 UTC, OANDA:XAUUSD M15/M5 replay window
- **related_ids**: DC-0013 (NY-session sustained expansion, 4 candles, ~43pt, ended in consolidation), DC-0014 (V-reversal + sustained expansion at 00:00-01:00 UTC, 4-5 candles, ~35pt, ended in reversal), DC-0015 (NY-afternoon sustained expansion, 11 candles/~2h45m, ~31pt, ended in modest pullback), DC-0008 (sustained multi-minute construction, the underlying mechanism family)
- **content_hash**: sha256:e1c1c4dce4455e9046e786358546bac2359b50b8217bc364357faad8e9660ff2

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-09-01 (Monday), starting at the 01:00-01:15 UTC M15 candle (O3439.025), price advanced in
a broadly sustained direction across roughly six to seven consecutive M15 candles, reaching an
absolute peak of 3486.262 at approximately 02:30-02:45 UTC, before a sharp single-candle reversal
gave back most of the final leg (that candle: O3483.49, H3486.262, L3469.59, C3473.52 -- a ~16.7pt
range closing near the low). The candle immediately following confined itself to a narrower range
(3469.625-3476.48) on declining volume (7766), consistent with the expansion phase having ended.

The point move across the full run (3439.025 -> 3486.262, roughly 1h30m-1h45m) was approximately
47.2 points -- the largest single-direction point move observed among this family of candidates so
far (DC-0013: ~43pt, DC-0014: ~35pt, DC-0015: ~31pt).

Volume across the run: 5795, 9477, 15884, 12957, 15153, 11770, then 13863 on the reversal candle
itself. Dropping to M5 on the two highest-volume M15 candles (15884 and 15153 vol) showed volume
distributed across the three M5 sub-candles each time (e.g. 3968/6579/5337 for the first), with no
single M5 candle exceeding roughly 40% of the M15 total -- matching the "sustained, distributed"
construction already catalogued in DC-0008/DC-0013/DC-0014/DC-0015, rather than a single-minute
concentrated sweep.

## 2. Why It Attracted Attention

The v2 pre-investigation filter would ordinarily screen out isolated high-volume candles as
already-documented. What passed the filter here was the combination of (a) a new clock-time window
for this construction -- roughly 01:00-02:45 UTC, distinct from NY midday (DC-0013), the 00:00-01:00
UTC transition (DC-0014), and NY afternoon (DC-0015) -- and (b) the largest point move of the family
observed to date, achieved over a duration (6-7 candles, ~1h45m) that sits between DC-0013/DC-0014's
4-5 candles and DC-0015's eleven.

## 3. Why It May Repeat

The underlying construction (sustained, distributed multi-minute volume, no single-candle
concentration) is the same mechanism already catalogued across DC-0008/DC-0013/DC-0014/DC-0015.
What is new here is a fourth distinct clock-time instance, which -- taken together with the other
three -- weakly suggests the construction is not restricted to a single session or hour, though a
single instance at this specific hour cannot establish that on its own. The ending shape (a marginal
new high immediately followed by a sharp single-candle giveback) also resembles DC-0014's reversal
ending more than DC-0013's consolidation or DC-0015's modest pullback, which may be worth comparing
across a larger sample.

## 4. Why It Deserves Further Investigation

Alpha now has four documented instances of "large sustained multi-candle expansion" (DC-0013,
DC-0014, DC-0015, DC-0016) at four different clock times/sessions, with four different point-move
magnitudes (~43, ~35, ~31, ~47pt), four different durations (4, ~5, 11, ~6-7 candles), and three
distinct resolution shapes (consolidation, sharp reversal, modest pullback, sharp reversal again).
Comparing magnitude, duration, and resolution shape across these four instances -- and any future
ones -- remains a natural next step for understanding whether this construction family has any
time-of-day-dependent or duration-dependent behavior. Whether the largest-magnitude instance
observed so far coinciding with a reversal-type ending (rather than consolidation) is meaningful or
coincidental cannot be assessed from n=1 additional instance.

## 5. Confidence

**Low.** One instance at this specific clock-time window. The construction mechanism itself
(sustained, distributed volume) has multiple precedents, but the magnitude, duration, and ending
shape observed here rest on n=1 for this hour and should not be treated as a repeatable signature.

## Additional Notes (optional)

This instance immediately followed a weekend gap (Friday 2025-08-29 21:00 UTC -> Sunday 2025-08-31
22:15 UTC, small gap, quickly retraced, already a documented pattern) and roughly two hours of
ordinary thin Sunday-evening/early-Asia trading (volumes ~650-6300, no notable ranges). No external
calendar catalyst is visible from price/volume data alone; this candidate makes no claim about
cause, and in particular makes no claim that "start of week" or "Monday Asia open" is itself a
mechanism -- that would require comparing against other week-opens, which has not been done.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-23**. Content hash: **sha256:e1c1c4dce4455e9046e786358546bac2359b50b8217bc364357faad8e9660ff2**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file -- never as an edit to this
file.
