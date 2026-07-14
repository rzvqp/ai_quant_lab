# Performance Analyzer v1 — metrics, attribution & reporting (design)

The Performance Analyzer consumes the simulation's trade history, equity curve, execution log, and risk events,
and produces the **`SimulationReport`** — the full performance picture that proves (or disproves) profitability.
It is read-only analytics: it measures, it never decides or trades. Design only — no code. The report shape is in
`SIMULATION_SCHEMA.json`.

---

## 1. Purpose & boundaries
- Turn the Portfolio Simulator's outputs into a complete, deterministic performance report.
- Compute portfolio-level and per-strategy metrics, roll-ups (session/daily/monthly), attribution, allocation, and
  risk-event summaries.
- **No decisions, no learning, no optimization** — it produces the numbers a human (and a future Learning Engine)
  will read; it never feeds back into the pipeline mid-run.

## 2. Inputs
Trade history + closed/floating PnL + equity curve (Portfolio Simulator); execution log (Execution Simulator);
risk events (Risk Manager decisions + Portfolio Simulator margin events); the `SimulationContext` (for the run
descriptor). All already produced by the pipeline — the Analyzer reads, it does not re-run anything.

## 3. Portfolio performance metrics
| metric | definition |
|---|---|
| **Net profit** | final `closed_pnl` (+ floating if held) in currency and % of starting balance |
| **Return** | total return; CAGR over the replay period |
| **Expectancy** | mean PnL per trade (R and currency) |
| **Profit Factor** | gross profit / gross loss |
| **Win rate** | winning trades / total |
| **Payoff ratio** | avg win / avg loss |
| **Sharpe / Sortino** | risk-adjusted return on the equity-curve returns (periodic; annualized) — deterministic |
| **Max Drawdown** | max peak-to-trough equity drop (currency, %, and in R); drawdown duration |
| **Recovery factor** | net profit / max drawdown |
| **Exposure** | avg % of time in market; avg gross/net exposure |
| **Trade count / frequency** | total trades; trades per day/week/month |
| **Avg holding time**, **MFE/MAE** | from the trade history |

Metrics are computed over the RUNNING phase only (WARMUP excluded) and are deterministic functions of the inputs.

## 4. Strategy attribution
Per active strategy (and per correlation group):
- trades, win rate, expectancy (R + currency), profit factor, net PnL, max drawdown contribution, exposure share,
  and **contribution to total portfolio PnL** (with and without netting for correlated strategies).
- Identifies which strategies carried the portfolio and which detracted — the key input for future allocation
  decisions (made downstream, not here). Attribution ties every trade to its `strategy_id` (and `decision_id`).

## 5. Capital allocation report
- How equity/risk was distributed across strategies/groups over time (from open positions + realized PnL): average
  and time-series allocation, allocation vs contribution (efficiency), and concentration (max share in one
  strategy/group). Measures the `capital_allocation` policy's effect; does not change it.

## 6. Risk-event summary
- Aggregates the run's risk events: Risk Manager DENYs by reason; SUSPENDED/EMERGENCY_STOP episodes; margin
  calls/liquidations; cooldown activations; filter blocks. Counts, durations, and the PnL context around each —
  so the review can see how risk controls shaped the outcome.

## 7. Statistics roll-ups
| roll-up | contents |
|---|---|
| **Session statistics** | per session (asia/london/ny/late): trades, PnL, win rate, exposure |
| **Daily statistics** | per day: PnL, return, trades, max intraday drawdown, end-of-day equity |
| **Monthly statistics** | per month: PnL, return, trades, drawdown; the monthly-return table (for stability review) |
Roll-ups are incremental (updated at each session/day/month boundary during the run) and deterministic.

## 8. `SimulationReport` (output)
A single, self-describing report object (`SIMULATION_SCHEMA.json`) containing:
`meta` (run_id, versions, date range, symbols, strategy set) · `portfolio_summary` (final balance/equity, net
profit, return, max drawdown, PF, expectancy, Sharpe/Sortino) · `performance` (the full metric set) ·
`attribution` (per-strategy/group) · `allocation` · `risk_events` · `stats` (session/daily/monthly) · references
to the persisted `trade_history` / `execution_log` / `equity_curve`.

The report is the deliverable a human reviews to judge robustness, and the exact artifact a future Learning Engine
would consume — never produced with any hidden randomness (determinism law).

## 9. Determinism & scale
- Every metric is a deterministic function of the recorded inputs; identical runs ⇒ identical reports.
- For **batch runs** (thousands of simulations), the Analyzer emits one `SimulationReport` per run plus an
  optional **batch summary** (cross-run distributions: return, drawdown, PF across seeds/dates/strategy-sets) —
  the basis for robustness evaluation (e.g. out-of-sample stability, parameter/date sensitivity). The batch
  summary is descriptive statistics over the per-run reports; it performs no optimization or selection.
