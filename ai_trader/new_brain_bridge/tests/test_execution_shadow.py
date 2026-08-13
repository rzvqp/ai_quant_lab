"""`attempt_shadow_execution` tests -- the CEO's own explicit standard: "Nu e suficient sa demonstrezi
ca NO_TRADE nu trimite ordine" (section 3). `test_a_fully_approved_candidate_reaches_and_is_blocked_at_
the_real_broker_gate` is THE proof that standard requires: a genuinely Risk-Manager-APPROVED decision,
not merely a denied one, reaching the REAL `BrokerOrderSubmissionGate` and being refused there."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness.broker_gate import BrokerOrderSubmissionGate
from ai_trader.mandate2_readiness.decision_provenance import NEW_BRAIN_SOURCE, DecisionProvenance
from ai_trader.mandate2_readiness.event_identity import EventIdentity
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome
from ai_trader.new_brain_bridge.execution_shadow import RISK_MANAGER_DENIED, attempt_shadow_execution
from ai_trader.new_brain_bridge.risk_gate import submit_new_brain_candidate
from ai_trader.risk_manager_live.tests._fixtures import (
    AS_OF,
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_risk_context,
)
from ai_trader.risk_manager_live.types import LiveRiskDecision

_TRACE_ID = "trace-shadow-0001"
_CATALOG_HASH = ve_brain.CANONICAL_CATALOG_HASH
_CONFIG_FP = "decision-fp-shadow-0001"


def _approved_decision() -> LiveRiskDecision:
    """The REAL Risk Manager, run through `submit_new_brain_candidate` (never hand-built), against
    fixtures deliberately configured (`make_config`) so the ALLOW path is genuinely reachable."""
    event_identity = EventIdentity(
        trace_id=_TRACE_ID, market_event_id="evt-shadow-1", symbol="XAUUSD", timeframe="M15",
        bar_id="bar-shadow-1", market_timestamp=AS_OF, received_timestamp=AS_OF,
        brain_version=ve_brain.VE_BRAIN_VERSION, catalog_hash=_CATALOG_HASH,
        configuration_fingerprint=_CONFIG_FP,
    )
    decision = ve_brain.DecisionResponse(
        contract_id=ve_brain.OUTPUT_CONTRACT_ID, decision="TRADE", expected_value_net=0.5,
        expected_reward=1.0, expected_loss=0.3, estimated_cost=0.02, probability_assumptions={},
        strategy_id="trend_pullback", configuration_fingerprint=_CONFIG_FP,
        reason_codes=(ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,), engine_version=ve_brain.ENGINE_VERSION,
    )
    provenance = DecisionProvenance(source=NEW_BRAIN_SOURCE, trace_id=_TRACE_ID, catalog_hash=_CATALOG_HASH,
                                     configuration_fingerprint=_CONFIG_FP)
    outcome = NewBrainOutcome(
        event_identity=event_identity, strategy_id="trend_pullback", strategy_version="v1", node_traces=(),
        decision=decision, provenance=provenance, entry_price=2000.0, stop_price=1990.0, target_price=2020.0,
    )
    return submit_new_brain_candidate(
        outcome, account=make_account(), portfolio=make_portfolio(), instrument=make_instrument(),
        risk_context=make_risk_context(), risk_config=make_config(),
    )


def test_a_fully_approved_candidate_reaches_and_is_blocked_at_the_real_broker_gate() -> None:
    risk_decision = _approved_decision()
    assert risk_decision.approved is True, (
        "fixture must produce a genuine APPROVAL -- a denied candidate would prove nothing about the "
        "broker barrier's own behavior, which is exactly the gap the CEO's section 3 called out"
    )

    result = attempt_shadow_execution(risk_decision)

    assert result.reached_broker_gate is True
    assert result.blocked is True
    assert "DISABLED" in result.reason


def test_a_denied_candidate_never_even_reaches_the_gate() -> None:
    """Distinct from the above -- a RISK_MANAGER_DENIED candidate is refused before `authorize()` is
    ever called, so it cannot be mistaken for a proof about the barrier itself."""
    denied = LiveRiskDecision(
        approved=False, reason_codes=("SOME_DENIAL",), requested_risk=None, approved_risk=None,
        calculated_volume=None, monetary_risk=None, stop_distance=None, margin_estimate=None,
        warnings=(), calculation_trace=(),
    )
    result = attempt_shadow_execution(denied)
    assert result.reached_broker_gate is False
    assert result.blocked is True
    assert result.reason == RISK_MANAGER_DENIED


def test_the_function_genuinely_calls_authorize_not_a_hardcoded_block() -> None:
    """Fault-injection ONLY: an explicitly, visibly `enabled=True` gate (never constructed this way by
    any real caller) proves `attempt_shadow_execution` actually delegates to `gate.authorize()` rather
    than always returning blocked=True regardless of the gate it's given."""
    approved = LiveRiskDecision(
        approved=True, reason_codes=(), requested_risk=100.0, approved_risk=100.0, calculated_volume=0.1,
        monetary_risk=100.0, stop_distance=10.0, margin_estimate=50.0, warnings=(),
        calculation_trace=({"step": "test"},),  # type: ignore[arg-type]
    )
    fault_injected_gate = BrokerOrderSubmissionGate(enabled=True, reason="test-only fault injection")

    result = attempt_shadow_execution(approved, gate=fault_injected_gate)

    assert result.reached_broker_gate is True
    assert result.blocked is False
    assert result.reason == "AUTHORIZED"
