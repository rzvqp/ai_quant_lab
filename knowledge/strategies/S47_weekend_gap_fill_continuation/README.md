# S47 — Weekend-Gap Fill / Continuation

> **Class:** Batch2 — weekend gap  ·  **Status:** INVALID  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** INVALID

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
The Friday-close -> Monday-open weekend liquidity gap either fills or continues. Distinct from S19 (intraday gaps). TECHNICALLY INVALID for research: sample too small (n<25).

## Rules
- **Entry:** At Monday open, a gap > thr*ATR; fill = toward the prior close, continue = with the gap; enter next open.
- **Exit:** rr2 | rr3 | opp_struct (prior close for fills) | time.
- **Stop-loss:** atr (1.5*ATR).
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** Monday open only
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** mode(fill|continue), thr(0.3|0.6), exit

### Invalid conditions
- ATR non-finite or <= 0 at the signal bar
- signal on the last available bar (no next-open to fill)
- a position is already open (overlap suppression)
- INVALID — sample size n<25 (weekend Mondays only); not a valid research result.

### Position sizing assumptions
- **model:** risk-normalised (1R per trade)
- **risk_definition:** risk = |entry - executable_stop|; result R = (dir*(exit-entry) - 2*cost)/risk
- **stop_floor:** executable risk = max(2*spread_ticks*tick, 5*tick, 0.10*ATR) = max(0.20, 0.50, 0.10*ATR) price units (v2, pre-registered)
- **costs:** (spread 1 + slippage 1) ticks/side * 0.1 = 0.10/side; 0.20 round-trip charged in R
- **concurrency:** ONE position at a time (overlapping signals suppressed until the open trade closes)
- **absolute_size:** lot = per-trade risk budget / risk-distance — an EXECUTION-LAYER decision, NOT set by the research

## Executable default (representative hypothesis)
- **Selection rule:** largest-n (no positive hypothesis)
- **Hypothesis id:** `80c42f36d50e`
- **Parameters:** `{"mode": "fill", "thr": 0.3, "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.0727 |
| Profit Factor | 0.707 |
| Max Drawdown (R) | 1.93 |
| Win rate | 0.7 |
| Trades (n) | 10 |
| Positive months | 3/5 |
| Top-1 trade share | 0.463 |
| **OOS expectancy (R/trade)** | -0.369 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0727R · median exp -0.3058R.

## Validation
- **Historical metrics:** expectancy -0.0727R, PF 0.707, maxDD 1.93R over n=10 (research 60%).
- **OOS metrics:** expectancy -0.369R (validation 20%).
- **Drawdown:** 1.93R (research).
- **Profit Factor:** 0.707.
- **Expectancy:** -0.0727R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** INVALID
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. THIS FAMILY IS INVALID: INVALID — sample size n<25 (weekend Mondays only); not a valid research result.

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
