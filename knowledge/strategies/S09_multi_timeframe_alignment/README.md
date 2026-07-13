# S9 — Multi-Timeframe Alignment

> **Class:** MTF-trend momentum  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
4H trend context (optionally 1H-aligned) plus a fresh M15 breakout trigger — trade only with the higher-timeframe. Loser = counter-trend breakout faders.

## Rules
- **Entry:** 4H trend in the trade direction (and 1H aligned if conf1h=align); ONSET of a close beyond the `lb`-bar rolling extreme; enter next open.
- **Exit:** rr2 | rr3.
- **Stop-loss:** atr (1.5*ATR) or structural (20-bar extreme).
- **Required confirmations:** HTF trend alignment (and optional 1H confirm).
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** H4 trend (+optional H1)
- **Grammar (degrees of freedom):** c4h(up|down), conf1h(align|any), lb(10|20), stop, exit

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
- **Hypothesis id:** `904767451034`
- **Parameters:** `{"c4h": "up", "conf1h": "any", "lb": 10, "stop": "structural", "exit": "rr3"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0624 |
| Profit Factor | 1.117 |
| Max Drawdown (R) | 20.53 |
| Win rate | 0.418 |
| Trades (n) | 687 |
| Positive months | 12/26 |
| Top-1 trade share | 0.007 |
| **OOS expectancy (R/trade)** | 0.1713 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 32 hypotheses · 12 historically-profitable · 6 research-worthy · best exp 0.068R · median exp -0.0767R.

## Validation
- **Historical metrics:** expectancy 0.0624R, PF 1.117, maxDD 20.53R over n=687 (research 60%).
- **OOS metrics:** expectancy 0.1713R (validation 20%).
- **Drawdown:** 20.53R (research).
- **Profit Factor:** 1.117.
- **Expectancy:** 0.0624R/trade.
- **Monte Carlo summary:** Matched-null pilot representative tested (engine-validation pilot; no strategy verdict issued).
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** LOW — exploratory; research-worthy with positive out-of-sample expectancy
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 32 hypotheses, 12 historically-profitable, 6 research-worthy. Representative 904767451034: n=687, exp=0.0624R, PF=1.117, maxDD=20.53R, OOS exp=0.1713R, pos-months 12/26, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
