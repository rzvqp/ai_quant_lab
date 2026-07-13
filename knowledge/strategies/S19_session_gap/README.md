# S19 — Session Gap

> **Class:** Gap fill / continuation  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy (flagged FRAGILE — dominated by few periods)

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A session-open gap (open vs prior-session close) either fills (revert to prior close) or continues. Small sample. Loser depends on mode.

## Rules
- **Entry:** At session start a gap > 0.5*ATR (up or down); fill = trade toward the prior close, continue = with the gap; enter next open.
- **Exit:** rr2 | opp_liq (prior close for fills) | time.
- **Stop-loss:** atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Session opens
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** gap_dir(up|down), mode(fill|continue), exit

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
- **Hypothesis id:** `316c9abb653d`
- **Parameters:** `{"gap_dir": "down", "mode": "fill", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0596 |
| Profit Factor | 1.076 |
| Max Drawdown (R) | 10.17 |
| Win rate | 0.263 |
| Trades (n) | 19 |
| Positive months | 3/7 |
| Top-1 trade share | 0.361 |
| **OOS expectancy (R/trade)** | 0.6205 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | True |

**Family distribution:** 12 hypotheses · 4 historically-profitable · 0 research-worthy · best exp 0.9155R · median exp -0.2034R.

## Validation
- **Historical metrics:** expectancy 0.0596R, PF 1.076, maxDD 10.17R over n=19 (research 60%).
- **OOS metrics:** expectancy 0.6205R (validation 20%).
- **Drawdown:** 10.17R (research).
- **Profit Factor:** 1.076.
- **Expectancy:** 0.0596R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy (flagged FRAGILE — dominated by few periods)
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 4 historically-profitable, 0 research-worthy. Representative 316c9abb653d: n=19, exp=0.0596R, PF=1.076, maxDD=10.17R, OOS exp=0.6205R, pos-months 3/7, hist-profitable, FRAGILE. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
