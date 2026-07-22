# Discovery Candidate DC-0006: Candles With Extreme Relative Volume Frequently Fail To Extend

## Metadata

- **candidate_id**: DC-0006
- **title**: Candles With Extreme Relative Volume Frequently Fail To Extend
- **origin_mode**: discretionary-observation, TradingView Replay manual candle-by-candle stepping
- **date_first_observed**: 2026-07-22 (replay 2024-03-20, 2024-03-27, 2024-07-16)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M15
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: field journal #013, #016, #017, #018; manual stepping logs 2024-03-20, 2024-03-27, 2024-07-16/17
- **related_ids**: DC-0003 (scale), DC-0005, OBS-0017
- **content_hash**: sha256:ef1e217fd3ff1aeb0fd8fa96f6e110f5cc4bcdbffb7a2c49474190f2af6585a4
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `PENDING`

## 1. Observation

Candles carrying the largest relative volume of their local sequence repeatedly turned out to be the
candles that did **not** continue, while moves that did continue arrived on ordinary volume.

Observed instances (all M15, all noted during forward stepping):
- **2024-03-20 ~05:00** — coil broke up on the *highest* volume of the sequence (813) → failed, −3.3.
- **2024-03-27 ~01:15** — coil broke up on rising volume (546) → failed, reverted.
- **2024-07-16 ~14:30** — displacement down, range 11.4 (≈4× normal) on volume 8448 (≈4× average) →
  fully rejected within 6 candles; volume then decayed 8448 → 6134 → 5678 → 4741.
- **2024-07-16, same day** — the sustained 6-candle advance that *did* hold came on ordinary volume
  (3600–6200), and the eventual break of the day's high came on volume **850**, the lowest of the block.

## 2. Why It Attracted Attention

The relation appeared four times inside a single session and contradicted the standard reading that
volume confirms a move. I had no prior interest in volume — it kept presenting itself.

## 3. Why It May Repeat

Descriptively: an extreme volume print marks the moment the largest number of participants act
simultaneously. If that population is being filled by the opposite side, the candle records
transfer rather than initiation. No causal claim is made.

## 4. Why It Deserves Further Investigation

It is trivially measurable (relative volume vs rolling average, forward extension), it appeared
repeatedly and unbidden, and it directly contradicts a widely-used heuristic — which makes it cheap
to falsify.

## 5. Confidence

**Very low.** A clear counterexample was found the very next replay day.

Opposing evidence recorded:
- **2024-07-17, London open:** the break that held came *with* volume 5251 (≈3×). The relation
  inverted within 24 hours of being noticed.
- n≈5 instances, one instrument, one observer, no counting of the (probably many) high-volume candles
  that did extend.
- Volume on this feed is tick/broker volume, not exchange volume.

## 6. Library Concept Scan

Concepts identifiable in this event, **listed not judged**.

| Library concept | How it appears |
|---|---|
| **OBS-0017** break geometry uninformative | Same family: a per-candle property proposed as informative about continuation. |
| **DC-0003** scale inversion | Three of the instances are micro-scale coils, where DC-0003 already predicts failure — volume may be redundant with scale here. |
| **Volatility primitive — clustering** | Extreme-volume candles are also extreme-range candles; range clustering is already established. |
| **Volatility hour-of-day profile** (4.3×, NY peak) | The 8448 print sits in the NY window; session timing is entangled with "extreme" volume. |
| **K02** breakout/expansion-chasing generally negative | Entering on the extreme-volume expansion candle is exactly the chasing K02 found negative. |
| **absorption** (census event class) | The definition used in the census — high volume, small range — is the sibling of this observation. |
| **DC-0005** | The 2180 third-test displacement was also the highest-volume candle of its sequence. |

## Handoff Statement

Submitted to Red Team as a descriptive observation only. Not validated, not an edge, not a strategy,
no profitability claim. Content hash: sha256:ef1e217fd3ff1aeb0fd8fa96f6e110f5cc4bcdbffb7a2c49474190f2af6585a4.
