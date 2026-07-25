# Discovery Candidate DC-0026: A Thin-Liquidity Daily-Rollover Reopen Produces a ~100-Point Parabolic Spike That Fully Reverses Within Minutes

## Metadata

- **candidate_id**: DC-0026
- **title**: A Thin-Liquidity Daily-Rollover Reopen Produces a ~100-Point Parabolic Spike That Fully Reverses Within Minutes
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint (v2 pre-investigation filter applied)
- **date_first_observed**: 2026-07-25
- **date_frozen**: 2026-07-25
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: post_holdout_reopened_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00 (original cutoff; this candidate's data postdates it under the CEO's explicit window-reopening authorization)
- **source_artifacts**: 2026-01-28 23:00-23:50 UTC, OANDA:XAUUSD M15/M5/M1 replay window
- **related_ids**: DC-0001 (isolated single-bar velocity outlier followed by gradual continuation — this instance is a multi-minute sustained spike followed by a full reversal, not a single bar or a continuation), DC-0010 (quiet-hour volume expansion — broader category, does not capture this specific spike-then-reversal round-trip shape), DC-0025/Addendum B (fastest prior point-velocity documented, ~58pt/5min — this instance is roughly twice as fast, ~100pt/6min), DC-0024/Addendum A (largest magnitude record, 154.665pt over ~8h — this instance is a small fraction of that magnitude but at an order-of-magnitude-faster velocity), none of which cover the specific "thin daily-rollover reopen, fast round-trip spike" mechanism
- **content_hash**: sha256:c4155ef5caf0a154543e77cd0929fca90a3db64d6170caccaf7dacae84fa97e6

> Lifecycle status is NOT recorded here. This document is a frozen historical snapshot; only its
> `date_frozen` and `version` belong to it. The current lifecycle status of this candidate is
> tracked exclusively in `DISCOVERY_CANDIDATE_INDEX.md`.

## 1. Observation

On 2026-01-28, following the standard daily-rollover pause (~4500s, 21:37-23:00 UTC, already
documented as non-anomalous), price reopened at 23:00 UTC and traded normally for roughly 34
minutes (23:00-23:34 UTC, M1 volume 750-2800/min, ordinary early-Asia activity) before an abrupt,
extremely fast parabolic spike:

| Time (UTC) | Price | Event |
|---|---|---|
| 23:34:00 | 5502.145 | Pre-spike level (last calm print) |
| 23:40:00-23:41:00 | **5602.225** (intrabar high) | Spike peak — **+100.08pt in ~6 minutes** |
| 23:44:00-23:45:00 | **5525.125** (intrabar low) | Reversal low — **-77.1pt in ~4-5 minutes** from the peak |

The full round trip (spike up, then reversal back down) completed within roughly 10-11 minutes.
This is the **fastest point-velocity documented anywhere in this replay** — roughly double the
previous fastest instance (DC-0025 Addendum B's ~58pt in 5 minutes).

Dropping to M1 to verify this is not a data artifact: every 1-minute candle through the spike and
reversal carries substantial, non-sparse volume (900-4,100/min, in several cases *higher* than the
immediately preceding calm minutes), and each candle's open matches the prior candle's close with no
gaps or teleporting. The M5 sub-candles containing the spike (14,058 and 14,432 volume) split their
volume across three 1-minute bars each with no single minute exceeding ~29% of its parent 5-minute
bar — a distributed, organic construction, clearly distinct from the sparse/gapped/single-digit-volume
signature of the Black Friday data-quality artifact previously documented in this replay
(Observation Registry entry 11). This is judged a genuine, if extreme, market event.

Notably, this spike did **not** set any volume record — the M5 sub-candles spanning the event
carried 6,262/14,058/14,432 volume, all far below this replay's all-time volume records (the
current record is 42,808, DC-0025 Addendum B). The novel axis here is **velocity**, not volume.

After the reversal low, price did not stabilize cleanly — it continued in elevated-volatility chop
(roughly 5444-5551 UTC over the following ~2h, M15 volume 14k-33k) rather than settling into a quiet
range, though it did not revisit the spike's extreme in either direction during the observed window.

## 2. Why It Attracted Attention

The ~100-point move in 6 minutes, immediately followed by a ~77-point reversal in the next 4-5
minutes, is the fastest point-velocity documented in this replay by a wide margin (roughly 2x the
previous record-holder), yet it occurs at a session boundary (the daily-rollover reopen) that has
been repeatedly observed as low-volume and non-anomalous in this replay up to this point. This
combination — a session context previously associated only with quiet, unremarkable reopens now
producing this replay's fastest price move — did not fit any existing candidate's mechanism.

## 3. Why It May Repeat

The daily-rollover reopen occurs nightly in this replay and has, in every other observed instance,
been quiet and unremarkable (a ~75-minute pause followed by ordinary low-volume trading). This is
the first instance in which that same thin-liquidity window produced a violent, fast round-trip
spike. Whether this reflects a rare, low-probability tail event that can occur in any thin-liquidity
reopen (daily, weekend, or holiday alike), or is specific to some unobserved condition on this
particular night, is not established by a single instance.

## 4. Why It Deserves Further Investigation

This candidate raises a question about whether this replay's thin-liquidity reopen windows
(nightly rollover, weekend gaps, holiday closures) share a common tail-risk profile for fast,
low-volume-driven price dislocations, distinct from the high-volume, high-conviction moves
documented in the DC-0013/DC-0025/DC-0024 families. A single instance cannot establish base rates;
future instances of unusually fast moves at any thin-liquidity reopen would be directly comparable
to this candidate.

## 5. Confidence

**Low.** A single instance (n=1). The specific ~100pt/6min velocity and the near-total reversal
within the following few minutes should not be treated as a repeatable pattern or as evidence this
particular session boundary carries elevated risk generally — this is one observed instance of an
otherwise-quiet recurring window.

## Additional Notes (optional)

No external calendar catalyst is confirmed from price/volume data alone. The organic-construction
verification here relied on M1 data (not just M5) given the extraordinary nature of the price
action — this is the first candidate in this replay verified at three timeframes (M15/M5/M1) rather
than two.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-25**. Content hash to be computed and recorded in
`HANDOFF_LOG.md` at handoff time. This document is immutable from this point forward. Any correction
or new evidence must be filed as a separate, dated addendum in this candidate's folder, or as a new
version file — never as an edit to this file.
