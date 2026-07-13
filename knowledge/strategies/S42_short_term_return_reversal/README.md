# S42 — Short-Term Return Reversal

> **Class:** Batch1 — short-term reversal (overreaction)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
The largest recent L-bar mover reverses (liquidity providers absorb overreaction) — the classic short-term-reversal anomaly. Distinct from S8 (distance-from-SMA).

## Rules
- **Entry:** Onset of L-bar return > thr (overbought -> short) or < -thr (oversold -> long); enter next open (fade).
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** L(3|6), thr(0.006|0.012), exit

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
- **Hypothesis id:** `481371b95170`
- **Parameters:** `{"L": 6, "thr": 0.012, "stop": "atr", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0833 |
| Profit Factor | 1.139 |
| Max Drawdown (R) | 5.23 |
| Win rate | 0.419 |
| Trades (n) | 43 |
| Positive months | 8/18 |
| Top-1 trade share | 0.067 |
| **OOS expectancy (R/trade)** | 0.0574 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 12 hypotheses · 6 historically-profitable · 3 research-worthy · best exp 0.1483R · median exp -0.0152R.

## Validation
- **Historical metrics:** expectancy 0.0833R, PF 1.139, maxDD 5.23R over n=43 (research 60%).
- **OOS metrics:** expectancy 0.0574R (validation 20%).
- **Drawdown:** 5.23R (research).
- **Profit Factor:** 1.139.
- **Expectancy:** 0.0833R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 6 historically-profitable, 3 research-worthy. Representative 481371b95170: n=43, exp=0.0833R, PF=1.139, maxDD=5.23R, OOS exp=0.0574R, pos-months 8/18, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
