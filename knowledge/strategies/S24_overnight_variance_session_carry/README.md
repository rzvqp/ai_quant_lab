# S24 — Overnight Variance / Session Carry

> **Class:** Class IV — session structure  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
The prior session's close position in its range conditions the next session; carry (same bias) or fade at the target session's early bar.

## Rules
- **Entry:** At bar `entry_bar` of London/NY, bias from where the prior session closed in its range; carry or fade; enter next open.
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** london | ny (target)
- **Long/Short applicability:** both
- **Higher-timeframe context:** prior-session structure
- **Grammar (degrees of freedom):** sess(london|ny), mode(carry|fade), entry_bar(1|2), exit

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
- **Selection rule:** hist_profitable & largest-n
- **Hypothesis id:** `560615553726`
- **Parameters:** `{"sess": "ny", "mode": "fade", "entry_bar": 1, "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0815 |
| Profit Factor | 1.107 |
| Max Drawdown (R) | 33.37 |
| Win rate | 0.303 |
| Trades (n) | 551 |
| Positive months | 15/27 |
| Top-1 trade share | 0.041 |
| **OOS expectancy (R/trade)** | -0.0746 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 24 hypotheses · 2 historically-profitable · 0 research-worthy · best exp 0.0815R · median exp -0.084R.

## Validation
- **Historical metrics:** expectancy 0.0815R, PF 1.107, maxDD 33.37R over n=551 (research 60%).
- **OOS metrics:** expectancy -0.0746R (validation 20%).
- **Drawdown:** 33.37R (research).
- **Profit Factor:** 1.107.
- **Expectancy:** 0.0815R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 24 hypotheses, 2 historically-profitable, 0 research-worthy. Representative 560615553726: n=551, exp=0.0815R, PF=1.107, maxDD=33.37R, OOS exp=-0.0746R, pos-months 15/27, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
