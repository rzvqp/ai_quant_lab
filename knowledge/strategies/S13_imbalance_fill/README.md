# S13 — Imbalance Fill

> **Class:** Imbalance / FVG reaction  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A fair-value gap (imbalance) tends to be filled then produce a reaction (revert) or act as continuation. Loser depends on mode.

## Rules
- **Entry:** Onset of an FVG (bull or bear); enter next open — revert (against the gap) or continue (with it).
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr or struct (20-bar extreme).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** fvg(bull|bear), mode(revert|continue), stop, exit

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
- **Hypothesis id:** `45116649200d`
- **Parameters:** `{"fvg": "bull", "mode": "continue", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0199 |
| Profit Factor | 1.028 |
| Max Drawdown (R) | 121.8 |
| Win rate | 0.338 |
| Trades (n) | 1928 |
| Positive months | 16/27 |
| Top-1 trade share | 0.009 |
| **OOS expectancy (R/trade)** | 0.0732 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 5 historically-profitable · 0 research-worthy · best exp 0.0405R · median exp -0.1531R.

## Validation
- **Historical metrics:** expectancy 0.0199R, PF 1.028, maxDD 121.8R over n=1928 (research 60%).
- **OOS metrics:** expectancy 0.0732R (validation 20%).
- **Drawdown:** 121.8R (research).
- **Profit Factor:** 1.028.
- **Expectancy:** 0.0199R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 5 historically-profitable, 0 research-worthy. Representative 45116649200d: n=1928, exp=0.0199R, PF=1.028, maxDD=121.8R, OOS exp=0.0732R, pos-months 16/27, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
