"""Testele post VE_HANDOFF_CONDITIONAL: registrul CANONIC e INTERN artefactului VE (nu parametru), proprietatea
strategiei nu poate fi suprascrisă de obiectele consumatorului ȘI nici registrul nu poate fi injectat de consumator.
FAIL-2 axe brute + A5 + calea COMPLETĂ. Testul component izolat e insuficient. (Cele 25 end-to-end rămân la AI Trader.)
"""

from __future__ import annotations

import dataclasses
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

from ve_brain import (  # noqa: E402
    DecisionRequest, DuplicateStrategyPolicyError, ELIGIBILITY_POLICY_VERSION, EligibilityDecision, HierarchyLevel,
    INPUT_CONTRACT_ID, N1_CONTRACT_VERSION, NonComparableDecisionError, OutcomeCell, ProbabilityInputs,
    RAW_AXIS_SCHEMA_VERSION, ROUTER_VERSION, RawAxes, RoutingMode, SemanticRegime, StrategyRegistry, StrategyRouter,
    ValidationStatus, applicable_regimes, compare_decisions, decide_n6, regime_fingerprint,
    register_canonical_strategy, reset_canonical_registry, set_registry_available, strategy_policy_fingerprint,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402

MC = "canonical-evaluator-v2.7.66-A2"
AXES = RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")   # {TREND_UP}


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    """Registrul canonic e INTERN + global → resetat înaintea FIECĂRUI test pentru izolare."""
    reset_canonical_registry()


def _sc(sid: str, *, family: str, allowed: tuple[SemanticRegime, ...],
        status: ValidationStatus = ValidationStatus.RATIFIED) -> SC:
    return SC(strategy_id=sid, strategy_family=family, allowed_regimes=allowed, allowed_directions=("LONG",),
              arming_regimes=(), trigger_transition=None, minimum_regime_confidence=0.0, required_N2_bias=None,
              required_N3_map=True, required_N4_confirmation=None, entry_rule="e", invalidation_rule="i",
              exit_rule="x", holding_window=10, validation_status=status, strategy_version="v1",
              measurement_contract_version=MC)


TREND_SC = _sc("trend", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,))
RANGE_SC = _sc("range_fade", family="RANGE_MEAN_REVERSION", allowed=(SemanticRegime.RANGE,))


def _register(*contracts: SC) -> None:
    """Populează registrul CANONIC intern prin API-ul controlat (unica sursă pe care N6 o citește)."""
    for c in contracts:
        register_canonical_strategy(c)


def _prob() -> ProbabilityInputs:
    cell = OutcomeCell(n=1000, n_target=500, n_horizon=200, sum_horizon_R=0.0)
    return ProbabilityInputs(hierarchy=(HierarchyLevel(cell=cell, siblings=(cell, cell)),), credibility=0.80)


def _candidate(c: SC, *, enter: bool = True, event: str = "ev1", regime_fp: str | None = None,
               family: str | None = None, policy_fp: str | None = None, status: ValidationStatus | None = None,
               n1v: str = N1_CONTRACT_VERSION, version: str = "v1") -> DecisionRequest:
    return DecisionRequest(
        contract_id=INPUT_CONTRACT_ID, strategy_id=c.strategy_id, strategy_version=version,
        validation_status=status if status is not None else c.validation_status,
        strategy_family=family if family is not None else c.strategy_family,
        strategy_policy_fingerprint=policy_fp if policy_fp is not None else strategy_policy_fingerprint(c),
        market_event_id=event, regime_fingerprint=regime_fp if regime_fp is not None else regime_fingerprint(AXES),
        market_state_ref="ms", regime_label="TREND_UP", bias_direction="LONG", market_map_available=True,
        levels_available=True, confirmation_available=True, entry_price=100.0, stop_price=99.0, target_kind="rr",
        target_param=(3.0 if enter else 0.001), holding_window=10, atr=1.0, probability_inputs=_prob(),
        full_spread_price=0.05, entry_slippage_price=0.0, exit_slippage_price=0.0, symbol="XAUUSD", timeframe="M15",
        block_start=0, block_end=100, segment_id="s", manifest_hash="m", n1_contract_version=n1v,
        raw_axis_schema_version=RAW_AXIS_SCHEMA_VERSION, router_version=ROUTER_VERSION,
        eligibility_policy_version=ELIGIBILITY_POLICY_VERSION, measurement_contract_version=MC,
        configuration_fingerprint="rh")


def _real_elig(c: SC, event: str = "ev1") -> EligibilityDecision:
    return StrategyRouter((c,)).eligible(AXES, event, "LONG", 1.0)[0]


def _forged_elig(sid: str, *, event: str = "ev1", regime_fp: str | None = None) -> EligibilityDecision:
    """Eligibilitate FABRICATĂ manual cu ID-uri POTRIVITE, is_eligible=TRUE, reason=ROUTER_ELIGIBLE."""
    return EligibilityDecision(strategy_id=sid, strategy_version="v1", market_event_id=event,
                               regime_fingerprint=regime_fp if regime_fp is not None else regime_fingerprint(AXES),
                               router_version=ROUTER_VERSION, eligible=True, mode=RoutingMode.NORMAL,
                               matched_regimes=("TREND_UP",), reason_codes=("ROUTER_ELIGIBLE",))


# ═══ FIXTURE-UL DECISIV + testele de registru ═══
def test_c02_range_forged_eligibility_matching_ids_no_trade() -> None:
    # DECISIV: range strategy, TOATE ID-urile potrivite, is_eligible=TRUE, reason=ROUTER_ELIGIBLE, EV pozitiv
    _register(RANGE_SC)
    cand = _candidate(RANGE_SC)                                  # policy_fp POTRIVIT cu registrul
    forged = _forged_elig("range_fade")
    r = decide_n6(cand, forged)
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c01_range_real_eligibility_no_trade() -> None:
    _register(RANGE_SC)
    r = decide_n6(_candidate(RANGE_SC), _real_elig(RANGE_SC))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c03_range_requires_false_ignored_reads_registry() -> None:
    # N6 citește requires_true_range DIN REGISTRU (candidatul n-are cum să-l falsifice — nu e câmp autoritar)
    _register(RANGE_SC)
    r = decide_n6(_candidate(RANGE_SC), _forged_elig("range_fade"))
    assert r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c04_range_presented_as_trend_no_trade() -> None:
    _register(RANGE_SC)
    cand = _candidate(RANGE_SC, family="TREND_PULLBACK")         # familie FALSĂ
    r = decide_n6(cand, _forged_elig("range_fade"))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c05_forged_policy_fingerprint_no_trade() -> None:
    _register(TREND_SC)
    r = decide_n6(_candidate(TREND_SC, policy_fp="FORGED"), _real_elig(TREND_SC))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c06_unknown_strategy_no_trade() -> None:
    _register(TREND_SC)                                          # range_fade absent
    r = decide_n6(_candidate(RANGE_SC), _forged_elig("range_fade"))
    assert r.reason_codes == ("UNKNOWN_STRATEGY",)


def test_c07_unknown_version_no_trade() -> None:
    _register(TREND_SC)
    r = decide_n6(_candidate(TREND_SC, version="v2"), _real_elig(TREND_SC))   # versiune inexistentă
    assert r.reason_codes == ("UNKNOWN_STRATEGY",)


def test_c08_registry_unavailable_no_trade() -> None:
    _register(TREND_SC)
    set_registry_available(False)                               # fault: registry indisponibil → fail-closed
    r = decide_n6(_candidate(TREND_SC), _real_elig(TREND_SC))
    assert r.reason_codes == ("STRATEGY_REGISTRY_UNAVAILABLE",)


def test_c09_trend_real_eligibility_positive_ev_trades() -> None:
    _register(TREND_SC)
    r = decide_n6(_candidate(TREND_SC), _real_elig(TREND_SC))
    assert r.decision == "TRADE" and r.reason_codes == ("TRADE_VALIDATED_EDGE",)


def test_c10_trend_eligibility_for_another_event_no_trade() -> None:
    _register(TREND_SC)
    r = decide_n6(_candidate(TREND_SC, event="ev1"), _real_elig(TREND_SC, event="ev2"))
    assert r.reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_c11_metadata_changed_after_router_no_trade() -> None:
    exp = _sc("s", family="F", allowed=(SemanticRegime.TREND_UP,), status=ValidationStatus.EXPERIMENTAL)
    _register(exp)
    cand = _candidate(exp, status=ValidationStatus.RATIFIED)     # status FALSIFICAT în candidat
    r = decide_n6(cand, _forged_elig("s"))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c12_direct_call_manual_objects_no_bypass() -> None:
    _register(RANGE_SC)
    r = decide_n6(_candidate(RANGE_SC), _forged_elig("range_fade"))   # obiecte construite manual
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c13_same_id_version_cannot_have_two_policies() -> None:
    reg = StrategyRegistry(); reg.register(TREND_SC)
    with pytest.raises(DuplicateStrategyPolicyError):
        reg.register(_sc("trend", family="DIFFERENT", allowed=(SemanticRegime.COMPRESSION,)))


def test_c14_full_real_path_still_works() -> None:
    _register(TREND_SC)
    router = StrategyRouter((TREND_SC,))
    elig = router.eligible(AXES, "ev1", "LONG", 1.0)[0]
    r = decide_n6(_candidate(TREND_SC, event="ev1"), elig)
    assert r.decision == "TRADE"


def test_c15_old_consumer_fails_explicitly() -> None:
    _register(TREND_SC)
    r = decide_n6(_candidate(TREND_SC, n1v="n1-OLD"), _real_elig(TREND_SC))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("INCOMPATIBLE_N1_CONTRACT",)


def test_c16_consumer_cannot_inject_a_false_registry() -> None:
    # AUTO-ATAC (addendum CEO): consumatorul construiește un registru MINCINOS (range declarat ca trend ⇒
    # requires_true_range=False). Nu există CALE prin care acel registru ajunge la N6 — decide_n6 NU ia registry.
    # Sursa canonică rămâne cea internă (range_fade e range), deci blocajul de range ține.
    _register(RANGE_SC)                                          # adevărul canonic: range_fade E range
    liar = StrategyRegistry()
    liar.register(_sc("range_fade", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,)))  # minte
    # candidatul poartă amprenta registrului MINCINOS al consumatorului (încearcă să pară potrivit)
    fake_c = liar.resolve("range_fade", "v1")
    assert fake_c is not None
    cand = _candidate(RANGE_SC, family=fake_c.strategy_family,
                      policy_fp=strategy_policy_fingerprint(fake_c))
    r = decide_n6(cand, _forged_elig("range_fade"))
    # amprenta consumatorului NU se potrivește cu cea canonică ⇒ mismatch (registrul fals nu poate ajunge la N6)
    assert r.decision == "NO_TRADE" and r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


# ═══ FAIL-2 — axele brute independente ═══
def _ax(**kw: object) -> RawAxes:
    d: dict[str, object] = dict(is_compressed=False, is_displacement=False, direction="up", structure="strong")
    d.update(kw)
    return RawAxes(**d)  # type: ignore[arg-type]


def test_f2_both_flags_survive_multiaxial() -> None:
    a = applicable_regimes(_ax(is_compressed=True, is_displacement=True, structure="range", direction="neutral"))
    assert SemanticRegime.COMPRESSION in a and SemanticRegime.BREAKOUT_TRANSITION in a


def test_f2_volatility_string_not_used() -> None:
    base = dict(is_compressed=True, is_displacement=True, structure="range", direction="neutral")
    assert applicable_regimes(RawAxes(**base, volatility_state="expanding")) == \
        applicable_regimes(RawAxes(**base, volatility_state="compressed"))


def test_f2_multiaxial_compression_and_trend() -> None:
    assert applicable_regimes(_ax(is_compressed=True, structure="strong", direction="up")) == \
        frozenset({SemanticRegime.COMPRESSION, SemanticRegime.TREND_UP})


# ═══ A5 — amprentă + comparabilitate ═══
def test_a5_fingerprint_by_data_and_compare_raises() -> None:
    _register(TREND_SC)
    xau = decide_n6(_candidate(TREND_SC), _real_elig(TREND_SC))
    es = decide_n6(dataclasses.replace(_candidate(TREND_SC), symbol="ES"), _real_elig(TREND_SC))
    assert xau.configuration_fingerprint != es.configuration_fingerprint
    with pytest.raises(NonComparableDecisionError):
        compare_decisions(xau.configuration_fingerprint, es.configuration_fingerprint)
