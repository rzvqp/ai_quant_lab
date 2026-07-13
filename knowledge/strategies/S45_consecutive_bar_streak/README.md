# S45 — Consecutive-Bar Streak

> **Class:** Batch1 — sequence / run-length  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
N consecutive same-direction closes -> reverse (overextension) or continue (momentum). NEW ingredient: raw close-streak length. k=3 excluded (not "extended").

## Rules
- **Entry:** Exactly k consecutive up/down closes (streak onset); reverse or continue; enter next open.
- **Exit:** rr2 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** k(4|5|6), mode(reverse|continue), exit

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
- **Selection rule:** hist_profitable & largest-n
- **Hypothesis id:** `19ff587f4e5c`
- **Parameters:** `{"k": 6, "mode": "reverse", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0448 |
| Profit Factor | 1.063 |
| Max Drawdown (R) | 39.05 |
| Win rate | 0.334 |
| Trades (n) | 601 |
| Positive months | 11/27 |
| Top-1 trade share | 0.034 |
| **OOS expectancy (R/trade)** | 0.1299 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 1 historically-profitable · 0 research-worthy · best exp 0.0448R · median exp -0.1029R.

## Validation
- **Historical metrics:** expectancy 0.0448R, PF 1.063, maxDD 39.05R over n=601 (research 60%).
- **OOS metrics:** expectancy 0.1299R (validation 20%).
- **Drawdown:** 39.05R (research).
- **Profit Factor:** 1.063.
- **Expectancy:** 0.0448R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 1 historically-profitable, 0 research-worthy. Representative 19ff587f4e5c: n=601, exp=0.0448R, PF=1.063, maxDD=39.05R, OOS exp=0.1299R, pos-months 11/27, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
