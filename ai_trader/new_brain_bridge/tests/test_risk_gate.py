"""`submit_new_brain_candidate` tests -- every distinct rejection reason exercised individually, plus one
fully-valid candidate reaching the REAL `evaluate_trade_proposal` (never mocked/stubbed)."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.new_brain_bridge.risk_gate import (
    MISSING_DECISION_PROVENANCE,
    NO_ACTIONABLE_N6_DECISION,
    PROVENANCE_DECISION_FINGERPRINT_MISMATCH,
    PROVENANCE_EVENT_IDENTITY_MISMATCH,
    UNTRUSTED_DECISION_SOURCE,
    submit_new_brain_candidate,
)
from ai_trader.risk_manager_live.tests._fixtures import (
    AS_OF,
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager_live.types import LiveRiskDecision

_TRACE_ID = "trace-0001"
_CATALOG_HASH = ve_brain.CANONICAL_CATALOG_HASH
_CONFIG_FP = "decision-fp-0001"


def _event_identity(**overrides: object) -> EventIdentity:
    kwargs: dict[str, object] = dict(
        trace_id=_TRACE_ID, market_event_id="evt-1", symbol="XAUUSD", timeframe="M15",
        bar_id="bar-1", market_timestamp=AS_OF, received_timestamp=AS_OF,
        brain_version=ve_brain.VE_BRAIN_VERSION, catalog_hash=_CATALOG_HASH,
        configuration_fingerprint=_CONFIG_FP,
    )
    kwargs.update(overrides)
    return EventIdentity(**kwargs)  # type: ignore[arg-type]


def _decision_response(**overrides: object) -> ve_brain.DecisionResponse:
    kwargs: dict[str, object] = dict(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="TRADE",
        expected_value_net=0.5, expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02,
        probability_assumptions={}, strategy_id="trend_pullback", configuration_fingerprint=_CONFIG_FP,
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    kwargs.update(overrides)
    return ve_brain.DecisionResponse(**kwargs)


def _outcome(*, decision: ve_brain.DecisionResponse | None, provenance: DecisionProvenance | None,
             event_identity: EventIdentity | None = None, entry_price: float | None = 2400.0,
             stop_price: float | None = 2390.0, target_price: float | None = 2420.0) -> NewBrainOutcome:
    return NewBrainOutcome(
        event_identity=event_identity if event_identity is not None else _event_identity(),
        strategy_id="trend_pullback", strategy_version="v1", node_traces=(), decision=decision,
        provenance=provenance, entry_price=entry_price, stop_price=stop_price, target_price=target_price,
    )


def _submit(outcome: NewBrainOutcome) -> LiveRiskDecision:
    return submit_new_brain_candidate(
        outcome, account=make_account(), portfolio=make_portfolio(), instrument=make_instrument(),
        risk_context=make_risk_context(), risk_config=make_config(),
    )


def test_no_decision_at_all_is_denied_as_not_actionable() -> None:
    outcome = _outcome(decision=None, provenance=None)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (NO_ACTIONABLE_N6_DECISION,)


def test_a_no_trade_decision_is_denied_as_not_actionable_not_as_untrusted() -> None:
    """NO_TRADE is a legitimate N6 outcome, not a provenance failure -- must get its own distinct
    reason, never conflated with an untrusted-source rejection."""
    outcome = _outcome(decision=_decision_response(decision="NO_TRADE", reason_codes=("MISSING_LEVEL_INPUT",)),
                        provenance=None)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (NO_ACTIONABLE_N6_DECISION,)


def test_trade_decision_without_any_provenance_is_denied() -> None:
    outcome = _outcome(decision=_decision_response(), provenance=None)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (MISSING_DECISION_PROVENANCE,)


def test_provenance_from_a_non_new_brain_source_is_rejected() -> None:
    provenance = DecisionProvenance(source="LEGACY_RECOGNIZER", trace_id=_TRACE_ID, catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (UNTRUSTED_DECISION_SOURCE,)


def test_provenance_with_an_empty_required_field_is_rejected() -> None:
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id="", catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (UNTRUSTED_DECISION_SOURCE,)


def test_provenance_trace_id_not_matching_the_event_identity_is_rejected() -> None:
    """A provenance object that is internally valid (real source, all fields non-empty) but describes a
    DIFFERENT event than the one being submitted -- the exact forged/substituted-provenance attack this
    cross-check exists to catch."""
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id="some-other-trace",
                                     catalog_hash=_CATALOG_HASH, configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (PROVENANCE_EVENT_IDENTITY_MISMATCH,)


def test_provenance_catalog_hash_not_matching_the_event_identity_is_rejected() -> None:
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id=_TRACE_ID,
                                     catalog_hash="stale-catalog-hash", configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (PROVENANCE_EVENT_IDENTITY_MISMATCH,)


def test_provenance_configuration_fingerprint_not_matching_the_decision_is_rejected() -> None:
    """Proves the provenance describes THIS decision, not merely this event -- a stale provenance from
    an earlier decision on the same trace_id/catalog_hash must not authorize a later, different one."""
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id=_TRACE_ID, catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint="a-different-decision-fingerprint")
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    assert result.approved is False
    assert result.reason_codes == (PROVENANCE_DECISION_FINGERPRINT_MISMATCH,)


def test_a_fully_valid_candidate_reaches_the_real_risk_manager() -> None:
    """Every check passes -- the REAL `evaluate_trade_proposal` (never mocked) runs and returns its own
    genuine verdict. This proves the gate's job (get a trustworthy candidate TO Risk Manager), not Risk
    Manager's own sizing logic (that is `risk_manager_live`'s own test suite's job)."""
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id=_TRACE_ID, catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(decision=_decision_response(), provenance=provenance)
    result = _submit(outcome)
    # Whatever Risk Manager's own sizing/limits verdict is, it must have genuinely RUN (a real
    # LiveRiskDecision, not this module's own _deny placeholder) -- confirmed by requiring the
    # invariant _deny() itself always upholds: approved implies a non-empty calculation_trace.
    if result.approved:
        assert len(result.calculation_trace) > 0
    else:
        assert result.reason_codes != (NO_ACTIONABLE_N6_DECISION,)
        assert result.reason_codes != (MISSING_DECISION_PROVENANCE,)
        assert result.reason_codes != (UNTRUSTED_DECISION_SOURCE,)
        assert result.reason_codes != (PROVENANCE_EVENT_IDENTITY_MISMATCH,)
        assert result.reason_codes != (PROVENANCE_DECISION_FINGERPRINT_MISMATCH,)


def test_shadow_trade_candidate_is_also_actionable_not_only_trade() -> None:
    """CEO amendment A1: N6 producing SHADOW_TRADE_CANDIDATE must ALSO reach Risk Manager (in shadow) --
    only NO_TRADE is a non-actionable decision, not every non-TRADE decision."""
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id=_TRACE_ID, catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint=_CONFIG_FP)
    outcome = _outcome(
        decision=_decision_response(decision="SHADOW_TRADE_CANDIDATE",
                                     reason_codes=(ve_brain.ReasonCode.SHADOW_CANDIDATE_EV_POSITIVE.value,)),
        provenance=provenance,
    )
    result = _submit(outcome)
    assert result.reason_codes != (NO_ACTIONABLE_N6_DECISION,)
