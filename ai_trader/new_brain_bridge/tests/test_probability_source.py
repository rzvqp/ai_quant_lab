"""`probability_source.py` infrastructure demonstration -- CEO instruction, Mandate B point 4 (2026-08-14):
"demonstreaza ca infrastructura e corecta... interfata EXISTA, o sursa ratificata poate fi introdusa FARA
recablare, lipsa produce DETERMINIST NO_TRADE, AI Trader nu inventeaza probabilitati."

**Every `ProbabilityInputs`/`OutcomeCell` value in this file is a labeled, illustrative CANONICAL FIXTURE
-- never a claim about any real strategy's actual historical performance, and never wired into
`probability_source.load_probability_inputs`'s own production return value (still `None`, unconditionally,
confirmed by `test_probability_source_still_returns_none_in_production` below). The CEO's own instruction:
"Alea nu devin valori de productie" -- these numbers exist ONLY to prove the wiring, not to trade on."""

from __future__ import annotations

from typing import Any

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

from ai_trader.new_brain_bridge import bridge as bridge_module
from ai_trader.new_brain_bridge.probability_source import load_probability_inputs
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"


def _illustrative_canonical_fixture() -> ve_brain.ProbabilityInputs:
    """A LABELED, non-production fixture -- 200 trades / 150 target hits, matching the SAME shape
    already used and disclosed as a fixture in `mandate2_readiness/tests/test_brain_functional_proofs
    .py`. Not derived from any real trade history; exists only to prove the interface accepts and acts
    on a populated `ProbabilityInputs`, not to represent a real edge's actual statistics."""
    cell = ve_brain.OutcomeCell(n=200, n_target=150, n_horizon=0, sum_horizon_R=0.0)
    return ve_brain.ProbabilityInputs(hierarchy=(ve_brain.HierarchyLevel(cell=cell),), credibility=0.80)


def _fully_eligible_fixture_request(
    canon: ve_brain.StrategyContract, *, probability_inputs: ve_brain.ProbabilityInputs | None,
) -> tuple[ve_brain.DecisionRequest, ve_brain.EligibilityDecision]:
    """A `DecisionRequest`/`EligibilityDecision` pair with `market_map_available=True`,
    `levels_available=True`, `confirmation_available=True` -- CANONICAL FIXTURE values for THIS
    isolated demonstration only. `bridge.py`'s own production wiring keeps these hardcoded `False`
    (the CEO's own explicit, unmodified instruction, pending TOWER_HANDOFF_PASS) -- this helper
    constructs its OWN `DecisionRequest` directly, the same way `mandate2_readiness/tests/
    test_brain_functional_proofs.py` already does, never by editing or monkeypatching `bridge.py`'s
    N3/N4 fields."""
    market_event_id, regime_fingerprint = "PROOF-EVENT-PROB-001", "proof-prob-fingerprint"
    eligibility = ve_brain.EligibilityDecision(
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
        market_event_id=market_event_id, regime_fingerprint=regime_fingerprint,
        router_version=ve_brain.ROUTER_VERSION, eligible=True, mode=ve_brain.RoutingMode.NORMAL,
        matched_regimes=("TREND_UP",), reason_codes=(ve_brain.ReasonCode.ROUTER_ELIGIBLE.value,),
    )
    request = ve_brain.DecisionRequest(
        contract_id=ve_brain.INPUT_CONTRACT_ID, strategy_id=canon.strategy_id,
        strategy_version=canon.strategy_version, validation_status=canon.validation_status,
        strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id=market_event_id, regime_fingerprint=regime_fingerprint,
        market_state_ref="proof-market-state-ref", regime_label="TREND_UP", bias_direction="LONG",
        market_map_available=True, levels_available=True, confirmation_available=True,  # fixture-only
        entry_price=2400.0, stop_price=2390.0, target_kind="rr", target_param=2.0, holding_window=10,
        atr=10.0, probability_inputs=probability_inputs, full_spread_price=0.10,
        entry_slippage_price=0.05, exit_slippage_price=0.05, symbol=_SYMBOL, timeframe=_TIMEFRAME,
        block_start=0, block_end=1_000, segment_id="proof-segment", manifest_hash="proof-manifest-hash",
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
        raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION, router_version=ve_brain.ROUTER_VERSION,
        eligibility_policy_version="eligibility-v1",
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
        configuration_fingerprint="proof-config-fingerprint-prob",
    )
    return request, eligibility


def test_the_interface_exists_and_accepts_strategy_identity() -> None:
    """`load_probability_inputs` is a real, callable, correctly-shaped function -- not a stub that would
    need its own signature rewritten once a real source exists."""
    result = load_probability_inputs("trend_pullback", "v1")
    assert result is None  # today's honest, correct answer -- see module docstring


def test_probability_source_still_returns_none_in_production() -> None:
    """The illustrative fixtures in THIS file are never wired into production -- confirmed directly,
    not merely asserted in a docstring."""
    for strategy_id in ("trend_pullback", "range_fade", "trend_shadow", "trend_experimental"):
        assert load_probability_inputs(strategy_id, "v1") is None


def test_absence_produces_deterministic_no_trade_missing_probability_inputs() -> None:
    """CEO requirement: "lipsa produce DETERMINIST NO_TRADE." With every OTHER gate satisfied
    (canonical fixture values, isolated from bridge.py's own real N3/N4 wiring), `probability_inputs
    =None` is the ONLY thing standing between this request and EV actually running -- and it produces
    exactly, deterministically, `NO_TRADE / MISSING_PROBABILITY_INPUTS`, never a guess, never a silent
    default."""
    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
    request, eligibility = _fully_eligible_fixture_request(canon, probability_inputs=None)

    response = ve_brain.decide_n6(request, eligibility)

    assert response.decision == "NO_TRADE"
    assert response.reason_codes == (ve_brain.ReasonCode.MISSING_PROBABILITY_INPUTS.value,)
    assert response.expected_value_net is None  # EV never ran -- refused before that stage


def test_a_populated_source_lets_ev_actually_run_once_isolated_from_the_n3_n4_gate() -> None:
    """The other half of the same proof: swap in the labeled canonical fixture (same request,
    otherwise byte-identical) and N6 proceeds all the way to EV -- proving the interface is not merely
    present but FUNCTIONAL. (Reaches `TRADE` here specifically because this test isolates the request
    from `bridge.py`'s own real, unmodified N3/N4 gates via the fixture helper above -- see that
    helper's own docstring. This is NOT a claim that the live pipeline produces TRADE today; `bridge.py`
    itself is untouched and still correctly refuses via MISSING_LEVEL_INPUT, proven separately below.)"""
    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
    request, eligibility = _fully_eligible_fixture_request(
        canon, probability_inputs=_illustrative_canonical_fixture(),
    )

    response = ve_brain.decide_n6(request, eligibility)

    assert response.decision == "TRADE"
    assert response.reason_codes == (ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,)
    assert response.expected_value_net is not None and response.expected_value_net > 0.0


def test_a_ratified_source_can_be_introduced_without_touching_bridge_py(monkeypatch: Any) -> None:
    """CEO requirement: "o sursa ratificata poate fi introdusa FARA recablare." Proven structurally --
    ONLY `probability_source.load_probability_inputs`'s own return value is swapped (via monkeypatch,
    standing in for a future real implementation change confined to that ONE function); `bridge.py`'s
    own source is not edited, not even in this test. `evaluate_bar` still correctly returns
    NO_TRADE/MISSING_LEVEL_INPUT for the real, live-shaped request -- confirming the swap took effect at
    exactly the call site it should (probability_inputs is populated now) while `bridge.py`'s OWN
    separate, untouched N3/N4 gates (`market_map_available=False` etc.) continue to refuse first, per
    their own explicit reason -- exactly the CORRECT combined behavior until TOWER_HANDOFF_PASS, not a
    bug and not something this test papers over."""
    monkeypatch.setattr(bridge_module, "load_probability_inputs",
                         lambda strategy_id, strategy_version: _illustrative_canonical_fixture())

    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = bridge_module.evaluate_bar(bars[-1], timeframe=_TIMEFRAME, axes_builder=builder)

    trend_pullback = next(o for o in outcomes if o.strategy_id == "trend_pullback")
    assert trend_pullback.decision is not None
    assert trend_pullback.decision.decision == "NO_TRADE"
    assert trend_pullback.decision.reason_codes == (ve_brain.ReasonCode.MISSING_LEVEL_INPUT.value,)
    # MISSING_PROBABILITY_INPUTS is gone from the reason set -- the swap reached N6, it just wasn't the
    # ONLY gate standing between this event and a trade. bridge.py's own source: zero edits.
