# S8 — Extension Mean-Reversion

> **Class:** Extension mean-reversion  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Price extends k*ATR beyond a reference (SMA or session VWAP); the onset of over-extension reverts toward the reference. Loser = late trend-chasers.

## Rules
- **Entry:** At the ONSET of |close-ref| > k*ATR (first bar of the extension); enter next open toward the reference.
- **Exit:** rr2 | opp_liq (revert to the reference) | time.
- **Stop-loss:** atr (1.5*ATR) or ext (2 ticks past the bar extreme).
- **Required confirmations:** none (extension onset is selective)
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** ref(sma|vwap), k(2.0|3.0), side, stop, exit

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
- **Hypothesis id:** `0e2979c0d58e`
- **Parameters:** `{"ref": "vwap", "k": 3.0, "side": "up", "stop": "atr", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0171 |
| Profit Factor | 1.026 |
| Max Drawdown (R) | 24.62 |
| Win rate | 0.407 |
| Trades (n) | 302 |
| Positive months | 16/27 |
| Top-1 trade share | 0.01 |
| **OOS expectancy (R/trade)** | 0.1094 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 48 hypotheses · 4 historically-profitable · 2 research-worthy · best exp 0.0291R · median exp -0.2355R.

## Validation
- **Historical metrics:** expectancy 0.0171R, PF 1.026, maxDD 24.62R over n=302 (research 60%).
- **OOS metrics:** expectancy 0.1094R (validation 20%).
- **Drawdown:** 24.62R (research).
- **Profit Factor:** 1.026.
- **Expectancy:** 0.0171R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 48 hypotheses, 4 historically-profitable, 2 research-worthy. Representative 0e2979c0d58e: n=302, exp=0.0171R, PF=1.026, maxDD=24.62R, OOS exp=0.1094R, pos-months 16/27, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
