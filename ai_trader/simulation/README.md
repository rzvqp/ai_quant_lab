# AI Trader Simulation Framework v1 — (design)

The Simulation Framework is how the AI Trader **proves it can manage a portfolio of executable strategies
profitably — before any broker exists**. It replays years of historical data through the **exact same pipeline**
the live AI will run, with a virtual broker and a virtual account, and produces a full performance report. No
broker, no MetaTrader, no live execution — and, per the new roadmap, this framework is the priority; broker
integration is Phase 8+.

**This package is documentation and architecture only.** No runtime code, no executable logic, no broker/MT5
dependency, no research/strategy/learning changes, no backtests run here. It modifies nothing: Research Lab,
engine, Strategy Library, Strategy Interface, Market Scanner, Strategy Manager, Signal Engine, Scoring Engine,
Risk Manager, Execution Engine, S1–S51, Wave 1, Knowledge Graph, holdout are all untouched. Everything is additive
inside `ai_trader/simulation/`.

## The core principle — identical pipeline, one swap point
The simulator runs the SAME modules, in the SAME order, as the future live AI:

```
Market Scanner → Strategy Manager → Signal Engine → Scoring Engine → Risk Manager
      → Execution Engine → [ Execution Simulator ] → Portfolio Simulator → Performance Analyzer → Learning Engine (future)
```

The **only** difference between simulation and live is the component behind the Execution Engine's Broker Adapter
contract:
- **Simulation:** the **Execution Simulator** plays the Broker Adapter (virtual fills against historical bars) and
  the **Portfolio Simulator** plays the account (virtual balance/equity/positions).
- **Live (Phase 8+):** a real **Broker Adapter** + real account reconciliation replace exactly those two.

Everything upstream — Scanner, Manager, Signal Engine, Scoring Engine, Risk Manager, Execution Engine — is
**byte-identical** between sim and live. This is what makes the simulation a faithful proof: if it is profitable
and robust in simulation, the same decisions run live. The Simulation Framework **composes** the existing modules;
it does not modify them.

## What the framework provides (the swap-in parts + the harness)
- **Replay Clock + Replay Data Source** — drives the deterministic historical clock and feeds the Market Scanner
  (via the replay/lab-parity data-source adapter defined in the Market Scanner design).
- **Execution Simulator** — the virtual Broker Adapter (spread, commission, slippage, partial fills, order types).
- **Portfolio Simulator** — the virtual account (balance, equity, floating/closed PnL, positions, margin,
  exposure, drawdown, trade history) exposing the same `PortfolioState` the future Portfolio Manager will.
- **Performance Analyzer** — metrics, strategy attribution, capital allocation, risk events, session/daily/monthly
  statistics, and the full `SimulationReport`.
- **Simulation Harness** — the orchestrator that runs the pipeline bar-by-bar over a replay, and can run thousands
  of runs across hundreds of strategies.

## Design principles (non-negotiable)
- **Deterministic:** replay produces **bit-identical** results every run. No hidden randomness; any stochastic
  model (slippage) is seeded deterministically from the run seed + order/bar identifiers. No wall-clock in logic.
- **No broker / no MetaTrader dependency.** Everything works offline against historical data.
- **No research/strategy/learning modification, no optimization.** The framework only composes + measures.
- **Faithful to live:** same modules, same contracts, same order of operations; only the Execution Simulator and
  Portfolio Simulator stand in for the venue.

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `SIMULATION_ARCHITECTURE.md` | the framework as a deterministic orchestrator of the identical live pipeline; components, data flow, determinism, scale, versioning, boundaries |
| `SIMULATION_CONTEXT.md` | the immutable run spec (dates/symbols/timeframes/capital/costs/seed/strategy set) + the runtime context threaded through the loop |
| `EXECUTION_SIMULATOR.md` | the virtual Broker Adapter: spread/commission/slippage/partial-fills/order-types, deterministic fills against historical bars |
| `PORTFOLIO_SIMULATOR.md` | the virtual account: balance/equity/floating+closed PnL/positions/margin/exposure/drawdown/trade history/capital allocation |
| `PERFORMANCE_ANALYZER.md` | metrics, strategy attribution, allocation, risk events, session/daily/monthly stats, `SimulationReport` |
| `SIMULATION_API.md` | the framework API (configure/load/run/step/run_batch/report/health/statistics) — definition only |
| `SIMULATION_SEQUENCE.md` | the per-bar loop (the exact pipeline), warmup, fills across bars, roll-ups, batch runs, startup/shutdown |
| `SIMULATION_STATE_MACHINE.md` | the framework lifecycle + per-bar cycle |
| `SIMULATION_SCHEMA.json` | JSON Schema (Draft 2020-12) for the `SimulationRun` (config + report) |

## Goal
Run thousands of historical simulations, evaluate hundreds of strategies simultaneously, manage a complete virtual
portfolio, and produce a full performance report — **deterministically, without any broker**. Only after this
framework is complete and validated will the Broker Adapter and MetaTrader integration be designed.

## Status
DESIGN (Simulation Framework v1). Deliverables complete for review. **Nothing beyond the Simulation Framework is
begun** (no Broker Adapter, no live execution, no MT5, no Learning Engine implementation) — all await explicit CEO
approval.
