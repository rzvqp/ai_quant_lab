# S22 — Round-Number Magnet / Rejection

> **Class:** Class I — psychological levels  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Psychological $ levels ($50/$100 on gold) attract limit orders and stops; price rejects or cleanly breaks them. Loser = orders resting at the round number.

## Rules
- **Entry:** reject: wick tags the round level and closes back (fade); breakout: the floor(price/step) band changes (crossed a round level); onset only; enter next open.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr or level (2 ticks past the round level).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** step(50|100), mode(reject|breakout), stop, exit

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
- **Hypothesis id:** `46c7c98c262b`
- **Parameters:** `{"step": 100, "mode": "breakout", "stop": "atr", "exit": "rr3"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0819 |
| Profit Factor | 1.117 |
| Max Drawdown (R) | 22.47 |
| Win rate | 0.336 |
| Trades (n) | 223 |
| Positive months | 15/25 |
| Top-1 trade share | 0.017 |
| **OOS expectancy (R/trade)** | 0.1465 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 24 hypotheses · 6 historically-profitable · 1 research-worthy · best exp 0.1207R · median exp -0.1R.

## Validation
- **Historical metrics:** expectancy 0.0819R, PF 1.117, maxDD 22.47R over n=223 (research 60%).
- **OOS metrics:** expectancy 0.1465R (validation 20%).
- **Drawdown:** 22.47R (research).
- **Profit Factor:** 1.117.
- **Expectancy:** 0.0819R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 6 historically-profitable, 1 research-worthy. Representative 46c7c98c262b: n=223, exp=0.0819R, PF=1.117, maxDD=22.47R, OOS exp=0.1465R, pos-months 15/25, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
