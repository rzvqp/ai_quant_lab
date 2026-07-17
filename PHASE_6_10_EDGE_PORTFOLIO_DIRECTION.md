# Phase 6.10 — Edge Portfolio Direction

**Date:** 2026-07-17. **Scope: a short architectural-direction note, requested by the CEO before any
further implementation.** No code is changed by this document. It does not implement Checkpoint 1C or
select a Strategy Health integration policy — it re-frames what Checkpoints 1A/1B already built and
shows, with evidence rather than assertion, that the same architecture scales from 1 edge to N edge
families without redesign.

---

## 1. The re-frame: Phase 6.10 is not "a Shadow system for S10"

S10 was the CEO's own chosen **first validation target** (Checkpoint 1B, §OBJECTIVE: "S10 is only the
first configured strategy"). Nothing in Checkpoints 1A/1B was ever built around S10 specifically —
that constraint was explicit from the start and was verified, not merely stated: Checkpoint 1B's own
test suite includes `test_shadow_enabled_for_multiple_strategies_still_produces_byte_identical_
competitive_execution`, which enables Shadow for `("S10", "S21", "S39", "S40")` — four strategies, none
privileged — and passes identically to the single-strategy case. `ShadowEvidenceEngine` and
`ShadowConfig` contain zero references to any specific strategy id anywhere in their own source.

**Terminology mapping** (so this document's own vocabulary and the codebase's don't talk past each
other): the CEO's **"edge"** — New York Reversal, Opening Range Breakout, London Breakout, Trend
Continuation, Asia Range Sweep, Mean Reversion, Liquidity Reversal, or a future discovery — is exactly
what the codebase already calls a **strategy**: one `RuntimeEvaluator` subclass, registered once under
one `strategy_id` in `ai_trader/strategy_runtime/registry.py`. S1–S51 are 43 such edges already
implemented and registered. "New York Reversal" is not a new kind of *object* the system needs to learn
about — it is a 44th (or Nth) entry in the same registry, exactly like S1–S51 already are. This document
does not propose renaming `strategy_id`/`RuntimeEvaluator` to `edge_id`/`EdgeEvaluator` — that would be
pure churn, not an architectural change — but uses "edge" and "strategy" interchangeably below, since
they are the same unit.

---

## 2. Why the architecture scales without redesign — the mechanism, not just the claim

The reason Checkpoints 1A/1B generalize is structural, not incidental. Three facts, each already
verified (not assumed):

1. **Signal Engine and Scoring Engine are called once per bar, for every registered strategy together**
   (`harness.py::_run_one_bar`, unchanged since before Phase 6.10). Adding a 44th, 50th, or Nth edge to
   the registry means these two calls simply iterate one more handle — nothing about how they're
   invoked changes, because they already iterate the FULL registered set, not a fixed list.
2. **`ShadowEvidenceEngine.observe()` filters `score_batch.scores` by `strategy_id in
   self._shadow_strategy_ids`** — a single membership check against a `frozenset[str]` built from
   `ShadowConfig.active_strategy_ids()`. This is O(1) per score and carries no per-strategy branching:
   the exact same code path handles 1, 5, 43, or any N strategy ids.
3. **Every dedicated per-strategy object (`RiskManager` today; `ExecutionEngine`/`ExecutionSimulator`/
   `PortfolioSimulator` when Checkpoint 1C adds them) is constructed lazily, keyed by `strategy_id`, in
   a plain `dict[str, ...]`** (`ShadowEvidenceEngine._risk_managers`). Adding edge N+1 means the dict
   gains one more key the first time that edge produces a score — no code path is aware of "how many"
   edges exist, only "which one is this."

Nothing here required inventing a new abstraction for this document — it is a description of code that
already exists and is already tested at N=1 and N=4.

---

## 3. The scaling walkthrough: 1 → 5 → 43 → N, what changes and what doesn't

| Stage | Config change | Code change | Evidence |
|---|---|---|---|
| **1 edge** (S10) | `shadow_strategies=("S10",)` | none | Checkpoint 1B: full-scale validation against Phase 6.9A, byte-identical competitive execution. |
| **5 edges** | `shadow_strategies=("S10","S21","S39","S40","S46")` (or any 5 ids) | none | Checkpoint 1B already tested 4 of these 5 simultaneously (`test_shadow_enabled_for_multiple_strategies...`); a 5th is the same code path, unverified only because nobody has run it yet — not because anything would need to change to run it. |
| **43 strategies** | `shadow_strategies=ai_trader.strategy_runtime.registry.registered_strategy_ids()` — literally "all currently registered edges," already a one-line, existing repository call | none to `ShadowConfig`/`ShadowEvidenceEngine`/`harness.py` | Not yet run at this scale. Genuinely new consideration: **runtime/memory**, addressed in §4 below — this is a real, honestly-disclosed risk, not a free lunch. |
| **N edge families** (new, not-yet-implemented edges: Opening Range Breakout, London Breakout, etc.) | Same as above — `shadow_strategies` grows by however many new ids get registered | **none**, provided the new edge is implemented the same way S1–S51 already are: a `RuntimeEvaluator` subclass registered via `@register("EDGE_ID")` in `strategy_runtime/registry.py` | Structural guarantee from §2 — Signal/Scoring Engine already iterate the full registry; the shadow tap already filters by membership in a set, not a fixed list. |

**The one thing that does NOT come for free at any stage above N=1**: someone has to actually implement
and register the new edge's own detection/entry logic (a new `RuntimeEvaluator` subclass) — that is
Research Lab / strategy-development work, not Shadow Evidence work. Shadow Evidence does not discover
edges; it evaluates already-implemented candidate edges with live, independent evidence. This is stated
explicitly so "scales without redesign" is not misread as "requires no new work at all" — the NEW WORK
is bounded to writing the edge's own evaluator (the same work every one of S1–S51 already required),
never to modifying the Shadow Evidence system itself.

---

## 4. Honest risks at scale (not glossed over)

1. **Runtime/memory at 43+ edges.** Already flagged in the accepted architecture design (§17.1, Q6):
   Signal/Scoring Engine calls are unaffected (0× — shared, tapped once regardless of N); `RiskManager.
   evaluate()` calls scale with **actionable-opportunity volume**, not strategy count × bar count (Phase
   6.9A's own portfolio-wide figures put this around ~1.3× today's per-bar-batched volume, not a naive
   43×). The one real multiplier risk is per-bar bookkeeping once Checkpoint 1C adds per-edge
   `ExecutionSimulator`/`PortfolioSimulator` instances (mark-to-market, order-book scan) — bounded by a
   proposed, exact-parity-preserving optimization (skip processing for any shadow instance with no open
   position and no pending order that bar), estimated at ~3–5× rather than 43×, **still requiring an
   actual benchmark before a 43-edge rollout**, exactly as already specified in the accepted design's
   own test plan (§13, test 8) and staged rollout (§14, Checkpoint 3). Nothing about today's Checkpoint
   1B result changes this — the S10 validation ran ONE shadow edge, not 43.
2. **Strategy Health integration is still unselected** (design §11: three options compared, none
   chosen) — this is the "health" stage of the CEO's own 7-stage lifecycle (§5 below), and it remains a
   dedicated, separate, future CEO decision. What IS already in place: `ShadowTradeLegRecord` is
   trivially projectable into `strategy_health.types.ClosedTrade`'s exact shape, and
   `strategy_health.metrics.py`'s own frozen computation functions could consume a shadow-sourced
   `ClosedTrade` stream for ANY number of edges without new scoring math — this was a deliberate design
   choice specifically so the health stage scales the same way the rest of the lifecycle does, but it is
   not implemented or activated today.
3. **Capital allocation across edges (the actual "Portfolio Manager" decision) does not exist yet.**
   Nothing in Checkpoints 1A/1B designs, implements, or even sketches how N validated edges would
   eventually share real capital, resolve same-bar conflicts among themselves, or receive a real
   position slot each. This is explicitly the territory of a future "Portfolio Orchestrator"/allocation
   layer — named but never designed in the accepted architecture doc (§18/§17.1 Q9's own scope-discipline
   table explicitly confirms "consensus execution," "strategy aggregation," and "Portfolio Orchestrator"
   were never introduced by Checkpoints 1A/1B, by design). Saying the EVIDENCE-COLLECTION architecture
   scales to N edges is not the same claim as saying the CAPITAL-ALLOCATION architecture exists yet — it
   does not, and this document does not pretend otherwise.
4. **Edge families as a grouping concept (e.g., "all session-timing edges") do not require new
   infrastructure** — if ever wanted, a family is just a set of `strategy_id`s, expressible today as
   `shadow_strategies=(...)` filtered to that subset, or as an optional metadata tag on the existing
   `Contract`/registry entry. No new registry mechanism, no new data contract, is implied by "family" as
   a concept — it is a query over the existing `strategy_id` keyspace, not a new keyspace.

---

## 5. The 7-stage lifecycle, mapped onto what exists / what's planned / what's undesigned

The CEO's own required lifecycle per edge — opportunities, virtual positions, virtual executions, trade
history, statistics, health, portfolio contribution — maps directly onto the accepted architecture
design's own checkpoints, already scoped in that order before this document existed:

| Lifecycle stage | Status | Where |
|---|---|---|
| Opportunities | **DONE (Checkpoint 1B)** | `ShadowOpportunityRecord`, generic over any configured edge |
| Virtual positions | Designed, not implemented | `ShadowPositionRecord` (contract exists since 1A); lifecycle in design §4, Checkpoint 1C candidate |
| Virtual executions | Designed, not implemented | `ShadowTradeLegRecord` (contract exists since 1A, extends `TradeRecord`); design §4/§7, Checkpoint 1C candidate |
| Trade history | Designed, not implemented | The same `ShadowTradeLegRecord`/`ShadowPositionRecord` ledger, per edge, once populated |
| Statistics | Designed, not implemented | `ShadowStrategySummary` → reuses `strategy_health.metrics.py`'s own frozen `WindowMetrics` computation on a shadow-sourced `ClosedTrade` stream (design §9, revised) |
| Health | **Explicitly deferred, three options compared, none selected** | Design §11 — requires its own dedicated CEO decision |
| Portfolio contribution (capital allocation across edges) | **Not designed** | Future work — no document to date proposes an architecture for this |

Every stage through "statistics" already has a concrete, generic (non-S10-specific) design; "health" has
a menu with no selection; "portfolio contribution" has neither.

---

## 6. The end goal, and what stands between here and there

**The end goal, in the CEO's own words: an AI Portfolio Manager that continuously discovers, evaluates,
validates, and allocates capital across statistically robust market edges.** Mapped against what exists
today:

- **Discovers**: the Research Lab's own existing hypothesis-generation and backtesting pipeline
  (`code/`, frozen, unrelated to Shadow Evidence) — already exists, unaffected by anything in this
  document.
- **Evaluates**: Shadow Evidence (Checkpoints 1A/1B done for opportunities; positions/executions/
  statistics designed, not yet implemented) — this is the piece Phase 6.10 is actively building, and the
  piece this document confirms scales generically.
- **Validates**: Strategy Health (frozen scoring methodology, integration policy unselected) plus the
  Research Lab's own statistical-validation machinery (matched-null engine, global-FDR — both
  separately gated, unrelated to this phase).
- **Allocates capital**: does not exist yet, in any form, for any edge. This is the largest remaining
  gap between today's architecture and the stated end goal, and it is intentionally not addressed by
  this document — it is a distinct design question for a distinct, future, dedicated CEO-approved phase.

**This document's own conclusion**: the Shadow Evidence architecture, as built through Checkpoint 1B,
is already a genuine, unforced, generic Edge Portfolio evidence-collection layer — not a system that
happens to also work for other strategies as an afterthought. Scaling it to 5, 43, or N edges requires
configuration changes only, for the "opportunities" stage already implemented and the "positions/
executions/statistics" stages already designed. It does **not** yet reach "health" (unselected) or
"portfolio contribution" (undesigned) — those remain open, and this document does not claim otherwise.

---

## 7. Recommendation

Proceed to Checkpoint 1C as previously recommended — virtual execution for one edge (S10 remains the
natural first proof point, since it is the only edge with an existing, independently-verified Phase
6.9A isolated-run ground truth to validate against) — but reframed explicitly as **the first proof that
the "virtual positions/executions" stage of the Edge Portfolio lifecycle is ALSO generic**, using the
same multi-strategy test pattern Checkpoint 1B already established (`("S10", "S21", "S39", "S40")`-style
tests proving byte-identical competitive execution regardless of which or how many edges are shadow-
tracked). No change to this recommendation's own scope boundaries (still no Strategy Health integration,
still no capital allocation, still no multi-position live trading) — only the framing changes: this is
not "S10's checkpoint," it is "the second proof point for the Edge Portfolio's evidence lifecycle,
validated using S10's own existing ground truth because it is the one edge with independently verified
isolated-run numbers to check against."

**No code is implemented by this document. Waiting for CEO approval before Checkpoint 1C begins.**
