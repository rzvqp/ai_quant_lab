# Recognition Engine — Phase 1 Design

**Status of this document**: DESIGN ONLY, per explicit CEO instruction (2026-07-24). No code was written,
no classifier implemented, no model trained, no edge computed, no strategy/decision/execution logic
touched, no `ai_trader/` file touched, no Learning Feedback / Flow A / Flow B file touched. Written to
disk, deliberately left **uncommitted** (`git status` will show it `??`) pending CEO review — the same
treatment `RECOGNITION_ENGINE_DESIGN.md` received before its own acceptance.

**Relationship to the prior design**: this document extends, not replaces,
`RECOGNITION_ENGINE_DESIGN.md` (ACCEPTED, §8.28 of `PROJECT_STATE_v2.md`) — its scope, non-goals,
architecture placement, and module boundaries all still stand. That document was written when Phase 0's
own diagnostic had found **zero** real `Outcome`/`PositionOutcome` records anywhere. Phase 1 of Learning
Feedback has since produced and audited a real dataset (**688 `PositionOutcome`, 575 `STRATEGY` / 113
`PORTFOLIO`, 26 `InterimRealization`, 23,639 `Observation`**, full 12-month window,
`LEARNING_FEEDBACK_DATASET_AUDIT.md`, verdict READY, officially CLOSED and declared the OFFICIAL data
source per the CEO's own most recent decision). This document answers the CEO's own 10 explicit
questions, grounded in that real, audited dataset's own actual shape — not assumption.

---

## 1. What is the fundamental unit of learning?

**The `(decision-time Observation, terminal PositionOutcome)` pair, scoped per `(strategy_id,
outcome_kind)`.** Not `Outcome` alone, not `StrategyOutcome`, not a temporal sequence — for reasons
proven, not assumed, below.

- **`Observation` alone is necessary but not sufficient.** 23,639 exist; only 688 (2.9%) ever resolve
  into a captured position. An `Observation` with no eventual `PositionOutcome` is not itself a learning
  example — it is either still-pending context or context that never converted to a position (the
  overwhelming majority, matching this project's own already-measured low-conversion-rate architecture,
  Phase 6.9A).
- **`Outcome` (the terminal, per-fill record) is UNSAFE as the primary label.** The dataset audit
  (`LEARNING_FEEDBACK_DATASET_AUDIT.md` §2) found, and individually verified, **4 of 688 records (0.58%)
  where `Outcome.normalized_result`'s own sign disagrees with the position's true, complete
  `PositionOutcome.total_net_pnl` sign** — e.g. an early partial closing at +1.92R followed by a final
  fill at −1.08R yields a real, cumulative +$4.62 result, while the terminal-fill-only `Outcome` alone
  reads as a loss. Training or querying on `Outcome` as if it were the position's own complete result
  would systematically mislabel exactly the multi-partial-exit cases `PositionOutcome` was built to
  correct (Sprint 2 Blocker 2's own entire justification). **`Outcome` must never be used as a Recognition
  Engine label.**
- **`PositionOutcome` (688 total) is the CEO-ratified canonical, complete, Level-1 economic result** —
  the correct target, by construction and by the audit's own empirical confirmation that it, not
  `Outcome`, reflects what actually happened.
- **`StrategyOutcome` (an aggregate across many positions) is too coarse as the PRIMARY unit.** Collapsing
  to one number per strategy before recognition happens would destroy the very thing this engine needs
  to recognize — which CONTEXT precedes which RESULT. It remains a valid, useful SECONDARY/derived
  summary (built by aggregating many `(Observation, PositionOutcome)` pairs after the fact), never the
  training unit itself.
- **A temporal sequence of Observations is a valid FUTURE extension, explicitly out of Phase 1 scope.**
  Context Memory's own schema carries no "previous Observation" pointer or sequence identifier today —
  building sequence-awareness would require a schema change (`nu modifica schema acum`, the CEO's own
  standing instruction from the dataset-audit closeout). Phase 1 recognizes single-snapshot context, not
  unfolding regime evolution.
- **`InterimRealization` is never a standalone learning unit** — this is not a new rule invented here; it
  is the type's own pre-existing, CEO-ratified docstring ("never a learning target, structurally excluded
  from evidence.py/retrieval.py aggregation"). Recognition Engine must inherit this exclusion unchanged.

**Verified, not assumed, leakage-relevant fact about this unit**: `PositionOutcome.observation_id` (and
the terminal `Outcome.observation_id` for the same position) is set, at capture time, to the position's
own **decision-time** Observation — the market context that existed the moment the position was OPENED,
never anything from later (`ai_trader/learning_feedback/capture.py::capture_portfolio_terminal`, line
575/579-581: both `build_portfolio_outcome` and `build_portfolio_position_outcome` are called with
`entry.observation_id`, where `entry` is the `PendingPosition` registered at decision time via
`register_pending_correlation`/`promote_opening_fill`, inspected directly this session, not inferred from
a docstring alone). This is the load-bearing fact behind §5 below.

## 2. What must the engine actually recognize?

Mapped strictly onto fields that already exist in the audited dataset — nothing invented:

- **Similar contexts**: `ContextSnapshot`'s own already-stored categorical fields (`session_state`,
  `trend_m15/h1/h4/d1`, `momentum_m15/h1/h4/d1`, `volatility_regime`, `liquidity_state`,
  `expansion_state`, `multi_timeframe_agreement`) — this is EXACTLY what Context Memory's own
  `retrieval.py` (Checkpoint 12, unmodified) already does via its fixed-priority hierarchical relaxation
  ladder. Recognition Engine does not reinvent similarity; it reuses this unmodified.
- **Result patterns**: the CONDITIONAL shape of `PositionOutcome.total_net_pnl`/`Outcome.normalized_result`
  (sign distribution, dispersion) given a context bucket + `strategy_id` + `outcome_kind` — never a single
  scalar prediction, always a distribution/count, per §3.
- **Strategy behavior**: per-`strategy_id` conditional patterns, STRICTLY isolated per strategy (never
  blended across strategy_ids — matching `evidence.aggregate_evidence()`'s own existing `strategy_id`
  filter) and per `outcome_kind` (never blending `STRATEGY`- and `PORTFOLIO`-kind evidence for the same
  strategy — matching the Normative Model's own existing kind-isolation rule, already enforced by
  `evidence.py`).
- **Regimes**: `volatility_regime`/`trend_*`/`expansion_state` are already first-class categorical fields
  — directly recognizable without any new derived concept.
- **Agreement and disagreement**: two distinct, already-supported meanings, both legitimate:
  (a) `ContextSnapshot.multi_timeframe_agreement` itself (STRONG/UNKNOWN observed in the real dataset,
  `LEARNING_FEEDBACK_DATASET_AUDIT.md` §3); (b) **agreement between Edge Intelligence's own rule-based
  PRESENT verdict and Recognition Engine's own empirical pattern** — the exact boundary
  `RECOGNITION_ENGINE_DESIGN.md` §1 already staked out: Edge Intelligence answers "does the DECLARED rule
  match," Recognition Engine answers "does the EMPIRICAL history support it." A future consumer could
  compare the two verdicts; Recognition Engine Phase 1 produces only its own half of that comparison.
- **Other relations the data genuinely supports, disclosed as low-confidence given volume**: whether a
  given context tends to produce multi-partial exits (26 `InterimRealization` total, spread thin — any
  such pattern would be low-n and should be flagged `INSUFFICIENT_EVIDENCE`, never asserted).

**What Recognition Engine explicitly does NOT recognize**: a point prediction, a probability, an expected
value, a ranking, or anything resembling "this will win" — those are the province of a hypothetical future
Prediction Engine / Statistics Engine (§4), not authorized and not designed here.

## 3. What does memory represent?

**Conditional statistics over Context Memory's own already-existing categorical bucketing, retrieved via
the already-existing hierarchical relaxation ladder — not examples, prototypes, clusters, or embeddings,
for Phase 1.** This is a data-volume-driven decision, proven with real numbers, not a stylistic
preference:

- The richest single strategy in the entire 12-month dataset (S46) has **66 `STRATEGY`-kind
  `PositionOutcome` records total** — before any context conditioning at all. The Research Lab's own
  established evidence-sufficiency convention, reused twice already in this project
  (`code/alpha_lab.py`'s `MINTR=25`, `PROJECT_AUDIT.md` notes; Strategy Health's own
  `MIN_EVIDENCE_TRADES`), requires **≥25** observations before treating a statistic as anything beyond
  `LIMITED`. Conditioning S46's own 66 records on even ONE additional dimension (e.g. `session_state`,
  4 values) already pushes most buckets below 25; conditioning on two dimensions simultaneously
  (`session_state` × `volatility_regime`, 4×3=12 buckets) makes every bucket for every strategy in this
  dataset fall below the sufficiency threshold. **There is not enough data today to support prototype/
  cluster/embedding-based memory, which would need far more examples per cell to avoid overfitting to
  noise — and this project's own standing discipline (Edge Intelligence's "no hidden score, no
  probabilistic guess"; the Research Lab's own analytic-p-value defect, `PROJECT_AUDIT.md` D1, which
  taught this project not to trust an unvalidated statistical method) argues against introducing one
  before the simpler, disclosed alternative is exhausted.**
- **Conditional statistics + disclosed classification is exactly what Context Memory's own Checkpoint 12
  (`retrieval.py`) + Checkpoint 13 (`evidence.py`, `ContextualEvidenceReport`) already compute, unmodified,
  today** — reusing them means "memory," for Phase 1, is not a new data structure at all: it is the
  already-tested `ContextualEvidenceReport` (win rate, mean/median normalized result, 95% CI, sign counts,
  `EvidenceStatus`) Recognition Engine's own accepted architecture (`RECOGNITION_ENGINE_DESIGN.md` §6)
  already designed around.
- **"Rules"** — a disclosed, deterministic classification of that conditional statistic into a
  `RecognitionVerdict` (FAVORABLE/UNFAVORABLE/NEUTRAL/INSUFFICIENT_EVIDENCE/UNAVAILABLE) is the OUTPUT
  layer sitting on top of this memory, exactly as `RECOGNITION_ENGINE_DESIGN.md` §9 already proposed —
  not a separate memory type.

**Explicit, evidence-gated future path (not authorized here)**: embeddings/clustering/example-based memory
remain architecturally possible later, IF the dataset's own volume grows by roughly an order of magnitude
per strategy (a concrete, checkable future re-evaluation trigger, not a vague "someday") — this document
does not propose when or how, only that it is not yet justified.

## 4. How are recognition, statistical estimation, decision, and execution separated?

A strict, one-directional read layering — each layer reads only from the layer below, writes nothing
upward, mirroring every other Phase 7 intelligence layer's own already-proven isolation discipline
(verified by grep/AST scan at every prior checkpoint's own close):

```
Execution         (ExecutionEngine/ExecutionSimulator)        -- untouched, never touched by Recognition
       ^
Decision           (decision_intelligence / decision_intelligence_v2, "Decision Engine")
       ^                -- NOT authorized to consume Recognition Engine's output yet; a future,
       |                   separately-authorized decision, not implied by this design
Recognition        (THIS component)
       ^                -- reads Context Memory's ALREADY-COMPUTED evidence; classifies it into a
       |                   disclosed verdict; computes ZERO new statistics of its own
"Statistics"       (Context Memory's own retrieval.py + evidence.py, Checkpoints 12-13)
       ^                -- the CEO's own named "Statistics Engine" is NOT a new component this design
       |                   proposes building; Context Memory's own evidence-aggregation machinery already
       |                   fills that role for Phase 1's own narrow needs. If a future, genuinely separate
       |                   Statistics Engine (deeper hypothesis testing, multiple-comparison correction,
       |                   confidence calibration beyond evidence.py's own scope) is ever authorized, it
       |                   would sit at THIS layer, between Context Memory and Recognition -- not proposed
       |                   or designed here.
Data               (Learning/Research Feedback capture -> Context Memory repository, CLOSED, §8.30)
```

**The separation is structural, not procedural**: Recognition Engine's own package must never import
`decision_intelligence`/`decision_intelligence_v2`/`execution_engine`/`risk_manager`/`shadow_evidence`/
`learning_feedback` (matching every sibling layer's own already-verified isolation rule,
`PROJECT_STATE_v2.md` §10) — its ONLY runtime dependencies are Context Memory's `retrieval.py` and
`evidence.py` public functions, both unmodified, and Edge Intelligence's own `present_strategy_ids()`
query surface. Recognition Engine writes nothing anywhere — its own output (`RecognitionSnapshot`) is
ephemeral, computed on demand, never persisted back into Context Memory's repository, never automatically
consumed by any decision path.

## 5. How is information leakage prevented?

Four distinct leakage risks, addressed individually, each grounded in verified (not assumed) code
behavior:

1. **Temporal leakage** (using information from after the decision moment): PREVENTED BY CONSTRUCTION —
   `PositionOutcome.observation_id` is always the DECISION-TIME Observation (§1's own verified fact).
   Recognition Engine must additionally respect `retrieval.py`'s own `as_of_cutoff` parameter (Checkpoint
   12's own pre-existing "no future data" invariant) for every query — never bypassed, never
   re-implemented locally.
2. **Outcome leakage** (a query accidentally seeing its own future result, or a result that wouldn't have
   been knowable yet): PREVENTED BY CONSTRUCTION — `evidence.aggregate_evidence()`'s own existing
   filtering (`index.outcomes_for_observation(obs_id, visible_as_of=retrieval.as_of_cutoff)`, inspected
   directly in this project's own source this session) already excludes any `Outcome`/`PositionOutcome`
   that would not have been visible at the query's own `as_of_cutoff`. Recognition Engine must reuse this
   exact mechanism, never compute its own visibility logic.
3. **Train/test contamination**: Phase 1's own memory representation (§3) has NO fitting/training step —
   "training" and "querying" are the same operation (a lookup against already-computed evidence), so there
   is no ML-style train/test split to contaminate. The genuine residual analog risk — a position's own
   outcome contaminating the evidence used to classify it — is prevented by the SAME `as_of_cutoff`
   mechanism in (2): a query issued at a position's own decision time can never retrieve episodes dated
   AFTER that same decision time, so a position can never see itself. **This specific claim (a position
   never appears in its own retrieved evidence) is asserted here as the DESIGNED behavior of Checkpoint
   12's own retrieval contract, not independently re-verified line-by-line this session — §7 requires an
   explicit synthetic negative-control test to confirm it empirically before Recognition Engine is
   considered valid, rather than resting on design intent alone.**
4. **Indirect future identification** (inferring close-time information from decision-time fields):
   checked directly — `position_key`'s own fields (`run_id`, `symbol`, `opened_as_of`, `direction` for
   `PORTFOLIO`-kind) are all decision-time facts; nothing in the decision-time `Observation`/`Context
   Snapshot` encodes any hint of the eventual result. Recognition Engine's own input side (the context it
   queries WITH) must never be constructed from a real `PositionOutcome`/`Outcome` object belonging to the
   position currently being evaluated — a discipline to be enforced by test (§8), not merely assumed.

## 6. Handling of inactive strategies, rare strategies, partial exits, PositionOutcome vs. terminal Outcome, and missing direction/close-reason

- **Inactive strategies** (7 never-`PRESENT`, 8 `PRESENT`-but-zero-`PositionOutcome` — 15/43 total, per
  the audit's own §4): Recognition Engine must return `UNAVAILABLE`/`INSUFFICIENT_EVIDENCE`, never
  fabricate a verdict — this is ALREADY `aggregate_evidence()`'s own existing, tested default behavior
  when a `strategy_id` was never `PRESENT` in any retrieved episode; no new logic is needed to honor this.
- **Rare strategies** (e.g. S29 with 1 `STRATEGY`-kind record, S2/S6/S8 in the single digits): governed by
  `EvidencePolicy`'s own existing, versioned `min_episodes_sufficient`/`min_episodes_limited` thresholds
  — reused unmodified, never a single data point permitted to produce a FAVORABLE/UNFAVORABLE verdict.
- **Partial exits**: `InterimRealization` records are read ONLY as constituents already folded into their
  own `PositionOutcome` (via `constituent_interim_realization_ids`, already aggregated at capture time) —
  never queried or scored as standalone examples, matching their own pre-existing, non-negotiable
  docstring exclusion.
- **`PositionOutcome` vs. terminal `Outcome`**: resolved definitively by §1 — `PositionOutcome` is the
  only valid label; `Outcome` is read only to resolve `PositionOutcome.terminal_outcome_id` for
  traceability/disclosure, never as an independent target.
- **Missing direction/close-reason** (the audit's own "Scientific/Schema Debt, non-blocking" finding,
  officially registered by the CEO, schema unchanged per explicit instruction): Recognition Engine Phase 1
  **does not use either dimension at all.** It must NOT reconstruct direction via `position_key` string
  parsing as a sanctioned feature (that parsing was audit-only investigative tooling over an incidental
  string structure, never a documented data contract, and doing so for `STRATEGY`-kind records is not even
  possible — Shadow's own `position_id` carries no direction field, §3 of the audit). If a future stage
  genuinely needs either dimension, that requires its own separate, explicitly-authorized schema
  extension — not proposed, not designed, not worked around here.

## 7. What evidence is required before Recognition Engine is considered valid?

A staged evidence bar, each item concrete and checkable, mirroring this project's own established
precedent for validating a new statistical layer before real use (the Research Lab's own matched-null
validation; Portfolio Architect's own Phase 2A calibration; every Phase 7 layer's own byte-identical
competitive-execution proof):

1. **Self-matching negative control, empirically confirmed** (not merely designed-in, per §5 item 3): for
   a sample of real positions from the audited dataset, confirm each position's own retrieved evidence set
   never includes itself.
2. **A pre-registered minimum sample-size policy**, decided BEFORE implementation, not tuned after seeing
   results — reusing `MINTR=25` (this project's own established convention) unless a separate, explicit,
   pre-registered justification for a different threshold is documented first.
3. **Calibration check on the existing 688-record dataset**: a chronological split (train on the earlier
   portion of the 12-month window, evaluate classification against the later portion) — does
   Recognition Engine's own `FAVORABLE`/`UNFAVORABLE` classification, where it can be computed at all given
   §3's own sparsity finding, correlate with real subsequent results better than a naive baseline (e.g.
   "always NEUTRAL" or the strategy's own unconditional base rate)? This is the SAME class of validation
   gate every other statistical method in this project has been required to clear (the Research Lab's own
   matched-null Verdict A calibration/power/adversarial/parity battery is the direct precedent) — not
   optional, not skippable because the architecture "looks right."
4. **Byte-identical non-interference proof**: once implemented, confirm Recognition Engine's own presence
   changes nothing about competitive execution, Shadow Evidence, or any existing test's own result — the
   same standing proof every prior Phase 7 layer has delivered.
5. **An explicit adversarial self-review of the implementation against every invariant this document
   states** (§10's own "must-not" list in particular) before any implementation is reported complete —
   matching this project's own standing per-checkpoint discipline.

**None of these five items are satisfied yet** — this document establishes the bar, it does not clear it.

## 8. Negative tests and synthetic controls

- **Random-label shuffle control** (direct methodological reuse of the Research Lab's own matched-null
  validation approach — proven, not invented for this design): shuffle which `PositionOutcome` belongs to
  which context across DIFFERENT, unrelated observations, breaking the true context→outcome association,
  and confirm Recognition Engine's own classification collapses toward `INSUFFICIENT_EVIDENCE`/`NEUTRAL`
  rather than continuing to report confident `FAVORABLE`/`UNFAVORABLE` verdicts on data that no longer
  contains a real pattern.
- **Self-matching control** (§5/§7 item 1): a position must never appear in its own evidence.
- **Time-reversal control**: deliberately feed a later position's own outcome as if it preceded an earlier
  query and confirm this either has no effect (correctly excluded by `as_of_cutoff`) or, if it does have
  an effect, that this is caught as a genuine defect, not silently accepted.
- **Empty/degenerate-input control**: a `(strategy_id, context)` combination with zero matching evidence
  must return `UNAVAILABLE` cleanly — never raise, never fabricate a verdict from nothing.
- **Known-outlier regression control**: the 4 already-identified `PositionOutcome`-vs-terminal-`Outcome`
  sign-mismatch cases (`LEARNING_FEEDBACK_DATASET_AUDIT.md` §2, position keys already on record) must be
  used as concrete, permanent regression fixtures — confirming any future implementation reads
  `PositionOutcome`, never `Outcome`, for these specific, already-understood cases.

## 9. Input and output contract

Unchanged from `RECOGNITION_ENGINE_DESIGN.md` §5 (the accepted architecture), restated here for
completeness against a now-real dataset:

**Input**: a `ContextSnapshot` (the query context, decision-time), an `EdgeIntelligenceSnapshot`
(`present_strategy_ids()` — which edges to evaluate), a `HistoricalIndex` handle (Context Memory's
read-only repository index), `OutcomeKind` (which population — `STRATEGY` is the realistic default per
§4 of the original design, confirmed correct: 575 of 688 records are `STRATEGY`-kind, far denser than
`PORTFOLIO`'s 113), and versioned policy objects (`RetrievalPolicy`, `EvidencePolicy`,
`RecognitionPolicy` — the last still without proposed numeric defaults, per the original design's own
Maturity Verdict item 2, still unresolved by this document).

**Output**: a `RecognitionSnapshot` — one `RecognitionReading` per `PRESENT` edge, each carrying a
`RecognitionVerdict` (`RECOGNIZED_FAVORABLE`/`RECOGNIZED_UNFAVORABLE`/`RECOGNIZED_NEUTRAL`/
`INSUFFICIENT_EVIDENCE`/`UNAVAILABLE`), the full embedded `ContextualEvidenceReport` it was derived from
(complete traceability), and ≥1 disclosed, concrete evidence string. Ephemeral, read-only, never persisted,
never automatically consumed downstream.

## 10. What Recognition Engine may NOT do

A consolidated, explicit list — every item either restates an existing standing constraint this project
already enforces elsewhere, or is newly derived from this document's own analysis above:

- May not execute a trade, submit an order, or size a position (standing, every Phase 7 layer).
- May not produce a BUY/SELL/execution recommendation (standing).
- May not compute a numerical prediction, probability, or expected value — categorical classification of
  already-computed evidence only, v1 (original design §10, reaffirmed).
- May not train or fit any parametric or machine-learned model in Phase 1 (§3, data-volume-justified).
- May not blend evidence across `outcome_kind` (`STRATEGY` vs `PORTFOLIO`) for the same statistic
  (standing, `evidence.py`'s own existing rule).
- May not blend evidence across `strategy_id` (standing, `evidence.py`'s own existing rule).
- May not use information from after its own query's `as_of_cutoff` (§5).
- May not fabricate a verdict when evidence is insufficient — must return `INSUFFICIENT_EVIDENCE`/
  `UNAVAILABLE` honestly (§6).
- May not treat the terminal, per-fill `Outcome` as if it were the position's complete result (§1, proven
  unsafe by the audit's own 4-case finding).
- May not treat `InterimRealization` as a standalone learning example (§1/§6, pre-existing rule).
- May not infer `direction`/close-reason via `position_key` string parsing as a sanctioned feature, or any
  other undocumented reach into fields the current schema does not actually store (§6).
- May not import or modify `learning_feedback`, `shadow_evidence`, `decision_intelligence`,
  `decision_intelligence_v2`, `risk_manager`, `execution_engine`, or any strategy contract/evaluator (§4).
- May not modify Context Memory's own contracts, `retrieval.py`, or `evidence.py` (reused unmodified
  throughout).
- May not be wired into `harness.py` or any execution path without its own separate, explicit CEO
  approval (standing, every Phase 7 layer).

---

## Executive summary

**Proposed architecture**: Recognition Engine sits structurally parallel to Decision Intelligence, both
downstream of Edge Intelligence and Context Memory (`RECOGNITION_ENGINE_DESIGN.md` §3, unchanged). It
answers "does the real historical record favor this edge, in this context" — an empirical counterpart to
Edge Intelligence's own rule-based "does the declared condition hold."

**Unit of learning**: the `(decision-time Observation, terminal PositionOutcome)` pair, per
`(strategy_id, outcome_kind)` — never raw `Outcome` alone (proven unsafe by the audit's own 4/688
sign-mismatch finding), never `StrategyOutcome` as a primary unit, never a temporal sequence (out of
schema/scope for Phase 1).

**Contracts**: input = `ContextSnapshot` + `EdgeIntelligenceSnapshot` + `HistoricalIndex` + `OutcomeKind`
+ versioned policies; output = an ephemeral, read-only `RecognitionSnapshot` (one categorical verdict +
full disclosed evidence per present edge), never persisted, never auto-consumed downstream.

**Separation from Statistics and Decision**: strict, one-directional layering (Data → "Statistics"
[Context Memory's own existing `retrieval.py`/`evidence.py`, not a new component] → Recognition →
Decision → Execution); Recognition computes zero new statistics of its own and writes nothing anywhere.

**Principal risks**:
1. **Data sparsity once conditioned** — the richest strategy has 66 records total; any multi-dimensional
   context conditioning pushes every strategy below this project's own 25-sample sufficiency convention.
   Mitigated by memory representation choice (§3: conditional statistics, not learned models) and by
   honest `INSUFFICIENT_EVIDENCE` reporting rather than forcing a verdict.
2. **Leakage**, structurally well-guarded (temporal/outcome leakage prevented by construction, verified
   via direct code inspection this session) but **not yet empirically tested** — §7/§8's own negative
   controls are required, not optional, before real use.
3. **No calibration evidence yet** — architectural soundness is not the same as predictive validity; §7
   item 3 is unmet.

**Validation tests required**: self-matching control, random-label shuffle control (Research-Lab-style
matched-null methodology reused), time-reversal control, empty-input control, and the 4 known
sign-mismatch cases as permanent regression fixtures (§8) — all required before any implementation is
considered complete, not merely proposed as future work.

**Open questions, genuinely unresolved by this document**:
- `RecognitionPolicy`'s own numeric classification thresholds (still unset — carried over, unresolved,
  from the original design's own Maturity Verdict item 2).
- The exact combination policy a future Decision layer would use to merge Recognition Engine's own
  verdict with Edge Intelligence's rule-based verdict (explicitly out of scope, a separate future
  decision).
- Whether/when the dataset's own volume will justify moving beyond conditional statistics to
  example-based memory (§3) — no timeline proposed, evidence-gated only.

**Recommendation: CONDITIONAL GO.** The architecture is sound, reuses exclusively already-existing,
already-validated Context Memory primitives, and requires no new statistical method beyond what this
project has already built and tested. It is **not, however, unconditionally ready for full
implementation as originally scoped** — the honest data-volume finding in §3 means a first
implementation should be deliberately narrow (single-strategy, single-dimension conditional statistics
only, not full joint multi-dimensional context matching, which the data cannot yet support without
overfitting risk this project's own standing discipline would reject), and must clear the §7/§8 evidence
bar — specifically the self-matching negative control and the chronological calibration check — before
being considered valid for any real use, even read-only. This mirrors, deliberately, Portfolio
Architect's own Phase 2A precedent: architecture accepted, first real implementation scoped narrowly and
gated on evidence generated by that implementation itself, rather than blocked indefinitely or
authorized in full before either question is answered.

**No code has been written. No repository change beyond this document. Awaiting CEO approval.**
