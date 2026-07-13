# S40 — Regime Router

> **Class:** Class VIII — meta / regime router  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Deploy each sub-edge only where its mechanism holds: TREND regime (efficiency>=thr) -> efficient continuation; RANGE regime -> fade extremes back to the middle. Addresses S11/S12 regime-blindness.

## Rules
- **Entry:** Classify regime by efficiency ratio; trend -> expansion continuation (like S39); range -> fade the `range_lb` rolling extreme back to the middle; onset only; enter next open.
- **Exit:** rr2 | rr3 (range legs target the range middle).
- **Stop-loss:** atr or swing.
- **Required confirmations:** the regime classification.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** efficiency-ratio regime
- **Grammar (degrees of freedom):** er_thr(0.3|0.5), range_lb(20|50), stop, exit

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
- **Hypothesis id:** `69f673010580`
- **Parameters:** `{"er_thr": 0.5, "range_lb": 20, "stop": "swing", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3109 |
| Profit Factor | 0.62 |
| Max Drawdown (R) | 1073.11 |
| Win rate | 0.337 |
| Trades (n) | 3453 |
| Positive months | 0/27 |
| Top-1 trade share | 0.007 |
| **OOS expectancy (R/trade)** | -0.1335 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 16 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.1178R · median exp -0.1802R.

## Validation
- **Historical metrics:** expectancy -0.3109R, PF 0.62, maxDD 1073.11R over n=3453 (research 60%).
- **OOS metrics:** expectancy -0.1335R (validation 20%).
- **Drawdown:** 1073.11R (research).
- **Profit Factor:** 0.62.
- **Expectancy:** -0.3109R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 16 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 69f673010580: n=3453, exp=-0.3109R, PF=0.62, maxDD=1073.11R, OOS exp=-0.1335R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
