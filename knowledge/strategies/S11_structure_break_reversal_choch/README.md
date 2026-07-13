# S11 — Structure-Break Reversal (CHoCH)

> **Class:** Structure-break reversal  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
In an HTF trend, a break of the opposite recent swing (change-of-character) signals a reversal. Found NEGATIVE (regime-blind; the router S40 addresses this).

## Rules
- **Entry:** HTF trend up and close < `lb`-bar rolling min (or trend down and close > rolling max) — onset only; enter next open counter to the prior trend.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** struct (20-bar extreme) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 or H1 trend
- **Grammar (degrees of freedom):** htf(h4|h1), lb(20|50), stop, exit

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
- **Hypothesis id:** `842deff14459`
- **Parameters:** `{"htf": "h4", "lb": 20, "stop": "atr", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.1668 |
| Profit Factor | 0.776 |
| Max Drawdown (R) | 205.01 |
| Win rate | 0.329 |
| Trades (n) | 1210 |
| Positive months | 4/27 |
| Top-1 trade share | 0.003 |
| **OOS expectancy (R/trade)** | -0.0441 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0525R · median exp -0.1203R.

## Validation
- **Historical metrics:** expectancy -0.1668R, PF 0.776, maxDD 205.01R over n=1210 (research 60%).
- **OOS metrics:** expectancy -0.0441R (validation 20%).
- **Drawdown:** 205.01R (research).
- **Profit Factor:** 0.776.
- **Expectancy:** -0.1668R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 842deff14459: n=1210, exp=-0.1668R, PF=0.776, maxDD=205.01R, OOS exp=-0.0441R, pos-months 4/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
