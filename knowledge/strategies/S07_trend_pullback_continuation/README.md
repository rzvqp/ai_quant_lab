# S7 — Trend Pullback Continuation

> **Class:** Trend-pullback continuation  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
In an established HTF trend, a pullback to the M15 EMA20 then a confirmation close back in the trend direction resumes the move. Found NEGATIVE (late entries; the redesign is S38).

## Rules
- **Entry:** HTF trend up/down; price pulls to the wrong side of EMA20; within `pb_within` bars a close returns through EMA20; enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** ema (2 ticks past EMA at entry) or atr.
- **Required confirmations:** REQUIRED: the confirmation close back through EMA20.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 or H1 trend
- **Grammar (degrees of freedom):** htf(h4|h1), stop, exit, pb_within(4|8)

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
- **Hypothesis id:** `c91b945af60e`
- **Parameters:** `{"htf": "h4", "stop": "ema", "exit": "rr2", "pb_within": 8}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.5641 |
| Profit Factor | 0.449 |
| Max Drawdown (R) | 1844.9 |
| Win rate | 0.324 |
| Trades (n) | 3270 |
| Positive months | 0/27 |
| Top-1 trade share | 0.001 |
| **OOS expectancy (R/trade)** | -0.4291 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0987R · median exp -0.3999R.

## Validation
- **Historical metrics:** expectancy -0.5641R, PF 0.449, maxDD 1844.9R over n=3270 (research 60%).
- **OOS metrics:** expectancy -0.4291R (validation 20%).
- **Drawdown:** 1844.9R (research).
- **Profit Factor:** 0.449.
- **Expectancy:** -0.5641R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 0 historically-profitable, 0 research-worthy. Representative c91b945af60e: n=3270, exp=-0.5641R, PF=0.449, maxDD=1844.9R, OOS exp=-0.4291R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
