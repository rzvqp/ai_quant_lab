# S31 — Month-End / Month-Start Effect

> **Class:** Class IV — calendar  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Fixed windows around the month change (day-of-month >=27 or <=2), entered at the day's first bar. Calendar effect; small sample; in-sample-only overfit risk.

## Rules
- **Entry:** In the month-end/start window, at the day's first bar, enter next open directionally.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Month-end/start first bar
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** window(month_end|month_start), side, exit

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
- **Hypothesis id:** `75078bddddd9`
- **Parameters:** `{"window": "month_start", "side": "down", "exit": "rr3"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.1249 |
| Profit Factor | 1.163 |
| Max Drawdown (R) | 9.51 |
| Win rate | 0.316 |
| Trades (n) | 38 |
| Positive months | 12/26 |
| Top-1 trade share | 0.087 |
| **OOS expectancy (R/trade)** | -0.4385 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 12 hypotheses · 2 historically-profitable · 2 research-worthy · best exp 0.1783R · median exp -0.3099R.

## Validation
- **Historical metrics:** expectancy 0.1249R, PF 1.163, maxDD 9.51R over n=38 (research 60%).
- **OOS metrics:** expectancy -0.4385R (validation 20%).
- **Drawdown:** 9.51R (research).
- **Profit Factor:** 1.163.
- **Expectancy:** 0.1249R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 2 historically-profitable, 2 research-worthy. Representative 75078bddddd9: n=38, exp=0.1249R, PF=1.163, maxDD=9.51R, OOS exp=-0.4385R, pos-months 12/26, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
