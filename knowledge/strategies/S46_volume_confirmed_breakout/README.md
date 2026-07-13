# S46 — Volume-Confirmed Breakout

> **Class:** Batch1 — participation-gated breakout  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Breakout of a level ONLY when volume expands (conviction) — tests whether VOLUME is the missing ingredient that made the volume-blind breakouts (S3/S23) fail.

## Rules
- **Entry:** Close beyond the `lb`-bar extreme with volume rank >= vthr; onset only; enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** level (2 ticks past the level) or atr.
- **Required confirmations:** REQUIRED: volume expansion.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** vthr(0.70|0.85), lb(20|50), stop, exit

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
- **Selection rule:** research_worthy & largest-n
- **Hypothesis id:** `6131c7eced5d`
- **Parameters:** `{"vthr": 0.85, "lb": 50, "stop": "level", "exit": "rr3"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0172 |
| Profit Factor | 1.052 |
| Max Drawdown (R) | 24.33 |
| Win rate | 0.453 |
| Trades (n) | 519 |
| Positive months | 13/27 |
| Top-1 trade share | 0.016 |
| **OOS expectancy (R/trade)** | -0.017 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 24 hypotheses · 1 historically-profitable · 1 research-worthy · best exp 0.0172R · median exp -0.0966R.

## Validation
- **Historical metrics:** expectancy 0.0172R, PF 1.052, maxDD 24.33R over n=519 (research 60%).
- **OOS metrics:** expectancy -0.017R (validation 20%).
- **Drawdown:** 24.33R (research).
- **Profit Factor:** 1.052.
- **Expectancy:** 0.0172R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 1 historically-profitable, 1 research-worthy. Representative 6131c7eced5d: n=519, exp=0.0172R, PF=1.052, maxDD=24.33R, OOS exp=-0.017R, pos-months 13/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
