# AI Trader

The AI Trader is a **separate system** from the Research Lab. It consumes strategies **only** through the frozen
**Strategy Interface v1** (`knowledge/interface/`): the static Execution Contract (`strategy.json` validated by
`strategy_contract.v1.schema.json`) plus the runtime Strategy API. It **never** reads Research-Lab internals —
not the engine (`code/`), not result parquets (`results/`), not the knowledge base / graph / experiments.

> This `ai_trader/` tree is the AI Trader's own home. It is designed to be extractable into its own repository;
> nothing here modifies the Research Lab, the Strategy Library, the Strategy Interface, the engine, S1–S51,
> Wave 1, matched-null, or the holdout. Everything in this tree is **DESIGN / DOCUMENTATION** until a build phase
> is explicitly gated.

## Canonical pipeline (CEO-ratified, Phase 5.x)

```
Market Scanner      ← Phase 5.1 (this deliverable): observe market → standardized MarketContext
      ↓
Strategy Loader     ← load + validate contracts (Strategy Interface v1)
      ↓
Strategy Manager    ← live registry, health, cooldown, kill-switch, maturity gating
      ↓
Signal Engine       ← per strategy: required_context → detect → generate_signal (feeds it the MarketContext)
      ↓
Scoring Engine      ← get_score + evidence prior → cross-strategy comparable confidence
      ↓
Conflict Resolver   ← net/suppress contradictory or correlated signals
      ↓
Portfolio Manager   ← what to hold together (exposure, diversification, allocation)
      ↓
Risk Manager        ← R → real size, drawdown/exposure caps, global kill-switch (owns money)
      ↓
Execution Engine    ← approved sized targets → order plan → venue adapter
      ↓
Learning Engine     ← adapts ALLOCATION / meta-params only (never strategy internals; feedback to Lab is gated)
```

Cross-cutting (not in the linear flow): Performance Monitor, Knowledge Feedback, Explainability Engine (see
`knowledge/interface/AI_TRADER_ARCHITECTURE.md` for the interface-level view — unchanged by this phase).

## Separation law (unchanged, restated)
- Research **produces** strategies · Strategy Library **publishes** them · Strategy Interface **defines** the
  contract · **AI Trader only consumes the contract.**
- The Market Scanner is the AI Trader's single point of contact with raw market data. Downstream modules and
  strategies see only the standardized `MarketContext` — never the broker feed, never Lab data.

## Modules
| module | phase | location |
|---|---|---|
| **Market Scanner** | **5.1 (design here)** | `ai_trader/market_scanner/` |
| Strategy Loader … Learning Engine | later phases (gated) | `ai_trader/<module>/` (not yet created) |

Start with `ai_trader/market_scanner/MARKET_SCANNER_README.md`.
