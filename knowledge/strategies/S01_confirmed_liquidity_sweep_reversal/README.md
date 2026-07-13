# S1 — Confirmed Liquidity Sweep Reversal

> **Class:** Liquidity / stop-hunt reversal  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
Price sweeps a resting liquidity level (prior swing / session / prev-day high-low), trapping breakout traders and triggering stops, then closes back inside the range. The reversal is the absorption of that forced flow. Loser = breakout entrants and stopped-out positions.

## Rules
- **Entry:** A sweep bar takes out the reference level (high>refH & close<refH for a high-sweep; low<refL & close>refL for a low-sweep), THEN a confirmation occurs within `window` bars; enter next open after confirmation.
- **Exit:** Grammar: rr2 / rr3 (2R or 3R fixed target) | opp_liq (opposite liquidity level) | time (24-bar timeout).
- **Stop-loss:** beyond_sweep (2 ticks past the sweep extreme) or structural (2 ticks past the 20-bar extreme at entry).
- **Required confirmations:** REQUIRED: consecutive2 (two same-direction closes) | close_beyond (close back through the level) | displacement (displacement bar with matching close). Optional imbalance filter (FVG present).
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** side, liq_ref(swing|session|pdh_pdl), liq_lb(20|50), confirm, imb(none|fvg), stop, exit, window(4|8)

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
- **Hypothesis id:** `f34e8d2827c3`
- **Parameters:** `{"side": "low", "liq_ref": "pdh_pdl", "liq_lb": 50, "confirm": "consecutive2", "imb": "none", "stop": "beyond_sweep", "exit": "rr2", "window": 8}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.032 |
| Profit Factor | 1.054 |
| Max Drawdown (R) | 20.74 |
| Win rate | 0.461 |
| Trades (n) | 399 |
| Positive months | 20/26 |
| Top-1 trade share | 0.008 |
| **OOS expectancy (R/trade)** | -0.0614 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 1152 hypotheses · 261 historically-profitable · 90 research-worthy · best exp 0.3911R · median exp -0.0885R.

## Validation
- **Historical metrics:** expectancy 0.032R, PF 1.054, maxDD 20.74R over n=399 (research 60%).
- **OOS metrics:** expectancy -0.0614R (validation 20%).
- **Drawdown:** 20.74R (research).
- **Profit Factor:** 1.054.
- **Expectancy:** 0.032R/trade.
- **Monte Carlo summary:** Matched-null pilot (research, engine-validation only). Wave-1 EXP-03 beta/regime-matched null p=0.0069 (Holm-adj 0.042) — DIAGNOSTIC-grade, and OOS expectancy is NEGATIVE. Wave-1 EXP-01 (confirmation contribution) and EXP-05 (level placebo) = NO DIFFERENCE DETECTED. NO confirmed alpha.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 1152 hypotheses, 261 historically-profitable, 90 research-worthy. Representative f34e8d2827c3: n=399, exp=0.032R, PF=1.054, maxDD=20.74R, OOS exp=-0.0614R, pos-months 20/26, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
