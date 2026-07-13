# S27 — VWAP Reclaim in Trend

> **Class:** Class III — value + trend  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
In the HTF trend, price reclaims session VWAP (mean-revert to VWAP then continue with the trend). Distinct from S26 (excursion).

## Rules
- **Entry:** HTF trend up and a close reclaims above VWAP (or trend down and close breaks below VWAP); onset only; enter next open.
- **Exit:** opp_struct (far VWAP band) | time.
- **Stop-loss:** atr or vwap (fraction of sigma past VWAP).
- **Required confirmations:** HTF trend.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4/H1 trend + session VWAP
- **Grammar (degrees of freedom):** htf(h4|h1), band_k(1.0|2.0), stop, exit

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
- **Hypothesis id:** `90f754da36c5`
- **Parameters:** `{"htf": "h4", "band_k": 1.0, "stop": "vwap", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.4462 |
| Profit Factor | 0.469 |
| Max Drawdown (R) | 1952.65 |
| Win rate | 0.341 |
| Trades (n) | 4364 |
| Positive months | 1/27 |
| Top-1 trade share | 0.005 |
| **OOS expectancy (R/trade)** | -0.2416 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0642R · median exp -0.2263R.

## Validation
- **Historical metrics:** expectancy -0.4462R, PF 0.469, maxDD 1952.65R over n=4364 (research 60%).
- **OOS metrics:** expectancy -0.2416R (validation 20%).
- **Drawdown:** 1952.65R (research).
- **Profit Factor:** 0.469.
- **Expectancy:** -0.4462R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 90f754da36c5: n=4364, exp=-0.4462R, PF=0.469, maxDD=1952.65R, OOS exp=-0.2416R, pos-months 1/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
