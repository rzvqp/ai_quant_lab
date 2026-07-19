# Phase 7 — Checkpoint 7: Decision Intelligence Layer

## 1. Executive Summary

Checkpoint 7 builds the **Decision Intelligence layer** (`ai_trader/decision_intelligence/`) — the AI
Trader's first reasoning layer. Market Intelligence (Checkpoint 5) describes what the market is doing;
Edge Intelligence (Checkpoint 6) identifies which strategies' statistical edges are currently PRESENT;
Decision Intelligence answers the new question this checkpoint exists to build: **which edge, if any,
deserves execution.**

The public entry point `make_decision(context)` evaluates every currently-PRESENT edge against a small,
disclosed set of eligibility gates built entirely from each strategy's own already-declared Contract
fields (never invented, never re-scored), ranks the eligible ("ACCEPT") candidates by a deterministic,
fully disclosed tie-break chain, and recommends the single best one — or explicitly **NO TRADE** when no
edge qualifies, which the CEO's own directive names as a valid decision in its own right, not an error
or an omission. Every verdict, at every stage, is traceable to a concrete, already-produced fact from a
prior layer or an already-declared metadata field — never a hidden score, never a probabilistic guess.

This checkpoint does not execute a trade, send an order, size a position, or touch MT5, Signal Engine,
Scoring Engine, Risk Manager, Shadow Evidence, or Execution Engine — it produces a recommendation only.

## 2. Architecture

```
MarketContext
     |
     v
evaluate_edges(context)                          <- Edge Intelligence (Checkpoint 6), reused as-is
     |
     v
EdgeIntelligenceSnapshot  ---------------------+
     |                                          |
     | filter: state is PRESENT                | load_strategy_contracts(library_path)
     v                                          v   <- Edge Intelligence's own reader, reused as-is
present strategy_ids                    dict[strategy_id, Contract]
     |                                          |
     +-------------------+----------------------+
                          |
                          v
     evaluate_candidate(strategy_id, edge_reading, contract, research_stats)   (eligibility.py)
                          |
              +-----------+-----------+
              |                       |
              v                       v
         DecisionOutcome.REJECT   DecisionOutcome.ACCEPT
     (status/maturity/confidence/  (no eligibility gate triggered)
      expectancy gate triggered)
                                       |
                                       v
                      rank_candidates(accepted, contracts, research_stats)     (ranking.py)
                      -- maturity_rank desc -> confidence rank desc -> expectancy_r desc -> strategy_id asc
                                       |
                                       v
                      comparison_notes(ranked, contracts, research_stats)
                      -- pairwise "why X outranks Y" narrative, or an honest tie disclosure
                                       |
                                       v
                              DecisionReport(candidates, recommended_strategy_id, comparison_notes)
                                       |
                                       v
                    recommended_strategy_id  or  "NO TRADE"   (engine.py::recommended_or_no_trade)
```

## 3. Decision Flow

1. `make_decision(context, research_stats=None, library_path=None)` is called once per bar/context
   snapshot (the same cadence every prior layer is designed for).
2. It calls `edge_intelligence.evaluate_edges(context)` — unmodified, reused exactly as Checkpoint 6
   built it — and `edge_intelligence.load_strategy_contracts(library_path)` for the same purpose.
3. Only strategies whose `EdgeState` is `PRESENT` become candidates at all (per the CEO's own "Evaluate
   every PRESENT edge" framing) — a strategy that is `ABSENT`/`POSSIBLE` never appears in
   `DecisionReport.candidates`, since Edge Intelligence has already produced a fully disclosed verdict
   for it and Decision Intelligence would add no new information by repeating it.
4. Each PRESENT candidate is run through four disclosed eligibility gates, in order (§4): contract
   status, contract maturity, declared research confidence, and — only if the caller supplied
   `research_stats` for that strategy — historical expectancy. The first gate that trips produces a
   REJECT with a concrete explanation; a candidate that clears every gate is ACCEPT.
5. Every ACCEPT candidate is deterministically ranked (§5); the pairwise ranking narrative is recorded.
6. The single top-ranked ACCEPT candidate becomes `recommended_strategy_id`; if there are zero ACCEPT
   candidates (either because zero edges were PRESENT, or every PRESENT edge failed a gate),
   `recommended_strategy_id` is `None` — `recommended_or_no_trade()` reports this as the literal string
   `"NO TRADE"`.
7. Nothing here mutates the input `context`, calls any execution primitive, or retains state between
   calls — every call is a pure function of its own arguments.

## 4. Eligibility Gates (`eligibility.py`) — all four disclosed, all reused from already-declared fields

| Gate | Rejects when | Source |
|---|---|---|
| Contract status | `lifecycle.status` is not `IMPLEMENTED` | `Contract.lifecycle.status` (existing strategy metadata) |
| Contract maturity | `lifecycle.maturity` is `RETIRED` | `Contract.lifecycle.maturity`, via the existing `maturity_rank()` helper (`strategy_manager.contract`) |
| Declared research confidence | `evidence.confidence.level` is `NONE` or `NEGATIVE` | `Contract.evidence.confidence.level` (existing strategy metadata) |
| Historical expectancy (only if `research_stats` supplied for that strategy) | `n_trades > 0` and `expectancy_r <= 0` | Caller-supplied `ResearchStats` (existing research statistics) |

A candidate with zero historical trades (`n_trades == 0`) never trips the fourth gate — there is no
track record to judge, which is a different fact from a negative one, and this layer never fabricates a
verdict from absent data.

## 5. Ranking (`ranking.py`) — the deterministic tie-break chain

1. Contract maturity, higher first (`maturity_rank()`, reused from `strategy_manager.contract` —
   `RETIRED` is already excluded at the eligibility stage, so only `EXPLORATORY`..`PROMOTED` are ever
   compared here).
2. Declared research confidence, higher first (`VERY_LOW`..`HIGH`; a local, disclosed ordinal ladder —
   no `confidence_rank()` helper exists upstream to reuse).
3. Historical `expectancy_r`, higher first, only if `research_stats` was supplied (a strategy with no
   supplied stats sorts after one with a known positive value — never assumed equal to it).
4. `strategy_id`, ascending — the final, always-available deterministic tie-break, matching the
   convention already established by `shadow_evidence/comparison.py` (Checkpoint 4).

`comparison_notes()` walks the ranked list pairwise and names, for each adjacent pair, the FIRST
criterion that differentiates them (e.g. `"S7 outranks S12: maturity=PROMOTED(rank 3) > VALIDATED(rank
2)"`), or — when two candidates are genuinely tied on every criterion — discloses that honestly
(`"...tied on maturity, confidence, and expectancy_r -- S1 ranked first only by strategy_id..."`). This
satisfies the CEO's own "why it is stronger or weaker than competing edges" and "if multiple edges are
equally valid, explain why" requirements without any invented scoring.

## 6. Public API

```python
from ai_trader.decision_intelligence.engine import make_decision, recommended_or_no_trade

report = make_decision(context)                       # MarketContext -> DecisionReport
report = make_decision(context, research_stats={...})  # optional, caller-supplied ResearchStats mapping
best = recommended_or_no_trade(report)                  # -> strategy_id str, or the literal "NO TRADE"
```

`recommended_or_no_trade()` is the clean, execution-decoupled query surface — "what is the best decision
right now?" (the CEO's own Checkpoint 7 directive) — a future execution-facing module is meant to call,
without needing to inspect `DecisionReport.candidates` or any evidence internals itself.

## 7. Data Structures

`types.py`: `DecisionOutcome` (ACCEPT/REJECT), `ResearchStats` (a minimal, LOCAL echo of research
statistics — n_trades/win_rate/expectancy_r/sharpe_ratio — deliberately NOT the
`shadow_evidence.types.StrategyResearchSummary` type, and this package never imports
`ai_trader.shadow_evidence` at all), `DecisionCandidate` (`__post_init__` rejects empty evidence — a
verdict with no disclosed reasoning is exactly what this layer must never produce), `DecisionReport`
(`candidates`, `recommended_strategy_id`, `comparison_notes`).

## 8. Independence (verified, not merely designed)

The CEO's own Checkpoint 7 directive requires complete independence from Signal Engine, Scoring Engine,
Risk Manager, Shadow Evidence, Execution Engine, and MT5. Verified via grep before committing: zero
imports of `signal_engine`, `scoring_engine`, `risk_manager`, `execution_engine`, `shadow_evidence`, or
any MT5/MetaTrader reference anywhere in `ai_trader/decision_intelligence/` (the only hits are
comment-level disclosures explaining the independence itself, e.g. "this package never imports
`ai_trader.shadow_evidence`"). Zero reference to `decision_intelligence` in `harness.py` — not wired
into the simulation/live runtime in this checkpoint. The only `ai_trader/` packages imported are
`edge_intelligence` (an explicitly allowed input) and, transitively through it, `market_intelligence` and
`strategy_manager.contract` (also explicitly allowed inputs — "existing strategy contracts"/"existing
strategy metadata").

## 9. Files Added

All files are new; nothing pre-existing was modified.

```
ai_trader/decision_intelligence/__init__.py
ai_trader/decision_intelligence/types.py
ai_trader/decision_intelligence/eligibility.py
ai_trader/decision_intelligence/ranking.py
ai_trader/decision_intelligence/engine.py
ai_trader/decision_intelligence/tests/__init__.py
ai_trader/decision_intelligence/tests/_fixtures.py
ai_trader/decision_intelligence/tests/test_eligibility.py
ai_trader/decision_intelligence/tests/test_ranking.py
ai_trader/decision_intelligence/tests/test_types.py
ai_trader/decision_intelligence/tests/test_engine.py
ai_trader/decision_intelligence/tests/test_integration.py
```

No file outside `ai_trader/decision_intelligence/` was touched. `harness.py`, every prior-checkpoint
package (`market_intelligence/`, `edge_intelligence/`, `shadow_evidence/`), and every original frozen
pipeline module are byte-for-byte unchanged.

## 10. Validation

```
pytest ai_trader/ -q
    -> 1830 passed (Checkpoint 6 baseline 1798 + 32 net new, zero regressions, zero failures)

mypy --strict ai_trader/ --exclude 'tests/'
    -> Success: no issues found in 199 source files (Checkpoint 6 baseline: 194)

coverage report --omit="*\tests\*"
    -> TOTAL 10879 stmts, 432 miss, 96%  (Checkpoint 6 baseline: 10776 stmts, 432 miss, 96%)
    -> +103 new statements from decision_intelligence, +0 net new misses
    -> every decision_intelligence/*.py source file: 100% covered individually
       (__init__ 1/1, eligibility 19/19, engine 22/22, ranking 29/29, types 32/32)
```

A first full-suite run surfaced 3 real coverage gaps (`ranking.py`'s expectancy-differentiator branch in
`comparison_notes`, `types.py`'s `ResearchStats` negative-`n_trades` guard, `types.py`'s
`DecisionCandidate` empty-evidence guard) — all three closed with 4 additional targeted tests before the
final run above.

## 11. Tests

- **Unit tests** (30, split by module): `test_eligibility.py` (11 — accepts a clean candidate, each of
  the four gates individually, the zero-trades non-block case, determinism); `test_ranking.py` (11 —
  each tie-break criterion individually, the missing-research-stats-sorts-last case, comparison-notes
  correctness for every branch including the genuine-tie disclosure, determinism, empty-input handling);
  `test_types.py` (2 — both `__post_init__` guards).
- **Engine unit tests** (5, `test_engine.py`): a synthetic Strategy Library (`tmp_path`) with real,
  currently-registered strategy ids — a clean top-ranked recommendation, NO TRADE when every PRESENT
  candidate is REJECTed, NO TRADE when zero edges are PRESENT at all, caller-supplied `research_stats`
  changing the outcome, determinism.
- **Real-data integration tests** (3, `test_integration.py`): drives the real `MarketScanner`/
  `ReplayDataSource` pair (identical construction to Checkpoints 5–6's own integration tests) over real
  XAUUSD data, calling `make_decision()` against the REAL Strategy Library with no synthetic override and
  no `research_stats` supplied, across 20 real, fully-warmed-up contexts — confirms the full
  Market-Intelligence-to-Edge-Intelligence-to-Decision-Intelligence chain never raises, is deterministic,
  and that both ACCEPT and REJECT outcomes genuinely occur among real candidates (proving the eligibility
  gates are real discriminators on real data, not vacuous). NO TRADE itself did not occur within this
  particular 20-bar window (disclosed, not hidden: the current Library's contract maturity/confidence
  metadata is static across the window, so whichever strategy is both PRESENT and top-ranked on most bars
  dominates the recommendation deterministically — correct behaviour given static metadata, not a defect;
  the unit-level `test_engine.py` tests separately prove NO TRADE is reachable and correctly reported).

## 12. Commit Hash / Branch / Working Tree Status

- Branch: `ai-trader-implementation`
- Parent commit: `952b2c73e4833c084b3b8e43dae749037f9d8e34` (Official Project Save)
- This checkpoint's commit hash: recorded in a documentation-only follow-up commit after this report's
  own commit lands (same pattern used at the close of Checkpoints 5 and 6).
- Working tree: clean after commit (all `decision_intelligence/` files added, nothing else changed).
