# S15 — Trend Acceleration

> **Class:** Trend acceleration  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A trend plus a fresh range/momentum expansion bar continues. Found NEGATIVE (buys local tops; the fix is the efficiency-gated S39).

## Rules
- **Entry:** HTF/M15 trend and onset of an expansion bar (range>k*ATR) in the trend direction; enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** atr or struct.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 or H1 trend
- **Grammar (degrees of freedom):** htf(h4|h1), exp_k(1.5|2.0), stop, exit

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
- **Hypothesis id:** `3d62ddd9a828`
- **Parameters:** `{"htf": "h1", "exp_k": 1.5, "stop": "atr", "exit": "trailing"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.2812 |
| Profit Factor | 0.404 |
| Max Drawdown (R) | 830.41 |
| Win rate | 0.278 |
| Trades (n) | 2939 |
| Positive months | 2/27 |
| Top-1 trade share | 0.037 |
| **OOS expectancy (R/trade)** | -0.1987 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.05R · median exp -0.1166R.

## Validation
- **Historical metrics:** expectancy -0.2812R, PF 0.404, maxDD 830.41R over n=2939 (research 60%).
- **OOS metrics:** expectancy -0.1987R (validation 20%).
- **Drawdown:** 830.41R (research).
- **Profit Factor:** 0.404.
- **Expectancy:** -0.2812R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 3d62ddd9a828: n=2939, exp=-0.2812R, PF=0.404, maxDD=830.41R, OOS exp=-0.1987R, pos-months 2/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
