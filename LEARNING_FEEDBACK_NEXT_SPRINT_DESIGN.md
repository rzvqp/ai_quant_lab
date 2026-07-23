# Learning/Research Feedback — Next Sprint Design Package (DESIGN ONLY)

Status: **DESIGN ONLY. No code, no pseudocode, no refactor performed.** Nothing in `ai_trader/
learning_feedback/`, `ai_trader/context_memory/`, `ai_trader/simulation/harness.py`, or any other module
has been modified to produce this document. This document proposes options for the three mandatory
blockers the CEO identified after the technical audit; it selects nothing. Implementation awaits separate,
explicit authorization after this design is reviewed.

Builds directly on, and does not repeat, the already-accepted `LEARNING_FEEDBACK_LIFECYCLE_SPECIFICATION.
md` and `LEARNING_FEEDBACK_ARCHITECTURAL_DECISION_PACKAGE.md`, and on the implementation actually shipped
in commit `4e0da51` (`ai_trader/learning_feedback/{capture.py,adapters.py,position_registry.py,
market_snapshot.py,observation_builder.py}`, `ai_trader/context_memory/{contracts.py,identities.py,
repository.py}`, `ai_trader/simulation/harness.py`).

---

## Blocker 1 — Connecting Shadow Evidence to Learning Feedback

### Exact problem

`ShadowEvidenceEngine.observe(as_of, score_batch, risk_context) -> None` (`shadow_evidence/engine.py:221`)
runs its own, fully independent, per-strategy Risk Manager/Execution Engine/Execution Simulator internally
and returns nothing. No per-strategy `RiskDecision` (ALLOW/DENY, `decision_id`, `constraints`), and no
resulting `position_id`, is ever exposed to the caller. `harness.py` (the sole caller, confirmed by
grep) therefore has zero visibility into individual shadow strategy decisions at the moment they happen —
it can only observe RESULTS after the fact, via the already-public `positions()` method and the public
`trade_legs` list attribute. This blocks capturing `OperationalMetadata` (which requires the ALLOW/DENY
decision itself) and blocks REGISTERING a `PendingPosition`-equivalent at decision time (which requires
knowing `observation_id`/`cost_model_ref`/`strategy_id`/the resulting `position_id` before or as the
decision happens, not after).

**A materially favorable fact discovered while drafting this design**: `Observation` is captured once per
`(symbol, as_of)`, never per strategy (Architectural Decision Package Decision 4) — the SAME
`lf_observation_id` `harness.py` already computes for the real-portfolio side, on the same bar, for the
same symbol, is valid for every Shadow strategy trading that symbol that same bar too. Shadow Evidence
does not need its own separate Market Intelligence/Edge Intelligence call — only a way to learn, per
decision, which `(strategy_id, position_id, decision_as_of)` to associate with it.

**A second favorable fact**: Shadow's own `position_id` (`f"{run_id}:{strategy_id}:{symbol}:{as_of}:
{decision.decision_id}"`, `engine.py:310`) is minted DETERMINISTICALLY at decision time, before the
virtual entry order is even known to have filled — unlike the real-portfolio side's `position_key`
(Architectural Decision Package Decision 1), which cannot exist until the opening fill's own `opened_as_of`
is known. This means Shadow, once given decision-time visibility, needs NO two-stage "register candidate,
promote on fill" dance (`promote_opening_fill`) at all — a genuine simplification versus the real side.

### Existing contracts involved

- `ShadowEvidenceEngine.observe()` (`shadow_evidence/engine.py:221`) — the single call site, currently
  opaque.
- `ShadowPositionRecord`/`ShadowTradeLegRecord` (`shadow_evidence/types.py`) — already carry `position_id`,
  already public via `positions()`/`trade_legs`.
- `CorrelationMap`/`PendingCapture`, `PositionCorrelationMap`/`PendingPosition`
  (`learning_feedback/capture.py`) — the real-side machinery; `PositionCorrelationMap` in particular is
  already generically shaped around a `position_key: str`, agnostic to whether that string originates from
  `RealPositionRegistry.make_position_key` or from Shadow's own `position_id` formula — no new type is
  needed there, only a new way to REGISTER an entry for Shadow.
- `capture_operational_metadata` (`learning_feedback/capture.py`) — already generic (takes any
  `RiskDecision`); the blocker is obtaining the `RiskDecision` object itself from Shadow, not the function.

### Architectural options

**A. `observe()` returns a new result type (`ShadowObservationResult`, one row per strategy evaluated this
bar) instead of `None`.**
- Ownership: `shadow_evidence` PRODUCES data (decision outcome, `decision_as_of`, `strategy_id`,
  `position_id` if ALLOW, `denied_reasons` if DENY); `harness.py` CONSUMES it and drives all Learning
  Feedback capture itself — exactly symmetric to how `risk_manager.evaluate()` already returns
  `decision_batch.decisions` for the real side, which `harness.py` alone processes.
- Files changed: `shadow_evidence/types.py` (new frozen type), `shadow_evidence/engine.py` (`observe()`
  return type changes from `None` to `tuple[ShadowObservationResult, ...]`), `harness.py` (process the new
  return value, mirroring the existing real-side decision loop).
- Frozen modules affected: `shadow_evidence/engine.py`/`types.py` — NOT part of Flow A, but a
  previously-closed, extensively tested checkpoint (1A/1B/1C + later aggregation/query-API work) this
  Sprint has not touched until now.
- Advantages: keeps `shadow_evidence` fully independent of `learning_feedback` (zero new import
  dependency); perfectly symmetric with the already-built and already-tested real-side architecture (same
  mental model, same code shape in `harness.py`); Shadow's own `position_id` can be registered directly,
  no promotion-at-fill-time step needed.
- Risks: changes a public method's return type — every existing caller must be updated (confirmed only
  `harness.py` calls it, so blast radius is contained, but `shadow_evidence`'s own existing test suite
  that calls `observe()` directly will need updating too); a genuine, disclosed modification to a
  previously-closed checkpoint.

**B. `ShadowEvidenceEngine` gains an injected, optional Learning Feedback sink and calls it internally.**
- Ownership: `shadow_evidence` becomes a direct CALLER of `learning_feedback` (new dependency edge),
  invoking capture functions itself at exactly the right internal moments, using its own already-known
  internal state without ever exposing it externally.
- Files changed: `shadow_evidence/engine.py` (constructor gains `learning_feedback_sink` parameter, new
  internal calls at decision/resolution points), a new small interface/protocol type (where it lives is
  itself a design question — `learning_feedback` or `shadow_evidence`).
- Frozen modules affected: same as A, `shadow_evidence/engine.py`, but more deeply — new imports, new
  constructor parameter, calls threaded through several internal methods (`observe()`,
  `apply_time_stops()`, `apply_trailing_stops()`, `settle_bar()`, `finalize_at_end()` would ALL need the
  sink threaded through, since resolution can happen from any of them).
- Advantages: `harness.py` stays thin (constructs the sink once, passes it in); Shadow's own internal
  state never has to cross its own module boundary as raw data.
- Risks: `shadow_evidence` gains a real, permanent dependency on `learning_feedback` — a directional
  coupling this project's own design conventions have consistently avoided introducing without strong
  reason (Context Memory's own "zero import dependency on any other package" precedent, `enums.py`'s own
  module docstring); a substantially larger and more invasive change than A, touching five internal
  methods instead of one; higher regression risk against `shadow_evidence`'s own large existing test
  suite (competitive-parity, multi-edge isolation, 43-strategy integration tests all touch these methods).

**C. External, read-only diff over `positions()`/`trade_legs`, mirroring `RealPositionRegistry` (Decision
1's own Option D), with NO decision-time visibility at all.**
- Ownership: `learning_feedback`/`harness.py` only; zero changes to `shadow_evidence`.
- Files changed: a new `ShadowResultRegistry`-equivalent in `learning_feedback`, harness.py wiring.
- Frozen modules affected: none.
- Advantages: zero risk to `shadow_evidence`'s own already-closed checkpoints.
- **Fatal flaw, not merely a risk**: `OperationalMetadata` (the ALLOW/DENY record itself) genuinely
  cannot be produced this way — there is no post-hoc way to recover a DENY decision that never produced
  any position or trade leg at all; a diff over `positions()`/`trade_legs` sees only ALLOW decisions that
  actually resulted in economic activity. This option can, at best, partially solve Outcome/
  InterimRealization capture (using Shadow's own already-exposed `position_id`) but cannot solve
  OperationalMetadata capture for Shadow at all. **Rejected as an insufficient solution to the actual
  problem**, listed for completeness.

### Recommendation

**Option A.** Keeps `shadow_evidence` domain-pure and dependency-free of `learning_feedback` (matching this
whole Sprint's own established preference for one-directional, harness-orchestrated capture rather than
producer modules calling into the capture layer themselves), is architecturally symmetric with the
already-built and already-tested real-portfolio side, and is the smallest of the three viable changes to
`shadow_evidence/engine.py` (one method's return type, not five methods threaded with a new dependency).
Option C is rejected outright as insufficient. Option B is not recommended: it is a larger, riskier change
for a smaller architectural benefit than A, and introduces a coupling this project's own conventions
elsewhere avoid.

### Files that would be modified (if A is authorized)

`shadow_evidence/types.py` (new `ShadowObservationResult`), `shadow_evidence/engine.py` (`observe()`
signature/body), `shadow_evidence/tests/*` (every existing test calling `observe()` directly),
`learning_feedback/capture.py` (a Shadow-specific decision-time registration function, likely simpler than
`register_pending_correlation`/`promote_opening_fill` combined, since no promotion step is needed),
`simulation/harness.py` (process the new return value in the existing shadow-tap call site).

### Frozen modules affected / not affected

Affected: `shadow_evidence/engine.py`, `shadow_evidence/types.py` — the first modification to this package
in this Sprint. Not affected: `portfolio_simulator.py`, `execution_simulator.py`, `execution_engine/`,
`risk_manager/` (Shadow's own internal copies of these remain untouched — only the OUTER `observe()`
boundary changes), Flow A, `context_memory/evidence.py`, `context_memory/retrieval.py`.

### Mandatory tests

Every existing `shadow_evidence` test that calls `observe()` must be updated and must still pass
UNCHANGED IN BEHAVIOR (only the call-site shape changes, per the same "provably behavior-preserving"
proof standard `harness.py`'s own docstring already established for the tap-reordering change). New tests:
`ShadowObservationResult` shape/determinism; an ALLOW decision producing a correctly-registered Shadow
`PendingPosition`; a DENY decision producing `OperationalMetadata` only, no `PendingPosition`; a full
open→interim→terminal Shadow lifecycle captured end-to-end (the first-ever such test for the Shadow side,
since none exists today); a harness-level regression proving the change is a pure, non-interfering tap
exactly like every other Learning Feedback call site (byte-identical Shadow account behavior with the
sink enabled vs. disabled).

### Exact acceptance criterion

`shadow_evidence`'s own full existing test suite passes with zero behavioral change (proven, not assumed);
at least one end-to-end test demonstrates a real `OutcomeKind.STRATEGY` `Outcome` and at least one
`InterimRealization` captured via the new path, using Shadow's own `position_id` directly (no promotion
step); `harness.py` remains the sole orchestrator (no new `learning_feedback` import inside
`shadow_evidence`).

---

## Blocker 2 — Terminal Outcome aggregation for multi-partial-exit positions (REVISED)

**CEO ruling on the prior version of this section**: the original recommendation (read-time join, `Outcome`
left unchanged, last-partial-only) is **rejected**. An object named `Outcome` must never be accidentally
interpretable as the complete position result when it structurally is not — this is a real risk for
Recognition Engine, Prediction Engine, and any future statistical consumer. This revision separates the
canonical accounting result from research metrics, as required, and evaluates naming/structure explicitly
rather than deferring the ambiguity to documentation alone.

### The two levels, kept structurally separate

**Level 1 — Canonical accounting result of the position.** A single, deterministic, position-scoped
aggregate, computed by PURE ARITHMETIC over the complete, closed set of fills belonging to one
`position_key` — no interpretation, no research judgment, nothing that could vary by the question being
asked:
- `total_net_pnl = Σ(partial.net_pnl)`, `total_gross_pnl = Σ(partial.gross_pnl)` across every partial.
- `total_qty_closed = Σ(partial.qty)`.
- `weighted_avg_exit_price = Σ(partial.qty × partial.exit_price) / total_qty_closed` — meaningful for a
  normal close (one direction closing out); for the closing side of a flip, this covers only the qty that
  belonged to the OLD position, never the flip's own new-side remainder (Decision 2's boundary, unchanged).
- `total_costs = Σ(partial.fees)`.
- `holding_time = terminal.exit_as_of − position.opened_as_of` — the FULL lifecycle duration, not the
  last partial's own `holding_bars` (today's `Outcome.horizon` conflates these; a genuine, disclosed
  correction needed regardless of which option below is chosen).
- An explicit, enumerable link to every constituent `InterimRealization` (and, transitively, every
  `TradeRecord`/`ShadowTradeLegRecord`) that contributed — not merely a derivable-in-principle join, but a
  literal list of ids carried on the record itself, so the aggregation trail is directly auditable without
  re-deriving it.

**Level 2 — Research metrics.** Anything computed FROM Level 1 (or from Level 1 + `InterimRealization`s)
for a specific analytical question — e.g. a risk-normalized R-multiple using a specific denominator
convention, a Sharpe-style contribution, a win/loss classification threshold, an execution-quality score
comparing `weighted_avg_exit_price` against some benchmark. These are legitimately plural and
question-dependent — different research questions may reasonably want different formulas over the SAME
Level-1 facts. **Level 2 must never be confused with Level 1**: Level 1 is arithmetic fact, Level 2 is
interpretation. No option below computes Level 2 inside the capture layer — only Level 1, deterministically,
always the same regardless of who reads it or why.

### Existing contracts involved

`Outcome` (`context_memory/contracts.py:315-458`) — CEO-ratified since Phase D; today conflates Level 1 and
Level 2 by construction (its `normalized_result` is already a Level-2-style risk-normalized figure, computed
from only the last partial, presented as if it were the position's own single number). `InterimRealization`
(added this Sprint) — diagnostic-only, per-partial, already excluded from `evidence.py`/`retrieval.py`.
`TradeRecord`/`ShadowTradeLegRecord` — the raw, per-fill source data both levels are ultimately built from.
`PendingPosition` (`learning_feedback/capture.py`) — today stateless between fills; every option below that
persists a Level-1 aggregate at capture time requires it to accumulate references across a position's whole
life.

### Options

**Option (a) — `Outcome` is redefined to unambiguously mean the complete terminal position result.**

- Exact semantic contract: `Outcome.normalized_result` (and every other field) is recomputed to represent
  the FULL Level-1 accounting result (or a clearly-labeled Level-2 figure derived from it), aggregated
  across every partial, written exactly once, at the moment the position reaches zero. The type keeps its
  existing name and its existing `record_type` string (`"context_memory.outcome"`) in the repository.
- Source of truth: the complete ledger of partials for the `position_key`, accumulated by `PendingPosition`
  from first partial to terminal.
- Double-counting risk: **structural, not merely procedural** — because the SAME `record_type` string
  already exists in production-shaped code with the OLD (last-partial) meaning, silently redefining what
  `"context_memory.outcome"` records mean, under an unchanged type name and unchanged schema version, is a
  genuine versioning hazard: if this schema is ever revised again later, or if any historical run's data
  ever needs to be read back, "an `Outcome` record" would no longer have one stable meaning across the
  repository's own append-only history. (No production data exists today, so this risk is latent, not yet
  realized — but the pattern itself is the kind of silent-meaning-drift this project's own conventions
  elsewhere explicitly avoid, e.g. `unavailable_reason`/`InterimRealization` were both added as NEW,
  additive fields/types rather than redefinitions of existing ones.)
- Behavior — partial exit: still produces `InterimRealization` (diagnostic), and now ALSO extends the
  accumulating Level-1 state `PendingPosition` retains; no `Outcome` is written until terminal. Flip: the
  OLD position's `Outcome` aggregates only its own accumulated partials (never the flip's new side,
  unchanged from Decision 2); the new position starts a fresh accumulation. Terminal close: `Outcome` is
  now written from the FULL aggregate, not the last partial alone.
- Impact on existing adapters: **high** — `build_portfolio_outcome`/`build_strategy_outcome` (Phase D,
  already CEO-ratified and shipped) would need their own signature rewritten from "one `TradeRecord`" to "a
  list/aggregate of every partial" — reopening already-closed, already-tested Phase D work.
- Data migration: no real production data currently exists (Shadow is not wired yet; real strategies do not
  yet trade, per the audit's own finding), so migration cost today is zero in practice — but the SCHEMA's
  own meaning changes under an unchanged name, which is a durable, structural risk for whenever this does
  go to production and needs revising a second time.
- Mandatory tests: full rewrite of every existing `test_adapters.py` test that constructs `Outcome` from one
  `TradeRecord` (a breaking change to already-passing tests); new aggregation-math determinism tests;
  single-partial-position regression proof (must reduce to today's exact numeric result, since a plain
  full-fill close is the degenerate one-partial case of the aggregate).

**Option (b) — Rename the existing (last-fill) type so it no longer claims completeness; introduce nothing
new unless paired with option (c).**

- Exact semantic contract: `Outcome` is renamed (e.g. `TerminalFillRealization`/`ClosingFillRecord` — exact
  name a separate decision) to something that honestly scopes it as "the economics of the fill that closed
  this position," never implying "the position's own full result." Fields, construction, and per-fill
  meaning stay EXACTLY as shipped — a rename, not a semantic change.
- Source of truth: unchanged — one `TradeRecord`/`(ShadowPositionRecord, closing_leg)` pair, exactly as
  today.
- Double-counting risk: low for the renamed type itself (its own honest name discourages accidental
  full-result use), but **this option alone does not produce Level-1 aggregate data at all** — it only
  removes a misleading name. On its own, it does not satisfy the CEO's own stated goal (Recognition/
  Prediction Engines still have no canonical, complete position result to consume). Incomplete unless paired
  with (c).
- Behavior: identical to today for partial exit, flip, and terminal close — nothing computationally
  changes, only the name.
- Impact on existing adapters: moderate — `build_portfolio_outcome`/`build_strategy_outcome` renamed to
  match (e.g. `build_portfolio_terminal_fill_record`), internal logic and signature otherwise untouched —
  much lower risk than (a)'s full rewrite.
- Data migration: a pure rename; since no consumer outside this Sprint's own code imports `Outcome`/these
  adapters by name today (Learning Feedback remains fully opt-in/unwired into any other module), the
  rename's blast radius is entirely self-contained.
- Mandatory tests: mechanical rename of every existing reference across `test_adapters.py`/`test_capture.py`
  — no new aggregation-behavior tests required, since nothing computational changes.

**Option (c) — A new, separate `PositionOutcome` type: the canonical Level-1 aggregate, additive, never
replacing the existing per-fill type.**

- Exact semantic contract: a NEW contract, `PositionOutcome`, produced EXACTLY ONCE per `position_key`, at
  the same trigger point `Outcome` already fires on today (the fill that brings the position to zero). It
  carries precisely the Level-1 fields enumerated above — `total_net_pnl`, `total_gross_pnl`,
  `total_qty_closed`, `weighted_avg_exit_price`, `total_costs`, `holding_time` (open → terminal), and an
  explicit tuple of every constituent `InterimRealization`/fill reference. It computes NO Level-2 figure
  itself (no risk-normalized ratio baked in) — that remains a research-layer concern, reconstructable from
  `PositionOutcome`'s own Level-1 facts however a given question requires.
- A further sub-decision this option must resolve explicitly: **persisted at capture time vs. computed at
  read time.**
  - *Persisted* (recommended sub-choice, see below): a new repository stream (`position_outcomes.jsonl`),
    new identity/codec functions mirroring `Outcome`'s/`InterimRealization`'s own already-established
    pattern, and `PendingPosition` gains real accumulation state (every partial's own reference retained
    until terminal). A Recognition/Prediction Engine reads ONE record type and trusts it fully — no join
    logic left to any downstream consumer to get right or wrong.
  - *Computed at read time* (a function, not a persisted record): no new repository stream, no new
    capture-layer accumulation — but this reintroduces the EXACT failure mode the CEO's own ruling rejected
    for the prior "Option D": every future consumer must independently know to perform the join correctly,
    and a missed join silently produces wrong conclusions. Not recommended for the same reason the original
    read-time-join proposal was rejected.
- Source of truth: the complete ledger of partials for a `position_key` (same source as option (a)), but
  written to a NEW, additively-named contract rather than redefining an existing one.
- Double-counting risk: low for `PositionOutcome` itself (written exactly once, deterministically). The
  residual risk is between `PositionOutcome` and `InterimRealization` — a consumer must not ALSO sum
  `InterimRealization`s on top of reading `PositionOutcome` (it already incorporates them). This must be
  documented on both types' own docstrings, and is a smaller, more contained risk than option (a)'s because
  the NEW name carries no pre-existing "this should already be complete" assumption to accidentally trip
  over — a reader encountering an unfamiliar `PositionOutcome` type is more likely to read its own docstring
  than a reader who already has priors about what "Outcome" means.
- Behavior — partial exit: unchanged (`InterimRealization` captured as today), plus contributes to the
  running Level-1 accumulation. Flip: `PositionOutcome` for the OLD position finalizes from its own
  accumulated partials only (Decision 2's boundary, unchanged); the new position starts fresh. Terminal
  close: produces BOTH the existing per-fill type (unchanged or renamed, per whichever of (b) is paired in)
  AND the new `PositionOutcome`.
- Impact on existing adapters: **zero to low** — `build_portfolio_outcome`/`build_strategy_outcome` (Phase
  D) are untouched (or, if paired with (b), renamed only, logic untouched); a NEW pair of adapters
  (`build_portfolio_position_outcome`/`build_strategy_position_outcome`) is ADDITIVE. This is the lowest
  adapter-impact option of the three that actually produces the aggregate data.
- Data migration: none required for the existing type (whichever name it ends up with) — a new, additive
  repository stream starts empty and fills going forward, exactly like `InterimRealization`'s own stream did
  this Sprint. No historical data to migrate (none exists in practice yet).
- Mandatory tests: full contract validation/identity/codec/repository round-trip suite for `PositionOutcome`
  (mirroring exactly how `InterimRealization` was built and tested this Sprint); aggregation-math
  determinism and edge-case tests (a single-partial position's `PositionOutcome` must reduce to numbers
  identical to what the existing per-fill type already reports for that same fill — a continuity proof, not
  a new formula producing a different number for the simple case); flip-boundary test (the old position's
  `PositionOutcome` never includes the new side's own economics); an explicit double-counting-guard test/
  documented contract proving `PositionOutcome` + `InterimRealization` must never both be summed by a
  correct consumer; a test proving the constituent-reference list is complete and correctly ordered for
  audit.

### Recommendation

**Option (c), persisted, paired with a rename under Option (b).** Concretely: rename the existing per-fill
type (currently `Outcome`) to something explicitly scoped to "the closing fill's own economics" — removing
the misleading name entirely, at near-zero risk since no code outside this Sprint's own package depends on
the current name yet — and introduce a new, persisted `PositionOutcome` as the ONE canonical, unambiguous,
Level-1 accounting result intended for Recognition Engine/Prediction Engine/any statistical consumer.
This is preferred over:
- pure Option (a) (redefine `Outcome` in place), because silently changing an already-shipped record type's
  meaning under an unchanged `record_type` string is a durable schema-versioning hazard, and because it
  forces a full, high-risk rewrite of already-ratified Phase D adapters;
- pure Option (b) alone, because a rename without the new aggregate does not actually give Recognition/
  Prediction Engines the canonical result they need — it only removes a bad name, it does not supply the
  right data;
- the read-time-computed sub-variant of (c), because it reintroduces exactly the "must remember to join
  correctly" failure mode the CEO's own ruling already rejected.

Keeping BOTH an ambiguous-sounding `Outcome` AND a new `PositionOutcome` side by side (Option (c) without
the (b) rename) was considered and rejected here as well: two types that could both plausibly be mistaken
for "the result" at the same terminal moment is arguably a WORSE accidental-misinterpretation risk than one
honestly-narrow name plus one canonically-complete name.

### Files that would be modified (if this recommendation is authorized)

`context_memory/contracts.py` (rename existing `Outcome`→ new name, throughout; add new `PositionOutcome`
+ `PositionOutcomeId`), `context_memory/identities.py` (rename existing canonical/id functions; add new
ones for `PositionOutcome`), `context_memory/repository.py` (rename existing stream file/methods if the
rename is literal; add a new `position_outcomes.jsonl` stream + `append_position_outcome`/
`get_position_outcome`/`iter_position_outcomes`/`count_position_outcomes`), `learning_feedback/adapters.py`
(rename existing `build_*_outcome` functions; add new `build_*_position_outcome` functions consuming an
accumulated partial list), `learning_feedback/capture.py` (`PendingPosition` gains accumulation state; new
capture functions for `PositionOutcome`, alongside renamed existing ones), every existing test file
referencing the renamed type (`test_adapters.py`, `test_capture.py`, `test_outcome.py`,
`test_public_api.py`, fixtures in `decision_intelligence_v2/tests/_fixtures.py` if they construct `Outcome`
directly).

### Frozen modules affected / not affected

None affected — entirely within `learning_feedback`/`context_memory`, both fully owned by this Sprint. No
change to Flow A, `harness.py`, `portfolio_simulator.py`, `execution_simulator.py`, `shadow_evidence/`, or
`evidence.py`/`retrieval.py` (the new type remains excluded from evidence aggregation, exactly like
`InterimRealization` and `OperationalMetadata`, unless a future, separately-authorized phase decides
otherwise).

### Mandatory tests

Full contract/identity/codec/repository test suite for `PositionOutcome` (new); mechanical rename
verification for the existing per-fill type across every referencing test file, with zero behavioral change
proven (same numeric results, same construction rules, only the name/identifiers differ); aggregation
determinism and edge-case tests for `PositionOutcome` (single-partial continuity proof, flip-boundary proof,
multi-partial weighted-exit-price correctness, constituent-reference completeness); an explicit
double-counting-guard test/documented contract for `PositionOutcome` + `InterimRealization` never being
summed together.

### Exact acceptance criterion

No type in the repository is named or shaped in a way that could be mistaken for "the complete position
result" while actually representing only its last fill. `PositionOutcome` exists as the one, unambiguous,
persisted, deterministic Level-1 accounting record per `position_key`, computed exactly once, with an
explicit, auditable link to every constituent `InterimRealization`; the renamed per-fill type's own
docstring makes its narrower scope explicit; and a passing test suite proves both the rename's zero
behavioral impact and the new aggregate's own correctness, including the single-partial continuity
guarantee and the flip-boundary guarantee.

---

## Blocker 3 — Full lifecycle and cleanup for `CorrelationMap`

### Exact problem

`CorrelationMap` (`learning_feedback/capture.py`, client-order-id-keyed, the decision-time bridge to a
position's own opening fill) has no cleanup path for a candidate that is registered (an ALLOW decision) but
never reaches a fill: the order is subsequently REJECTED (validation- or broker-level), CANCELLED, or
EXPIRES (TIF) before filling. `pop_for_resolution` is only ever invoked by `promote_opening_fill` when the
position registry detects a birth — a rejected/cancelled/expired order never produces one. These entries
persist in `CorrelationMap._pending` for the entire run, unbounded, with no signal that they exist and
never resolved (`PositionCorrelationMap`, the position-key-level layer, already has `drain_pending()` for
exactly this purpose at the `HOLD_AND_MARK` end-of-run point — `CorrelationMap` has no equivalent).

### Existing contracts involved

`CorrelationMap`/`PendingCapture` (`learning_feedback/capture.py:99-158`) — `register_decision`,
`pop_for_resolution`, `is_pending`, `is_resolved`, `pending_count`; no `discard`/`drain_pending`.
`OrderStatus`/`OrderState` (`execution_engine/types.py`) — `status.state` is already returned
SYNCHRONOUSLY by `execution_engine.execute()`, already read in `harness.py` immediately (`status =
self._execution_engine.execute(decision, portfolio_state)`) — the REJECTED/FAILED case is therefore
already visible for free at the exact call site `register_pending_correlation` is invoked from today.
`ExecutionEngine.cancel()` (`execution_engine/engine.py:190-213`) — never called from `harness.py` (Phase F
Integration Design's own finding); CANCELLED is unreachable in practice today. `WorkingOrderState.EXPIRED`
(`simulation/types.py`) — computed inside `execution_simulator.py`, never surfaced to `harness.py`'s own
per-bar loop (`advance_bar()` returns only `fills`, no terminal-non-fill event stream) — a genuine
execution-layer gap, not a `learning_feedback` gap, already flagged in
`LEARNING_FEEDBACK_PHASE_F_INTEGRATION_DESIGN.md`.

### Architectural options

**A. Synchronous rejection handling + end-of-run `drain_pending()`.**
- Rejection (already visible synchronously): check `status.state` immediately after `execute()`; if it
  indicates immediate rejection/failure, never call `register_pending_correlation` for that decision at
  all (simpler than registering-then-discarding, since the outcome is already known before registration
  would happen).
- Cancellation/expiry (not currently surfaced to `harness.py` at all): bound, not solved in real time —
  add `CorrelationMap.drain_pending()` (mirroring `PositionCorrelationMap`'s own existing method) called
  once at `_finalize_at_end`, guaranteeing no candidate survives past the end of a single run, and that
  every such candidate is at least COUNTED/reported at drain time (not silently lost).
- Files changed: `learning_feedback/capture.py` (`CorrelationMap.drain_pending()`, and optionally
  `discard()` for symmetry/direct use), `simulation/harness.py` (check `status.state` before registering;
  call `drain_pending()` at `_finalize_at_end`).
- Frozen modules affected: none.
- Advantages: closes the unbounded-growth risk completely (bounded to one run's own memory footprint,
  guaranteed reclaimed and reported at end-of-run); zero risk to `execution_simulator.py`/`execution_
  engine.py`; the rejection case is handled with genuinely less code than originally anticipated (skip
  registration, not register-then-discard).
- Risks: does not provide TIMELY (mid-run) observability for cancellation/expiry — a candidate that
  expires on bar 50 of a 10,000-bar run is only ever accounted for at the very end, not when it actually
  happened. Acceptable for correctness (no leak, no wrong data) but not for real-time audit granularity.

**B. Full timely observability via an execution-layer change.**
- Requires `execution_simulator.py`'s `advance_bar()` (or a new `ExecutionEngine`/`ExecutionSimulator`
  query method) to additionally surface orders that transitioned to a terminal, non-fill state THIS bar —
  a new return value or a new queryable surface.
- Files changed: `simulation/execution_simulator.py`, `execution_engine/engine.py` (and their own existing
  test suites), plus `learning_feedback/capture.py`/`harness.py` to consume the new signal.
- Frozen modules affected: **`execution_simulator.py`/`execution_engine/engine.py`** — genuinely frozen,
  real-money-adjacent simulation core modules this entire Sprint (across every phase) has never touched,
  materially larger and riskier than anything done so far.
- Advantages: real-time cleanup and full audit granularity (a candidate's fate is known and recorded the
  same bar it happens).
- Risks: the largest, riskiest change of any option across all three blockers in this document; touches
  modules shared with the REAL, live-money-adjacent execution path, not just diagnostic capture; would
  need its own, separately-gated design review given the blast radius, independent of Learning Feedback's
  own scope.

**C. Hybrid — implement A now; formally, explicitly defer B to a separate, future, execution-layer-focused
Sprint with its own dedicated design review, never bundled into Learning Feedback's own scope.**

### Recommendation

**Option C.** Implement A in full now (closes the actual risk — unbounded memory growth and silent,
un-auditable loss — completely, with zero frozen-module risk), and explicitly record B as out of scope for
Learning Feedback, a genuinely separate execution-layer initiative requiring its own authorization and
review given it touches `execution_simulator.py`/`execution_engine.py` directly. Bundling B into this
Sprint would import a much larger risk surface for a benefit (real-time vs. end-of-run observability) that
does not change correctness, only audit timeliness.

### Files that would be modified (if A/C is authorized)

`learning_feedback/capture.py` (`CorrelationMap.drain_pending()`, optionally `discard()`),
`simulation/harness.py` (rejection check before registration; `drain_pending()` call in
`_finalize_at_end`). B, explicitly deferred, would touch `simulation/execution_simulator.py` and
`execution_engine/engine.py` — not modified under this recommendation.

### Frozen modules affected / not affected

Not affected (under the recommended A/C scope): `execution_simulator.py`, `execution_engine/`,
`portfolio_simulator.py`, `risk_manager/`, Flow A. Would be affected only under the explicitly-deferred
Option B, which this recommendation does not propose for this Sprint.

### Mandatory tests

Unit tests for `CorrelationMap.drain_pending()`/`discard()` (mirroring the already-existing
`PositionCorrelationMap` test patterns in `test_capture.py`); a harness-level (or direct, no-harness) test
proving a synchronously-rejected decision never enters `CorrelationMap` at all; an end-of-run test proving
`drain_pending()` empties the map completely with no fabricated `Outcome`, mirroring the already-existing
`HOLD_AND_MARK` test pattern for `PositionCorrelationMap`.

### Exact acceptance criterion

`CorrelationMap.pending_count() == 0` at the end of every run, proven by a test, accounting for the full
union of dispositions: resolved via promotion to a `position_key`, never registered at all (immediate
rejection), or drained at end-of-run (cancelled/expired, never surfaced mid-run) — no candidate may
silently persist beyond one run's own lifetime. Plus an explicit, written CEO acknowledgment that real-time
(mid-run) observability for cancellation/expiry is deliberately out of scope for this Sprint and deferred
to a separate, future execution-layer initiative.

---

## Cross-cutting notes (informational, not a fourth blocker)

- Blocker 1 is the only one of the three that would touch a module outside `learning_feedback`/
  `context_memory`/`harness.py` (`shadow_evidence/engine.py`/`types.py`) — this is the first time in the
  entire Learning/Research Feedback initiative that a module other than `harness.py` itself would need
  modification, and should be reviewed with that in mind.
- Blockers 2 and 3 are both fully containable within already-owned Sprint scope, zero frozen-module risk,
  under their recommended options.
- None of the three recommended options require touching Flow A, `context_memory/evidence.py`,
  `context_memory/retrieval.py`, `portfolio_simulator.py`, or `execution_simulator.py`/`execution_engine/`
  (the last two explicitly and deliberately deferred for Blocker 3's Option B).

No implementation, refactor, or new subject was undertaken to produce this document. Awaiting review and
explicit authorization before any of the above is built.
