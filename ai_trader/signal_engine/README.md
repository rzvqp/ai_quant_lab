# Signal Engine v1 — Phase 5.3 (design)

The **Signal Engine** is the third module of the AI Trader. It is a **pure evaluation engine**: it takes the
current `MarketContext` (from the Market Scanner) and the set of ACTIVE strategies (from the Strategy Manager),
evaluates **every active strategy independently**, and produces standardized, self-explaining `StrategySignal`
objects. It makes no trading decision of any kind.

**This package is documentation and JSON Schema only.** No runtime code, no executable logic, no research, no
backtests. It modifies nothing: Research Lab, engine, Strategy Library, Strategy Interface, Market Scanner,
Strategy Manager, S1–S51, Wave 1, Knowledge Graph, holdout are all untouched.

## What it is — and is NOT
| the Signal Engine DOES | the Signal Engine does NOT |
|---|---|
| receive the current `MarketContext` | execute or route trades |
| receive ACTIVE strategy handles from the Strategy Manager | **rank or score** strategies (that is the Scoring Engine) |
| evaluate each active strategy **independently + deterministically** | perform risk management or sizing |
| call the Strategy API (health → can_trade → detect → generate_signal → explain_signal) | modify a strategy or its contract |
| produce a standardized `StrategySignal` + structured `Explanation` | learn or adapt anything |
| validate every emitted signal against the schema | fetch market data or build MarketContext |
| emit signals to the Scoring Engine | read Research-Lab artifacts |

It is a **pure function of (MarketContext, active strategies)** → signals. Same inputs ⇒ same signals (replay
parity). It never decides *what to do* with a signal — only *what each strategy says*.

## Boundary note — evaluation, not scoring
The Signal Engine calls the Strategy API methods that **describe** a strategy's state (`detect`, `generate_signal`,
`explain_signal`, and the `health`/`can_trade` gates). It **does NOT** call `get_score()` — cross-strategy scoring
belongs to the downstream **Scoring Engine**. A `StrategySignal` carries the strategy's OWN declared `confidence`
and `signal_strength` (copied from the contract/`generate_signal`), never a comparative rank.

## Dependencies (stable, upstream)
- **Market Scanner v1** (`ai_trader/market_scanner/`) — supplies the `MarketContext` (per symbol, per `as_of`).
- **Strategy Manager v1** (`ai_trader/strategy_manager/`) — supplies `active_strategies()` handles.
- **Strategy Interface v1** (`knowledge/interface/`) — the Strategy API it calls and the runtime response shapes
  it consumes (`Signal`, `DetectResult`, `Explanation`, `Gate`, `HealthReport`).

The Signal Engine consumes these as stable dependencies; it never modifies them and never reaches past the
interface into research internals.

## Position in the pipeline
```
Market Scanner → Strategy Manager → [Signal Engine] → Scoring Engine → … → Execution Engine → Learning Engine
     MarketContext        active handles        StrategySignal[]
```

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `SIGNAL_ENGINE_ARCHITECTURE.md` | responsibilities, boundaries, components, evaluation pipeline, data flow, invariants, failure modes, isolation, explainability, validation, performance model, module interaction, versioning, startup/shutdown |
| `SIGNAL_ENGINE_STATE_MACHINE.md` | the signal states (BUY/SELL/LONG_READY/SHORT_READY/WAIT_CONFIRMATION/NEED_CONTEXT/BLOCKED/INVALID/NO_SIGNAL), when each is produced, the evaluation state machine |
| `SIGNAL_ENGINE_API.md` | the public API (evaluate/evaluate_strategy/evaluate_all/get_signal(s)/validate_signal/explain/statistics/health) — definition only |
| `SIGNAL_SCHEMA.json` | JSON Schema (Draft 2020-12) for the canonical `StrategySignal` |
| `SIGNAL_EXPLANATION_SCHEMA.json` | JSON Schema for the structured `Explanation` (no free-text generation) |
| `SIGNAL_ENGINE_SEQUENCE.md` | evaluation-pipeline sequences: per-bar, per-strategy, multi-symbol, failure, startup/shutdown |

## Status
DESIGN (Phase 5.3). Deliverables complete for review. **The Scoring Engine is NOT begun** and must wait for
explicit CEO approval.
