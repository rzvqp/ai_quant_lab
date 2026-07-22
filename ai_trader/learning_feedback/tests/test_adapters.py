"""Unit tests for :mod:`ai_trader.learning_feedback.adapters` -- Phase D.

Every adapter is exercised as a pure function: no repository, no harness, no I/O anywhere in this file.
"""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import ObservationId
from ai_trader.context_memory.enums import (
    ContextRiskDecision,
    OutcomeKind,
    OutcomeStatus,
    OutcomeUnavailableReason,
    SourceType,
)
from ai_trader.learning_feedback.adapters import (
    ALL_DENIAL_CODES,
    REJECTION_STAGE_BY_DENIAL_CODE,
    UnmappedDenialCodeError,
    build_operational_metadata,
    build_portfolio_interim_realization,
    build_portfolio_outcome,
    build_strategy_interim_realization,
    build_strategy_outcome,
    canonical_cost_model_ref,
    rejection_stage_for,
)
from ai_trader.risk_manager.types import (
    AppliedRule,
    Decision,
    DeniedReason,
    EngineState,
    RiskDecision,
    RiskRefs,
)
from ai_trader.shadow_evidence.types import ShadowPositionRecord
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import CostModel
from ai_trader.simulation.portfolio_simulator import TradeRecord

OBS_ID = ObservationId("fake-observation-id-for-learning-feedback-tests")
AS_OF = 1_700_000_000


# ------------------------------------------------------------------ fixture builders (local to this file)


def _position(**overrides: object) -> ShadowPositionRecord:
    kwargs: dict[str, object] = {
        "position_id": "POS-1", "strategy_id": "S1", "symbol": "XAUUSD", "direction": Direction.LONG,
        "entry_as_of": AS_OF, "entry_price": 2000.0, "entry_opportunity_id": "OPP-1",
        "status": "CLOSED", "full_exit_as_of": AS_OF + 400, "n_legs": 1,
        "aggregate_net_pnl": 25.0, "aggregate_holding_bars_full": 4,
    }
    kwargs.update(overrides)
    return ShadowPositionRecord(**kwargs)  # type: ignore[arg-type]


def _trade(**overrides: object) -> TradeRecord:
    kwargs: dict[str, object] = {
        "client_order_id": "CO-1", "strategy_id": "S1", "symbol": "XAUUSD", "direction": Direction.LONG,
        "entry_price": 2000.0, "exit_price": 2010.0, "entry_as_of": AS_OF, "exit_as_of": AS_OF + 400,
        "qty": 1.0, "gross_pnl": 25.0, "fees": 1.0, "net_pnl": 24.0, "pnl_r": 1.5, "holding_bars": 4,
        "mfe": 30.0, "mae": -5.0,
    }
    kwargs.update(overrides)
    return TradeRecord(**kwargs)  # type: ignore[arg-type]


def _risk_decision(**overrides: object) -> RiskDecision:
    kwargs: dict[str, object] = {
        "risk_schema_version": "1.0.0", "risk_engine_version": "1.0.0", "risk_policy_version": "1.0.0",
        "decision_id": "S1|XAUUSD|1700000000", "score_id": "SC-1", "signal_id": "SIG-1",
        "strategy_id": "S1", "symbol": "XAUUSD", "timestamp": AS_OF, "as_of": AS_OF,
        "engine_state": EngineState.READY, "decision": Decision.ALLOW, "direction": Direction.LONG,
        "applied_rules": (AppliedRule(rule="GLOBAL_STATE", passed=True),),
        "refs": RiskRefs(scoring_schema_version="1.0.0", interface_version="1.0.0"),
        "denied_reasons": (),
    }
    kwargs.update(overrides)
    return RiskDecision(**kwargs)  # type: ignore[arg-type]


# ------------------------------------------------------------------ build_strategy_outcome


def test_build_strategy_outcome_happy_path_resolved() -> None:
    out = build_strategy_outcome(_position(), _trade(pnl_r=1.5), OBS_ID, AS_OF, "ref-1")
    assert out is not None
    assert out.status is OutcomeStatus.RESOLVED
    assert out.normalized_result == 1.5
    assert out.unavailable_reason is None
    assert out.outcome_kind is OutcomeKind.STRATEGY
    assert out.source_type is SourceType.SHADOW_EVIDENCE_ADAPTER
    assert out.strategy_id == "S1"
    assert out.horizon == 4
    assert out.resolution_as_of == AS_OF + 400
    assert out.cost_model_ref == "ref-1"


def test_build_strategy_outcome_unavailable_when_pnl_r_none() -> None:
    out = build_strategy_outcome(_position(), _trade(pnl_r=None), OBS_ID, AS_OF, "ref-1")
    assert out is not None
    assert out.status is OutcomeStatus.UNAVAILABLE
    assert out.normalized_result is None
    assert out.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_build_strategy_outcome_none_when_position_open() -> None:
    open_position = _position(status="OPEN", full_exit_as_of=None, aggregate_net_pnl=None, aggregate_holding_bars_full=None)
    assert build_strategy_outcome(open_position, _trade(), OBS_ID, AS_OF, "ref-1") is None


def test_build_strategy_outcome_none_when_aggregate_net_pnl_missing() -> None:
    # A CLOSED position with aggregate_net_pnl=None would violate ShadowPositionRecord's OWN invariant
    # (CLOSED requires full_exit_as_of set, but says nothing about aggregate_net_pnl) -- constructing
    # this directly proves the adapter's own explicit None-check, not ShadowPositionRecord's validation.
    position = _position(aggregate_net_pnl=None)
    assert build_strategy_outcome(position, _trade(), OBS_ID, AS_OF, "ref-1") is None


def test_build_strategy_outcome_none_when_holding_bars_non_positive() -> None:
    position = _position(aggregate_holding_bars_full=0)
    assert build_strategy_outcome(position, _trade(), OBS_ID, AS_OF, "ref-1") is None


# ------------------------------------------------------------------ build_portfolio_outcome


def test_build_portfolio_outcome_happy_path_resolved() -> None:
    out = build_portfolio_outcome(_trade(pnl_r=2.0), OBS_ID, AS_OF, "ref-1")
    assert out is not None
    assert out.status is OutcomeStatus.RESOLVED
    assert out.normalized_result == 2.0
    assert out.unavailable_reason is None
    assert out.outcome_kind is OutcomeKind.PORTFOLIO
    assert out.source_type is SourceType.REAL_PORTFOLIO_LEDGER
    assert out.horizon == 4
    assert out.resolution_as_of == AS_OF + 400


def test_build_portfolio_outcome_unavailable_when_pnl_r_none() -> None:
    out = build_portfolio_outcome(_trade(pnl_r=None), OBS_ID, AS_OF, "ref-1")
    assert out is not None
    assert out.status is OutcomeStatus.UNAVAILABLE
    assert out.normalized_result is None
    assert out.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_build_portfolio_outcome_none_when_holding_bars_non_positive() -> None:
    assert build_portfolio_outcome(_trade(holding_bars=0), OBS_ID, AS_OF, "ref-1") is None


# ------------------------------------------------------------------ kind/source pairing is always valid by construction


def test_strategy_and_portfolio_outcomes_never_share_a_kind_source_pair() -> None:
    # The adapters hardcode kind/source internally (never caller-controlled), so a mismatched pair
    # cannot be attempted through these signatures -- this test documents/proves that structural fact
    # rather than exercising a negative path that the signatures make unreachable (DoD Phase D §5).
    strategy_out = build_strategy_outcome(_position(), _trade(), OBS_ID, AS_OF, "ref-1")
    portfolio_out = build_portfolio_outcome(_trade(), OBS_ID, AS_OF, "ref-1")
    assert strategy_out is not None
    assert portfolio_out is not None
    assert (strategy_out.outcome_kind, strategy_out.source_type) == (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER)
    assert (portfolio_out.outcome_kind, portfolio_out.source_type) == (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER)


# ------------------------------------------------------------------ build_operational_metadata


def test_build_operational_metadata_allow_without_reason() -> None:
    decision = _risk_decision(decision=Decision.ALLOW, denied_reasons=())
    meta = build_operational_metadata(decision, "ACTIVE", OBS_ID)
    assert meta.risk_decision is ContextRiskDecision.ALLOW
    assert meta.denied_reason_code is None
    assert meta.rejection_stage is None
    assert meta.strategy_health_policy_state == "ACTIVE"
    assert meta.strategy_id == "S1"


def test_build_operational_metadata_deny_with_reason() -> None:
    decision = _risk_decision(
        decision=Decision.DENY,
        denied_reasons=(DeniedReason(code="LIMIT_MAX_PER_SYMBOL", observed=3, limit=2),),
    )
    meta = build_operational_metadata(decision, "PROBATION", OBS_ID)
    assert meta.risk_decision is ContextRiskDecision.DENY
    assert meta.denied_reason_code == "LIMIT_MAX_PER_SYMBOL"
    assert meta.rejection_stage == "portfolio_limits"
    assert meta.strategy_health_policy_state == "PROBATION"


def test_build_operational_metadata_deny_uses_first_reason_when_multiple() -> None:
    decision = _risk_decision(
        decision=Decision.DENY,
        denied_reasons=(
            DeniedReason(code="SIZE_BELOW_MIN"), DeniedReason(code="LIMIT_MAX_PER_SYMBOL"),
        ),
    )
    meta = build_operational_metadata(decision, None, OBS_ID)
    assert meta.denied_reason_code == "SIZE_BELOW_MIN"
    assert meta.rejection_stage == "sizing"


def test_build_operational_metadata_policy_state_may_be_none() -> None:
    decision = _risk_decision(decision=Decision.ALLOW)
    meta = build_operational_metadata(decision, None, OBS_ID)
    assert meta.strategy_health_policy_state is None


def test_build_operational_metadata_deny_with_unmapped_code_raises() -> None:
    decision = _risk_decision(decision=Decision.DENY, denied_reasons=(DeniedReason(code="NOT_A_REAL_CODE"),))
    with pytest.raises(UnmappedDenialCodeError):
        build_operational_metadata(decision, None, OBS_ID)


# ------------------------------------------------------------------ rejection_stage_for / exhaustiveness


def test_all_denial_codes_are_mapped() -> None:
    # Load-bearing (CEO requirement): the independently-curated domain model and the mapping's own key
    # set must match exactly -- catches a typo/omission in either without being tautological.
    assert set(REJECTION_STAGE_BY_DENIAL_CODE.keys()) == ALL_DENIAL_CODES


def test_every_mapped_code_resolves_via_rejection_stage_for() -> None:
    for code in ALL_DENIAL_CODES:
        stage = rejection_stage_for(code)
        assert isinstance(stage, str) and stage


def test_unmapped_code_fails_closed() -> None:
    with pytest.raises(UnmappedDenialCodeError):
        rejection_stage_for("SOME_FUTURE_CODE_NOT_YET_CLASSIFIED")


def test_rejection_stage_mapping_uses_only_grounded_stage_names() -> None:
    # "Do not introduce stages that cannot be grounded in the current implementation" (CEO requirement)
    # -- every stage name traces to pipeline.py's own numbered comments or a distinct engine-level gate.
    grounded_stages = {
        "global_state", "opportunity_sanity", "recommendation_floor", "pre_trade_filters",
        "portfolio_limits", "loss_drawdown_guards", "cooldowns", "sizing",
        "portfolio_unavailable", "internal_error",
    }
    assert set(REJECTION_STAGE_BY_DENIAL_CODE.values()) == grounded_stages


# ------------------------------------------------------------------ canonical_cost_model_ref


def test_canonical_cost_model_ref_is_deterministic() -> None:
    cm = CostModel(spread_model="fixed_ticks", spread_ticks=1.5, commission_model="per_lot", commission_per_lot=2.0, cost_model_version="1.0.0")
    assert canonical_cost_model_ref(cm) == canonical_cost_model_ref(cm)
    assert canonical_cost_model_ref(cm) == canonical_cost_model_ref(
        CostModel(spread_model="fixed_ticks", spread_ticks=1.5, commission_model="per_lot", commission_per_lot=2.0, cost_model_version="1.0.0")
    )


def test_canonical_cost_model_ref_is_human_readable_and_field_ordered() -> None:
    cm = CostModel(spread_model="fixed_ticks", spread_ticks=1.5, commission_model="per_lot", commission_per_lot=2.0, cost_model_version="1.0.0")
    ref = canonical_cost_model_ref(cm)
    assert ref == "spread_model=fixed_ticks|spread_ticks=1.5|commission_model=per_lot|commission_per_lot=2|cost_model_version=1.0.0"


def test_canonical_cost_model_ref_zero_commission_is_explicit_not_omitted() -> None:
    cm = CostModel(spread_model="fixed_ticks", spread_ticks=1.0, commission_model="per_lot", commission_per_lot=0.0, cost_model_version="1.0.0")
    assert "commission_per_lot=0" in canonical_cost_model_ref(cm)


@pytest.mark.parametrize(
    "field_name,new_value",
    [
        ("spread_model", "variable_ticks"),
        ("spread_ticks", 2.5),
        ("commission_model", "flat"),
        ("commission_per_lot", 3.0),
        ("cost_model_version", "2.0.0"),
    ],
)
def test_canonical_cost_model_ref_is_sensitive_to_every_field(field_name: str, new_value: object) -> None:
    base = CostModel(spread_model="fixed_ticks", spread_ticks=1.0, commission_model="per_lot", commission_per_lot=0.0, cost_model_version="1.0.0")
    changed = dataclasses.replace(base, **{field_name: new_value})  # type: ignore[arg-type]
    assert canonical_cost_model_ref(base) != canonical_cost_model_ref(changed)


# ------------------------------------------------------------------ build_portfolio_interim_realization /
# build_strategy_interim_realization -- Architectural Decision Package Decision 3 (Option C)

POSITION_KEY = "run-A:XAUUSD:1700000000:LONG"


def test_build_portfolio_interim_realization_happy_path() -> None:
    r = build_portfolio_interim_realization(_trade(pnl_r=0.4), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    assert r is not None
    assert r.normalized_result == 0.4
    assert r.unavailable_reason is None
    assert r.outcome_kind is OutcomeKind.PORTFOLIO
    assert r.source_type is SourceType.REAL_PORTFOLIO_LEDGER
    assert r.position_key == POSITION_KEY
    assert r.strategy_id == "S1"
    assert r.horizon == 4
    assert r.realization_as_of == AS_OF + 400


def test_build_portfolio_interim_realization_unavailable_when_pnl_r_none() -> None:
    r = build_portfolio_interim_realization(_trade(pnl_r=None), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    assert r is not None
    assert r.normalized_result is None
    assert r.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_build_portfolio_interim_realization_none_when_holding_bars_non_positive() -> None:
    assert build_portfolio_interim_realization(_trade(holding_bars=0), POSITION_KEY, OBS_ID, AS_OF, "ref-1") is None


def test_build_strategy_interim_realization_happy_path() -> None:
    r = build_strategy_interim_realization(_trade(pnl_r=0.9), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    assert r is not None
    assert r.normalized_result == 0.9
    assert r.outcome_kind is OutcomeKind.STRATEGY
    assert r.source_type is SourceType.SHADOW_EVIDENCE_ADAPTER
    assert r.position_key == POSITION_KEY


def test_build_strategy_interim_realization_unavailable_when_pnl_r_none() -> None:
    r = build_strategy_interim_realization(_trade(pnl_r=None), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    assert r is not None
    assert r.unavailable_reason is OutcomeUnavailableReason.NO_VALID_RISK_DENOMINATOR


def test_build_strategy_interim_realization_none_when_holding_bars_non_positive() -> None:
    assert build_strategy_interim_realization(_trade(holding_bars=0), POSITION_KEY, OBS_ID, AS_OF, "ref-1") is None


def test_interim_realizations_never_share_a_kind_source_pair_with_each_other() -> None:
    portfolio_r = build_portfolio_interim_realization(_trade(), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    strategy_r = build_strategy_interim_realization(_trade(), POSITION_KEY, OBS_ID, AS_OF, "ref-1")
    assert portfolio_r is not None and strategy_r is not None
    assert (portfolio_r.outcome_kind, portfolio_r.source_type) == (OutcomeKind.PORTFOLIO, SourceType.REAL_PORTFOLIO_LEDGER)
    assert (strategy_r.outcome_kind, strategy_r.source_type) == (OutcomeKind.STRATEGY, SourceType.SHADOW_EVIDENCE_ADAPTER)
