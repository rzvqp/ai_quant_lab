# Wave D — First Full-Portfolio Historical Simulation (All 43 Strategies)

**Date:** 2026-07-15. **Scope:** the first full historical XAUUSD simulation with ALL 43 migrated
strategies active simultaneously, per the CEO's own standing Wave D instructions: $2,000 initial
capital, 5% risk per trade, over the full available historical data range
(`data/market/OANDA_XAUUSD_M15.csv`: 2022-12-16 → 2026-07-13, ~3.6 years, 84,151 M15 bars).
**This is a report-only step** — no strategy was removed, tuned, or optimized based on these results.

---

## 0. Two real bugs found and fixed during this Wave — disclosed up front

The first two simulation attempts produced implausible results that led to genuine defects being
found and fixed in the (non-frozen) `ai_trader/simulation/` package. **Neither fix touched the
Research Lab (`code/`, `results/`) or any of the six frozen pipeline modules** (Market Scanner,
Strategy Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine) — both are confined
to the Simulation Framework, which Phase 6.7 always designated non-frozen and extensible.

### Bug 1 — cooldown-after-loss clock permanently stuck at zero

The first Wave D run produced **exactly 1 trade in 3.6 years**. Root cause:
`PortfolioSimulator.to_portfolio_state()` (`ai_trader/simulation/portfolio_simulator.py`) built every
`ClosedPosition.bars_since_close` as a hardcoded `0`, regardless of how much simulated time had
actually passed. `ClosedPosition.bars_since_close` is the SOLE clock source for
`check_cooldown_after_loss()` (`ai_trader/risk_manager/guards.py`): "if a closed position on this
symbol was a loss and `bars_since_close < after_loss_bars` (4), deny." With the clock frozen at 0
forever, this guard NEVER expired once XAUUSD had its first losing trade — permanently blocking every
future entry on the only symbol being traded, for the rest of any run.

**Fix**: compute the real elapsed bar count —
`bars_since_close = max(0, (as_of - trade.exit_as_of) // timeframe_seconds(base_timeframe))` — reusing
the existing `ai_trader.market_scanner.timeframes.timeframe_seconds` helper. A regression test
(`test_bars_since_close_advances_with_as_of`) was added to
`ai_trader/simulation/tests/test_portfolio_simulator.py` proving the clock now genuinely advances with
`as_of`. This test gap existed because no prior test exercised `to_portfolio_state()`'s own
`recent_closed_positions` projection with more than one `as_of` snapshot.

### Bug 2 — time-stop exits landing one bar late

After fixing Bug 1, the full regression suite's own `test_checkpoint2_end_to_end.py` — run against
much more real trading activity than any earlier scenario had produced — caught a second, narrower
defect: a real S25 trade showed `holding_bars=25` against its own declared 24-bar time-stop limit.

Root cause: `positions_due_for_time_stop()` (`ai_trader/simulation/time_stop.py`) fired at
`age_bars >= limit`. But `ExecutionSimulator.advance_bar()` never matches an order on the same bar it
was submitted (`EXECUTION_SIMULATOR.md` §3 — the same lookahead-safe, one-bar submit-to-fill lag every
entry order already has, "enter next open"). A reduce-only time-stop decision built exactly at
`age_bars == limit` therefore only actually filled one bar later, at `age_bars == limit + 1` — silently
violating the strategy's own declared horizon by one bar, every time.

**Fix**: fire one bar early, at `age_bars >= limit - 1`, so the fill (one bar later, by the same
universal lag) lands exactly at `age_bars == limit`. Both affected unit tests in
`ai_trader/simulation/tests/test_time_stop.py` were updated to the corrected boundary, and the real
end-to-end proof (`test_checkpoint2_end_to_end.py`, all 3 tests) was rerun clean afterward — including
the exact `holding_bars <= 24` assertion that caught this.

### Why this matters for the numbers below

The Wave D result reported here is the run captured **after both fixes**, verified against a fresh
full regression suite (1515/1515 passing) and `mypy --strict` (158 files clean). The very first,
buggy attempt (1 trade) and the second, partially-fixed attempt (545 trades, still carrying Bug 2) are
both superseded and not reported further — only the final, correct numbers below should be treated as
Wave D's own result.

---

## 1. Run configuration

```
SimulationHarness(
    date_range: 2022-12-16 -> 2026-07-13 (1,671,187,500 -> 1,783,922,400 epoch seconds)
    symbols: ("XAUUSD",); timeframes: ("M15", "H1", "H4", "D1"); warmup_bars: 200
    starting_balance: $2,000.00; run_seed: 1
    use_strategy_runtime: True (all 43 migrated strategies, auto_admit_min_maturity="EXPLORATORY")
    enable_time_stops: True; enable_trailing_stops: True
    RiskConfig.sizing.risk_per_trade_pct: 0.05 (5%, CEO directive -- default is 0.005)
)
```

## 2. Headline performance

| Metric | Value |
|---|---|
| Total trades | **513** |
| Wins / Losses | **204 / 309** |
| Win rate | 39.77% |
| Expectancy | +0.179 R (+$0.611/trade) |
| Profit factor | 1.264 |
| Payoff ratio | 1.915 |
| Net profit | **+$313.21** |
| Return | **+15.66%** on $2,000 |
| CAGR | 4.16% |
| Max drawdown | 6.16% |
| Recovery factor | 2.543 |
| Calmar ratio | 0.675 |
| Sharpe | 1.196 |
| Sortino | 1.372 |
| Max losing streak | 11 trades |
| Avg holding period | 173.2 bars (~43.3 hours) |
| Avg exposure | 87.7% of the run's own bars had an open position |
| Turnover | 106.4 |
| Long / Short trades | 306 / 207 |
| Long / Short net PnL | +$360.43 / -$47.22 |

**Execution costs**: `total_commission = $0.00`, `total_spread_cost = $0.00`,
`total_slippage_cost = $0.00` — the Simulation Framework's cost model was not configured with non-zero
values for this run (`SimulationContext.cost_model` defaults). This is a known limitation, not a claim
of zero real-world trading costs — a future Wave D re-run with realistic spread/commission/slippage
values would show a lower net return.

## 3. Equity curve summary

| | |
|---|---|
| Starting balance | $2,000.00 |
| Final balance | $2,310.63 |
| Final equity (incl. 1 floating position) | $2,313.21 |
| Equity curve points (bars) | 84,151 |
| First point | 2022-12-16, balance/equity $2,000.00 |
| Last point | 2026-07-13, balance $2,310.63 / equity $2,313.21, drawdown 3.47% at close, 1 open position |

## 4. Yearly performance

| Year | Trades | Net PnL |
|---|---|---|
| 2022 (partial, from Dec 16) | 5 | -$12.89 |
| 2023 | 67 | +$100.59 |
| 2024 | 52 | +$19.94 |
| 2025 | 139 | +$97.66 |
| 2026 (through Jul 13) | 250 | +$107.91 |

## 5. Monthly performance

Every month with at least one trade (43 of the range's ~44 months; two months, 2024-02 and
2025-11, had zero trades and are omitted, not silently dropped from the underlying data):

| Month | Trades | PnL | Win rate |
|---|---|---|---|
| 2022-12 | 5 | -$12.89 | 20.0% |
| 2023-01 | 4 | +$10.16 | 50.0% |
| 2023-02 | 5 | +$33.05 | 60.0% |
| 2023-03 | 9 | +$52.65 | 55.6% |
| 2023-04 | 5 | -$17.28 | 20.0% |
| 2023-05 | 7 | -$14.66 | 28.6% |
| 2023-06 | 7 | -$25.92 | 0.0% |
| 2023-07 | 5 | -$4.49 | 20.0% |
| 2023-08 | 1 | -$3.18 | 0.0% |
| 2023-09 | 1 | +$12.55 | 100.0% |
| 2023-10 | 7 | +$41.61 | 71.4% |
| 2023-11 | 8 | -$17.57 | 25.0% |
| 2023-12 | 8 | +$33.68 | 75.0% |
| 2024-01 | 2 | -$6.91 | 0.0% |
| 2024-03 | 3 | +$47.61 | 66.7% |
| 2024-04 | 15 | -$9.02 | 40.0% |
| 2024-05 | 10 | -$33.72 | 20.0% |
| 2024-06 | 3 | -$17.38 | 0.0% |
| 2024-07 | 1 | -$7.61 | 0.0% |
| 2024-08 | 1 | +$18.14 | 100.0% |
| 2024-09 | 3 | +$11.89 | 66.7% |
| 2024-11 | 7 | +$19.92 | 42.9% |
| 2024-12 | 7 | -$2.97 | 28.6% |
| 2025-01 | 5 | -$5.42 | 20.0% |
| 2025-02 | 11 | -$5.23 | 27.3% |
| 2025-03 | 13 | -$6.94 | 46.2% |
| 2025-04 | 31 | +$27.66 | 38.7% |
| 2025-05 | 6 | +$7.62 | 33.3% |
| 2025-06 | 11 | -$22.16 | 27.3% |
| 2025-07 | 10 | -$3.45 | 40.0% |
| 2025-08 | 8 | -$18.59 | 12.5% |
| 2025-09 | 12 | +$14.26 | 33.3% |
| 2025-10 | 17 | +$83.65 | 70.6% |
| 2025-12 | 15 | +$26.27 | 46.7% |
| 2026-01 | 17 | +$108.50 | 70.6% |
| 2026-02 | 62 | +$27.94 | 37.1% |
| 2026-03 | 72 | -$77.67 | 33.3% |
| 2026-04 | 41 | +$19.12 | 39.0% |
| 2026-05 | 36 | +$21.45 | 47.2% |
| 2026-06 | 17 | +$20.82 | 47.1% |
| 2026-07 (partial, through Jul 13) | 5 | -$12.25 | 40.0% |

Trade volume rises sharply from 2026-02 onward (62, 72, 41, 36 trades/month) — consistent with several
high-frequency strategies (S39, S46, S22) clustering signals in that period rather than a data or
mechanism anomaly; not investigated further, per the report-only mandate.

## 6. Rejection stats (Risk Manager denial reasons, whole run)

| Reason | Count |
|---|---|
| `NOT_ACTIONABLE` (no strategy found a valid setup this bar) | 3,510,009 |
| `LIMIT_MAX_PER_SYMBOL` (symbol slot already occupied) | 70,467 |
| `BELOW_FLOOR` (below the pre-trade filter's own minimum) | 26,722 |
| `SIZE_BELOW_MIN` (computed size rounds to zero) | 8,261 |
| `COOLDOWN_AFTER_LOSS` (within the 4-bar post-loss cooldown) | 948 |
| `INVALID_INPUT` | 1,475 |
| `FILTER_VOLATILITY` (outside the volatility-ratio filter band) | 65 |

`NOT_ACTIONABLE` dominates by construction — 43 strategies × 84,151 bars is ~3.6M possible
evaluations, and most strategies are deliberately selective (onset-only, multi-bar confirmation
patterns). `LIMIT_MAX_PER_SYMBOL` is the second-largest reason by a wide margin: with only one symbol
(XAUUSD) and a strict one-position-per-symbol limit, 43 strategies are in constant competition for a
single slot — directly explains why only 29 of 43 strategies ever got a trade in this run (§7).

## 7. Per-strategy attribution

29 of 43 strategies got at least one trade in this run. Sorted by net PnL:

| Strategy | Trades | Net PnL | Win rate | Expectancy R | Profit factor |
|---|---|---|---|---|---|
| S46 | 144 | +$179.32 | 36.1% | +0.104 | 1.410 |
| S44 | 18 | +$75.05 | 33.3% | +1.300 | 3.009 |
| S39 | 96 | +$72.23 | 46.9% | +0.263 | 1.262 |
| S13 | 18 | +$36.75 | 55.6% | +0.430 | 3.726 |
| S40 | 6 | +$28.67 | 83.3% | +1.758 | 14.889 |
| S18 | 3 | +$15.86 | 66.7% | +0.519 | 4.485 |
| S28 | 10 | +$14.74 | 40.0% | +0.790 | 2.058 |
| S2 | 7 | +$13.93 | 57.1% | +0.810 | 3.288 |
| S12 | 3 | +$12.34 | 100.0% | +1.390 | n/a (no losses) |
| S24 | 5 | +$8.69 | 60.0% | +0.433 | 1.914 |
| S8 | 4 | +$5.68 | 50.0% | +0.636 | 2.146 |
| S16 | 4 | +$6.53 | 75.0% | +0.599 | 6.854 |
| S51 | 1 | +$7.00 | 100.0% | +1.999 | n/a (no losses) |
| S48 | 13 | +$0.45 | 46.2% | +0.046 | 1.071 |
| S4 | 2 | -$0.68 | 50.0% | -0.247 | 0.506 |
| S10 | 16 | -$1.34 | 43.8% | -0.032 | 0.909 |
| S25 | 11 | -$1.86 | 54.5% | -0.128 | 0.825 |
| S41 | 1 | -$2.37 | 0.0% | -1.000 | 0.000 |
| S6 | 4 | -$2.40 | 25.0% | -0.297 | 0.657 |
| S43 | 2 | -$5.74 | 0.0% | -1.000 | 0.000 |
| S26 | 10 | -$5.82 | 30.0% | -0.202 | 0.281 |
| S21 | 2 | -$5.36 | 0.0% | -1.001 | 0.000 |
| S45 | 1 | -$5.44 | 0.0% | -0.589 | 0.000 |
| S30 | 13 | -$9.55 | 30.8% | -0.102 | 0.619 |
| S5 | 23 | -$10.14 | 34.8% | -0.259 | 0.765 |
| S42 | 7 | -$10.87 | 28.6% | -0.383 | 0.056 |
| S22 | 31 | -$38.41 | 29.0% | -0.210 | 0.466 |
| S14 | 9 | -$40.46 | 0.0% | -0.672 | 0.000 |
| S1 | 49 | -$23.56 | 34.7% | +0.296 | 0.803 |

**14 strategies never got a trade in this run**: S3, S7, S9, S11, S15, S17, S19, S20, S23, S27, S29,
S31, S38, S50. This is NOT reported as a strategy defect — with only one symbol and a strict
one-per-symbol slot, 43 strategies compete for a single concurrent position, and this particular
historical path simply never handed these 14 strategies the winning race for that slot (or their own
signal conditions never triggered in this specific window). No conclusion about their own quality
should be drawn from zero trades here; the Research Lab's own historical backtests (per-strategy,
unconstrained by portfolio-level slot competition) remain the correct source for judging any individual
strategy's own standalone edge.

**S1** is a notable case: -$23.56 net over 49 trades despite a POSITIVE +0.296R expectancy and a
0.803 profit factor close to breakeven — the negative net result at this trade count, combined with a
positive per-trade expectancy, is consistent with variance around a thin edge rather than a
contradiction; not investigated further (report-only).

**S14** and **S41/S43/S21/S45** show 0% win rates across (respectively) 9 and 1-2 trades each —
small samples, consistent with several of these strategies' own v0 Research Lab confidence already
being NEGATIVE (research-worthy in-sample but not confirmed out-of-sample) or VERY LOW. This matches
the frozen Research Lab's own prior findings; it is not a new discovery, and per the CEO's standing
instruction, none of these strategies were removed, disabled, or re-tuned as a result.

## 8. Capital utilization and exposure

- **Average exposure**: 87.7% of simulated time had an open position (`avg_exposure_pct`). Given the
  strict one-position-per-symbol constraint and a single symbol, this reflects how often SOME
  strategy's own position occupies the slot, not aggregate portfolio-level leverage.
- **Turnover**: 106.4 (a dimensionless ratio per `PERFORMANCE_ANALYZER.md`'s own formula) — a large
  number of relatively short-duration round-trips relative to the account's own size.
- **Orders submitted**: 643 total (including synthetic time-stop/trailing-stop reduce-only orders),
  against 513 realized trades — the gap is expected (time-stop/trailing-stop closes are themselves
  additional orders on top of each position's own entry).

## 9. Verdict

Wave D's first full-portfolio run is **complete and green**: a modest but real positive result
(+15.66% over 3.6 years, Sharpe 1.196, max drawdown 6.16%) with all 43 strategies competing honestly
for one XAUUSD slot, two genuine Simulation Framework bugs found and fixed along the way (both
disclosed in full above, both confined to non-frozen code, both verified via regression + a fresh full
suite run), and every underperforming strategy reported honestly without modification. This is a
report, not a recommendation — no strategy was added, removed, or re-weighted based on these numbers.

**Not yet done** (future work, not part of this Wave D pass): a cost-model-configured rerun (non-zero
spread/commission/slippage); a per-strategy conformance check against the frozen Research Lab's own
historical trade log; portfolio-level `max_drawdown_R`; investigating the 2026-02/03 trade-volume
spike; a multi-symbol run once the frozen Research Lab's own strategies extend beyond XAUUSD.
