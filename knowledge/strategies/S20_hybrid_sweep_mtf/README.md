# S20 — Hybrid Sweep + MTF

> **Class:** Hybrid (composite)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Combines S9 MTF-trend context with an S1-style sweep or breakout trigger — a non-arbitrary composite. Loser = counter-trend sweep faders.

## Rules
- **Entry:** 4H trend context plus a sweep (or breakout onset) of the `lb`-bar extreme in the trend direction; enter next open.
- **Exit:** rr2 | rr3.
- **Stop-loss:** atr or struct.
- **Required confirmations:** MTF trend context
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 trend
- **Grammar (degrees of freedom):** ctx(h4up|h4down), trig(sweep|breakout), lb(20|50), stop, exit

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
- **Hypothesis id:** `e38573221e35`
- **Parameters:** `{"ctx": "h4up", "trig": "breakout", "lb": 20, "stop": "struct", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0553 |
| Profit Factor | 1.121 |
| Max Drawdown (R) | 10.76 |
| Win rate | 0.469 |
| Trades (n) | 469 |
| Positive months | 15/26 |
| Top-1 trade share | 0.009 |
| **OOS expectancy (R/trade)** | 0.1371 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 32 hypotheses · 6 historically-profitable · 5 research-worthy · best exp 0.0994R · median exp -0.1673R.

## Validation
- **Historical metrics:** expectancy 0.0553R, PF 1.121, maxDD 10.76R over n=469 (research 60%).
- **OOS metrics:** expectancy 0.1371R (validation 20%).
- **Drawdown:** 10.76R (research).
- **Profit Factor:** 1.121.
- **Expectancy:** 0.0553R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 6 historically-profitable, 5 research-worthy. Representative e38573221e35: n=469, exp=0.0553R, PF=1.121, maxDD=10.76R, OOS exp=0.1371R, pos-months 15/26, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
