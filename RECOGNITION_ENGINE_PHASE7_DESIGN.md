# Phase 7 — Recognition Engine (Live Wiring) — Design

**CEO scope**: only authorized/versioned pattern recognition, never runtime-invented patterns; returns
`RecognitionCandidate`/`RecognitionResult`; never decides risk, never sends orders.

## 1. Investigation finding

`ai_trader/recognition_engine/` (Phase 1A, built and CEO-approved in an earlier session) is a
**batch/historical statistics library**, not a live query path: `compute_conditional_statistics(
repository, strategy_id, outcome_kind, dimension, policy) -> tuple[ConditionalStatistics, ...]` scans
the ENTIRE matching population in a `ContextMemoryRepository` and returns one row per bucket value
*observed in history* -- never a single answer for "this one candidate now." Its own Phase 1 design doc
states explicitly: "May not be wired into `harness.py` or any execution path without its own separate,
explicit CEO approval (standing, every Phase 7 layer)" -- this phase's own authorization is that
approval. Confirmed: **no `RecognitionCandidate`/`RecognitionResult` type exists anywhere**, and **no
pattern-ID/version catalog exists anywhere** -- `ContextDimension` (15 members) and `SufficiencyPolicy`
are the only existing "authorization" surface, neither is a discrete, nameable pattern registry. Per
CEO's own instruction, both are built fresh this phase, not invented as statistics/methodology.

`ai_trader/decision_intelligence_v2/adapters.py::build_context_snapshot(mi_snapshot) -> ContextSnapshot`
already exists as a pure, lossless translation from a live `MarketIntelligenceSnapshot` (Phase 6's own
embedded field) into `context_memory`'s `ContextSnapshot` -- the exact bridge this phase needs. It is
**not imported directly** (duplicated instead, ~25 lines, pure and deterministic) to avoid creating a
dependency edge onto `decision_intelligence_v2`, which every other live phase this session has
deliberately excluded from its own allow-list (it belongs to the old scoring-engine-coupled batch
pipeline) -- the same "duplicate a small, self-contained, pure helper rather than import across an
established boundary" precedent already used for `RetryPolicy` (Phase 5) and `CalculationTraceStep`
(Phases 4/6).

`recognition_engine.engine._bucket_value(context_snapshot, dimension) -> str` (private,
underscore-prefixed) IS imported directly, deliberately -- reusing the EXACT SAME function for both the
live candidate's own bucket assignment and the historical group-by is a correctness requirement, not
merely a style choice: it guarantees "which bucket does this live candidate fall into" and "how were
historical positions bucketed" can never silently drift apart into two different mappings.

## 2. Architectural decision: authorized pattern catalog + thin live wrapper

`ai_trader/recognition_engine_live/`:

- `AUTHORIZED_PATTERNS: tuple[RecognitionPattern, ...]` -- a small, explicit, hand-declared catalog. One
  entry per `(ContextDimension, OutcomeKind.STRATEGY)` pair (all 15 dimensions), each with a
  `pattern_id` (e.g. `"REC-SESSION-STRATEGY"`) and `pattern_version` (`"v1"`). A caller supplies a
  `pattern_id`, never a raw `(dimension, outcome_kind)` pair directly -- this is what makes pattern
  recognition "authorized/versioned, never runtime-invented": an unrecognized `pattern_id` is rejected
  before any statistics are ever computed.
- `RecognitionCandidate` -- the live query input (`strategy_id`, `pattern_id`, `as_of`, `correlation_id`).
- `RecognitionResult` -- the output: pattern/candidate echo, `context_bucket_value` (the live candidate's
  own bucket, computed via the reused `_bucket_value`), the REUSED `ConditionalStatistics` row matching
  that bucket (or `None` if history has no observations in this exact bucket -- a truly novel context,
  never fabricated), `sufficiency` (reused `Sufficiency` enum), `pattern_authorized: bool` (deliberately
  NOT named `approved`/`allowed` -- this is a catalog-membership fact, never a trade authorization),
  `reason_codes`, `calculation_trace`.
- `engine.recognize(candidate, mi_snapshot, repository, policy=None) -> RecognitionResult` -- looks up
  the pattern, builds the live `ContextSnapshot`, computes the bucket value, calls
  `compute_conditional_statistics` UNMODIFIED, selects the matching row. Never short-circuits the trace;
  always returns descriptive statistics, never a trading recommendation (the exact Phase 1A discipline,
  carried forward unchanged).

## 3. Safety boundary

Static tests forbid: `MetaTrader5`, any import from `execution_engine`/`order_manager`/`risk_manager`/
`risk_manager_live`/`portfolio_manager_live`/`decision_intelligence`/`decision_intelligence_v2`/
`simulation`, and order-submission vocabulary -- Recognition Engine (live) cannot decide risk or submit
an order even in principle. `RecognitionResult` carries no field that could be mistaken for a trade
decision (no `approved`, no `should_trade`, no directional recommendation of any kind).

## 4. Known, disclosed limitation

`compute_conditional_statistics` re-scans the ENTIRE matching repository population on every call (its
existing, unmodified behavior) -- a live caller invoking this per-candidate against a large repository
pays that full scan cost every time. No caching/incremental-index optimization is built this phase (out
of scope: "wiring," not "re-architecting the statistics engine") -- disclosed as a known performance
limitation, not silently hidden.
