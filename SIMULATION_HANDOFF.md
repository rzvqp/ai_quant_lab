# Simulation Framework — Phase 6.7 Implementation Handoff

**Purpose:** everything the next Claude session needs to begin implementing the Simulation Framework
immediately, with zero context loss. **Documentation only — no implementation code was written to
produce this document; no simulation code exists anywhere in the repo.** Written 2026-07-15 at the close
of the Execution Engine (Phase 6.6) session, HEAD commit `3add548` on `ai-trader-implementation`.

**Before writing any code:** get explicit CEO approval for Phase 6.7 (see `NEXT_SESSION.md` §H/§I —
this is a standing, non-negotiable gate). This document prepares you to start immediately once that
approval is granted; it does not itself constitute approval.

---

## 1. Purpose of the Simulation Framework

Per `README.md` and `SIMULATION_ARCHITECTURE.md` §1: the Simulation Framework is how the AI Trader
**proves it can manage a portfolio of executable strategies profitably — before any broker exists.** It
replays years of historical data through the **exact same pipeline** the live system will run (Market
Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine, all six
already READY and composed **unchanged**), with a virtual broker and virtual account standing in for the
real venue, and produces a full performance report.

"The **only** difference between simulation and live is the component behind the Execution Engine's
Broker Adapter contract" (README.md). Everything upstream of that swap point is byte-identical between
sim and live — this is what makes the simulation a *faithful proof*: if it is profitable and robust in
simulation, the same decisions run live.

## 2. Why simulation precedes Learning Engine, Broker Adapter, and MT5

This is a standing, explicit CEO directive (not merely this framework's own preference): "this framework
is the priority; broker integration is Phase 8+" and "only after this framework is complete and
validated will the Broker Adapter and MetaTrader integration be designed" (README.md). The framework
exists specifically to be the validation gate a strategy portfolio must pass — demonstrated, robust
profitability over historical data — before any live-execution or learning work is justified. Per
`SIMULATION_ARCHITECTURE.md` §11, "the Learning Engine slot is future and NOT implemented; the framework
only produces the reports a future Learning Engine would consume." **Nothing beyond the Simulation
Framework is authorized right now** — no Broker Adapter (a real one), no live execution, no MT5, no
Learning Engine implementation.

## 3. Exact pipeline

```
Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager → Execution Engine
   (all six composed UNCHANGED — same modules, same contracts, same order of operations)
        │
        ▼  OrderRequest, via the Execution Engine's Broker Adapter contract
   Execution Simulator   (= the virtual Broker Adapter — deterministic fills vs. historical bars)
        │  Fill / OrderStatus events
        ▼
   Portfolio Simulator   (= the virtual account — balance/equity/PnL/positions/margin/exposure/drawdown;
                            provides PortfolioState, the same shape a future Portfolio Manager will)
        │
        ▼
   Performance Analyzer  (metrics/attribution/allocation/risk-events/session-daily-monthly stats)
        │
        ▼
   SimulationReport
        │
        ▼
   Learning Engine (future — NOT designed, NOT implemented, NOT in scope)
```

**Important, verified gap regarding the Execution Simulator ↔ `BrokerAdapter` relationship** (this is
the single most important open question for this phase, carried forward from
`EXECUTION_ENGINE_HANDOFF.md`/`NEXT_SESSION.md` §G item 3):

- `ai_trader/execution_engine/broker_adapter.py` already defines a concrete Python `Protocol` named
  `BrokerAdapter` with exactly five methods: `capabilities()`, `submit_order(order)`,
  `cancel_order(client_order_id)`, `query_status(client_order_id)`, `query_open_orders()`. That file's
  own docstring flags itself as an **IMPLEMENTATION CHOICE** — the frozen architecture only described
  the concept in prose, so the Execution Engine's own implementer designed this exact shape.
- `EXECUTION_SIMULATOR.md` asserts conformance to "the exact Broker Adapter contract" and to the
  `broker_adapter_contract_version` **by name**, but never itself enumerates those five method
  signatures — it only describes the resulting event/state stream in prose (order lifecycle emission:
  `SUBMITTED → ACKNOWLEDGED → (PARTIALLY_FILLED)* → FILLED | CANCELLED | REJECTED | EXPIRED`).
- **Conclusion: no doc anywhere states the explicit mapping between `EXECUTION_SIMULATOR.md`'s prose and
  the concrete `BrokerAdapter` Protocol's five methods.** The most natural, spec-consistent reading is
  that the Execution Simulator should literally implement `ai_trader.execution_engine.broker_adapter.BrokerAdapter`
  unmodified (reusing the exact Protocol the Execution Engine's own test suite already exercises via its
  `FakeBrokerAdapter` test double) — but this is an inference, not a documented certainty. **Verify or
  explicitly decide this (and document it as an IMPLEMENTATION CHOICE) before writing the Execution
  Simulator.** If you choose to implement `BrokerAdapter` directly, the Execution Engine's own
  `tests/fixtures/fake_broker.py` is a working reference for what a Protocol-conformant implementation
  looks like structurally (though it is a static, one-shot-fill test double, not a real historical-replay
  simulator).

## 4. Frozen simulation documents to read (in full, before writing any code)

All under `ai_trader/simulation/`, confirmed present this session (10 files, no `.py` files anywhere in
this directory):

| file | what it defines |
|---|---|
| `README.md` | overview, design principles (deterministic/faithful-to-live/no-broker), pipeline diagram, package contents, status |
| `SIMULATION_ARCHITECTURE.md` | purpose, component diagram + table, determinism/parity guarantees (§5), failure modes (§7), startup/shutdown, versioning (§10), boundaries/interaction (§11) |
| `PORTFOLIO_SIMULATOR.md` | the virtual account: balance/equity/margin/exposure/drawdown mechanics, position lifecycle, trade history, live-parity swap (§10) |
| `EXECUTION_SIMULATOR.md` | the virtual Broker Adapter: fill rules per order type (§3), cost model (§4), partial fills (§5), TIF handling (§6), order lifecycle emission (§7), determinism (§8), live-parity swap (§9) |
| `PERFORMANCE_ANALYZER.md` | inputs, portfolio performance metrics (§3), strategy attribution (§4), capital allocation report (§5), risk-event summary (§6), session/daily/monthly roll-ups (§7), `SimulationReport` composition (§8), batch summaries (§9) |
| `SIMULATION_CONTEXT.md` | the immutable `SimulationContext` run spec — every config field, with §C describing the sim/live relationship |
| `SIMULATION_API.md` | the public API surface (definition only) |
| `SIMULATION_SEQUENCE.md` | 10 operational sequences: startup/warmup, per-bar loop, order filling across bars, multi-symbol, margin/insolvency, end-of-run, batch runs, determinism, shutdown/failure, condensed end-to-end |
| `SIMULATION_STATE_MACHINE.md` | (A) the run lifecycle (9 states) and (B) the per-bar cycle sub-states |
| `SIMULATION_SCHEMA.json` | JSON Schema (Draft 2020-12) for `SimulationRun` — `meta`/`context`/`report`/optional `batch_summary` |

Read all 10 in full before writing code, exactly as done for every prior module.

## 5. Existing module APIs and schemas available for integration

All six pipeline modules are READY and composed **unchanged** — do not modify any of them:

- **Market Scanner** (`ai_trader/market_scanner/`) — the Replay Data Source is explicitly named as "the
  Market Scanner's own `replay`/`lab-parity` adapter (Phase 5.1) — not a new data path"
  (`SIMULATION_ARCHITECTURE.md` §3). Reuse the existing `adapters/replay.py`.
- **Strategy Manager** (`ai_trader/strategy_manager/`) — `load_library()`, `active_strategies()`, exactly
  as used live.
- **Signal Engine** (`ai_trader/signal_engine/`) — `evaluate`/`evaluate_strategy`, unchanged.
- **Scoring Engine** (`ai_trader/scoring_engine/`) — `score_batch`/`score_signal`, unchanged.
- **Risk Manager** (`ai_trader/risk_manager/`) — `evaluate(opportunities, risk_context, portfolio)`,
  unchanged. **Consumes `PortfolioState`** (`ai_trader.risk_manager.types.PortfolioState`) — the
  Portfolio Simulator must produce this exact shape every bar (see §6/§16 of the extraction below, and
  `NEXT_SESSION.md` §G item 2's carried-forward Portfolio Manager gap).
- **Execution Engine** (`ai_trader/execution_engine/`) — `execute(decision, portfolio) -> OrderStatus`,
  unchanged; consumes a `BrokerAdapter`-conformant object (§3 above); builds `OrderRequest` per
  `ORDER_SCHEMA.json`.
- **`ai_trader.risk_manager.types.PortfolioState`** — already exists, already reused by Execution Engine
  (documented IMPLEMENTATION CHOICE #1 there). Strongly consider reusing it again here rather than
  designing a third parallel type, unless the Portfolio Simulator's own required fields (margin, HWM,
  session/daily/weekly PnL — see §9 below) don't fit it cleanly; if they don't fit, document that
  decision explicitly as its own IMPLEMENTATION CHOICE rather than silently diverging.
- **`SIMULATION_SCHEMA.json`** — ready for the same `fastjsonschema`-compiled hot-path validation pattern
  every prior module uses (`jsonschema` only for one-time startup shape-sanity checks).

## 6. Required components

Per `SIMULATION_ARCHITECTURE.md` §3's own component table:

| component | role | new/existing |
|---|---|---|
| **Simulation Harness** | the orchestrator: owns the replay clock, drives the per-bar pipeline, collects outputs | new |
| **Replay Clock** | the deterministic historical clock (`as_of` steps over the run's date range) | new |
| **Replay Data Source** | feeds the Market Scanner historical bars in order | existing (Market Scanner's own replay/lab-parity adapter) |
| Pipeline modules | Scanner → Manager → Signal → Scoring → Risk → Execution Engine | existing, composed unchanged |
| **Execution Simulator** | virtual Broker Adapter: deterministic fills vs. bars (spread/commission/slippage/partials) | new |
| **Portfolio Simulator** | virtual account: balance/equity/PnL/positions/margin/exposure/drawdown; provides `PortfolioState` | new |
| **Performance Analyzer** | metrics/attribution/allocation/risk-events/session-daily-monthly stats → report | new |
| **Simulation Ledger & Logs** | trade history, execution log, equity curve, risk-events log | new |
| **Run Config (`SimulationContext`)** | the immutable run spec (dates/symbols/timeframes/capital/costs/seed/strategies) | new |

**Artifact/report writer**: no dedicated component is named. The Performance Analyzer itself "persist[s]
ledger/logs" at shutdown (`SIMULATION_ARCHITECTURE.md` §8). `SIMULATION_SCHEMA.json`'s
`report.artifacts` object holds only *references* to persisted logs (`trade_history_ref`,
`execution_log_ref`, `equity_curve_ref` — nullable strings), not inlined data. **The actual persistence
mechanism/format (file path convention? something else?) is unspecified anywhere in the frozen docs** —
this is a genuine gap requiring an explicit, documented IMPLEMENTATION CHOICE.

## 7. Determinism requirements

This is, if anything, a STRICTER requirement here than for any prior module — a backtest that isn't
perfectly reproducible is close to worthless as a profitability proof. Verbatim/near-verbatim from the
docs:

- **Bit-identical replay**: "identical `(SimulationContext, historical data, module versions)` ⇒
  identical fills, equity curve, trades, and report — every run" (`SIMULATION_ARCHITECTURE.md` §5).
- **No hidden randomness**: the ONLY stochastic model is slippage; it is drawn from a PRNG **seeded
  deterministically** from `run_seed` + a stable key (e.g. `client_order_id` + `as_of`) — reproducible
  and order-independent. No wall-clock, no `Date.now`, no unseeded RNG anywhere.
- **`context.deterministic`** is hard-coded `const: true` in the schema itself — there is no "off"
  switch.
- **Ordered processing**: symbols and orders processed in a fixed, documented order (symbol id, then the
  Scoring Engine's own deterministic rank) — matches the fixed-order precedent every prior module
  followed (Risk Manager's rank order, Execution Engine's decision-order processing).
  **Lookahead-safe**: the same `available_at ≤ as_of` rule as live applies throughout; the Execution
  Simulator fills only on bars at/after the order (never the signal bar).
- **Immutability**: `SimulationContext` is frozen at run start; ANY field change is a NEW run (new
  `run_id`). Two runs with the same context + data + module versions MUST produce identical results.
- **Parallel batch runs never share state** (`SIMULATION_SEQUENCE.md` §8) — each run in a batch is
  independently reproducible from its own `(context, seed)`.

## 8. Replay/live parity requirements

- "Same modules, same contracts, same order of operations; only the Execution Simulator and Portfolio
  Simulator stand in for the venue" (README.md, design principles).
- **`SIMULATION_ARCHITECTURE.md` §5**: "fill conventions (entry at next-open, stop-before-target
  intrabar, cost model) mirror the frozen research execution so simulated results are comparable to the
  Strategy Library's metrics" — **"a conformance check is owed at build; the framework references, never
  copies, the engine."** This is an explicitly acknowledged, NOT-yet-specified obligation: no doc gives a
  test plan or numerical tolerance for what "conformant" means. Budget time to design this conformance
  check yourself, document it, and flag it in the eventual validation report exactly like every prior
  module's own gap-fills.
- **The live-parity "swap" is explicit and load-bearing for both new components**:
  - Portfolio Simulator: "provides the same `PortfolioState` contract the live Portfolio Manager will...
    the state SHAPE and the upstream consumers are unchanged" (`PORTFOLIO_SIMULATOR.md` §10).
  - Execution Simulator: "a real Broker Adapter implement[s] the SAME contract... conformance to the
    research engine's conventions is the v1 baseline; richer microstructure models are future, versioned,
    and optional" (`EXECUTION_SIMULATOR.md` §9).
- **`SimulationContext`'s `mode=SIMULATION` vs `mode=LIVE`** is stated as "the ONLY conceptual
  difference; the runtime-context SHAPE is identical, so the pipeline modules cannot tell simulation from
  live" (`SIMULATION_CONTEXT.md` §C) — design the context object with this in mind from the start.

## 9. Cost model

All of the following is directly from `EXECUTION_SIMULATOR.md` §3–§7 and `PORTFOLIO_SIMULATOR.md` §4:

**Fill rules per order type**: Market fills at next bar open ± spread ± slippage (engine-parity). Limit
fills only if the bar's range touches `limit_price` (buy: low ≤ limit; sell: high ≥ limit), at
`limit_price`, else stays working. Stop triggers when the bar's range crosses `stop_price`, then fills as
a market order at the trigger ± slippage. Stop-Limit becomes a limit at `limit_price` on trigger.
Bracket's protective stop+target become an OCO pair on parent fill. OCO: a fill on one leg cancels the
other deterministically.

**Stop-vs-target same-bar ordering (a fixed, non-negotiable rule)**: "when a single bar could hit both a
stop and a target, the **stop is assumed hit first** (worst-case, engine-parity)... never random."

**Default v1 cost model — the one concrete numeric default in the frozen docs**: spread = 1 tick +
slippage = 1 tick per side (mirrors the research engine, so the simulator reproduces the Strategy
Library's own cost assumptions).

**Spread**: applied on entry and exit per `cost_model.spread_model` (fixed ticks or a per-symbol
schedule); buys fill at ask, sells at bid.

**Commission**: charged per fill per `cost_model.commission_model` (per-lot or per-notional), deducted by
the Portfolio Simulator.

**Slippage models** (three named, `fill_model.slippage_model`): `fixed` (constant tick adjustment),
`atr_fraction` (a fraction of ATR at the fill bar), `seeded_random` (PRNG seeded by
`hash(run_seed, client_order_id, as_of)`, bounded by the order's own `max_slippage` constraint).

**Partial fills**: policy-driven (`fill_model.partial_fill_policy`) — "fill up to the bar's available
liquidity proxy, or full-fill for liquid instruments (default)." **The "liquidity proxy" itself is never
defined anywhere in the frozen docs — a genuine gap requiring a documented IMPLEMENTATION CHOICE.** When
partial, emit `PARTIALLY_FILLED` + a `Fill` for the filled quantity; remainder handled per TIF (IOC/FOK
cancel; GTC/DAY keep working).

**Time-in-force**: IOC (fill what the bar allows, cancel remainder), FOK (fill fully this bar or cancel
entirely), GTC (remain working across bars), DAY (expire at the simulated session/day boundary).
`valid_until` honored deterministically against the replay clock.

**Order lifecycle / rejects**: `SUBMITTED → ACKNOWLEDGED → (PARTIALLY_FILLED)* → FILLED | CANCELLED |
REJECTED | EXPIRED`. Example rejects: a limit never touched within TIF → `EXPIRED`; market closed in the
replay calendar → `REJECTED(MARKET_CLOSED)`. Acks are immediate (no latency) unless a `latency_model` is
configured — **`latency_model` is named but never defined anywhere (no shape, no default, no options
list) — another genuine gap.**

**Margin**: on open, `required_margin = notional × initial_margin_pct`; must be ≤ `free_margin` or the
fill is rejected back deterministically. Each bar: recompute `used_margin`/`margin_level`; if
`margin_level < maintenance_margin_pct` → margin-call/liquidation event (reduce/close positions per a
"deterministic" liquidation policy whose actual ordering rule is UNSPECIFIED — another gap), book
realized PnL, log a risk event. **`initial_margin_pct`/`maintenance_margin_pct`/`leverage_max` have no
numeric defaults anywhere in the docs** — pure config knobs you must default explicitly and document.

**Floating vs. closed PnL** (`PORTFOLIO_SIMULATOR.md` §2/§5):
```
floating_pnl = Σ over open positions of (mark_price − entry) × dir × size × point_value
closed_pnl   = Σ realized PnL of closed positions (cumulative + per period)
balance      = starting_balance + Σ closed PnL − Σ commissions/fees
equity       = balance + floating_pnl
```
Mark price for mark-to-market = the current bar's close (the same bar the pipeline evaluated). Floating
PnL updates every bar; closed PnL books at each closing fill (full or partial), net of that fill's own
commission/spread (already applied by the Execution Simulator); fees/spread/slippage reduce balance at
fill time.

**Other account quantities tracked every bar**: `used_margin`, `free_margin = equity − used_margin`,
`margin_level = equity / used_margin (%)`, `exposure` (gross+net, per-symbol, per-correlation-group),
`leverage = gross notional / equity`, `equity_hwm`, `drawdown` (absolute + % + running `max_drawdown`).

**Position lifecycle**: `OPEN → MODIFY (bracket legs attached; stop moved by partial-exit plan) →
SCALE_OUT/PARTIAL_EXIT (reduce_only fill, realized PnL booked for the closed fraction) → CLOSE`.
Weighted-average entry on scale-in; FIFO/average realized PnL on scale-out (a fixed, documented, versioned
convention). One position per symbol by default (Risk Manager already gates this upstream).

## 10. Required simulation outputs

Per `PERFORMANCE_ANALYZER.md` §3–§9 and `SIMULATION_SCHEMA.json`'s `report` object:

**Portfolio performance metrics**: net profit (currency + % of starting balance), total return + CAGR,
expectancy (R + currency), profit factor, win rate, payoff ratio, Sharpe, Sortino (both deterministic
from the equity-curve periodic returns, annualized), max drawdown (currency, %, and R) + drawdown
duration, recovery factor, exposure (avg % time in market, avg gross/net), trade count/frequency, avg
holding time, MFE/MAE. All computed over the RUNNING phase only — WARMUP is excluded.

**Strategy attribution** (per strategy/correlation group): trades, win rate, expectancy (R + currency),
profit factor, net PnL, max-drawdown contribution, exposure share, contribution to total portfolio PnL
(with and without netting for correlated strategies).

**Capital allocation report**: average + time-series allocation, allocation-vs-contribution efficiency,
concentration (max share in one strategy/group).

**Risk-event summary**: Risk Manager DENYs by reason; SUSPENDED/EMERGENCY_STOP episodes; margin
calls/liquidations; cooldown activations; filter blocks — counts, durations, PnL context around each.

**Session/daily/monthly statistics roll-ups**: per-session (asia/london/ny/late: trades, PnL, win rate,
exposure), per-day (PnL, return, trades, max intraday drawdown, end-of-day equity), per-month (PnL,
return, trades, drawdown — "the monthly-return table for stability review"). Incremental, updated at
each boundary during the run, deterministic.

**`SimulationReport`** bundles: `meta` (run_id, versions, date range, symbols, strategy set),
`portfolio_summary`, `performance`, `attribution`, `allocation`, `risk_events`, `stats`
(session/daily/monthly), and `artifacts` (references to persisted trade_history/execution_log/
equity_curve — see §6's gap about the actual persistence mechanism).

**Batch summary** (optional, cross-run): descriptive statistics (mean/median/p05/p95/min/max) over
return/max_drawdown/profit_factor distributions across a batch of runs (seeds/dates/strategy-sets) —
"it performs no optimization or selection," purely descriptive.

## 11. Testing strategy

Follow the exact same discipline every prior module was held to:

1. Unit tests per new component (`SimulationContext` validation, Replay Clock, Execution Simulator's fill
   rules per order type, Portfolio Simulator's accounting formulas, Performance Analyzer's metric
   formulas) with hand-constructed, controllable inputs (fixed bars, fixed orders) — mirroring the
   `FakeBrokerAdapter`-style fully-controllable-fixture pattern from Execution Engine's own test suite.
2. **Determinism tests are the highest-value new test class here** — run the identical `SimulationContext`
   + data twice, assert byte-identical `SimulationReport`. This matters more here than for any prior
   module.
3. **A dedicated conformance test against the frozen research engine's own conventions** (§8's
   acknowledged-but-unspecified obligation) — design this explicitly; do not skip it just because the
   docs don't hand you a ready-made test plan.
4. Integration tests running the REAL composed pipeline (real Market Scanner + Strategy Manager + Signal
   Engine + Scoring Engine + Risk Manager + Execution Engine) through a short historical replay window
   against the new Execution Simulator + Portfolio Simulator, proving the full chain produces a coherent
   `SimulationReport` — mirroring every prior module's own `test_engine_integration.py` pattern, scaled
   up to the full six-module chain plus the three new components.
5. Explicit coverage for every documented failure mode in `SIMULATION_ARCHITECTURE.md` §7 (config/data
   errors at configure/load, unrecoverable mid-run errors, margin/insolvency halts).
6. Explicit state-machine coverage for both the run lifecycle (9 states) and the per-bar cycle
   sub-states.
7. Test the "one bad bar/order/position cannot abort the whole run" principle — the same sibling-
   entry-point / exception-safety discipline carried forward from Risk Manager's and Execution Engine's
   own adversarial reviews (§13 below).

## 12. Performance/benchmark strategy

- Historical precedent: Market Scanner's own Phase 6.1 large-scale benchmark ran into a real problem
  (`tracemalloc` measurement artifact at large scale — resolved, documented in
  `MARKET_SCANNER_VALIDATION_REPORT.md` and `NEXT_SESSION.md` §G item 6). **Default any memory profiling
  of a hot replay loop to OFF, with an explicit opt-in flag and a documented safe-scale ceiling, from the
  start** — do not repeat that investigation from scratch.
- A multi-year, multi-symbol replay is exactly the kind of hot loop where `jsonschema`'s per-call `$ref`
  resolution would be a measured bottleneck (as it was for Market Scanner) — use `fastjsonschema` for any
  hot-path `SIMULATION_SCHEMA.json` validation from the start, not as an after-the-fact fix.
- `cProfile` overhead is large for code with millions of tiny function calls (a multi-year bar-by-bar
  replay will have exactly that shape) — always cross-check profiler conclusions against a real,
  unprofiled timing measurement.
- Establish a **controlled, smaller-scale baseline first** (e.g. a few months, one symbol) before
  attempting a large multi-year, multi-symbol run — this was the approach that worked for Market Scanner
  after its own large-scale benchmark investigation.

## 13. Adversarial review requirement

**Mandatory, not optional** — it has found real bugs in every one of the 6 implemented modules so far
(2 Market Scanner, 6 Strategy Manager, 5+1 Signal Engine, 4 Scoring Engine, 8 Risk Manager, 7 Execution
Engine — 33 real issues, zero false-negative sessions). Before declaring any Simulation Framework
component READY:

- Spawn a fresh-eyes subagent with NO memory of writing the code. It must read all 10 frozen spec docs in
  full, then every source file, hunting for: cost-model/formula deviations from §9 above, fail-safe
  violations (does a single bad bar/order/position ever abort the whole run instead of degrading
  gracefully?), determinism violations (any hidden wall-clock, unseeded randomness, or order-dependent
  iteration anywhere in the replay loop?), state-machine correctness (both state machines from §10 of the
  frozen docs), and — the two most-likely-to-recur classes of bug, carried forward explicitly from the
  last two modules' own reviews:
  - **Sibling-entry-point inconsistency**: the Simulation API has AT LEAST 9 entry points
    (`configure`/`load`/`run`/`step`/`run_batch`/`pause`/`resume`/`stop`/`report`/`status` — more than
    either Risk Manager's 2 or Execution Engine's 5) that can each touch the run's mutable state (the
    Portfolio Simulator's account, the Execution Simulator's open orders, the Performance Analyzer's
    accumulating stats). Design ONE shared internal helper for state mutation/advancement from the FIRST
    draft, not after review finds the gap.
  - **Prose ordering vs. execution-order correctness**: Execution Engine's own CRITICAL finding #1 was
    exactly this class of bug (a frozen doc's prose list order didn't match the order needed for
    correctness). The per-bar cycle in `SIMULATION_STATE_MACHINE.md` §B and the sequences in
    `SIMULATION_SEQUENCE.md` list stages in a specific order — verify the actual implementation's order
    is causally necessary, not just copied from the prose, especially around the margin/insolvency check
    (which `SIMULATION_SEQUENCE.md` §5 says "runs inside `ACCOUNT`" — verify this doesn't create a
    similar reordering trap where an account mutation happens before or after it should relative to
    fills/rollups).
- Verify EVERY finding against the actual source before fixing (don't trust the review's claims at face
  value) — this project's own standing discipline.
- Fix every genuine issue with a dedicated regression test.

## 14. Non-negotiable boundaries

- **No broker, no MetaTrader, no network** — everything offline against historical data
  (`SIMULATION_API.md` §4.3, `SIMULATION_ARCHITECTURE.md` §11).
- **No research/strategy/learning mutation, no optimization** — the framework composes and measures
  only; batch runs produce descriptive cross-run statistics ONLY, never selection/optimization
  (`SIMULATION_API.md` §4.4/§5).
- **Never modifies any composed pipeline module** (Market Scanner through Execution Engine) — the
  framework composes them, provides the Replay Data Source + three new simulation-only components, and
  nothing else.
- **Strategy access ONLY via the Strategy Manager** (`load_library()`/`active_strategies()`) — never
  reaches into the Strategy Library or Research Lab directly, same boundary rule every prior module has
  followed.
- **No method mutates a strategy, a contract, research, or a composed module** (`SIMULATION_API.md` §5).
- Every standing rule in `NEXT_SESSION.md` §I applies unchanged (no shortcuts, no fake benchmarks, no
  fabricated statistics, no hidden redesign, mandatory adversarial review, stop-and-wait-for-CEO-approval
  between phases — do not self-authorize Learning Engine, Broker Adapter, or MT5 after this phase either).

## 15. Known integration gaps (carry these into implementation explicitly, don't rediscover them)

1. **Execution Simulator ↔ `BrokerAdapter` Protocol mapping is unverified** — §3 above. Resolve and
   document as IMPLEMENTATION CHOICE before writing `EXECUTION_SIMULATOR.md`'s implementation.
2. **Portfolio Manager still does not exist as a real module** — reuse
   `ai_trader.risk_manager.types.PortfolioState` (as Execution Engine already does) or design a new type;
   document whichever is chosen (§5 above, `NEXT_SESSION.md` §G item 2).
3. **Partial-fill "liquidity proxy" is undefined** (§9) — needs a documented numeric/formulaic
   IMPLEMENTATION CHOICE.
4. **`latency_model` is named but never specified** (§9) — needs a documented default (e.g. "no latency
   in v1, config hook reserved for future use") if not fully implementing it.
5. **`initial_margin_pct`/`maintenance_margin_pct`/`leverage_max` have no numeric defaults** (§9) — needs
   documented, conservative placeholder defaults, matching every prior module's "conservative placeholder
   for design review, not tuned values" precedent (e.g. Risk Manager's `RISK_POLICY.md` §0 framing).
6. **Liquidation policy's actual ordering rule is unspecified** (only asserted "deterministic," §9) —
   needs an explicit, documented rule (e.g. largest-loss-first, or symbol-id order) chosen and justified.
7. **The conformance check against the frozen research engine is explicitly acknowledged as owed but not
   specified** (§8) — design the actual test/tolerance yourself; this is real, required work, not
   optional polish.
8. **Artifact/report persistence mechanism is unspecified** (§6/§10) — file path convention? In-memory
   only for v1? Needs an explicit, documented choice.
9. **`capital_allocation`'s concrete schema is undocumented** — named in `SIMULATION_CONTEXT.md` §A.4 as
   "advisory; Risk Manager enforces" but has no formal shape in `SIMULATION_SCHEMA.json` (which only has
   an `allocation` object under `report`, not under `context`). Needs an explicit, documented input shape
   if you choose to support per-strategy initial allocation at all in v1.

## 16. Exact first implementation task

1. **Get explicit CEO approval for Phase 6.7** — the one open gate (`NEXT_SESSION.md` §H/§I).
2. **Re-read all 10 frozen docs in full** (§4 above) — this handoff summarizes and cross-references them,
   it does not replace reading the originals.
3. **Resolve §15 items 1 and 2 explicitly first** (Execution Simulator's Protocol relationship;
   Portfolio Manager/`PortfolioState` reuse-vs-new-type decision) — these block writing the Execution
   Simulator and Portfolio Simulator respectively, and both should be documented as IMPLEMENTATION
   CHOICE before any other code is written, exactly like the Portfolio Manager gap was resolved at the
   start of Execution Engine's own implementation.
4. **Suggested build order** (mirrors every prior module's own successful "types → config → core logic →
   facade" sequence): `types.py` (mirror `SIMULATION_SCHEMA.json` + design `PortfolioState`-adjacent
   types as needed) → `config.py`/`SimulationContext` (mirror `SIMULATION_CONTEXT.md`'s field tables
   exactly, with every unspecified numeric default from §15 documented explicitly) →
   `schema_validation.py` (`fastjsonschema` from the start) → **Execution Simulator** (the fill-rules
   engine, §9) → **Portfolio Simulator** (the accounting engine, §9) → **Performance Analyzer** (the
   metrics engine, §10) → the Replay Clock + Simulation Harness (the orchestrator wiring everything
   together, implementing the per-bar cycle from `SIMULATION_STATE_MACHINE.md` §B and
   `SIMULATION_SEQUENCE.md` §2) → the public API facade (`SIMULATION_API.md`'s ~11 methods).
5. Unit tests per component as you build (not deferred to the end), then integration tests against the
   real composed pipeline, then the mandatory adversarial review (§13), then the validation report
   (following the exact template every prior module used: what was built → design decisions marked
   IMPLEMENTATION CHOICE → adversarial review findings + fixes → final numbers → protected-invariants
   confirmation → verdict), then `NEXT_SESSION.md`/`CHANGELOG.md` updates, then commit.

## 17. Explicit STOP conditions

**Stop immediately once the Simulation Framework (Execution Simulator + Portfolio Simulator + Performance
Analyzer + orchestration) reaches a READY or NOT READY verdict.** Do NOT, in this or any future session,
self-authorize beginning:

- **Learning Engine** — not designed, not started, no architecture docs exist for it at all yet.
- **Broker Adapter** — a REAL one. (The abstract `Protocol` in `execution_engine/broker_adapter.py`
  already exists and is not itself "the Broker Adapter phase" — that phase means a real venue
  integration, which remains unauthorized.)
- **MT5 integration** — no code, no design work, nothing.
- **Live execution** of any kind.

All four require an explicit new CEO go-ahead, granted only after the Simulation Framework has
demonstrated — with real, reproducible numbers, never fabricated or estimated — robust, profitable
portfolio management across many historical runs. That determination is the CEO's to make from the
`SimulationReport`s this framework produces, not something to self-declare from within an implementation
session.
