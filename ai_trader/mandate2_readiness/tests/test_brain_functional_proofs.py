"""Steps 3-4 of the CEO's post-install 12-step list (Mandate 2 activation, 2026-08-14): "demonstrezi
range_fade -> NO_TRADE" si "demonstrezi trend_pullback -> TRADE, intr-un fixture controlat." Red Team's
own `RT-PIN-0001_ve_brain_wheel_a1d2a6d_PASS.md` already ran these two functional checks on the installed
package (checklist items 9-10); this file REPRODUCES them independently, in THIS environment, against the
REAL installed `ve_brain` package -- not trusted from the report alone.

Both fixtures use the REAL canonical catalog (`ve_brain.CANONICAL_STRATEGIES`), the REAL `StrategyRouter`
(for `trend_pullback`) and the REAL `decide_n6` gate -- nothing here is a stub or a mock of `ve_brain`
itself. This is deliberately NOT wired into any live process; it is the fixture-level proof the CEO's
step 5 ("begin integration feed -> N1 -> Router -> Eligibility -> EV -> N6") requires as a precondition.

`ve_brain` is a genuine dependency of THIS test file only -- `mandate2_readiness`'s own production code
(`broker_gate.py`, `artifact_pin.py`, `event_identity.py`, `decision_provenance.py`, `wheel_verification.py`)
still imports nothing from it, matching every other CEO instruction in this mandate not to reach into
N1-N6/EV internals ahead of real integration."""

from __future__ import annotations

import ve_brain  # type: ignore[import-untyped]  # external VE artifact, no py.typed marker -- never modified

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"
_BLOCK_START = 0
_BLOCK_END = 1_000
_SEGMENT_ID = "mandate2-functional-proof-segment"
_MANIFEST_HASH = "mandate2-functional-proof-manifest-hash"

# CEO Mandate Step 8 cost calibration figures (BASE_PROVISIONAL, from
# AI_TRADER_MANDATE8_STEP1_COST_CALIBRATION_REPORT.md) -- 0.10 spread + 2x0.05 slippage = 0.20 round-trip,
# reused here rather than inventing new numbers for the fixture.
_FULL_SPREAD_PRICE = 0.10
_ENTRY_SLIPPAGE_PRICE = 0.05
_EXIT_SLIPPAGE_PRICE = 0.05


def _canon(strategy_id: str) -> ve_brain.StrategyContract:
    matches = [c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == strategy_id]
    assert len(matches) == 1, f"expected exactly one canonical entry for {strategy_id!r}, found {len(matches)}"
    return matches[0]


def _strong_probability_inputs() -> ve_brain.ProbabilityInputs:
    """A single global cell, 200 trades / 150 target hits (75% raw), 0 horizon exits -- enough sample size
    that the 80%-credibility LCB on p_t clears a 2R target against a 0.20 round-trip cost at r=10.0."""
    cell = ve_brain.OutcomeCell(n=200, n_target=150, n_horizon=0, sum_horizon_R=0.0)
    return ve_brain.ProbabilityInputs(hierarchy=(ve_brain.HierarchyLevel(cell=cell),), credibility=0.80)


def _base_request_kwargs(*, canon: ve_brain.StrategyContract, market_event_id: str, regime_fingerprint: str,
                          configuration_fingerprint: str) -> dict[str, object]:
    return dict(
        contract_id=ve_brain.INPUT_CONTRACT_ID,
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version,
        validation_status=canon.validation_status, strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id=market_event_id, regime_fingerprint=regime_fingerprint,
        market_state_ref="proof-market-state-ref",
        entry_price=2400.0, stop_price=2390.0, target_kind="rr", target_param=2.0, holding_window=10, atr=10.0,
        full_spread_price=_FULL_SPREAD_PRICE, entry_slippage_price=_ENTRY_SLIPPAGE_PRICE,
        exit_slippage_price=_EXIT_SLIPPAGE_PRICE,
        symbol=_SYMBOL, timeframe=_TIMEFRAME, block_start=_BLOCK_START, block_end=_BLOCK_END,
        segment_id=_SEGMENT_ID, manifest_hash=_MANIFEST_HASH,
        n1_contract_version=ve_brain.N1_CONTRACT_VERSION, raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION,
        router_version=ve_brain.ROUTER_VERSION, eligibility_policy_version=ve_brain.ELIGIBILITY_POLICY_VERSION,
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
        configuration_fingerprint=configuration_fingerprint,
    )


def test_trend_pullback_reaches_trade_through_the_real_router_and_n6() -> None:
    """Step 4: a legitimate RATIFIED trend strategy, routed through the REAL `StrategyRouter` off a
    TREND_UP-producing `RawAxes`, with a positive-EV fixture, reaches `decide_n6` -> TRADE."""
    canon = _canon("trend_pullback")
    axes = ve_brain.RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")
    assert ve_brain.applicable_regimes(axes) == frozenset({ve_brain.SemanticRegime.TREND_UP})

    router = ve_brain.StrategyRouter(ve_brain.CANONICAL_STRATEGIES)
    market_event_id = "PROOF-EVENT-TREND-001"
    decisions = router.eligible(axes, market_event_id, bias_direction="LONG", confidence=1.0)
    eligibility = next(d for d in decisions if d.strategy_id == "trend_pullback")
    assert eligibility.eligible is True
    assert eligibility.mode is ve_brain.RoutingMode.NORMAL

    candidate = ve_brain.DecisionRequest(
        **_base_request_kwargs(
            canon=canon, market_event_id=market_event_id, regime_fingerprint=eligibility.regime_fingerprint,
            configuration_fingerprint="mandate2-proof-config-trend-001"),
        regime_label="TREND_UP", bias_direction="LONG", market_map_available=True, levels_available=True,
        confirmation_available=True, probability_inputs=_strong_probability_inputs(),
    )

    response = ve_brain.decide_n6(candidate, eligibility)

    assert response.decision == "TRADE", response.reason_codes
    assert response.reason_codes == (ve_brain.ReasonCode.TRADE_VALIDATED_EDGE.value,)
    assert response.expected_value_net is not None and response.expected_value_net > 0.0


def test_range_fade_stays_no_trade_even_with_matching_eligibility_and_positive_ev() -> None:
    """Step 3: `range_fade`'s canonical definition declares `RANGE` in `allowed_regimes`, so
    `requires_true_range(canon)` is True and N6's catalog-derived block fires BEFORE eligibility or EV are
    even inspected (n6.py's own step 5+7, ahead of step 8). To prove the block is genuinely independent of
    those later checks -- not just untested because a realistic router would never route range_fade in the
    first place, since RANGE is never produced by `applicable_regimes` -- this fixture hand-supplies a
    MATCHING, eligible=True `EligibilityDecision` and a fully positive-EV probability fixture (the same one
    the trend_pullback proof uses) and shows N6 still refuses. This mirrors RT-PIN-0001 checklist item 9
    exactly ("decide_n6(range_fade candidate, matching eligibility, EV+) -> NO_TRADE /
    TRUE_RANGE_NOT_IDENTIFIABLE")."""
    canon = _canon("range_fade")
    assert ve_brain.requires_true_range(canon) is True

    market_event_id = "PROOF-EVENT-RANGE-001"
    regime_fingerprint = "mandate2-proof-range-fingerprint"
    eligibility = ve_brain.EligibilityDecision(
        strategy_id=canon.strategy_id, strategy_version=canon.strategy_version, market_event_id=market_event_id,
        regime_fingerprint=regime_fingerprint, router_version=ve_brain.ROUTER_VERSION, eligible=True,
        mode=ve_brain.RoutingMode.NORMAL, matched_regimes=("RANGE",),
        reason_codes=(ve_brain.ReasonCode.ROUTER_ELIGIBLE.value,),
    )

    candidate = ve_brain.DecisionRequest(
        **_base_request_kwargs(
            canon=canon, market_event_id=market_event_id, regime_fingerprint=regime_fingerprint,
            configuration_fingerprint="mandate2-proof-config-range-001"),
        regime_label="RANGE", bias_direction=None, market_map_available=True, levels_available=True,
        confirmation_available=True, probability_inputs=_strong_probability_inputs(),
    )

    response = ve_brain.decide_n6(candidate, eligibility)

    assert response.decision == "NO_TRADE", response.reason_codes
    assert response.reason_codes == (ve_brain.ReasonCode.TRUE_RANGE_NOT_IDENTIFIABLE.value,)
    # the block fired at step 5+7 -- before EV ever ran, so no EV terms are populated on the response
    assert response.expected_value_net is None


def test_the_two_proofs_are_reproducible_pure_function_calls() -> None:
    """`decide_n6` is documented as deterministic on its inputs -- calling it twice with byte-identical
    fixtures must yield the identical decision and configuration_fingerprint, matching the fingerprint
    module's own "same inputs, same fingerprint" contract."""
    canon = _canon("trend_pullback")
    axes = ve_brain.RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")
    router = ve_brain.StrategyRouter(ve_brain.CANONICAL_STRATEGIES)
    market_event_id = "PROOF-EVENT-TREND-DETERMINISM-001"
    eligibility = next(d for d in router.eligible(axes, market_event_id, bias_direction="LONG", confidence=1.0)
                        if d.strategy_id == "trend_pullback")
    kwargs = _base_request_kwargs(
        canon=canon, market_event_id=market_event_id, regime_fingerprint=eligibility.regime_fingerprint,
        configuration_fingerprint="mandate2-proof-config-determinism-001")
    candidate = ve_brain.DecisionRequest(
        **kwargs, regime_label="TREND_UP", bias_direction="LONG", market_map_available=True,
        levels_available=True, confirmation_available=True, probability_inputs=_strong_probability_inputs(),
    )

    first = ve_brain.decide_n6(candidate, eligibility)
    second = ve_brain.decide_n6(candidate, eligibility)

    assert first.decision == second.decision == "TRADE"
    assert first.configuration_fingerprint == second.configuration_fingerprint
    assert first.expected_value_net == second.expected_value_net
