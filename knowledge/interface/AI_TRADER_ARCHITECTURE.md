# AI Trader — reference architecture (modules only)

The future AI Trader consumes the Strategy Library **exclusively** through Strategy Interface v1 (the static
Execution Contract + the runtime API). This document describes its modules, their responsibilities, the data
flow, and where the separation boundary is enforced. **Modules only — no implementation, no code.**

The AI Trader is a separate system from the Research Lab. It never imports lab code, never reads
`results/*.parquet`, `knowledge/experiments/*`, `knowledge/ontology/*`, or `code/*`. Its only knowledge of a
strategy is that strategy's Contract and the typed responses of the API.

---

## 1. The boundary (where it is enforced)

```
        ══════════════════ RESEARCH LAB (upstream, private) ══════════════════
        engine · matched-null · Wave-N · knowledge graph · result parquets
                                   │  emits (gated)
                                   ▼
        ┌──────────────────  STRATEGY LIBRARY  ──────────────────┐
        │  knowledge/strategies/S**/strategy.json  (CONTRACT)    │   ← validated by strategy_contract.v1.schema.json
        └───────────────────────────┬────────────────────────────┘
                                     │  Strategy Interface v1 (contract + runtime API)   ◀── THE ONLY DOOR
        ══════════════════════════════╪═══════════════════════════════════════════════
                                     ▼
        ┌───────────────────────  AI TRADER  ─────────────────────────────────────┐
        │  Strategy Loader → Strategy Manager → Signal Scanner → Confidence Engine │
        │  → Conflict Resolver → Portfolio Manager → Risk Manager → Execution      │
        │  Planner ;  cross-cutting: Performance Monitor, Learning Engine,         │
        │  Knowledge Feedback, Explainability Engine                               │
        └─────────────────────────────────────────────────────────────────────────┘
```

The **Strategy Loader** is the single point that touches contract files; every other module works with in-memory
`StrategyHandle` objects that expose only the interface. Nothing downstream can reach research artifacts.

---

## 2. Modules

### Strategy Loader
Discovers `knowledge/strategies/*/strategy.json`, validates each against `strategy_contract.v1.schema.json`,
checks `interface_version` compatibility (§6 of the interface spec), and produces validated `StrategyHandle`s.
A contract that fails validation or targets an unsupported MAJOR is quarantined (`current_health=INVALID`,
never tradable). This is the ONLY module that reads files from the Library.

### Strategy Manager
Owns the live registry of `StrategyHandle`s and their operational state: enable/disable, cooldown clocks,
kill-switches, `current_health`, and the per-strategy `TraderState`. Exposes the roster to the scanner and
enforces `lifecycle.status`/`maturity` gates (e.g. never route capital to `EXPLORATORY` beyond a research budget).
Holds no market logic.

### Signal Scanner
Per bar/tick: assembles each strategy's `Context` from `required_context()`, then calls `health` → `can_trade` →
`detect` → `generate_signal` in the reference order. Emits the set of live `Signal`s (with their `Context`) to the
Confidence Engine. Purely an orchestrator of the API; contains no strategy logic.

### Confidence Engine
Calls `get_score()` and combines it with the Contract's `evidence` (maturity prior, OOS, validation ladder) into
a single, cross-strategy-comparable confidence. Caps unvalidated strategies (the interface already refuses to let
`EXPLORATORY`/negative-OOS strategies look confident). Produces ranked, scored signal candidates.

### Conflict Resolver
Resolves contradictions among concurrent signals: opposite directions on the same instrument, overlapping
setups, correlated strategies double-counting one move. Uses `explain_signal()` context + declared
`dependencies`/`market_regime` to net or suppress. Outputs a coherent, de-conflicted candidate set.

### Portfolio Manager
Decides which de-conflicted candidates to hold together: exposure budgeting across strategies/regimes,
correlation-aware diversification, per-strategy `capital_limit` and `max_concurrent_positions`, and honouring
`can_open_position()`. Produces target positions (still in R terms).

### Risk Manager
Translates R-terms into real risk: per-trade risk budget → absolute size (the execution-layer decision the
Contract leaves open), portfolio drawdown limits, exposure caps, and the global kill-switch. Can veto or scale
any target. It — not the strategy — owns money.

### Execution Planner
Turns approved, sized targets into an execution plan (order type, entry/stop/target placement, timing, slippage
assumptions consistent with the Contract's cost model). Emits orders to the broker/engine adapter. The only
module aware of the live venue; still strategy-agnostic.

### Performance Monitor
Tracks realised vs expected per strategy (live expectancy, drawdown, hit-rate, drift vs `historical_metrics`).
Feeds `live_drift_ok` back into `health()` inputs and flags `DEGRADED`/`STALE`. Emits alerts and the live metrics
stream. Read-only w.r.t. strategies.

### Learning Engine
Adapts ALLOCATION and META-PARAMETERS the Trader owns (weights, thresholds, regime gating), learning from the
Performance Monitor. **It may never mutate a strategy's internals or Contract** — strategies change only via new,
research-gated contract versions. This is the hard rule that keeps learning on the Trader side of the boundary.

### Knowledge Feedback
The ONE-WAY, gated return channel to the Lab: packages live outcomes and observed limitations as *proposals*
(e.g. "S5 live drift consistent with the EXP-04 beta finding") for the Research Lab to consider. It writes
NOTHING into the Library or the Lab directly; it emits a report the Lab may act on under its own governance.

### Explainability Engine
Produces human/audit narratives for every decision by composing `explain_signal()` + the Confidence/Conflict/
Risk rationale. Every order is traceable to a strategy `contract_ref{id,version}`, the triggered conditions, and
the risk decision — without exposing any research internals.

---

## 3. Data flow (per decision cycle)
```
market feed ──▶ Signal Scanner ──(Context)──▶ [Strategy API] ──▶ Signals
                                                        │
Signals ──▶ Confidence Engine ──▶ scored ──▶ Conflict Resolver ──▶ de-conflicted
        ──▶ Portfolio Manager ──▶ targets ──▶ Risk Manager ──▶ sized/approved
        ──▶ Execution Planner ──▶ orders ──▶ venue
Performance Monitor ⟲ (realised) ──▶ Learning Engine (allocation only) ─┐
                                    └▶ Knowledge Feedback ──(proposals)──▶ Research Lab (gated)
Explainability Engine ⟵ taps every stage ──▶ audit log
```

## 4. Invariants the architecture must preserve
1. **One door:** only the Strategy Loader reads the Library; everything else uses the interface. No module reads
   research artifacts.
2. **Strategies are pure evaluators:** stateless, dataless, orderless. All state and money live in the Trader.
3. **Validation gates action:** `maturity`/validation-ladder fields cap allocation; `EXPLORATORY` strategies get
   at most a research/paper budget until the Lab advances them (matched-null full universe → walk-forward →
   holdout). No strategy is treated as validated alpha by default.
4. **Learning stays Trader-side:** the Learning Engine tunes allocation/meta-params only; strategy behaviour
   changes exclusively through new contract versions produced by the Lab.
5. **Everything is explainable and versioned:** every order references `contract_ref{id,version}` and the
   interface version; the audit trail reconstructs any decision from (contract, context, responses).
6. **Fail safe:** invalid/quarantined contracts, missing context, cooldown, kill-switch, and drift all resolve to
   "do not trade" — never to a guess.

## 5. Status
DESIGN only. No AI-Trader code exists or is implemented here. This document + `STRATEGY_INTERFACE_v1.md` +
`STRATEGY_API_v1.md` + the two JSON Schemas constitute the permanent contract the future AI Trader will be built
against. Building the Trader, and migrating the v0 `strategy.json` files to fully validate against v1, are
separate CEO-gated tasks.
