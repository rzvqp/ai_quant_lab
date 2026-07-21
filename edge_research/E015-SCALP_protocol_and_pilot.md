# E015-SCALP — Immediate Scalping Validation (Phase 0: Replay Feasibility Pilot)

**Program**: 40-Edge Alpha Discovery Program (Flow A). **Stage**: 2 (Immediate Scalping Validation),
per `EDGE_RESEARCH_PROTOCOL.md` §9 (Protocol v2). **Parent structural result**: E015 — Order Block
Re-Mitigation (`edge_research/E015_order_block_remitigation.md`), **unmodified, verdict/status
unchanged**. This is a separate, append-only study; it does not overwrite or reinterpret E015's own
structural-behavior result.

**Authorized scope of this document**: Phase 0 only — reconstruct the detector/event list, select a
pilot sample, freeze the trade rules, replay the pilot via TradingView, record outcomes, and issue a
**feasibility verdict**. No formal validation, no optimization, no AI Trader implementation, no
acceptance/rejection of E015-SCALP itself.

---

## Phase A — Definition (frozen BEFORE any TradingView interaction)

### Detector (unchanged, reused from E015's own structural definition)

Order block = a displacement bar on M15 (range > 1.5×ATR14(prior bar), directional body ≥50% of its
own range) whose originating opposite-colored bar (within the preceding 10 bars) is the OB zone
`[ob_low, ob_high]`. Identical, byte-for-byte reused construction from
`edge_research/e015_order_block_remitigation.py::detect_obs()` — not re-tuned for this study.

### Event definition tested here

**First mitigation only** ("visit-1"), per the CEO's own stated priority ("the existing structural
result identified first mitigation as the clearest current candidate"). Visit-1 = the first M15 bar,
after OB formation, whose range overlaps the OB zone.

### Confirmation rule

Confirmed at the first M1 candle, within the M15 visit-1 bar's own 15-minute window, whose range
overlaps `[ob_low, ob_high]`. (In the structural M15 study this was resolved at 15-minute granularity;
here it is resolved down to the minute that actually touches the zone.)

### Entry rule

Enter at the **close of the confirming M1 candle** (the first M1 candle that touches the zone) — a
single, mechanically defined, non-cherry-picked entry point. Direction: bullish OB → long; bearish
OB → short.

### Stop rule

Structural stop placed just beyond the OB zone's own far edge, plus a small, disclosed buffer:
- Bull OB (long): `stop = ob_low − buffer`
- Bear OB (short): `stop = ob_high + buffer`
- `buffer = max(2 × estimated_spread, 0.05% × entry_price)` — the same style of disclosed
  executable-stop-floor convention already used elsewhere in this project (`code/mstrat.py`'s
  `max(2×spread, 5×tick, 0.10×ATR)`), adapted to M1/scalp scale, not fit to this sample's own outcomes.

### Risk and target

`1R = |entry_price − stop_price|`. `TP = entry_price + direction × 2R` (fixed 1:2 RR, per Protocol v2's
own standing convention — not selected after seeing any outcome).

### Primary validation horizon (predeclared — the ONE horizon used for the primary result)

**15 minutes**, chosen because it matches the structural detector's own native M15 resolution (the
timeframe on which "first mitigation" was itself defined) — disclosed before any replay, not selected
after seeing results. **5, 10, 30, 60 minutes, and session-end are recorded as secondary profiling
outputs only, never used to pick the most favorable result.**

### Timeout rule

If neither TP nor SL is touched within the primary 15-minute horizon, classify **TIMEOUT** at the
15-minute mark, recording the bar's own MFE/MAE up to that point regardless.

### Invalidation rule

Classify **INVALID** if: the M1-level data does not actually show a candle touching the OB zone within
the M15 visit-1 bar's own window (a resolution/feed mismatch between the structural M15 detection and
the M1 replay), or if TradingView's own replay/feed does not have data at the required date/time.

### Tie-break rule for same-candle TP/SL ambiguity (frozen in advance, per explicit CEO instruction)

If a single M1 candle's range touches both the TP and the SL level, and no finer-resolution evidence
(e.g. a visible wick-formation order, or a broker's own lower-timeframe tick chart if made available)
resolves which was hit first, classify **AMBIGUOUS**. Never assume the favorable outcome by default.

### Costs (disclosed, estimated, not fit to this sample)

Estimated spread: **$0.25** (typical retail XAUUSD spread). Estimated slippage: **$0.05** per side.
Cost-adjusted R subtracts `(spread + 2×slippage) / 1R` from the raw R outcome of every non-invalid,
non-ambiguous event.

### Event sample (pilot)

Population: all visit-1 events detected on the clean M15 split (`data_split_id =
pre_holdout_2025-10-23T09-15-00Z_v1`), **n = 6,919** (`edge_research/e015_scalp_all_visit1_events.json`).

**Pilot sample-selection rule (frozen before any replay, `edge_research/e015_scalp_reconstruct_events.py`)**:
stratify by `(ob_polarity, session)` (8 non-empty strata found: bull/bear × asia/london/ny/late), draw
one event per stratum in round-robin order using a fixed seed (42, this program's own standing
convention), **outcome-blind — the event's own already-computed structural reaction (continuation/
reversal/MFE/MAE) is never consulted when selecting**, capped at **5 events** for this Phase 0
feasibility pilot (a disclosed reduction from the CEO's own recommended 10-20, given the real per-event
cost of manual candle-by-candle TradingView replay — this pilot's purpose is to expose workflow
problems, not to claim statistical coverage; extendable by a future session if the verdict below is
FEASIBLE or FEASIBLE WITH LIMITATIONS).

### Break-even threshold after estimated costs

For a 1:2 RR trade, gross break-even win rate = 1/3 (33.3%). Net of the disclosed cost estimate above
(cost ≈ 0.35/1R at typical XAUUSD M1 risk distances in this sample, itself only estimable once real risk
distances are observed in the pilot), the cost-adjusted break-even win rate will be computed and
reported per event once real entry/stop prices are recorded — not assumed in advance.

---

## Phase B/C — Pilot replay (this document's own results section)

See `edge_research/e015_scalp_pilot_events.json` for the complete, structured per-event record (all
fields required by the CEO's own mandatory event schema) and the narrative walkthrough below.
