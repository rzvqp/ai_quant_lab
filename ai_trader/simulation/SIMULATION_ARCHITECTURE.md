# Simulation Framework v1 — Architecture (design)

The Simulation Framework is a deterministic orchestrator that replays historical data through the exact live AI
Trader pipeline, with a virtual broker (Execution Simulator) and a virtual account (Portfolio Simulator), and
measures the result (Performance Analyzer). It composes the existing modules unchanged. Design only — no code, no
broker.

---

## 1. Purpose
Prove, deterministically and without any broker, that the AI Trader can manage a portfolio of executable
strategies profitably over years of history — running the identical pipeline that will later run live, so the
proof transfers.

## 2. The identical-pipeline invariant
```
                         ┌──────────────── SAME AS LIVE (composed unchanged) ────────────────┐
 Replay Data Source ────▶│ Market Scanner → Strategy Manager → Signal Engine → Scoring Engine │
 (historical bars)       │ → Risk Manager → Execution Engine                                  │
                         └───────────────────────────────┬──────────────────────────────────┘
                                                          │ OrderRequest (via Broker Adapter contract)
                              ┌───────────── SIMULATION-ONLY SWAP-INS ──────────┼──────────────┐
                              │  Execution Simulator (= virtual Broker Adapter) ◀┘              │
                              │        │ fills / OrderStatus                                    │
                              │        ▼                                                        │
                              │  Portfolio Simulator (= virtual account / PortfolioState)       │
                              │        │ equity / positions / PnL                               │
                              │        ▼                                                        │
                              │  Performance Analyzer → SimulationReport                        │
                              └────────────────────────────────────────────────────────────────┘
                                       Learning Engine (future) — NOT implemented
```
- Everything above the swap line is the **live pipeline, composed unchanged** (Phases 5.1–5.6).
- Only the **Execution Simulator** (Broker Adapter contract impl) and **Portfolio Simulator** (the account /
  `PortfolioState` provider) are simulation-specific. Replacing the Execution Simulator with a real Broker Adapter
  (Phase 8+) is the ONLY change to go live; everything else is identical.
- The Replay Data Source is the Market Scanner's own `replay`/`lab-parity` adapter (Phase 5.1) — not a new data
  path, just the historical clock source.

## 3. Components
| component | role | provenance |
|---|---|---|
| **Simulation Harness** | the orchestrator: owns the replay clock, drives the per-bar pipeline, collects outputs | new (this framework) |
| **Replay Clock** | the deterministic historical clock (`as_of` steps over the run's date range) | new |
| **Replay Data Source** | feeds the Market Scanner historical bars in order | Market Scanner `replay`/`lab-parity` adapter (existing contract) |
| **Pipeline modules** | Scanner → Manager → Signal → Scoring → Risk → Execution Engine | composed UNCHANGED (Phases 5.1–5.6) |
| **Execution Simulator** | virtual Broker Adapter: deterministic fills vs bars (spread/commission/slippage/partials) | new (`EXECUTION_SIMULATOR.md`) |
| **Portfolio Simulator** | virtual account: balance/equity/PnL/positions/margin/exposure/drawdown; provides `PortfolioState` | new (`PORTFOLIO_SIMULATOR.md`) |
| **Performance Analyzer** | metrics/attribution/allocation/risk-events/session-daily-monthly stats → report | new (`PERFORMANCE_ANALYZER.md`) |
| **Simulation Ledger & Logs** | trade history, execution log, equity curve, risk-events log | new |
| **Run Config (SimulationContext)** | the immutable run spec (dates/symbols/timeframes/capital/costs/seed/strategies) | new (`SIMULATION_CONTEXT.md`) |

## 4. Data flow (per replayed bar / `as_of`)
```
Replay Clock → as_of
Replay Data Source → Market Scanner.ingest/advance → MarketContextBatch (per symbol, lookahead-safe)
Strategy Manager.active_strategies() → handles
Signal Engine.evaluate(ctx, handles) → StrategySignal[]
Scoring Engine.score_batch(signals) → OpportunityScore[] (ranked, deterministic)
Risk Manager.evaluate(scores, RiskContext, PortfolioState←Portfolio Simulator) → RiskDecision[] (ALLOW/DENY)
Execution Engine.execute(ALLOW decisions) → OrderRequest → Execution Simulator (Broker Adapter contract)
Execution Simulator: match orders vs the current/next bars → fills / OrderStatus (deterministic)
Portfolio Simulator: apply fills → update positions/balance ; mark-to-market on the bar → equity/floating PnL
Performance Analyzer: record trade/equity/exposure/risk-events ; roll up session/daily/monthly at boundaries
```
`RiskContext` and `PortfolioState` are assembled from the already-flowing MarketContext + the Portfolio Simulator
— exactly the passed-in shapes the Risk Manager/Execution Engine expect. No module learns it is in simulation.

## 5. Determinism (the headline guarantee)
- **Bit-identical replay:** identical `(SimulationContext, historical data, module versions)` ⇒ identical fills,
  equity curve, trades, and report — every run.
- **No hidden randomness:** the only stochastic model is slippage; it is drawn from a PRNG seeded deterministically
  from `run_seed` + a stable key (e.g. `client_order_id` + `as_of`), so it is reproducible and order-independent.
  No wall-clock, no `Date.now`, no unseeded RNG anywhere.
- **Ordered processing:** symbols and orders are processed in a fixed, documented order (symbol id, then the
  Scoring Engine's deterministic rank); the Risk Manager's running-portfolio view is applied in rank order.
- **Lookahead-safe:** the Replay Data Source and Market Scanner enforce the same `available_at ≤ as_of` rule as
  live (Phase 5.1); the Execution Simulator fills only on bars at/after the order (never the signal bar).
- **Parity with the research engine:** the fill conventions (entry at next-open, stop-before-target intrabar,
  cost model) mirror the frozen research execution so simulated results are comparable to the Strategy Library's
  metrics (a conformance check is owed at build; the framework references, never copies, the engine).

## 6. Multi-symbol & multi-timeframe replay
- **Multi-symbol:** the Replay Data Source streams all configured symbols on one shared clock; the Market Scanner
  produces a `MarketContextBatch` per `as_of`; the pipeline evaluates per symbol; the Portfolio Simulator holds
  one virtual account across all symbols (cross-symbol exposure/margin).
- **Multi-timeframe:** the base heartbeat (e.g. M15) drives the loop; higher timeframes advance lookahead-safe
  (Phase 5.1 sync). Strategies needing H1/H4/D1/W1 get them from the MarketContext exactly as live.

## 7. Failure modes (simulation)
| condition | handling |
|---|---|
| missing/gappy historical bar | Market Scanner marks the gap; strategies needing it → NEED_CONTEXT; sim continues (never fabricates prices) |
| warmup not met (run start) | no trades until windows fill (sufficiency INSUFFICIENT); documented warmup period excluded from stats |
| Execution Simulator cannot fill (e.g. limit not touched) | order EXPIRES/CANCELS per TIF, deterministically |
| Portfolio insolvency (equity ≤ 0 / margin call) | Portfolio Simulator triggers a margin/liquidation event; risk-event logged; run may halt per config |
| config/data error at load | run → FAILED with a reason before any bar is processed (fail-fast) |
Determinism is preserved through every failure path.

## 8. Startup & shutdown
**Startup**
```
1. load SimulationContext (dates/symbols/timeframes/capital/costs/seed/strategy set/risk config)
2. compose the pipeline modules (Scanner..Execution Engine) with sim swap-ins (Execution Simulator, Portfolio Simulator)
3. Strategy Manager.load_library → aggregated required_context → configure Replay Data Source / Scanner
4. WARMUP: replay leading bars until scanner warmup satisfied (excluded from performance)
5. RUNNING
```
**Shutdown / completion**
```
1. at end-of-range (or stop): close/mark open positions per config (close-at-last or hold-and-mark)
2. Performance Analyzer finalizes metrics + SimulationReport ; persist ledger/logs
3. COMPLETED (or FAILED/STOPPED); framework holds no live state
```

## 9. Performance & scale
- **Scale targets:** thousands of runs; hundreds of strategies evaluated simultaneously within one run.
- **Batch runs:** `run_batch` executes many `SimulationContext`s (parameter/date/strategy-set sweeps); runs are
  independent and MAY run in parallel — determinism is per-run (each run fully reproducible from its context+seed).
- **Vectorization/caching:** feature computation + windows are the Market Scanner's; the framework caches
  per-`as_of` context and reuses it across all strategies in that bar. Analyzer roll-ups are incremental.
- **Memory:** bounded per run (rolling windows + open orders/positions + incremental stats); trade history +
  equity curve stream to the ledger, not held wholesale. No unbounded growth.
- **Determinism under parallelism:** parallel runs never share mutable state; within a run, parallel per-strategy
  evaluation re-imposes deterministic order (Signal/Scoring guarantees), so results are identical to serial.

## 10. Versioning
- **`simulation_framework_version`** — this framework's spec version.
- **`simulation_schema_version`** — `SimulationRun` shape (`SIMULATION_SCHEMA.json`).
- **`fill_model_version`** / **`cost_model_version`** — the Execution Simulator's fill + cost models (any change
  bumps these so every report is reproducible against the exact models).
- Echoes the composed modules' versions (scanner/manager/signal/scoring/risk/execution + interface/context/signal/
  scoring/risk/order schema versions) so a report records the entire pipeline it was produced by.
- **Compatibility:** the Execution Simulator conforms to the Execution Engine's `broker_adapter_contract_version`
  (Phase 5.6) — the same contract a real Broker Adapter will implement, guaranteeing the drop-in swap.

## 11. Boundaries / interaction
- The framework **composes** the pipeline modules and provides the Replay Data Source, Execution Simulator,
  Portfolio Simulator, and Performance Analyzer. It does not modify any composed module.
- **No broker, no MetaTrader, no network.** Everything is offline against historical data.
- **No research/strategy/learning modification, no optimization.** The Learning Engine slot is future and NOT
  implemented; the framework only produces the reports a future Learning Engine would consume.
- The simulation-only components (Execution Simulator, Portfolio Simulator) implement the exact contracts
  (`Broker Adapter`, `PortfolioState`) their live counterparts will, so going live is a single, localized swap.
