# S26 — Value-Area Rejection / Acceptance

> **Class:** Class III — auction / value  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Excursions beyond the value-area edge (session VWAP +/- k*sigma) are rejected (revert) or accepted (value migrates -> follow). Institutions anchor to value.

## Rules
- **Entry:** reject: onset of an excursion beyond the VA edge that closes back inside (fade); accept: close beyond the edge (follow); enter next open.
- **Exit:** rr2 | rr3 | vwap (revert to VWAP for rejects) | time.
- **Stop-loss:** atr or edge (2 ticks past the excursion bar).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** session VWAP
- **Grammar (degrees of freedom):** mode(reject|accept), k(2.0|3.0), stop, exit

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
- **Hypothesis id:** `51a65f7481bc`
- **Parameters:** `{"mode": "reject", "k": 2.0, "stop": "edge", "exit": "vwap"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3336 |
| Profit Factor | 0.55 |
| Max Drawdown (R) | 1286.82 |
| Win rate | 0.347 |
| Trades (n) | 3826 |
| Positive months | 0/27 |
| Top-1 trade share | 0.007 |
| **OOS expectancy (R/trade)** | -0.1423 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 32 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.1226R · median exp -0.2267R.

## Validation
- **Historical metrics:** expectancy -0.3336R, PF 0.55, maxDD 1286.82R over n=3826 (research 60%).
- **OOS metrics:** expectancy -0.1423R (validation 20%).
- **Drawdown:** 1286.82R (research).
- **Profit Factor:** 0.55.
- **Expectancy:** -0.3336R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 51a65f7481bc: n=3826, exp=-0.3336R, PF=0.55, maxDD=1286.82R, OOS exp=-0.1423R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
