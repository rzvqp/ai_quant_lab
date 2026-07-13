# S18 — Time-of-Day Edge

> **Class:** Calendar / time-of-day  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A fixed intraday hour with a directional bias (session-open flows). Pure clock effect; multiple-testing across hours acknowledged.

## Rules
- **Entry:** At a fixed UTC hour (00,07,08,13,14,20) on the hour, enter next open directionally.
- **Exit:** rr2 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Fixed hours 00/07/08/13/14/20 UTC
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** hour, side, exit

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
- **Hypothesis id:** `2f80a0854e1a`
- **Parameters:** `{"hour": 0, "side": "up", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0316 |
| Profit Factor | 1.037 |
| Max Drawdown (R) | 75.15 |
| Win rate | 0.284 |
| Trades (n) | 550 |
| Positive months | 14/27 |
| Top-1 trade share | 0.019 |
| **OOS expectancy (R/trade)** | 0.0132 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 5 historically-profitable · 0 research-worthy · best exp 0.177R · median exp -0.0756R.

## Validation
- **Historical metrics:** expectancy 0.0316R, PF 1.037, maxDD 75.15R over n=550 (research 60%).
- **OOS metrics:** expectancy 0.0132R (validation 20%).
- **Drawdown:** 75.15R (research).
- **Profit Factor:** 1.037.
- **Expectancy:** 0.0316R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 5 historically-profitable, 0 research-worthy. Representative 2f80a0854e1a: n=550, exp=0.0316R, PF=1.037, maxDD=75.15R, OOS exp=0.0132R, pos-months 14/27, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
