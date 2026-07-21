# IMPLEMENTATION_DEFINITION_OF_DONE.md — Mandatory Phase-Gate Checklist (Flow B roadmap step 3/6)

**Status: ACCEPTANCE CRITERIA ONLY. No code written, no code modified, nothing committed to
`ai_trader/`.** Companion to `LEARNING_RESEARCH_FEEDBACK_DESIGN.md` (Normative Model, commit `b150f1e`),
`LEARNING_RESEARCH_FEEDBACK_IMPLEMENTATION_PLAN.md` (commit `d8265fa`), and
`IMPLEMENTATION_EXECUTION_PLAN.md` (commit `bb0dd79`). This document does not redesign the architecture,
introduce new phases, or change the approved phase sequence (A → B → C → D → E → F → G-optional). It
defines the objective, verifiable completion criteria each phase must satisfy before being accepted.
**Implementation has not begun. No phase may start without its own separate, explicit CEO
authorization.**

---

## Mandatory global rules

1. **Only one phase may be implemented at a time.** Never begin a phase before the prior one is accepted.
2. **Stop after every phase.** Report per §10 of that phase, then wait.
3. **No subsequent phase may begin without explicit CEO approval** — a passing phase is not
   self-authorizing.
4. **A passing test suite is necessary but not sufficient.** Every other acceptance criterion (scope,
   non-scope, repository-state, evidence) must also hold.
5. **No unrelated cleanup or refactoring is allowed** in any phase — touch only what that phase's own
   scope names.
6. **Flow A must remain untouched** in every phase, verified every time, not assumed.
7. **Existing behavior must remain unchanged until Phase F explicitly activates the feature** — Phases
   A–E must have zero observable runtime effect.
8. **Phase F must remain opt-in and off by default.**
9. **Phase G remains optional and must not be started automatically** — it requires its own explicit
   authorization exactly like every other phase, never assumed to follow F.
10. **Any discovered architectural contradiction stops implementation and must be reported, never
    silently resolved** — this applies to a contradiction found in this document, the design, the
    implementation plan, or the execution plan, at any point during any phase.

---

## Phase A — Context Memory: new, independent types

### 1. Scope
Add `OutcomeKind` (`STRATEGY`/`PORTFOLIO`), the new `SourceType.REAL_PORTFOLIO_LEDGER` member,
`OperationalMetadata`/`OperationalMetadataId`, `identities.py::compute_operational_metadata_id`, and
`repository.py::append_operational_metadata`/`append_operational_metadatas`.

### 2. Explicit non-scope
`Outcome`'s own shape (deferred to Phase B — do not add `outcome_kind` to `Outcome` in this phase).
`evidence.py` (Phase C). Anything in `ai_trader/learning_feedback/` (Phases D/E). `harness.py` (Phase F).
Any existing test fixture. Any file outside `context_memory/`.

### 3. Required deliverables
- `context_memory/enums.py`: `OutcomeKind` enum; `SourceType.REAL_PORTFOLIO_LEDGER` member.
- `context_memory/contracts.py`: `OperationalMetadata` dataclass + `OperationalMetadataId`, with
  `__post_init__` enforcing "DENY requires a reason code, ALLOW must not carry one."
- `context_memory/identities.py`: `compute_operational_metadata_id`.
- `context_memory/repository.py`: `append_operational_metadata` + batch variant, new backing JSONL file.
- `context_memory/tests/test_operational_metadata.py` (new).

### 4. Acceptance criteria
- All 4 new files/additions above exist exactly as scoped — no more, no less.
- `Outcome`, `evidence.py`, `retrieval.py`, `index.py`, `episodes.py`, `codec.py` show zero diff.
- Every EXISTING `context_memory/` test passes unmodified.
- New `OperationalMetadata` construction round-trips through `append_operational_metadata` and is
  retrievable in an equivalent form (content-addressed ID stable across repeated construction with
  identical inputs).

### 5. Required tests
- **Unit**: `OperationalMetadata` construction (valid ALLOW, valid DENY, invalid ALLOW-with-reason,
  invalid DENY-without-reason); `compute_operational_metadata_id` determinism (same input → same ID,
  different input → different ID).
- **Integration**: `append_operational_metadata`/batch round-trip against a real repository instance.
- **Regression**: full existing `context_memory/` suite, unmodified, must stay green.
- **Negative**: constructing `OperationalMetadata` with an invalid ALLOW/DENY + reason-code combination
  must raise, not silently accept.
- **Invariant**: N/A beyond the above (no cross-type invariant exists yet in this phase — that is
  Phase B).

### 6. Static validation
- Type checking: mypy over the 4 modified/new files (if the environment's own Application Control
  policy still blocks mypy's native DLL — a pre-existing, disclosed, unrelated limitation from prior
  roadmap steps — this must be re-disclosed, not silently skipped or hidden).
- Imports: `OperationalMetadata`'s own fields must use only local, package-internal types, no
  cross-package import of `risk_manager`/`strategy_health` types directly (mirrors `enums.py`'s own
  "local mirror" rationale — the actual `ContextRiskDecision` mirror enum is introduced in this phase or
  Phase A, per the Implementation Plan §2; if introduced here, it must be a local enum, never an import
  of `risk_manager.types.Decision`).
- Schema validation: `__post_init__` invariants exercised by the negative tests above.
- Serialization compatibility: `OperationalMetadata` must round-trip through `codec.py`'s own existing
  (de)serialization mechanism without modification to `codec.py` itself, if `codec.py` is generic over
  dataclass shape; if it is NOT generic and requires its own per-type touch, this is a discovered
  contradiction with the Implementation Plan's own file list (§9/global rule 10) — stop and report,
  do not silently extend `codec.py` beyond what was planned.

### 7. Runtime validation
**Not required.** Nothing in this phase is reachable from any live or simulated harness run — purely
isolated, test-exercised code.

### 8. Repository-state validation
- Working tree clean immediately before and after the phase's own commit.
- Only the files listed in §3 changed — `git status --porcelain` confirms no unrelated file appears.
- Flow A zero-diff: `git status --porcelain -- NEXT_SESSION_FLOW_A.md edge_research
  EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md EDGE_DISCOVERY_ROADMAP.md` empty.
- No unauthorized Flow B changes: no file outside `context_memory/` and its own tests changed.
- Exactly one phase-specific commit exists for Phase A.

### 9. Failure conditions
- **Reject** if any existing `context_memory/` test fails, or any file outside the scoped list changed.
- **Rollback** if `Outcome`'s own shape was touched (scope violation — belongs to Phase B).
- **Stop implementation, report, await CEO review** if `codec.py` requires a per-type touch not
  anticipated by the Implementation Plan (a discovered contradiction, global rule 10).

### 10. Evidence required for CEO acceptance
Files changed (exact list); tests executed and their pass/fail counts; full test output for the new
`test_operational_metadata.py`; confirmation of zero diff on `Outcome`/`evidence.py`/`harness.py`;
commit hash; one-paragraph diff summary; remaining risks (if any); explicit confirmation that Phase B
has not started.

---

## Phase B — `Outcome.outcome_kind` field, validation, and existing fixture updates

### 1. Scope
Add the required `outcome_kind: OutcomeKind` field to the existing `Outcome` dataclass; add the
kind/source `__post_init__` compatibility validation; update every existing `Outcome(...)` construction
site to supply the new field, in the SAME commit.

### 2. Explicit non-scope
`evidence.py` (Phase C — do not add kind-awareness to it in this phase, even though it will need it).
`ai_trader/learning_feedback/` (Phases D/E). `harness.py` (Phase F). Any field other than `outcome_kind`
on `Outcome`. Any other existing type's shape.

### 3. Required deliverables
- `context_memory/contracts.py`: `Outcome.outcome_kind: OutcomeKind` field + `__post_init__` validation
  enforcing exactly `{(STRATEGY, SHADOW_EVIDENCE_ADAPTER), (PORTFOLIO, REAL_PORTFOLIO_LEDGER)}` as the
  only valid pairs.
- Updated, in the same commit: every `Outcome(...)` construction in
  `context_memory/tests/_fixtures.py`, `context_memory/tests/test_outcome.py`,
  `decision_intelligence_v2/tests/_fixtures.py`.
- Extended `context_memory/tests/test_outcome.py`: valid-pair and invalid-pair construction tests.
- **Verify-only** (per the Implementation Plan §0 OPTIONAL list): inspect `context_memory/validation.py`
  for any independent re-validation of `Outcome`'s own shape; extend ONLY if found — do not add
  speculative validation logic there if none already exists.

### 4. Acceptance criteria

**Special attention — mandatory atomicity requirement, checked first**: the field addition and every
affected fixture/constructor update must land in exactly one commit. The repository must never be
committed in a state where `outcome_kind` is a required field but any existing `Outcome(...)` call site
has not been updated to supply it — this would leave the build broken between commits, violating global
rule 7 (existing behavior unchanged) at the test-suite level even before Phase F. If, during
implementation, the full set of affected call sites cannot be identified and fixed in one sitting, the
phase is NOT done — do not commit a partial state.

- `Outcome.outcome_kind` exists and is required (no default value).
- Every one of the two currently-valid `(OutcomeKind, SourceType)` pairs constructs successfully; every
  other pairing raises at `__post_init__`.
- Every EXISTING `context_memory/`, `decision_intelligence_v2/`, and `decision_comparison/` test passes,
  in full, with zero change to their own assertions or logic — only their `Outcome(...)` calls gained
  one argument.
- `evidence.py`, `retrieval.py`, `harness.py`, and everything in `ai_trader/learning_feedback/` (if it
  exists yet from a later phase) show zero diff.

### 5. Required tests
- **Unit**: both valid pairs construct; representative invalid pairs (e.g. `(PORTFOLIO,
  SHADOW_EVIDENCE_ADAPTER)`, `(STRATEGY, REAL_PORTFOLIO_LEDGER)`) each raise.
- **Regression**: full existing `context_memory/`, `decision_intelligence_v2/`, `decision_comparison/`
  suites, unmodified logic, must pass.
- **Negative**: an invalid pairing must raise a clear, specific error — not a generic/silent failure.
- **Invariant**: the existing `Outcome` invariants (`RESOLVED` requires `normalized_result`/
  `resolution_as_of` set; `PENDING`/`INVALID`/`UNAVAILABLE` behavior) must be re-confirmed unaffected by
  the new field's own addition.

### 6. Static validation
- Type checking: mypy over `contracts.py` and the three updated fixture/test files (same disclosed
  limitation as Phase A if still blocked).
- Imports: no new imports required beyond `OutcomeKind` itself (already added in Phase A).
- Schema validation: the kind/source `__post_init__` check, exercised by §5's negative tests.
- Serialization compatibility: any EXISTING persisted/serialized `Outcome` fixture data (if any exists in
  test golden files) must be checked for compatibility with the new required field — if none exists,
  state this explicitly rather than silently assume it.

### 7. Runtime validation
**Not required.** Still zero production callers write real `Outcome` data.

### 8. Repository-state validation
Same 5-point check as Phase A (§8 pattern), scoped to Phase B's own file list. Exactly one phase-specific
commit for Phase B.

### 9. Failure conditions
- **Reject** if the commit ever leaves any existing test broken, even transiently within the same PR's
  own history (must be one atomic commit, per §4 above).
- **Reject** if any fixture/test file outside the three named ones needed updating and was missed —
  re-scan before declaring done.
- **Stop, report, await CEO review** if `validation.py` is found to require MORE than a mechanical
  extension (e.g. if it encodes its own independent business logic about `Outcome`'s shape that
  contradicts `contracts.py`'s own new invariant) — a discovered contradiction, global rule 10.

### 10. Evidence required for CEO acceptance
Exact files changed; full regression test output (`context_memory/`, `decision_intelligence_v2/`,
`decision_comparison/`); new validation test results; commit hash; diff summary; confirmation
`validation.py` was inspected and either left untouched or extended (state which, and why); remaining
risks; confirmation Phase C has not started.

---

## Phase C — `evidence.py` kind-awareness

### 1. Scope
Add a required `outcome_kind: OutcomeKind` parameter to `aggregate_evidence` and
`aggregate_all_present_edges`; make their internal per-episode Outcome lookup filter by it.

### 2. Explicit non-scope
`retrieval.py`/`index.py`/`episodes.py` (confirmed not required — they operate on `ContextSnapshot`/
`Observation`, never on `Outcome` directly). Anything in `ai_trader/learning_feedback/`. `harness.py`.
Any change to `evidence.py`'s own statistical formulas (win rate, mean/median result,
`evidence_consistency`, confidence interval) beyond adding the kind filter itself.

### 3. Required deliverables
- `context_memory/evidence.py`: both public functions gain the required `outcome_kind` parameter (no
  default — callers must state intent); internal Outcome-selection logic filters to it.
- `context_memory/tests/test_evidence.py` (extended): new tests per §4 below.

### 4. Acceptance criteria

**Special attention — mandatory cross-kind isolation proof, checked first**: prove directly, with both
outcome kinds present in the same context/episode, that `evidence.py` cannot aggregate Strategy and
Portfolio outcomes into the same statistic. Minimum required test: construct one `Observation`/episode
with BOTH a `(STRATEGY, SHADOW_EVIDENCE_ADAPTER)` Outcome and a `(PORTFOLIO, REAL_PORTFOLIO_LEDGER)`
Outcome attached; call `aggregate_evidence(..., outcome_kind=STRATEGY)` and confirm the returned
statistics reflect ONLY the Strategy-kind row; call again with `outcome_kind=PORTFOLIO` and confirm ONLY
the Portfolio-kind row is reflected; assert the two calls' own results differ (proving the filter is
load-bearing, not a no-op) when the two kinds' underlying values are engineered to differ.

- Both public functions require `outcome_kind` — omitting it is a `TypeError`, not a silent default.
- The cross-kind isolation proof (above) passes.
- Every existing `evidence.py` test (extended to pass the new required parameter, never removed) passes.
- No confirmed production caller of `aggregate_evidence`/`aggregate_all_present_edges` exists outside
  this module's own test suite — re-verified by a fresh grep at implementation time, not assumed from
  the design/planning passes.

### 5. Required tests
- **Unit**: kind filter selects the correct subset for a single-kind episode (trivial case).
- **Integration**: the dual-kind cross-isolation proof (§4) — the load-bearing test for this entire
  phase.
- **Regression**: full existing `evidence.py` test suite, extended only to add the now-required
  parameter, never with removed or weakened assertions.
- **Negative**: omitting `outcome_kind` raises; passing an outcome_kind with zero matching rows returns
  the SAME degenerate/`UNAVAILABLE`-shaped report the module already returns for "no evidence," never a
  crash.
- **Invariant**: statistics computed under `outcome_kind=STRATEGY` must be mathematically independent of
  how many Portfolio-kind rows exist for the same episode (adding/removing Portfolio rows must not
  change the Strategy-kind aggregation's own numbers at all).

### 6. Static validation
Type checking (mypy, same disclosed limitation); imports (no new external imports); schema validation
N/A (no new dataclass in this phase); serialization compatibility N/A (no new persisted shape).

### 7. Runtime validation
**Not required.** Still zero production callers/writers of real Outcome data.

### 8. Repository-state validation
Same 5-point pattern, scoped to `evidence.py` + its own test file. Exactly one phase-specific commit.

### 9. Failure conditions
- **Reject** if the dual-kind isolation proof (§4) fails, or is missing.
- **Reject** if a confirmed production caller of either function is found and not updated to pass
  `outcome_kind` explicitly in the same commit.
- **Stop, report, await CEO review** if updating the signature reveals `evidence.py`'s own internal
  Outcome-selection logic cannot be cleanly filtered by kind without touching its statistical formulas
  (a discovered contradiction with the Implementation Plan's own §3.5 scoping) — do not silently expand
  scope to "fix" this.

### 10. Evidence required for CEO acceptance
Exact files changed; the dual-kind isolation test's own output; full `evidence.py` regression results;
confirmation of the fresh-grep production-caller check and its result; commit hash; diff summary;
remaining risks; confirmation Phase D has not started.

---

## Phase D — `ai_trader/learning_feedback/` adapters (pure, unwired)

### 1. Scope
`build_strategy_outcome`, `build_portfolio_outcome`, `build_operational_metadata` (pure functions);
`LearningFeedbackConfig` type.

### 2. Explicit non-scope
`capture.py`/any orchestration logic (Phase E). `harness.py` (Phase F). Any change to
`context_memory/`, `shadow_evidence/`, `risk_manager/`, `strategy_health/` — these are read-only inputs
to the adapters, never modified.

### 3. Required deliverables
- `ai_trader/learning_feedback/__init__.py`, `adapters.py`, `config.py`.
- `ai_trader/learning_feedback/tests/__init__.py`, `test_adapters.py`.

### 4. Acceptance criteria
- Each adapter is a pure function: no I/O, no side effects, no wall-clock/randomness reads.
- `build_strategy_outcome` returns `None` (not raises) for an unresolved position or missing
  `aggregate_net_pnl` — confirmed by test.
- `build_operational_metadata` produces output that satisfies `OperationalMetadata`'s own
  `__post_init__` invariant (Phase A) for both ALLOW and DENY inputs.
- Zero diff anywhere outside the new package.

### 5. Required tests
- **Unit**: happy path for each of the three adapters; skip/`None` path for `build_strategy_outcome`;
  DENY-with-reason and ALLOW-without-reason paths for `build_operational_metadata`.
- **Negative**: attempting to build an `Outcome` with a mismatched kind/source pair (if the adapter's
  own signature makes this possible to attempt) must raise via the Phase B validation it delegates to,
  not silently succeed.
- Integration/regression/invariant: **not applicable** — nothing existing is touched, nothing else
  consumes this code yet.

### 6. Static validation
Type checking (mypy, same disclosed limitation); imports (adapters may import from
`context_memory`, `shadow_evidence`, `risk_manager`, `simulation.portfolio_simulator` read-only types,
but must not import anything from `ai_trader.simulation.harness` itself — no circular dependency back
into the orchestrator this package will eventually be wired into); schema validation N/A; serialization
N/A (adapters return in-memory dataclasses, they do not serialize anything themselves — that remains
the repository's own job).

### 7. Runtime validation
**Not required.** Nothing in production calls this package yet.

### 8. Repository-state validation
Same 5-point pattern, scoped to the new `ai_trader/learning_feedback/` files only. Exactly one
phase-specific commit.

### 9. Failure conditions
- **Reject** if any adapter has a side effect, reads wall-clock time, or uses randomness.
- **Reject** if any existing package outside `ai_trader/learning_feedback/` shows any diff.
- **Stop, report, await CEO review** if building a correct `build_strategy_outcome` reveals that
  `ShadowTradeLegRecord.leg.pnl_r` is NOT reliably populated for every closed Shadow position — the
  open detail flagged in the Implementation Plan §9 — rather than silently inventing a fallback
  normalization not previously specified.

### 10. Evidence required for CEO acceptance
Exact files changed; full new test suite output; confirmation of zero diff elsewhere; commit hash; diff
summary; resolution (or open status) of the `pnl_r` availability question; remaining risks;
confirmation Phase E has not started.

---

## Phase E — `ai_trader/learning_feedback/capture.py` (orchestration, unwired)

### 1. Scope
The two write-path entry functions (decision-time capture, resolution-time capture) and the run-scoped
`(strategy_id, symbol, entry_as_of) → observation_id` correlation map.

### 2. Explicit non-scope
`harness.py` — this phase's own code must not be called from anywhere in the harness yet. Any change to
Phase D's own adapters (consumed, not modified).

### 3. Required deliverables
- `ai_trader/learning_feedback/capture.py`.
- `ai_trader/learning_feedback/tests/test_capture.py`.

### 4. Acceptance criteria
- Correlation-map hit path: a resolution event with a matching prior decision-time entry produces a
  correctly-linked `Outcome`.
- Correlation-map miss path: a resolution event with NO matching entry is dropped and logged, never
  fabricates a placeholder `Observation`/`observation_id`.
- Every failure-handling rule from the Implementation Plan §11 is exercised by a test (missing/degraded
  Market Intelligence data → skip, not fabricate; unexpected exception → caught, never propagates).
- Zero diff anywhere outside the new package.

### 5. Required tests
- **Unit**: correlation-map insert/lookup/miss in isolation.
- **Integration**: end-to-end capture call using directly-constructed Shadow/Risk Manager/Portfolio
  Simulator fixture objects (no harness), confirming the correct sequence of `append_*` calls.
- **Negative**: the miss path (§4) and the malformed/degraded-input path both degrade safely, never
  raise out of the capture function itself.
- Regression/invariant: **not applicable** beyond Phase D's own adapters being reused unmodified.

### 6. Static validation
Type checking (mypy, same disclosed limitation); imports (no import of `ai_trader.simulation.harness`
itself, same discipline as Phase D); schema N/A; serialization N/A.

### 7. Runtime validation
**Not required.** Not yet reachable from any harness run.

### 8. Repository-state validation
Same 5-point pattern, scoped to `capture.py` + its own test file. Exactly one phase-specific commit.

### 9. Failure conditions
- **Reject** if any exception can escape the capture functions themselves under a malformed/missing
  input — this must be proven by test, not asserted.
- **Reject** if the miss path ever fabricates an `Observation`/ID rather than dropping and logging.
- **Stop, report, await CEO review** if the correlation-map design is found, during implementation, to
  require persisting state ACROSS runs (contradicting the design's own "run-scoped, in-memory only,
  never persisted" property) — a discovered contradiction, global rule 10.

### 10. Evidence required for CEO acceptance
Exact files changed; full new test suite output; confirmation every failure-handling rule has its own
passing test; commit hash; diff summary; remaining risks; confirmation Phase F has not started.

---

## Phase F — `harness.py` wiring (feature goes live, opt-in)

### 1. Scope
The new, additive `learning_feedback_config: LearningFeedbackConfig | None = None` constructor
parameter; two new call sites in `_run_one_bar` (decision-time, resolution-time), gated by `is not None`.

### 2. Explicit non-scope
Any change to the existing per-bar loop's own order, gate logic, or any other module's own behavior.
Any change to `strategy_id_filter`, `health_eligible_ids`, or `portfolio_architect_config`'s own existing
semantics. Wiring `decision_intelligence_v2`'s `context_memory_index` into `harness.py` (explicitly
deferred, per the Implementation Plan §0 — this phase does NOT do that).

### 3. Required deliverables
- `ai_trader/simulation/harness.py`: the one new constructor parameter, two new call sites, matching the
  exact convention of every prior touch (docstring paragraph explaining the parameter, plain attribute
  storage, `is None` short-circuit when disabled).
- `ai_trader/simulation/tests/test_learning_feedback_integration.py` (new).

### 4. Acceptance criteria

**Special attention — the stricter acceptance criteria this phase requires.** Because `harness.py` is the
shared orchestrator and the feature becomes operational here, all of the following must be independently
demonstrated, not merely asserted:

- **Opt-in behavior**: the feature only activates when `learning_feedback_config` is explicitly supplied
  and non-`None`.
- **Off-by-default behavior**: omitting the parameter entirely behaves identically to passing `None`
  explicitly.
- **No behavior change when disabled**: byte-identical competitive execution (fingerprint comparison,
  the same method used for every prior touch) between `learning_feedback_config=None` and the parameter
  omitted entirely, AND between this version of `harness.py` and the pre-Phase-F version, over the same
  fixture window used by every prior touch this session.
- **Idempotent writes**: re-processing the same bar's own data (if ever replayed) produces the same
  content-addressed IDs, never duplicate rows — inherited from the repository's own existing guarantee
  (Implementation Plan §10), re-confirmed here at the integration level, not re-implemented.
- **Duplicate prevention**: no `Observation`/`Outcome`/`OperationalMetadata` is ever appended twice for
  the conceptually same event within one run.
- **Correct decision-time capture**: a real bar with an actionable candidate set produces a real
  `Observation` (+ `PresentEdgeReference`s) and the corresponding `OperationalMetadata` for every
  strategy Risk Manager actually evaluated that bar.
- **Correct resolution-time capture**: both the Shadow-position-closure trigger and the real-trade-closure
  trigger are independently exercised and produce correctly-linked outcomes.
- **Absence of Portfolio Outcome when no real trade exists**: a bar (or an entire fixture window) with
  zero real trades produces zero Portfolio Outcome rows — never a fabricated `UNAVAILABLE` placeholder.
- **Strategy Outcome sourced from Shadow Evidence**: directly verified by inspecting the constructed
  `Outcome.source_type == SHADOW_EVIDENCE_ADAPTER` for every Strategy-kind row.
- **Portfolio Outcome sourced from the real ledger**: directly verified,
  `Outcome.source_type == REAL_PORTFOLIO_LEDGER` for every Portfolio-kind row.
- **Preservation of OperationalMetadata**: every `RiskDecision` this bar has a corresponding
  `OperationalMetadata` row, correctly reflecting ALLOW/DENY + reason + rejection stage +
  `PolicyState` at that `as_of`.
- **Failure isolation**: an injected exception inside the capture path (test-only fault injection) must
  never propagate into or alter the real competitive run's own outcome.
- **End-of-run finalization**: any position still open at run end (handled today by `CLOSE_AT_END`
  policy) produces a genuine, non-fabricated Outcome from whatever `CLOSE_AT_END` actually produces, or
  is correctly left unresolved if the run terminates before any resolution.
- **Regression safety for existing harness behavior**: the full existing harness-level regression suite
  (below) passes unmodified.

### 5. Required tests
- **Unit**: N/A at this layer (covered by Phases D/E).
- **Integration**: every bullet in §4 above, each as its own dedicated test.
- **Regression**: `context_memory/` (full), `decision_intelligence_v2/` (full, proving its own
  recommendation-equality invariant still holds untouched), `strategy_health/` (full),
  `portfolio_architect/` (full), `test_shadow_disabled_parity.py` (the 43-strategy parity suite, since
  `harness.py` is touched again), `test_health_eligible_ids.py`, `test_portfolio_architect_passthrough.py`
  — all re-run unmodified.
- **Negative**: fault-injection into the capture path (failure isolation, §4) must not alter the
  competitive outcome.
- **Invariant**: aggregate ALLOW count and the full trade ledger are identical whether
  `learning_feedback_config` is `None` or a real config — mirrors the exact proof convention already
  established for `health_eligible_ids` and `portfolio_architect_config`.

### 6. Static validation
Type checking (mypy, same disclosed limitation); imports (no new circular dependency — `harness.py` may
import from `ai_trader.learning_feedback`, never the reverse); schema validation N/A (no new type in
this phase); serialization compatibility re-confirmed end-to-end (a real harness run's own appended
rows round-trip through the repository correctly).

### 7. Runtime validation
**Required, and the primary purpose of this phase.** A real, full harness run (same fixture-scale
convention as every prior touch — the proven 4-strategy or 43-strategy window) must demonstrate every
bullet in §4, not merely pass isolated unit tests.

### 8. Repository-state validation
Same 5-point pattern, scoped to `harness.py` + its own new test file. Exactly one phase-specific commit.
Given this phase's own higher risk, the pre-commit diff must be inspected line-by-line to confirm it
contains ONLY the one new parameter and the two new call sites — no incidental change to any existing
line.

### 9. Failure conditions
- **Reject and rollback immediately** if the byte-identical-when-disabled proof (§4) fails in any way —
  this is non-negotiable, matching every prior touch's own zero-tolerance standard.
- **Reject** if any regression suite in §5 fails.
- **Reject** if the pre-commit diff contains any change beyond the scoped parameter/call sites.
- **Stop, report, await CEO review** if achieving correct decision-time/resolution-time capture is found
  to require reordering any EXISTING call in `_run_one_bar` beyond inserting the two new ones at their
  already-planned points (§8 of the Implementation Plan) — any reordering of existing logic is a
  discovered contradiction with this phase's own non-scope, not a routine implementation detail.

### 10. Evidence required for CEO acceptance
Exact files changed; the full byte-identical-when-disabled proof output; results for every §4 bullet's
own dedicated test; full regression suite results (every suite named in §5, pass/fail counts); commit
hash; line-by-line diff summary of `harness.py` itself; remaining risks (explicitly including anything
still open from Phase D's `pnl_r`-availability question if unresolved); confirmation Phase G has not
started and was not authorized.

---

## Phase G (OPTIONAL) — operational polish

### 1. Scope
Structured logging/metrics for Learning's own write volume and failure/drop counts.

### 2. Explicit non-scope
Any behavior change. Any new decision-relevant data. Any change to what is written to Context Memory —
this phase only observes and reports on Phase F's own already-defined behavior.

### 3. Required deliverables
Additive logging calls inside `ai_trader/learning_feedback/capture.py` only.

### 4. Acceptance criteria
Logging calls do not raise; do not alter control flow; do not change any appended record's own content.

### 5. Required tests
Unit: logging calls execute without raising, under both success and failure/drop paths. Nothing else
applicable — no behavior exists to regress.

### 6. Static validation
Type checking (mypy, same disclosed limitation); imports (logging library only, no new dependency).

### 7. Runtime validation
Not required beyond confirming log output appears during a normal Phase F run (informal, not a
correctness gate).

### 8. Repository-state validation
Same 5-point pattern, scoped to `capture.py` alone. Exactly one phase-specific commit, if and when
separately authorized.

### 9. Failure conditions
Reject if any logging call can raise or alter behavior. This phase carries no rollback urgency — it may
simply not be done at all, indefinitely, without weakening anything else.

### 10. Evidence required for CEO acceptance
Exact files changed; confirmation of zero behavioral change; commit hash; diff summary.

---

## A. Compact phase-gate checklist

For every phase, before reporting completion to the CEO:

- [ ] Scope respected — only the phase's own named files changed.
- [ ] Non-scope respected — nothing named as out-of-scope was touched.
- [ ] All required deliverables exist exactly as specified.
- [ ] All acceptance criteria objectively verified, not asserted.
- [ ] All required tests (unit/integration/regression/negative/invariant, where applicable) written and
      passing.
- [ ] Static validation performed (type checking attempted and its result disclosed; imports checked;
      schema/serialization checked where applicable).
- [ ] Runtime validation performed where required (Phase F only, formally; informal for G).
- [ ] Repository-state validation complete: working tree clean; no unrelated changes; Flow A zero-diff;
      no unauthorized Flow B changes; exactly one phase-specific commit exists.
- [ ] No failure condition triggered; if one was, implementation stopped and was reported, not
      silently resolved.
- [ ] Full evidence package assembled per that phase's own §10.
- [ ] Explicit confirmation that the next phase has NOT started.
- [ ] Await CEO approval before proceeding.

---

## B. Exact recommended first implementation authorization

**Authorize Phase A only**: "Implement Phase A — Context Memory: new, independent types — per
`IMPLEMENTATION_DEFINITION_OF_DONE.md`. Do not begin Phase B without separate authorization." Phase A is
the lowest-risk, fully additive, zero-existing-shape-change phase, and its own completion (§10 evidence)
gives the CEO the first concrete implementation artifact to inspect before any higher-risk phase (B's
existing-shape change, or F's `harness.py` touch) is considered.

## C. Confirmation

**Implementation has not started.** No file under `ai_trader/` has been created or modified as a result
of this document or any document preceding it in this roadmap step. No phase has been authorized.

## D. Repository status and commit hash for this document

To be confirmed at commit time (immediately following, in the same message): working tree clean before
staging; only this document staged; Flow A zero-diff confirmed; commit created on branch
`ai-trader-implementation`; commit hash reported after creation.

---

## Governance confirmation

No code was written or modified. No contract or schema was changed. No `ai_trader/` file was touched.
This document defines acceptance criteria only — it does not itself authorize any phase. Zero diff
confirmed against every frozen module, Flow A, and Context Memory's own existing package.
