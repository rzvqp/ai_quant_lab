# S12 — Range Rotation

> **Class:** Range rotation  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
At a range extreme, a rejection rotates price back toward the centre/opposite edge. Found NEGATIVE (regime-blind — fails in trends).

## Rules
- **Entry:** Onset of price tagging the `lb`-bar rolling extreme; enter next open toward the middle/opposite side.
- **Exit:** rr (to centre ~1.5R) | opp_liq | time.
- **Stop-loss:** ext (2 ticks past the extreme) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** lb(20|50), target(center|opp), side, stop, exit

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
- **Hypothesis id:** `061854e10b15`
- **Parameters:** `{"lb": 20, "target": "center", "side": "down", "stop": "ext", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.2384 |
| Profit Factor | 0.67 |
| Max Drawdown (R) | 484.25 |
| Win rate | 0.408 |
| Trades (n) | 2036 |
| Positive months | 1/27 |
| Top-1 trade share | 0.001 |
| **OOS expectancy (R/trade)** | -0.1921 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 48 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0365R · median exp -0.155R.

## Validation
- **Historical metrics:** expectancy -0.2384R, PF 0.67, maxDD 484.25R over n=2036 (research 60%).
- **OOS metrics:** expectancy -0.1921R (validation 20%).
- **Drawdown:** 484.25R (research).
- **Profit Factor:** 0.67.
- **Expectancy:** -0.2384R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 48 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 061854e10b15: n=2036, exp=-0.2384R, PF=0.67, maxDD=484.25R, OOS exp=-0.1921R, pos-months 1/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
