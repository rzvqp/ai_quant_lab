# S49 — Narrowest-Range (NR) Breakout

> **Class:** Batch2 — NR pattern  ·  **Status:** INVALID  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** INVALID

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
The NR-N compression pattern (smallest range of the last N bars) as the breakout trigger. TECHNICALLY INVALID: the pattern is non-selective (fires too often to be a discrete setup); NOT backtested/retained.

## Rules
- **Entry:** An NR-N bar, then a close beyond that bar's high/low within a few bars; breakout or fade; enter next open.
- **Exit:** rr2 | time.
- **Stop-loss:** bar (2 ticks past the NR bar) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** N(4|7), mode(breakout|fade), stop, exit

### Invalid conditions
- ATR non-finite or <= 0 at the signal bar
- signal on the last available bar (no next-open to fill)
- a position is already open (overlap suppression)
- INVALID — non-selective trigger (fails the discrete-setup selectivity gate); excluded from results.

### Position sizing assumptions
- **model:** risk-normalised (1R per trade)
- **risk_definition:** risk = |entry - executable_stop|; result R = (dir*(exit-entry) - 2*cost)/risk
- **stop_floor:** executable risk = max(2*spread_ticks*tick, 5*tick, 0.10*ATR) = max(0.20, 0.50, 0.10*ATR) price units (v2, pre-registered)
- **costs:** (spread 1 + slippage 1) ticks/side * 0.1 = 0.10/side; 0.20 round-trip charged in R
- **concurrency:** ONE position at a time (overlapping signals suppressed until the open trade closes)
- **absolute_size:** lot = per-trade risk budget / risk-distance — an EXECUTION-LAYER decision, NOT set by the research

## Executable default (representative hypothesis)
- **Selection rule:** no committed results
- **Hypothesis id:** `—`

## Performance summary (research segment; frozen)
_No committed results for this family._

**Family distribution:** 0 hypotheses · 0 historically-profitable · 0 research-worthy · best exp —R · median exp —R.

## Validation
- **Historical metrics:** expectancy —R, PF —, maxDD —R over n=— (research 60%).
- **OOS metrics:** expectancy —R (validation 20%).
- **Drawdown:** —R (research).
- **Profit Factor:** —.
- **Expectancy:** —R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** INVALID
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. THIS FAMILY IS INVALID: INVALID — non-selective trigger (fails the discrete-setup selectivity gate); excluded from results.

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
