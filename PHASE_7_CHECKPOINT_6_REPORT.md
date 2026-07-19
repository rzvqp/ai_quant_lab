# Phase 7 — Checkpoint 6: Edge Intelligence Layer

## 1. Executive Summary

Checkpoint 6 builds the **Edge Intelligence layer** (`ai_trader/edge_intelligence/`) — the second
component of the AI Trader's reasoning process, sitting directly on top of Checkpoint 5's Market
Intelligence layer. Where Market Intelligence answers *"What is the market doing right now?"*, Edge
Intelligence answers *"Which validated statistical edges currently exist?"* — for every one of the 43
registered production strategies, independently, deterministically, and fully explainably.

For each strategy, the public entry point `evaluate_edges(context)` produces a `StrategyEdgeReading`
carrying one of three states — **PRESENT / POSSIBLE / ABSENT** — plus the exact tuple of
`EdgeEvidenceItem`s that produced it. Every evidence item names the concrete, actually-observed values
that drove it (never a vague phrase), and every item is built from ONLY: (a) the already-built Market
Intelligence snapshot, (b) each strategy's own DECLARED, schema-validated Contract fields
(`execution.long_short`, `execution.sessions`, `semantics.required_data`), and (c) simple, disclosed,
hand-written rules — never a learned model, never a probabilistic guess, never free-text keyword
classification of strategy mechanism. This checkpoint does not choose a trade, does not score, does not
rank, and does not modify any existing module — it only teaches the AI Trader to recognize which
strategies' declared conditions currently line up with the market.

## 2. Architecture

```
MarketContext --------------------------------------------------+
        |                                                        |
        v                                                        v
build_market_intelligence(context)          load_strategy_contracts(library_path)
        |                                          |  (ai_trader.strategy_manager.loader.load_all,
        v                                          |   never StrategyManager -- no scanner handshake,
MarketIntelligenceSnapshot                         |   no lifecycle/health machinery needed)
        |                                          v
        |                                   dict[strategy_id, Contract]
        |                                          |
        +------------------+  +--------------------+
                           |  |
                           v  v
         evaluate_edges(context, library_path=None)      <- single public entry point (engine.py)
                           |
     for each strategy_id in (registered runtime ids) ∩ (readable contracts):
                           |
        +------------------+------------------+------------------+------------------+------------------+
        |                  |                  |                  |                  |                  |
        v                  v                  v                  v                  v                  v
data_availability   directional        session          context_confidence  multi_timeframe   volatility_regime
  (Contract +          (Contract.       (Contract.        (MI snapshot)      _agreement          (MI snapshot)
   context bars)        execution.       execution.                          (MI snapshot)
                         long_short +     sessions +
                         MI trend)        MI session)
        |                  |                  |                  |                  |                  |
        +------------------+------------------+--------+---------+------------------+------------------+
                                                         |
                                                         v
                                        (EdgeEvidenceItem, EdgeEvidenceItem, ...)  -- always 6 items
                                                         |
                                                         v
                                         determine_edge_state(evidence)   (verdict.py)
                                                         |
                                                         v
                                              StrategyEdgeReading(strategy_id, state, evidence)
                                                         |
                                        (collected across every strategy)
                                                         v
                                              EdgeIntelligenceSnapshot(symbol, as_of, readings)
```

## 3. Evidence Dimensions (the CEO's own named examples, each mapped to a real, disclosed check)

| Dimension | Source (declared / computed) | Contribution values used |
|---|---|---|
| `data_availability` | `Contract.execution.timeframe` + `semantics.required_data[*].timeframe`/`.htf` vs. actual bars in the context | SUPPORTS / CONTRADICTS (binary, factual — never NEUTRAL/UNKNOWN) |
| `directional_trend_alignment` (Trend alignment) | `Contract.execution.long_short` vs. Market Intelligence's `TrendReading` on the strategy's own execution timeframe | SUPPORTS / CONTRADICTS / NEUTRAL (BOTH) / UNKNOWN (FLAT/no reading) |
| `session_suitability` | `Contract.execution.sessions` (free text) vs. Market Intelligence's `SessionReading.session_name` | SUPPORTS / CONTRADICTS / NEUTRAL ("all sessions") / UNKNOWN (unparseable) |
| `context_confidence` (Context confidence) | Market Intelligence's `ContextConfidence.score` vs. a disclosed 0.5 threshold | SUPPORTS / CONTRADICTS / UNKNOWN |
| `multi_timeframe_agreement` (Multi-timeframe agreement) | Market Intelligence's `MultiTimeframeAgreement.level` | SUPPORTS (STRONG) / NEUTRAL (MODERATE/WEAK) / UNKNOWN |
| `volatility_regime` (Volatility regime) | Market Intelligence's `VolatilityReading.regime` | SUPPORTS (NORMAL) / NEUTRAL (LOW/HIGH/EXTREME) / UNKNOWN |

**Structure alignment** and **Liquidity behaviour** (also named in the CEO's example list) were
deliberately NOT turned into a per-strategy contradiction/support check: no strategy in the Library
declares a structure or liquidity requirement anywhere in its schema (`market_regime.applicable`/`avoid`
is universally `["ANY"]`/`[]` across all 43 real contracts — verified empirically, not assumed), so
building a per-strategy verdict from them would require inventing an undeclared classification (e.g.
guessing from free-text `mechanism`/`klass` prose) — exactly the "no AI guesses, no hidden reasoning"
the CEO's directive forbids. They remain fully available on every `MarketIntelligenceSnapshot` for a
future checkpoint to use once/if strategies declare real structure/liquidity requirements.

## 4. Data Flow

1. `evaluate_edges(context, library_path=None)` is called once per bar/context snapshot (same cadence
   `build_market_intelligence` is designed for).
2. It builds one `MarketIntelligenceSnapshot` (Checkpoint 5, untouched) and loads every readable
   Contract from the Strategy Library (`ai_trader.strategy_manager.loader.load_all` directly — read-only,
   no Manager, no scanner handshake).
3. For every strategy id that is BOTH currently registered in the runtime (`strategy_runtime.registry`)
   AND has a valid Contract, exactly six evidence items are computed and combined into one
   `StrategyEdgeReading`.
4. A strategy that fails schema validation, or isn't registered with a runtime evaluator, produces NO
   reading at all — never a fabricated one.
5. All readings are assembled into one `EdgeIntelligenceSnapshot`, returned. Missing/insufficient data at
   any single evidence dimension degrades that ONE dimension to `UNKNOWN` — it never fabricates a value
   and never raises.

## 5. Public API

```python
from ai_trader.edge_intelligence.engine import evaluate_edges, present_strategy_ids

snapshot = evaluate_edges(context)                 # MarketContext -> EdgeIntelligenceSnapshot
present = present_strategy_ids(snapshot)           # -> tuple[str, ...], sorted, PRESENT-only
```

`present_strategy_ids()` is the clean, execution-decoupled query surface a future Decision AI is meant
to call — it never needs to inspect `snapshot.readings` or any evidence internals itself.

## 6. Internal Components

| Module | Responsibility |
|---|---|
| `types.py` | `EvidenceContribution`, `EdgeState`, `EdgeEvidenceItem`, `StrategyEdgeReading`, `EdgeIntelligenceSnapshot`. |
| `contracts.py` | `load_strategy_contracts()` — thin, read-only wrapper over `strategy_manager.loader.load_all`. |
| `directional.py` | Directional trend alignment evidence. |
| `session.py` | Session suitability evidence (small, disclosed, honest-degrade parser — see §3). |
| `data_availability.py` | Required-timeframe data-presence evidence. |
| `context.py` | The three context-wide, contract-independent evidence items (confidence, agreement, volatility). |
| `verdict.py` | `determine_edge_state()` — the one disclosed combination rule. |
| `engine.py` | `evaluate_edges()` / `present_strategy_ids()` — the public API. |

## 7. Data Structures

All immutable `@dataclass` types in `types.py`. `StrategyEdgeReading.__post_init__` rejects an empty
evidence tuple — a verdict with no disclosed reasoning is exactly what this layer must never produce.
No field here duplicates or reinterprets a `strategy_health` type; there is zero overlap with
`HealthState`/`WindowScore` — verified via grep before committing (§10).

## 8. Extension Points

- **Decision AI** (explicitly named as the next, NOT-yet-authorized component) can consume
  `present_strategy_ids(snapshot)` or the full `EdgeIntelligenceSnapshot` directly as a pure input — no
  changes needed here.
- New evidence dimensions (e.g. Structure/Liquidity, once/if strategies declare real requirements for
  them) can be added as new modules following the same "pure function → `EdgeEvidenceItem`" shape,
  wired into `engine.py`'s evidence tuple, without touching existing dimensions.
- `verdict.py`'s combination rule is isolated on purpose — a future checkpoint could refine it without
  touching any evidence-producing module.

## 9. Test Strategy

- **Unit tests** (one file per module, 46 tests total): `test_directional.py` (8), `test_session.py` (6),
  `test_data_availability.py` (5), `test_context.py` (10, incl. the `score=None` degrade path via
  `dataclasses.replace`), `test_verdict.py` (5), `test_contracts.py` (3), `test_types.py` (1, the empty-
  evidence guard), `test_engine.py` (5) — every module covers its full-data path, its honest-degrade
  path (never raise, never fabricate), and a determinism check.
- **Real-data integration test** (`test_integration.py`, 3 tests): drives the real `MarketScanner` +
  `ReplayDataSource` pair (same construction as Checkpoint 5's own integration test) over real XAUUSD
  data, calling `evaluate_edges()` against the REAL Strategy Library (no synthetic override) across 20
  real, fully-warmed-up contexts — confirms exactly 43 readings every time (matching the real registered
  ∩ real-valid-contract count, verified independently via `loader.load_all` beforehand), confirms
  determinism, and confirms all three `EdgeState` values genuinely appear across real data (not a
  silently-collapsed verdict).

## 10. Files Added

All files are new; nothing pre-existing was modified.

```
ai_trader/edge_intelligence/__init__.py
ai_trader/edge_intelligence/types.py
ai_trader/edge_intelligence/contracts.py
ai_trader/edge_intelligence/directional.py
ai_trader/edge_intelligence/session.py
ai_trader/edge_intelligence/data_availability.py
ai_trader/edge_intelligence/context.py
ai_trader/edge_intelligence/verdict.py
ai_trader/edge_intelligence/engine.py
ai_trader/edge_intelligence/tests/__init__.py
ai_trader/edge_intelligence/tests/_fixtures.py
ai_trader/edge_intelligence/tests/test_directional.py
ai_trader/edge_intelligence/tests/test_session.py
ai_trader/edge_intelligence/tests/test_data_availability.py
ai_trader/edge_intelligence/tests/test_context.py
ai_trader/edge_intelligence/tests/test_verdict.py
ai_trader/edge_intelligence/tests/test_contracts.py
ai_trader/edge_intelligence/tests/test_types.py
ai_trader/edge_intelligence/tests/test_engine.py
ai_trader/edge_intelligence/tests/test_integration.py
```

No file outside `ai_trader/edge_intelligence/` was touched. `harness.py`, Signal Engine, Scoring Engine,
Risk Manager, Execution Engine, Shadow Evidence, Research, and every `strategy_runtime/families/*.py`
strategy implementation are byte-for-byte unchanged from the Checkpoint 5 commit.

## 11. Validation

```
pytest ai_trader/ -q
    -> 1798 passed (Checkpoint 5 baseline 1752 + 46 net new, zero regressions, zero failures)

mypy --strict ai_trader/ --exclude 'tests/'
    -> Success: no issues found in 194 source files (Checkpoint 5 baseline: 185)

coverage report --omit="*\tests\*"
    -> TOTAL 10776 stmts, 432 miss, 96%  (Checkpoint 5 baseline: 10612 stmts, 432 miss, 96%)
    -> +164 new statements from edge_intelligence, +0 net new misses
    -> every edge_intelligence/*.py source file: 100% covered individually
       (__init__ 1/1, context 25/25, contracts 9/9, data_availability 19/19, directional 20/20,
        engine 27/27, session 21/21, types 31/31, verdict 11/11)
```

A first full-suite run surfaced 2 real coverage gaps (`context.py`'s `score is None` branch,
`types.py`'s empty-evidence guard) — both closed with 2 additional targeted tests before the final run
above; the numbers here are from the corrected, final run.

**Adversarial scope review** (grep-verified against the CEO's explicit DO-NOT list):
- No import of `ai_trader.strategy_health.scoring`, `.classifier`, or `.evaluator` anywhere in the package.
- No `HealthState` or `WindowScore` type used or produced anywhere in the package (one comment-only
  mention in `types.py`'s own module docstring, documenting the absence).
- No import of `signal_engine`, `scoring_engine`, `risk_manager`, `execution_engine`, or `shadow_evidence`
  in any `edge_intelligence` source or test file (two comment-only mentions in `context.py`/`engine.py`
  docstrings explaining a threshold/pattern choice — no import, no call, no coupling).
- No reference to `edge_intelligence` anywhere in `harness.py` — not wired into the simulation/live
  runtime in this checkpoint, matching "Decision AI will consume this package later. Do NOT implement
  Decision AI now."
- No `submit_order`/`OrderRequest`/`RiskDecision`/`"BUY"`/`"SELL"` anywhere in the package — no execution
  or trade-decision logic exists here.
- `git status --porcelain` before committing showed only the new `ai_trader/edge_intelligence/`
  directory — zero diff against every existing strategy family, Signal/Scoring/Risk/Execution/Shadow/
  Research module.

## 12. Commit Hash / Branch / Working Tree Status

- Branch: `ai-trader-implementation`
- Parent commit: `a68ac1fe1b429acb7b471eaf3705fc57354f0478` (Checkpoint 5, doc-only follow-up)
- This checkpoint's commit hash: recorded in a documentation-only follow-up commit after this report's
  own commit lands (same pattern used at the close of Checkpoint 5).
- Working tree: clean after commit (all `edge_intelligence/` files added, nothing else changed).
