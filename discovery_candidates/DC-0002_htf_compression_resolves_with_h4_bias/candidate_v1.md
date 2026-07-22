# Discovery Candidate DC-0002: Higher-Timeframe Compression Resolves Into Expansion In The Direction Of The Prevailing H4 Bias

## Metadata

- **candidate_id**: DC-0002
- **title**: Higher-Timeframe Compression Resolves Into Expansion In The Direction Of The Prevailing H4 Bias
- **origin_mode**: discretionary-observation, TradingView Replay (manual + traverse), Alpha autonomous sprint
- **date_first_observed**: 2026-07-22 (replay windows Sep 2023 – Mar 2024)
- **date_frozen**: 2026-07-22
- **version**: v1
- **instrument**: XAUUSD (OANDA)
- **timeframes_examined**: H4 (regime/bias), H1 (structure), M15 (execution of the resolution)
- **data_split_id**: pre_holdout_2025-10-23T09-15-00Z_v1
- **holdout_cutoff**: 2025-10-23T09:15:00+00:00
- **source_artifacts**: replay windows 2023-09-01→10-10; 2024-01-01→02; 2024-02→03; 2024-03-12→03-27. Screenshots `fj_run1_a/b/c`, `p1_h4_2024-03-19`, `p1_h1_2024-03-19`, `sprint_h4_bias_0320`. Field journal #003, #010, #013, #014. Ledger `research_log/LINE-A_COMPRESSION_CASES.md`.
- **related_ids**: LINE-A; K03 (trend-efficiency gating); K05 (long-beta confound); DC-0003 (scale inversion)
- **content_hash**: sha256:8dcf79e3f4b77e7f78d934b9c8d51b4a3bc960052b34466f19c25147f3afcdad
- **content_hash_method**: sha256 over this file's UTF-8 bytes, LF line endings, single trailing newline, with both `content_hash` occurrences replaced by the literal `PENDING`

## 1. Observation

On XAUUSD, when the H4 chart enters a **compression phase** — a multi-day consolidation following an
expansion leg, characterised visually by overlapping candles, contracting range, declining volume, and
"effort without result" (volume rising while range stays flat and price stays pinned) — the phase
terminates in a **directional expansion**, and in every observed instance the expansion travelled in
the **direction of the prevailing H4 bias** rather than in the direction suggested by the micro-structure
inside the compression.

Four observed instances:

| # | Date | H4 bias | Compression | Resolution |
|---|---|---|---|---|
| C1 | Jun–Oct 2023 | bearish | stair-stepped chop, dense alternating structure | DOWN, clean slide 1925→1829 |
| C2 | Jan–Feb 2024 | bullish | churn zone 2000–2060 | UP, +10% to 2195 |
| C3 | Feb–Mar 2024 | bullish | slow grind, small overlapping candles | UP, vertical 2040→2195 |
| C4 | Mar 12–20 2024 | bullish (corrective) | range 2145–2195, vol contracting, effort-without-result | UP, to 2222.9 (+67) |

C4 was **pre-registered**: the compression, the low efficiency and the explicit statement "direction
unknown" were written to the field journal *before* the resolution occurred.

## 2. Why It Attracted Attention

It recurred without being sought. C1 appeared during an unselected autoplay traverse; C2 emerged as a
*counterexample* while investigating a different question; C3 and C4 appeared during a chronological
forward sprint. The signature was recognisable each time by texture alone — the market visibly stops
"arguing with itself" and commits.

## 3. Why It May Repeat

Descriptively: a compression phase is a period in which neither side achieves displacement; positioning
accumulates on both sides while range contracts. When the balance breaks, the resulting move is
disproportionate to the preceding range. The higher timeframe appears to supply the direction, which is
consistent with the compression being a *timing/energy* condition rather than a directional one. No
causal claim is made.

## 4. Why It Deserves Further Investigation

It is concrete, visually identifiable in advance (demonstrated by the pre-registered C4), and it makes a
directional statement conditioned on an independently-observable variable (H4 bias). It also offers an
explanation for why prior break-geometry studies returned nulls: they conditioned on the break, not on
the compression that preceded it.

## 5. Confidence

**Low-to-medium in the shape; the directional component is materially confounded.**

Opposing evidence recorded deliberately:
- **K05 confound (serious):** 3 of 4 cases resolved UP inside the 2023–2025 gold bull trend. "Resolves
  with the H4 bias" is operationally "goes up" in this sample. C1 is the only non-long case.
- **K03 overlap:** this is adjacent to "trend continuation gated by high trend-efficiency", already
  tested lab-side and found weak (+.02R OOS, threshold-selected, explicitly not validated).
- Sample is n=4, single instrument, in-sample, selected by a human eye.
- "Compression" is not yet formally defined; trend efficiency is the proposed defensible operationalisation.

## Additional Notes (optional)

The falsification test that matters is a **direction/beta-matched null**, and bearish/lateral-H4 cases.
Lateral H4 makes no directional prediction under this candidate; if lateral compressions still resolve
upward systematically, that is long beta and this candidate should die.

## Handoff Statement

Submitted to Red Team as a descriptive observation only. This is **not** validated, **not** an edge,
**not** a strategy, and carries no profitability claim. Content hash: sha256:8dcf79e3f4b77e7f78d934b9c8d51b4a3bc960052b34466f19c25147f3afcdad.
