# S51 — Intraday Range-Position Reversion

> **Class:** Batch2 — session range position  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Position within the developing SESSION range: near the top/bottom -> revert toward the middle. Distinct from S8 (SMA distance) and S26 (VWAP band).

## Rules
- **Entry:** After the session range has formed (>=8 bars), price at >= thr (short) or <= 1-thr (long) of the session range; onset only; enter next open (revert).
- **Exit:** rr2 | time.
- **Stop-loss:** atr or edge (2 ticks past the session extreme).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions (intraday range)
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** thr(0.85|0.95), stop, exit

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
- **Hypothesis id:** `893393d0f0bc`
- **Parameters:** `{"thr": 0.85, "stop": "edge", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3491 |
| Profit Factor | 0.592 |
| Max Drawdown (R) | 1190.79 |
| Win rate | 0.436 |
| Trades (n) | 3410 |
| Positive months | 0/27 |
| Top-1 trade share | 0.001 |
| **OOS expectancy (R/trade)** | -0.2622 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 8 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.1261R · median exp -0.1796R.

## Validation
- **Historical metrics:** expectancy -0.3491R, PF 0.592, maxDD 1190.79R over n=3410 (research 60%).
- **OOS metrics:** expectancy -0.2622R (validation 20%).
- **Drawdown:** 1190.79R (research).
- **Profit Factor:** 0.592.
- **Expectancy:** -0.3491R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 8 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 893393d0f0bc: n=3410, exp=-0.3491R, PF=0.592, maxDD=1190.79R, OOS exp=-0.2622R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
