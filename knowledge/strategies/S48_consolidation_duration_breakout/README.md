# S48 — Consolidation-Duration Breakout

> **Class:** Batch2 — compression duration  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
TIME spent compressed (run-length of compression), not the compression level — longer coil -> larger expansion. Distinct from S23 (level + HTF).

## Rules
- **Entry:** D consecutive compressed bars, then a close beyond the D-bar band; onset only; enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** range (opposite band edge) or atr.
- **Required confirmations:** the sustained coil.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** D(6|12), stop, exit

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
- **Hypothesis id:** `38fa907224e9`
- **Parameters:** `{"D": 6, "stop": "range", "exit": "trailing"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.2184 |
| Profit Factor | 0.285 |
| Max Drawdown (R) | 402.2 |
| Win rate | 0.234 |
| Trades (n) | 1843 |
| Positive months | 0/27 |
| Top-1 trade share | 0.025 |
| **OOS expectancy (R/trade)** | -0.1314 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.1296R · median exp -0.2274R.

## Validation
- **Historical metrics:** expectancy -0.2184R, PF 0.285, maxDD 402.2R over n=1843 (research 60%).
- **OOS metrics:** expectancy -0.1314R (validation 20%).
- **Drawdown:** 402.2R (research).
- **Profit Factor:** 0.285.
- **Expectancy:** -0.2184R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 38fa907224e9: n=1843, exp=-0.2184R, PF=0.285, maxDD=402.2R, OOS exp=-0.1314R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
