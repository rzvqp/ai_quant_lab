# IMPLEMENTATION_EXECUTION_PLAN.md — Implementation Sequencing Review (Flow B roadmap step 3/6)

**Status: SEQUENCING REVIEW ONLY. No code written, no code modified, nothing committed to `ai_trader/`.**
Companion to `LEARNING_RESEARCH_FEEDBACK_IMPLEMENTATION_PLAN.md` (commit `d8265fa`), which this document
does not revise — it only sequences the SAME work into independent, incrementally-mergeable phases with
explicit rollback points, per CEO directive. No implementation is authorized by this document.

---

## Phase A — Context Memory: new, independent types (zero touch to existing shapes)

1. **Goal**: introduce `OutcomeKind`, the new `SourceType.REAL_PORTFOLIO_LEDGER` member, and the entirely
   new `OperationalMetadata`/`OperationalMetadataId` types + their `identities.py`/`repository.py`
   support — with nothing existing changed in shape or behavior.
2. **Files modified**: `context_memory/enums.py` (additive), `context_memory/contracts.py` (additive —
   new types only, `Outcome` itself untouched in this phase), `context_memory/identities.py` (additive —
   new function only), `context_memory/repository.py` (additive — new methods only). Plus new tests:
   `context_memory/tests/test_operational_metadata.py` (new file).
3. **Risk level: LOW.** Every change is a pure addition — a new enum, one new member on an existing enum
   (safe in Python; nothing exhaustively pattern-matches over `SourceType`'s members without a
   catch-all), a new dataclass, a new function, two new repository methods. No existing type's shape
   changes, no existing caller is touched.
4. **Rollback strategy**: revert the single commit. Nothing yet references any of these additions, so
   rollback has zero second-order effects.
5. **Validation required before continuing**: new unit tests for `OperationalMetadata`'s own
   construction/validation, `compute_operational_metadata_id`'s determinism, and
   `append_operational_metadata`'s own round-trip through the repository — all NEW tests. Full EXISTING
   `context_memory/` test suite re-run to confirm zero regression (expected: 100% unchanged, since
   nothing existing was touched).
6. **Can the repository remain in a working state after this phase?** **Yes, fully.** Every existing
   test, fixture, and caller is completely unaffected.
7. **Can this phase be merged independently?** **Yes.** It is a complete, self-contained, inert addition.

---

## Phase B — `Outcome.outcome_kind` field, validation, and existing fixture updates

1. **Goal**: add the required `outcome_kind: OutcomeKind` field to the EXISTING `Outcome` dataclass, add
   the kind/source `__post_init__` compatibility validation, and update every existing `Outcome(...)`
   construction site to supply it.
2. **Files modified**: `context_memory/contracts.py` (the one existing-type shape change in the whole
   plan), plus the three files that construct `Outcome` today: `context_memory/tests/_fixtures.py`,
   `context_memory/tests/test_outcome.py`, `decision_intelligence_v2/tests/_fixtures.py`.
3. **Risk level: MEDIUM.** The only phase that changes an already-relied-upon type's shape. A missed
   call site anywhere would surface as an immediate, loud test failure (a `TypeError` for a missing
   required argument) — not a silent bug — but every call site must genuinely be found and fixed for the
   phase to complete.
4. **Rollback strategy**: revert the single commit. Phase A's own additions (`OperationalMetadata`, the
   `OutcomeKind` enum itself, the new `SourceType` member) are entirely unaffected and remain valid,
   since nothing in Phase A depended on `Outcome`'s own shape changing.
5. **Validation required before continuing**: full EXISTING `context_memory/`, `decision_intelligence_v2/`,
   and `decision_comparison/` test suites must pass UNMODIFIED in their own logic (only their `Outcome(...)`
   construction calls gain one new argument) — this is the load-bearing proof for this phase specifically.
   New tests: both valid `(OutcomeKind, SourceType)` pairings accepted, every invalid pairing rejected.
6. **Can the repository remain in a working state after this phase?** **Yes.** Once the fixture updates
   land in the SAME commit as the field addition (never split across two commits, or the repo would be
   broken in between), every existing test passes and the type system is fully consistent.
7. **Can this phase be merged independently?** **Yes**, but it is the highest-friction phase in the
   entire plan — the one place where "independently" still means "atomically, including every existing
   call site in the same commit."

---

## Phase C — `evidence.py` kind-awareness

1. **Goal**: give `aggregate_evidence`/`aggregate_all_present_edges` an explicit, required
   `outcome_kind: OutcomeKind` parameter, and make their internal per-episode Outcome lookup filter by
   it — closing the statistical-separation gap identified during the implementation-planning pass.
2. **Files modified**: `context_memory/evidence.py`, `context_memory/tests/test_evidence.py` (extended).
3. **Risk level: MEDIUM.** A public function signature change. Blast radius is contained: no confirmed
   production caller of `aggregate_evidence`/`aggregate_all_present_edges` exists outside this module's
   own test suite today (verified during the design/planning research passes) — but this must be
   RE-confirmed at implementation time (a fresh grep), not assumed from memory of an earlier pass.
4. **Rollback strategy**: revert the single commit. Phases A and B are entirely unaffected — `Outcome`
   and `OperationalMetadata` remain valid, usable types independent of whether `evidence.py` knows how
   to filter by kind yet.
5. **Validation required before continuing**: extended `test_evidence.py` proving Strategy and Portfolio
   outcomes attached to the SAME `Observation` are correctly kept separate by the new parameter; full
   existing `evidence.py` test suite re-run.
6. **Can the repository remain in a working state after this phase?** **Yes, fully.**
7. **Can this phase be merged independently?** **Yes.**

**Sequencing note**: Phase C has no CODE dependency on Phases D/E/F below (it is purely on the READ side;
the write-side adapters and harness wiring are independent of it). It is placed here, before D/E/F, as a
DELIBERATE SAFETY CHOICE, not a hard requirement: closing the read-side gap before any write-side phase
lands means there is never a window where real dual-kind data could exist while `evidence.py` is still
kind-blind. A team with more parallel capacity could run C and D concurrently; this plan recommends the
linear order for the same reason this project has repeatedly chosen to close a gap proactively rather
than race it (e.g. the Shadow-tap reordering discipline in Portfolio Architect Phase 1).

---

## Phase D — `ai_trader/learning_feedback/` package: adapters only (pure functions, unwired)

1. **Goal**: implement the three pure-function adapters (`build_strategy_outcome`,
   `build_portfolio_outcome`, `build_operational_metadata`) and `LearningFeedbackConfig`, fully tested in
   isolation, with ZERO wiring into `harness.py` yet.
2. **Files modified**: new `ai_trader/learning_feedback/{__init__.py,adapters.py,config.py}`, new
   `ai_trader/learning_feedback/tests/{__init__.py,test_adapters.py}`.
3. **Risk level: LOW.** An entirely new, isolated package. Nothing existing is touched or imported by
   anything existing; nothing calls into it yet.
4. **Rollback strategy**: delete the new package directory. Nothing else references it.
5. **Validation required before continuing**: new unit tests only — happy path, skip/`None` path
   (unresolved position, missing data), and the kind/source validation being genuinely enforced when an
   adapter is asked to build an invalid pairing.
6. **Can the repository remain in a working state after this phase?** **Yes, fully** — zero regression
   risk to anything existing, since nothing existing calls this new code.
7. **Can this phase be merged independently?** **Yes**, cleanly.

---

## Phase E — `ai_trader/learning_feedback/capture.py`: write-path orchestration (still unwired)

1. **Goal**: implement the two write-path entry functions (decision-time capture, resolution-time
   capture) and the run-scoped `(strategy_id, symbol, entry_as_of) → observation_id` correlation map —
   tested against directly-constructed Shadow/Risk Manager/Portfolio Simulator fixture objects, still
   WITHOUT touching `harness.py`.
2. **Files modified**: new `ai_trader/learning_feedback/capture.py`, new
   `ai_trader/learning_feedback/tests/test_capture.py`.
3. **Risk level: LOW-MEDIUM.** More orchestration logic than Phase D's pure adapters (the correlation-map
   lookup/miss behavior, the two-trigger-point resolution logic), but still fully isolated — no harness
   involvement, so still zero regression risk to anything existing.
4. **Rollback strategy**: revert the single commit. Phase D's own adapters remain independently valid
   and tested regardless — Phase E only consumes them, it does not modify them.
5. **Validation required before continuing**: `test_capture.py` — correlation-map hit/miss behavior,
   the "drop and log, never fabricate" rule for an unmatched resolution event (§11 of the main plan).
6. **Can the repository remain in a working state after this phase?** **Yes, fully.**
7. **Can this phase be merged independently?** **Yes.**

---

## Phase F — `harness.py` wiring (the one phase touching the shared orchestrator)

1. **Goal**: add the new, additive `learning_feedback_config: LearningFeedbackConfig | None = None`
   constructor parameter and the two new call sites in `_run_one_bar` (decision-time, resolution-time),
   gated by `is not None` — the point at which the feature can, for the first time, actually run.
2. **Files modified**: `ai_trader/simulation/harness.py`, new
   `ai_trader/simulation/tests/test_learning_feedback_integration.py`.
3. **Risk level: HIGH.** The single most shared, most heavily-relied-upon file in the codebase — every
   prior touch this session to this file (Shadow Evidence, Strategy Health, Portfolio Architect ×2) has
   required a full byte-identical-execution proof and a full regression run to be trusted, and this
   phase is no different. High risk is about the FILE's own sensitivity and blast radius if a mistake
   were made, not about this specific change being conceptually complex.
4. **Rollback strategy**: revert the single commit. Every prior phase (A–E) remains valid, tested, and
   entirely inert — because Phases A–E are either pure schema/type additions or fully-isolated,
   never-yet-wired orchestration code, none of them has ANY effect on runtime behavior until this phase
   exists. Reverting Phase F alone fully and cleanly disables the feature.
5. **Validation required before continuing**: the full required battery — (a) byte-identical competitive
   execution proof, `learning_feedback_config` omitted vs. explicit `None` (the mandatory first test,
   matching every prior touch to this file); (b) the harness-level integration tests (Observation/Outcome/
   OperationalMetadata actually appended when enabled; Portfolio Outcome absence confirmed valid when no
   real trade occurs; both ALLOW and DENY `OperationalMetadata` cases); (c) full regression:
   `context_memory/`, `decision_intelligence_v2/`, `strategy_health/`, `portfolio_architect/`, and
   `test_shadow_disabled_parity.py`'s own 43-strategy parity suite, all re-run unmodified.
6. **Can the repository remain in a working state after this phase?** **Yes** — the new parameter
   defaults to `None`, and (5)(a) is the direct proof that every existing caller's own behavior is
   unaffected whether or not this phase has landed.
7. **Can this phase be merged independently?** **Yes** — this is the phase that makes the feature real,
   but it remains additive and off-by-default like every prior touch.

---

## Phase G (OPTIONAL, deferrable indefinitely) — operational polish

1. **Goal**: structured logging/metrics for Learning's own write volume and failure counts (e.g. how many
   Observations/Outcomes/OperationalMetadata rows were appended this run, how many resolution events were
   dropped for lacking a matching `observation_id`).
2. **Files modified**: `ai_trader/learning_feedback/capture.py` (additive logging calls only).
3. **Risk level: LOW.** Purely additive instrumentation, no behavior change.
4. **Rollback strategy**: revert the single commit; no functional impact either way.
5. **Validation required before continuing**: none beyond confirming the logging calls themselves don't
   raise.
6. **Can the repository remain in a working state after this phase?** **Yes, trivially.**
7. **Can this phase be merged independently?** **Yes**, and it may be deferred indefinitely without
   weakening the approved Normative Model in any way — it is observability, not correctness.

**Also verify-only, foldable into Phase B, not its own phase**: `context_memory/validation.py` — inspect
during Phase B whether it independently re-validates `Outcome`'s own shape outside `contracts.py`'s own
`__post_init__`; extend only if so. Not confirmed either way by the design/planning passes to date.

---

## Dependency graph

```
Phase A  (Context Memory: new independent types)
   |
   v
Phase B  (Outcome.outcome_kind + fixture updates)         <- the one existing-shape change
   |
   v
Phase C  (evidence.py kind-awareness)                     <- recommended before D/E/F (safety choice,
   |                                                          not a hard code dependency -- see note above)
   v
Phase D  (learning_feedback/ adapters, pure, unwired)
   |
   v
Phase E  (learning_feedback/capture.py, orchestration, unwired)
   |
   v
Phase F  (harness.py wiring -- feature goes live, opt-in)
   |
   v
Phase G  (OPTIONAL -- logging/metrics polish, deferrable indefinitely)
```

**Mandatory**: A, B, C, D, E, F — all six are required for the approved Normative Model to be fully and
safely realized; none may be skipped.

**Optional**: G only.

**Deferrable** (not phases of THIS implementation at all — separate, future, independently-authorized
work, per the Implementation Plan's own §0 DEFERRED list): wiring `decision_intelligence_v2`'s
`context_memory_index` into `harness.py` live; any `SourceType` member beyond
`REAL_PORTFOLIO_LEDGER`; slippage/spread/latency fields; Portfolio Architect diagnostics capture.

---

## If implementation stopped halfway — where is the repository still fully functional and consistent?

**After every phase from A through F, without exception.** This is a deliberate property of the
sequencing, not a coincidence: each phase was designed so that stopping there leaves zero broken state.

Precisely, by phase:
- **After A**: new types exist, entirely unused — the pre-existing system is byte-for-byte unaffected.
- **After B**: `Outcome` now requires and validates `outcome_kind`; every existing test passes; still zero
  production callers write real data, so zero runtime impact.
- **After C**: the read side (`evidence.py`) is now fully kind-aware and ready for whenever real data
  starts flowing — still zero production impact, since nothing writes real `Outcome` rows yet.
- **After D**: adapters exist, fully tested in isolation, called by nothing in production.
- **After E**: write-path orchestration exists, fully tested against fixtures, still not reachable from
  any real run (`harness.py` untouched).
- **After F**: the feature is live but strictly opt-in and proven byte-identical when the new parameter
  is left at its default — every existing caller is unaffected regardless.

**One honest distinction worth stating explicitly, since "functional and consistent" is not the same
question as "has the feature shipped its own value"**: Phases A through E are *safe* to stop at, but the
Learning / Research Feedback capability itself does not actually observe or record anything until Phase F
lands — before that, the work is entirely inert preparation, correctly so. If a genuinely FORCED stop had
to pick the single most valuable place to halt while still guaranteeing full safety, **the end of Phase C**
is the strongest candidate: at that point, both the write-side data model (Phases A/B) and the read-side
statistical-separation guarantee (Phase C) are complete and mutually consistent, so any FUTURE resumption
(even much later, even by a different implementer) inherits a schema that is already correct and cannot
silently blend Strategy and Portfolio outcomes — the hardest-to-retrofit property (§ADR's own
backward-compatibility argument: fixing this after real data exists is a migration; fixing it before is
free) is already locked in, even though the feature itself is not yet live.

---

## Governance confirmation

No code was written or modified. No contract or schema was changed. No `ai_trader/` file was touched.
This is a sequencing review only — implementation of any phase requires its own separate, explicit CEO
approval. Zero diff confirmed against every frozen module, Flow A, and Context Memory's own existing
package.
