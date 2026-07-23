# Recognition Engine — DESIGN ONLY (kickoff document)

**Status of this document**: DESIGN ONLY, per explicit CEO instruction (2026-07-23). No code was written, no
`ai_trader/` file was touched, no test was run. This file itself is written to disk but has been
deliberately left uncommitted (`git status` will show it as untracked) — it has not been added to the
repository's history, consistent with "nu modifica repository-ul." It exists purely for CEO review; if
accepted, an explicit commit-and-authorization step is a separate future action, not implied by this
document existing.

**Context this document was written from**: `PROJECT_STATE_v2.md` §8.27 (Learning/Research Feedback,
CLOSED for Sprint 1+2 scope) and `NEXT_SESSION_FLOW_B.md`, both current as of this same session. Grounded
directly in the real, already-implemented contracts of `ai_trader/context_memory/`,
`ai_trader/edge_intelligence/`, `ai_trader/market_intelligence/`, and `ai_trader/decision_intelligence/`
(v1 and v2) — every type named below is a real, existing type unless explicitly marked NEW.

---

## 1. Scope

**Recognition Engine answers exactly one question, continuously, per currently-PRESENT edge: "does the
real historical record — what actually happened the last several times the market looked like this —
favor this edge, or not?"**

This is a **read-only, empirical, evidence-classification layer**. It is the first component in this
project to turn Context Memory's accumulated `Outcome`/`PositionOutcome` history (populated by
Learning/Research Feedback, §8.27) into a disclosed, per-edge verdict, rather than leaving that history as
raw statistics a caller must interpret itself.

**What Recognition Engine is explicitly NOT**:
- Not a trading decision. Never BUY/SELL, never an order, never a position size, never wired into
  `harness.py` — same standing rule as every Phase 7 intelligence layer (`market_intelligence/`,
  `edge_intelligence/`, `decision_intelligence/`).
- Not a replacement for, or a modification of, Edge Intelligence. Edge Intelligence already answers "does
  this specific strategy's own AUTHOR-DECLARED conditions (long/short direction, sessions, timeframe
  trend alignment) currently hold" — a rule-based, declarative check against `Contract` metadata,
  entirely independent of trading history. Recognition Engine answers a DIFFERENT question: "does the
  EMPIRICAL, OUTCOME-BASED record support it" — evidence-based, never rule-based. Both can and normally
  will disagree on some edges; that disagreement is meaningful information, not a bug to reconcile here.
- Not a replacement for, or a modification of, Decision Intelligence v1 or v2. v1 already gates on
  contract lifecycle/maturity/confidence/expectancy and ranks PRESENT edges; v2 already ATTACHES a
  `ContextualEvidenceReport` per candidate for explanation, without changing the recommendation
  (`V1_REMAINS_ACTIVE`, Checkpoint 15). Recognition Engine does something neither does today: it
  CLASSIFIES that evidence into a disclosed categorical verdict (mirroring how Edge Intelligence
  classifies raw contract/market facts into PRESENT/POSSIBLE/ABSENT) — a recognition primitive a future
  decision layer could gate on, not an explanation attached to an existing decision.
- Not a Prediction Engine. It produces a categorical, disclosed verdict from already-computed statistics
  (win rate, confidence interval, evidence status) — never a numerical forecast, probability estimate, or
  expected-value projection. A genuine prediction layer, if ever pursued, is a separate, future,
  separately-authorized component; conflating the two would repeat the Research Lab's own hard-learned
  lesson about analytic p-values asserting confidence the underlying statistics didn't support (§B,
  `PROJECT_AUDIT.md`).
- Not a new evidence-computation method. It performs ZERO new statistics. Every number it classifies
  (`contextual_win_rate`, `confidence_interval_95`, `evidence_consistency`, `evidence_status`, etc.) is
  read verbatim from an already-computed `ContextualEvidenceReport` (Checkpoint 13, `evidence.py`,
  UNMODIFIED). The one genuinely new logic in this whole design is the classification thresholds
  themselves (§9).

## 2. Responsibilities

1. For every edge Edge Intelligence currently reports PRESENT, retrieve the matching
   `ContextualEvidenceReport` (reusing Context Memory's own Checkpoint 12 retrieval + Checkpoint 13
   aggregation, unmodified).
2. Classify each report into one disclosed `RecognitionVerdict` (§6), with at least one concrete,
   traceable evidence string per verdict — the same "no hidden score, no vague phrase" discipline
   `DecisionCandidate` already enforces.
3. Assemble one `RecognitionSnapshot` per `(symbol, as_of)` — one `RecognitionReading` per PRESENT edge,
   fully reproducible from the same inputs (deterministic, no randomness, no external state beyond the
   supplied `HistoricalIndex`).
4. Disclose, per reading, exactly which evidence-quality limitation applies when a favorable/unfavorable
   verdict cannot be reached (mirroring `ContextualEvidenceReport.limitations` verbatim, never inventing
   a new limitation taxonomy).

**Explicitly NOT a responsibility**: computing evidence statistics (Context Memory's job, unchanged),
declaring which edges are PRESENT (Edge Intelligence's job, unchanged), ranking or recommending execution
(Decision Intelligence's job, unchanged), capturing new Outcomes (Learning/Research Feedback's job,
unchanged), running virtual executions (Shadow Evidence's job, unchanged).

## 3. Place in the AI Trader architecture

```
Market Intelligence  ──────────────┐
  (OBSERVE/UNDERSTAND,             │
   MarketIntelligenceSnapshot)     │
                                   ▼
                          Edge Intelligence
                    (RECOGNIZE, rule-based, per declared
                     Contract: PRESENT / POSSIBLE / ABSENT)
                                   │
                     present_strategy_ids()
                                   │
                   ┌───────────────┴────────────────┐
                   ▼                                 ▼
        Decision Intelligence v1/v2          RECOGNITION ENGINE (NEW)
     (EVALUATE/DECIDE: contract-based        (RECOGNIZE, empirical, per
      eligibility gates + ranking;            accumulated Outcome history:
      v2 attaches CM evidence for             FAVORABLE / UNFAVORABLE /
      explanation only)                       NEUTRAL / INSUFFICIENT)
                                                        │
                                          reuses, unmodified:
                                          retrieval.py (Ckpt 12) +
                                          evidence.py (Ckpt 13)
                                                        │
                                                        ▼
                                              Context Memory repository
                                          (Observation/Outcome/PositionOutcome
                                           — populated over time by ↓)
                                                        │
                                          Learning / Research Feedback
                                        (captures real-portfolio + Shadow
                                         Outcomes/PositionOutcomes, §8.27)
                                                        ▲
                                                        │
                                              Shadow Evidence (per-edge
                                              virtual execution — the
                                              realistic evidence-volume
                                              source, since real trades
                                              alone are sparse)
```

Recognition Engine sits **structurally parallel to Decision Intelligence, both downstream of Edge
Intelligence and Context Memory** — it does not sit "inside" or "above" Decision Intelligence, and it does
not feed it automatically (§8). It is the same kind of independent, read-only, additively-composed layer
Context Memory's own evidence report already is; the difference is that Recognition Engine turns that
report into a verdict, the way Edge Intelligence turns raw contract/market facts into a verdict.

## 4. Inputs

All inputs are already-computed, already-existing types — Recognition Engine invents no new upstream
data:

| Input | Source | Type (existing) |
|---|---|---|
| Current market context | Market Intelligence | `MarketIntelligenceSnapshot`, adapted locally into `ContextSnapshot` (own local adapter, §7 — NOT a reuse of `decision_intelligence_v2`'s adapter, for the same isolation reason `decision_intelligence`'s `ResearchStats` is a local echo rather than importing a sibling package's type) |
| Currently-PRESENT edges | Edge Intelligence | `EdgeIntelligenceSnapshot.present_strategy_ids()` |
| Historical evidence store | Context Memory | `HistoricalIndex` (Checkpoint 11, read-only handle) |
| Retrieval policy | Context Memory | `RetrievalPolicy` (Checkpoint 12, unmodified, caller-supplied or default) |
| Evidence classification thresholds | Recognition Engine (NEW) | `RecognitionPolicy` (§9 — deliberately a NEW, separately-versioned policy type, not a repurposing of `EvidencePolicy`, whose thresholds were calibrated for a different purpose — evidence *sufficiency*, not verdict *classification*) |
| Which `Outcome` population to evaluate | caller-supplied | `OutcomeKind` (`STRATEGY` — Shadow-sourced — is the realistic default; see §10 open question 2) |

## 5. Outputs

Two NEW, frozen, `__post_init__`-validated dataclasses, in `recognition_engine/types.py`:

```
RecognitionVerdict(str, Enum):
    RECOGNIZED_FAVORABLE
    RECOGNIZED_UNFAVORABLE
    RECOGNIZED_NEUTRAL
    INSUFFICIENT_EVIDENCE
    UNAVAILABLE

RecognitionReading:
    strategy_id: str
    verdict: RecognitionVerdict
    evidence_report: ContextualEvidenceReport   # embedded verbatim, full traceability
    evidence: tuple[str, ...]                   # >=1 disclosed, concrete reasoning strings
    explanation: str

RecognitionSnapshot:
    symbol: str
    as_of: int
    readings: tuple[RecognitionReading, ...]     # one per PRESENT edge, sorted by strategy_id
    recognition_policy_version: SchemaVersion
```

`recognized_favorable_strategy_ids(snapshot) -> frozenset[str]` — the clean, execution-decoupled query
surface, mirroring `present_strategy_ids()`/`recommended_or_no_trade()`'s own established pattern.

## 6. Pipeline

1. Caller supplies the current `ContextSnapshot` (already computed elsewhere — Recognition Engine does
   not run Market Intelligence itself) and the current `EdgeIntelligenceSnapshot`.
2. Recognition Engine's own local adapter converts the snapshot into Context Memory's `ContextSnapshot`
   contract if not already in that shape (identical transformation `decision_intelligence_v2/adapters.py`
   already performs for a different caller — same logic, independently owned, §7).
3. Call `retrieval.retrieve(index, context_snapshot, retrieval_policy)` **once** (Checkpoint 12,
   unmodified) — the result is not edge-specific, so this is O(1) per `as_of`, not O(N present edges).
4. For every `strategy_id` in `EdgeIntelligenceSnapshot.present_strategy_ids()`: call
   `evidence.aggregate_evidence(index, retrieval_result, strategy_id, outcome_kind, evidence_policy)`
   (Checkpoint 13, unmodified) to obtain one `ContextualEvidenceReport`.
5. Classify each report into a `RecognitionVerdict` via the NEW, pure, deterministic `classify()` function
   (§9) — the one genuinely new algorithm in this design.
6. Assemble the `RecognitionSnapshot`, `readings` sorted by `strategy_id` (same canonicalization
   discipline `Observation.present_edges` already enforces).

No step writes to the repository. No step calls Decision Intelligence, Signal Engine, Scoring Engine, Risk
Manager, Execution Engine, Shadow Evidence, or Learning/Research Feedback.

## 7. Component modules (proposed)

New package `ai_trader/recognition_engine/`:

- `types.py` — `RecognitionVerdict`, `RecognitionReading`, `RecognitionSnapshot`,
  `RECOGNITION_ENGINE_SCHEMA_VERSION`. No logic.
- `policy.py` — `RecognitionPolicy` (NEW, versioned, explicit, caller-overridable — never a hidden
  constant, same discipline as `EvidencePolicy`; see §9 for why this must be its own type).
- `adapters.py` — the local `MarketIntelligenceSnapshot -> ContextSnapshot` bridge (a deliberately
  independent copy of the logic `decision_intelligence_v2/adapters.py` already contains — duplication
  accepted for isolation, matching the project's own established precedent of local echoes over
  cross-layer imports).
- `classification.py` — the one new algorithm: `classify(report: ContextualEvidenceReport, policy:
  RecognitionPolicy) -> tuple[RecognitionVerdict, tuple[str, ...]]`. Pure function, no I/O, fully unit-
  testable in isolation (mirrors `edge_intelligence/verdict.py`'s own split from `engine.py`).
- `engine.py` — `recognize(context_snapshot, edge_snapshot, index, outcome_kind, retrieval_policy=None,
  evidence_policy=None, recognition_policy=None) -> RecognitionSnapshot`. The public entry point;
  orchestration only, calls `classification.classify()` and Context Memory's own `retrieval.py`/
  `evidence.py`, never reimplements either.

## 8. Contracts between modules

- `types.py` has zero dependencies on any other Recognition Engine module — pure data, importable
  standalone (same rule `context_memory/contracts.py` and `edge_intelligence/types.py` both already
  follow).
- `classification.py` depends only on `types.py` and Context Memory's own `ContextualEvidenceReport`
  (read-only) — never on `engine.py`, `adapters.py`, or any live index/retrieval state. This keeps the
  ONE new algorithm fully deterministic and testable with synthetic reports, no simulation required.
- `engine.py` depends on `types.py`, `policy.py`, `adapters.py`, `classification.py`, and Context Memory's
  public API (`retrieval.retrieve`, `evidence.aggregate_evidence`) — never on Context Memory's internal
  `index.py`/`episodes.py`/`codec.py`/`repository.py` internals directly, same isolation boundary
  `decision_intelligence_v2` already respects.
- `recognition_engine/` must NEVER import `signal_engine`, `scoring_engine`, `risk_manager`,
  `execution_engine`, `shadow_evidence`, `learning_feedback`, `decision_intelligence`, or
  `decision_intelligence_v2` — same isolation discipline every Phase 7 layer follows, to be verified by
  grep + a static AST import-independence scan at implementation time (the same technique
  `context_memory/tests/test_import_independence.py` already established).
- `RecognitionSnapshot` must never be interpreted as, or silently promoted to, a trading recommendation by
  any future caller — the same discipline that motivated renaming the Blocker-2 discussion around
  `Outcome`/`PositionOutcome` (§8.27): a categorical verdict is not a decision.

## 9. Interaction with Decision Engine, Learning Feedback, and other subsystems

- **Decision Intelligence (v1/v2)**: NOT wired together by this design. `RecognitionSnapshot` is produced
  as an independent artifact, available for a FUTURE, separately-authorized Decision Intelligence version
  (a hypothetical v3, or a v2 extension) to consume alongside Edge Intelligence's own PRESENT verdict and
  the existing contract-based eligibility gates. This design does not propose how that combination would
  work (e.g. AND-gate vs. weighted signal vs. tie-break input) — that is deliberately a separate, future
  design question, out of scope here, exactly as the CEO's own request specified ("interacția cu Decision
  Engine" means describing the *interface point*, not deciding the *combination policy*).
- **Learning/Research Feedback**: no direct dependency (never imported). Purely transitive — Recognition
  Engine's evidence quality is entirely bounded by how much Learning Feedback has captured into Context
  Memory's repository so far. This is a load-bearing limitation, not a footnote: see §10 open question 2.
- **Shadow Evidence**: no direct dependency (never imported) — same transitive relationship, one layer
  further removed (Shadow Evidence → Learning/Research Feedback → Context Memory → Recognition Engine).
- **Context Memory**: the only genuine runtime dependency — `retrieval.py` and `evidence.py`, both
  reused completely unmodified. Recognition Engine adds a NEW policy type (`RecognitionPolicy`) but never
  a new Context Memory contract, never a new repository stream, never a schema change.
- **Edge Intelligence**: the only other genuine runtime dependency — reads `present_strategy_ids()`
  only, never re-derives PRESENT/POSSIBLE/ABSENT itself, never imports `edge_intelligence.evidence`
  internals.
- **Market Intelligence**: read-only, via a local adapter (§7) — same relationship every other consumer
  of `MarketIntelligenceSnapshot` already has.

## 10. Extensibility and architectural principles

1. **Read-only, always.** Never BUY/SELL/entry/stop/target/size/execution, ever, in any future version of
   this package — the one non-negotiable principle every Phase 7 layer shares.
2. **Deterministic, disclosed classification only, v1.** No hidden score, no black-box statistical or ML
   model. A future version that wanted genuine machine-learned pattern recognition would need its own
   separate, explicit CEO authorization and its own validation discipline (calibration, adversarial
   review, out-of-sample test) — conflating that leap with this kickoff would repeat exactly the mistake
   the Research Lab's own analytic-p-value defect (`PROJECT_AUDIT.md` D1) already taught this project to
   avoid.
3. **Additive only.** No existing frozen module changes. No existing package's return-type contract
   changes. Verified the same way every other Sprint in this project has verified it — zero-diff proofs
   against `context_memory/`, `edge_intelligence/`, `market_intelligence/`, `decision_intelligence*/`.
4. **Versioned policy, never a hidden constant** — `RecognitionPolicy` gets its own `SchemaVersion`, same
   as `EvidencePolicy`/`RetrievalPolicy` before it.
5. **Single-instrument scope, disclosed.** Like every other Phase 7 layer to date, this design assumes
   one instrument (XAUUSD) and does not address multi-instrument recognition — a disclosed limitation, not
   an oversight.
6. **Extensible dimensions, not extensible principles.** Future versions may add more evidence dimensions
   to classify on (e.g. `PositionOutcome`-derived duration/cost patterns, not just win-rate/CI) — additive
   fields, additive classification rules — without ever relaxing principles 1–4 above.

---

## 11. Maturity verdict — is this ready for implementation authorization?

**Not yet — two concrete, checkable gaps should be closed first, not because the architecture is wrong,
but because this project has twice already learned the same lesson the hard way (Learning Feedback's own
3-round Phase F design rejection; Portfolio Architect's Phase 2A "too sparse to calibrate" finding) and
both apply here almost exactly:**

1. **Evidence-population check, not yet done.** This design assumes Context Memory's repository already
   holds, or will soon hold, a meaningful population of `Outcome`/`PositionOutcome` records to recognize
   patterns from. Nothing in this session verified how many actually exist right now. If the real number
   is near-zero (plausible — Learning/Research Feedback's real-portfolio capture path has run in very
   little live/simulated volume so far, and Shadow-sourced `STRATEGY`-kind Outcomes depend on Shadow
   Evidence having been run with capture wired for meaningful stretches), every `RecognitionReading`
   would classify as `INSUFFICIENT_EVIDENCE`/`UNAVAILABLE` at launch — architecturally correct (the
   system is honest about not knowing), but worth knowing BEFORE authorizing implementation, exactly as
   Portfolio Architect's own Phase 2A calibration run discovered for a structurally similar
   evidence-sparsity risk. Recommended next step: a small, code-only, zero-production-diff instrumented
   count of `context_memory` repository population (mirroring Phase 2A's own offline-instrumented
   approach) before implementation begins.
2. **Classification thresholds are not yet chosen.** §9's `RecognitionPolicy` is deliberately left with
   no proposed numeric defaults in this document — asserting thresholds (e.g. "CI excludes zero and mean
   > +0.1R => FAVORABLE") without evidence to calibrate against would repeat the same category of mistake
   Portfolio Architect's rejected `STRATEGY_CONCENTRATION_REORDER` policy made: a plausible-sounding rule
   with no evidence behind the specific numbers. This should be its own short second-round design
   deliverable, informed by whatever the evidence-population check in (1) actually shows — not resolved
   by assertion here.

**Everything else in this document — the module boundaries, the contracts, the pipeline, the isolation
rules, the non-goals — is architecturally sound and requires no further design revision**: it reuses
exactly two existing, already-validated Context Memory entry points (`retrieval.retrieve`,
`evidence.aggregate_evidence`), introduces exactly one genuinely new algorithm (verdict classification,
cleanly isolated in its own pure-function module), and follows every isolation/versioning/disclosure
convention already established and tested across Market Intelligence, Edge Intelligence, Decision
Intelligence v1/v2, and Context Memory itself.

**Recommendation**: authorize the evidence-population check (item 1) as a small, standalone, code-only
diagnostic (no new package, no `recognition_engine/` yet) before authorizing full implementation. If the
population turns out to be non-trivial, item 2's threshold design can follow immediately, informed by real
numbers rather than assertion — and full implementation authorization would then be well-grounded, not
premature.
