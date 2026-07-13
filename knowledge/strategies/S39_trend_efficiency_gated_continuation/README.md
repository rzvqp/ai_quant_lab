# S39 — Trend-Efficiency-Gated Continuation

> **Class:** Class VII — efficient continuation (redesign of S15)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Take continuation ONLY when the trend is CLEAN — high Kaufman efficiency ratio (net move / path length) predicts persistence; skip noisy chop. Loser = counter-trend faders in efficient trends. (Wave-1 EXP-02: the gate did not beat random selection at the family-wise bar.)

## Rules
- **Entry:** M15 trend + an expansion bar (range>1.5*ATR, matching close) GATED by efficiency ratio >= er_thr over L bars; onset only; enter next open.
- **Exit:** rr2 | rr3 | trailing.
- **Stop-loss:** atr or swing (20-bar extreme).
- **Required confirmations:** the efficiency-ratio gate.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** M15 trend + efficiency ratio
- **Grammar (degrees of freedom):** L(10|20), er_thr(0.3|0.5), stop, exit

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
- **Hypothesis id:** `13752e544049`
- **Parameters:** `{"L": 20, "er_thr": 0.5, "stop": "swing", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0289 |
| Profit Factor | 1.085 |
| Max Drawdown (R) | 11.65 |
| Win rate | 0.472 |
| Trades (n) | 320 |
| Positive months | 14/27 |
| Top-1 trade share | 0.02 |
| **OOS expectancy (R/trade)** | 0.0179 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 24 hypotheses · 2 historically-profitable · 2 research-worthy · best exp 0.0305R · median exp -0.1037R.

## Validation
- **Historical metrics:** expectancy 0.0289R, PF 1.085, maxDD 11.65R over n=320 (research 60%).
- **OOS metrics:** expectancy 0.0179R (validation 20%).
- **Drawdown:** 11.65R (research).
- **Profit Factor:** 1.085.
- **Expectancy:** 0.0289R/trade.
- **Monte Carlo summary:** Wave-1 EXP-02: the efficiency gate did NOT select better-than-random continuation trades at the family-wise bar (NO DIFFERENCE DETECTED).
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 2 historically-profitable, 2 research-worthy. Representative 13752e544049: n=320, exp=0.0289R, PF=1.085, maxDD=11.65R, OOS exp=0.0179R, pos-months 14/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
