# S21 — Equal-Highs/Lows Liquidity-Pool Raid

> **Class:** Class I — resting liquidity  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Stops/breakout orders pool at CLUSTERS of equal highs/lows (a level tested >=2x). Large players raid the pool then price reverses. Stronger/rarer than S1 (requires a multi-touch pool).

## Rules
- **Entry:** A level touched >= min_touches times in the last 20 bars, then a raid (sweep beyond) with a close back inside; enter next open (reversal).
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** beyond_raid (2 ticks past the raid) or structural.
- **Required confirmations:** the multi-touch pool + close-back-inside rejection.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** side, lb(20|50), min_touches(2|3), stop, exit

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
- **Hypothesis id:** `6ddb75c3f9b1`
- **Parameters:** `{"side": "high", "lb": 20, "min_touches": 2, "stop": "beyond_raid", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3669 |
| Profit Factor | 0.586 |
| Max Drawdown (R) | 868.62 |
| Win rate | 0.314 |
| Trades (n) | 2354 |
| Positive months | 0/27 |
| Top-1 trade share | 0.002 |
| **OOS expectancy (R/trade)** | -0.2608 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 48 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0923R · median exp -0.2756R.

## Validation
- **Historical metrics:** expectancy -0.3669R, PF 0.586, maxDD 868.62R over n=2354 (research 60%).
- **OOS metrics:** expectancy -0.2608R (validation 20%).
- **Drawdown:** 868.62R (research).
- **Profit Factor:** 0.586.
- **Expectancy:** -0.3669R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 48 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 6ddb75c3f9b1: n=2354, exp=-0.3669R, PF=0.586, maxDD=868.62R, OOS exp=-0.2608R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
