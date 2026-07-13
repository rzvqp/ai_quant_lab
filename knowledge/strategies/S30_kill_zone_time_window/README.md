# S30 — Kill-Zone Time-Window

> **Class:** Class IV — session time-window  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Pre-registered UTC kill-zones (London 07-10, NY 12-15); breakout of the prior 4-bar range inside the window -> continuation or reversal. Fixed clock (not S5's session-relative range).

## Rules
- **Entry:** Inside the kill-zone, close breaks the prior 4-bar high/low; onset only; continuation or reversal; enter next open.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** London KZ 07-10 UTC | NY KZ 12-15 UTC
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** zone(london_kz|ny_kz), mode(continuation|reversal), exit

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
- **Hypothesis id:** `d660247ea59d`
- **Parameters:** `{"zone": "ny_kz", "mode": "continuation", "stop": "atr", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.1073 |
| Profit Factor | 0.848 |
| Max Drawdown (R) | 159.67 |
| Win rate | 0.344 |
| Trades (n) | 1088 |
| Positive months | 8/27 |
| Top-1 trade share | 0.003 |
| **OOS expectancy (R/trade)** | 0.0554 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0163R · median exp -0.1567R.

## Validation
- **Historical metrics:** expectancy -0.1073R, PF 0.848, maxDD 159.67R over n=1088 (research 60%).
- **OOS metrics:** expectancy 0.0554R (validation 20%).
- **Drawdown:** 159.67R (research).
- **Profit Factor:** 0.848.
- **Expectancy:** -0.1073R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 0 historically-profitable, 0 research-worthy. Representative d660247ea59d: n=1088, exp=-0.1073R, PF=0.848, maxDD=159.67R, OOS exp=0.0554R, pos-months 8/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
