# LEARNING_RESEARCH_FEEDBACK_IMPLEMENTATION_PLAN.md — Implementation Plan (Flow B roadmap step 3/6)

**Status: PLANNING ONLY. No code written, no code modified, nothing committed to `ai_trader/`.** Produced
per explicit CEO authorization following the FINAL APPROVAL of `LEARNING_RESEARCH_FEEDBACK_DESIGN.md`
(commit `b150f1e`, Normative Model). This document plans the implementation described there — it does
not revisit any design decision. **No runtime change is authorized by this document; implementation
begins only after this plan is itself explicitly reviewed and approved.**

---

## 0. Required / optional / deferred — summary

**REQUIRED** (the minimum implementation that fulfills the approved Normative Model):
- `context_memory/enums.py`: `OutcomeKind`, `SourceType.REAL_PORTFOLIO_LEDGER`.
- `context_memory/contracts.py`: `Outcome.outcome_kind` field + kind/source validation; new
  `OperationalMetadata` type + its ID wrapper.
- `context_memory/identities.py`: `compute_operational_metadata_id`.
- `context_memory/repository.py`: `append_operational_metadata` (+ batch variant).
- `context_memory/evidence.py`: `aggregate_evidence`/`aggregate_all_present_edges` must filter/group by
  `OutcomeKind` — **identified during this planning pass, not previously flagged**; without this, real
  Portfolio Outcomes would silently blend into Strategy Outcome statistics the moment both exist,
  violating the Normative Model's own statistical-separation rule. See §3.5.
- New package `ai_trader/learning_feedback/` (adapters + write-path entry points).
- One new, additive `SimulationHarness` constructor parameter + two new call sites in `_run_one_bar`.
- Required updates to existing `Outcome`-constructing test fixtures (`context_memory/tests/_fixtures.py`,
  `context_memory/tests/test_outcome.py`, `decision_intelligence_v2/tests/_fixtures.py`) to supply the
  new required field — a real, disclosed code touch, not hidden.
- Full test plan, §13.

**OPTIONAL** (would improve the implementation but is not necessary for the approved model to hold):
- A dedicated, tested `ObservationIndex` helper class for the within-run `(strategy_id, symbol,
  entry_as_of) → observation_id` correlation, rather than harness-local inline state (§5).
- Structured logging/metrics for Learning's own write volume and failure counts.
- `context_memory/validation.py` — inspect during implementation; extend only if it independently
  re-validates `Outcome`'s own shape outside `contracts.py`'s own `__post_init__` (not confirmed either
  way by this planning pass — flagged for verification, not assumed).

**DEFERRED** (explicitly out of scope for this implementation, requires its own future authorization):
- Wiring `decision_intelligence_v2`'s own `context_memory_index` into `harness.py` live (already excluded
  by the design's own §3; reaffirmed here).
- Any `SourceType` member beyond `REAL_PORTFOLIO_LEDGER` (e.g. a future MT5 Live broker-execution
  source) — "further source types only when separately authorized" (Normative Model).
- Any capture of slippage/spread/latency as new fields.
- Any capture of Portfolio Architect diagnostics (moot today — `PASSTHROUGH` only).
- Any change to `retrieval.py` (confirmed not required — it matches on `ContextSnapshot`/`Observation`
  fields only; `Outcome` is resolved separately, after retrieval, via `outcomes_for_observation`).

---

## 1. Exact files expected to change

**New files:**
- `ai_trader/learning_feedback/__init__.py`
- `ai_trader/learning_feedback/adapters.py` — `build_strategy_outcome`, `build_portfolio_outcome`,
  `build_operational_metadata` (pure functions; §3).
- `ai_trader/learning_feedback/capture.py` — the two write-path entry functions the harness calls
  (§4/§5).
- `ai_trader/learning_feedback/config.py` — `LearningFeedbackConfig` (the new, additive, default-`None`
  harness parameter's own type).
- `ai_trader/learning_feedback/tests/__init__.py`
- `ai_trader/learning_feedback/tests/test_adapters.py`
- `ai_trader/learning_feedback/tests/test_capture.py`
- `ai_trader/simulation/tests/test_learning_feedback_integration.py`

**Modified files (required):**
- `ai_trader/context_memory/enums.py` — additive: `OutcomeKind` enum, one new `SourceType` member.
- `ai_trader/context_memory/contracts.py` — additive: `Outcome.outcome_kind` field + `__post_init__`
  validation; new `OperationalMetadata` dataclass + `OperationalMetadataId`.
- `ai_trader/context_memory/identities.py` — additive: `compute_operational_metadata_id`.
- `ai_trader/context_memory/repository.py` — additive: `append_operational_metadata` +
  `append_operational_metadatas` (batch), new backing JSONL file, mirroring `append_outcome`'s own
  existing pattern exactly.
- `ai_trader/context_memory/evidence.py` — additive: `aggregate_evidence`/`aggregate_all_present_edges`
  gain an explicit `outcome_kind: OutcomeKind` parameter (no silent default that could mask cross-kind
  blending); internal Outcome-selection logic filters by it.
- `ai_trader/context_memory/tests/_fixtures.py`, `ai_trader/context_memory/tests/test_outcome.py`,
  `ai_trader/decision_intelligence_v2/tests/_fixtures.py` — required, mechanical: every existing
  `Outcome(...)` construction gains the new required `outcome_kind` argument.
- `ai_trader/simulation/harness.py` — one new, additive constructor parameter
  (`learning_feedback_config: LearningFeedbackConfig | None = None`, default `None` = current behavior,
  unchanged) and two new call sites in `_run_one_bar` (§4/§5), matching the exact convention of every
  prior touch (`health_eligible_ids`, `portfolio_architect_config`).

**Files explicitly NOT touched**: `risk_manager/`, `strategy_health/{types,metrics,scoring,classifier,
evaluator}.py`, `shadow_gate.py`, `signal_engine/`, `scoring_engine/`, `execution_engine/`,
`shadow_evidence/` (semantics unchanged — read-only consumer), `retrieval.py`, `episodes.py`,
`index.py`, `codec.py`, `identities.py`'s own existing functions, `portfolio_architect/`, all Flow A
artifacts.

---

## 2. Exact contracts and enums to be added or extended

```python
# context_memory/enums.py (additive)

class OutcomeKind(str, Enum):
    """What an Outcome represents. Small, closed, stable -- per the Normative Model, expected to
    remain exactly these two members for the foreseeable future."""
    STRATEGY = "STRATEGY"
    PORTFOLIO = "PORTFOLIO"

class SourceType(str, Enum):          # EXISTING enum, ONE member added
    PRICE_ONLY = "PRICE_ONLY"                     # unchanged
    SHADOW_EVIDENCE_ADAPTER = "SHADOW_EVIDENCE_ADAPTER"   # unchanged
    REAL_PORTFOLIO_LEDGER = "REAL_PORTFOLIO_LEDGER"       # NEW

class ContextRiskDecision(str, Enum):   # NEW, local mirror -- per enums.py's own established design
    """Local mirror of risk_manager.types.Decision, per this package's own stated rationale (enums.py:
    1-24): every upstream-originating vocabulary is a local mirror, zero import dependency."""
    ALLOW = "ALLOW"
    DENY = "DENY"
```

```python
# context_memory/contracts.py (additive)

@dataclass(frozen=True, slots=True)
class Outcome:                         # EXISTING dataclass, ONE field added
    observation_id: ObservationId
    strategy_id: str
    horizon: int
    horizon_unit: HorizonUnit
    outcome_definition_version: SchemaVersion
    status: OutcomeStatus
    observation_as_of: int
    normalized_result: float | None
    resolution_as_of: int | None
    cost_model_ref: str
    source_type: SourceType
    outcome_kind: OutcomeKind          # NEW field

    def __post_init__(self) -> None:
        ...                             # EXISTING invariants, unchanged
        _VALID_KIND_SOURCE_PAIRS = {
            (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER),
            (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER),
        }
        if (self.outcome_kind, self.source_type) not in _VALID_KIND_SOURCE_PAIRS:
            raise ValueError(
                f"Outcome: invalid (outcome_kind, source_type) pair "
                f"({self.outcome_kind!r}, {self.source_type!r}) -- only "
                f"{sorted(_VALID_KIND_SOURCE_PAIRS)} are currently valid"
            )

@dataclass(frozen=True, slots=True)
class OperationalMetadataId:            # NEW, mirrors ObservationId/EdgeEvidenceId's own shape
    value: str

@dataclass(frozen=True, slots=True)
class OperationalMetadata:              # NEW type, per the Normative Model / Addendum §A2
    observation_id: ObservationId
    strategy_id: str
    risk_decision: ContextRiskDecision
    denied_reason_code: str | None
    rejection_stage: str | None
    strategy_health_policy_state: str | None

    def __post_init__(self) -> None:
        if self.risk_decision is ContextRiskDecision.DENY and self.denied_reason_code is None:
            raise ValueError("OperationalMetadata: a DENY must carry a denied_reason_code")
        if self.risk_decision is ContextRiskDecision.ALLOW and self.denied_reason_code is not None:
            raise ValueError("OperationalMetadata: an ALLOW must not carry a denied_reason_code")
```

`identities.py` gains `compute_operational_metadata_id(metadata: OperationalMetadata) ->
OperationalMetadataId`, mirroring `compute_edge_evidence_id`'s own existing SHA-256-over-content pattern
exactly (no new hashing scheme).

`repository.py` gains `append_operational_metadata(self, metadata: OperationalMetadata) ->
OperationalMetadataId` and `append_operational_metadatas(...)` (batch), mirroring `append_outcome`'s own
existing structure line-for-line — one new backing JSONL file, same idempotent-append discipline already
proven for the other three record types.

---

## 3. Adapter responsibilities

All adapters are **pure functions** — no I/O, no side effects, no exceptions for expected-missing data
(return `None`/skip instead), mirroring `decision_intelligence_v2/adapters.py`'s own existing style.

### 3.1 Reused, unmodified

`decision_intelligence_v2/adapters.py::build_context_snapshot(mi_snapshot) -> ContextSnapshot` and
`build_present_edge_reference(strategy_id, contract) -> PresentEdgeReference` — called, not
reimplemented, for the decision-time write path.

### 3.2 New — `build_strategy_outcome`

```python
def build_strategy_outcome(
    position: ShadowPositionRecord, observation_id: ObservationId, observation_as_of: int,
) -> Outcome | None:
```
Returns `None` if `position.status != "CLOSED"` (not yet resolvable) or if
`position.aggregate_net_pnl is None`. Otherwise builds `Outcome(outcome_kind=STRATEGY,
source_type=SHADOW_EVIDENCE_ADAPTER, status=RESOLVED, resolution_as_of=position.full_exit_as_of,
horizon=position.aggregate_holding_bars_full, horizon_unit=BARS, ...)`.
`normalized_result` — **open detail, to confirm during implementation** (§9): proposed to reuse
`pnl_r` from the position's own constituent `ShadowTradeLegRecord.leg` (a `TradeRecord`, which already
carries `pnl_r: float | None`) — needs verification that this is populated for every closed Shadow
position, not just some.

### 3.3 New — `build_portfolio_outcome`

```python
def build_portfolio_outcome(
    trade: TradeRecord, observation_id: ObservationId, observation_as_of: int,
) -> Outcome:
```
Simpler than 3.2: `TradeRecord.pnl_r` already exists directly (confirmed,
`portfolio_simulator.py:66`), no reconstruction needed. Builds `Outcome(outcome_kind=PORTFOLIO,
source_type=REAL_PORTFOLIO_LEDGER, status=RESOLVED, resolution_as_of=trade.exit_as_of,
horizon=trade.holding_bars, horizon_unit=BARS, normalized_result=trade.pnl_r, ...)`.

### 3.4 New — `build_operational_metadata`

```python
def build_operational_metadata(
    decision: RiskDecision, policy_state: str | None, observation_id: ObservationId,
) -> OperationalMetadata:
```
Maps `decision.decision` (Risk Manager's own `Decision.ALLOW`/`Decision.DENY`) to the local
`ContextRiskDecision` mirror; `denied_reason_code` from `decision.denied_reasons[0].code` if any deny
reasons exist (first/primary reason — `rejection_stage` derived from which gate group produced it,
matching `AppliedRule`'s own existing rule-name-to-stage grouping, e.g. `LIMIT_MAX_PER_SYMBOL` →
`"portfolio_limit"`, `SIZE_BELOW_MIN` → `"sizing"` — an explicit, small, static mapping table, not new
logic duplicating Risk Manager's own gate chain).

### 3.5 Required, non-adapter touch — `evidence.py` kind-awareness

`aggregate_evidence`/`aggregate_all_present_edges` currently pull "the `Outcome` attached to that
episode's first member observation" (per `evidence.py:211`, confirmed during design research) with no
kind filter — because `OutcomeKind` did not exist when that code was written. Once Learning writes both
kinds, this code would silently blend Strategy and Portfolio outcomes into one statistic unless it is
updated. **Required change**: both functions gain an explicit `outcome_kind: OutcomeKind` parameter (no
default — callers must state intent), and the internal per-episode Outcome lookup filters to that kind
only. This is the one place outside `ai_trader/learning_feedback/` itself and the four `context_memory/`
files above that must change for the Normative Model's own statistical-separation rule to actually hold
once real data exists — flagged here precisely because it is easy to miss (evidence.py predates the
concept it now needs to respect).

---

## 4. Decision-time write path

**Where**: `harness.py::_run_one_bar`, inside the existing per-symbol loop, placed AFTER the Shadow
Evidence tap and AFTER the `health_eligible_ids` filter (i.e., the same general region as Portfolio
Architect's own call site) but reading from the FULL, unfiltered `score_batch` — same principle Shadow's
own tap already establishes: Learning's own decision-time capture must never be gated by Strategy
Health/Portfolio Architect/Risk Manager's own eligibility or acceptance decisions, or it would
under-observe exactly the strategies whose outcomes are most interesting to compare (excluded ones).

**What**: once per bar (not per strategy), if `learning_feedback_config is not None`:
1. Build `ContextSnapshot` from the bar's own already-computed Market Intelligence snapshot (via the
   reused, unmodified adapter, §3.1). Skip the whole bar's capture if Market Intelligence data quality is
   insufficient (§11) — never fabricate.
2. For every candidate in `score_batch.scores` (matching Risk Manager's own full input population, not
   just eligible ones): build `PresentEdgeReference` (via the reused adapter) if Edge Intelligence
   recognizes it as PRESENT or POSSIBLE (matching that adapter's own existing scope — ABSENT edges are
   not referenced, mirroring `PresentEdgeReference`'s own name and existing semantics).
3. Bundle into one `Observation` (one `ContextSnapshot`, the tuple of that bar's own `PresentEdgeReference`s).
4. `repository.append_observation(observation)` → `observation_id`.
5. For every strategy with a real `RiskDecision` this bar (from `decision_batch.decisions`, already
   computed downstream in the SAME bar — §8 handles the exact sequencing since decision-time capture
   logically needs the RiskDecision, which is computed slightly later in the existing per-bar order; see
   §8 note): build and append `OperationalMetadata` (§3.4), linked to this `observation_id`.
6. Record `(strategy_id, symbol, as_of) → observation_id` in Learning's own in-memory, run-scoped
   correlation map (§5) for later resolution-time linkage.

---

## 5. Resolution-time write path

**Two independent trigger points**, since Strategy Outcome (Shadow) and Portfolio Outcome (real) resolve
on their own, generally different, schedules:

**(a) Shadow resolution** — immediately after the harness's own existing
`self.shadow_engine.settle_bar(...)` call: for every `ShadowPositionRecord` that just transitioned to
`status="CLOSED"` this bar (Shadow's own engine already exposes this — no new tracking needed beyond
reading its own already-updated `positions` collection), look up the correlation map for
`(strategy_id, symbol, entry_as_of)` → `observation_id`; if found, build and append a Strategy Outcome
(§3.2); if NOT found (§11 — e.g. Learning was enabled mid-run), drop and log, never fabricate a
placeholder observation.

**(b) Real resolution** — immediately after the harness's own existing
`self.portfolio_simulator.apply(fills, ...)` call: for every NEW `TradeRecord` appended to
`account.trade_ledger` this bar, same correlation-map lookup, build and append a Portfolio Outcome (§3.3).

**Correlation map** (proposed, run-scoped, in-memory only, never persisted — it is not part of Context
Memory's own schema, purely a within-run linking aid): `dict[tuple[str, str, int], ObservationId]` keyed
by `(strategy_id, symbol, entry_as_of)`. Cleared at the end of the run. Whether this lives as a small
private attribute on the harness itself or inside a dedicated, separately-tested helper class
(`ObservationIndex`, OPTIONAL per §0) is an implementation-detail choice, not a design question.

---

## 6. Strategy Outcome construction

Covered in full in §3.2. Summary of field derivation:

| `Outcome` field | Derived from |
|---|---|
| `observation_id` | Correlation-map lookup (§5) |
| `strategy_id` | `position.strategy_id` |
| `horizon` / `horizon_unit` | `position.aggregate_holding_bars_full` / `BARS` |
| `status` | `RESOLVED` |
| `observation_as_of` | The original `Observation`'s own `as_of` |
| `normalized_result` | `pnl_r` from the position's own leg data — **verify during implementation** |
| `resolution_as_of` | `position.full_exit_as_of` |
| `cost_model_ref` | The run's own `SimulationContext.cost_model` identifier — **exact string format to confirm during implementation** |
| `source_type` | `SHADOW_EVIDENCE_ADAPTER` |
| `outcome_kind` | `STRATEGY` |

---

## 7. Portfolio Outcome construction

Covered in full in §3.3. Same field derivation table as §6, with `TradeRecord` as the source
(`trade.pnl_r`, `trade.exit_as_of`, `trade.holding_bars` all already exist, confirmed directly) and
`source_type=REAL_PORTFOLIO_LEDGER`, `outcome_kind=PORTFOLIO`.

---

## 8. OperationalMetadata construction

Covered in full in §3.4. **Sequencing note**: `_run_one_bar`'s existing order computes `score_batch` →
Shadow tap → `health_eligible_ids` filter → Portfolio Architect → `decision_batch =
risk_manager.evaluate(...)`. Decision-time Observation capture (§4) needs `score_batch` (available
early) for `ContextSnapshot`/`PresentEdgeReference`, but `OperationalMetadata` needs `decision_batch`
(available later, after Risk Manager runs). **Resolution**: split decision-time capture into two
sub-steps at their own natural points in the existing order — `Observation` (and its `observation_id`)
recorded right after `score_batch` is available (matching Shadow's own placement), with
`OperationalMetadata` recorded immediately after `decision_batch` is computed (a few lines later, still
within the same bar/symbol iteration, same conceptual "decision time"). Both reference the SAME
`observation_id` computed in the first sub-step. This does not require reordering any existing call —
only inserting two new, small, sequential call sites at their own already-correct points.

---

## 9. Validation invariants

- `Outcome.__post_init__` — kind/source pairing (§2), plus all EXISTING invariants unchanged
  (`RESOLVED` requires `normalized_result`/`resolution_as_of` set; `PENDING` requires both absent, etc.).
- `OperationalMetadata.__post_init__` — DENY requires a reason code; ALLOW must not carry one (§2).
- **Open details requiring confirmation during implementation** (disclosed, not silently assumed):
  (a) whether Shadow's own `ShadowTradeLegRecord.leg.pnl_r` is populated for every closed position or
  only some, and the fallback if absent; (b) the exact string format for `cost_model_ref`.

---

## 10. Idempotency and duplicate-write prevention

**Inherited, not built.** The existing repository already provides deterministic, content-addressed
(SHA-256) identity and idempotent append for every record type (`identities.py`/`repository.py`,
confirmed during design research) — Learning's own new calls (`append_operational_metadata` included)
get this for free, PROVIDED the adapters (§3) are pure and deterministic, which they are by construction
(no randomness, no wall-clock reads, same inputs always produce the same dataclass content, hence the
same computed ID). The only NEW discipline Learning itself must uphold: never call `append_observation`
more than once for the conceptually same decision-time event within a run — guaranteed structurally by
the harness's own per-bar, per-symbol loop already processing each `(symbol, as_of)` exactly once.

---

## 11. Failure handling

Mirrors Shadow Evidence's own established defense-in-depth convention exactly (already used twice this
session — Shadow's own `observe()` wrapper, and this design's own §8/§9 anticipated it): every one of
Learning's own write-path calls is wrapped in `try/except`, catching, logging, and continuing —
**Learning must never fail or alter the real competitive run.**

- **Missing/degraded Market Intelligence data** → skip that bar's own `Observation` write entirely; do
  not fabricate a `ContextSnapshot` with invented values (mirrors `ContextDataQualityState` already
  existing precisely to describe this, rather than pretending it away).
- **Shadow/real resolution with no matching `observation_id`** (e.g. Learning enabled mid-run, or a
  data-quality gap suppressed the original write) → drop, log, never invent a placeholder `Observation`
  after the fact — an `Outcome` must never exist without its own real, previously-recorded `Observation`.
- **Any unexpected exception anywhere in the write path** → caught at the outermost call site inside
  `_run_one_bar`, logged, competitive execution continues untouched — the same hard guarantee Shadow
  Evidence already provides.

---

## 12. Backward compatibility

- **Zero for the harness/runtime**: the entire feature is opt-in via one new, additive, default-`None`
  constructor parameter. Every existing test, fixture, and committed result is unaffected until a caller
  explicitly opts in — identical convention to every prior touch this session.
- **Real, disclosed cost for existing Context Memory test fixtures**: `Outcome.outcome_kind` is proposed
  as a REQUIRED field (not defaulted) — deliberately, since a defaulted value risks silently mislabeling
  a future Portfolio-kind test fixture as `STRATEGY` by accident, and this project has repeatedly
  preferred explicit correctness over convenient defaults (e.g. Strategy Health's own PROBATION-is-
  Shadow-only decision). This means every EXISTING `Outcome(...)` construction in
  `context_memory/tests/_fixtures.py`, `context_memory/tests/test_outcome.py`, and
  `decision_intelligence_v2/tests/_fixtures.py` must be updated to supply the new argument — a small,
  mechanical, but real touch to existing test files, listed explicitly in §1 rather than left implicit.

---

## 13. Test plan

- **`ai_trader/learning_feedback/tests/test_adapters.py`** (unit, pure-function): each of the three
  adapters (§3.2–3.4) — happy path, `None`/skip path (unresolved position, missing data), and the
  kind/source validation being actually enforced (constructing an invalid pair raises).
- **`ai_trader/learning_feedback/tests/test_capture.py`** (unit): the correlation-map lookup/miss
  behavior (§5/§11) in isolation, without a full harness run.
- **`ai_trader/context_memory/tests/test_outcome.py`** (extended): the new `outcome_kind` field and its
  `__post_init__` validation — both valid pairings accepted, both invalid pairings rejected.
- **`ai_trader/context_memory/tests/test_evidence.py`** (extended): `aggregate_evidence`'s new
  `outcome_kind` parameter actually filters — construct both a Strategy and a Portfolio `Outcome` for
  the same `Observation`, confirm each `aggregate_evidence` call sees only its own kind.
- **`ai_trader/simulation/tests/test_learning_feedback_integration.py`** (harness-level, real data):
  1. Byte-identical competitive execution, `learning_feedback_config=None` (default) vs. explicit `None`
     vs. omitted entirely — the mandatory first proof, matching every prior touch.
  2. With Learning enabled over a small fixture window: confirm `Observation`/`Outcome`/
     `OperationalMetadata` rows are actually appended, and a Strategy Outcome exists for at least one
     closed Shadow position.
  3. Confirm a bar with NO real trade produces NO Portfolio Outcome (the absence rule, Normative Model)
     — never a fabricated `UNAVAILABLE` row.
  4. Confirm `OperationalMetadata` is recorded for both an ALLOW and a DENY case, with the DENY carrying
     a `denied_reason_code`.
- **Regression, re-run unmodified**: `context_memory/` (full existing suite), `decision_intelligence_v2/`
  (full existing suite, proving its own recommendation-equality invariant still holds untouched),
  `strategy_health/`, `portfolio_architect/`, `test_shadow_disabled_parity.py` (43-strategy parity,
  since `harness.py` is touched again).
- **mypy**: expected to be blocked by the same machine-level Application Control policy already disclosed
  twice this session (Strategy Health, Portfolio Architect reports) — not a new issue, will be
  re-disclosed, not silently skipped.

---

## 14. Rollback plan

Identical shape to every prior touch: omitting (or leaving `None`) the new `learning_feedback_config`
parameter reverts the harness to its current, already-proven-byte-identical behavior — no data migration
needed to roll back the RUNTIME feature, since Context Memory's own repository is append-only and simply
halting future writes requires no cleanup of past ones (there are none yet). The one asymmetric cost:
`Outcome.outcome_kind` is a required-field schema change at the `context_memory/` package level,
independent of the harness toggle — rolling back the RUNTIME feature does not require reverting this
schema change (harmless today, zero real data exists); reverting the SCHEMA change itself, if ever
needed, would require re-touching the same test fixtures again, a real but currently zero-risk cost
(disclosed, not hidden).

---

## 15. Explicit proof that Flow A remains untouched

Every file listed in §1 is under `ai_trader/context_memory/`, `ai_trader/learning_feedback/` (new),
`ai_trader/simulation/`, or `ai_trader/decision_intelligence_v2/tests/` — all Flow B/AI-Trader-only
paths, structurally disjoint from Flow A's own root-level-markdown-only footprint
(`NEXT_SESSION_FLOW_A.md`, `edge_research/`, the three `EDGE_*.md` documents) and from the
`ai_quant_lab-alpha-discovery` worktree, which this plan never proposes accessing. At implementation
time, the same verification already used at every prior step applies: `git status --porcelain --
NEXT_SESSION_FLOW_A.md edge_research EDGE_DISCOVERY_REGISTRY_v1.md EDGE_RESEARCH_PROTOCOL.md
EDGE_DISCOVERY_ROADMAP.md` must return empty both before and after the implementation commit.

---

## Governance confirmation

No code was written or modified. No contract or schema was changed. No `ai_trader/` file was touched.
This is a plan only — implementation requires its own separate, explicit CEO approval of this document.
Zero diff confirmed against every frozen module, Flow A, and Context Memory's own existing package.
