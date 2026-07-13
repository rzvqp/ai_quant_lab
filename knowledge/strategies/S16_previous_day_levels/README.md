# S16 — Previous-Day Levels

> **Class:** Reference-level (daily)  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — historically profitable but not research-worthy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Prior-day high/low/open/close/mid act as magnets/decision points — breakout or rejection. Loser = the crowd anchored to the daily level.

## Rules
- **Entry:** Onset of a close beyond the chosen prev-day level (breakout) or a wick-tag-then-reject (reject); enter next open.
- **Exit:** rr2 | time.
- **Stop-loss:** atr or level (2 ticks past the level).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** D1 levels
- **Grammar (degrees of freedom):** level(pdh|pdl|pd_open|pd_close|pd_mid), mode(breakout|reject), stop, exit

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
- **Hypothesis id:** `8b586b06d4c0`
- **Parameters:** `{"level": "pd_close", "mode": "breakout", "stop": "atr", "exit": "time"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0316 |
| Profit Factor | 1.042 |
| Max Drawdown (R) | 90.31 |
| Win rate | 0.321 |
| Trades (n) | 1146 |
| Positive months | 14/26 |
| Top-1 trade share | 0.013 |
| **OOS expectancy (R/trade)** | 0.1368 |
| Historically profitable | True |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 40 hypotheses · 1 historically-profitable · 0 research-worthy · best exp 0.0316R · median exp -0.2503R.

## Validation
- **Historical metrics:** expectancy 0.0316R, PF 1.042, maxDD 90.31R over n=1146 (research 60%).
- **OOS metrics:** expectancy 0.1368R (validation 20%).
- **Drawdown:** 90.31R (research).
- **Profit Factor:** 1.042.
- **Expectancy:** 0.0316R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — historically profitable but not research-worthy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 40 hypotheses, 1 historically-profitable, 0 research-worthy. Representative 8b586b06d4c0: n=1146, exp=0.0316R, PF=1.042, maxDD=90.31R, OOS exp=0.1368R, pos-months 14/26, hist-profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
