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

## Phase B — Pilot replay: narrative walkthrough

**Environment check**: `tv_health_check` confirmed a live CDP connection to TradingView Desktop
(`cdp_connected: true`), chart initially on `FUSIONMARKETS:XAUUSD`, 45-min resolution, with the user's
own SMC/ICT indicator set loaded (irrelevant to raw OHLCV replay, noted for completeness).

**Setup steps taken** (verified working correctly):
1. `chart_set_symbol("OANDA:XAUUSD")` — succeeded. Switched away from the original
   `FUSIONMARKETS:XAUUSD` feed specifically to match this repository's own OANDA data provenance and
   avoid an unnecessary cross-provider confound, per the mandatory event schema's own
   "provider/feed shown in TradingView" field.
2. `chart_set_timeframe("1")` — succeeded, chart confirmed ready at M1.

**Pilot attempt 1 (`E015SCALP-PILOT-01`, 2023-03-22, ~asia session)**:
- `chart_scroll_to_date("2023-03-22")` reported success with a plausible-looking centered timestamp.
- `replay_start(date="2023-03-22")` reported `success: true`, but the returned `current_date` field
  (1753075260) decoded to the **live, real-time bar** (2026-07-21), not 2023-03-22.
- Repeated with a fresh `chart_scroll_to_date` immediately before `replay_start`, and again with no
  `date` argument at all (letting the tool "select first available date") — same result each time:
  the reported/actual position stayed at the live bar.
- A screenshot taken at this point (`e015_scalp_evidence/e015_scalp_diag_scroll_2023-03-22.png`) shows
  two decisive facts directly from the TradingView UI itself (not inferred): (a) an unhandled **"Continue
  your last replay?"** modal dialog was open, and (b) a native TradingView toast reading **"Data point
  unavailable — The selected date is not available for playback."** The dialog was cleared via
  `ui_click(by="text", value="Start new")`.

**Pilot attempt 2 (`E015SCALP-PILOT-05`, 2025-05-28, ~late session)** — deliberately chosen recent
(~8 weeks before this session) to separate "date too old for this feed's retention" from "the tool's
own seek mechanism is broken":
- Same `chart_scroll_to_date` → `replay_start(date="2025-05-28")` sequence. `replay_start` again
  reported success, `current_date` again decoded to the live real-time bar.
- **No "data unavailable" toast appeared this time** — a screenshot
  (`e015_scalp_evidence/e015_scalp_diag_2025-05-28.png`) shows the "Replay" watermark active (confirming
  replay mode genuinely engaged) but the visible price/date is the live one ($3,364.50, matching the
  live quote), not 2025-05-28.
- `replay_step()` was then called once: `current_date` advanced from 1753075380 to 1753075439 — **exactly
  59-60 seconds, i.e. a correct, precise one-minute step**. This confirms candle-by-candle advancement
  itself works correctly **once replay is active** — the defect is specifically in seeking to a
  requested **start** date, not in stepping forward from wherever replay happens to be.

**Remaining 3 pilot events (`PILOT-02/03/04`) were not attempted.** The blocking defect was reproduced
identically on two independent dates (one ~3.3 years back, one ~8 weeks back); attempting the same
diagnostic a third, fourth, and fifth time would not add information, consistent with Phase 0's own
purpose (expose workflow problems, not accumulate a large sample once the blocker is confirmed).

**Full structured record**: `edge_research/e015_scalp_pilot_events.json` (all fields from the mandatory
event schema, for all 5 pilot events).

## Phase D — Feasibility report

**What worked**: CDP connection, symbol switching, timeframe switching, entering replay mode itself
(confirmed via the "Replay" watermark), single-bar step precision (exactly 1 minute per `replay_step`
call), screenshot evidence capture, and UI-dialog handling via `ui_click`.

**What did not work**: `replay_start`'s own `date` parameter did not seek the chart/replay to the
requested historical date in either test — the position consistently remained at (or reverted to) the
live real-time bar. This was tested with a prior `chart_scroll_to_date` to the same date immediately
beforehand (which itself reported a plausible-looking centered timestamp), and without any prior scroll
at all — same failure both ways.

**Two distinct signals, not fully separated by this pilot**:
1. For the older date (2023-03-22, ~3.3 years back), TradingView's own native UI produced a **"Data
   point unavailable — The selected date is not available for playback"** toast — consistent with a
   real feed-retention limit on how far back M1 replay history extends for `OANDA:XAUUSD` on this
   TradingView connection/plan, independent of any tooling defect.
2. For the recent date (2025-05-28, ~8 weeks back — almost certainly within any reasonable M1 retention
   window), no such toast appeared, yet the seek still failed identically — pointing to a genuine
   **automation/tool-integration defect** in how `replay_start`'s `date` argument is wired to
   TradingView's own internal replay-seek mechanism, separate from any data-retention question.

**Per the CEO's own explicit instruction** ("If automation skips candles, loses replay position...
stop and document the issue. Do not silently substitute manual visual assumptions for missing
automation capability"), no attempt was made to work around this by manually estimating candle
positions, clicking blindly at inferred chart-pixel coordinates to select a historical bar, or otherwise
approximating the seek. This is a **tooling-capability finding**, not a claim that TradingView Bar
Replay is inherently unusable by a human operator through the ordinary UI — a person manually
scrolling/clicking through TradingView's own Bar Replay panel might well succeed where this specific
automated `date`-parameter path did not; that distinction is explicitly not resolved by this pilot.

### Mandatory feasibility verdict

**C. NOT FEASIBLE** — with the currently available automated TradingView Replay tooling, specifically:
timestamp-seeking to a precise historical event start point is unreliable (reproduced on two
independent dates, one additionally implicating a possible feed-retention limit), which makes formal,
scaled validation (10+ events, let alone the full 6,919-event visit-1 population) impractical and
untrustworthy at this time. This is a **tooling/data-access limitation finding, not a judgment on E015's
own structural finding** (unchanged, see `E015_order_block_remitigation.md`) and not a judgment on
whether TradingView Replay could ever work for this purpose via a different automation approach or
manual operation.

### What would need to change before re-attempting Phase 0

1. **Diagnose and fix (or replace) the `replay_start` date-seek path** — e.g. confirm whether the
   underlying CDP script actually passes the date through to TradingView's own replay-selection API, or
   whether a UI-click-based date selection (via `ui_find_element`/`ui_mouse_click` on TradingView's own
   Bar Replay date picker) is required instead of the current parameterized call.
2. **Separately confirm the feed's own M1 replay retention window** for `OANDA:XAUUSD` (or an
   alternative broker feed) on this TradingView plan — e.g. by manually testing Bar Replay via the
   ordinary UI (outside automation) at a few known dates to establish the actual lookback boundary,
   before assuming any specific historical event is reachable.
3. Only once both of the above are resolved should Phase 0 be re-attempted, ideally against the full
   5-event pilot sample already selected (`e015_scalp_pilot_sample.json`) plus enough of the remaining
   6,914 unused visit-1 events to reach the CEO's own recommended 10-20 count.

**E015-SCALP is NOT accepted, NOT rejected, and remains at Phase 0 — incomplete due to a tooling
blocker**, not due to any finding about the underlying market behavior. E015's own structural result
(V0 NOT SUPPORTED as registered; V1 candidate = "reaction concentrated in the first mitigation only")
is unchanged and continues to stand as a **structural-behavior Discovery** result only — its own status
already states this is not yet a validated scalp, and this pilot has not changed that determination
either way.
