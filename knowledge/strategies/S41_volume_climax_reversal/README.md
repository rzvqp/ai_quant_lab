# S41 — Volume-Climax Reversal

> **Class:** Batch1 — volume magnitude  ·  **Status:** IMPLEMENTED  ·  **Timeframe:** M15  ·  **Applicability:** both  ·  **Confidence:** NEGATIVE — family unprofitable on the research segment

*Executable strategy specification generated from FROZEN research (no re-backtest, no optimisation, no engine change). This is the Research-Lab → AI-Trader interface; the machine-readable form is `strategy.json`.*

## Mechanism
A participation spike (high volume rank) at a 20-bar price extreme = capitulation/blow-off; forced flow exhausts -> reversal. NEW ingredient: volume MAGNITUDE.

## Rules
- **Entry:** Volume rank >= vthr at a 20-bar high (short) or low (long); onset only; enter next open (reversal).
- **Exit:** rr2 | rr3 | time.
- **Stop-loss:** bar (2 ticks past the climax bar) or atr.
- **Required confirmations:** the volume climax.
- **Timeframe:** M15 execution (signal at bar close, fill at next M15 open; lookahead-safe). XAUUSD/OANDA, NY-17:00 sessions.
- **Sessions:** All sessions
- **Long/Short applicability:** both
- **Higher-timeframe context:** none
- **Grammar (degrees of freedom):** vthr(0.90|0.95), stop, exit

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
- **Hypothesis id:** `73a2a8a65e5e`
- **Parameters:** `{"vthr": 0.9, "stop": "bar", "exit": "rr2"}`

## Performance summary (research segment; frozen)
| metric | value |
|---|---|
| Expectancy (R/trade) | -0.388 |
| Profit Factor | 0.575 |
| Max Drawdown (R) | 535.55 |
| Win rate | 0.319 |
| Trades (n) | 1380 |
| Positive months | 1/27 |
| Top-1 trade share | 0.003 |
| **OOS expectancy (R/trade)** | -0.3384 |
| Historically profitable | False |
| Research-worthy | False |
| Fragile | False |

**Family distribution:** 12 hypotheses · 0 historically-profitable · 0 research-worthy · best exp -0.0387R · median exp -0.082R.

## Validation
- **Historical metrics:** expectancy -0.388R, PF 0.575, maxDD 535.55R over n=1380 (research 60%).
- **OOS metrics:** expectancy -0.3384R (validation 20%).
- **Drawdown:** 535.55R (research).
- **Profit Factor:** 0.575.
- **Expectancy:** -0.388R/trade.
- **Monte Carlo summary:** NOT RUN — matched-null was applied only to the pre-registered pilot and the Wave-1 representatives. The analytic normal-approx p-value is INVALIDATED (PROJECT_AUDIT D1) and is not used as a verdict.
- **Walk-forward status:** NOT RUN (lab-wide; see PROJECT_AUDIT.md).
- **Current confidence:** NEGATIVE — family unprofitable on the research segment
- **Validation status:** EXPLORATORY — historical research segment only. No confirmed alpha. Holdout SEALED; global-FDR NOT run; walk-forward NOT run. Family: 12 hypotheses, 0 historically-profitable, 0 research-worthy. Representative 73a2a8a65e5e: n=1380, exp=-0.388R, PF=0.575, maxDD=535.55R, OOS exp=-0.3384R, pos-months 1/27, not profitable. 

*Provenance: engine mstrat.py v2 (FROZEN) (module `mstrat_ext`), metrics from `results/ext_families/EXT_FAMILY_RESULTS.parquet`. frozen research; NO re-backtest, NO optimisation, NO engine change. Terminal 20% M15 holdout SEALED — never used in any metric here.*
