# LEARNING_RESEARCH_FEEDBACK_DESIGN.md — Learning / Research Feedback (Flow B roadmap step 3/6)

**Status: DESIGN ONLY. No code written, no code modified, nothing committed to `ai_trader/`.** Produced
per explicit CEO authorization following the official closure of roadmap step 2/6
(`PROJECT_STATE_v2.md` §8.26). This document defines the scope of "Learning / Research Feedback" — a
name that has existed in the roadmap since the Flow A/B bifurcation (§8.20) but has never been given
content by any official document until now. Nothing here changes runtime behavior, and no implementation
is proposed for adoption without its own separate CEO authorization.

**The central design question, answered directly**: *"Learning / Research Feedback" is not a new concept
requiring invention from nothing — it is the specific, well-scoped role that `ai_trader/context_memory/`'s
own existing contract, `Outcome`, already reserves and names. That type's own docstring
(`contracts.py:312-333`) states it is "the immutable record shape a FUTURE checkpoint will populate once
outcome calculation exists." Its own `SourceType` enum (`enums.py:129-135`) already has exactly two
members: `PRICE_ONLY` and `SHADOW_EVIDENCE_ADAPTER` — the second naming, by design, precisely the data
source this document independently arrives at as the correct one (§4). Learning / Research Feedback is
the bridge that populates Context Memory's already-built, already-tested, currently-empty repository
with real evidence, using adapters that already exist
(`decision_intelligence_v2/adapters.py::build_context_snapshot`/`build_present_edge_reference`) but have
never been called to write anything.**

**Status update (2026-07-21): CEO REVIEW — ACCEPTED WITH REFINEMENTS.** Two design questions were
raised before implementation and are answered in the **Addendum** at the end of this document, which
supersedes §4's original single-Outcome-type framing and §8's original Invariant 6/"no new schema"
framing. Read the Addendum together with §§1–10 below, not as a replacement for them.

---

## 1. Purpose

**The problem**: once a trade closes today, the only persisted artifact is a narrow, execution-focused
`TradeRecord` (entry/exit price, size, pnl, holding_bars, mfe/mae) or its Shadow equivalent
(`ShadowTradeLegRecord`). Neither records *why* the trade was taken — what Market Intelligence believed
about the regime, which edges Edge Intelligence recognized as present, what the full competing candidate
set looked like — nor is that belief-state ever linked back to what eventually happened. Every one of
those ephemeral, decision-moment facts is computed transiently within one bar's own evaluation and
discarded the moment the harness advances. Context Memory (`ai_trader/context_memory/`, Phase 7
Checkpoints 8–13) was built specifically to close this gap — it defines exactly the right immutable
record shapes (`ContextSnapshot`, `PresentEdgeReference`, `Observation`, `Outcome`), a deterministic,
content-addressed (SHA-256) append-only repository, and a deterministic, non-learned retrieval/evidence-
aggregation pipeline (`retrieval.py`, `evidence.py`) — but its write side has **zero real callers**
anywhere in the codebase; every existing `Observation`/`Outcome` construction is confined to test
fixtures.

**Why this component exists**: to be that one missing caller — observing real (or Shadow-virtual) trade
lifecycles as they resolve and translating them into Context Memory's own already-defined contract,
so that its already-built retrieval and evidence-aggregation machinery (currently returning only
degenerate `UNAVAILABLE` reports, since no `Outcome` has ever been written) finally has real evidence to
answer with. **This is a capture-and-populate role, not a new analysis engine and not a new data model.**

---

## 2. Position in the architecture

```
Signal Engine -> Scoring Engine -> Strategy Health filter -> Portfolio Architect -> Risk Manager -> Execution
      |                 |                                                                              |
      | (Market/Edge    |                                                                              | (fills,
      |  Intelligence,   \                                                                             |  closes)
      |  read-only)       \                                                                            v
      v                    v                                                              [Shadow Evidence: every
[Market Intelligence] [Edge Intelligence]                                                  strategy's own virtual
      |                    |                                                               position lifecycle,
      +---------+----------+                                                               unconditional]
                |                                                                                       |
                v  (at decision time, per bar)                                                          v (at resolution)
      +-------------------------------+                                                    +-------------------------+
      |  Learning / Research Feedback  | <---------------- observe (read-only) -----------  |  Shadow Evidence engine  |
      |  (PROPOSED, not implemented)   |                                                    +-------------------------+
      +-------------------------------+
                |  write (append-only)
                v
      [Context Memory Repository] (already built, Phase 7 Checkpoints 8-13)
                |
                v  read (already built)
      [retrieval.py / evidence.py] -> ContextualEvidenceReport
                |
        +-------+--------+
        v                 v
[decision_intelligence_v2]  [offline human/research scripts]
 (optional, advisory-only,
  never feeds back — already
  proven, engine.py:5-11)
```

**Inputs** (all read-only; Learning never writes to or mutates any of them):
- **At decision time, per bar**: Market Intelligence's own snapshot (already computed by the harness's
  own `MarketScanner`/whatever produces `MarketIntelligenceSnapshot` for Decision Intelligence's own use)
  and Edge Intelligence's own PRESENT/POSSIBLE/ABSENT verdicts per strategy — translated via the
  ALREADY-EXISTING `build_context_snapshot`/`build_present_edge_reference` adapters
  (`decision_intelligence_v2/adapters.py:43,76`), never re-derived from scratch.
- **At resolution time**: Shadow Evidence's own `ShadowPositionRecord`/`ShadowTradeLegRecord` for a
  position that has just transitioned to `status="CLOSED"` (§4 explains why Shadow, not the real
  competitive ledger, is the correct source).

**Outputs**: `ContextSnapshot`, `PresentEdgeReference`, `Observation`, and `Outcome` rows appended to the
existing `ContextMemoryRepository` — nothing else. No new data model, no new storage engine.

**Consumers** (already exist, already read-only, already proven non-feedback):
`ai_trader/decision_intelligence_v2` (optional, advisory-only — `context_memory_index` defaults to
`None`, and when present its evidence is attached purely for explanatory display, never touching
eligibility/ranking/scoring/sizing/execution, per that module's own already-audited docstring) and
offline human/research scripts querying the repository directly (matching the established precedent of
`ai_trader/shadow_evidence/{research,comparison,portfolio_research}.py`).

---

## 3. Scope

**Inside this component**:
- Observing the harness's own per-bar, already-computed Market Intelligence/Edge Intelligence state and
  translating it into `ContextSnapshot`/`PresentEdgeReference`/`Observation` via the existing adapters.
- Observing Shadow Evidence's own position-closure events and translating them into `Outcome` rows,
  linked back to their originating `Observation` via `observation_id`.
- Calling Context Memory's own existing `append_context_snapshot`/`append_observation`/`append_outcome`
  (and their batch variants) — nothing more.
- Defining **when** an observation/outcome pair is recorded (§4) and the **normalization** rule for
  `Outcome.normalized_result` (a design decision, not yet made by any existing code — `Outcome`'s own
  docstring leaves this to whatever "future checkpoint" populates it).

**Outside this component** (§5 elaborates why, per responsibility):
- Anything resembling a decision, a ranking, a score, a threshold, or a parameter.
- Any new storage format, schema, or repository — Context Memory's own is reused, not replaced or
  extended with new fields.
- Any change to Market Intelligence, Edge Intelligence, Signal Engine, Scoring Engine, Strategy Health,
  Portfolio Architect, Risk Manager, Execution Engine, or Shadow Evidence's own semantics — all are
  read-only inputs.
- Wiring `decision_intelligence_v2`'s own `context_memory_index` parameter into `harness.py` — that is
  a separate, later, explicitly-flagged-as-not-yet-authorized escalation (§8.18: *"any future checkpoint
  letting Context Memory influence eligibility/ranking/scoring"*), not part of this design.

---

## 4. Information model

Evaluated against the CEO's own candidate list, each with an explicit belongs/doesn't-belong verdict and
justification:

| Candidate | Belongs in Learning's capture? | Why |
|---|---|---|
| Market context (regime, session, multi-timeframe agreement) | **Yes** | This is exactly `ContextSnapshot`'s own existing shape — already defined, already adapter-translatable, the whole reason Context Memory exists. |
| Volatility, structure, momentum, liquidity, expansion | **Yes** | Already individual fields on `ContextSnapshot` — no new modeling required. |
| "Edge present" verdicts (Edge Intelligence's own recognition) | **Yes** | `PresentEdgeReference`'s own existing shape. |
| Execution outcome / trade lifecycle result | **Yes — but see the Addendum below: this is now TWO distinct outcome types (Strategy Outcome, Shadow-sourced; Portfolio Outcome, real-ledger-sourced), not one.** | Originally stated here as "Shadow Evidence only" — refined by CEO review; superseded by the Addendum's own §A1. |
| Accepted signals (real Risk Manager ALLOW) | **Not as new Learning-owned DATA, but see the Addendum: preserved as read-only, non-statistical operational METADATA.** | Original reasoning (avoid duplicating `TradeRecord`) still holds for the DATA itself; refined by CEO review to distinguish "new data" from "preserved metadata" — see Addendum §A2. |
| Rejected signals (real Risk Manager DENY) | **Not as new Learning-owned DATA, but see the Addendum: denial reason + rejection stage preserved as operational metadata.** | Original reasoning (already in `RiskEventRecord`) still holds; refined per Addendum §A2. |
| Strategy Health decisions (`PolicyState`) | **Not as a new classification, but see the Addendum: the already-computed `PolicyState` AT that `as_of` preserved as operational metadata.** | Original reasoning (a separate, already-serving classification) still holds for OWNERSHIP of the classification logic; refined per Addendum §A2 to distinguish "re-deriving/owning" from "recording an already-computed output." |
| Slippage, spread, latency | **No, not as new fields** | Already implicitly reconstructable from `TradeRecord`/`SimFillEvent`'s own existing entry-price-vs-signal-price and timestamp fields where needed for OFFLINE research; Context Memory's own contract is deliberately market-regime-and-outcome-shaped, not an execution-quality ledger — adding new fields to `ContextSnapshot`/`Outcome` is explicitly out of this document's own proposed scope (§3). |
| Portfolio Architect diagnostics | **No, currently** | `ArchitectMode.PASSTHROUGH` produces no decision-relevant diagnostic worth preserving; if a future, separately-authorized policy exists, whether ITS diagnostics belong in Context Memory is a question for THAT authorization, not this one. |

**Why Shadow Evidence, not the real competitive ledger, is the correct Outcome source** — the single
most load-bearing decision in this document, and the reason `SourceType.SHADOW_EVIDENCE_ADAPTER` already
exists as a named enum member:

1. **Evidence sparsity, empirically proven fatal in this exact codebase this session.**
   `PORTFOLIO_ARCHITECT_PHASE2A_CALIBRATION_REPORT.md` found only 19 real competitive ALLOW events across
   43 strategies over an 85-day window — a policy relying on real-trade evidence alone starved before it
   could ever activate. Shadow Evidence, tracking every strategy unconditionally regardless of real
   competitive capacity, produced 88 isolated ALLOWs in the same window from a partial roster, and would
   produce substantially more across the full 43-strategy universe. Sourcing `Outcome` from real trades
   would silently import this same failure mode into Context Memory.
2. **Conflation risk.** A real trade's own occurrence is capacity-and-contention-dependent (the shared
   XAUUSD slot, `LIMIT_MAX_PER_SYMBOL`) — whether a given edge/regime combination produced a REAL trade
   this time reflects portfolio-level competition, not the edge's own quality. Sourcing outcomes from the
   real ledger would conflate "did this edge work" with "did this edge happen to win a scarce shared
   resource" — precisely the contamination Shadow Evidence's entire existence already prevents for
   Strategy Health, and the same argument applies identically here.
3. **Already-established precedent.** Strategy Health already made exactly this choice for exactly this
   reason (`shadow_gate.py`'s own module docstring: real trades are "scarce and shared-slot-contested," so
   gating evidence on them "made the evidence source and the eligibility gate the same resource").
4. **Directly confirmed by the contract itself.** `SourceType.SHADOW_EVIDENCE_ADAPTER` already exists —
   this document did not invent the idea that Shadow Evidence should feed `Outcome`; it confirms what the
   contract's own author(s) already reserved space for.

`Outcome.normalized_result` — proposed convention, not yet decided by any code: `pnl_r` (the same
R-multiple normalization `ClosedTrade`/`WindowMetrics` already use throughout `strategy_health/`), so
Learning reuses an existing, already-validated normalization rather than inventing a new one.
`Outcome.horizon`/`horizon_unit` — proposed: `holding_bars`/`BARS` (the only `HorizonUnit` member that
exists), taken directly from the Shadow position's own already-computed
`aggregate_holding_bars_full`.

---

## 5. Forbidden responsibilities

Explicitly, Learning / Research Feedback **must never**:

- **Signal Engine's**: generate, modify, or suppress a `StrategySignal`.
- **Scoring Engine's**: compute, adjust, or re-derive any `OpportunityScore`/`component_scores`/
  `conflict_penalty`.
- **Strategy Health's**: classify a strategy's own eligibility state, or read/write `PolicyState`.
- **Portfolio Architect's**: reorder, exclude, or prioritize any opportunity.
- **Risk Manager's**: decide ALLOW/DENY, compute sizing, or enforce any limit/guard/cooldown/filter.
- **Execution's**: submit, fill, or reconcile any order.

**Structural guarantee, not just a stated intention**: every one of Learning's own outputs is an
*appended* row in Context Memory's repository — an immutable, content-addressed record with no return
value any caller in the live decision path consumes. `decision_intelligence_v2` (the one production-
shaped reader) already proves, by its own existing, tested design, that Context Memory evidence can be
attached to a candidate purely for explanation without altering `v1`'s own recommendation — Learning
inherits that same non-feedback guarantee by construction, not by new policy.

---

## 6. Feedback philosophy

**Learning must only create structured evidence for future research — it must never change decisions,
parameters, rankings, or thresholds.**

Justification, from three independent angles:

1. **The CEO's own stated goal is explicit and singular**: "a deterministic feedback layer that improves
   future research while preserving reproducibility" — not online learning, not self-modification, not
   optimization. Evidence-only satisfies this literally; anything else would not.
2. **Every existing precedent in this codebase draws the same line, and every one of them was arrived at
   deliberately, not by accident**: Shadow Evidence never gates real trades; `shadow_gate.py`'s own
   eligibility policy is a SEPARATE, explicitly-authorized layer built on TOP of Shadow's own evidence,
   never Shadow itself deciding anything; Context Memory "never recommends" (established naming
   convention, `NEXT_SESSION_FLOW_B.md`'s own warnings section); `decision_intelligence_v2`'s context
   evidence is proven, by its own test suite, to never alter `v1`'s recommendation. Learning sits at the
   START of this same lineage (it only ever WRITES evidence; it never even READS back to influence
   anything) — the most conservative position possible.
3. **This project's own repeated two-stage discipline** (evidence generation, always separated from
   policy authorization, at every single Portfolio Architect phase this session — Phase 2A calibration
   vs. Phase 2 policy design vs. Phase 2B specification, each its own explicit CEO gate) is the working
   pattern to extend, not deviate from. If a future policy ever wants to ACT on Context Memory's own
   evidence beyond today's optional, advisory, non-feedback attachment, that is its own, separate,
   future, explicitly-authorized escalation — not something Learning itself should ever decide.

---

## 7. Research interface

Two already-existing, already-tested surfaces become useful once Learning starts writing real data —
no NEW interface is proposed:

1. **`decision_intelligence_v2`'s own optional `context_memory_index` parameter** — currently always
   `None` in every production path (never wired into `harness.py`, confirmed by direct grep). Once
   Learning has written real `Observation`/`Outcome` pairs, an offline research session could construct a
   `HistoricalIndex` from the repository and pass it to `make_decision_v2` purely for its own EXPLANATORY
   value (a human researcher reviewing why v1 recommended what it did, with contextual historical
   evidence attached) — still never touching v1's own recommendation, per that module's own already-
   proven invariant. Wiring this into the LIVE harness remains a separate, later, unauthorized escalation
   (§3).
2. **Direct repository queries via `retrieval.py`/`evidence.py`** — the same offline-analysis pattern
   `ai_trader/shadow_evidence/research.py`/`comparison.py`/`portfolio_research.py` already established:
   a researcher (human, or a future dedicated research script, matching the `ceo_strategy_constraint_
   root_cause_study.py`-style preserved-diagnostic-artifact convention already used repeatedly this
   session) calls `retrieve()`/`aggregate_evidence()` directly against the repository to ask questions
   like "under HIGH volatility + BULLISH_BOS structure, what has this edge's own historical outcome
   distribution looked like" — entirely offline, entirely after the fact, with zero connection to any
   live decision.

---

## 8. Invariants

Proposed, for whatever implementation eventually follows — all directly inherited from, and consistent
with, Context Memory's own already-built and already-tested guarantees:

1. **Append-only.** Learning never modifies or deletes an existing `ContextSnapshot`/`Observation`/
   `Outcome` — only appends new ones, exactly as `repository.py`'s own existing API already enforces.
2. **Deterministic identity.** Every appended record's own ID is a pure, deterministic function of its
   own content (SHA-256, `identities.py`) — already guaranteed by the repository Learning merely calls.
3. **No look-ahead.** An `Observation` is built ONLY from information available strictly at its own
   `as_of` (Market/Edge Intelligence's own already-computed, point-in-time state); an `Outcome` is
   appended ONLY once its own position has genuinely resolved (`status="CLOSED"`), never speculated in
   advance — `OutcomeStatus.PENDING` exists precisely for the interval between observation and
   resolution, per the contract's own already-defined invariants (`contracts.py:371-398`).
4. **One-way data flow.** Learning reads from the live pipeline and Shadow Evidence; it writes only to
   Context Memory. Nothing downstream of Context Memory (retrieval/evidence/decision_intelligence_v2)
   ever writes back into Learning or into any upstream module.
5. **Minimal schema extension, explicitly justified, never silent.** ~~Originally stated as "no new
   schema" — SUPERSEDED by the Addendum below.~~ Two extensions are now proposed, each with its own
   explicit justification: one new `SourceType` member (Addendum §A1) and one new, separate, optional
   `OperationalMetadata` companion type (Addendum §A2) — never new fields bolted onto
   `ContextSnapshot`/`PresentEdgeReference`/`Observation`/`Outcome` themselves.
6. **Outcome sourcing is explicit and per-type, never blended.** ~~Originally stated as "Shadow-sourced
   outcomes only" — SUPERSEDED by the Addendum below.~~ Strategy Outcome is always Shadow-sourced
   (preventing the capacity-conflation and evidence-sparsity failure modes already proven in this
   project's own history); Portfolio Outcome is always real-ledger-sourced; the two are never merged
   into one number, and every `Outcome` row's own `source_type` field makes which is which
   unambiguous and machine-checkable (Addendum §A1).
7. **Reproducibility.** Given the same underlying simulation run (same seed, same data, same config),
   Learning's own output (the full sequence of appended records) must be byte-for-byte reproducible —
   inherited directly from the harness's own existing, already-proven determinism guarantee.

---

## 9. Failure modes

- **Silent schema drift**: a future maintainer adding a field to `ContextSnapshot`/`Outcome` to serve
  Learning's own convenience, without recognizing this violates invariant 5 and risks the exact
  "PresentEdgeReference deliberately excludes strategy Contract copies" discipline the module was built
  with. Mitigation: any new field requires its own separate, explicit Context Memory design review, not
  a Learning-side workaround.
- **Observation/Outcome linkage drift**: an `Outcome` appended with an `observation_id` that does not
  correspond to a real, previously-appended `Observation` — already guarded structurally by the
  repository's own append API requiring the caller to supply a valid, previously-computed ID, but worth
  a dedicated test once implementation is authorized.
- **Outcome computed from the wrong source** (real ledger instead of Shadow) — the single most likely
  and most consequential mistake, given how tempting real trade data appears at first glance; §4's own
  reasoning must be the primary guard, reinforced by a dedicated negative control (§10).
- **Silent recommendation feedback**: a future change wiring `context_memory_index` into `harness.py`
  without its own separate authorization, treating "Learning now has data" as license to also activate
  the READ side in production — these are two independent authorizations (§3), and conflating them is
  the most likely path toward accidentally reintroducing the "online learning" outcome this whole design
  was built to avoid.
- **Partial/incomplete resolution**: a position that never cleanly closes (e.g. a run ending mid-position,
  handled today by `CLOSE_AT_END` policy) — the resulting `Outcome` must be computed from whatever
  `CLOSE_AT_END` produces (a genuine close, not a fabricated one), or left `PENDING`/`UNAVAILABLE` if the
  run terminates before that resolution — never invented.

---

## 10. Negative controls

How to prove this component is not silently becoming an optimizer, once (if) it is implemented:

1. **No return value influences a decision.** Every call Learning makes into Context Memory's own
   `append_*` API returns only an ID (`ContextSnapshotId`/`ObservationId`/`EdgeEvidenceId`) — a proof-of-
   write receipt, structurally incapable of being consumed as a scoring/ranking/sizing input even if a
   future caller tried, since no live decision-path code holds a reference to Learning's own output.
2. **Byte-identical competitive execution with Learning enabled vs. disabled** — the same proof pattern
   used for every prior additive touch this session (Strategy Health, Portfolio Architect): running the
   harness with and without Learning's own observation hooks active must produce an identical
   `RiskDecisionBatch`/trade ledger, since Learning only ever reads already-computed state and writes to
   a repository nothing else reads during the run.
3. **`decision_intelligence_v2`'s own existing recommendation-equality test suite continues to pass
   unmodified** — direct proof that populating Context Memory with real data does not, even once
   `context_memory_index` is supplied, change `v1`'s own recommendation (already covered by that module's
   own test suite; re-run as a regression, not reinvented).
4. **No optimization objective exists anywhere in Learning's own code** — unlike Portfolio Architect's own
   rejected `STRATEGY_CONCENTRATION_REORDER` candidate, Learning computes no share, no threshold, no
   ranking criterion at all; there is no parameter for "hidden optimization" to hide inside, by
   construction, since the entire component's own output type is "append an immutable record," never
   "return a decision."
5. **Retrieval/evidence-aggregation logic is untouched** — `retrieval.py`'s exact-match-plus-deterministic
   -relaxation-ladder and `evidence.py`'s own statistics (already built, already tested) are consumed
   as-is; Learning proposes zero changes to either, so no new statistical/learned weighting could enter
   through this design even inadvertently.

---

## Addendum (2026-07-21) — CEO-requested refinements: Outcome semantics and operational metadata

**Verdict this addendum implements: ACCEPTED WITH REFINEMENTS.** The overall architecture (§§1–10 above)
stands; this addendum resolves two design questions raised before implementation. Both refinements
**continue from Context Memory's own existing contracts**, per the CEO's own instruction — neither
proposes a parallel subsystem.

### A1. Outcome semantics — Strategy Outcome vs. Portfolio Outcome are both required, and must never merge

The original document's Invariant 6 stated outcomes must always come from Shadow Evidence. **This was too
strong, and is superseded here.** "How did the strategy itself perform?" and "what actually happened in
the live AI Trader?" are genuinely different questions, and collapsing them into one number would hide
exactly the phenomenon this project's own research has spent the most effort measuring this session —
the gap between an edge's own intrinsic quality and what the shared-slot-contested competitive system
actually realized (`CEO_STRATEGY_CONSTRAINT_ROOT_CAUSE_REPORT.md`, `PORTFOLIO_ARCHITECT_PHASE2A_
CALIBRATION_REPORT.md`).

**Both outcome types are required, distinguished by `Outcome.source_type`, never blended:**

| | A. Strategy Outcome | B. Portfolio Outcome |
|---|---|---|
| **Question answered** | How did the strategy itself perform? | What actually happened in the live AI Trader? |
| **Evidence source** | Shadow Evidence (`ShadowPositionRecord`/`ShadowTradeLegRecord`) | Real portfolio/execution ledger (`portfolio_simulator.account.trade_ledger`) |
| **Existence** | Written for essentially every `Observation` — Shadow tracks every configured strategy unconditionally, regardless of real eligibility or capacity | Written ONLY when a real position for that strategy actually opened and closed — the common case, per Phase 2A's own measured evidence (19 real ALLOWs vs. 88 Shadow-isolated ALLOWs in the same window), is that NO Portfolio Outcome exists for a given Observation. **Absence is the expected, correct state, never an error** — it must not be papered over with a fabricated `UNAVAILABLE` row; simply no row is written. |
| **Why this source** | Avoids the evidence-sparsity (Phase 2A) and capacity-conflation failure modes (§4 of the main design) | Answers the genuinely different, system-level question of realized performance under real, capacity-constrained competition — the exact question the Root-Cause Report, Performance Atlas, and Portfolio Architect's own research this session were built to answer, now made retrievable by regime/context instead of requiring a fresh offline study each time |
| **Contract mechanism** | Existing `SourceType.SHADOW_EVIDENCE_ADAPTER` (already present in `enums.py` — no change needed) | **One new `SourceType` member required — the sole schema extension this addendum proposes**: e.g. `PORTFOLIO_LEDGER_ADAPTER`. This is additive to an existing enum, not a new type, not a new field on any dataclass. |
| **Scope** | Per `(observation_id, strategy_id)`, exactly like `Outcome` already is today | Same — the real ledger's own winning strategy for that bar maps directly onto the SAME `Outcome.strategy_id` field; no new scoping concept is introduced |

**How they remain conceptually separate, structurally, not just by convention** (mirroring
`ShadowStrategySummary.source`'s own already-established discipline — *"always `'shadow'` here, never
silently merged with a competitive stream by any downstream consumer"*, `shadow_evidence/types.py`):

- `source_type` is present on every `Outcome` row and is the sole, unambiguous discriminator — never
  inferred from context, never defaulted.
- Any future `evidence.py`-style aggregation MUST group by `source_type` before computing any statistic
  (win rate, mean result, etc.) — aggregating across both types into one number is exactly the failure
  this separation exists to prevent. This is a requirement on any FUTURE implementation, not something
  this addendum builds.
- A single `Observation` may have zero, one, or two `Outcome` rows attached (Strategy only; Portfolio
  only — architecturally rare given real trades require real eligibility; or both) — the retrieval layer
  must treat these as independent, co-existing facts about the same decision moment, never as
  alternates where one supersedes the other.
- **New research question this unlocks** (illustrative only, not proposed for implementation): comparing
  Strategy Outcome against Portfolio Outcome for the same `Observation` set directly measures the
  "realization gap" — how much of an edge's own intrinsic quality was actually captured by the real,
  contested system versus lost to shared-slot competition — a quantified, retrievable-by-regime version
  of what the Root-Cause Study and Phase 2A each had to measure from scratch with bespoke instrumentation.

### A2. Operational metadata — Risk Manager and Strategy Health outputs belong as a separate, optional, non-statistical companion record

**Risk Manager's and Strategy Health's own decisions must never become learning targets — this is
unchanged and non-negotiable.** The question is narrower: should their already-computed OUTPUTS (not
their logic, not a re-derivation) be preserved as read-only historical facts for future diagnostics.

**Answer: yes, they belong — but NOT as new fields on `ContextSnapshot`/`PresentEdgeReference`/
`Observation`/`Outcome` themselves.** Adding them there would risk exactly the failure mode the main
design already flagged (§9, "Silent schema drift") and would blur a boundary the existing package has
already drawn once, deliberately: `PresentEdgeReference`'s own documented exclusion of "any strategy
Contract copy or performance figure" is about not re-embedding a LIVING, evolving reference into a frozen
snapshot. A single bar's ALLOW/DENY outcome and that moment's own `PolicyState`, by contrast, are
discrete, point-in-time historical facts, permanently fixed the instant they occur — architecturally
closer to `ContextSnapshot`'s own "frozen belief-state at one moment" pattern than to a "living reference"
the exclusion warns against. That distinction is what makes preservation legitimate here where a Contract
copy would not be.

**Proposed shape (design only, not implemented)** — a new, small, strictly optional companion type,
e.g. `OperationalMetadata`, one row per `(observation_id, strategy_id)`, mirroring `Outcome`'s own
existing scope:

```
observation_id: ObservationId          # FK, same pattern as Outcome
strategy_id: str
risk_decision: "ALLOW" | "DENY"        # Risk Manager's own already-computed output, recorded, not re-derived
denied_reason_code: str | None         # from the existing DeniedReason, unchanged
rejection_stage: str | None            # which gate (pre-trade filter / portfolio limit / guard / cooldown / sizing) -- mirrors AppliedRule's own existing concept, unchanged
strategy_health_policy_state: str | None   # shadow_gate.py's own already-computed PolicyState at this as_of, read only
```

**Why this does not violate ownership boundaries**:
- Risk Manager still, and only, OWNS the act of deciding ALLOW/DENY — Learning never re-executes any gate,
  never re-derives a denial reason; it records a fact Risk Manager already produced, exactly the same
  relationship `PresentEdgeReference` already has with Edge Intelligence's own `declared_status` (records
  Edge Intelligence's OUTPUT, never re-implements Edge Intelligence).
- Strategy Health still, and only, OWNS the classification logic (`shadow_gate.py`'s frozen, unmodified
  `policy_states_at()`) — Learning reads its OUTPUT at one `as_of`, never recomputes or second-guesses it.
- The field is explicitly, structurally kept OUT of any statistical computation: `retrieval.py`'s own
  matching dimensions and `evidence.py`'s own aggregated statistics must never read
  `OperationalMetadata` — it exists purely for direct, human/offline diagnostic queries (e.g. "show every
  DENY reason for strategy X under HIGH volatility, cross-referenced with its own Strategy Outcome") —
  satisfying the CEO's own framing precisely: *"The purpose is NOT decision making. The purpose is future
  diagnostics and research."*
- Being a SEPARATE, optional type (not new fields on the core four) means it can be entirely absent
  (e.g., for observations predating Strategy Health's own policy layer) without touching any existing
  type's own already-tested shape, and a future maintainer cannot accidentally wire it into
  `retrieval.py`'s own query dimensions without that itself being a visible, separate, reviewable change.

### Revised invariants (supersede §8 items 5 and 6 above, all other invariants unchanged)

- **Item 5, revised**: "No new schema" is replaced by "minimal, explicit, additive schema extension" — one
  new `SourceType` enum member (A1) and one new, separate, optional `OperationalMetadata` type (A2).
  Both are additive to existing structures; neither modifies an existing field or an existing type's own
  already-tested shape.
- **Item 6, revised**: "Shadow-sourced outcomes only" is replaced by "outcome sourcing is explicit and
  per-type, never blended" (A1's own table).
- **New invariant 8**: `OperationalMetadata` is never read by `retrieval.py` or `evidence.py` — it is a
  write-once, read-only-by-humans-or-offline-scripts record, structurally excluded from every statistical
  or matching computation this package performs.

### Updated negative control (extends §10)

6. **`OperationalMetadata` never appears in any `RetrievalQuery` field or any `ContextualEvidenceReport`
   statistic** — directly checkable once implemented by confirming neither `retrieval.py` nor
   `evidence.py` imports or references the new type at all.

---

## Governance confirmation

No code was written or modified. No new module was created. No `ai_trader/` file was touched. Zero diff
confirmed against every frozen module, every Flow A artifact, and Context Memory's own existing package
(read, never written to, by this research). This document proposes an information model and a component
boundary only — implementation, if ever authorized, is a separate, later, explicit CEO decision.
