# S23 — Squeeze Breakout + HTF Filter

> **Class:** Class II — volatility regime (redesign of S4)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Volatility compresses then expands; take the squeeze breakout ONLY in the HTF trend direction (fixes S4 random direction). Loser = range faders caught at the regime change.

## Rules
- **Entry:** Sustained prior compression (min_sq bars); close breaks the squeeze range on the HTF-trend side; enter next open.
- **Exit:** rr2 | rr3 | trailing | time.
- **Stop-loss:** range_opp (opposite squeeze edge) or atr.
- **Required confirmations:** HTF trend filter.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 or H1 trend
- **Grammar (degrees of freedom):** htf(h4|h1), min_sq(3|6), stop, exit

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
- **Hypothesis id:** `ccee5fc45b0a`
- **Parameters:** `{"htf": "h4", "min_sq": 3, "stop": "range_opp", "exit": "trailing"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.2604 |
| Profit Factor | 0.332 |
| Max Drawdown (R) | 423.44 |
| Win rate | 0.236 |
| Trades (n) | 1627 |
| Positive months | 1/27 |
| Top-1 trade share | 0.061 |
| **OOS expectancy (R/trade)** | -0.1659 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 32 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0911R · median exp -0.1802R.

## Validation
- **Historical metrics:** expectancy -0.2604R, PF 0.332, maxDD 423.44R over n=1627 (research 60%).
- **OOS metrics:** expectancy -0.1659R (validation 20%).
- **Drawdown:** 423.44R (research).
- **Profit Factor:** 0.332.
- **Expectancy:** -0.2604R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 0 historically-profitable, 0 research-worthy. Representative ccee5fc45b0a: n=1627, exp=-0.2604R, PF=0.332, maxDD=423.44R, OOS exp=-0.1659R, pos-months 1/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
