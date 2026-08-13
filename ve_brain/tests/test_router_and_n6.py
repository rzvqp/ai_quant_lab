"""Testele artefactului post VE_HANDOFF_FAIL: FAIL-1 (router = poartă obligatorie, 10) + FAIL-2 (axe brute în
contract, 10) + A5 (identitate date + comparabilitate) + calea COMPLETĂ N1→Router→EligibilityDecision→EV→N6.
Testul component izolat NU e suficient. (Cele 25 end-to-end rămân la AI Trader.)"""

from __future__ import annotations

import dataclasses
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_brain import (  # noqa: E402
    DecisionRequest, ELIGIBILITY_POLICY_VERSION, HierarchyLevel, INPUT_CONTRACT_ID, N1_CONTRACT_VERSION,
    NonComparableDecisionError, OutcomeCell, ProbabilityInputs, RAW_AXIS_SCHEMA_VERSION, ROUTER_VERSION, RawAxes,
    RoutingMode, SemanticRegime, StrategyRegistry, StrategyRouter, ValidationStatus, applicable_regimes,
    compare_decisions, data_identity, decide_n6, regime_fingerprint,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402

MC = "canonical-evaluator-v2.7.66-A2"


def _sc(sid: str, *, family: str = "F", allowed: tuple[SemanticRegime, ...] = (SemanticRegime.TREND_UP,),
        directions: tuple[str, ...] = ("LONG",), arming: tuple[SemanticRegime, ...] = (),
        trigger: SemanticRegime | None = None, status: ValidationStatus = ValidationStatus.RATIFIED) -> SC:
    return SC(strategy_id=sid, strategy_family=family, allowed_regimes=allowed, allowed_directions=directions,
              arming_regimes=arming, trigger_transition=trigger, minimum_regime_confidence=0.0, required_N2_bias=None,
              required_N3_map=True, required_N4_confirmation=None, entry_rule="e", invalidation_rule="i",
              exit_rule="x", holding_window=10, validation_status=status, strategy_version="v1",
              measurement_contract_version=MC)


TREND_AXES = RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")
COMPRESS_AXES = RawAxes(is_compressed=True, is_displacement=False, direction="neutral", structure="range")


def _prob() -> ProbabilityInputs:
    cell = OutcomeCell(n=1000, n_target=500, n_horizon=200, sum_horizon_R=0.0)
    return ProbabilityInputs(hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, cell)),), credibility=0.80)


def _candidate(sid: str, status: ValidationStatus, *, enter: bool = True, event: str = "ev1", regime_fp: str = "rfp",
               with_prob: bool = True, confirmation: bool = True, n1v: str = N1_CONTRACT_VERSION) -> DecisionRequest:
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id=sid, strategy_version="v1", validation_status=status,
        market_event_id=event, regime_fingerprint=regime_fp, market_state_ref="ms", regime_label="TREND_UP",
        bias_direction="LONG", market_map_available=True, levels_available=True, confirmation_available=confirmation,
        entry_price=100.0, stop_price=99.0, target_kind="rr", target_param=(3.0 if enter else 0.001),
        holding_window=10, atr=1.0, probability_inputs=_prob() if with_prob else None, full_spread_price=0.05,
        entry_slippage_price=0.0, exit_slippage_price=0.0, symbol="XAUUSD", timeframe="M15", block_start=0,
        block_end=100, segment_id="seg1", manifest_hash="mh", n1_contract_version=n1v,
        raw_axis_schema_version=RAW_AXIS_SCHEMA_VERSION, router_version=ROUTER_VERSION,
        eligibility_policy_version=ELIGIBILITY_POLICY_VERSION, measurement_contract_version=MC,
        configuration_fingerprint="runhash")


def _elig(sc: SC, axes: RawAxes, event: str = "ev1", bias: str = "LONG"):
    return StrategyRouter((sc,)).eligible(axes, event, bias, 1.0)[0]


# ═══ FAIL-1 — routerul e poartă obligatorie (10) ═══
def test_f1_01_range_ratified_positive_ev_no_trade() -> None:
    rng = _sc("range_fade", family="RANGE_MEAN_REVERSION", allowed=(SemanticRegime.RANGE,))
    elig = _elig(rng, TREND_AXES)
    cand = _candidate("range_fade", ValidationStatus.RATIFIED, regime_fp=regime_fingerprint(TREND_AXES))
    r = decide_n6(cand, elig)
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_f1_02_direct_call_no_eligibility() -> None:
    r = decide_n6(_candidate("s", ValidationStatus.RATIFIED), None)   # fără router
    assert r.decision == "NO_TRADE" and r.reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_03_eligibility_for_another_strategy() -> None:
    elig = _elig(_sc("other"), TREND_AXES)
    cand = _candidate("target", ValidationStatus.RATIFIED, regime_fp=regime_fingerprint(TREND_AXES))
    assert decide_n6(cand, elig).reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_04_eligibility_for_another_event() -> None:
    elig = _elig(_sc("s"), TREND_AXES, event="ev2")
    cand = _candidate("s", ValidationStatus.RATIFIED, event="ev1", regime_fp=regime_fingerprint(TREND_AXES))
    assert decide_n6(cand, elig).reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_05_stale_eligibility_old_regime() -> None:
    elig = _elig(_sc("s"), TREND_AXES)                               # amprentă din regimul VECHI
    cand = _candidate("s", ValidationStatus.RATIFIED, regime_fp=regime_fingerprint(COMPRESS_AXES))  # regim curent DIFERIT
    assert decide_n6(cand, elig).reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_06_fingerprint_mismatch() -> None:
    elig = _elig(_sc("s"), TREND_AXES)
    cand = _candidate("s", ValidationStatus.RATIFIED, regime_fp="WRONG")
    assert decide_n6(cand, elig).reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_07_trend_eligible_positive_ev_trades() -> None:
    elig = _elig(_sc("trend"), TREND_AXES)
    assert elig.eligible
    cand = _candidate("trend", ValidationStatus.RATIFIED, regime_fp=regime_fingerprint(TREND_AXES))
    r = decide_n6(cand, elig)
    assert r.decision == "TRADE" and r.reason_codes == ("TRADE_VALIDATED_EDGE",)


def test_f1_08_trend_ineligible_positive_ev_no_trade() -> None:
    elig = _elig(_sc("trend"), COMPRESS_AXES)                        # trend neeligibil în compresie
    assert not elig.eligible
    cand = _candidate("trend", ValidationStatus.RATIFIED, regime_fp=regime_fingerprint(COMPRESS_AXES))
    assert decide_n6(cand, elig).reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_f1_09_direct_instantiation_cannot_bypass() -> None:
    # nu există semnătură legacy permisivă: eligibility e parametru OBLIGATORIU; None ⇒ MISSING
    import inspect
    params = inspect.signature(decide_n6).parameters
    assert "eligibility" in params and params["eligibility"].default is inspect.Parameter.empty
    assert decide_n6(_candidate("s", ValidationStatus.RATIFIED), None).decision == "NO_TRADE"


def test_f1_10_traceable_to_router_decision() -> None:
    elig = _elig(_sc("trend"), TREND_AXES, event="evX")
    cand = _candidate("trend", ValidationStatus.RATIFIED, event="evX", regime_fp=regime_fingerprint(TREND_AXES))
    r = decide_n6(cand, elig)
    assert r.decision == "TRADE"
    assert elig.market_event_id == cand.market_event_id and elig.regime_fingerprint == cand.regime_fingerprint
    assert elig.router_version == ROUTER_VERSION


# ═══ FAIL-2 — axele brute independente (10) ═══
def _ax(**kw: object) -> RawAxes:
    d: dict[str, object] = dict(is_compressed=False, is_displacement=False, direction="up", structure="strong")
    d.update(kw)
    return RawAxes(**d)  # type: ignore[arg-type]


def test_f2_01_compressed_only() -> None:
    assert applicable_regimes(_ax(is_compressed=True, structure="range", direction="neutral")) == \
        frozenset({SemanticRegime.COMPRESSION})


def test_f2_02_displacement_only_no_invented_compression() -> None:
    a = applicable_regimes(_ax(is_displacement=True, structure="range", direction="neutral"))
    assert SemanticRegime.COMPRESSION not in a and SemanticRegime.BREAKOUT_TRANSITION in a


def test_f2_03_both_flags_survive() -> None:
    a = applicable_regimes(_ax(is_compressed=True, is_displacement=True, structure="range", direction="neutral"))
    assert SemanticRegime.COMPRESSION in a and SemanticRegime.BREAKOUT_TRANSITION in a   # ambele fapte supraviețuiesc


def test_f2_04_expanding_state_does_not_erase_compressed() -> None:
    a = _ax(is_compressed=True, is_displacement=True, volatility_state="expanding", structure="range", direction="neutral")
    assert a.is_compressed is True and SemanticRegime.COMPRESSION in applicable_regimes(a)


def test_f2_05_compressed_state_does_not_erase_displacement() -> None:
    a = _ax(is_compressed=True, is_displacement=True, volatility_state="compressed", structure="range", direction="neutral")
    assert a.is_displacement is True and SemanticRegime.BREAKOUT_TRANSITION in applicable_regimes(a)


def test_f2_06_router_not_using_volatility_string() -> None:
    # aceleași flaguri, string-uri de rezumat DIFERITE ⇒ aceeași mulțime (routerul nu citește stringul)
    base = dict(is_compressed=True, is_displacement=True, structure="range", direction="neutral")
    assert applicable_regimes(RawAxes(**base, volatility_state="expanding")) == \
        applicable_regimes(RawAxes(**base, volatility_state="compressed"))


def test_f2_07_serialization_preserves_both_flags() -> None:
    a = _ax(is_compressed=True, is_displacement=True)
    d = dataclasses.asdict(a); a2 = RawAxes(**d)
    assert a2.is_compressed is True and a2.is_displacement is True


def test_f2_08_replay_and_live_same_structure() -> None:
    a = _ax(is_compressed=True, is_displacement=True, structure="range", direction="neutral")
    assert applicable_regimes(a) == applicable_regimes(a)            # determinist
    assert regime_fingerprint(a) == regime_fingerprint(a)


def test_f2_09_old_contract_refused_incompatible_n1() -> None:
    cand = _candidate("s", ValidationStatus.RATIFIED, n1v="n1-OLD-single-string")
    elig = _elig(_sc("s"), TREND_AXES)
    r = decide_n6(cand, elig)
    assert r.decision == "NO_TRADE" and r.reason_codes == ("INCOMPATIBLE_N1_CONTRACT",)


def test_f2_10_multiaxial_reaches_eligibility() -> None:
    # compressed + strong + up ⇒ {COMPRESSION, TREND_UP}: ambele familii eligibile din aceleași axe brute
    multi = _ax(is_compressed=True, is_displacement=False, direction="up", structure="strong")
    assert applicable_regimes(multi) == frozenset({SemanticRegime.COMPRESSION, SemanticRegime.TREND_UP})
    r = StrategyRouter((_sc("t", allowed=(SemanticRegime.TREND_UP,)),
                        _sc("c", allowed=(SemanticRegime.COMPRESSION,)))).eligible(multi, "ev", "LONG", 1.0)
    assert all(d.eligible for d in r) and len(r) == 2


# ═══ A5 — identitatea datelor + comparabilitatea impusă ═══
def test_a5_data_identity_covers_blocks_and_symbol() -> None:
    a = data_identity(symbol="XAUUSD", timeframe="M15", block_start=0, block_end=100, segment_id="s", manifest_hash="m")
    b = data_identity(symbol="ES", timeframe="M15", block_start=0, block_end=100, segment_id="s", manifest_hash="m")
    assert a != b                                                   # simbol diferit ⇒ identitate diferită


def test_a5_fingerprint_differs_by_data_and_compare_raises() -> None:
    elig = _elig(_sc("s"), TREND_AXES)
    fp = regime_fingerprint(TREND_AXES)
    xau = decide_n6(_candidate("s", ValidationStatus.RATIFIED, regime_fp=fp), elig)
    es = decide_n6(dataclasses.replace(_candidate("s", ValidationStatus.RATIFIED, regime_fp=fp), symbol="ES"), elig)
    assert xau.configuration_fingerprint != es.configuration_fingerprint   # datele intră în amprentă
    compare_decisions(xau.configuration_fingerprint, xau.configuration_fingerprint)
    with pytest.raises(NonComparableDecisionError):
        compare_decisions(xau.configuration_fingerprint, es.configuration_fingerprint)


# ═══ CALEA COMPLETĂ N1 → Router → EligibilityDecision → EV → N6 ═══
def test_full_path_n1_router_eligibility_ev_n6() -> None:
    reg = StrategyRegistry(); reg.register(_sc("trend"))
    axes = TREND_AXES                                              # N1 axe brute
    router = StrategyRouter(reg.n6_eligible())                    # Router
    elig = router.eligible(axes, "ev1", "LONG", 1.0)[0]           # EligibilityDecision
    assert elig.eligible
    cand = _candidate("trend", ValidationStatus.RATIFIED, event="ev1", regime_fp=regime_fingerprint(axes))
    r = decide_n6(cand, elig)                                     # EV → N6
    assert r.decision == "TRADE" and r.expected_value_net is not None


# ═══ cele 5 condiții de range (rămân) ═══
def test_range_conditions_fail_closed_and_persisted() -> None:
    rng = _sc("range_fade", family="RANGE_MEAN_REVERSION", allowed=(SemanticRegime.RANGE,))
    for axes in (TREND_AXES, COMPRESS_AXES, _ax(is_compressed=False, is_displacement=False, direction="neutral",
                                                structure="range")):
        d = _elig(rng, axes)
        assert not d.eligible and d.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)
        assert SemanticRegime.RANGE not in applicable_regimes(axes)     # nicidecum produs
