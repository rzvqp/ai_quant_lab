"""Immutable data contracts -- Phase 7 Checkpoint 9.

Every dataclass here is ``@dataclass(frozen=True)`` and validates itself in ``__post_init__`` -- an
invalid or ambiguous construction raises :class:`~ai_trader.context_memory.validation.
ContextMemoryValidationError` immediately, never silently accepting bad data (this repository's own
"never fabricate" convention, applied to construction-time validation).

**No outcome/future-data field exists anywhere on :class:`ContextSnapshot` or :class:`Observation`** --
Checkpoint 9 §D's own explicit exclusion list (realized return, future price, MFE/MAE, win/loss label,
trade result, future volatility, later strategy verdict, execution result) is enforced by omission, and
verified by a dedicated test asserting none of those field names ever appears
(``tests/test_context_snapshot.py::test_no_future_data_fields``).

**``__hash__``/``__eq__`` note**: ``@dataclass(frozen=True)`` gives every contract Python's own built-in
value-equality and hashability (for ordinary in-process container use -- e.g. holding a
:class:`ContextSnapshot` in a Python ``set`` during a test). This is UNRELATED to this package's own
record identity (:mod:`ai_trader.context_memory.identities`), which is computed exclusively via
``hashlib.sha256`` over a canonical serialization -- Python's built-in ``hash()`` is never used for
record identity anywhere in this package (Checkpoint 9 §H's own explicit prohibition).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.context_memory.enums import (
    ContextAgreementLevel,
    ContextDataQualityState,
    ContextEdgeStatus,
    ContextExpansionState,
    ContextLiquidityState,
    ContextMomentumState,
    ContextRiskDecision,
    ContextStructureState,
    ContextTrendDirection,
    ContextVolatilityRegime,
    HorizonUnit,
    OutcomeKind,
    OutcomeStatus,
    OutcomeUnavailableReason,
    SourceType,
)
from ai_trader.context_memory.validation import (
    ContextMemoryValidationError,
    require_finite_float_or_none,
    require_non_empty_str,
    require_positive_int,
    require_unit_interval_or_none,
)

# ---------------------------------------------------------------------------------------------------
# Schema/definition versions (Checkpoint 9 §C) -- see identities.py for how these participate in hashing.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SchemaVersion:
    """One immutable, deterministic version identifier. IMPLEMENTATION CHOICE: a single, generic type
    parameterized by ``namespace`` serves every one of Checkpoint 9 §C's six required version kinds
    (Context Memory's own record schema, Market Intelligence source schema, Edge Intelligence source
    schema, strategy contract version, outcome definition version, future retrieval-model version) --
    the CEO's own instruction asked for "an explicit immutable version type suitable for" all six,
    singular, not six separate classes. ``version`` is always caller-supplied and literal -- NEVER
    inferred from a git hash, a file timestamp, or package installation metadata (``importlib.metadata``
    is never imported here), satisfying "avoid implicit dependence on package installation metadata" and
    "do not automatically infer versions from Git hashes or file timestamps" exactly."""

    namespace: str
    version: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.namespace, "SchemaVersion.namespace")
        require_non_empty_str(self.version, "SchemaVersion.version")


#: This package's OWN record schema version -- bumped by hand whenever a future checkpoint changes any
#: contract's own field shape. Participates in every record's identity (identities.py).
CONTEXT_MEMORY_SCHEMA_VERSION = SchemaVersion(namespace="context_memory", version="v1")

#: The Market Intelligence field-shape version these enum mirrors (enums.py) and ContextSnapshot's own
#: field set were captured against. Externally tracked here -- Market Intelligence itself carries no
#: self-declared schema version today (Checkpoint 8 design §6, §16 -- an explicit, disclosed gap).
MARKET_INTELLIGENCE_SCHEMA_VERSION = SchemaVersion(namespace="market_intelligence", version="mi-v1")

#: The Edge Intelligence field-shape version PresentEdgeReference/Observation were captured against.
EDGE_INTELLIGENCE_SCHEMA_VERSION = SchemaVersion(namespace="edge_intelligence", version="ei-v1")


# ---------------------------------------------------------------------------------------------------
# Deterministic ID value types (Checkpoint 9 §H) -- simple, dependency-free wrappers so a
# ContextSnapshotId can never be confused with an ObservationId even if their string values collided.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ContextSnapshotId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "ContextSnapshotId.value")


@dataclass(frozen=True)
class PresentEdgeReferenceId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "PresentEdgeReferenceId.value")


@dataclass(frozen=True)
class ObservationId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "ObservationId.value")


@dataclass(frozen=True)
class EdgeEvidenceId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "EdgeEvidenceId.value")


# ---------------------------------------------------------------------------------------------------
# Context Snapshot (Checkpoint 9 §D)
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ContextSnapshot:
    """One immutable record of what Market Intelligence already computed at one ``as_of``/``instrument``
    -- pure regime-state description, nothing derived, nothing about the future. Every categorical field
    is validated to be a member of its own controlled vocabulary (enums.py); ``context_confidence_score``
    is the one continuous field, kept as a quality/eligibility signal, never a similarity dimension
    (Checkpoint 8 design §3.2's own explicit reasoning, preserved here).

    IMPLEMENTATION CHOICE: no top-level ``timeframe`` field exists. ``MarketIntelligenceSnapshot`` itself
    (the real, existing public contract this mirrors) carries no single top-level timeframe either --
    only per-sub-reading ``.timeframe`` attributes -- so a flat "timeframe" field here would be either
    redundant with the four per-timeframe fields below or misleadingly imply the snapshot describes only
    one timeframe. Trend and momentum are captured per-timeframe (M15/H1/H4/D1, the fixed, known set
    ``ai_trader.market_intelligence.trend.TREND_TIMEFRAMES`` already defines) as four explicit, separately
    named fields rather than a generic mapping -- avoiding any need for map-key-ordering canonicalization
    logic for a set that is fixed and small, and giving each dimension its own strong type.

    IMPLEMENTATION CHOICE: ``trend_strength`` (M15-only, continuous) and ``momentum_rsi``
    (per-timeframe, continuous) are deliberately NOT stored at all in Checkpoint 9 -- Checkpoint 8 design
    §3.2 already excluded them from similarity, and they add no information the categorical
    ``trend_m15``/``momentum_state_*`` fields don't already carry for this checkpoint's own purposes;
    they can be added later without any identity-breaking change to existing records, since adding a new
    OPTIONAL field is additive.
    """

    instrument: str
    as_of: int
    session_state: str | None
    trend_m15: ContextTrendDirection
    trend_h1: ContextTrendDirection
    trend_h4: ContextTrendDirection
    trend_d1: ContextTrendDirection
    structure_state: ContextStructureState
    momentum_m15: ContextMomentumState
    momentum_h1: ContextMomentumState
    momentum_h4: ContextMomentumState
    momentum_d1: ContextMomentumState
    volatility_regime: ContextVolatilityRegime
    liquidity_state: ContextLiquidityState
    expansion_state: ContextExpansionState
    multi_timeframe_agreement: ContextAgreementLevel
    context_confidence_score: float | None
    data_quality_state: ContextDataQualityState
    market_intelligence_schema_version: SchemaVersion = field(default=MARKET_INTELLIGENCE_SCHEMA_VERSION)

    def __post_init__(self) -> None:
        require_non_empty_str(self.instrument, "ContextSnapshot.instrument")
        require_positive_int(self.as_of, "ContextSnapshot.as_of")
        if self.session_state is not None:
            require_non_empty_str(self.session_state, "ContextSnapshot.session_state")
        for field_name, enum_type in (
            ("trend_m15", ContextTrendDirection), ("trend_h1", ContextTrendDirection),
            ("trend_h4", ContextTrendDirection), ("trend_d1", ContextTrendDirection),
            ("structure_state", ContextStructureState),
            ("momentum_m15", ContextMomentumState), ("momentum_h1", ContextMomentumState),
            ("momentum_h4", ContextMomentumState), ("momentum_d1", ContextMomentumState),
            ("volatility_regime", ContextVolatilityRegime),
            ("liquidity_state", ContextLiquidityState),
            ("expansion_state", ContextExpansionState),
            ("multi_timeframe_agreement", ContextAgreementLevel),
            ("data_quality_state", ContextDataQualityState),
        ):
            value = getattr(self, field_name)
            if not isinstance(value, enum_type):
                raise ContextMemoryValidationError(
                    f"ContextSnapshot.{field_name} must be a {enum_type.__name__}, got {value!r}"
                )
        require_unit_interval_or_none(self.context_confidence_score, "ContextSnapshot.context_confidence_score")
        if not isinstance(self.market_intelligence_schema_version, SchemaVersion):
            raise ContextMemoryValidationError(
                "ContextSnapshot.market_intelligence_schema_version must be a SchemaVersion, "
                f"got {self.market_intelligence_schema_version!r}"
            )


# ---------------------------------------------------------------------------------------------------
# Present Edge Reference (Checkpoint 9 §E)
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PresentEdgeReference:
    """One edge that was PRESENT (Edge Intelligence's own verdict) at observation time. Deliberately
    does NOT embed the full strategy Contract (Checkpoint 9 §E's own explicit "do not copy the complete
    strategy contract" instruction) and does NOT compute or store any performance figure -- only the
    minimal identity/version metadata needed to distinguish and later re-interpret this reference.

    ``contract_version`` is always caller-supplied: this package has zero dependency on
    ``strategy_manager`` (Checkpoint 9 §L's own dependency rules restrict allowed external types to
    Market Intelligence/Edge Intelligence public types only, and this design chooses to depend on
    NEITHER live type -- see enums.py's own module docstring), so a future adapter that DOES have access
    to a real ``Contract`` is responsible for supplying its version identity here."""

    strategy_id: str
    contract_version: SchemaVersion
    edge_intelligence_schema_version: SchemaVersion
    declared_status: ContextEdgeStatus

    def __post_init__(self) -> None:
        require_non_empty_str(self.strategy_id, "PresentEdgeReference.strategy_id")
        if not isinstance(self.contract_version, SchemaVersion):
            raise ContextMemoryValidationError(
                f"PresentEdgeReference.contract_version must be a SchemaVersion, got {self.contract_version!r}"
            )
        if not isinstance(self.edge_intelligence_schema_version, SchemaVersion):
            raise ContextMemoryValidationError(
                "PresentEdgeReference.edge_intelligence_schema_version must be a SchemaVersion, "
                f"got {self.edge_intelligence_schema_version!r}"
            )
        if not isinstance(self.declared_status, ContextEdgeStatus):
            raise ContextMemoryValidationError(
                f"PresentEdgeReference.declared_status must be a ContextEdgeStatus, got {self.declared_status!r}"
            )


# ---------------------------------------------------------------------------------------------------
# Observation (Checkpoint 9 §F)
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Observation:
    """One Context Snapshot plus the complete, canonically-ordered set of edges PRESENT at that same
    moment. The snapshot's own ``as_of`` IS the observation's timestamp -- no separate, redundant
    timestamp field exists here (Checkpoint 9 §F's "observation timestamp OR snapshot reference": this
    design embeds the full snapshot, so a separate timestamp field would be pure duplication of
    ``context_snapshot.as_of``, a state that could never legitimately diverge and so is never given the
    chance to).

    ``present_edges`` is ALWAYS re-sorted by ``strategy_id`` in ``__post_init__``, regardless of the
    order the caller passed in -- "edge ordering supplied by a caller must not change the identity"
    (Checkpoint 9 §F) is enforced structurally here, not merely by convention at the identity-computation
    call site. A duplicate ``strategy_id`` within the supplied set is REJECTED (raises), never silently
    deduplicated -- the documented policy Checkpoint 9 §F requires: two references for the same strategy
    at the same ``as_of`` indicate an upstream inconsistency worth surfacing loudly, not papering over.

    An EMPTY ``present_edges`` tuple is explicitly ALLOWED and meaningful (Edge Intelligence's own "if
    zero are present, report zero" precedent, Checkpoint 8 design §4.1) -- never rejected as if it were
    an error.

    ``provenance_note`` is deliberately excluded from this record's own identity (see
    ``identities.py::_canonical_observation``) -- incidental metadata about HOW a record entered this
    system is not "material" to WHAT was observed (Checkpoint 9 §H's own "materially different input"
    standard), so two otherwise-identical observations with different provenance notes are the same
    observation, not two different ones.
    """

    context_snapshot: ContextSnapshot
    present_edges: tuple[PresentEdgeReference, ...]
    edge_intelligence_schema_version: SchemaVersion = field(default=EDGE_INTELLIGENCE_SCHEMA_VERSION)
    provenance_note: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.context_snapshot, ContextSnapshot):
            raise ContextMemoryValidationError(
                f"Observation.context_snapshot must be a ContextSnapshot, got {self.context_snapshot!r}"
            )
        for ref in self.present_edges:
            if not isinstance(ref, PresentEdgeReference):
                raise ContextMemoryValidationError(
                    f"Observation.present_edges entries must be PresentEdgeReference, got {ref!r}"
                )
        strategy_ids = [ref.strategy_id for ref in self.present_edges]
        if len(strategy_ids) != len(set(strategy_ids)):
            raise ContextMemoryValidationError(
                f"Observation.present_edges contains duplicate strategy_id entries: {strategy_ids!r}"
            )
        canonical_edges = tuple(sorted(self.present_edges, key=lambda ref: ref.strategy_id))
        object.__setattr__(self, "present_edges", canonical_edges)
        if not isinstance(self.edge_intelligence_schema_version, SchemaVersion):
            raise ContextMemoryValidationError(
                "Observation.edge_intelligence_schema_version must be a SchemaVersion, "
                f"got {self.edge_intelligence_schema_version!r}"
            )
        if self.provenance_note is not None:
            require_non_empty_str(self.provenance_note, "Observation.provenance_note")


# ---------------------------------------------------------------------------------------------------
# Outcome (Checkpoint 9 §G) -- CONTRACT ONLY. No calculation, no settlement, anywhere in this package.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Outcome:
    """The immutable record shape a FUTURE checkpoint will populate once outcome calculation exists
    (Checkpoint 8 design §4.2-§4.8) -- this checkpoint implements only the contract and its invariants,
    never the arithmetic. ``observation_as_of`` is a deliberate, disclosed denormalization: it is a copy
    of the parent Observation's own ``context_snapshot.as_of``, stored here specifically so the
    "resolution timestamp must not precede observation timestamp" invariant (Checkpoint 9 §J) can be
    enforced locally, without requiring a lookup this storage-less package has no way to perform.

    **Invariants enforced in ``__post_init__`` (Checkpoint 9 §G/§J)**:
    - ``PENDING`` <=> both ``normalized_result`` and ``resolution_as_of`` are ``None`` -- an unresolved
      outcome can never pretend to contain a resolved numerical result.
    - ``RESOLVED`` <=> both ``normalized_result`` and ``resolution_as_of`` are set (not ``None``), and
      ``resolution_as_of >= observation_as_of``.
    - ``INVALID``/``UNAVAILABLE`` => ``normalized_result`` is always ``None`` (an invalid/unavailable
      outcome never carries a number); ``resolution_as_of`` MAY be set (recording when resolution was
      attempted and failed) or ``None``.
    - **``unavailable_reason``** (CEO decision, Learning/Research Feedback Phase D contract amendment):
      required (not ``None``) exactly when ``status is UNAVAILABLE``; forbidden (must be ``None``) for
      every other status, including ``INVALID`` -- the schema gap this field closes concerns
      ``UNAVAILABLE`` only; ``INVALID``'s own pre-existing semantics (a resolution attempt that failed
      for a reason unrelated to missing evidence) are unchanged and deliberately do not gain this field.
    - **(``outcome_kind``, ``source_type``) compatibility** (Learning/Research Feedback Normative Model,
      ADR ``ADR_OUTCOME_IDENTITY_VS_SOURCE.md``, Option B): exactly the pairs
      ``(STRATEGY, SHADOW_EVIDENCE_ADAPTER)`` and ``(PORTFOLIO, REAL_PORTFOLIO_LEDGER)`` are valid today.
      ``SourceType.PRICE_ONLY`` -- a Checkpoint 9 placeholder for a price-only calculation method never
      actually implemented -- currently has no valid ``outcome_kind`` pairing; it remains a defined enum
      member (still a legitimate future ``SourceType``) but cannot back a real ``Outcome`` until it is
      given its own explicit pairing by a future, separate decision.

    This checkpoint does NOT solve how a later-resolved Outcome relates to an earlier-written ``PENDING``
    row for "the same" observation/strategy/horizon slot (append-only immutability means resolving a
    pending outcome is a NEW row, never an in-place update) -- that supersession model is explicitly
    deferred to a future storage-layer checkpoint (see the Checkpoint 9 report's own Limitations section).
    """

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
    outcome_kind: OutcomeKind
    unavailable_reason: OutcomeUnavailableReason | None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, ObservationId):
            raise ContextMemoryValidationError(
                f"Outcome.observation_id must be an ObservationId, got {self.observation_id!r}"
            )
        require_non_empty_str(self.strategy_id, "Outcome.strategy_id")
        require_positive_int(self.horizon, "Outcome.horizon")
        if not isinstance(self.horizon_unit, HorizonUnit):
            raise ContextMemoryValidationError(f"Outcome.horizon_unit must be a HorizonUnit, got {self.horizon_unit!r}")
        if not isinstance(self.outcome_definition_version, SchemaVersion):
            raise ContextMemoryValidationError(
                f"Outcome.outcome_definition_version must be a SchemaVersion, got {self.outcome_definition_version!r}"
            )
        if not isinstance(self.status, OutcomeStatus):
            raise ContextMemoryValidationError(f"Outcome.status must be an OutcomeStatus, got {self.status!r}")
        require_positive_int(self.observation_as_of, "Outcome.observation_as_of")
        require_finite_float_or_none(self.normalized_result, "Outcome.normalized_result")
        if self.resolution_as_of is not None:
            require_positive_int(self.resolution_as_of, "Outcome.resolution_as_of")
        require_non_empty_str(self.cost_model_ref, "Outcome.cost_model_ref")
        if not isinstance(self.source_type, SourceType):
            raise ContextMemoryValidationError(f"Outcome.source_type must be a SourceType, got {self.source_type!r}")
        if not isinstance(self.outcome_kind, OutcomeKind):
            raise ContextMemoryValidationError(f"Outcome.outcome_kind must be an OutcomeKind, got {self.outcome_kind!r}")
        if self.unavailable_reason is not None and not isinstance(self.unavailable_reason, OutcomeUnavailableReason):
            raise ContextMemoryValidationError(
                f"Outcome.unavailable_reason must be an OutcomeUnavailableReason or None, "
                f"got {self.unavailable_reason!r}"
            )

        if self.status is OutcomeStatus.PENDING:
            if self.normalized_result is not None or self.resolution_as_of is not None:
                raise ContextMemoryValidationError(
                    "a PENDING Outcome must have normalized_result=None and resolution_as_of=None, "
                    f"got normalized_result={self.normalized_result!r}, resolution_as_of={self.resolution_as_of!r}"
                )
            if self.unavailable_reason is not None:
                raise ContextMemoryValidationError(
                    f"a PENDING Outcome must have unavailable_reason=None, got {self.unavailable_reason!r}"
                )
        elif self.status is OutcomeStatus.RESOLVED:
            if self.normalized_result is None or self.resolution_as_of is None:
                raise ContextMemoryValidationError(
                    "a RESOLVED Outcome requires both normalized_result and resolution_as_of to be set, "
                    f"got normalized_result={self.normalized_result!r}, resolution_as_of={self.resolution_as_of!r}"
                )
            if self.resolution_as_of < self.observation_as_of:
                raise ContextMemoryValidationError(
                    f"Outcome.resolution_as_of ({self.resolution_as_of!r}) must not precede "
                    f"observation_as_of ({self.observation_as_of!r})"
                )
            if self.unavailable_reason is not None:
                raise ContextMemoryValidationError(
                    f"a RESOLVED Outcome must have unavailable_reason=None, got {self.unavailable_reason!r}"
                )
        elif self.status is OutcomeStatus.UNAVAILABLE:
            if self.normalized_result is not None:
                raise ContextMemoryValidationError(
                    f"an UNAVAILABLE Outcome must have normalized_result=None, got {self.normalized_result!r}"
                )
            if self.resolution_as_of is not None and self.resolution_as_of < self.observation_as_of:
                raise ContextMemoryValidationError(
                    f"Outcome.resolution_as_of ({self.resolution_as_of!r}) must not precede "
                    f"observation_as_of ({self.observation_as_of!r})"
                )
            if self.unavailable_reason is None:
                raise ContextMemoryValidationError(
                    "an UNAVAILABLE Outcome requires unavailable_reason to be set, got None"
                )
        else:  # INVALID
            if self.normalized_result is not None:
                raise ContextMemoryValidationError(
                    f"an INVALID Outcome must have normalized_result=None, got {self.normalized_result!r}"
                )
            if self.resolution_as_of is not None and self.resolution_as_of < self.observation_as_of:
                raise ContextMemoryValidationError(
                    f"Outcome.resolution_as_of ({self.resolution_as_of!r}) must not precede "
                    f"observation_as_of ({self.observation_as_of!r})"
                )
            if self.unavailable_reason is not None:
                raise ContextMemoryValidationError(
                    f"an INVALID Outcome must have unavailable_reason=None, got {self.unavailable_reason!r}"
                )

        valid_kind_source_pairs = {
            (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER),
            (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER),
        }
        if (self.outcome_kind, self.source_type) not in valid_kind_source_pairs:
            raise ContextMemoryValidationError(
                f"Outcome: invalid (outcome_kind, source_type) pair ({self.outcome_kind!r}, "
                f"{self.source_type!r}) -- only {sorted(valid_kind_source_pairs, key=lambda p: p[0].value)} "
                "are currently valid"
            )


# ---------------------------------------------------------------------------------------------------
# Operational Metadata (Learning/Research Feedback Normative Model, Addendum §A2) -- a separate,
# optional, immutable, DIAGNOSTIC-ONLY companion type. Never a learning target: structurally excluded
# from retrieval.py/evidence.py, never aggregated as evidence, never fed into any statistic. Records the
# Risk Manager's ALLOW/DENY decision and Strategy Health's PolicyState for one (observation, strategy)
# pair -- the operational "what happened to this candidate procedurally" record, distinct from the
# Outcome contract's own "what happened to this strategy/portfolio economically" record above.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class OperationalMetadataId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "OperationalMetadataId.value")


@dataclass(frozen=True)
class OperationalMetadata:
    """One row per ``(observation_id, strategy_id)`` -- the Risk Manager's own ALLOW/DENY decision (and,
    for a DENY, its reason code and rejection stage) plus Strategy Health's own ``PolicyState`` at that
    same moment. Write-once, read-only-by-humans, immutable; never a learning target.

    **Invariant enforced in ``__post_init__``**: a ``DENY`` must always carry a ``denied_reason_code``;
    an ``ALLOW`` must never carry one -- the two fields' own presence/absence is the direct, structural
    expression of the decision itself, never left to drift independently of it.
    """

    observation_id: ObservationId
    strategy_id: str
    risk_decision: ContextRiskDecision
    denied_reason_code: str | None
    rejection_stage: str | None
    strategy_health_policy_state: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, ObservationId):
            raise ContextMemoryValidationError(
                f"OperationalMetadata.observation_id must be an ObservationId, got {self.observation_id!r}"
            )
        require_non_empty_str(self.strategy_id, "OperationalMetadata.strategy_id")
        if not isinstance(self.risk_decision, ContextRiskDecision):
            raise ContextMemoryValidationError(
                f"OperationalMetadata.risk_decision must be a ContextRiskDecision, got {self.risk_decision!r}"
            )
        if self.denied_reason_code is not None:
            require_non_empty_str(self.denied_reason_code, "OperationalMetadata.denied_reason_code")
        if self.rejection_stage is not None:
            require_non_empty_str(self.rejection_stage, "OperationalMetadata.rejection_stage")
        if self.strategy_health_policy_state is not None:
            require_non_empty_str(
                self.strategy_health_policy_state, "OperationalMetadata.strategy_health_policy_state"
            )

        if self.risk_decision is ContextRiskDecision.DENY and self.denied_reason_code is None:
            raise ContextMemoryValidationError("OperationalMetadata: a DENY must carry a denied_reason_code")
        if self.risk_decision is ContextRiskDecision.ALLOW and self.denied_reason_code is not None:
            raise ContextMemoryValidationError("OperationalMetadata: an ALLOW must not carry a denied_reason_code")


# ---------------------------------------------------------------------------------------------------
# Interim Realization (Learning/Research Feedback Phase F, Architectural Decision Package Decision 3,
# Option C) -- a separate, optional, immutable, DIAGNOSTIC-ONLY companion type, following the EXACT same
# precedent as OperationalMetadata directly above: never a learning target, structurally excluded from
# evidence.py/retrieval.py aggregation, never fed into any statistic.
#
# WHY this cannot be an Outcome (see LEARNING_FEEDBACK_ARCHITECTURAL_DECISION_PACKAGE.md, Decision 3):
# Outcome's own existing, CEO-ratified meaning is "the position's final word" -- RESOLVED/UNAVAILABLE with
# no further Outcome ever following it for the same position. A position closed via multiple partial exits
# produces multiple economically DISTINCT realizations (Lifecycle Specification Finding C) that are each
# real, but NONE of the non-final ones may be mistaken for "the position is now closed, permanently. "
# InterimRealization exists specifically for every partial realization that does NOT bring its own
# position to zero size; the partial (or single) realization that DOES bring it to zero instead produces
# a normal Outcome, never this type -- the two types are mutually exclusive per closing fill, never both.
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class InterimRealizationId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "InterimRealizationId.value")


@dataclass(frozen=True)
class InterimRealization:
    """One partial, NON-terminal economic realization against a still-open economic position lifecycle.
    ``position_key`` is the stable, run-scoped position identity (Learning/Research Feedback Phase F
    Decision 1) this realization belongs to -- deliberately NOT ``client_order_id`` (an order identity,
    proven insufficient as a position identity by the Lifecycle Specification) and NOT persisted anywhere
    else in Context Memory's own schema; it exists here purely so a human or a future, separately-
    authorized aggregation phase can group every interim realization (and the eventual terminal Outcome)
    belonging to the same economic lifecycle, mirroring Shadow Evidence's own already-proven
    ``ShadowTradeLegRecord.position_id`` FK precedent.

    Same RESOLVED-vs-UNAVAILABLE branching as ``Outcome`` (``normalized_result`` set XOR
    ``unavailable_reason`` set -- never both, never neither): a partial realization can be just as
    unmeasurable (no valid risk denominator) as a terminal one, for the identical reason (Learning/
    Research Feedback Phase D's own ``NO_VALID_RISK_DENOMINATOR`` decision applies identically here).
    """

    observation_id: ObservationId
    strategy_id: str
    position_key: str
    outcome_kind: OutcomeKind
    source_type: SourceType
    horizon: int
    horizon_unit: HorizonUnit
    observation_as_of: int
    realization_as_of: int
    normalized_result: float | None
    cost_model_ref: str
    unavailable_reason: OutcomeUnavailableReason | None

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, ObservationId):
            raise ContextMemoryValidationError(
                f"InterimRealization.observation_id must be an ObservationId, got {self.observation_id!r}"
            )
        require_non_empty_str(self.strategy_id, "InterimRealization.strategy_id")
        require_non_empty_str(self.position_key, "InterimRealization.position_key")
        if not isinstance(self.outcome_kind, OutcomeKind):
            raise ContextMemoryValidationError(
                f"InterimRealization.outcome_kind must be an OutcomeKind, got {self.outcome_kind!r}"
            )
        if not isinstance(self.source_type, SourceType):
            raise ContextMemoryValidationError(
                f"InterimRealization.source_type must be a SourceType, got {self.source_type!r}"
            )
        valid_kind_source_pairs = {
            (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER),
            (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER),
        }
        if (self.outcome_kind, self.source_type) not in valid_kind_source_pairs:
            raise ContextMemoryValidationError(
                f"InterimRealization: invalid (outcome_kind, source_type) pair ({self.outcome_kind!r}, "
                f"{self.source_type!r}) -- only {sorted(valid_kind_source_pairs, key=lambda p: p[0].value)} "
                "are currently valid"
            )
        require_positive_int(self.horizon, "InterimRealization.horizon")
        if not isinstance(self.horizon_unit, HorizonUnit):
            raise ContextMemoryValidationError(
                f"InterimRealization.horizon_unit must be a HorizonUnit, got {self.horizon_unit!r}"
            )
        require_positive_int(self.observation_as_of, "InterimRealization.observation_as_of")
        require_positive_int(self.realization_as_of, "InterimRealization.realization_as_of")
        if self.realization_as_of < self.observation_as_of:
            raise ContextMemoryValidationError(
                f"InterimRealization.realization_as_of ({self.realization_as_of!r}) must not precede "
                f"observation_as_of ({self.observation_as_of!r})"
            )
        require_finite_float_or_none(self.normalized_result, "InterimRealization.normalized_result")
        require_non_empty_str(self.cost_model_ref, "InterimRealization.cost_model_ref")
        if self.unavailable_reason is not None and not isinstance(self.unavailable_reason, OutcomeUnavailableReason):
            raise ContextMemoryValidationError(
                f"InterimRealization.unavailable_reason must be an OutcomeUnavailableReason or None, "
                f"got {self.unavailable_reason!r}"
            )
        if (self.normalized_result is None) == (self.unavailable_reason is None):
            raise ContextMemoryValidationError(
                "InterimRealization requires exactly one of normalized_result/unavailable_reason to be "
                f"set, got normalized_result={self.normalized_result!r}, "
                f"unavailable_reason={self.unavailable_reason!r}"
            )


# ---------------------------------------------------------------------------------------------------
# Position Outcome (Learning/Research Feedback Sprint 2, Blocker 2 -- CEO-ratified, additive) -- the ONE
# canonical, unambiguous, Level-1 accounting result for a complete economic position lifecycle. Pure
# arithmetic aggregate over every constituent partial fill; NEVER a research metric (no risk-normalized
# ratio, no interpretation of any kind) -- Recognition Engine/Prediction Engine/any future statistical
# consumer should read THIS type for "how did the position do," not any single per-fill record alone,
# which by construction reflects only its own closing fill's own economics, never the position's full
# lifecycle (see the existing per-fill Outcome type's own docstring for the explicit, documented scope
# boundary between the two).
# ---------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class PositionOutcomeId:
    value: str

    def __post_init__(self) -> None:
        require_non_empty_str(self.value, "PositionOutcomeId.value")


@dataclass(frozen=True)
class PositionOutcome:
    """The complete, aggregated Level-1 economic result for one position lifecycle, identified by
    `position_key` (Architectural Decision Package Decision 1) -- produced EXACTLY ONCE, at the moment
    the position reaches zero size (the same trigger the existing per-fill Outcome type already fires
    on). Computed by summing every constituent partial (every `InterimRealization` plus the final
    closing fill) -- pure arithmetic, never risk-normalized, never dependent on which research question
    is being asked (Level 2 metrics are a separate, future concern, reconstructable FROM this type's own
    fields, never computed here).

    `constituent_interim_realization_ids` is the explicit, auditable link to every non-terminal partial
    that contributed to this aggregate; `terminal_outcome_id` links to the final, terminal-fill-only
    Outcome record produced for the SAME position lifecycle. A correct consumer reads PositionOutcome
    for "how did the position do" and never additionally sums `InterimRealization`s on top of it (they
    are already incorporated) -- double-counting risk, documented here and on `InterimRealization`'s own
    docstring."""

    observation_id: ObservationId
    strategy_id: str
    position_key: str
    outcome_kind: OutcomeKind
    source_type: SourceType
    opened_as_of: int
    terminal_as_of: int
    total_qty_closed: float
    weighted_avg_exit_price: float | None
    total_gross_pnl: float
    total_net_pnl: float
    total_costs: float
    cost_model_ref: str
    terminal_outcome_id: EdgeEvidenceId
    constituent_interim_realization_ids: tuple[InterimRealizationId, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.observation_id, ObservationId):
            raise ContextMemoryValidationError(
                f"PositionOutcome.observation_id must be an ObservationId, got {self.observation_id!r}"
            )
        require_non_empty_str(self.strategy_id, "PositionOutcome.strategy_id")
        require_non_empty_str(self.position_key, "PositionOutcome.position_key")
        if not isinstance(self.outcome_kind, OutcomeKind):
            raise ContextMemoryValidationError(
                f"PositionOutcome.outcome_kind must be an OutcomeKind, got {self.outcome_kind!r}"
            )
        if not isinstance(self.source_type, SourceType):
            raise ContextMemoryValidationError(
                f"PositionOutcome.source_type must be a SourceType, got {self.source_type!r}"
            )
        valid_kind_source_pairs = {
            (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER),
            (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER),
        }
        if (self.outcome_kind, self.source_type) not in valid_kind_source_pairs:
            raise ContextMemoryValidationError(
                f"PositionOutcome: invalid (outcome_kind, source_type) pair ({self.outcome_kind!r}, "
                f"{self.source_type!r}) -- only {sorted(valid_kind_source_pairs, key=lambda p: p[0].value)} "
                "are currently valid"
            )
        require_positive_int(self.opened_as_of, "PositionOutcome.opened_as_of")
        require_positive_int(self.terminal_as_of, "PositionOutcome.terminal_as_of")
        if self.terminal_as_of < self.opened_as_of:
            raise ContextMemoryValidationError(
                f"PositionOutcome.terminal_as_of ({self.terminal_as_of!r}) must not precede "
                f"opened_as_of ({self.opened_as_of!r})"
            )
        if self.total_qty_closed <= 0:
            raise ContextMemoryValidationError(
                f"PositionOutcome.total_qty_closed must be > 0, got {self.total_qty_closed!r}"
            )
        require_finite_float_or_none(self.weighted_avg_exit_price, "PositionOutcome.weighted_avg_exit_price")
        require_finite_float_or_none(self.total_gross_pnl, "PositionOutcome.total_gross_pnl")
        require_finite_float_or_none(self.total_net_pnl, "PositionOutcome.total_net_pnl")
        require_finite_float_or_none(self.total_costs, "PositionOutcome.total_costs")
        require_non_empty_str(self.cost_model_ref, "PositionOutcome.cost_model_ref")
        if not isinstance(self.terminal_outcome_id, EdgeEvidenceId):
            raise ContextMemoryValidationError(
                f"PositionOutcome.terminal_outcome_id must be an EdgeEvidenceId, got {self.terminal_outcome_id!r}"
            )
        for ref in self.constituent_interim_realization_ids:
            if not isinstance(ref, InterimRealizationId):
                raise ContextMemoryValidationError(
                    "PositionOutcome.constituent_interim_realization_ids entries must be "
                    f"InterimRealizationId, got {ref!r}"
                )
