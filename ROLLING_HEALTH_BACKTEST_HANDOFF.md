# Rolling Health-Gated Backtest — Full Handoff (Phase 6.9 Preparation)

**Date:** 2026-07-16. **Purpose:** this document, together with `NEXT_SESSION.md` and
`CHANGELOG.md`, is designed to let a BRAND-NEW chat reconstruct this entire project — architecture,
history, current results, and the exact specification for the next phase — using ONLY these three
files. No conversation memory should be required for anything. Every fact below was verified live
against the repository at the time of writing (`git log`/`git status`/`git diff`/a live
`pytest`+`mypy --strict`+`coverage` run) — nothing here is assumed or carried forward unverified.

---

## 1. Current repository state

```
Repository path:  C:\Users\MEDION GAMING\ai_quant_lab-research-main
Branch:           ai-trader-implementation
Working tree:     clean (verified live at this handoff's own close)
```

Re-verify `git branch --show-current`, `git log -1`, `git status --porcelain` directly before
trusting any git-state claim — this repository's own standing discipline, followed by every prior
handoff.

## 2. Completed phases and checkpoints

| Phase / Checkpoint | Status | Report |
|---|---|---|
| Phase 6.1–6.6 (six live pipeline modules) | READY | (pre-dates this handoff's own scope) |
| Phase 6.7 (Simulation Framework) | READY | (pre-dates this handoff's own scope) |
| Phase 6.8 Checkpoint 1 (S1 reference slice) | READY | — |
| Phase 6.8 Checkpoint 2 (batches B1+B2, 15 strategies) | READY | `PHASE_6_8_CHECKPOINT_2_REPORT.md` |
| Phase 6.8 Wave B (batches B3–B10, all 43 strategies) | **COMPLETE** | `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md` |
| Wave D (first full-portfolio simulation) | **COMPLETE** | `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md` |
| Wave D Audit (per-strategy tiering, correlation, 3 static variants) | **COMPLETE** | `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` |
| Strategy Health System (build + first static evaluation) | **COMPLETE** | `STRATEGY_HEALTH_SYSTEM_REPORT.md` |
| Phase 6.9 (Rolling Health-Gated Backtest) | **NOT STARTED** | this document, §8 |

## 3. Current architecture

```
Claude Code ←→ MCP Server (stdio) ←→ CDP (localhost:9222) ←→ TradingView Desktop (Electron)
```
*(that architecture line refers to an UNRELATED tool available in this environment — TradingView MCP
— and has no bearing on this project; included only because it sometimes appears in tool
descriptions surfaced in this workspace. The AI Trader's own architecture is below.)*

```
Research Lab (code/, results/, knowledge/) — FROZEN, discovers/validates strategies offline
        │  (Strategy Interface v1 contracts, knowledge/strategies/*/strategy.json)
        ▼
Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine
   (six FROZEN pipeline modules — byte-identical since Checkpoint 2, except one disclosed
    CEO-approved additive touch to Market Scanner, §6)
        │
        ▼
Simulation Framework (ai_trader/simulation/ — NOT frozen, extensible)
   SimulationHarness → ExecutionSimulator → PortfolioSimulator → PerformanceAnalyzer
   + time_stop.py / trailing_stop.py (generic exit overlays, opt-in per strategy)
        │
        ▼
Strategy Runtime (ai_trader/strategy_runtime/ — NOT frozen)
   43 real evaluators (families/*.py) + registry.py + context_access.py (incl. the
   historical-features window) + migration.py
        │
        ▼
Strategy Health System (ai_trader/strategy_health/ — NOT frozen, NEW this cycle)
   Independent of everything above — reads closed-trade history only, produces Health
   Scores + ACTIVE/WATCHLIST/PROBATION/DISABLED classifications. NOT YET WIRED into the
   Simulation Framework's own strategy-selection logic (that wiring is Phase 6.9, §8).
```

## 4. All READY modules

- **Market Scanner** (`ai_trader/market_scanner/`) — FROZEN except the historical-features window
  (§6). Produces `MarketContext` per (symbol, as_of), lookahead-safe.
- **Strategy Manager** (`ai_trader/strategy_manager/`) — FROZEN. Loads the Strategy Library, tracks
  contract `Health`/`Lifecycle` (schema-validity/compatibility/maturity — **unrelated to trading
  performance**, do not confuse with the Strategy Health System's own `HealthState`).
- **Signal Engine** (`ai_trader/signal_engine/`) — FROZEN. Runs registered runtime evaluators.
- **Scoring Engine** (`ai_trader/scoring_engine/`) — FROZEN. Scores/ranks signals.
- **Risk Manager** (`ai_trader/risk_manager/`) — FROZEN. Sizing, guards, cooldowns, constraints.
- **Execution Engine** (`ai_trader/execution_engine/`) — FROZEN. Order construction/execution.
- **Simulation Framework** (`ai_trader/simulation/`) — NOT frozen, extensible. `SimulationHarness`
  orchestrates a full backtest; `ExecutionSimulator`/`PortfolioSimulator`/`PerformanceAnalyzer` do
  fills/accounting/reporting; `time_stop.py`/`trailing_stop.py` are generic exit overlays.
- **Strategy Runtime** (`ai_trader/strategy_runtime/`) — NOT frozen. `families/` holds all 43 real
  evaluators; `registry.py` builds runtime handles (with `only_ids`/`strategy_id_filter` support);
  `context_access.py` includes `feature_n_ago`/`flag_n_ago` for historical feature access;
  `migration.py` converts v0→v1 contracts.
- **Strategy Health System** (`ai_trader/strategy_health/`) — NOT frozen, NEW. See §5.

## 5. Strategy Health System — status and full methodology

**Status: READY, tested, committed. Used so far ONLY as a one-time static classifier** (evaluated
once, from a single `as_of` snapshot, against the Wave D trade history). It has NOT been wired into
a time-evolving backtest where the active strategy roster changes as simulated time advances — that
wiring is Phase 6.9's own entire purpose (§8).

### 5.1 Why it was introduced

Wave D and its own audit judged every strategy from its FULL 3.6-year lifetime average. The CEO's own
stated concern: a lifetime average hides regime change. A strategy strong in 2023 may be irrelevant to
2026's market; a strategy weak across its full lifetime may have quietly become excellent under the
CURRENT regime, buried under years of unrelated history. Multi-year averages cannot see this — rolling
windows, re-evaluated regularly, can.

### 5.2 Data model (`ai_trader/strategy_health/types.py`)

- `ClosedTrade` — a minimal, SOURCE-INDEPENDENT trade record (`strategy_id`, `exit_as_of`, `net_pnl`,
  `pnl_r`, `holding_bars`). Deliberately NOT tied to `ai_trader.simulation.portfolio_simulator.
  TradeRecord` — `from_trade_record()` adapts one, but the scoring code never imports the Simulation
  Framework, so it can score a live broker fill log tomorrow with zero changes.
- `HealthState` enum — `ACTIVE` / `WATCHLIST` / `PROBATION` / `DISABLED`. **Independent of, and not
  to be confused with,** `ai_trader.strategy_manager.types.Health`/`Lifecycle` (schema-validity and
  maturity-ladder concepts, unrelated to trading performance).
- `WindowMetrics` — every metric computed per rolling window (3m/6m/12m, fixed day-counts 90/180/365,
  NOT calendar months, for determinism regardless of which day of the month `as_of` falls on):
  `n_trades`, `win_rate`, `profit_factor`, `expectancy_currency`, `expectancy_r` (avg R/trade),
  `net_r`, `net_pnl`, `max_drawdown` (isolated proxy, see caveat below), `monthly_consistency`
  (fraction of active months net-positive), `equity_stability` (mean/stdev of monthly PnL),
  `max_losing_streak`, `avg_holding_bars`. Any metric that cannot be computed is `None` — never
  fabricated.
- `WindowScore` — the 0–100 composite for one window, plus `confidence` (credibility weight),
  `metric_weights` (the PCA-derived weight vector), `metric_percentiles` (this strategy's own raw
  ranks) — the score shows its own work, not just a bare number.
- `StrategyHealthReport` — the full per-strategy output: all 3 windows' metrics/scores, the blended
  `overall_score`, `trend_delta`, final `state`, and a plain-language `rationale` string.

### 5.3 Metric computation (`metrics.py`)

`trades_in_window()` filters by the trade's own `exit_as_of` (a trade's CLOSE is what counts as
"this window's own evidence" — an entry from before the window that's still open, or exits after
`as_of`, tells us nothing about performance realized inside the window). All the metrics above are
computed per window from that filtered set; pure functions, no state, no side effects.

**Disclosed limitation**: `max_drawdown` is an ISOLATED proxy — one strategy's own trades chained
into their own cumulative-PnL curve, peak-to-trough. Real strategies share ONE capital account and
ONE symbol slot in this system, so this cannot be summed into a true portfolio-attributed drawdown.
(Same limitation already disclosed in `WAVE_D_PORTFOLIO_AUDIT_REPORT.md` §1.)

### 5.4 Composite scoring — why it is "not hardcoded" (`scoring.py`)

Three layers, in order:

1. **Percentile-rank normalization** (`percentile_rank()`): every metric becomes a 0–100 rank within
   the cross-section of strategies with ≥1 trade in that window. Scale-free, outlier-robust — needed
   because this system's real trade history produces extreme R-multiples (a +21.6R single-trade
   result was found in the Wave D audit's own S1 variant analysis) that would badly distort a
   z-score approach. `None` values are handled per-metric: `profit_factor=None` means "zero losing
   trades this window" (unambiguously excellent → ranks 100); every other `None` means "not
   computable" (neutral → ranks 50).
2. **Bühlmann credibility shrinkage** (`credibility_weight()`, `CREDIBILITY_K = 10.0`): a standard
   actuarial technique. A strategy's percentile is pulled toward the neutral midpoint (50) by
   `k / (n + k)` — at `n=10` trades, a strategy's own evidence and the neutral prior are weighted
   equally. Stops one lucky/unlucky trade from swinging a small-sample strategy to an extreme score.
3. **PCA-derived metric weights** (`_pca_weights()`) — **the actual answer to "do not hardcode
   weights"**: the 8 scored metrics (`expectancy_r`, `profit_factor`, `net_r`, `win_rate`,
   `monthly_consistency`, `equity_stability`, `max_drawdown` [inverted — lower is better],
   `max_losing_streak` [inverted]), each already shrunk per-strategy, are assembled into a
   strategies × metrics matrix. Its covariance matrix's DOMINANT EIGENVECTOR (first principal
   component — the linear combination of metrics that explains the most cross-strategy variance,
   i.e. the axis the metrics themselves agree is "better") becomes the weight vector, clipped to
   non-negative and renormalized to sum to 1. This is a deterministic function of the CURRENT
   population's own data — no person chooses it. Falls back to equal weights only when fewer than
   `MIN_POPULATION_FOR_PCA = 5` strategies have data in a window (disclosed, not hidden).

**Two things are intentionally NOT data-derived — labeled as editorial choices, not disguised as
objective:**

- **`WINDOW_PRIORITY` = `{12m: 0.60, 6m: 0.25, 3m: 0.15}`** combining the 3 window scores into one
  overall Health Score (`combine_windows()`). This is the CEO's own explicit business rule
  ("12-month is the primary decision window; shorter windows are supporting evidence") — stated as a
  rule, not disguised as a discovered pattern. A window with no trades has its weight redistributed
  proportionally among the windows that do have data.
- **Classification bands** (`classifier.py`): `score ≥ 65 → ACTIVE`, `45 ≤ score < 65 → WATCHLIST`,
  `25 ≤ score < 45 → PROBATION`, `score < 25 → DISABLED`. Fixed thresholds on the 0–100 scale where
  50 is, by construction, near the population's own median. A defensible first-version choice, not
  learned; revisiting them is a reasonable FUTURE refinement, not attempted yet (the CEO's own
  standing "do not optimize" instruction applied to this build).

### 5.5 Regime-adaptation trend rule (`classifier.py`, `TREND_STRONG = 15.0`)

`trend_delta = 3-month score − 12-month score`. If ≥ +15, the strategy is bumped UP one
classification tier (capped at `ACTIVE`) — strong recent improvement overrides an adequate-but-stale
12-month baseline. If ≤ −15, bumped DOWN one tier (floored at `DISABLED`) — a strategy whose
12-month number still looks fine but whose latest quarter has collapsed is exactly the case
multi-year (or even 12-month) averages can still conceal.

### 5.6 Top-level entry point (`evaluator.py`)

```python
def evaluate_strategy_health(
    trades_by_strategy: Mapping[str, Sequence[ClosedTrade]], as_of: int,
) -> dict[str, StrategyHealthReport]
```

Evaluates every strategy id present (including ids with an empty trade list — they still get a
report, classified `WATCHLIST` for lack of evidence, never penalized for an absence of data).
Designed for REPEATED calls with an advancing `as_of` — recomputes everything from scratch every
call, nothing cached or carried over between calls. **This is the exact function Phase 6.9 must call
repeatedly, at each rolling re-evaluation checkpoint, with progressively more trade history** — no
new scoring logic needs to be built, only the orchestration that calls it on a schedule and gates the
simulation's own active strategy set accordingly.

### 5.7 Verification (at the time this system was built)

```
mypy --strict ai_trader/strategy_health/ --exclude 'tests/'
Success: no issues found in 6 source files

pytest ai_trader/strategy_health/ -q
47 passed

coverage (ai_trader.strategy_health only)
TOTAL   243 stmts   5 miss   98%

pytest ai_trader/ -q   (full suite, confirmed zero regressions)
1562 passed
```

## 6. Current Wave D results (static, no health-gating)

**Baseline** (`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`): all 43 strategies active simultaneously
throughout, $2,000 initial capital, 5% risk/trade, 2022-12-16→2026-07-13 (~3.6 years, 84,151 M15
bars). 513 trades, +$313.21 net profit (+15.66%), Sharpe 1.196, max drawdown 6.16%, profit factor
1.264, win rate 39.77%, expectancy +0.179R. Zero execution costs modeled (spread/commission/slippage
all $0.00 — a known limitation, not a claim of zero real-world cost). Two real Simulation Framework
bugs were found and fixed getting to this result (both fully disclosed in that report's §0; both
confined to `ai_trader/simulation/`, zero impact on the Research Lab or the six frozen pipeline
modules):
1. `portfolio_simulator.py`'s `bars_since_close` was hardcoded to 0, permanently locking the
   cooldown-after-loss guard after a symbol's first-ever loss (first attempt: 1 trade in 3.6 years).
2. `time_stop.py` fired one bar too late relative to its own declared time-stop horizon, due to the
   execution simulator's standard one-bar submit-to-fill lag.

**Audit** (`WAVE_D_PORTFOLIO_AUDIT_REPORT.md`): full per-strategy tiering from that same 513-trade
result — VERY_GOOD (6: S2, S13, S24, S28, S40, S44), GOOD (2: S39, S46), NEUTRAL (28), NEGATIVE (4:
S1, S5, S22, S30), ELIMINATE (3: S14, S26, S42). Three static portfolio variants (Conservative =
VERY_GOOD only [6 strategies], Balanced = VERY_GOOD+GOOD [8], Aggressive = all-minus-ELIMINATE [40])
were simulated and compared to the baseline. **The single most important finding**: the Aggressive
variant's apparently-best Sharpe/return was driven almost entirely by ONE strategy (S1) capturing a
handful of extreme-outlier trades via a path-dependent shift in slot-timing once 3 losing strategies
were removed — not genuine broad-based edge. **This proves the single-shared-symbol-slot
architecture makes results highly sensitive to strategy-set composition in a NON-ADDITIVE way** —
removing/adding a strategy does not simply add/remove its own historical trades from the total;
it can completely change which OTHER trades get taken, because only one position may be open at a
time system-wide. **This finding is directly relevant to Phase 6.9**: a rolling health-gate that
changes the active roster monthly will trigger this same path-dependence repeatedly, and the
resulting equity curve must not be over-interpreted as "the gate found the best strategies" without
accounting for this structural sensitivity (see §8's own validation requirements).

**Strategy Health System first evaluation** (`STRATEGY_HEALTH_SYSTEM_REPORT.md`): the same 513-trade
history, re-sliced into rolling 3/6/12-month windows as of 2026-07-13 (a single static snapshot, not
yet rolling through time): **2 ACTIVE (S40, S46), 34 WATCHLIST, 7 PROBATION (S1, S5, S13, S14, S22,
S28, S30), 0 DISABLED.** Notable: S42 and S26 (both lifetime `ELIMINATE`) show genuine recent
improvement — S42's own 3-month score exceeds its 12-month baseline by +17.0 points, triggering the
trend-bump rule directly, landing it on `WATCHLIST` despite a lifetime-worst tier. S13 (lifetime
`VERY_GOOD`) shows a sharp, otherwise-hidden 3-month decline (trend −22.7, bumped from `WATCHLIST` down
to `PROBATION`). S46's own 12-month net R (+21.6) exceeds its full 3.6-year lifetime net R (+14.9) —
its pre-2025 history was a net drag on an otherwise-strong current edge.

## 7. Known limitations and remaining risks

- **Execution costs are zero in every result reported so far** (Wave D, the audit, the Health
  System's own input data). Every return/Sharpe/profit-factor number in this project overstates
  real-world profitability by an unknown amount. Not yet addressed.
- **Portfolio-level `max_drawdown_R`** remains unresolved (`PerformanceAnalyzer` cannot compute it
  from the recorded inputs without fabricating data — disclosed since Checkpoint 2).
- **No per-strategy conformance test** exists against the frozen Research Lab's own historical trade
  log, for any of the 43 strategies — a long-standing, still-open gap.
- **The single-shared-symbol-slot architecture's own path-dependence** (§6) is demonstrated but not
  yet characterized or mitigated. A rolling health-gate (Phase 6.9) will interact with this same
  path-dependence; results must be interpreted with this firmly in mind.
- **The Strategy Health System's own classification bands and window-priority weights are fixed,
  disclosed CHOICES, not validated against alternatives.** They have not been "tuned" (per the CEO's
  own standing instruction), but neither have they been stress-tested against different bands/weights
  to see how sensitive the classifications are to these specific numbers.
- **Small sample sizes dominate.** In the Wave D audit, 25 of 43 strategies had fewer than 5 lifetime
  trades. In the Strategy Health System's own first run, 16 of 43 strategies have ZERO trades in
  every rolling window (no evidence in the last 12 months at all). Any rolling-gated backtest will
  inherit this same sparsity — most strategies will spend most of the backtest on `WATCHLIST` for lack
  of recent evidence, not necessarily because they are bad.
- **The Strategy Health System has never been run more than once.** It has not yet been proven stable
  under repeated re-evaluation with growing history, nor has its own anti-lookahead property been
  tested end-to-end (only asserted by construction — `trades_in_window()` filters by `exit_as_of <=
  as_of`, which is correct by inspection, but has no dedicated regression test proving a later
  checkpoint's own trade set never retroactively changes an earlier checkpoint's own computed score).

## 8. Phase 6.9 — Rolling Health-Gated Backtest — full specification

**Status: proposed specification, NOT YET APPROVED, NOT YET STARTED.** The name and general intent
("Rolling Health-Gated Backtest") were set by CEO directive; the mechanics below are this handoff's
own proposed design, derived from the natural next step implied by the Strategy Health System's own
stated purpose (§5.1) and the tools already built and tested (§5.6). **A future session must get
explicit CEO sign-off on this specification (or a revised one) before implementing any of it.**

### 8.1 Exact objective

Prove whether a TIME-EVOLVING strategy roster — periodically re-evaluated by the Strategy Health
System using ONLY data available up to that point in simulated time, restricted to `ACTIVE`-classified
strategies between re-evaluations — produces a more robust historical result than EITHER extreme
already tested: the static all-43 baseline (Wave D) or the static lifetime-tier-based portfolios
(the Wave D audit's Conservative/Balanced/Aggressive variants). "More robust" means better risk-
adjusted metrics (Sharpe, max drawdown, Calmar) AND — critically, given §6's own path-dependence
finding — a result that is NOT simply an artifact of which strategies happened to occupy the shared
slot at path-dependent moments.

### 8.2 Methodology constraints

- **Re-evaluation cadence**: monthly, aligned to the existing rolling-window definitions (90/180/365
  fixed days for 3m/6m/12m — NOT calendar months, for determinism).
- **Bootstrap period**: the Strategy Health System needs real trade history before it can gate
  anything. Proposed: run the FIRST 12 months (2022-12-16 → 2023-12-16) UNGATED — all 43 strategies
  active, identical to the Wave D baseline's own early period — purely to accumulate initial trade
  history. Monthly health-gating begins only from month 13 onward, using only trades closed strictly
  before each checkpoint.
- **Roster determination**: at each monthly checkpoint `T`, call `evaluate_strategy_health()` with the
  full trade ledger accumulated so far (never a future-truncated or artificially-limited slice
  BEYOND what "up to T" naturally means) and `as_of = T`. The `ACTIVE`-classified strategies become
  the `strategy_id_filter` for the simulation period `[T, T + 1 month)`. `WATCHLIST`/`PROBATION`/
  `DISABLED` strategies do not trade during that period, per the CEO's own original design
  requirement ("Only ACTIVE strategies are allowed to trade").
- **Same everything else as Wave D**: $2,000 starting capital, 5% risk/trade, XAUUSD only, same date
  range, same `run_seed=1`, same `enable_time_stops`/`enable_trailing_stops=True`. The ONLY variable
  Phase 6.9 introduces is the health-gating mechanism itself — every other input stays identical to
  the already-verified Wave D baseline, so any difference in outcome is attributable to gating, not
  to a confound.

### 8.3 Anti-lookahead rules (must be enforced AND proven, not just asserted)

1. No strategy's Health Score at checkpoint `T` may be computed from any trade whose `exit_as_of ≥
   T`. (`metrics.trades_in_window()` already enforces `exit_as_of <= as_of` — this must be re-verified
   in the specific rolling-gate context, not merely assumed from the existing unit tests, which use
   synthetic data, not this backtest's own real trade sequence.)
2. No strategy's Health Score at checkpoint `T` may be influenced by ANY information about periods
   after `T` — this includes not just trade data but also, implicitly, the ORDER in which the
   rolling-gate orchestrator processes strategies or months (must be deterministic and forward-only).
3. **A dedicated automated test is required, not optional**: prove that a checkpoint `T`'s own
   computed Health Score is IDENTICAL whether computed from (a) the trade ledger truncated to trades
   with `exit_as_of ≤ T`, or (b) the FULL final trade ledger (including trades far in the future of
   `T`) passed to the same function — i.e., adding future trades to the input must never change a
   past checkpoint's own already-computed score. This is the single most important correctness
   property of the entire phase and must be verified programmatically, per the CEO's own "anti-
   lookahead rules" requirement.
4. Simulation determinism must be preserved exactly: identical `(SimulationContext, seed)` (and now
   also identical accumulated trade history at each checkpoint) must produce a byte-identical result,
   re-verified the same way every previous phase's own determinism was proven
   (`asdict(report_a) == asdict(report_b)`).

### 8.4 Frozen assumptions (must NOT change in Phase 6.9)

- No strategy evaluator, contract, or parameter changes.
- No Research Lab (`code/`, `results/`) changes.
- No changes to any of the six frozen pipeline modules' production code (Market Scanner may receive
  further additive, disclosed, CEO-approved touches only if a genuine new gap is found and approved —
  same standing rule as every prior phase; none is anticipated for Phase 6.9).
- The Strategy Health System's own scoring methodology (§5.4–5.6) is CONSUMED as-is. Phase 6.9 does
  not redesign, retune, or re-weight it — if the methodology needs to change, that is a separate,
  explicitly-scoped decision, not a side effect of building the rolling-gate orchestrator.
- Same $2,000 capital / 5% risk / XAUUSD-only / date-range conventions as Wave D (§8.2).

### 8.5 Stop conditions (pause and ask the CEO before continuing)

- The health-gating mechanism reduces the ACTIVE roster to ZERO strategies for an extended period —
  a structural failure mode to flag and discuss, not silently work around (e.g. by loosening bands).
- Any anti-lookahead violation is found (§8.3's own test fails) — this is a correctness bug requiring
  a fix and re-verification before any results can be trusted, not a design choice to route around.
- Determinism fails to reproduce (same seed/history → different result).
- The frozen Simulation Framework's own code needs a MORE-than-additive change to support monthly
  re-gating (e.g. if running the harness in monthly segments with state carried forward between them
  turns out to be insufficient and a deeper `harness.py` change seems necessary) — propose the change,
  disclose the reasoning, and get sign-off before implementing, exactly as the trailing-stop and
  historical-features-window mechanisms were handled in Wave B.
- Any result that looks implausibly good or bad (mirroring the discipline that caught both Wave D
  bugs) — investigate before reporting, never report a number that hasn't been sanity-checked.

### 8.6 Suggested implementation order (not mandatory, but a reasonable starting point)

1. Build the anti-lookahead regression test (§8.3.3) FIRST, against the existing, already-committed
   `evaluate_strategy_health()` — this can be done immediately, requires no new simulation code, and
   establishes the correctness bar everything else must meet.
2. Build a `rolling_health_gate` component (new file, likely `ai_trader/strategy_health/` or a new
   sibling package) — a pure function: given accumulated trade history and a checkpoint `T`, return
   the `ACTIVE` strategy id set at `T` (thin wrapper around `evaluate_strategy_health()`).
3. Build the monthly-segmented orchestration: run `SimulationHarness` repeatedly over successive
   one-month sub-ranges, each with its own `strategy_id_filter` computed by step 2, carrying portfolio
   state (balance, open positions, equity curve, trade ledger) forward between segments. Prefer this
   over modifying `harness.py` itself to accept a per-bar re-gating callback — lower risk, reuses the
   existing, already-tested harness unchanged.
4. Run the full rolling-gated backtest over the complete Wave D historical range.
5. Compare against the Wave D baseline AND the Wave D audit's 3 static variants (same metrics: trades,
   return%, Sharpe, max drawdown, profit factor, expectancy — the same table shape used in both prior
   reports, for direct comparability).
6. Write the results report, following the same rigor and disclosure standard as
   `WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`/`WAVE_D_PORTFOLIO_AUDIT_REPORT.md` — especially disclosing
   how the §6-documented path-dependence may be influencing whatever result appears.

### 8.7 Validation requirements

- The anti-lookahead test (§8.3.3) passes.
- Determinism re-verified for the rolling-gated run specifically (not just inherited from Wave D's own
  proof, since the mechanism is new).
- Full existing regression suite stays green (`pytest ai_trader/ -q`, `mypy --strict`, coverage not
  regressing from wherever this handoff's own close leaves it — see `CHANGELOG.md`'s own top entry
  for that exact number).
- A results report comparable in rigor and honesty to the two Wave D reports, including an explicit
  discussion of whether the rolling-gate's own performance can be distinguished from path-dependent
  luck (§6) — not just a headline number.

### 8.8 Final acceptance criteria

- Rolling health-gated backtest runs deterministically end-to-end over the full historical range.
- Anti-lookahead is PROVEN via an automated test, not just asserted by code inspection.
- Full regression suite green, `mypy --strict` clean, coverage maintained or improved.
- A comparison report exists showing the rolling-gated approach's own Sharpe/return/drawdown/
  expectancy/stability against BOTH the static all-43 baseline and the 3 static tier-based variants,
  with an honest discussion of the path-dependence caveat.
- Explicit CEO review and sign-off before any further phase (multi-symbol expansion, live/paper
  gating, Learning Engine, Broker Adapter, or anything else) begins.

---

*This document supersedes no prior report — `PHASE_6_8_WAVE_B_COMPLETION_REPORT.md`,
`WAVE_D_PORTFOLIO_SIMULATION_REPORT.md`, `WAVE_D_PORTFOLIO_AUDIT_REPORT.md`, and
`STRATEGY_HEALTH_SYSTEM_REPORT.md` remain the authoritative, detailed sources for their own respective
scopes. This handoff exists to make the CURRENT state and the NEXT phase's own specification reachable
without needing to read every prior report in full, and without needing any conversation history at
all.*
