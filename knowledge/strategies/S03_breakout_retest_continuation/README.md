# S3 — Breakout Retest Continuation

> **Class:** Breakout-retest momentum  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A genuine breakout of a level, then a retest of that level as new support/resistance, then continuation. Loser = faders of the confirmed breakout.

## Rules
- **Entry:** Close breaks the level; within `retest_within` bars price returns to the level; enter next open in the breakout direction.
- **Exit:** rr2 | rr3 | trailing (1.5*ATR trail).
- **Stop-loss:** beyond_level (2 ticks past the level) or atr.
- **Required confirmations:** The retest hold is the confirmation.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** ref(swing|session), lb(20|50), retest_within(4|8), stop, exit, side

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
- **Selection rule:** hist_profitable & largest-n
- **Hypothesis id:** `6e148815498c`
- **Parameters:** `{"ref": "swing", "lb": 50, "retest_within": 8, "stop": "atr", "exit": "rr3", "side": "up"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0634 |
| Profit Factor | 1.086 |
| Max Drawdown (R) | 40.57 |
| Win rate | 0.332 |
| Trades (n) | 761 |
| Positive months | 15/27 |
| Top-1 trade share | 0.005 |
| **OOS expectancy (R/trade)** | 0.1052 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 96 hypotheses · 2 historically-profitable · 0 research-worthy · best exp 0.0634R · median exp -0.2694R.

## Validation
- **Historical metrics:** expectancy 0.0634R, PF 1.086, maxDD 40.57R over n=761 (research 60%).
- **OOS metrics:** expectancy 0.1052R (validation 20%).
- **Drawdown:** 40.57R (research).
- **Profit Factor:** 1.086.
- **Expectancy:** 0.0634R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 96 hypotheses, 2 historically-profitable, 0 research-worthy. Representative 6e148815498c: n=761, exp=0.0634R, PF=1.086, maxDD=40.57R, OOS exp=0.1052R, pos-months 15/27, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
