# S14 — Momentum Exhaustion

> **Class:** Momentum exhaustion  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample (flagged FRAGILE — dominated by few periods)

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A sharp move (high |ROC|) that then STALLS (ROC magnitude shrinks) signals exhaustion; fade it. Loser = late momentum chasers.

## Rules
- **Entry:** Onset of acceleration (|ROC3|>k) together with a stall (current |ROC| < prior |ROC|); enter next open against the exhausted move.
- **Exit:** rr2 | time.
- **Stop-loss:** atr or bar (2 ticks past the bar extreme).
- **Required confirmations:** the stall
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** roc_k(0.004|0.008), side, stop, exit

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
- **Hypothesis id:** `4c47c202af20`
- **Parameters:** `{"roc_k": 0.004, "side": "down", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0349 |
| Profit Factor | 1.061 |
| Max Drawdown (R) | 14.01 |
| Win rate | 0.373 |
| Trades (n) | 118 |
| Positive months | 11/25 |
| Top-1 trade share | 0.137 |
| **OOS expectancy (R/trade)** | -0.1374 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | True |

**Family distribution:** 16 hypotheses · 6 historically-profitable · 1 research-worthy · best exp 0.5785R · median exp -0.0688R.

## Validation
- **Historical metrics:** expectancy 0.0349R, PF 1.061, maxDD 14.01R over n=118 (research 60%).
- **OOS metrics:** expectancy -0.1374R (validation 20%).
- **Drawdown:** 14.01R (research).
- **Profit Factor:** 1.061.
- **Expectancy:** 0.0349R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample (flagged FRAGILE — dominated by few periods)
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 16 hypotheses, 6 historically-profitable, 1 research-worthy. Representative 4c47c202af20: n=118, exp=0.0349R, PF=1.061, maxDD=14.01R, OOS exp=-0.1374R, pos-months 11/25, research-worthy, FRAGILE. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
