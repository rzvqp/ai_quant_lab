# Strategy Interface — the permanent Research-Lab ↔ AI-Trader boundary

This package defines **Strategy Interface v1**: the ONLY sanctioned way the future AI Trader may communicate
with the strategies in `knowledge/strategies/`. It is **documentation and machine-readable schema only** — no
executable code, no engine, no research. It does not modify the Strategy Library, the engine, or S1–S51.

## The separation law (non-negotiable)

```
   RESEARCH LAB                     STRATEGY LIBRARY                    AI TRADER
   (produces strategies)            (executable specifications)        (consumes the interface)
   ────────────────────            ─────────────────────────          ──────────────────────
   engine (mstrat v2)      ──▶     knowledge/strategies/S**/     ◀──   Strategy Interface v1 ONLY
   matched-null, Wave-N            strategy.json (the CONTRACT)        (contract + runtime API)
   knowledge graph, parquets       README.md (human mirror)
        │                                                                     ▲
        │  research artifacts                                                 │
        └────────────────── NEVER crosses this line ─────────────────────────┘
```

- **Research produces strategies.** The lab (engine, matched-null, Wave experiments, knowledge graph, result
  parquets, research reports) is upstream and private.
- **The Strategy Library stores executable specifications.** Each strategy exposes EXACTLY the same interface.
- **The AI Trader consumes ONLY the Strategy Interface** — the static Contract (`strategy.json`, validated by the
  JSON Schema here) plus the runtime API defined here. **The AI Trader must never read internal research
  artifacts** (`results/*.parquet`, `knowledge/experiments/*`, `knowledge/ontology/*`, `code/*`, the raw market
  builders). If a value is not in the Contract or returned by an API method, the AI Trader does not get it.

This boundary is what makes the two systems independently evolvable: research can rewrite a strategy's internals
and re-run Wave experiments without breaking the Trader, as long as the Contract still validates against the
schema and the interface version is respected.

## Package contents

| file | purpose |
|---|---|
| `STRATEGY_INTERFACE_v1.md` | the Execution Contract: every field, required/optional, enums, validation rules, versioning & compatibility policy |
| `strategy_contract.v1.schema.json` | JSON Schema (Draft 2020-12) that every `strategy.json` must validate against |
| `STRATEGY_API_v1.md` | the runtime query API (`detect`, `generate_signal`, `get_score`, `can_trade`, `can_open_position`, `explain_signal`, `required_context`, `health`) — signatures & semantics, no implementation |
| `runtime_responses.v1.schema.json` | JSON Schema for the runtime response objects (Signal, Score, Health, gates, ContextRequirement, Explanation) |
| `AI_TRADER_ARCHITECTURE.md` | the future AI Trader as modules only (Loader … Explainability), the data-flow, and where the boundary is enforced |

## Design stance
- **Strategies are pure evaluators.** A strategy never fetches its own data and never executes orders. The AI
  Trader supplies market context (per `required_context()`); the strategy returns a signal/score/health. This is
  what keeps a strategy stateless, testable, and swappable.
- **Honesty is encoded.** The Contract carries the true epistemic state (`maturity`, `validation_status`,
  `matched_null_status`, `global_fdr_status`, `walk_forward_status`). Today nearly every strategy is
  `EXPLORATORY` / `NOT_RUN`; the interface makes the Trader gate on that rather than assume validity.
- **Everything is versioned.** `interface_version` (this contract's schema) and each strategy's `version` evolve
  under the semver + compatibility policy in `STRATEGY_INTERFACE_v1.md`.

*Status: DESIGN (Strategy Interface v1). No code is executed by this package. The existing `strategy.json` files in
`knowledge/strategies/` are the v0 seed; migrating them to fully validate against v1 is a separate, gated task.*
