# Discovery Candidate DC-0020: An 18:00 UTC Low Sweep Followed By a Failed Fresh-High Reclaim Sets a New All-Time Volume Record and Extends Into a Multi-Leg, Bidirectional Decline

## Metadata

- **candidate_id**: DC-0020
- **title**: An 18:00 UTC Low Sweep Followed By a Failed Fresh-High Reclaim Sets a New All-Time Volume Record and Extends Into a Multi-Leg, Bidirectional Decline
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-24
- **date_frozen**: 2026-07-24
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2025-10-29 17:45-20:30 UTC, OANDA:XAUUSD M15/M5/M1 replay window
- **related_ids**: DC-0018 (prior all-time single-candle volume record, 36,798 — now exceeded), DC-0006 (extreme-volume candles frequently fail to extend — contrast: here the failure triggered a large extended episode, not a stabilization), DC-0011 (single-minute sweep reclaimed and extends to new highs — contrast: here the reclaim attempt failed and reversed), DC-0013 (sustained multi-candle decline family, here inverted-order and far higher volume), `DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md` (same clock hour flagged elsewhere as a possible artifact on a different day — this instance is high-magnitude and high-volume throughout, contrasting with that concern)
- **content_hash**: sha256:211c6dad5b369dd4377055adc1971b657f2cb5dce0e0587150e9956c18537ec0

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2025-10-29, after a quiet baseline (~3994-3995, volume under 2,000/M5), the 18:00-18:15 UTC M15
candle (O3994.9, H4007.875, L3978.655, C3983.285, vol 28,523) swept down to a fresh low
(3978.655), then spiked up to a fresh high (4007.875, above the pre-move level) within the same
candle, before reversing and closing near the low. Volume was distributed across all 15 one-minute
sub-candles (1053-3223, no single minute exceeding ~11.3% of the total) — a genuine sustained,
non-concentrated construction, not a thin-liquidity artifact.

The failed reclaim extended into a large, multi-leg episode over the following ~2h15m (10 M15
candles total, 18:00-20:30 UTC):

| Candle (UTC) | O-H-L-C | Volume |
|---|---|---|
| 18:00-18:15 | 3994.9 / 4007.875 / 3978.655 / 3983.285 | 28,523 |
| 18:15-18:30 | 3983.32 / 3989.595 / 3976.79 / 3981.14 | 15,053 |
| 18:30-18:45 | 3981.385 / 3989.83 / **3942.71** / 3954.245 | **37,204** |
| 18:45-19:00 | 3954.335 / 3972.755 / 3947.85 / 3969.4 | 30,717 |
| 19:00-19:15 | 3969.315 / 3979.9 / 3953.54 / 3970.62 | 24,524 |
| 19:15-19:30 | 3970.68 / 3974.755 / 3951.4 / 3953.39 | 19,026 |
| 19:30-19:45 | 3953.515 / 3954.82 / **3927.86** / 3929.19 | 21,828 |
| 19:45-20:00 | 3929.18 / 3949.74 / 3929.135 / 3945.825 | 22,040 |
| 20:00-20:15 | 3945.845 / 3949.7 / 3932.68 / 3941.25 | 9,034 |
| 20:15-20:30 | 3941.285 / 3954.375 / 3937.245 / 3948.915 | 6,857 |

The 18:30-18:45 candle's volume (**37,204**) is the **new largest single-candle volume observed
anywhere in this replay**, exceeding DC-0018's previous record (36,798). Dropping to M5, this
candle's volume splits 6,948/15,895/14,361 across its three sub-candles — the largest single M5
component is 42.7% of the total, matching (not exceeding) the concentration ratio DC-0018 itself
accepted as organic (7,964/18,652 = 42.7%), confirming this is a genuine sustained/distributed
construction rather than a single-minute concentrated spike or thin-liquidity artifact.

The episode does not resolve as a single directional move: after the extreme-volume candle, price
bounced (3954.245 -> 3970.62 over two candles), reversed back down to a **new, lower low**
(3927.86 — below the extreme-volume candle's own low), bounced again, and only then did volume
normalize (9,034, then 6,857) with price stabilizing around 3937-3954. Total range across the full
episode: 4007.875 (high) to 3927.86 (low) = **80.0 points**; from the pre-move level (~3994.9) to
the ultimate low, **~67.0 points**.

## 2. Why It Attracted Attention

This episode combines several elements none of which alone would clear the v2 filter, but which
together represent a genuinely new combination: (a) a **new all-time single-candle volume record**
for this replay (37,204, exceeding DC-0018's 36,798), (b) a **low sweep followed by a failed
fresh-high reclaim** within the same candle — the mirror image of DC-0018's high-spike-then-fail,
and the opposite outcome of DC-0011's sweep-then-successful-reclaim, (c) a **multi-leg, bidirectional**
resolution (bounce, new lower low, bounce again) rather than either a clean single-direction decline
(DC-0013 family) or a fail-then-stabilize pattern (DC-0006/DC-0017), and (d) occurring at the 18:00
UTC clock hour, which has a documented data-quality concern on a different date
(`DATA_QUALITY_OPEN_ITEM_2025-09-17_1800UTC.md`) — this instance's substantial, well-distributed
volume throughout distinguishes it clearly from that concern rather than repeating it.

## 3. Why It May Repeat

The underlying sustained multi-minute volume construction is the same mechanism documented since
DC-0008. What is new is the specific sequence — sweep low, spike to a fresh high, fail, and extend
into an extreme-volume multi-leg decline rather than either stabilizing or continuing cleanly in one
direction. Whether "failed reclaim on record volume" reliably precedes multi-leg (rather than clean)
declines cannot be established from a single instance; DC-0018's single instance of a comparable
extreme-volume failure resolved into a cleaner, single-direction decline, so this instance's
multi-leg/bidirectional character is itself a further point of variation, not a confirmation of a
single "extreme-volume-failure" resolution style.

## 4. Why It Deserves Further Investigation

This candidate sits at the intersection of three previously separate observations: extreme-volume
single-candle failures (DC-0006/DC-0018), sweep-and-reclaim dynamics (DC-0011, where the reclaim
succeeded and extended — the opposite outcome), and multi-candle sustained directional moves
(DC-0013 family). Whether the direction of the initial failed reclaim (sweep-low-then-failed-high
vs. DC-0018's spike-high-then-failed) predicts the resolution style (multi-leg/bidirectional here
vs. DC-0018's cleaner single-direction decline) is a natural comparison point for future instances.
The new volume record itself (37,204) also resets the reference point for "extreme" in this replay,
superseding DC-0018's 36,798.

## 5. Confidence

**Low.** A single instance. The multi-minute sustained-volume construction and the general
"failed extreme-volume move precedes further movement" pattern both have precedent (DC-0006/
DC-0018), but the specific sequence (low sweep, failed high reclaim, new volume record, multi-leg
bidirectional resolution) rests on n=1 and should not be treated as a repeatable signature.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. This candidate makes no
claim about cause, and in particular makes no claim that 18:00 UTC is itself a mechanism — the only
other flagged instance at this clock hour (2025-09-17, a different day) was logged as a data-quality
concern rather than a genuine event, and this instance's well-distributed, substantial volume
throughout distinguishes it clearly from that concern. Whether 18:00 UTC has any general tendency
beyond coincidence cannot be assessed from two instances with opposite characterizations (one
flagged as possible artifact, one confirmed organic and extreme).

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-24**. Content hash: **sha256:211c6dad5b369dd4377055adc1971b657f2cb5dce0e0587150e9956c18537ec0**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
