"""Teste post-CONDITIONAL: catalogul CANONIC e INTERN, ÎNCORPORAT și SIGILAT — consumatorul nu-i poate defini
conținutul (a 6-a suprafață). Include fixture-ul DECISIV de otrăvire, refuzul pe catalog nesigilat/versiune greșită,
izolarea entrypoint-ului de test, FAIL-2 axe brute și A5. (Cele 25 end-to-end rămân la AI Trader.)"""

from __future__ import annotations

import dataclasses
import os
import sys

import pytest

_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

import ve_brain.testing as vt  # noqa: E402
from ve_brain import (  # noqa: E402
    CANONICAL_CATALOG_HASH, CANONICAL_CATALOG_VERSION, CANONICAL_STRATEGIES, DecisionRequest,
    DuplicateStrategyPolicyError, ELIGIBILITY_POLICY_VERSION, EligibilityDecision, HierarchyLevel, INPUT_CONTRACT_ID,
    N1_CONTRACT_VERSION, NonComparableDecisionError, OutcomeCell, ProbabilityInputs, RAW_AXIS_SCHEMA_VERSION,
    ROUTER_VERSION, RawAxes, RoutingMode, SealedRegistry, SemanticRegime, StrategyRouter, ValidationStatus,
    applicable_regimes, catalog_hash, compare_decisions, decide_n6, regime_fingerprint, strategy_policy_fingerprint,
)
from ve_brain.regime_routing import StrategyContract as SC  # noqa: E402

MC = "canonical-evaluator-v2.7.66-A2"
AXES = RawAxes(is_compressed=False, is_displacement=False, direction="up", structure="strong")   # {TREND_UP}

_CANON = {c.strategy_id: c for c in CANONICAL_STRATEGIES}
TREND = _CANON["trend_pullback"]        # RATIFIED, TREND_UP
RANGE = _CANON["range_fade"]            # RATIFIED, allowed=(RANGE,)  → requires_true_range
SHADOW = _CANON["trend_shadow"]         # SHADOW_ELIGIBLE, TREND_UP
EXPER = _CANON["trend_experimental"]    # EXPERIMENTAL, TREND_UP


@pytest.fixture(autouse=True)
def _canonical_catalog() -> None:
    """Catalogul canonic e global → deblochează hook-urile de test și repune catalogul de PRODUCȚIE la fiecare test."""
    vt.unlock_for_tests("VE-BRAIN-TEST-ONLY")
    vt.restore_production_catalog()


def _sc(sid: str, *, family: str, allowed: tuple[SemanticRegime, ...],
        status: ValidationStatus = ValidationStatus.RATIFIED) -> SC:
    return SC(strategy_id=sid, strategy_family=family, allowed_regimes=allowed, allowed_directions=("LONG",),
              arming_regimes=(), trigger_transition=None, minimum_regime_confidence=0.0, required_N2_bias=None,
              required_N3_map=True, required_N4_confirmation=None, entry_rule="e", invalidation_rule="i",
              exit_rule="x", holding_window=10, validation_status=status, strategy_version="v1",
              measurement_contract_version=MC)


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


# ═══ FIXTURE-UL DECISIV + testele de catalog canonic ═══
def test_c02_range_forged_eligibility_matching_ids_no_trade() -> None:
    # DECISIV: range strategy din CATALOGUL SIGILAT, TOATE ID-urile potrivite, is_eligible=TRUE, EV pozitiv
    cand = _candidate(RANGE)                                     # policy_fp POTRIVIT cu catalogul
    r = decide_n6(cand, _forged_elig("range_fade"))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c01_range_real_eligibility_no_trade() -> None:
    r = decide_n6(_candidate(RANGE), _real_elig(RANGE))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c03_range_block_reads_catalog_not_candidate() -> None:
    r = decide_n6(_candidate(RANGE), _forged_elig("range_fade"))
    assert r.reason_codes == ("TRUE_RANGE_NOT_IDENTIFIABLE",)


def test_c04_range_presented_as_trend_no_trade() -> None:
    cand = _candidate(RANGE, family="TREND_PULLBACK")            # familie FALSĂ vs catalog
    r = decide_n6(cand, _forged_elig("range_fade"))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c05_forged_policy_fingerprint_no_trade() -> None:
    r = decide_n6(_candidate(TREND, policy_fp="FORGED"), _real_elig(TREND))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c06_unknown_strategy_no_trade() -> None:
    ghost = _sc("ghost", family="F", allowed=(SemanticRegime.TREND_UP,))   # absent din catalog
    r = decide_n6(_candidate(ghost), _forged_elig("ghost"))
    assert r.reason_codes == ("UNKNOWN_STRATEGY",)


def test_c07_unknown_version_no_trade() -> None:
    r = decide_n6(_candidate(TREND, version="v2"), _real_elig(TREND))   # versiune inexistentă în catalog
    assert r.reason_codes == ("UNKNOWN_STRATEGY",)


def test_c08_trend_real_eligibility_positive_ev_trades() -> None:
    r = decide_n6(_candidate(TREND), _real_elig(TREND))
    assert r.decision == "TRADE" and r.reason_codes == ("TRADE_VALIDATED_EDGE",)


def test_c09_shadow_status_from_catalog_is_shadow_candidate() -> None:
    r = decide_n6(_candidate(SHADOW), _real_elig(SHADOW))
    assert r.decision == "SHADOW_TRADE_CANDIDATE" and r.reason_codes == ("SHADOW_CANDIDATE_EV_POSITIVE",)


def test_c10_trend_eligibility_for_another_event_no_trade() -> None:
    r = decide_n6(_candidate(TREND, event="ev1"), _real_elig(TREND, event="ev2"))
    assert r.reason_codes == ("MISSING_OR_INVALID_ELIGIBILITY",)


def test_c11_status_falsified_in_candidate_no_trade() -> None:
    cand = _candidate(EXPER, status=ValidationStatus.RATIFIED)   # status FALSIFICAT (catalog: EXPERIMENTAL)
    r = decide_n6(cand, _forged_elig("trend_experimental"))
    assert r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c12_experimental_status_from_catalog_no_eligible() -> None:
    # candidat ONEST pentru experimental (status potrivit) → oprit de statutul CANONIC, nu de mismatch
    r = decide_n6(_candidate(EXPER), _forged_elig("trend_experimental"))
    assert r.reason_codes == ("NO_ELIGIBLE_STRATEGY",)


def test_c13_catalog_rejects_two_policies_same_key() -> None:
    dup = (_sc("x", family="A", allowed=(SemanticRegime.TREND_UP,)),
           _sc("x", family="B", allowed=(SemanticRegime.COMPRESSION,)))
    with pytest.raises(DuplicateStrategyPolicyError):
        SealedRegistry.build(dup, "v")


def test_c14_full_real_path_still_works() -> None:
    router = StrategyRouter((TREND,))
    elig = router.eligible(AXES, "ev1", "LONG", 1.0)[0]
    r = decide_n6(_candidate(TREND, event="ev1"), elig)
    assert r.decision == "TRADE"


def test_c15_old_consumer_fails_explicitly() -> None:
    r = decide_n6(_candidate(TREND, n1v="n1-OLD"), _real_elig(TREND))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("INCOMPATIBLE_N1_CONTRACT",)


# ═══ A 6-A SUPRAFAȚĂ: catalogul nu poate fi otrăvit / injectat / desigilat ═══
def test_c16_no_arbitrary_definition_api_on_production_surface() -> None:
    import ve_brain
    # API-ul de definire arbitrară + resetarea + marcarea de indisponibilitate NU sunt pe suprafața de producție
    for gone in ("register_canonical_strategy", "reset_canonical_registry", "set_registry_available"):
        assert not hasattr(ve_brain, gone), f"{gone} nu trebuie exportat de ve_brain"
    # decide_n6 NU ia registry ca parametru (2 argumente)
    import inspect
    assert list(inspect.signature(decide_n6).parameters) == ["candidate", "eligibility"]


def test_c17_consumer_cannot_poison_range_as_trend() -> None:
    # Atacul din verdict: încearcă să faci range_fade să treacă ca TREND. Nu există API de înregistrare, iar
    # catalogul SIGILAT păstrează definiția adevărată (range_fade = RANGE). Un candidat care oglindește politica
    # OTRĂVITĂ (fake trend) are altă amprentă decât cea canonică ⇒ mismatch; nu poate ajunge la TRADE.
    poison = _sc("range_fade", family="TREND_PULLBACK", allowed=(SemanticRegime.TREND_UP,))  # definiție mincinoasă
    cand = _candidate(RANGE, family=poison.strategy_family, policy_fp=strategy_policy_fingerprint(poison))
    r = decide_n6(cand, _forged_elig("range_fade"))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("STRATEGY_POLICY_MISMATCH",)


def test_c18_unsealed_catalog_is_refused() -> None:
    vt.install_unsealed_catalog(CANONICAL_STRATEGIES, CANONICAL_CATALOG_VERSION)   # fault: nesigilat
    r = decide_n6(_candidate(TREND), _real_elig(TREND))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("CATALOG_NOT_SEALED",)


def test_c19_version_mismatch_is_refused() -> None:
    vt.force_version_mismatch("some-other-version")               # fault: versiune aprobată nepotrivită
    r = decide_n6(_candidate(TREND), _real_elig(TREND))
    assert r.decision == "NO_TRADE" and r.reason_codes == ("CATALOG_VERSION_MISMATCH",)


def test_c20_test_hooks_blocked_without_unlock() -> None:
    # entrypoint-ul de test e blocat până la unlock explicit → importul accidental din producție nu mutează nimic
    import importlib
    import ve_brain.testing as t
    importlib.reload(t)                                           # revine în starea BLOCATĂ (fără unlock)
    with pytest.raises(RuntimeError):
        t.install_unsealed_catalog(CANONICAL_STRATEGIES, "v")
    with pytest.raises(RuntimeError):
        t.unlock_for_tests("WRONG-TOKEN")


def test_c21_embedded_catalog_integrity() -> None:
    # amprenta încorporată = amprenta recalculată; N6 folosește exact versiunea/amprenta aprobată
    import ve_brain.n6 as n6
    assert CANONICAL_CATALOG_HASH == catalog_hash(CANONICAL_STRATEGIES)
    assert n6._APPROVED_CATALOG_VERSION == CANONICAL_CATALOG_VERSION
    assert n6._APPROVED_CATALOG_HASH == CANONICAL_CATALOG_HASH
    assert n6._SEALED_CATALOG.sealed is True


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
    xau = decide_n6(_candidate(TREND), _real_elig(TREND))
    es = decide_n6(dataclasses.replace(_candidate(TREND), symbol="ES"), _real_elig(TREND))
    assert xau.configuration_fingerprint != es.configuration_fingerprint
    with pytest.raises(NonComparableDecisionError):
        compare_decisions(xau.configuration_fingerprint, es.configuration_fingerprint)
