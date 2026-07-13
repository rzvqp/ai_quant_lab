# S6 — Session-Transition

> **Class:** Session-transition momentum  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Early in London/NY, price interacts with the PRIOR session high/low; breakout (continuation) or fade (reversion) of that level as the new session takes control.

## Rules
- **Entry:** In the first ~10 bars of the target session, cross of the prior-session high/low; breakout enters with the cross, fade enters against a tag-without-cross; enter next open.
- **Exit:** rr2 | time.
- **Stop-loss:** prev_ext (2 ticks past the level) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** london | ny (parameter)
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** session(london|ny), mode(breakout|fade), side, stop, exit

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
- **Hypothesis id:** `285dcba858f4`
- **Parameters:** `{"session": "ny", "mode": "breakout", "side": "up", "stop": "atr", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.017 |
| Profit Factor | 1.027 |
| Max Drawdown (R) | 23.91 |
| Win rate | 0.395 |
| Trades (n) | 395 |
| Positive months | 12/27 |
| Top-1 trade share | 0.008 |
| **OOS expectancy (R/trade)** | 0.1604 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 32 hypotheses · 7 historically-profitable · 3 research-worthy · best exp 0.4973R · median exp -0.2893R.

## Validation
- **Historical metrics:** expectancy 0.017R, PF 1.027, maxDD 23.91R over n=395 (research 60%).
- **OOS metrics:** expectancy 0.1604R (validation 20%).
- **Drawdown:** 23.91R (research).
- **Profit Factor:** 1.027.
- **Expectancy:** 0.017R/trade.
- **Monte Carlo summary:** Matched-null pilot used an S6 extreme hypothesis as a known tiny-stop/outlier CONTROL (not this representative).
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 7 historically-profitable, 3 research-worthy. Representative 285dcba858f4: n=395, exp=0.017R, PF=1.027, maxDD=23.91R, OOS exp=0.1604R, pos-months 12/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
