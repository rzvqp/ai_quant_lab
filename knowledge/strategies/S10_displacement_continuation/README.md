# S10 — Displacement Continuation

> **Class:** Displacement continuation  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A displacement bar (range>k*ATR with matching close) marks strong intent; a controlled pullback then continuation. Found NEGATIVE standalone.

## Rules
- **Entry:** Displacement bar; within `pb` bars price pulls back to the displacement close; enter next open in the displacement direction.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** bar (2 ticks past the displacement bar) or atr.
- **Required confirmations:** the controlled pullback
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** disp_k(1.5|2.0), pb(2|4), side, stop, exit

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
- **Selection rule:** largest-n (no positive hypothesis)
- **Hypothesis id:** `208de46a2aa8`
- **Parameters:** `{"disp_k": 1.5, "pb": 4, "side": "down", "stop": "bar", "exit": "trailing"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3217 |
| Profit Factor | 0.4 |
| Max Drawdown (R) | 1076.09 |
| Win rate | 0.269 |
| Trades (n) | 3346 |
| Positive months | 0/27 |
| Top-1 trade share | 0.026 |
| **OOS expectancy (R/trade)** | -0.3042 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 48 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0505R · median exp -0.2305R.

## Validation
- **Historical metrics:** expectancy -0.3217R, PF 0.4, maxDD 1076.09R over n=3346 (research 60%).
- **OOS metrics:** expectancy -0.3042R (validation 20%).
- **Drawdown:** 1076.09R (research).
- **Profit Factor:** 0.4.
- **Expectancy:** -0.3217R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 48 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 208de46a2aa8: n=3346, exp=-0.3217R, PF=0.4, maxDD=1076.09R, OOS exp=-0.3042R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
