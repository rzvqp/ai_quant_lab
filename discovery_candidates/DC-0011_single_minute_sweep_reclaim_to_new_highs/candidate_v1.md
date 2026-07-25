# Discovery Candidate DC-0011: A Single-Minute Sweep Is Reclaimed And The Move Extends To New Highs, Not Just Back To Pre-Sweep Levels

## Metadata

- **candidate_id**: DC-0011
- **title**: A Single-Minute Sweep Is Reclaimed And The Move Extends To New Highs, Not Just Back To Pre-Sweep Levels
- **origin_mode**: discretionary-observation, Alpha autonomous replay sprint
- **date_first_observed**: 2026-07-22 (replay 2025-08-07)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15, M5, M1
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual stepping log 2025-08-07 13:45-14:15 UTC
- **related_ids**: DC-0007, DC-0008
- **content_hash**: sha256:dc0607e02329bfa6818e5f91a049949199a8c32420b13572bfdba0a29207ea33
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:dc0607e02329bfa6818e5f91a049949199a8c32420b13572bfdba0a29207ea33`

## 1. Observation

At 2025-08-07, the M15 candle 14:00-14:15 UTC (NY session) showed O3385.015 H3390.31 L3374.77
C3390.285 — a 15.5-point range, wick deep into the low, close at the high, volume 23,286 (the
highest of the day). Dropping to M1: at 14:08 UTC, a single one-minute candle ran O3384.805
H3385.09 **L3374.77** C3376.125 — a 10-point plunge inside 60 seconds, volume 2,416 (roughly
1.5-3x the surrounding minutes' 700-1,700). The very next minute (14:09) reversed hard, high
3383.63, close 3380.8, and the move continued climbing for the following six minutes to a new
session high (3390.31) by 14:14 — not merely back to the pre-sweep level (~3384-3385) but well
beyond it.

## 2. Why It Attracted Attention

The sweep itself matches an already-seen shape (single-candle liquidity grab, cf. DC-0007), but
here the aftermath went further: price didn't just reclaim the swept level and stabilize, it broke
to fresh highs within the same 15-minute window. The sweep looked less like noise and more like a
stop-run that cleared out resistance to the subsequent move — the low was taken, and the rally that
followed outran the level the sweep had violated.

## 3. Why It May Repeat

Descriptively: a single-minute spike through a recent level, followed immediately by reclaim and
continuation past the pre-sweep range, is a distinct and countable shape from a sweep that merely
reclaims and goes sideways. Whether "sweep + continuation-past-pre-sweep-highs" recurs, versus
"sweep + reclaim-and-stall," is directly comparable across future instances.

## 4. Why It Deserves Further Investigation

Both the sweep (single-minute low, volume multiple vs. neighbors) and the outcome (does price
merely reclaim, or does it exceed the pre-sweep range within N minutes) are fully countable from
bar data. This gives a concrete way to distinguish sweeps that were exhaustion from sweeps that
preceded genuine continuation.

## 5. Confidence

**Low.** One instance, one instrument, one timeframe cluster.

## Additional Notes

Occurred during the NY session on a day (2025-08-07) already flagged for unusually elevated volume
across multiple hours (see DC-0010 and its addendum) — this instance's high volume may be partly a
function of the day's overall elevated activity rather than something specific to the sweep
mechanism itself; that confound is not resolved here.

## Handoff Statement

Frozen as of version **v1**, dated **2026-07-22**. Content hash: **sha256:dc0607e02329bfa6818e5f91a049949199a8c32420b13572bfdba0a29207ea33**. This document is
immutable from this point forward. Any correction or new evidence must be filed as a separate,
dated addendum in this candidate's folder, or as a new version file — never as an edit to this
file.
