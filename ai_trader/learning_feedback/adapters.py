"""Pure adapter functions -- Learning/Research Feedback Phase D.

Every function here is a PURE function: no I/O, no side effects, no wall-clock/randomness reads, same
inputs always produce the same output. Nothing in this module is wired into any orchestration path yet
(Phase E) or into ``harness.py`` (Phase F) -- these adapters are unreachable from production code today.

**Signature note, disclosed**: the Implementation Plan's own original sketches for ``build_strategy_
outcome``/``build_portfolio_outcome`` did not include a ``closing_leg``/``cost_model_ref`` parameter --
both were added during this phase's own implementation once two "open details" the plan itself flagged
were resolved (CEO decisions on ``pnl_r`` unavailability and ``cost_model_ref`` canonicalization): a pure
function cannot reach into a collection it wasn't given, so the specific ``TradeRecord`` supplying
``pnl_r``/``holding_bars``/``exit_as_of`` and the already-canonicalized ``cost_model_ref`` string (computed
once per run, not per outcome -- see :func:`canonical_cost_model_ref`) must be passed in explicitly. This
is a disclosed refinement of the plan's own sketch, not a contradiction of it.
"""

from __future__ import annotations

from ai_trader.context_memory.contracts import (
    EdgeEvidenceId,
    InterimRealization,
    InterimRealizationId,
    ObservationId,
    OperationalMetadata,
    Outcome,
    PositionOutcome,
    SchemaVersion,
)
from ai_trader.context_memory.enums import (
    ContextRiskDecision,
    HorizonUnit,
    OutcomeKind,
    OutcomeStatus,
    OutcomeUnavailableReason,
    SourceType,
)
from ai_trader.risk_manager.types import Decision, RiskDecision
from ai_trader.shadow_evidence.types import ShadowPositionRecord
from ai_trader.simulation.config import CostModel
from ai_trader.simulation.portfolio_simulator import TradeRecord

LEARNING_FEEDBACK_OUTCOME_DEFINITION_VERSION = SchemaVersion(
    namespace="learning_feedback_outcome", version="lfo-v1",
)

# ---------------------------------------------------------------------------------------------------
# Denial-code -> rejection-stage mapping (CEO decision, Phase D) -- centralized, pure, exhaustive.
#
# Every code below was found by direct inspection of ai_trader/risk_manager/{pipeline,filters,limits,
# guards,sizing,engine,assembler}.py (fresh grep + read, not inferred) -- the fixed gate order documented
# in pipeline.py's own module docstring: Global State -> Opportunity Sanity -> Recommendation Floor ->
# Pre-Trade Filters -> Portfolio Limits -> Loss/Drawdown Guards -> Cooldowns -> Sizing, plus two
# engine-level gates that never reach the per-opportunity pipeline at all (PORTFOLIO_UNAVAILABLE,
# INTERNAL_ERROR/INTERNAL_VALIDATION_FAILED).
#
# "LOSS_DAILY"/"LOSS_WEEKLY"/"DRAWDOWN_MAX" are emitted from TWO call sites (the per-opportunity Loss &
# Drawdown Guards stage in guards.py, AND copied into the Global State Gate's own denial when the whole
# engine is SUSPENDED for that same reason, engine.py:198-200) -- both map to the SAME stage here
# ("loss_drawdown_guards") because the CODE's own meaning (a loss/drawdown breach) is identical regardless
# of which call site attached it; this mapping is keyed by code, not by call site, since the code is the
# only signal available at the point OperationalMetadata is built.
# ---------------------------------------------------------------------------------------------------

#: The exhaustive domain model, curated INDEPENDENTLY of the mapping below (not derived from its keys) --
#: risk_manager/ has no canonical registry of its own denial codes to import or generate this from
#: (confirmed by direct inspection: every code is an inline string literal, no shared constant list
#: exists anywhere in that package), so this set is the closest available "source of truth," hand-written
#: from the same fresh grep + read that produced the mapping below. Writing it independently (rather than
#: as `frozenset(REJECTION_STAGE_BY_DENIAL_CODE.keys())`) is deliberate: a self-referential definition
#: could never fail its own exhaustiveness test, defeating the point of having one -- this way, a typo or
#: an omission in EITHER this set or the mapping is caught by test_all_denial_codes_are_mapped.
ALL_DENIAL_CODES: frozenset[str] = frozenset({
    "SUSPENDED", "EMERGENCY_STOP", "KILL_SWITCH",
    "NOT_ACTIONABLE", "INVALID_INPUT",
    "BELOW_FLOOR", "SCORE_TOO_LOW",
    "DATA_DEGRADED", "FILTER_VOLATILITY", "FILTER_SPREAD", "FILTER_LIQUIDITY", "FILTER_NEWS",
    "RULE_WEEKEND", "RULE_GAP",
    "LIMIT_MAX_POSITIONS", "LIMIT_MAX_PER_SYMBOL", "LIMIT_MAX_CORRELATED", "LIMIT_MAX_EXPOSURE",
    "LIMIT_MAX_LEVERAGE", "LIMIT_MAX_OVERNIGHT",
    "LOSS_DAILY", "LOSS_WEEKLY", "DRAWDOWN_MAX",
    "COOLDOWN_AFTER_LOSS", "COOLDOWN_CONSECUTIVE", "COOLDOWN_STRATEGY",
    "INVALID_STOP", "SIZE_BELOW_MIN",
    "PORTFOLIO_UNAVAILABLE",
    "INTERNAL_ERROR", "INTERNAL_VALIDATION_FAILED",
})

REJECTION_STAGE_BY_DENIAL_CODE: dict[str, str] = {
    # Stage: global_state (engine.py -- SUSPENDED/EMERGENCY_STOP/KILL_SWITCH only; loss/drawdown-caused
    # suspensions are classified under loss_drawdown_guards below, per the code-based rule above).
    "SUSPENDED": "global_state",
    "EMERGENCY_STOP": "global_state",
    "KILL_SWITCH": "global_state",
    # Stage: opportunity_sanity (pipeline.py stage 1)
    "NOT_ACTIONABLE": "opportunity_sanity",
    "INVALID_INPUT": "opportunity_sanity",
    # Stage: recommendation_floor (pipeline.py stage 2)
    "BELOW_FLOOR": "recommendation_floor",
    "SCORE_TOO_LOW": "recommendation_floor",
    # Stage: pre_trade_filters (pipeline.py stage 3 -> filters.py)
    "DATA_DEGRADED": "pre_trade_filters",
    "FILTER_VOLATILITY": "pre_trade_filters",
    "FILTER_SPREAD": "pre_trade_filters",
    "FILTER_LIQUIDITY": "pre_trade_filters",
    "FILTER_NEWS": "pre_trade_filters",
    "RULE_WEEKEND": "pre_trade_filters",
    "RULE_GAP": "pre_trade_filters",
    # Stage: portfolio_limits (pipeline.py stage 4 -> limits.py)
    "LIMIT_MAX_POSITIONS": "portfolio_limits",
    "LIMIT_MAX_PER_SYMBOL": "portfolio_limits",
    "LIMIT_MAX_CORRELATED": "portfolio_limits",
    "LIMIT_MAX_EXPOSURE": "portfolio_limits",
    "LIMIT_MAX_LEVERAGE": "portfolio_limits",
    "LIMIT_MAX_OVERNIGHT": "portfolio_limits",
    # Stage: loss_drawdown_guards (pipeline.py stage 5 -> guards.py::run_loss_drawdown_guards)
    "LOSS_DAILY": "loss_drawdown_guards",
    "LOSS_WEEKLY": "loss_drawdown_guards",
    "DRAWDOWN_MAX": "loss_drawdown_guards",
    # Stage: cooldowns (pipeline.py stage 6 -> guards.py::run_cooldowns)
    "COOLDOWN_AFTER_LOSS": "cooldowns",
    "COOLDOWN_CONSECUTIVE": "cooldowns",
    "COOLDOWN_STRATEGY": "cooldowns",
    # Stage: sizing (pipeline.py stage 7 -> sizing.py)
    "INVALID_STOP": "sizing",
    "SIZE_BELOW_MIN": "sizing",
    # Stage: portfolio_unavailable (engine.py -- PortfolioState missing/stale, never reaches the pipeline)
    "PORTFOLIO_UNAVAILABLE": "portfolio_unavailable",
    # Stage: internal_error (engine.py exception handler / assembler.py's own validation-failure fallback)
    "INTERNAL_ERROR": "internal_error",
    "INTERNAL_VALIDATION_FAILED": "internal_error",
}


class UnmappedDenialCodeError(ValueError):
    """Raised by :func:`rejection_stage_for` when given a denial code absent from
    :data:`REJECTION_STAGE_BY_DENIAL_CODE` -- fail closed, never a silent/free-form fallback (CEO
    decision, Phase D)."""


def rejection_stage_for(denial_code: str) -> str:
    """The one, pure, centralized lookup -- no substring inference, no heuristic. Raises
    :class:`UnmappedDenialCodeError` for any code not in the exhaustive domain model above."""
    try:
        return REJECTION_STAGE_BY_DENIAL_CODE[denial_code]
    except KeyError:
        raise UnmappedDenialCodeError(
            f"denial code {denial_code!r} is not in the exhaustive REJECTION_STAGE_BY_DENIAL_CODE "
            "mapping -- add it there (with its own grounded pipeline stage) before it can be classified"
        ) from None


# ---------------------------------------------------------------------------------------------------
# cost_model_ref canonicalization (CEO decision, Phase D)
# ---------------------------------------------------------------------------------------------------


def _canonical_float(value: float) -> str:
    # Deterministic, human-readable decimal formatting -- never str(float)/repr(float)'s shortest-
    # round-trip representation (a documented CPython implementation detail this project already avoids
    # relying on elsewhere, e.g. identities.py's own canonical_float uses float.hex() for hashing payloads
    # for the same reason). ".10g" is used here instead of hex specifically because THIS ref must stay
    # human-readable (CEO requirement), while remaining a well-defined, fixed-precision format: identical
    # floats always format identically, and 10 significant digits is far more precision than any of
    # CostModel's own fields (spread_ticks, commission_per_lot) plausibly carry.
    return format(value, ".10g")


def canonical_cost_model_ref(cost_model: CostModel) -> str:
    """One deterministic, human-readable reference string for a ``CostModel`` -- fixed field order,
    stable numeric formatting, every field always explicitly present (a zero/disabled component is
    serialized as ``=0``, never omitted). Identical configurations always produce identical strings;
    any field difference produces a different string (CEO requirement, Phase D)."""
    return (
        f"spread_model={cost_model.spread_model}"
        f"|spread_ticks={_canonical_float(cost_model.spread_ticks)}"
        f"|commission_model={cost_model.commission_model}"
        f"|commission_per_lot={_canonical_float(cost_model.commission_per_lot)}"
        f"|cost_model_version={cost_model.cost_model_version}"
    )


# ---------------------------------------------------------------------------------------------------
# Strategy / Portfolio Outcome construction
# ---------------------------------------------------------------------------------------------------


def _resolved_or_unavailable_outcome(
    *, observation_id: ObservationId, strategy_id: str, horizon: int, resolution_as_of: int,
    observation_as_of: int, pnl_r: float | None, cost_model_ref: str, source_type: SourceType,
    outcome_kind: OutcomeKind,
) -> Outcome:
    """Shared construction logic for both Strategy and Portfolio Outcomes (CEO decision, Phase D):
    ``pnl_r is not None`` -> RESOLVED with that value; ``pnl_r is None`` -> UNAVAILABLE with
    ``NO_VALID_RISK_DENOMINATOR``, never a net_pnl fallback, never zero substitution, never dropped."""
    if pnl_r is not None:
        return Outcome(
            observation_id=observation_id, strategy_id=strategy_id, horizon=horizon,
            horizon_unit=HorizonUnit.BARS,
            outcome_definition_version=LEARNING_FEEDBACK_OUTCOME_DEFINITION_VERSION,
            status=OutcomeStatus.RESOLVED, observation_as_of=observation_as_of, normalized_result=pnl_r,
            resolution_as_of=resolution_as_of, cost_model_ref=cost_model_ref, source_type=source_type,
            outcome_kind=outcome_kind, unavailable_reason=None,
        )
    return Outcome(
        observation_id=observation_id, strategy_id=strategy_id, horizon=horizon,
        horizon_unit=HorizonUnit.BARS,
        outcome_definition_version=LEARNING_FEEDBACK_OUTCOME_DEFINITION_VERSION,
        status=OutcomeStatus.UNAVAILABLE, observation_as_of=observation_as_of, normalized_result=None,
        resolution_as_of=resolution_as_of, cost_model_ref=cost_model_ref, source_type=source_type,
        outcome_kind=outcome_kind, unavailable_reason=OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR,
    )


def build_strategy_outcome(
    position: ShadowPositionRecord, closing_leg: TradeRecord, observation_id: ObservationId,
    observation_as_of: int, cost_model_ref: str,
) -> Outcome | None:
    """Returns ``None`` (never raises) if ``position`` is not yet resolvable: not ``CLOSED``, missing
    ``aggregate_net_pnl``, or (defensively) a non-positive holding period that could not satisfy
    ``Outcome.horizon``'s own required-positive invariant. Otherwise RESOLVED (using ``closing_leg.
    pnl_r``) or UNAVAILABLE (``NO_VALID_RISK_DENOMINATOR``), per the CEO's own explicit Phase D
    decision -- never a ``net_pnl`` fallback."""
    if position.status != "CLOSED":
        return None
    if position.aggregate_net_pnl is None:
        return None
    if position.full_exit_as_of is None:
        return None
    if position.aggregate_holding_bars_full is None or position.aggregate_holding_bars_full <= 0:
        return None
    return _resolved_or_unavailable_outcome(
        observation_id=observation_id, strategy_id=position.strategy_id,
        horizon=position.aggregate_holding_bars_full, resolution_as_of=position.full_exit_as_of,
        observation_as_of=observation_as_of, pnl_r=closing_leg.pnl_r, cost_model_ref=cost_model_ref,
        source_type=SourceType.SHADOW_EVIDENCE_ADAPTER, outcome_kind=OutcomeKind.STRATEGY,
    )


def build_portfolio_outcome(
    trade: TradeRecord, observation_id: ObservationId, observation_as_of: int, cost_model_ref: str,
) -> Outcome | None:
    """Returns ``None`` (never raises) only for the same defensive, structurally-required-positive-
    horizon case as :func:`build_strategy_outcome` (``trade.holding_bars <= 0``) -- otherwise always
    resolvable, since a ``TradeRecord`` in ``account.trade_ledger`` is by construction already closed.
    Same RESOLVED-vs-UNAVAILABLE branching on ``trade.pnl_r`` as the Strategy path: ``TradeRecord`` is the
    SAME type for both Shadow and real portfolio trades, sharing the identical ``pnl_r`` nullability
    (``portfolio_simulator.py`` -- no valid stop reference or a liquidation-forced close both leave
    ``pnl_r=None``), so the CEO's own Phase D decision applies identically here, not only to the Strategy
    case it was phrased against."""
    if trade.holding_bars <= 0:
        return None
    return _resolved_or_unavailable_outcome(
        observation_id=observation_id, strategy_id=trade.strategy_id, horizon=trade.holding_bars,
        resolution_as_of=trade.exit_as_of, observation_as_of=observation_as_of, pnl_r=trade.pnl_r,
        cost_model_ref=cost_model_ref, source_type=SourceType.REAL_PORTFOLIO_LEDGER,
        outcome_kind=OutcomeKind.PORTFOLIO,
    )


# ---------------------------------------------------------------------------------------------------
# OperationalMetadata construction
# ---------------------------------------------------------------------------------------------------


def _interim_or_none(
    *, observation_id: ObservationId, strategy_id: str, position_key: str, horizon: int,
    realization_as_of: int, observation_as_of: int, pnl_r: float | None, cost_model_ref: str,
    source_type: SourceType, outcome_kind: OutcomeKind,
) -> InterimRealization:
    """Shared construction logic for both Strategy and Portfolio InterimRealizations (Architectural
    Decision Package Decision 3): ``pnl_r is not None`` -> a measured realization; ``pnl_r is None`` ->
    UNAVAILABLE with ``NO_VALID_RISK_DENOMINATOR``, the identical branching :func:`_resolved_or_
    unavailable_outcome` uses for a terminal ``Outcome`` -- a partial realization can be exactly as
    unmeasurable as a terminal one, for the same reason."""
    if pnl_r is not None:
        return InterimRealization(
            observation_id=observation_id, strategy_id=strategy_id, position_key=position_key,
            outcome_kind=outcome_kind, source_type=source_type, horizon=horizon,
            horizon_unit=HorizonUnit.BARS, observation_as_of=observation_as_of,
            realization_as_of=realization_as_of, normalized_result=pnl_r, cost_model_ref=cost_model_ref,
            unavailable_reason=None,
        )
    return InterimRealization(
        observation_id=observation_id, strategy_id=strategy_id, position_key=position_key,
        outcome_kind=outcome_kind, source_type=source_type, horizon=horizon, horizon_unit=HorizonUnit.BARS,
        observation_as_of=observation_as_of, realization_as_of=realization_as_of, normalized_result=None,
        cost_model_ref=cost_model_ref, unavailable_reason=OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR,
    )


def build_portfolio_interim_realization(
    trade: TradeRecord, position_key: str, observation_id: ObservationId, observation_as_of: int,
    cost_model_ref: str,
) -> InterimRealization | None:
    """A non-terminal, diagnostic-only realization for one real-portfolio partial exit (Architectural
    Decision Package Decision 3, Option C) -- produced for every closing/reducing ``TradeRecord`` that
    does NOT bring its own position to zero size (the one that does produces a normal ``Outcome`` via
    :func:`build_portfolio_outcome` instead, never both). Returns ``None`` (never raises) only for the
    same defensively-required-positive-horizon case as :func:`build_portfolio_outcome`."""
    if trade.holding_bars <= 0:
        return None
    return _interim_or_none(
        observation_id=observation_id, strategy_id=trade.strategy_id, position_key=position_key,
        horizon=trade.holding_bars, realization_as_of=trade.exit_as_of, observation_as_of=observation_as_of,
        pnl_r=trade.pnl_r, cost_model_ref=cost_model_ref, source_type=SourceType.REAL_PORTFOLIO_LEDGER,
        outcome_kind=OutcomeKind.PORTFOLIO,
    )


def build_strategy_interim_realization(
    trade: TradeRecord, position_key: str, observation_id: ObservationId, observation_as_of: int,
    cost_model_ref: str,
) -> InterimRealization | None:
    """A non-terminal, diagnostic-only realization for one Shadow partial exit leg (Architectural
    Decision Package Decision 3, Option C) -- the Shadow-side mirror of :func:`build_portfolio_interim_
    realization`. Takes only the closing ``TradeRecord`` leg (``ShadowTradeLegRecord.leg``), never the
    full ``ShadowPositionRecord`` -- unlike the terminal :func:`build_strategy_outcome`, an interim
    realization needs no aggregate position-level state, only this one leg's own economics."""
    if trade.holding_bars <= 0:
        return None
    return _interim_or_none(
        observation_id=observation_id, strategy_id=trade.strategy_id, position_key=position_key,
        horizon=trade.holding_bars, realization_as_of=trade.exit_as_of, observation_as_of=observation_as_of,
        pnl_r=trade.pnl_r, cost_model_ref=cost_model_ref, source_type=SourceType.SHADOW_EVIDENCE_ADAPTER,
        outcome_kind=OutcomeKind.STRATEGY,
    )


def build_operational_metadata(
    decision: RiskDecision, policy_state: str | None, observation_id: ObservationId,
) -> OperationalMetadata:
    """Maps Risk Manager's own ``Decision.ALLOW``/``Decision.DENY`` to the local ``ContextRiskDecision``
    mirror; on DENY, ``denied_reason_code`` is the FIRST (primary) reason's own code, and
    ``rejection_stage`` is looked up via :func:`rejection_stage_for` -- fails closed
    (:class:`UnmappedDenialCodeError`) for any code outside the exhaustive domain model, never a silent/
    inferred stage."""
    if decision.decision is Decision.ALLOW:
        return OperationalMetadata(
            observation_id=observation_id, strategy_id=decision.strategy_id,
            risk_decision=ContextRiskDecision.ALLOW, denied_reason_code=None, rejection_stage=None,
            strategy_health_policy_state=policy_state,
        )
    primary_code = decision.denied_reasons[0].code if decision.denied_reasons else "INTERNAL_VALIDATION_FAILED"
    return OperationalMetadata(
        observation_id=observation_id, strategy_id=decision.strategy_id,
        risk_decision=ContextRiskDecision.DENY, denied_reason_code=primary_code,
        rejection_stage=rejection_stage_for(primary_code), strategy_health_policy_state=policy_state,
    )


# ---------------------------------------------------------------------------------------------------
# PositionOutcome construction (Learning/Research Feedback Sprint 2, Blocker 2 -- CEO-ratified,
# additive). Pure arithmetic aggregate over the COMPLETE ledger of partials belonging to one
# position_key -- never a research metric, never risk-normalized. The caller (learning_feedback/
# capture.py) is responsible for accumulating `partials` (every TradeRecord/leg contributing to this
# position, oldest first, terminal one last) across the position's whole lifetime; this module never
# retains state of its own.
# ---------------------------------------------------------------------------------------------------


def _position_outcome_from_partials(
    *, partials: tuple[TradeRecord, ...], observation_id: ObservationId, position_key: str,
    cost_model_ref: str, source_type: SourceType, outcome_kind: OutcomeKind,
    terminal_outcome_id: EdgeEvidenceId, constituent_interim_realization_ids: tuple[InterimRealizationId, ...],
) -> PositionOutcome | None:
    """Returns `None` (never raises) only if `partials` is empty or the total closed quantity is not
    positive -- both structurally unreachable in practice (a terminal capture always includes at least
    the terminal trade itself), but never assumed."""
    if not partials:
        return None
    total_qty = sum(p.qty for p in partials)
    if total_qty <= 0:
        return None
    weighted_avg_exit_price = sum(p.qty * p.exit_price for p in partials) / total_qty
    total_gross_pnl = sum(p.gross_pnl for p in partials)
    total_net_pnl = sum(p.net_pnl for p in partials)
    total_costs = sum(p.fees for p in partials)
    # entry_as_of/strategy_id are identical across every partial for one position lifecycle by
    # construction (all close/reduce the SAME originally-opened position) -- any partial's own value
    # would do; the first/last are used here purely for readability, not because they differ.
    opened_as_of = partials[0].entry_as_of
    terminal_as_of = partials[-1].exit_as_of
    strategy_id = partials[-1].strategy_id
    return PositionOutcome(
        observation_id=observation_id, strategy_id=strategy_id, position_key=position_key,
        outcome_kind=outcome_kind, source_type=source_type, opened_as_of=opened_as_of,
        terminal_as_of=terminal_as_of, total_qty_closed=total_qty,
        weighted_avg_exit_price=weighted_avg_exit_price, total_gross_pnl=total_gross_pnl,
        total_net_pnl=total_net_pnl, total_costs=total_costs, cost_model_ref=cost_model_ref,
        terminal_outcome_id=terminal_outcome_id,
        constituent_interim_realization_ids=constituent_interim_realization_ids,
    )


def build_portfolio_position_outcome(
    partials: tuple[TradeRecord, ...], position_key: str, observation_id: ObservationId,
    cost_model_ref: str, terminal_outcome_id: EdgeEvidenceId,
    constituent_interim_realization_ids: tuple[InterimRealizationId, ...],
) -> PositionOutcome | None:
    """The real-portfolio-side `PositionOutcome` builder -- the ONE canonical, complete result for a
    real position lifecycle, aggregated across every partial exit (Sprint 2 Blocker 2)."""
    return _position_outcome_from_partials(
        partials=partials, observation_id=observation_id, position_key=position_key,
        cost_model_ref=cost_model_ref, source_type=SourceType.REAL_PORTFOLIO_LEDGER,
        outcome_kind=OutcomeKind.PORTFOLIO, terminal_outcome_id=terminal_outcome_id,
        constituent_interim_realization_ids=constituent_interim_realization_ids,
    )


def build_strategy_position_outcome(
    partials: tuple[TradeRecord, ...], position_key: str, observation_id: ObservationId,
    cost_model_ref: str, terminal_outcome_id: EdgeEvidenceId,
    constituent_interim_realization_ids: tuple[InterimRealizationId, ...],
) -> PositionOutcome | None:
    """The Shadow-side mirror of `build_portfolio_position_outcome` (Sprint 2 Blocker 2)."""
    return _position_outcome_from_partials(
        partials=partials, observation_id=observation_id, position_key=position_key,
        cost_model_ref=cost_model_ref, source_type=SourceType.SHADOW_EVIDENCE_ADAPTER,
        outcome_kind=OutcomeKind.STRATEGY, terminal_outcome_id=terminal_outcome_id,
        constituent_interim_realization_ids=constituent_interim_realization_ids,
    )
