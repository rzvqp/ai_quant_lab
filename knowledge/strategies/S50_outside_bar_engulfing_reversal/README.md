# S50 — Outside-Bar / Engulfing Reversal

> **Class:** Batch2 — candlestick pattern  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
An engulfing (outside) candle that is also a genuine range expansion (>ATR) = a control shift; reversal or continuation. NEW ingredient: candlestick pattern.

## Rules
- **Entry:** Outside bar (high>prior high & low<prior low) with range>ATR; bullish/bearish engulfing; reversal or continuation; enter next open.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** bar (2 ticks past the engulfing bar) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** mode(reversal|continuation), stop, exit

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
- **Hypothesis id:** `9cc65b2c5452`
- **Parameters:** `{"mode": "reversal", "stop": "bar", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.5859 |
| Profit Factor | 0.444 |
| Max Drawdown (R) | 1892.1 |
| Win rate | 0.318 |
| Trades (n) | 3224 |
| Positive months | 0/27 |
| Top-1 trade share | 0.001 |
| **OOS expectancy (R/trade)** | -0.5938 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0724R · median exp -0.1681R.

## Validation
- **Historical metrics:** expectancy -0.5859R, PF 0.444, maxDD 1892.1R over n=3224 (research 60%).
- **OOS metrics:** expectancy -0.5938R (validation 20%).
- **Drawdown:** 1892.1R (research).
- **Profit Factor:** 0.444.
- **Expectancy:** -0.5859R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 9cc65b2c5452: n=3224, exp=-0.5859R, PF=0.444, maxDD=1892.1R, OOS exp=-0.5938R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
