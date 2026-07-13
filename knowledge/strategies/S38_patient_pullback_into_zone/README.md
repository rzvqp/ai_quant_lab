# S38 — Patient Pullback-into-Zone

> **Class:** Class VII — trend continuation (redesign of S7/S10)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
In an HTF trend, enter on a pullback INTO a discount zone (EMA20/EMA50/fib-0.5) WITHOUT waiting for a confirmation close (better fill than the confirmation crowd). Approximated by market-on-next-open.

## Rules
- **Entry:** HTF trend; onset of price tagging the zone (uptrend pullback down / downtrend pullback up); enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** swing (20-bar extreme) or atr.
- **Required confirmations:** none (patient entry, no confirmation)
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 or H1 trend
- **Grammar (degrees of freedom):** htf(h4|h1), zone(ema20|ema50|fib50), stop, exit

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
- **Hypothesis id:** `7ceb32e972b6`
- **Parameters:** `{"htf": "h1", "zone": "ema20", "stop": "swing", "exit": "trailing"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.2386 |
| Profit Factor | 0.371 |
| Max Drawdown (R) | 541.46 |
| Win rate | 0.263 |
| Trades (n) | 2269 |
| Positive months | 1/27 |
| Top-1 trade share | 0.017 |
| **OOS expectancy (R/trade)** | -0.1003 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 36 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0983R · median exp -0.1763R.

## Validation
- **Historical metrics:** expectancy -0.2386R, PF 0.371, maxDD 541.46R over n=2269 (research 60%).
- **OOS metrics:** expectancy -0.1003R (validation 20%).
- **Drawdown:** 541.46R (research).
- **Profit Factor:** 0.371.
- **Expectancy:** -0.2386R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 36 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 7ceb32e972b6: n=2269, exp=-0.2386R, PF=0.371, maxDD=541.46R, OOS exp=-0.1003R, pos-months 1/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
