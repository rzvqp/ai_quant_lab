# S4 — Volatility Compression Expansion

> **Class:** Volatility-regime expansion  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both (bar-directional)  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
After a compression regime (ATR below its mean), a range-expansion bar (>k*ATR) signals a volatility breakout; trade its direction. NOTE: S4 was found NEGATIVE — expansion direction is near-random without a trend filter (the fix is S23).

## Rules
- **Entry:** Prior compression for `min_compress` bars; an expansion bar range>k*ATR; direction = the expansion bar colour; enter next open.
- **Exit:** rr2 | rr3 | trailing | time.
- **Stop-loss:** bar (2 ticks past the expansion bar) or atr.
- **Required confirmations:** none
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both (bar-directional)
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** exp_k(1.5|2.0), stop, exit, min_compress(1|3)

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
- **Selection rule:** largest-n (no positive hypothesis)
- **Hypothesis id:** `9c749c4ba49d`
- **Parameters:** `{"exp_k": 1.5, "stop": "bar", "exit": "trailing", "min_compress": 1}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.3763 |
| Profit Factor | 0.269 |
| Max Drawdown (R) | 1183.6 |
| Win rate | 0.226 |
| Trades (n) | 3141 |
| Positive months | 0/27 |
| Top-1 trade share | 0.037 |
| **OOS expectancy (R/trade)** | -0.2415 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 32 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.1454R · median exp -0.2265R.

## Validation
- **Historical metrics:** expectancy -0.3763R, PF 0.269, maxDD 1183.6R over n=3141 (research 60%).
- **OOS metrics:** expectancy -0.2415R (validation 20%).
- **Drawdown:** 1183.6R (research).
- **Profit Factor:** 0.269.
- **Expectancy:** -0.3763R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 9c749c4ba49d: n=3141, exp=-0.3763R, PF=0.269, maxDD=1183.6R, OOS exp=-0.2415R, pos-months 0/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
