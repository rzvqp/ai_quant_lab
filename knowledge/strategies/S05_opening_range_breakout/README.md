# S5 — Opening-Range Breakout

> **Class:** Opening-range momentum  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
The first 4 M15 bars of a session define an opening range; a break of that range signals the session directional bias. Loser = mean-reversion faders of the OR break. (Wave-1 EXP-04: much of the edge is session/regime BETA.)

## Rules
- **Entry:** After the OR forms (bar_in_sess in 4..20), close breaks the OR high (up) or low (down); enter next open.
- **Exit:** rr2 | rr3 | opp_liq | time.
- **Stop-loss:** or_opp (opposite OR edge) or atr.
- **Required confirmations:** none (breakout close is the trigger)
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Session-specific: asia | london | ny (parameter)
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** session, mode(breakout|retest), stop, exit, side

### Invalid conditions
- ATR non-finite or <= 0 at the signal bar
- signal on the last available bar (no next-open to fill)
- a position is already open (overlap suppression)

### Position sizing assumptions
- **model:** risk-normalised (1R per trade)
- **risk_definition:** risk = |entry - executable_stop|; result R = (dir*(exit-entry) - 2*cost)/risk
- **stop_floor:** executable risk = max(2*spread_ticks*tick, 5*tick, 0.10*ATR) = max(0.20, 0.50, 0.10*ATR) price units (v2, pre-registered)
- **costs:** (spread 1 + slippage 1) ticks/side * 0.1 = 0.10/side; 0.20 round-trip charged in R
- **concurrency:** ONE position at a time (overlapping signals suppressed until the open trade closes)
- **absolute_size:** lot = per-trade risk budget / risk-distance — an EXECUTION-LAYER decision, NOT set by the research

## Executable default (representative hypothesis)
- **Selection rule:** research_worthy & largest-n
- **Hypothesis id:** `3a9d271b56b8`
- **Parameters:** `{"session": "ny", "mode": "breakout", "stop": "atr", "exit": "rr2", "side": "up"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0756 |
| Profit Factor | 1.135 |
| Max Drawdown (R) | 14.3 |
| Win rate | 0.441 |
| Trades (n) | 406 |
| Positive months | 14/27 |
| Top-1 trade share | 0.008 |
| **OOS expectancy (R/trade)** | 0.2371 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 96 hypotheses · 20 historically-profitable · 12 research-worthy · best exp 0.1658R · median exp -0.1041R.

## Validation
- **Historical metrics:** expectancy 0.0756R, PF 1.135, maxDD 14.3R over n=406 (research 60%).
- **OOS metrics:** expectancy 0.2371R (validation 20%).
- **Drawdown:** 14.3R (research).
- **Profit Factor:** 1.135.
- **Expectancy:** 0.0756R/trade.
- **Monte Carlo summary:** Matched-null pilot (research). Wave-1 EXP-04 beta/regime-matched null p=0.177 (NOT significant) -> the edge is substantially session/regime BETA (unstratified anchor p=0.034). I7 stands for this primitive.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 96 hypotheses, 20 historically-profitable, 12 research-worthy. Representative 3a9d271b56b8: n=406, exp=0.0756R, PF=1.135, maxDD=14.3R, OOS exp=0.2371R, pos-months 14/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
