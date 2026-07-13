# S29 — Day-of-Week Effect

> **Class:** Class IV — calendar  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A fixed weekday directional bias, entered at that day's first bar. Pure calendar effect; in-sample-favourable, multiple-testing across weekdays acknowledged (calendar families are overfit-prone).

## Rules
- **Entry:** At the first bar of the chosen weekday, enter next open directionally; hold.
- **Exit:** rr2 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Weekday first bar
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** dow(0..4), side, exit

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
- **Hypothesis id:** `13e900a2bf7b`
- **Parameters:** `{"dow": 3, "side": "up", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.2047 |
| Profit Factor | 1.332 |
| Max Drawdown (R) | 17.7 |
| Win rate | 0.482 |
| Trades (n) | 112 |
| Positive months | 16/27 |
| Top-1 trade share | 0.021 |
| **OOS expectancy (R/trade)** | -0.0259 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 20 hypotheses · 6 historically-profitable · 4 research-worthy · best exp 0.4188R · median exp -0.164R.

## Validation
- **Historical metrics:** expectancy 0.2047R, PF 1.332, maxDD 17.7R over n=112 (research 60%).
- **OOS metrics:** expectancy -0.0259R (validation 20%).
- **Drawdown:** 17.7R (research).
- **Profit Factor:** 1.332.
- **Expectancy:** 0.2047R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 20 hypotheses, 6 historically-profitable, 4 research-worthy. Representative 13e900a2bf7b: n=112, exp=0.2047R, PF=1.332, maxDD=17.7R, OOS exp=-0.0259R, pos-months 16/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
