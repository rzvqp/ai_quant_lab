# S17 — Weekly Levels

> **Class:** Reference-level (weekly)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Prior-week high/low as higher-timeframe decision levels — breakout or rejection.

## Rules
- **Entry:** Onset of a close beyond prev-week high/low (breakout) or a tag-then-reject; enter next open.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr or level.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** Weekly levels
- **Grammar (degrees of freedom):** level(pw_high|pw_low), mode(breakout|reject), stop, exit

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
- **Hypothesis id:** `f5afb9813f83`
- **Parameters:** `{"level": "pw_high", "mode": "reject", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0567 |
| Profit Factor | 1.082 |
| Max Drawdown (R) | 21.06 |
| Win rate | 0.353 |
| Trades (n) | 187 |
| Positive months | 13/25 |
| Top-1 trade share | 0.071 |
| **OOS expectancy (R/trade)** | 0.0312 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 24 hypotheses · 6 historically-profitable · 5 research-worthy · best exp 0.4235R · median exp -0.2033R.

## Validation
- **Historical metrics:** expectancy 0.0567R, PF 1.082, maxDD 21.06R over n=187 (research 60%).
- **OOS metrics:** expectancy 0.0312R (validation 20%).
- **Drawdown:** 21.06R (research).
- **Profit Factor:** 1.082.
- **Expectancy:** 0.0567R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 6 historically-profitable, 5 research-worthy. Representative f5afb9813f83: n=187, exp=0.0567R, PF=1.082, maxDD=21.06R, OOS exp=0.0312R, pos-months 13/25, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
