# Strategy Manager v1 — Phase 5.2 (design)

The **Strategy Manager** is the second module of the AI Trader. It is the **single owner of the Strategy Library
inside the AI Trader**: it loads every strategy, validates its contract, checks schema + interface + MarketContext
compatibility, keeps the live registry and lifecycle state, aggregates the union of context requirements for the
Market Scanner, and exposes the active strategies to the Signal Engine.

**This package is documentation and JSON Schema only.** No runtime code, no executable logic, no research, no
backtests. It modifies nothing: Research Lab, engine, Strategy Library, Strategy Interface, Market Scanner, S1–S51,
Wave 1, Knowledge Graph, holdout are all untouched.

## What it is — and is NOT
| the Strategy Manager DOES | the Strategy Manager does NOT |
|---|---|
| discover + load every `strategy.json` in the Strategy Library | generate trading signals |
| validate each Strategy Contract (schema + interface + compatibility) | score, rank, or size anything |
| maintain the strategy **registry** (indices, cache, versions) | execute or route orders |
| maintain each strategy's **lifecycle state** | read Research-Lab artifacts (engine/parquets/KB/KG/experiments) |
| aggregate `UNION(required_context())` → the Market Scanner spec | fetch market data or build MarketContext |
| expose ACTIVE strategies (as interface handles) to the Signal Engine | mutate a strategy's internals or contract |
| track health (loaded/disabled/invalid/incompatible/…) | make trading decisions of any kind |

It is a **management/registry/validation module**. It is the gatekeeper that decides *which* strategies are
loadable, compatible, and active — never *what* they signal.

## Dependencies (stable, upstream)
- **Strategy Interface v1** (`knowledge/interface/`): the Contract schema (`strategy_contract.v1.schema.json`), the
  runtime Strategy API, and the versioning/compatibility policy. The Manager validates every contract against it.
- **Strategy Library** (`knowledge/strategies/`): the source of `strategy.json` files. Read-only.
- **Market Scanner v1** (`ai_trader/market_scanner/`): the Manager's Context Aggregator produces the requirements
  the scanner is configured with (`register_requirements`), and checks `feature_dictionary_version` compatibility.

The Manager consumes these as **stable dependencies**; it never modifies them and never reaches past the contract
into research internals.

## Position in the pipeline
```
Market Scanner → [Strategy Manager] → Signal Engine → Scoring Engine → … → Execution Engine → Learning Engine
                      │  ▲
   required_context() │  │ ACTIVE strategy handles (interface only)
   (union) ───────────┘  └────────────────────────────────────────────▶ Signal Engine
```
The Manager sits between the Market Scanner and the Signal Engine: it tells the scanner what context to produce,
and it hands the Signal Engine the set of active, compatible strategies to evaluate against that context.

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `STRATEGY_MANAGER_ARCHITECTURE.md` | responsibilities, boundaries, components, data flow, dependencies, invariants, failure modes, startup/shutdown, compatibility checker, context aggregator, health monitor, module interaction, versioning |
| `STRATEGY_MANAGER_STATE_MACHINE.md` | the 9 lifecycle states, every transition, the state-machine diagram, mapping to Interface fields |
| `STRATEGY_MANAGER_API.md` | the public API (load_library/reload/validate/list/active/required_context/find/statistics/health + lifecycle ops) — definition only |
| `STRATEGY_REGISTRY_SCHEMA.json` | JSON Schema (Draft 2020-12) for the internal registry object |
| `STRATEGY_MANAGER_SEQUENCE.md` | startup/load, reload, activation, aggregation, compatibility, failure, shutdown sequences |

## Status
DESIGN (Phase 5.2). Deliverables complete for review. Next step (gated, NOT started): implement the Manager against
these documents. **The Signal Engine is NOT begun** and must wait for explicit CEO approval.
