# Discovery Candidate DC-0003: Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways

## Metadata

- **candidate_id**: DC-0003
- **title**: Scale Inversion — Micro-Scale Coils And Higher-Timeframe Compressions Resolve In Opposite Ways
- **origin_mode**: discretionary-observation, TradingView Replay (manual candle-by-candle), Alpha autonomous sprint
- **date_first_observed**: 2026-07-22 (replay 2024-03-20, 2024-03-27)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: M5, M15 (micro-scale), H1, H4 (higher-timeframe scale)
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: manual M15 stepping 2024-03-20 02:15–07:30 UTC and 2024-03-26 23:00–2024-03-27 03:00 UTC; field journal #013, #014; ledger `research_log/LINE-A_COMPRESSION_CASES.md`; OBS-0017 statistical null.
- **related_ids**: DC-0002; OBS-0017; OBS-0004; field journal #005/#006 (sub-H1 structure is noise-scale)
- **content_hash**: sha256:e56076c5c4fce6a296f77e996fe050f03ae6b27fc3b929819e8824033195ac7d
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `sha256:e56076c5c4fce6a296f77e996fe050f03ae6b27fc3b929819e8824033195ac7d`

## 1. Observation

Compression does not mean the same thing at every scale. Two classes were observed to behave in
**opposite** ways:

- **HTF-C** (H4 / multi-day consolidation after an expansion leg): resolves into a **genuine directional
  expansion** — observed 4/4 (see DC-0002).
- **micro-C** (M15 coil of ~5–10 candles inside a range, typically thin Asian tape): produces a
  **marginal break beyond the coil boundary that immediately fails and reverses** — observed 2/2.

micro-C instances, both stepped manually and both noted before resolution:
| # | Date/time (UTC) | Coil evidence | Resolution |
|---|---|---|---|
| m1 | 2024-03-20 ~05:00 | ranges 1.51→0.62, volume 656→343, price pinned in 1.3 pt | broke UP to 2160.295 on the *highest* volume of the sequence (813) → failed, −3.3 |
| m2 | 2024-03-27 ~01:15 | ranges 1.55→0.62, volume ~210 flat, price pinned in 1.5 pt | broke UP to 2180.25 on rising volume (546) → failed, back to 2177.4 |

## 2. Why It Attracted Attention

The two classes had been unconsciously pooled under one label. When m2 failed in exactly the manner m1
had failed — while the H4-scale compression a week earlier had produced a +67 point expansion — the
distinction became visible. In both micro cases the break came on *expanding* volume and still failed,
which contradicts the common reading that volume confirms a break.

## 3. Why It May Repeat

Descriptively: at the micro scale in thin liquidity, the coil boundary sits within ordinary noise
amplitude, so exceeding it carries no information about commitment. At the higher-timeframe scale the
boundary is far outside noise amplitude, so exceeding it requires genuine displacement. The same word
("breakout") therefore describes two different events depending on whether the boundary is inside or
outside the prevailing noise scale.

## 4. Why It Deserves Further Investigation

It offers a concrete, testable explanation for an existing null result: **OBS-0017** examined 384
swing-high exceedances and found break geometry uninformative — but it pooled all scales, where the two
classes would cancel. If the scale distinction is real, re-testing with scale separation should recover
structure that the pooled test destroyed. That is an unusually specific, falsifiable prediction about a
prior negative result.

## 5. Confidence

**Low.** micro-C n=2, HTF-C n=4, single instrument, in-sample, human-selected.

Opposing evidence recorded deliberately:
- Both micro-C cases occurred in thin Asian tape; the class may be a *liquidity* effect rather than a
  *scale* effect, and the two are not separated here.
- Field journal #005/#006 independently observed that sub-H1 structure labels contradict the prevailing
  drift in thin tape — consistent with micro-C being noise rather than a mechanism.
- "Marginal break fails" is exactly the intuition OBS-0017 refuted at pooled scale; this candidate
  claims the refutation was an artifact of pooling, but that claim is itself untested.

## Additional Notes (optional)

The operational question for whoever tests this is where the boundary between the two classes lies —
plausibly where the coil range crosses some multiple of prevailing ATR, rather than at a fixed timeframe.

## 6. Library Concept Scan

Concepts from the Living Knowledge Library identifiable in this event. **Listed, not judged.**

| Library concept | How it appears in this event |
|---|---|
| **OBS-0017** break geometry uninformative (n=384, CI spans 0) | Directly implicated: this candidate proposes that null arose from pooling the two scale classes. |
| **OBS-0004** sweep depth uninformative | Same family — a geometric property of the break carrying no information at pooled scale. |
| **K01** raw sweeps without confirmation are non-positive | micro-C marginal breaks are functionally unconfirmed sweeps; their failure is consistent with K01. |
| **K02** breakout / expansion-chasing generally negative | micro-C is breakout-chasing at the smallest scale. |
| **Volatility primitive — hour-of-day profile** (4.3× peak/trough) | Both micro-C cases sit in the *trough* of that profile (thin Asian tape) — so scale and liquidity are entangled here. |
| **Volatility primitive — clustering** | The "noise amplitude" the coil boundary sits inside is the local volatility state. |
| **Field journal #005/#006** — sub-H1 structure labels contradict the prevailing drift in thin tape | Independent prior observation that micro-scale structure is noise-scale. |
| **DC-0002** | The HTF-C half of this candidate is DC-0002's subject; the two are complementary halves of one scale question. |
| **E-program theme** — ~52% reversal rates on both M15 and H1 | Prior pooled-scale tests returning coin-flip outcomes. |

## Handoff Statement

Submitted to Red Team as a descriptive observation only. **Not** validated, **not** an edge, **not** a
strategy, no profitability claim. Content hash: sha256:e56076c5c4fce6a296f77e996fe050f03ae6b27fc3b929819e8824033195ac7d.
