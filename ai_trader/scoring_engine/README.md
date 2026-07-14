# Scoring Engine v1 — Phase 5.4 (design)

The **Scoring Engine** is the fourth module of the AI Trader. It receives every `StrategySignal` from the Signal
Engine and transforms them into standardized, deterministic **`OpportunityScore`** objects (0–100). It **only
evaluates signal quality** — it opens nothing, sizes nothing, learns nothing, and changes nothing about the
strategies.

**This package is documentation and JSON Schema only.** No runtime code, no executable logic, no research, no
backtests. It modifies nothing: Research Lab, engine, Strategy Library, Strategy Interface, Market Scanner,
Strategy Manager, Signal Engine, S1–S51, Wave 1, Knowledge Graph, holdout are all untouched. Everything is
additive inside `ai_trader/scoring_engine/`.

## What it is — and is NOT
| the Scoring Engine DOES | the Scoring Engine does NOT |
|---|---|
| consume `StrategySignal`s (Signal Engine) | open or size positions |
| read a strategy's contract **evidence** (via Strategy Manager, read-only) for historical confidence | manage risk |
| compute a deterministic 0–100 `OpportunityScore` per signal from fixed components | learn or adapt |
| penalize conflicts across concurrently active signals | change strategy parameters, contracts, or a strategy's stored confidence |
| rank opportunities deterministically (no stochastic behavior) | change research or read Research-Lab artifacts |
| explain every score with structured reason codes | execute trades or touch the broker |

It is a **pure, deterministic quality evaluator**: `score = f(StrategySignal, contract-evidence snapshot, fixed
weights, version)`. Same inputs ⇒ same scores and the same ranking. It is **not** a machine-learning predictor.

## Boundary note — evaluate the opportunity, not the trade
The Scoring Engine answers "how good is *this* opportunity, right now, relative to a fixed rubric?" It does NOT
decide whether to take it, how big, or against what portfolio — those are the Risk Manager's / Portfolio
Manager's job. Multiple strategies may simultaneously receive high scores; the Scoring Engine ranks them
deterministically and passes the ranked scores downstream. It never picks or executes.

## Dependencies (stable, upstream)
- **Signal Engine v1** (`ai_trader/signal_engine/`) — supplies `StrategySignal`s (`SIGNAL_SCHEMA.json`) with
  their structured `Explanation` and `context_ref`.
- **Strategy Manager v1** (`ai_trader/strategy_manager/`) — read-only source of a strategy's **contract evidence**
  (maturity, OOS, validation ladder, historical metrics) via `get_contract()`; and the sanctioned caller of the
  Strategy API `get_score()` if a strategy's self-assessment is used as an input.
- **Strategy Interface v1** (`knowledge/interface/`) — the contract `evidence` shape and the `Score` response
  shape it may consume.

The Scoring Engine consumes these as stable dependencies; it never modifies them and never reaches into research
internals (the contract `evidence` block is the interface, not research).

## Position in the pipeline
```
… Signal Engine → [Scoring Engine] → Risk Manager → Portfolio/Execution …
        StrategySignal[]      OpportunityScore[] (ranked, deterministic)
```

## Package contents
| file | purpose |
|---|---|
| `README.md` | this overview |
| `SCORING_ENGINE_ARCHITECTURE.md` | purpose, responsibilities, inputs/outputs, pipeline, components, data flow, failure modes, determinism, performance model, versioning, startup/shutdown, module interaction |
| `SCORING_MODEL.md` | the complete deterministic scoring philosophy: the 9 components, their normalization, the exact 0–100 formula and default weights (non-ML) |
| `SCORING_SCHEMA.json` | JSON Schema (Draft 2020-12) for the `OpportunityScore` |
| `SCORING_API.md` | the public API (score_signal/score_batch/explain_score/validate/statistics/health) — definition only |
| `SCORING_SEQUENCE.md` | single-symbol, multi-symbol, multi-strategy, missing-data, conflict, low-confidence, startup/shutdown sequences |
| `SCORING_STATE_MACHINE.md` | the internal engine lifecycle + the per-opportunity scoring lifecycle |

## Module interaction (fixed)
- **Allowed direct:** Signal Engine (input), Strategy Manager (read-only evidence), Risk Manager (output).
- **Forbidden:** Broker, Research Lab, Knowledge Base, Ontology, Experiment Planner (and no direct link to
  Portfolio/Execution/Learning — those are reached downstream, not by the Scoring Engine).

## Status
DESIGN (Phase 5.4). Deliverables complete for review. **The Risk Manager is NOT begun** and must wait for
explicit CEO approval.
