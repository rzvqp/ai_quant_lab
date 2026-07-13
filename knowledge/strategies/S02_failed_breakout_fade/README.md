# S2 — Failed-Breakout Fade

> **Class:** Failed-breakout / contrarian  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A close breaks beyond a reference level then FAILS (closes back inside) within a few bars — a false breakout. Fade back into the range. Loser = breakout buyers of the false break.

## Rules
- **Entry:** Close beyond ref (up: close>refH; low: close<refL); within `fail_within` bars a close returns inside; enter next open (contrarian, into the range).
- **Exit:** rr2 | opp_liq | time.
- **Stop-loss:** beyond_ext (2 ticks past the failed-break extreme) or atr (1.5*ATR).
- **Required confirmations:** The failure itself (close back inside within the window) is the confirmation.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** ref(swing|session|pdh_pdl), lb(20|50), fail_within(2|4), stop, exit, side

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
- **Hypothesis id:** `959581cbcdb3`
- **Parameters:** `{"ref": "pdh_pdl", "lb": 20, "fail_within": 4, "stop": "atr", "exit": "rr2", "side": "low"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | 0.0188 |
| Profit Factor | 1.03 |
| Max Drawdown (R) | 22.48 |
| Win rate | 0.412 |
| Trades (n) | 272 |
| Positive months | 13/26 |
| Top-1 trade share | 0.011 |
| **OOS expectancy (R/trade)** | -0.0311 |
| Historically profitable | True |
| Research-worthy | True |
| Fragile | False |

**Family distribution:** 144 hypotheses · 18 historically-profitable · 6 research-worthy · best exp 0.0746R · median exp -0.0949R.

## Validation
- **Historical metrics:** expectancy 0.0188R, PF 1.03, maxDD 22.48R over n=272 (research 60%).
- **OOS metrics:** expectancy -0.0311R (validation 20%).
- **Drawdown:** 22.48R (research).
- **Profit Factor:** 1.03.
- **Expectancy:** 0.0188R/trade.
- **Monte Carlo summary:** Wave-1 EXP-06 level placebo: real above shuffled but NOT significant (NO DIFFERENCE DETECTED).
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** VERY LOW — research-worthy in-sample but non-positive out-of-sample
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 144 hypotheses, 18 historically-profitable, 6 research-worthy. Representative 959581cbcdb3: n=272, exp=0.0188R, PF=1.03, maxDD=22.48R, OOS exp=-0.0311R, pos-months 13/26, research-worthy. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat`), metrics from `results/FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
